# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import sys

import pytest
from click.testing import CliRunner

from postroj.cli import cli


if sys.platform != "linux":
    pytest.skip("Skipping Linux-only tests", allow_module_level=True)


def test_pkgprobe_webfs(delay):
    """
    Spawn a Debian 9 "stretch" container, install a package from a 3rd party location,
    check if the corresponding systemd service unit is active, and also probe for
    the network server port to be listening.
    """
    runner = CliRunner()

    result = runner.invoke(
        cli,
        "pkgprobe --image=debian-stretch "
        "--package=http://ftp.debian.org/debian/pool/main/w/webfs/webfs_1.21+ds1-12_amd64.deb "
        "--check-unit=webfs --check-network=http://localhost:8000",
    )
    assert result.exit_code == 0
