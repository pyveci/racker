# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import dataclasses
from enum import Enum
from typing import Dict, Generator, List

from postroj.model import LinuxDistribution, OperatingSystemFamily, OperatingSystemName


class CuratedOperatingSystem(Enum):

    # .deb-based distributions
    DEBIAN_STRETCH = LinuxDistribution(
        family=OperatingSystemFamily.DEBIAN,
        name=OperatingSystemName.DEBIAN,
        release="stretch",
        version="9",
        image="docker://docker.io/debian:stretch-slim",
    )
    DEBIAN_BUSTER = LinuxDistribution(
        family=OperatingSystemFamily.DEBIAN,
        name=OperatingSystemName.DEBIAN,
        release="buster",
        version="10",
        # image="https://cloud.debian.org/images/cloud/buster/latest/debian-10-genericcloud-amd64.tar.xz",
        image="docker://docker.io/debian:buster-slim",
    )
    DEBIAN_BULLSEYE = LinuxDistribution(
        family=OperatingSystemFamily.DEBIAN,
        name=OperatingSystemName.DEBIAN,
        release="bullseye",
        version="11",
        # image="https://cloud.debian.org/images/cloud/bullseye/latest/debian-11-genericcloud-amd64.tar.xz",
        image="docker://docker.io/debian:bullseye-slim",
    )
    DEBIAN_BOOKWORM = LinuxDistribution(
        family=OperatingSystemFamily.DEBIAN,
        name=OperatingSystemName.DEBIAN,
        release="bookworm",
        version="12",
        image="docker://docker.io/debian:bookworm-slim",
    )
    DEBIAN_TRIXIE = LinuxDistribution(
        family=OperatingSystemFamily.DEBIAN,
        name=OperatingSystemName.DEBIAN,
        release="trixie",
        version="13",
        image="docker://docker.io/debian:trixie-slim",
    )
    DEBIAN_SID = LinuxDistribution(
        family=OperatingSystemFamily.DEBIAN,
        name=OperatingSystemName.DEBIAN,
        release="sid",
        version="unstable",
        image="docker://docker.io/debian:sid-slim",
    )
    UBUNTU_FOCAL = LinuxDistribution(
        family=OperatingSystemFamily.DEBIAN,
        name=OperatingSystemName.UBUNTU,
        release="focal",
        version="20",
        image="https://cloud-images.ubuntu.com/minimal/daily/focal/current/focal-minimal-cloudimg-amd64-root.tar.xz",
    )
    UBUNTU_JAMMY = LinuxDistribution(
        family=OperatingSystemFamily.DEBIAN,
        name=OperatingSystemName.UBUNTU,
        release="jammy",
        version="22",
        image="https://cloud-images.ubuntu.com/minimal/daily/jammy/current/jammy-minimal-cloudimg-amd64-root.tar.xz",
    )
    UBUNTU_NOBLE = LinuxDistribution(
        family=OperatingSystemFamily.DEBIAN,
        name=OperatingSystemName.UBUNTU,
        release="noble",
        version="24",
        image="https://cloud-images.ubuntu.com/minimal/daily/noble/current/noble-minimal-cloudimg-amd64-root.tar.xz",
    )

    # .rpm-based distributions
    FEDORA_35 = LinuxDistribution(
        family=OperatingSystemFamily.REDHAT,
        name=OperatingSystemName.FEDORA,
        release="35",
        version="35",
        image="docker://docker.io/fedora:35",
    )
    FEDORA_36 = LinuxDistribution(
        family=OperatingSystemFamily.REDHAT,
        name=OperatingSystemName.FEDORA,
        release="36",
        version="36",
        image="docker://docker.io/fedora:36",
    )
    FEDORA_37 = LinuxDistribution(
        family=OperatingSystemFamily.REDHAT,
        name=OperatingSystemName.FEDORA,
        release="37",
        version="37",
        image="docker://docker.io/fedora:37",
    )
    FEDORA_44 = LinuxDistribution(
        family=OperatingSystemFamily.REDHAT,
        name=OperatingSystemName.FEDORA,
        release="44",
        version="44",
        image="docker://docker.io/fedora:44",
    )
    FEDORA_45 = LinuxDistribution(
        family=OperatingSystemFamily.REDHAT,
        name=OperatingSystemName.FEDORA,
        release="45",
        version="45",
        image="docker://docker.io/fedora:45",
    )
    CENTOS_7 = LinuxDistribution(
        family=OperatingSystemFamily.REDHAT,
        name=OperatingSystemName.CENTOS,
        release="7",
        version="7",
        image="docker://docker.io/centos:7",
    )
    CENTOS_8 = LinuxDistribution(
        family=OperatingSystemFamily.REDHAT,
        name=OperatingSystemName.CENTOS,
        release="8",
        version="8",
        image="docker://docker.io/centos:8",
    )
    CENTOS_9 = LinuxDistribution(
        family=OperatingSystemFamily.REDHAT,
        name=OperatingSystemName.CENTOS,
        release="9",
        version="9",
        image="docker://quay.io/centos/centos:stream9",
    )
    CENTOS_10 = LinuxDistribution(
        family=OperatingSystemFamily.REDHAT,
        name=OperatingSystemName.CENTOS,
        release="10",
        version="10",
        image="docker://quay.io/centos/centos:stream10",
    )
    RHEL_8 = LinuxDistribution(
        family=OperatingSystemFamily.REDHAT,
        name=OperatingSystemName.RHEL,
        release="8",
        version="8",
        image="docker://registry.access.redhat.com/ubi8/ubi",
    )
    RHEL_9 = LinuxDistribution(
        family=OperatingSystemFamily.REDHAT,
        name=OperatingSystemName.RHEL,
        release="9",
        version="9",
        image="docker://registry.access.redhat.com/ubi9/ubi",
    )
    RHEL_10 = LinuxDistribution(
        family=OperatingSystemFamily.REDHAT,
        name=OperatingSystemName.RHEL,
        release="10",
        version="10",
        image="docker://registry.access.redhat.com/ubi10/ubi",
    )
    ROCKYLINUX_8 = LinuxDistribution(
        family=OperatingSystemFamily.REDHAT,
        name=OperatingSystemName.ROCKYLINUX,
        release="8",
        version="8",
        image="docker://docker.io/rockylinux:8",
    )
    ROCKYLINUX_9 = LinuxDistribution(
        family=OperatingSystemFamily.REDHAT,
        name=OperatingSystemName.ROCKYLINUX,
        release="9",
        version="9",
        image="docker://docker.io/rockylinux:9",
    )
    OPENSUSE_LEAP_15 = LinuxDistribution(
        family=OperatingSystemFamily.SUSE,
        name=OperatingSystemName.OPENSUSE,
        release="leap15",
        version="15",
        image="docker://docker.io/opensuse/leap:15",
    )
    OPENSUSE_LEAP_16 = LinuxDistribution(
        family=OperatingSystemFamily.SUSE,
        name=OperatingSystemName.OPENSUSE,
        release="leap16",
        version="16",
        image="docker://docker.io/opensuse/leap:16",
    )
    OPENSUSE_TUMBLEWEED = LinuxDistribution(
        family=OperatingSystemFamily.SUSE,
        name=OperatingSystemName.OPENSUSE,
        release="tumbleweed",
        version="latest",
        image="docker://docker.io/opensuse/tumbleweed:latest",
    )
    SLES_15 = LinuxDistribution(
        family=OperatingSystemFamily.SUSE,
        name=OperatingSystemName.SLES,
        release="15",
        version="15",
        image="docker://registry.suse.com/suse/sle15",
    )
    SLES_BCI = LinuxDistribution(
        family=OperatingSystemFamily.SUSE,
        name=OperatingSystemName.SLES,
        release="bci",
        version="latest",
        image="docker://registry.suse.com/bci/bci-base:latest",
    )
    AMAZONLINUX_2023 = LinuxDistribution(
        family=OperatingSystemFamily.REDHAT,
        name=OperatingSystemName.AMAZONLINUX,
        release="2023",
        version="2023",
        image="docker://docker.io/amazonlinux:2023",
    )
    ORACLELINUX_8 = LinuxDistribution(
        family=OperatingSystemFamily.REDHAT,
        name=OperatingSystemName.ORACLELINUX,
        release="8",
        version="8",
        image="docker://docker.io/oraclelinux:8",
    )
    ORACLELINUX_9 = LinuxDistribution(
        family=OperatingSystemFamily.REDHAT,
        name=OperatingSystemName.ORACLELINUX,
        release="9",
        version="9",
        image="docker://docker.io/oraclelinux:9",
    )
    ORACLELINUX_10 = LinuxDistribution(
        family=OperatingSystemFamily.REDHAT,
        name=OperatingSystemName.ORACLELINUX,
        release="10",
        version="10",
        image="docker://docker.io/oraclelinux:10",
    )

    # Other distributions, not based on .deb or .rpm.
    ARCHLINUX_20220501 = LinuxDistribution(
        family=None,
        name=OperatingSystemName.ARCHLINUX,
        release="20220501",
        version="20220501",
        image="docker://docker.io/archlinux:base-20220501.0.54834",
    )
    # TODO: Gentoo?


CURATED_OPERATING_SYSTEMS: List[Enum] = [
    # .deb-based
    CuratedOperatingSystem.DEBIAN_STRETCH,
    CuratedOperatingSystem.DEBIAN_BUSTER,
    CuratedOperatingSystem.DEBIAN_BULLSEYE,
    CuratedOperatingSystem.DEBIAN_BOOKWORM,
    CuratedOperatingSystem.DEBIAN_TRIXIE,
    CuratedOperatingSystem.DEBIAN_SID,
    CuratedOperatingSystem.UBUNTU_FOCAL,
    CuratedOperatingSystem.UBUNTU_JAMMY,
    CuratedOperatingSystem.UBUNTU_NOBLE,
    # .rpm-based I
    CuratedOperatingSystem.FEDORA_35,
    CuratedOperatingSystem.FEDORA_36,
    CuratedOperatingSystem.FEDORA_37,
    CuratedOperatingSystem.FEDORA_44,
    CuratedOperatingSystem.FEDORA_45,
    CuratedOperatingSystem.RHEL_8,
    CuratedOperatingSystem.RHEL_9,
    CuratedOperatingSystem.RHEL_10,
    CuratedOperatingSystem.OPENSUSE_LEAP_15,
    CuratedOperatingSystem.OPENSUSE_LEAP_16,
    CuratedOperatingSystem.OPENSUSE_TUMBLEWEED,
    CuratedOperatingSystem.SLES_15,
    CuratedOperatingSystem.SLES_BCI,
    # .rpm-based II
    CuratedOperatingSystem.CENTOS_7,
    CuratedOperatingSystem.CENTOS_8,
    CuratedOperatingSystem.CENTOS_9,
    CuratedOperatingSystem.CENTOS_10,
    CuratedOperatingSystem.ROCKYLINUX_8,
    CuratedOperatingSystem.ROCKYLINUX_9,
    CuratedOperatingSystem.AMAZONLINUX_2023,
    CuratedOperatingSystem.ORACLELINUX_10,
    # others
    CuratedOperatingSystem.ARCHLINUX_20220501,
]


@dataclasses.dataclass
class OperatingSystemType:
    family: OperatingSystemFamily
    name: OperatingSystemName


# Map of `NAME=` items in `/etc/os-release` file to qualified operating systems types.
OS_RELEASE_NAME_MAP: Dict[str, OperatingSystemType] = {
    "Debian GNU/Linux": OperatingSystemType(
        family=OperatingSystemFamily.DEBIAN,
        name=OperatingSystemName.DEBIAN,
    ),
    "Ubuntu": OperatingSystemType(
        family=OperatingSystemFamily.DEBIAN,
        name=OperatingSystemName.UBUNTU,
    ),
    "Fedora Linux": OperatingSystemType(
        family=OperatingSystemFamily.REDHAT,
        name=OperatingSystemName.FEDORA,
    ),
    "CentOS Linux": OperatingSystemType(
        family=OperatingSystemFamily.REDHAT,
        name=OperatingSystemName.CENTOS,
    ),
    "CentOS Stream": OperatingSystemType(
        family=OperatingSystemFamily.REDHAT,
        name=OperatingSystemName.CENTOS,
    ),
    "Red Hat Enterprise Linux": OperatingSystemType(
        family=OperatingSystemFamily.REDHAT,
        name=OperatingSystemName.RHEL,
    ),
    "Rocky Linux": OperatingSystemType(
        family=OperatingSystemFamily.REDHAT,
        name=OperatingSystemName.ROCKYLINUX,
    ),
    "Amazon Linux": OperatingSystemType(
        family=OperatingSystemFamily.REDHAT,
        name=OperatingSystemName.AMAZONLINUX,
    ),
    "openSUSE Leap": OperatingSystemType(
        family=OperatingSystemFamily.SUSE,
        name=OperatingSystemName.OPENSUSE,
    ),
    "openSUSE Tumbleweed": OperatingSystemType(
        family=OperatingSystemFamily.SUSE,
        name=OperatingSystemName.OPENSUSE,
    ),
    "SLES": OperatingSystemType(
        family=OperatingSystemFamily.SUSE,
        name=OperatingSystemName.SLES,
    ),
    "Arch Linux": OperatingSystemType(
        family=OperatingSystemFamily.ARCHLINUX,
        name=OperatingSystemName.ARCHLINUX,
    ),
}


def generate_curated_distributions() -> Generator[LinuxDistribution, None, None]:
    for system in CURATED_OPERATING_SYSTEMS:
        distribution: LinuxDistribution = system.value
        yield distribution


def find_distribution(image_label: str) -> LinuxDistribution:

    for distribution in generate_curated_distributions():
        if image_label == distribution.fullname or image_label == distribution.versionname:
            return distribution

    # TODO: Introduce appropriate exception classes.
    raise ValueError(f"Unknown image label: {image_label}")


def generate_images():
    for distribution in generate_curated_distributions():
        yield distribution.fullname


def list_images():
    return list(generate_images())
