from postroj.image import ImageProvider
from racker.babelfish import DynamicDistribution, logger


class ImageLibrary:
    """
    An adapter for pulling operating system images solely from Docker images.
    """

    def __init__(self):
        pass

    def acquire(self, name: str):
        logger.info(f"Acquiring Docker image {name}")
        distribution = DynamicDistribution.from_image(name)
        logger.info(f"Using {distribution}")
        provider = ImageProvider(distribution=distribution)
        return provider.image
