# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import os.path
from pathlib import Path
from textwrap import dedent, indent
from typing import Union

from postroj.model import LinuxDistribution, OperatingSystem, OperatingSystemFamily

from postroj.util import cmd, is_dir_empty

# TODO: Make this configurable.
archive_directory = Path("/var/lib/postroj/archive")
image_directory = Path("/var/lib/postroj/images")


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

    def __init__(self, distribution: LinuxDistribution):
        self.distribution = distribution
        archive_directory.mkdir(parents=True, exist_ok=True)
        image_directory.mkdir(parents=True, exist_ok=True)

    def setup(self):
        """
        Provision rootfs image per operating system family.
        """
        print(f"Provisioning container image for {self.distribution}")
        if self.distribution.family == OperatingSystemFamily.DEBIAN.value:
            self.setup_debian()
        elif self.distribution.family == OperatingSystemFamily.UBUNTU.value:
            self.setup_ubuntu()
        elif self.distribution.family == OperatingSystemFamily.CENTOS.value:
            self.setup_centos()

    def setup_debian(self):
        """
        Debian images are acquired from Docker Hub and will have to be adjusted
        by installing systemd.
        """

        # Acquire image.
        rootfs = self.acquire_from_docker()

        # Prepare image by installing systemd.
        cmd(f"systemd-nspawn --directory={rootfs} sh -c 'apt-get update; apt-get install --yes systemd'")

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
        archive_file = archive_directory / os.path.basename(self.distribution.image)
        archive_image = archive_directory / self.distribution.fullname
        archive_image.mkdir(parents=True, exist_ok=True)
        if not archive_file.exists():
            print(cmd(f"wget --directory-prefix={archive_directory} {self.distribution.image}"))
        if is_dir_empty(archive_image):
            print(cmd(f"tar --directory={archive_image} -xf {archive_file}"))

        # Prepare image by deactivating services which are hogging the bootstrapping.
        cmd(f"systemd-nspawn --directory={archive_image} systemctl disable ssh systemd-networkd-wait-online")

        # Activate image.
        self.activate_image(archive_image)

    def setup_centos(self):
        """
        CentOS 7 images are acquired from Docker Hub and will have to be
        adjusted by providing a more recent version of systemd.

        Failed to get shell PTY: Cannot set property StandardInputFileDescriptor, or unknown property.
        Failed to get shell PTY: Protocol error

        CentOS 7 has 219 but systemd >= 225 is needed.

        - https://hub.docker.com/_/centos
        - https://github.com/systemd/systemd/issues/2277
        """

        # Designate the minimum version of systemd needed.
        systemd_version_minimal = 225

        # Acquire image.
        rootfs = self.acquire_from_docker()

        # Skip installing systemd when already satisfied.
        response = cmd(f"systemd-nspawn --directory={rootfs} --pipe systemctl --version")
        systemd_version_installed = int(response.splitlines()[0].split(maxsplit=1)[1])
        if systemd_version_installed >= systemd_version_minimal:
            print(f"Found systemd version {systemd_version_installed}")
            return

        # Prepare image by upgrading systemd.
        upgrade_systemd_program = dedent(f"""
            set -x
            systemctl --version
            yum install -y wget gcc make libtool intltool gperf glib2-devel libcap-devel xz-devel libgcrypt-devel libmount-devel
            wget https://github.com/systemd/systemd/archive/refs/tags/v{systemd_version_minimal}.tar.gz -O systemd-{systemd_version_minimal}.tar.gz
            tar -xzf systemd-{systemd_version_minimal}.tar.gz
            cd systemd-{systemd_version_minimal}
            ./autogen.sh
            ./configure CFLAGS="-g -O0 -ftrapv" --enable-compat-libs --enable-kdbus --sysconfdir=/etc --localstatedir=/var --libdir=/usr/lib64 --disable-manpages
            make -j8
            make install
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

        # Activate image.
        self.activate_image(rootfs)

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
        if not archive_oci.exists():
            cmd(f"skopeo copy --override-os=linux {self.distribution.image} oci:{archive_oci}:{self.distribution.fullname}")
        if not archive_image.exists() or is_dir_empty(archive_image):
            cmd(f"umoci unpack --rootless --image={archive_oci}:{self.distribution.fullname} {archive_image}")

        return archive_image / "rootfs"

    def activate_image(self, rootfs: Union[Path, str]):
        """
        Activate a filesystem image to make it available for invoking it.
        """
        if not is_dir_empty(rootfs):
            target_path = image_directory / self.distribution.fullname
            target_path.unlink(missing_ok=True)
            target_path.symlink_to(rootfs, target_is_directory=True)
            return target_path
        else:
            raise ValueError(f"Unable to activate image at {rootfs}")


if __name__ == "__main__":
    """
    Provisioning rootfs images for all listed operating systems takes about
    four minutes from scratch.
    """
    all_distributions = [
        OperatingSystem.DEBIAN_BUSTER.value,
        OperatingSystem.DEBIAN_BULLSEYE.value,
        OperatingSystem.UBUNTU_FOCAL.value,
        OperatingSystem.UBUNTU_JAMMY.value,
        OperatingSystem.CENTOS_7.value,
    ]
    for distribution in all_distributions:
        ip = ImageProvider(distribution=distribution)
        ip.setup()
