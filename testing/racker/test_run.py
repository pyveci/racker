# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import shlex
import subprocess
import sys
from pathlib import Path

import pytest
from click._compat import strip_ansi
from click.testing import CliRunner

from racker.cli import cli


if sys.platform != "linux":
    pytest.skip("Skipping Linux-only tests", allow_module_level=True)


def test_run_image_invalid(caplog):
    """
    Spawning a container with an invalid image label should fail.
    """
    runner = CliRunner()

    runner.invoke(cli, "run -it --rm foo true", catch_exceptions=False)
    assert "Acquiring filesystem image failed" in caplog.text
    # assert "Error reading manifest latest in docker.io/library/foo" in caplog.text


def test_run_command_docker_image_success(capfd, delay):
    """
    Spawn a Debian 9 "stretch" container and run `hostnamectl` on it.
    The container image will be acquired from Docker.
    """
    runner = CliRunner()

    result = runner.invoke(cli, "run -it --rm debian:stretch-slim /usr/bin/hostnamectl", catch_exceptions=False)
    assert result.exit_code == 0

    captured = capfd.readouterr()

    assert "Static hostname: debuerreotype" in captured.out
    assert "Virtualization: systemd-nspawn" in captured.out
    assert "Operating System: Debian GNU/Linux 9 (stretch)" in captured.out
    assert captured.err == ""


def test_run_command_curated_cloudimage_success(capfd, delay):
    """
    Spawn an Ubuntu 22 "jammy" container and run `hostnamectl` on it.
    The container image will be derived from the upstream cloud image tarball.
    """
    runner = CliRunner()

    result = runner.invoke(cli, "run -it --rm ubuntu-jammy /usr/bin/hostnamectl", catch_exceptions=False)
    assert result.exit_code == 0

    captured = capfd.readouterr()

    assert "Static hostname: ubuntu" in captured.out
    assert "Virtualization: systemd-nspawn" in captured.out
    assert "Operating System: Ubuntu 22.04" in captured.out
    assert captured.err == ""


def test_run_command_failure_path_not_absolute(capfd, delay):
    """
    Running an invalid command on a container should croak.
    """
    runner = CliRunner()

    result = runner.invoke(cli, "run -it --rm debian:stretch-slim foo", catch_exceptions=False)
    assert result.exit_code == 1

    captured = capfd.readouterr()

    output = strip_ansi(captured.err).strip()
    assert output == "Failed to start transient service unit: Path foo is not absolute."


def test_run_command_failure_command_not_found(caplog, delay):
    """
    Running an invalid command on a container should croak.
    """
    runner = CliRunner()

    result = runner.invoke(cli, "run -it --rm debian:stretch-slim /bin/foo", catch_exceptions=False)
    assert result.exit_code == 203

    assert "Running command in container" in caplog.text
    assert "Reason: /bin/foo: No such file or directory" in caplog.text


def test_run_stdin_stdout(monkeypatch, capsys, delay):
    """
    Spawn a container and write something to its stdin.
    Proof that echoing this to stdout again works well.
    """
    program_path = Path(sys.argv[0]).parent
    racker = program_path / "racker"
    command = f"{racker} run -it --rm debian:stretch-slim /bin/cat /dev/stdin"
    process = subprocess.run(shlex.split(command), input=b"foo", stdout=subprocess.PIPE, env={"TESTING": "true"})
    process.check_returncode()
    assert process.stdout == b"foo"


# Unfortunately, this fails.
"""
def test_run_stdin_stdout_original(capfd):
    runner = CliRunner()

    sys.stdin = io.BytesIO(b"foo")
    result = runner.invoke(cli, "run -it --rm debian:stretch-slim /bin/cat /dev/stdin", input=b"foo", catch_exceptions=False)
    assert result.exit_code == 0

    # FIXME: Why is stdout empty?
    assert result.stdout == ""

    captured = capfd.readouterr()
    assert captured.out == "foo"
"""


# TODO: Provoke `Directory tree /var/lib/testdrive/postroj/archive/debian-stretch-slim.img/rootfs is currently busy.`, by
#       a) running a command while the container is still running.
#       b) trying to start a container twice.
