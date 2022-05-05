# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import os.path
import shutil
from pathlib import Path
from textwrap import dedent, indent
from typing import Union

from postroj.model import LinuxDistribution, OperatingSystemFamily, ALL_DISTRIBUTIONS
from postroj.settings import archive_directory, image_directory, download_directory

from postroj.util import is_dir_empty, scmd, hcmd, print_header, print_section_header


class ImageProvider:
    """
    Provision operating system images for spawning containers with
    `systemd-nspawn`. See also `doc/images.rst`.

    Similar to the scheme employed by Let's Encrypt at
    ``/etc/letsencrypt/archive`` vs. ``/etc/letsencrypt/live``, the image
    provider will physically manifest filesystem images at
    ``/var/lib/postroj/archive`` and activate them by symlinking into
    ``/var/lib/postroj/images``.
    """

    ADDITIONAL_PACKAGES = ["curl", "wget"]

    def __init__(self, distribution: LinuxDistribution, force: bool = True):
        self.distribution = distribution
        self.force = force
        archive_directory.mkdir(parents=True, exist_ok=True)
        image_directory.mkdir(parents=True, exist_ok=True)

    def setup(self):
        """
        Provision rootfs image per operating system family.
        """
        print_section_header(f"Provisioning container image {self.distribution.fullname}")
        print(f"Using distribution {self.distribution}")
        print(f"Installing image at {self.image}")
        if self.distribution.family == OperatingSystemFamily.DEBIAN.value:
            self.setup_debian()
        elif self.distribution.family == OperatingSystemFamily.UBUNTU.value:
            self.setup_ubuntu()
        elif self.distribution.family == OperatingSystemFamily.FEDORA.value:
            self.setup_fedora()
        elif self.distribution.family == OperatingSystemFamily.CENTOS.value:
            self.setup_centos()
        else:
            raise ValueError(f"Unknown operating system family: {self.distribution.family}")

    def setup_debian(self):
        """
        Debian images are acquired from Docker Hub and will have to be adjusted
        by installing systemd.
        """

        # Acquire image.
        rootfs = self.acquire_from_docker()

        # Prepare image by installing systemd and additional packages.
        scmd(directory=rootfs, command=f"sh -c 'apt-get update; apt-get install --yes systemd {' '.join(self.ADDITIONAL_PACKAGES)}'")

        # Activate image.
        self.activate_image(rootfs)

    def setup_ubuntu(self):
        """
        Ubuntu images are acquired from »Ubuntu Minimal Cloud Images« tarballs.
        They need to be adjusted in order not to hog the boot process by
        disabling network-related services.

        - https://cloud-images.ubuntu.com/minimal/
        - https://askubuntu.com/questions/972215/a-start-job-is-running-for-wait-for-network-to-be-configured-ubuntu-server-17-1
        - https://askubuntu.com/questions/1090631/start-job-is-running-for-wait-for-network-to-be-configured-ubuntu-server-18-04
        - https://github.com/systemd/systemd/issues/12313
        """

        # Acquire image.
        image_tarball = download_directory / os.path.basename(self.distribution.image)
        rootfs = archive_directory / self.distribution.fullname

        if self.force:
            shutil.rmtree(rootfs)

        hcmd(f"wget --continue --no-clobber --directory-prefix={download_directory} {self.distribution.image}")
        if not rootfs.exists() or is_dir_empty(rootfs):
            rootfs.mkdir(parents=True, exist_ok=True)
            hcmd(f"tar --directory={rootfs} -xf {image_tarball}")

        # Prepare image by adding additional packages.
        scmd(directory=rootfs, command=f"sh -c 'apt-get update; apt-get install --yes {' '.join(self.ADDITIONAL_PACKAGES)}'")

        # Prepare image by deactivating services which are hogging the bootstrapping.
        scmd(directory=rootfs,
             command="systemctl disable ssh systemd-networkd-wait-online systemd-resolved")
        scmd(directory=rootfs,
             command="systemctl mask systemd-remount-fs systemd-timedated")

        # Would bring boot time from 1.2s down to 0.6s, but
        # sometimes container does not signal readiness then.
        # scmd(directory=rootfs, command="systemctl mask snapd snapd.socket")

        # Activate image.
        self.activate_image(rootfs)

    def setup_fedora(self):
        """
        Fedora images are acquired from Docker Hub.
        """

        # Acquire image.
        rootfs = self.acquire_from_docker()

        # Prepare image by installing systemd and additional packages.
        scmd(directory=rootfs, command=f"dnf install -y systemd {' '.join(self.ADDITIONAL_PACKAGES)}")

        # Activate image.
        self.activate_image(rootfs)

    def setup_centos(self):
        """
        CentOS images are acquired from Docker Hub.
        """

        # Acquire image.
        rootfs = self.acquire_from_docker()

        # Fix CentOS 7 by upgrading systemd.
        self.upgrade_systemd(rootfs)

        # Fix CentOS 8.
        # Problem: "Failed to download metadata for repo ‘AppStream’ [CentOS]".
        # https://techglimpse.com/failed-metadata-repo-appstream-centos-8/
        if self.distribution.family == OperatingSystemFamily.CENTOS.value and self.distribution.release == "8":
            os.system(f"/usr/bin/sed -i 's/mirrorlist/#mirrorlist/g' {rootfs}/etc/yum.repos.d/*")
            os.system(f"/usr/bin/sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' {rootfs}/etc/yum.repos.d/CentOS-*")

        # Prepare image by adding additional packages.
        scmd(directory=rootfs, command=f"yum install -y {' '.join(self.ADDITIONAL_PACKAGES)}")

        # Activate image.
        self.activate_image(rootfs)

    @staticmethod
    def upgrade_systemd(rootfs):
        """
        CentOS 7 images acquired from Docker Hub will have to be
        adjusted by providing a more recent version of systemd.

        Failed to get shell PTY: Cannot set property StandardInputFileDescriptor, or unknown property.
        Failed to get shell PTY: Protocol error

        CentOS 7 has 219 but systemd >= 225 is needed.

        - https://hub.docker.com/_/centos
        - https://github.com/systemd/systemd/issues/2277
        """

        # Designate the minimum version of systemd needed.
        systemd_version_minimal = 225

        # Skip installing systemd when already satisfied.
        process = hcmd(f"systemd-nspawn --directory={rootfs} --pipe systemctl --version", capture=True)
        response = process.stdout.strip()
        try:
            systemd_version_installed = int(response.splitlines()[0].split(" ", maxsplit=2)[1].split("-")[0])
        except:
            raise ValueError(f"Unable to decode systemd version from:\n{response}")
        if systemd_version_installed >= systemd_version_minimal:
            print(f"Found systemd version {systemd_version_installed}, "
                  f"which satisfies minimum version {systemd_version_minimal}")
            return

        print_header(f"Upgrading systemd to version {systemd_version_minimal}")

        # Prepare image by upgrading systemd.
        upgrade_systemd_program = dedent(f"""
            set -x
            systemctl --version
            yum upgrade -y
            yum install -y wget gcc make file libtool intltool gperf glib2-devel libcap-devel xz-devel libgcrypt-devel libmount-devel
            wget https://github.com/systemd/systemd/archive/refs/tags/v{systemd_version_minimal}.tar.gz -O systemd-{systemd_version_minimal}.tar.gz
            tar -xzf systemd-{systemd_version_minimal}.tar.gz
            cd systemd-{systemd_version_minimal}
            ./autogen.sh
            ./configure CFLAGS="-g -O0 -ftrapv" --enable-compat-libs --enable-kdbus --sysconfdir=/etc --localstatedir=/var --libdir=/usr/lib64 --disable-manpages
            make -j8
            make install
            systemctl --version
        """.strip()).strip()
        upgrade_systemd_program_meson = dedent(f"""
            set -x
            systemctl --version
            yum upgrade -y
            yum install -y wget gcc make file libtool intltool gperf glib2-devel libcap-devel xz-devel libgcrypt-devel libmount-devel python3-pip
            pip3 install "meson==0.44"
            wget https://github.com/systemd/systemd/archive/refs/tags/v{systemd_version_minimal}.tar.gz -O systemd-{systemd_version_minimal}.tar.gz
            tar -xzf systemd-{systemd_version_minimal}.tar.gz
            cd systemd-{systemd_version_minimal}
            meson build/ && ninja -C build install
            systemctl --version
        """.strip()).strip()

        upgrade_systemd_command = dedent(f"""
        systemd-nspawn --directory={rootfs} --pipe /bin/sh << EOF
        {indent(upgrade_systemd_program, "  ")}
        EOF
        """).strip()
        print(upgrade_systemd_command)

        print(f"Installing systemd version {systemd_version_minimal}")
        os.system(upgrade_systemd_command)

    def acquire_from_docker(self):
        """
        Acquiring ready-made filesystem images from Docker Hub is the quickest
        way to bootstrap a container environment.

        TODO: To be challenged, corresponding suggestions are very welcome.

        For converging Docker images to rootfs filesystems suitable to be
        started by systemd-nspawn, we use `skopeo` and `umoci`. As an
        intermediary step, an OCI Filesystem Bundle is created.

        TODO: Patches for improvement are very welcome.

        - https://github.com/containers/skopeo
        - https://github.com/opencontainers/umoci
        - https://github.com/opencontainers/runtime-spec/blob/main/bundle.md
        """

        # Download and extract image.
        archive_oci = archive_directory / f"{self.distribution.fullname}.oci"
        archive_image = archive_directory / f"{self.distribution.fullname}.img"

        if self.force:
            shutil.rmtree(archive_oci, ignore_errors=True)
            shutil.rmtree(archive_image, ignore_errors=True)

        if not archive_oci.exists():
            hcmd(f"skopeo copy --override-os=linux {self.distribution.image} oci:{archive_oci}:{self.distribution.fullname}")
        if not archive_image.exists() or is_dir_empty(archive_image):
            hcmd(f"umoci unpack --rootless --image={archive_oci}:{self.distribution.fullname} {archive_image}")

        return archive_image / "rootfs"

    @property
    def image(self):
        return image_directory / self.distribution.fullname

    def activate_image(self, rootfs: Union[Path, str]):
        """
        Activate a filesystem image to make it available for invoking it.
        """
        if not is_dir_empty(rootfs):
            target_path = self.image
            target_path.unlink(missing_ok=True)
            target_path.symlink_to(rootfs, target_is_directory=True)
            return target_path
        else:
            raise ValueError(f"Unable to activate image at {rootfs}")
