# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import json

from click.testing import CliRunner

from postroj.cli import cli


def test_list_images():
    runner = CliRunner()

    result = runner.invoke(cli, "list-images", catch_exceptions=False)
    assert result.exit_code == 0

    reference = [
        "debian-stretch",
        "debian-buster",
        "debian-bullseye",
        "debian-bookworm",
        "debian-sid",
        "ubuntu-focal",
        "ubuntu-jammy",
        "fedora-35",
        "fedora-36",
        "fedora-37",
        "opensuse-leap",
        "opensuse-tumbleweed",
        "centos-7",
        "centos-8",
        "rockylinux-8",
        "amazonlinux-2022",
        "oraclelinux-8",
        "archlinux-20220501"
    ]

    assert json.loads(result.stdout) == reference
