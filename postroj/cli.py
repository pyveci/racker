# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import json
import sys

import click

import postroj
from postroj import runner, pkgprobe, selftest
from postroj.image import ImageProvider
from postroj.model import list_images, find_distribution


@click.group()
@click.version_option()
@click.option('--debug', required=False)
def cli(debug):
    click.echo(f"Debug mode is {'on' if debug else 'off'}", err=True)


@click.command()
@click.pass_context
def list_images(ctx):
    """
    List all available filesystem images
    """
    print(json.dumps(postroj.model.list_images(), indent=2))


@click.command()
@click.argument("name", type=str)
@click.pass_context
def pull_image(ctx, name: str):
    """
    Pull an image from a suitable location
    """
    try:
        distribution = find_distribution(name)
    except ValueError:
        print(f"ERROR: Image not found: {name}")
        sys.exit(1)

    ip = ImageProvider(distribution=distribution, force=True)
    ip.setup()


cli.add_command(cmd=list_images, name="list-images")
cli.add_command(cmd=pull_image, name="pull")
cli.add_command(cmd=pkgprobe.main, name="pkgprobe")
cli.add_command(cmd=selftest.selftest_main, name="selftest")
# cli.add_command(cmd=runner.main, name="run")
