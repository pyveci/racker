# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import io
import logging
import sys
from contextlib import redirect_stderr, redirect_stdout

import click

from postroj.container import PostrojContainer
from postroj.image import ImageProvider
from postroj.registry import find_distribution
from postroj.util import boot

logger = logging.getLogger(__name__)


@click.group()
@click.version_option(package_name="racker")
@click.option("--verbose", is_flag=True, required=False)
@click.option("--debug", is_flag=True, required=False)
@click.pass_context
def cli(ctx: click.Context, verbose: bool, debug: bool):
    return boot(ctx, verbose, debug)


@click.command()
@click.argument("name", type=str, required=True)
@click.pass_context
def racker_pull(ctx, name: str):
    """
    Pull rootfs images from suitable locations
    """
    raise NotImplementedError("Hm?")


@click.command()
@click.option("--interactive", "-i", is_flag=True)
@click.option("--tty", "-t", is_flag=True)
@click.option("--rm", is_flag=True)
@click.argument("image", type=str, required=False)
@click.argument("command", nargs=-1, type=str)
@click.pass_context
def racker_run(ctx, interactive: bool, tty: bool, rm: bool, image: str, command: str):
    """
    Spawn a container and run a command on it.
    Aims to be compatible with `docker run`.
    """

    """
    Goal
    ====

    Translate between those invocations and fill the gaps::

        docker run -it --rm debian:bullseye-slim bash
        systemd-run --machine=debian-bullseye --pty bash

    Progress
    ========
    ::

        # Works
        racker run -it --rm debian-bullseye bash
        # TODO: Advanced image resolution
        racker run -it --rm debian:bullseye-slim bash
    """

    verbose = ctx.parent.params.get("verbose", False)
    debug = ctx.parent.params.get("debug", False)

    # Adjust command line arguments and options.
    command = " ".join(command)
    use_pty = False
    if interactive or tty:
        use_pty = True

    # Figure out the image from the list of available ones.
    # TODO: Add more advanced image registry, maybe using `docker-py`,
    #       resolving image names from postroj-internal images, Docker Hub,
    #       GHCR, etc.
    dist = find_distribution(image)

    # Status reporting.
    logger.info(f"Invoking command '{command}' on {dist}")

    # Acquire rootfs filesystem image.
    ip = ImageProvider(distribution=dist)
    rootfs = ip.image

    # TODO: Combine verbose + capturing by employing some Tee-like multiplexing.
    if debug:
        stdout = sys.stderr
        stderr = sys.stderr
    else:
        stdout = io.StringIO()
        stderr = io.StringIO()

    # Boot container and run command.
    with PostrojContainer(rootfs=rootfs) as pc:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                pc.boot()
                pc.wait()
        pc.run(command, use_pty=use_pty)


cli.add_command(cmd=racker_pull, name="pull")
cli.add_command(cmd=racker_run, name="run")
