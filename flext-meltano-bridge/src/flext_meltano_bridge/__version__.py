"""Flext Meltano Bridge - Version Information.

This is the single source of truth for version information.
All references to version should import from this module.

Usage:
    from flext_meltano_bridge.__version__ import __version__
    print(f"Version: {__version__}")
"""

__version__ = "0.6.0"
__version_info__ = tuple(map(int, __version__.split(".")))

# Backwards compatibility
VERSION = __version__
version = __version__
