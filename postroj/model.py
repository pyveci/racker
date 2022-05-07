# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import dataclasses
from enum import Enum
from pathlib import Path
from typing import List


@dataclasses.dataclass
class ConfigurationOptions:
    archive_directory: Path = None
    image_directory: Path = None
    cache_directory: Path = None

    @property
    def download_directory(self) -> Path:
        return self.cache_directory / "downloads"


@dataclasses.dataclass
class LinuxDistribution:
    family: str
    name: str
    release: str
    image: str

    @property
    def fullname(self):
        return f"{self.family}-{self.name}"


class OperatingSystemFamily(Enum):
    DEBIAN = "debian"
    UBUNTU = "ubuntu"
    FEDORA = "fedora"
    CENTOS = "centos"
    ROCKYLINUX = "rockylinux"
    ARCHLINUX = "archlinux"
    SUSE = "suse"


class OperatingSystem(Enum):
    DEBIAN_STRETCH = LinuxDistribution(
        family="debian",
        name="stretch",
        release="9",
        image="docker://docker.io/debian:stretch-slim",
    )
    DEBIAN_BUSTER = LinuxDistribution(
        family="debian",
        name="buster",
        release="10",
        # image="https://cloud.debian.org/images/cloud/buster/latest/debian-10-genericcloud-amd64.tar.xz",
        image="docker://docker.io/debian:buster-slim",
    )
    DEBIAN_BULLSEYE = LinuxDistribution(
        family="debian",
        name="bullseye",
        release="11",
        # image="https://cloud.debian.org/images/cloud/bullseye/latest/debian-11-genericcloud-amd64.tar.xz",
        image="docker://docker.io/debian:bullseye-slim",
    )
    DEBIAN_BOOKWORM = LinuxDistribution(
        family="debian",
        name="bookworm",
        release="12",
        image="docker://docker.io/debian:bookworm-slim",
    )
    DEBIAN_SID = LinuxDistribution(
        family="debian",
        name="sid",
        release="unstable",
        image="docker://docker.io/debian:sid-slim",
    )
    UBUNTU_FOCAL = LinuxDistribution(
        family="ubuntu",
        name="focal",
        release="20",
        image="https://cloud-images.ubuntu.com/minimal/daily/focal/current/focal-minimal-cloudimg-amd64-root.tar.xz",
    )
    UBUNTU_JAMMY = LinuxDistribution(
        family="ubuntu",
        name="jammy",
        release="22",
        image="https://cloud-images.ubuntu.com/minimal/daily/jammy/current/jammy-minimal-cloudimg-amd64-root.tar.xz",
    )
    FEDORA_35 = LinuxDistribution(
        family="fedora",
        name="35",
        release="35",
        image="docker://docker.io/fedora:35",
    )
    FEDORA_36 = LinuxDistribution(
        family="fedora",
        name="36",
        release="36",
        image="docker://docker.io/fedora:36",
    )
    FEDORA_37 = LinuxDistribution(
        family="fedora",
        name="37",
        release="37",
        image="docker://docker.io/fedora:37",
    )
    CENTOS_7 = LinuxDistribution(
        family="centos",
        name="7",
        release="7",
        image="docker://docker.io/centos:7",
    )
    CENTOS_8 = LinuxDistribution(
        family="centos",
        name="8",
        release="8",
        image="docker://docker.io/centos:8",
    )
    ROCKYLINUX_8 = LinuxDistribution(
        family="rockylinux",
        name="8",
        release="8",
        image="docker://docker.io/rockylinux:8",
    )
    OPENSUSE_LEAP_15 = LinuxDistribution(
        family="suse",
        name="leap",
        release="15",
        image="docker://docker.io/opensuse/leap:15",
    )
    OPENSUSE_TUMBLEWEED = LinuxDistribution(
        family="suse",
        name="tumbleweed",
        release="latest",
        image="docker://docker.io/opensuse/tumbleweed:latest",
    )
    ARCHLINUX_20220501 = LinuxDistribution(
        family="archlinux",
        name="20220501",
        release="20220501",
        image="docker://docker.io/archlinux:base-20220501.0.54834",
    )


ALL_DISTRIBUTIONS: List[LinuxDistribution] = [
    OperatingSystem.DEBIAN_STRETCH.value,
    OperatingSystem.DEBIAN_BUSTER.value,
    OperatingSystem.DEBIAN_BULLSEYE.value,
    OperatingSystem.DEBIAN_BOOKWORM.value,
    OperatingSystem.DEBIAN_SID.value,
    OperatingSystem.UBUNTU_FOCAL.value,
    OperatingSystem.UBUNTU_JAMMY.value,
    OperatingSystem.FEDORA_35.value,
    OperatingSystem.FEDORA_36.value,
    OperatingSystem.FEDORA_37.value,
    OperatingSystem.CENTOS_7.value,
    OperatingSystem.CENTOS_8.value,
    OperatingSystem.ROCKYLINUX_8.value,
    OperatingSystem.OPENSUSE_LEAP_15.value,
    OperatingSystem.OPENSUSE_TUMBLEWEED.value,
    OperatingSystem.ARCHLINUX_20220501.value,
]


def find_distribution(image_label: str) -> LinuxDistribution:

    for distribution in ALL_DISTRIBUTIONS:
        if distribution.fullname == image_label:
            return distribution

    raise ValueError(f"Unknown image label {image_label}")


def list_images():
    return [distribution.fullname for distribution in ALL_DISTRIBUTIONS]
