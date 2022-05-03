# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import json

import click

import postroj
from postroj import runner, pkgprobe
from postroj.model import list_images


@click.group()
@click.version_option()
@click.option('--debug', required=False)
def cli(debug):
    click.echo(f"Debug mode is {'on' if debug else 'off'}", err=True)


@click.command()
@click.pass_context
def list_images(ctx):
    print(json.dumps(postroj.model.list_images(), indent=2))


cli.add_command(cmd=runner.main, name="run")
cli.add_command(cmd=pkgprobe.main, name="pkgprobe")
cli.add_command(cmd=list_images, name="list-images")
