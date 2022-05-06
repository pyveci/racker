# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import sys
from typing import List

from postroj.image import ImageProvider
from postroj.model import find_distribution


def pull_single_image(name: str):
    try:
        distribution = find_distribution(name)
    except ValueError:
        print(f"ERROR: Image not found: {name}")
        sys.exit(1)

    ip = ImageProvider(distribution=distribution, force=True)
    ip.setup()


def pull_multiple_images(names: List[str]):
    for name in names:
        try:
            pull_single_image(name)
        except Exception as ex:
            print(f"ERROR: Failed pulling image {name}. Reason: {ex}")
