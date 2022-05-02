# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import click

from postroj import runner


@click.group()
@click.version_option()
@click.option('--debug', required=False)
def cli(debug):
    click.echo(f"Debug mode is {'on' if debug else 'off'}")


cli.add_command(cmd=runner.main, name="run")
