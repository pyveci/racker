# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
from pathlib import Path

from postroj.model import ConfigurationOptions

appsettings = ConfigurationOptions(
    archive_directory=Path("/var/lib/postroj/archive"),
    image_directory=Path("/var/lib/postroj/images"),
    cache_directory=Path("/var/cache/postroj"),
)


def get_appsettings():
    return appsettings
