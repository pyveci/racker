# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
from enum import Enum
from typing import Generator, List

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
    ROCKYLINUX_8 = LinuxDistribution(
        family=OperatingSystemFamily.REDHAT,
        name=OperatingSystemName.ROCKYLINUX,
        release="8",
        version="8",
        image="docker://docker.io/rockylinux:8",
    )
    OPENSUSE_LEAP = LinuxDistribution(
        family=OperatingSystemFamily.SUSE,
        name=OperatingSystemName.OPENSUSE,
        release="leap",
        version="15",
        image="docker://docker.io/opensuse/leap:15",
    )
    OPENSUSE_TUMBLEWEED = LinuxDistribution(
        family=OperatingSystemFamily.SUSE,
        name=OperatingSystemName.OPENSUSE,
        release="tumbleweed",
        version="latest",
        image="docker://docker.io/opensuse/tumbleweed:latest",
    )
    AMAZONLINUX_2022 = LinuxDistribution(
        family=OperatingSystemFamily.REDHAT,
        name=OperatingSystemName.AMAZONLINUX,
        release="2022",
        version="2022",
        image="docker://docker.io/amazonlinux:2022",
    )
    ORACLELINUX_8 = LinuxDistribution(
        family=OperatingSystemFamily.REDHAT,
        name=OperatingSystemName.ORACLELINUX,
        release="8",
        version="8",
        image="docker://docker.io/oraclelinux:8",
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
    CuratedOperatingSystem.DEBIAN_SID,
    CuratedOperatingSystem.UBUNTU_FOCAL,
    CuratedOperatingSystem.UBUNTU_JAMMY,
    # .rpm-based I
    CuratedOperatingSystem.FEDORA_35,
    CuratedOperatingSystem.FEDORA_36,
    CuratedOperatingSystem.FEDORA_37,
    CuratedOperatingSystem.OPENSUSE_LEAP,
    CuratedOperatingSystem.OPENSUSE_TUMBLEWEED,
    # .rpm-based II
    CuratedOperatingSystem.CENTOS_7,
    CuratedOperatingSystem.CENTOS_8,
    CuratedOperatingSystem.ROCKYLINUX_8,
    CuratedOperatingSystem.AMAZONLINUX_2022,
    CuratedOperatingSystem.ORACLELINUX_8,
    # others
    CuratedOperatingSystem.ARCHLINUX_20220501,
]


def generate_curated_distributions() -> Generator[LinuxDistribution, None, None]:
    for system in CURATED_OPERATING_SYSTEMS:
        distribution: LinuxDistribution = system.value
        yield distribution


def find_distribution(image_label: str) -> LinuxDistribution:

    for distribution in generate_curated_distributions():
        if image_label == distribution.fullname or image_label == distribution.versionname:
            return distribution

    raise ValueError(f"Unknown image label {image_label}")


def generate_images():
    for distribution in generate_curated_distributions():
        yield distribution.fullname


def list_images():
    return list(generate_images())
