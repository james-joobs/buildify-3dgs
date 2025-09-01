"""Buildify 3D Gaussian Splatting - Python API"""

try:
    from .pybuildify import *
    from .pybuildify import __version__
except ImportError as e:
    import warnings
    warnings.warn(f"Failed to import C++ extensions: {e}")
    __version__ = "0.1.0"

__all__ = ["core", "utils", "__version__"]