# Lazy imports to avoid circular dependencies
# Lazy import to avoid circular dependencies
# Lazy import to avoid circular dependencies
from flx.utils.lazy_import import lazy_import

"""Engine components for FLX platform."""

# Lazy import to avoid circular dependencies
MeltanoEngine = lazy_import("flx.engine.meltano_wrapper", "MeltanoEngine")

__all__ = ["MeltanoEngine"]
