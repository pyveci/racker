# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
from pathlib import Path
from typing import Generator

import pytest

from _pytest.monkeypatch import MonkeyPatch

import postroj.model
import postroj.settings


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
