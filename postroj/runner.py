import sys

import click

from postroj.winrunner import WinRunner


@click.command()
@click.option('--system', type=str)
@click.option('--cpus', type=int)
@click.option('--memory', type=str)
@click.option('--mount', type=str)
@click.argument('command', nargs=-1, type=str)
@click.pass_context
def main(ctx, system, cpus, memory, mount, command):
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
    main()
