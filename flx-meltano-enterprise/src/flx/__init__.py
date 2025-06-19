
# Lazy imports to avoid circular dependencies
# Lazy import to avoid circular dependencies
# Lazy import to avoid circular dependencies
from flx.utils.lazy_import import lazy_import

"""
FLX Enterprise Data Platform.

Built on top of Meltano, providing enterprise-grade features for production data pipelines.
"""

__version__ = "2.0.0"
__author__ = "FLX Team"
__email__ = "team@flx.io"

# Export main classes
# Lazy imports to avoid circular dependencies
Settings = lazy_import('flx.config', 'Settings')
settings = lazy_import('flx.config', 'settings')

__all__ = ["Settings", "settings", "__version__"]
