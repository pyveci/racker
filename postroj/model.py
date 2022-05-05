# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import dataclasses
from enum import Enum
from typing import List


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
    CENTOS = "centos"


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
        #image="https://cloud.debian.org/images/cloud/buster/latest/debian-10-genericcloud-amd64.tar.xz",
        image="docker://docker.io/debian:buster-slim",
    )
    DEBIAN_BULLSEYE = LinuxDistribution(
        family="debian",
        name="bullseye",
        release="11",
        #image="https://cloud.debian.org/images/cloud/bullseye/latest/debian-11-genericcloud-amd64.tar.xz",
        image="docker://docker.io/debian:bullseye-slim",
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


ALL_DISTRIBUTIONS: List[LinuxDistribution] = [
    OperatingSystem.DEBIAN_STRETCH.value,
    OperatingSystem.DEBIAN_BUSTER.value,
    OperatingSystem.DEBIAN_BULLSEYE.value,
    OperatingSystem.UBUNTU_FOCAL.value,
    OperatingSystem.UBUNTU_JAMMY.value,
    OperatingSystem.CENTOS_7.value,
    OperatingSystem.CENTOS_8.value,
]


def find_distribution(image_label: str) -> LinuxDistribution:

    for distribution in ALL_DISTRIBUTIONS:
        if distribution.fullname == image_label:
            return distribution

    raise ValueError(f"Unknown image label {image_label}")


def list_images():
    return [distribution.fullname for distribution in ALL_DISTRIBUTIONS]
