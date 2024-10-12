import logging
from importlib.metadata import version

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

VERSION = version(__package__)
