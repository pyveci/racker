# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import dataclasses
from enum import Enum
from pathlib import Path
from typing import Union


@dataclasses.dataclass
class ConfigurationOptions:
    archive_directory: Path = None
    image_directory: Path = None
    cache_directory: Path = None

    @property
    def download_directory(self) -> Path:
        return self.cache_directory / "downloads"


class OperatingSystemFamily(Enum):
    DEBIAN = "debian"
    REDHAT = "redhat"
    SUSE = "suse"
    ARCHLINUX = "archlinux"


class OperatingSystemName(Enum):
    DEBIAN = "debian"
    UBUNTU = "ubuntu"
    FEDORA = "fedora"
    CENTOS = "centos"
    RHEL = "rhel"
    ROCKYLINUX = "rockylinux"
    ARCHLINUX = "archlinux"
    OPENSUSE = "opensuse"
    SLES = "sles"
    AMAZONLINUX = "amazonlinux"
    ORACLELINUX = "oraclelinux"


@dataclasses.dataclass
class LinuxDistribution:
    family: Union[OperatingSystemFamily, None]
    name: OperatingSystemName
    release: str
    version: str
    image: str

    @property
    def fullname(self):
        return f"{self.name.value}-{self.release}"

    @property
    def versionname(self):
        return f"{self.name.value}-{self.version}"
