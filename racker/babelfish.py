# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import dataclasses
import logging

from furl import furl
from slugify import slugify
from tld import get_tld

from postroj.model import LinuxDistribution

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class DynamicDistribution(LinuxDistribution):
    """
    An operating system type shim used when acquiring Docker filesystem images
    where nothing is known upfront about the nature of the operating system,
    if there is any at all.
    """

    @property
    def fullname(self):
        """
        Docker image names for canonical operating systems look like those.

        - docker://docker.io/fedora:36
        - docker://docker.io/debian:bullseye-slim
        - docker://docker.io/opensuse/tumbleweed:latest
        - docker://docker.io/archlinux:base-20220501.0.54834

        By slugifying them, we derive a name suitable to be used on a filesystem
        path, to `/var/lib/postroj/{name}`.

        - docker-docker-io-fedora-37
        - docker-docker-io-debian-stretch-slim
        - docker-docker-io-ubuntu-jammy
        - docker-docker-io-opensuse-tumbleweed-latest
        - docker-docker-io-archlinux-base-20220501-0-54834
        """
        return slugify(self.image)

    @property
    def versionname(self):
        """
        Addressing the version is not implemented yet, so just return the full name.
        """
        return self.fullname

    @classmethod
    def empty(cls):
        """
        Factory method to create an empty instance.
        """
        return cls(family=None, name="None", release="None", version=None, image=None)

    @classmethod
    def from_image(cls, image: str):
        """
        Factory method to create a shim instance, only carrying the Docker image name forward.
        """
        dist = cls(family=None, name=None, release=None, version=None, image=image)
        dist.resolve_docker_image_label()
        logger.info(f"Effective image is {dist.image}")
        return dist

    def resolve_docker_image_label(self):
        """
        Adjust source image URI.

        When parsing image labels as URLs, make sure labels are well understood and
        not accidentally misinterpreted with `scheme == "debian"`, `port == "bullseye-slim"`
        or `host == opensuse`.

        - debian:bullseye-slim
        - opensuse/tumbleweed:latest
        - ghcr.io/jpmens/mqttwarn-standard

        Accepted image labels.

        - archlinux
        - fedora:36
        - debian:bullseye-slim
        - opensuse/tumbleweed:latest
        - docker.io/debian:bullseye-slim
        - docker.io/debian:bullseye-slim
        - ghcr.io/jpmens/mqttwarn-standard

        Also with `docker://` prefix.

        - docker://fedora:36
        - docker://ghcr.io/jpmens/mqttwarn-standard
        """
        if self.image.startswith("docker://"):
            return
        image_uri = furl("/" + self.image)
        if image_uri.scheme is None and image_uri.host is None:
            do_prefix = False

            # `debian:bullseye-slim` croaks with `ValueError: Invalid port 'bullseye-slim'.`
            image_probe = "docker://" + self.image
            try:
                image_uri = furl(image_probe)
            except ValueError as ex:
                if "Invalid port" not in str(ex):
                    raise
                do_prefix = True

            if not do_prefix:
                if image_uri.host is None:
                    do_prefix = True
                else:
                    try:
                        get_tld(f"foo://{image_uri.host}")
                    except:
                        do_prefix = True

            if do_prefix:
                image_probe = "docker://docker.io/" + self.image
            self.image = image_probe
