try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:  # pragma: no cover
    import importlib_metadata

from .__main__ import main

__all__ = ["main", "__version__"]

__version__ = importlib_metadata.version(__name__)
