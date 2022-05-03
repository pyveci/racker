# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
from typing import List

import click

from postroj.container import PostrojContainer
from postroj.image import ImageProvider
from postroj.model import find_distribution
from postroj.probe import PackageProbe


@click.command()
@click.option('--image', type=str)
@click.option('--package', type=str)
@click.option('--check-unit', type=str, multiple=True)
@click.option('--check-network', type=str, multiple=True)
@click.option('--network-timeout', type=float, default=5.0)
@click.pass_context
def main(ctx, image: str, package: str, check_unit: List[str], check_network: List[str], network_timeout: float = 5.0):

    # Figure out the image from the list of available ones.
    dist = find_distribution(image)

    # Status reporting.
    print(f"Testing package {package} on distribution {dist}")

    # Acquire rootfs filesystem image.
    ip = ImageProvider(distribution=dist)
    rootfs = ip.image

    if not rootfs.exists():
        ip.setup()

    # Boot container and run probe commands.
    with PostrojContainer(rootfs=rootfs) as pc:
        pc.boot()
        pc.wait()
        pc.info()

        probe = PackageProbe(container=pc)
        probe.invoke(package=package, unit_names=check_unit, network_addresses=check_network, network_timeout=network_timeout)
