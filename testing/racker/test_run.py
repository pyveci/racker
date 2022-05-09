# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import shlex
import subprocess
import sys
from pathlib import Path

import pytest
from click._compat import strip_ansi
from click.testing import CliRunner

from postroj.racker.cli import cli


def test_run_image_invalid():
    """
    Spawning a container with an invalid image label should fail.
    """
    runner = CliRunner()

    with pytest.raises(ValueError) as ex:
        runner.invoke(cli, "run -it --rm foo true", catch_exceptions=False)
    assert ex.match("Unknown image label: foo")


def test_run_command_success():
    """
    Spawn a container and run `hostnamectl` on it.
    Proof that this worked well.
    """
    runner = CliRunner()

    result = runner.invoke(cli, "run -it --rm debian-stretch /usr/bin/hostnamectl", catch_exceptions=False)
    assert result.exit_code == 0

    assert "Static hostname: debuerreotype" in result.stdout
    assert "Virtualization: systemd-nspawn" in result.stdout
    assert "Operating System: Debian GNU/Linux 9 (stretch)" in result.stdout


def test_run_command_failure():
    """
    Running an invalid command on a container should croak.
    """
    runner = CliRunner()

    result = runner.invoke(cli, "run -it --rm debian-buster foo", catch_exceptions=False)
    assert result.exit_code == 1

    output = strip_ansi(result.output).strip()
    assert output == "Failed to start transient service unit: Path foo is not absolute."


def test_run_stdin_stdout(monkeypatch, capsys):
    """
    Spawn a container and write something to its stdin.
    Proof that echoing this to stdout again works well.
    """
    program_path = Path(sys.argv[0]).parent
    racker = program_path / "racker"
    command = f"{racker} run -it --rm debian-bullseye /bin/cat /dev/stdin"
    process = subprocess.run(shlex.split(command), input=b"foo", stdout=subprocess.PIPE, env={"TESTING": "true"})
    process.check_returncode()
    assert process.stdout == b"foo\n"


# Unfortunately, this fails.
"""
def test_run_stdin_stdout_original(capfd):
    runner = CliRunner()

    sys.stdin = io.BytesIO(b"foo")
    result = runner.invoke(cli, "run -it --rm debian-bullseye /bin/cat /dev/stdin", input=b"foo", catch_exceptions=False)
    assert result.exit_code == 0

    # FIXME: Why is stdout empty?
    assert result.stdout == ""

    captured = capfd.readouterr()
    assert captured.out == "foo"
"""
