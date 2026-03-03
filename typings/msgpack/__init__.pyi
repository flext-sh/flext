"""Type stubs for msgpack.

Consolidated from flext-api/src/msgpack.pyi into workspace typings.
"""

import os

from flext_core import t

from .exceptions import *

version = ...
__version__ = ...
if os.environ.get("MSGPACK_PUREPYTHON"): ...

def pack(o: object, stream: object, **kwargs: object) -> None:
    """Pack object `o` and write it to `stream`.

    See :class:`Packer` for options.
    """

def packb(o: object, **kwargs: object) -> bytes:
    """Pack object `o` and return packed bytes.

    See :class:`Packer` for options.
    """

def unpack(
    stream: object, **kwargs: object
) -> t.Scalar | dict[str, object] | list[object] | None:
    """Unpack an object from `stream`.

    Raises `ExtraData` when `stream` contains extra bytes.
    See :class:`Unpacker` for options.
    """

def unpackb(
    data: bytes, **kwargs: object
) -> t.Scalar | dict[str, object] | list[object] | None:
    """Unpack an object from `data` bytes.

    See :class:`Unpacker` for options.
    """

load = ...
loads = ...
dump = ...
dumps = ...
