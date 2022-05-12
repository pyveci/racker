# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import logging
import sys

import click

from postroj.winrunner import WinRunner
from racker.cli import racker_run

logger = logging.getLogger(__name__)


@click.command()
@click.option("--system", type=str)
@click.option("--cpus", type=int)
@click.option("--memory", type=str)
@click.option("--mount", type=str)
@click.argument("command", nargs=-1, type=str)
@click.pass_context
def invoke(ctx, system, cpus, memory, mount, command):
    """
    Run a command within a designated system environment
    """
    # TODO: Propagate and implement `cpus`, `memory` and `mount`. See
    command = " ".join(command)
    if system == "windows-1809":
        runner = WinRunner()
        runner.setup()
        runner.start()
        outcome = runner.run(command)
        sys.stdout.write(outcome)
    else:
        raise NotImplementedError(f'Runtime system "{system}" not supported yet')


if __name__ == "__main__":
    racker_run()
