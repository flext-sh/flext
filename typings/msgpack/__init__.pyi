
from collections.abc import Callable
from datetime import datetime
from typing import IO, TypeAlias

from msgpack.exceptions import (
    BufferFull as BufferFull,
    ExtraData as ExtraData,
    FormatError as FormatError,
    OutOfData as OutOfData,
    PackException as PackException,
    PackOverflowError as PackOverflowError,
    PackValueError as PackValueError,
    StackError as StackError,
    UnpackException as UnpackException,
    UnpackValueError as UnpackValueError,
)
from msgpack.ext import ExtType, Timestamp
from msgpack.fallback import Packer as Packer, Unpacker as Unpacker

version: tuple[int, int, int]
__version__: str

# Msgpack return type: all possible values that unpack can produce
_UnpackedValue: TypeAlias = (
    int
    | float
    | str
    | bool
    | bytes
    | bytearray
    | datetime
    | Timestamp
    | ExtType
    | dict[str, object]
    | list[object]
    | tuple[object, ...]
    | None
)

def pack(
    o: object,
    stream: IO[bytes],
    *,
    default: Callable[..., object] | None = None,
    use_single_float: bool = False,
    autoreset: bool = True,
    use_bin_type: bool = True,
    strict_types: bool = False,
) -> None: ...
def packb(
    o: object,
    *,
    default: Callable[..., object] | None = None,
    use_single_float: bool = False,
    autoreset: bool = True,
    use_bin_type: bool = True,
    strict_types: bool = False,
) -> bytes: ...
def unpack(
    stream: IO[bytes],
    *,
    raw: bool = False,
    use_list: bool = True,
    timestamp: int = 0,
    strict_map_key: bool = True,
    object_hook: Callable[..., object] | None = None,
    object_pairs_hook: Callable[..., object] | None = None,
    unicode_errors: str = "strict",
    ext_hook: Callable[[int, bytes], object] = ...,
) -> _UnpackedValue: ...
def unpackb(
    packed: bytes,
    *,
    raw: bool = False,
    use_list: bool = True,
    timestamp: int = 0,
    strict_map_key: bool = True,
    object_hook: Callable[..., object] | None = None,
    object_pairs_hook: Callable[..., object] | None = None,
    unicode_errors: str = "strict",
    ext_hook: Callable[[int, bytes], object] = ...,
) -> _UnpackedValue: ...

load = unpack
loads = unpackb
dump = pack
dumps = packb
