"""Type stubs for msgpack._cmsgpack C extension.

The C extension provides the same interface as the pure-Python fallback.
"""

from __future__ import annotations

from msgpack.fallback import Packer as Packer
from msgpack.fallback import Unpacker as Unpacker
from msgpack.fallback import unpackb as unpackb
