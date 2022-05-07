# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
from click.testing import CliRunner

from postroj.cli import cli


def test_racker_run(capfd):
    runner = CliRunner()

    result = runner.invoke(cli, "run -it --rm debian-stretch /usr/bin/hostnamectl", catch_exceptions=False)
    assert result.exit_code == 0

    # FIXME: Why is stdout empty?
    assert result.stdout == ""

    captured = capfd.readouterr()
    assert "Static hostname: debuerreotype" in captured.out
    assert "Virtualization: systemd-nspawn" in captured.out
    assert "Operating System: Debian GNU/Linux 9 (stretch)" in captured.out
