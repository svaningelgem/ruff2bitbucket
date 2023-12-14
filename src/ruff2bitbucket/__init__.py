from .__main__ import main
from importlib.metadata import version as md_version

__all__ = ["main", "__version__"]

__version__ = md_version(__name__)
