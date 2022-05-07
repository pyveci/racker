# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import logging
from typing import List

from postroj.image import ImageProvider
from postroj.model import find_distribution

logger = logging.getLogger(__name__)


def pull_single_image(name: str):
    """
    Resolve image label and pull artefacts from network.
    """
    distribution = find_distribution(name)
    return ImageProvider(distribution=distribution, force=True)


def pull_multiple_images(names: List[str]):
    """
    Pull multiple images from network.
    """
    providers: List[ImageProvider] = []
    for name in names:
        try:
            provider = pull_single_image(name)
            providers.append(provider)
        except Exception as ex:
            logger.error(f"Failed pulling image {name}. Reason: {ex}")
    return providers
