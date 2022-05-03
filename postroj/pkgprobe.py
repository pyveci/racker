# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
from typing import List

import click

from postroj.container import PostrojContainer
from postroj.image import ImageProvider
from postroj.model import find_distribution
from postroj.probe import PackageProbe


@click.command()
@click.option('--distribution', type=str)
@click.option('--package', type=str)
@click.option('--unit-is-active', type=str, multiple=True)
@click.option('--tcp-is-listening', type=str, multiple=True)
@click.pass_context
def main(ctx, distribution: str, package: str, unit_is_active: List[str], tcp_is_listening: List[str]):

    # Figure out the distribution from the list of available ones.
    dist = find_distribution(distribution)

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
        probe.invoke(package=package, units=unit_is_active, listen=tcp_is_listening)
