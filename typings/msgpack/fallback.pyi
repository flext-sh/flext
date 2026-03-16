

from collections.abc import Callable, Iterable, Iterator
from datetime import datetime
from io import IOBase
from typing import Self, TypeAlias

from msgpack.ext import ExtType, Timestamp

_UnpackedValue: TypeAlias = (
    int
    | float
    | str
    | bytes
    | bytearray
    | bool
    | list[object]
    | tuple[object, ...]
    | dict[object, object]
    | datetime
    | Timestamp
    | ExtType
    | None
)

_USING_STRINGBUILDER: bool

class BytesIO:
    def __init__(self, s: bytes = ...) -> None: ...
    def write(self, s: bytes | bytearray | memoryview) -> None: ...
    def getvalue(self) -> bytes: ...

def newlist_hint(size: int) -> list[object]: ...

EX_SKIP: int
EX_CONSTRUCT: int
EX_READ_ARRAY_HEADER: int
EX_READ_MAP_HEADER: int
TYPE_IMMEDIATE: int
TYPE_ARRAY: int
TYPE_MAP: int
TYPE_RAW: int
TYPE_BIN: int
TYPE_EXT: int
DEFAULT_RECURSE_LIMIT: int

def unpackb(packed: bytes | bytearray | memoryview, **kwargs: object) -> _UnpackedValue:
    ...

_NO_FORMAT_USED: str
_MSGPACK_HEADERS: dict[int, tuple[int, str] | tuple[int, str, int]]

class Unpacker(Iterator[_UnpackedValue]):
    

    def __init__(
        self,
        file_like: IOBase | None = ...,
        *,
        read_size: int = ...,
        use_list: bool = ...,
        raw: bool = ...,
        timestamp: int = ...,
        strict_map_key: bool = ...,
        object_hook: Callable[[dict[object, object]], object] | None = ...,
        object_pairs_hook: Callable[[list[tuple[object, object]]], object] | None = ...,
        list_hook: Callable[[list[object]], list[object]] | None = ...,
        unicode_errors: str | None = ...,
        max_buffer_size: int = ...,
        ext_hook: Callable[[int, bytes], ExtType] = ...,
        max_str_len: int = ...,
        max_bin_len: int = ...,
        max_array_len: int = ...,
        max_map_len: int = ...,
        max_ext_len: int = ...,
    ) -> None: ...
    def feed(self, next_bytes: bytes | bytearray | memoryview) -> None: ...
    def read_bytes(self, n: int) -> bytearray: ...
    def __iter__(self) -> Self: ...
    def __next__(self) -> _UnpackedValue: ...
    next = __next__
    def skip(self) -> None: ...
    def unpack(self) -> _UnpackedValue: ...
    def read_array_header(self) -> int: ...
    def read_map_header(self) -> int: ...
    def tell(self) -> int: ...

class Packer:
    

    def __init__(
        self,
        *,
        default: Callable[[object], object] | None = ...,
        use_single_float: bool = ...,
        autoreset: bool = ...,
        use_bin_type: bool = ...,
        strict_types: bool = ...,
        datetime: bool = ...,
        unicode_errors: str | None = ...,
        buf_size: int | None = ...,
    ) -> None: ...
    def pack(self, obj: object) -> bytes | None: ...
    def pack_map_pairs(
        self, pairs: Iterable[tuple[object, object]]
    ) -> bytes | None: ...
    def pack_array_header(self, n: int) -> bytes | None: ...
    def pack_map_header(self, n: int) -> bytes | None: ...
    def pack_ext_type(self, typecode: int, data: bytes) -> None: ...
    def bytes(self) -> bytes:
        ...
    def reset(self) -> None:
        ...
    def getbuffer(self) -> memoryview:
        ...
