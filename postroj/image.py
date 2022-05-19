# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import enum
import logging
import os.path
import shutil
import subprocess
from enum import Enum
from pathlib import Path
from textwrap import dedent, indent
from typing import Union

from furl import furl

from postroj.backend.nspawn import scmd
from postroj.exceptions import InvalidImageReference, InvalidPhysicalImage, OsReleaseFileMissing, ProvisioningError
from postroj.model import ConfigurationOptions, LinuxDistribution, OperatingSystemFamily, OperatingSystemName
from postroj.registry import OS_RELEASE_NAME_MAP
from postroj.settings import get_appsettings
from postroj.util import find_rootfs, hcmd, is_dir_empty, stdout_to_stderr, subprocess_get_error_message

logger = logging.getLogger(__name__)


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

    CAT_COMMAND = "/bin/cat"
    OS_RELEASE_FILE = "/etc/os-release"

    ADDITIONAL_PACKAGES = [
        # Needed for `pkgprobe`.
        "curl",
        "wget",
        # Put into `analytics` section.
        # "procps",
        # "lsof",
        # "nano",
    ]

    def __init__(self, distribution: Union[LinuxDistribution, Enum], autosetup: bool = True, force: bool = False):

        if isinstance(distribution, Enum):
            distribution = distribution.value

        self.distribution = distribution
        self.autosetup = autosetup

        self.has_operating_system = None
        self.has_systemd = None
        self.is_docker = None

        # TODO: Discriminate `force` vs. `update`.
        self.force = force

        self.settings: ConfigurationOptions = get_appsettings()
        path_prefix = self.settings.archive_directory / self.distribution.fullname
        self.oci_path = path_prefix.with_suffix(".oci")
        self.image_staging = path_prefix.with_suffix(".img")

        self.settings.archive_directory.mkdir(parents=True, exist_ok=True)
        self.settings.image_directory.mkdir(parents=True, exist_ok=True)

        if self.autosetup or self.force:

            if self.image.exists():
                self.discover()
            else:
                with stdout_to_stderr():
                    self.setup()

    def setup(self):
        """
        Provision rootfs image per operating system family.
        """
        logger.info(f"Provisioning container image {self.distribution.fullname}")
        logger.info(f"Using distribution {self.distribution}")
        logger.info(f"Installing image at {self.image}")
        self.acquire()
        self.activate_image()

    def acquire(self):
        """
        Acquire an operating system image from the network.
        """

        logger.info(f"Acquiring container image from {self.distribution.image}")
        image_uri = furl(self.distribution.image)
        if image_uri.scheme in ["http", "https"]:
            outcome = self.acquire_from_http()
        elif image_uri.scheme == "docker":
            outcome = self.acquire_from_docker()
        else:
            raise InvalidImageReference(f"Unsupported scheme for image: {self.distribution.image}")

        self.discover()

        if outcome == ImageAcquisitionOutcome.DOWLOADED_NEWER:
            logger.info(f"Status: Downloaded newer image for {self.distribution.fullname}")
        elif outcome == ImageAcquisitionOutcome.UP_TO_DATE:
            logger.info(f"Status: Image is up to date for {self.distribution.fullname}")

        if self.has_operating_system:
            try:
                self.provision_systemd()
            except ProvisioningError as ex:
                details = str(ex.args[0])
                message = f"Provisioning filesystem image failed: {details}"
                logger.warning(message)
                raise ProvisioningError(message)
        else:
            logger.info(f"Skipping provisioning of systemd")

    def discover(self):

        # Skip discovery if already qualified.
        if self.distribution.family and self.distribution.name:
            self.has_operating_system = True
            logger.info(
                f"Skipping operating system discovery, using distribution "
                f"family={self.distribution.family}, name={self.distribution.name}"
            )
            return

        logger.info(f"Inspecting container image at {self.image_staging}")
        rootfs = find_rootfs(self.image_staging)

        # Read `/etc/os-release` file from OS root directory in order to determine operating system.
        logger.info(f"Discovering operating system from OS root directory at {rootfs}")
        error_message = (
            f"Container {self.distribution.fullname} at directory {rootfs} "
            f"lacks an operating system (os-release file is missing or inaccessible)."
        )
        try:
            process = scmd(
                directory=rootfs, command=f"{self.CAT_COMMAND} {self.OS_RELEASE_FILE}", passthrough=False, capture=True
            )
            os_release = process.stdout
            self.has_operating_system = True
        except subprocess.CalledProcessError as ex:
            self.has_operating_system = False
            message = subprocess_get_error_message(exception=ex)
            logger.exception(f"Reading {self.OS_RELEASE_FILE} failed")
            raise OsReleaseFileMissing(f"{error_message} Error: {ex.__class__.__name__}. Reason: {message}")
        except Exception as ex:
            self.has_operating_system = False
            logger.exception(f"Reading {self.OS_RELEASE_FILE} failed")
            raise OsReleaseFileMissing(f"{error_message} Error: {ex.__class__.__name__}. Reason: {ex}")

        # Check if systemd is present in the OS root directory.
        self.check_systemd()

        # Determine operating system by reading `/etc/os-release` file.
        for os_name, os_type in OS_RELEASE_NAME_MAP.items():
            if os_name in os_release:
                self.distribution.family = os_type.family
                self.distribution.name = os_type.name

        logger.info(f"Discovered operating system family={self.distribution.family}, name={self.distribution.name}")

    def check_systemd(self) -> bool:
        """
        Check whether `systemd` or another `init` program is present in the OS root directory.

        When `systemd-nspawn` would encounter an OS root directory without an appropriate program, it would croak like:
        execv(/usr/lib/systemd/systemd, /lib/systemd/systemd, /sbin/init) failed: No such file or directory
        """

        self.has_systemd = False

        rootfs = find_rootfs(self.image_staging)
        init_candidates = ["usr/lib/systemd/systemd", "lib/systemd/systemd", "sbin/init"]
        for candidate in init_candidates:
            if (rootfs / candidate).exists():
                self.has_systemd = True
                logger.info(f"Init program {rootfs / candidate} found")
                break

        return self.has_systemd

    def provision_systemd(self):
        """
        Install systemd within the OS root directory in order to make the machine bootable.
        """

        if self.has_systemd:
            logger.info("Skipping systemd installation")
            return

        if self.distribution.name == OperatingSystemName.DEBIAN:
            self.setup_debian()
        elif self.distribution.name == OperatingSystemName.UBUNTU:
            self.setup_ubuntu()
        elif self.distribution.name == OperatingSystemName.CENTOS:
            self.setup_centos()
        elif self.distribution.family == OperatingSystemFamily.REDHAT:
            self.setup_redhat()
        elif self.distribution.family == OperatingSystemFamily.SUSE:
            self.setup_suse()
        elif self.distribution.family == OperatingSystemFamily.ARCHLINUX:
            self.setup_archlinux()
        else:
            raise ProvisioningError(f"Unsupported operating system: {self.distribution}")

        self.check_systemd()

    def setup_debian(self):
        """
        Debian images are acquired from Docker Hub and will have to be adjusted
        by installing systemd.
        """

        rootfs = find_rootfs(self.image_staging)

        # Prepare image by installing systemd and additional packages.
        scmd(
            directory=rootfs,
            command=f"sh -c 'export DEBIAN_FRONTEND=noninteractive; "
            f"apt-get update; apt-get install --yes systemd {' '.join(self.ADDITIONAL_PACKAGES)}'",
        )

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

        if self.is_docker:
            return self.setup_debian()

        rootfs = self.image_staging

        # Prepare image by adding additional packages.
        scmd(
            directory=rootfs,
            command=f"sh -c 'export DEBIAN_FRONTEND=noninteractive; "
            f"apt-get update; apt-get install --yes {' '.join(self.ADDITIONAL_PACKAGES)}'",
        )

        # Prepare image by deactivating services which are hogging the bootstrapping.
        scmd(directory=rootfs, command="systemctl disable ssh systemd-networkd-wait-online systemd-resolved")
        scmd(directory=rootfs, command="systemctl mask systemd-remount-fs systemd-timedated")

        # Would bring boot time from 1.2s down to 0.6s, but
        # sometimes container does not signal readiness then.
        # scmd(directory=rootfs, command="systemctl mask snapd snapd.socket")

    def setup_redhat(self):
        """
        It works the same for all Red Hat based systems like Fedora, CentOS, Rocky Linux and Oracle Linux.
        """

        # Unable to install packages on RHEL9/UBI9-beta.
        # This system is not registered with an entitlement server.
        if self.distribution.name == OperatingSystemName.RHEL and self.distribution.release == "9":
            logger.warning(
                "Unable to provision UBI9 image, as it would need " "to be registered with an entitlement server"
            )
            return

        rootfs = find_rootfs(self.image_staging)

        has_dnf = False
        has_microdnf = False
        try:
            scmd(directory=rootfs, command=f"command -v dnf")
            has_dnf = True
        except:
            try:
                scmd(directory=rootfs, command=f"command -v microdnf")
                has_microdnf = True
            except:
                raise

        # Prepare image by installing systemd and additional packages.
        if has_dnf:
            scmd(directory=rootfs, command=f"dnf install -y --skip-broken systemd {' '.join(self.ADDITIONAL_PACKAGES)}")
        elif has_microdnf:
            scmd(directory=rootfs, command=f"microdnf install -y systemd {' '.join(self.ADDITIONAL_PACKAGES)}")
        else:
            raise ProvisioningError(
                f"Installing packages on Red Hat Linux or derivate failed. "
                f"Unable to find appropriate package manager, tried `dnf` and `microdnf`."
            )

    def setup_suse(self):
        """
        openSUSE images are acquired from Docker Hub.
        """

        rootfs = find_rootfs(self.image_staging)

        # Prepare image by installing systemd and additional packages.
        # TODO: Install additional packages only for `postroj pkgprobe`, only `systemd` is mandatory.
        scmd(directory=rootfs, command=f"zypper install -y systemd {' '.join(self.ADDITIONAL_PACKAGES)}")

    def setup_centos(self):
        """
        CentOS images are acquired from Docker Hub.
        """

        rootfs = find_rootfs(self.image_staging)

        if self.distribution.name == OperatingSystemName.CENTOS and self.distribution.release == "9":
            return self.setup_redhat()

        # Fix CentOS 7 by upgrading systemd.
        self.upgrade_systemd(rootfs)

        # Fix CentOS 8.
        # Problem: "Failed to download metadata for repo ‘AppStream’ [CentOS]".
        # https://techglimpse.com/failed-metadata-repo-appstream-centos-8/
        if self.distribution.name == OperatingSystemName.CENTOS and self.distribution.release == "8":
            os.system(f"/usr/bin/sed -i 's/mirrorlist/#mirrorlist/g' {rootfs}/etc/yum.repos.d/*")
            os.system(
                f"/usr/bin/sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' {rootfs}/etc/yum.repos.d/CentOS-*"
            )

        # Prepare image by adding additional packages.
        scmd(directory=rootfs, command=f"yum install -y {' '.join(self.ADDITIONAL_PACKAGES)}")

    def setup_archlinux(self):
        """
        Arch Linux images are acquired from Docker Hub.
        """

        rootfs = find_rootfs(self.image_staging)

        # Prepare image by installing systemd and additional packages.
        scmd(directory=rootfs, command=f"pacman -Syu --noconfirm systemd {' '.join(self.ADDITIONAL_PACKAGES)}")

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
            raise ProvisioningError(f"Unable to decode systemd version from:\n{response}")
        if systemd_version_installed >= systemd_version_minimal:
            logger.info(
                f"Found systemd version {systemd_version_installed}, "
                f"which satisfies minimum version {systemd_version_minimal}"
            )
            return

        logger.info(f"Upgrading systemd to version {systemd_version_minimal}")

        # Prepare image by upgrading systemd.
        upgrade_systemd_program = dedent(
            f"""
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
        """.strip()
        ).strip()
        upgrade_systemd_program_meson = dedent(
            f"""
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
        """.strip()
        ).strip()

        upgrade_systemd_command = dedent(
            f"""
        systemd-nspawn --directory={rootfs} --pipe /bin/sh << EOF
        {indent(upgrade_systemd_program, "  ")}
        EOF
        """
        ).strip()
        logger.info(upgrade_systemd_command)

        logger.info(f"Installing systemd version {systemd_version_minimal}")
        os.system(upgrade_systemd_command)

    def acquire_from_http(self):
        download_directory = self.settings.download_directory

        # Acquire image.
        image_tarball = download_directory / os.path.basename(self.distribution.image)
        rootfs = self.image_staging

        if self.force:
            shutil.rmtree(rootfs, ignore_errors=True)

        try:
            hcmd(f"wget --continue --no-clobber --directory-prefix={download_directory} {self.distribution.image}")
        except subprocess.CalledProcessError as ex:
            raise InvalidImageReference(f"Unable to download image: {self.distribution.image}")

        if not rootfs.exists() or is_dir_empty(rootfs):
            logger.info(f"Extracting rootfs from {image_tarball} to {rootfs}")
            rootfs.mkdir(parents=True, exist_ok=True)
            hcmd(f"tar --directory={rootfs} -xf {image_tarball}")
            outcome = ImageAcquisitionOutcome.DOWLOADED_NEWER
        else:
            outcome = ImageAcquisitionOutcome.UP_TO_DATE

        return outcome

    def acquire_from_docker(self):
        """
        Acquiring ready-made filesystem images from Docker Hub is the quickest
        way to bootstrap a container environment.

        TODO: To be challenged, corresponding suggestions are very welcome.

        For converging Docker images to rootfs filesystems suitable to be
        started by systemd-nspawn, we use `skopeo` and `umoci`. As an
        intermediary step, an OCI Filesystem Bundle is created.

        TODO: Patches for improvements are very welcome.

        - https://github.com/containers/skopeo
        - https://github.com/opencontainers/umoci
        - https://github.com/opencontainers/runtime-spec/blob/main/bundle.md
        """

        self.is_docker = True

        # When forces are applied, start from scratch by removing
        # all established download artefacts.
        if self.force:
            shutil.rmtree(self.oci_path, ignore_errors=True)
            shutil.rmtree(self.image_staging, ignore_errors=True)

        # FIXME: Detect if tag is given.
        oci_tag = "default"

        # Download and extract image.
        outcome = ImageAcquisitionOutcome.UP_TO_DATE
        if not self.oci_path.exists() or not (self.oci_path / "index.json").exists():
            hcmd(f"skopeo copy --override-os=linux {self.distribution.image} oci:{self.oci_path}:{oci_tag}")
            outcome = ImageAcquisitionOutcome.DOWLOADED_NEWER
        if (
            not self.image_staging.exists()
            or is_dir_empty(self.image_staging)
            or is_dir_empty(self.image_staging / "rootfs", missing_ok=True)
        ):
            hcmd(f"umoci unpack --rootless --image={self.oci_path}:{oci_tag} {self.image_staging}")
            outcome = ImageAcquisitionOutcome.DOWLOADED_NEWER

        return outcome

    @property
    def image(self) -> Path:
        """
        Return path to image directory.
        """
        return self.settings.image_directory / self.distribution.fullname

    def activate_image(self):
        """
        Activate a filesystem image to make it available for invoking it.
        """
        if not is_dir_empty(self.image_staging):
            target_path = self.image
            target_path.unlink(missing_ok=True)
            target_path.symlink_to(self.image_staging, target_is_directory=True)
            return target_path
        else:
            raise InvalidPhysicalImage(f"Unable to activate image at {self.image_staging}")


class ImageAcquisitionOutcome(enum.Enum):
    """
    Bundle the outcome from an image acquisition operation.
    """

    DOWLOADED_NEWER = enum.auto()
    UP_TO_DATE = enum.auto()
