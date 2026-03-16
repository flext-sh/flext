"""Type stubs for msgpack._cmsgpack C extension.

The C extension provides the same interface as the pure-Python fallback.
"""

from msgpack.fallback import Packer as Packer, Unpacker as Unpacker, unpackb as unpackb
