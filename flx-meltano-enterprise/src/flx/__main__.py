
# Lazy imports to avoid circular dependencies
# Lazy import to avoid circular dependencies
# Lazy import to avoid circular dependencies
from flx.utils.lazy_import import lazy_import

"""
FLX Daemon entry point.
"""

# Lazy import to avoid circular dependencies
main = lazy_import('flx.daemon', 'main')

if __name__ == "__main__":
    main()
