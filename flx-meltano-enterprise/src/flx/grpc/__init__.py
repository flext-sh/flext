# Lazy imports to avoid circular dependencies
# Lazy import to avoid circular dependencies
# Lazy import to avoid circular dependencies
from flx.utils.lazy_import import lazy_import

"""gRPC components for FLX platform."""

# Lazy import to avoid circular dependencies
FlxGrpcServer = lazy_import("flx.grpc.server", "FlxGrpcServer")

__all__ = ["FlxGrpcServer"]
