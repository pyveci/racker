# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import time
from pathlib import Path
from typing import Generator
from unittest.mock import patch

import pytest
from _pytest.monkeypatch import MonkeyPatch

import postroj.model
import postroj.settings
from postroj.image import ImageProvider
from racker.babelfish import DynamicDistribution


@pytest.fixture(scope="session")
def monkeypatch_session() -> Generator[MonkeyPatch, None, None]:
    """
    Like the original `monkeypatch` fixture, but session-scoped.
    """
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="session", autouse=True)
def adjust_storage_paths(monkeypatch_session):
    """
    Provision test environment with different storage paths.
    """
    appsettings = postroj.model.ConfigurationOptions(
        archive_directory=Path("/var/lib/testdrive/postroj/archive"),
        image_directory=Path("/var/lib/testdrive/postroj/images"),
        cache_directory=Path("/var/cache/testdrive/postroj"),
    )
    monkeypatch_session.setattr(postroj.settings, "appsettings", appsettings)


@pytest.fixture
def delay():
    """
    Needed to give the container some time to settle after use. Otherwise, the test suite is
    timing-sensitive re.::

        Directory tree /var/lib/testdrive/postroj/archive/debian-stretch-slim.img/rootfs is currently busy.

    FIXME: Can be removed after proper "wait-for-teardown" has been implemented.
    """
    time.sleep(0.25)


@pytest.fixture
def fakeroot(tmpdir):
    path = Path(tmpdir)
    (path / "etc").mkdir()
    (path / "etc" / "os-release").touch()
    return path


@pytest.fixture
def fakeimage(fakeroot):
    distribution = DynamicDistribution.from_image("foo")
    ip = ImageProvider(distribution=distribution, autosetup=False)
    ip.image_staging = fakeroot
    return ip


@pytest.fixture
def scmd_mock():
    with patch("postroj.image.scmd") as scmd:
        yield scmd


@pytest.fixture
def scmd_first_command(scmd_mock):
    def invoker():
        scmd_mock.assert_called_once()
        kwargs = scmd_mock.call_args[1]
        command = kwargs["command"]
        return command

    return invoker


@pytest.fixture
def hcmd_mock():
    with patch("postroj.image.hcmd") as hcmd:
        yield hcmd
