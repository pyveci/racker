# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import json
import logging

import click

from postroj import runner, pkgprobe, selftest
from postroj.api import pull_single_image, pull_multiple_images
from postroj.model import list_images
from postroj.util import setup_logging


@click.group()
@click.version_option()
@click.option('--verbose', is_flag=True, required=False)
@click.option('--debug', is_flag=True, required=False)
@click.pass_context
def cli(ctx: click.Context, verbose: bool, debug: bool):

    # Debugging.
    # click.echo(f"Verbose mode is {'on' if verbose else 'off'}", err=True)
    # click.echo(f"Debug mode is {'on' if debug else 'off'}", err=True)

    # Adjust log level according to subcommand.
    # `postroj run` is more silent by default.
    if ctx.invoked_subcommand == "run":
        log_level = logging.WARNING
    else:
        log_level = logging.INFO

    # Adjust log level according to `verbose` / `debug` flags.
    if verbose:
        log_level = logging.INFO
    if debug:
        log_level = logging.DEBUG

    # Setup logging, according to `verbose` / `debug` flags.
    setup_logging(level=log_level)


@click.command()
@click.pass_context
def cli_list_images(ctx):
    """
    List all available filesystem images
    """
    print(json.dumps(list_images(), indent=2))


@click.command()
@click.argument("name", type=str, required=False)
@click.option("--all", "pull_all", is_flag=True, required=False)
@click.pass_context
def cli_pull_image(ctx, name: str, pull_all: bool = False):
    """
    Pull rootfs images from suitable locations
    """
    if not name and not pull_all:
        raise click.BadOptionUsage(option_name="name", message="Need image name or `--all`")

    if pull_all:
        names = list_images()
        pull_multiple_images(names)
    else:
        pull_single_image(name)


cli.add_command(cmd=cli_list_images, name="list-images")
cli.add_command(cmd=cli_pull_image, name="pull")
cli.add_command(cmd=pkgprobe.main, name="pkgprobe")
cli.add_command(cmd=selftest.selftest_main, name="selftest")
cli.add_command(cmd=runner.main, name="run")
