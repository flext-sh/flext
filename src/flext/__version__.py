"""Flext - Version Information.

This is the single source of truth for version information.
All references to version should import from this module.

Usage:
    from flext.__version__ import __version__
    print(f"Version: {__version__}")
"""

__version__ = "0.6.0"
try:
    __version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())
except ValueError:
    __version_info__ = (0, 6, 0)

# Backwards compatibility
VERSION = __version__
version = __version__
