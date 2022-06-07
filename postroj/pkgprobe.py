# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import io
import logging
import os
import sys
from contextlib import redirect_stdout
from functools import partial
from typing import List

import click

from postroj.container import PostrojContainer
from postroj.image import ImageProvider
from postroj.probe import ProbeBase
from postroj.registry import find_distribution
from postroj.settings import get_appsettings
from postroj.util import noop

logger = logging.getLogger(__name__)


@click.command()
@click.option("--image", type=str)
@click.option("--package", type=str)
@click.option("--check-unit", type=str, multiple=True)
@click.option("--check-network", type=str, multiple=True)
@click.option("--network-timeout", type=float, default=5.0)
@click.pass_context
def main(ctx, image: str, package: str, check_unit: List[str], check_network: List[str], network_timeout: float = 5.0):
    """
    Verify a distribution package
    """

    if sys.platform != "linux":
        raise NotImplementedError(f"Unable to launch Linux systems on non-Linux machines yet, "
                                  f"please use the Vagrant setup")

    # Figure out the image from the list of available ones.
    dist = find_distribution(image)

    # Status reporting.
    logger.info(f"Testing package {package} on distribution {dist}")

    # Acquire rootfs filesystem image.
    ip = ImageProvider(distribution=dist)
    rootfs = ip.image

    # TODO: Adjust verbosity.
    silent_boot = True
    ctx = noop
    if silent_boot:
        ctx = partial(redirect_stdout, io.StringIO())

    # Boot container and run probe commands.
    with PostrojContainer(image_path=rootfs) as pc:
        with ctx():
            pc.boot()
            pc.wait()
        pc.info()

        probe = PackageProbe(container=pc)
        probe.setup(package=package, unit_names=check_unit)
        probe.check(unit_names=check_unit, network_addresses=check_network, network_timeout=network_timeout)


class PackageProbe(ProbeBase):
    """
    Acquire a distribution package (.deb or .rpm), install it, and verify that
    a) a corresponding systemd unit is properly started and "active", and
    b) the service responds to network requests on designated ports.
    """

    def setup(self, package: str, unit_names: List[str]):

        self.install(package)
        for unit in unit_names:
            self.start(unit)

    def install(self, package: str):

        if package is None:
            return

        settings = get_appsettings()

        logger.info(f"Setting up package {package}")

        # Download package.
        if package.startswith("http"):
            logger.info(f"Downloading {package}")
            self.run(
                f"/usr/bin/wget --continue --no-clobber --directory-prefix={settings.download_directory} {package}"
            )
            package = settings.download_directory / os.path.basename(package)
        else:
            raise ValueError(f"Unable to acquire package at {package}")

        # Install package.
        logger.info(f"Installing package {package}")
        if self.is_debian:
            self.run(f"/usr/bin/apt-get install --yes {package}")
        elif self.is_redhat:
            self.run(f"/usr/bin/yum install -y {package}")
        elif self.is_suse:
            """
            Problem
            =======

            zypper install says::

                nothing provides 'systemd-units' needed by the to be installed

            rpm --install says::

                error: Failed dependencies:
                    shadow-utils is needed by crate-4.7.2-1.x86_64
                    systemd-units is needed by crate-4.7.2-1.x86_64
            """
            # self.run(f"/usr/bin/zypper --non-interactive install {package}")
            self.run(f"/usr/bin/rpm --install --nodeps {package}")
        else:
            raise ValueError(f"Unable to install package {package}. Reason: Unsupported operating system.")

    def start(self, unit: str):
        if unit not in ["systemd-journald"]:
            self.run(f"/bin/systemctl enable {unit}")
        self.run(f"/bin/systemctl start {unit}")

    def check(self, unit_names: List[str], network_addresses: List[str], network_timeout: float = 5.0):
        """
        Run probes.

        1. The systemd unit has to be "active".
        2. The designated ports should be available.
        """
        for unit in unit_names:
            self.check_unit(unit)
        for address in network_addresses:
            self.check_address(address, timeout=network_timeout)
