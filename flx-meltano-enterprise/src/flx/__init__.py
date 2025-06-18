"""
FLX Enterprise Data Platform.

Built on top of Meltano, providing enterprise-grade features for production data pipelines.
"""

__version__ = "2.0.0"
__author__ = "FLX Team"
__email__ = "team@flx.io"

# Export main classes
from flx.config import Settings, settings

__all__ = ["Settings", "settings", "__version__"]
