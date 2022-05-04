# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
from pathlib import Path


# TODO: Make those configurable.
archive_directory = Path("/var/lib/postroj/archive")
image_directory = Path("/var/lib/postroj/images")
cache_directory = Path("/var/cache/postroj")
download_directory = cache_directory / "downloads"
