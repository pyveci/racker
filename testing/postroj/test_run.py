# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import shlex
import subprocess
import sys
from pathlib import Path

from click.testing import CliRunner

from postroj.cli import cli


def test_run_hostnamectl(capfd):
    """
    Spawn a container and run `hostnamectl` on it.
    Proof that this worked well.
    """
    runner = CliRunner()

    result = runner.invoke(cli, "run -it --rm debian-stretch /usr/bin/hostnamectl", catch_exceptions=False)
    assert result.exit_code == 0

    # FIXME: Why is stdout empty?
    assert result.stdout == ""

    captured = capfd.readouterr()
    assert "Static hostname: debuerreotype" in captured.out
    assert "Virtualization: systemd-nspawn" in captured.out
    assert "Operating System: Debian GNU/Linux 9 (stretch)" in captured.out


def test_run_stdin_stdout(monkeypatch, capsys):
    """
    Spawn a container and write something to its stdin.
    Proof that echoing this to stdout again works well.
    """
    program_path = Path(sys.argv[0]).parent
    postroj = program_path / "postroj"
    command = f"{postroj} run -it --rm debian-buster /bin/cat /dev/stdin"
    process = subprocess.run(shlex.split(command), input=b"foo", stdout=subprocess.PIPE, env={"TESTING": "true"})
    process.check_returncode()
    assert process.stdout == b"foo"


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
