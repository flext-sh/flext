
from typing import Any

def packb(
    obj: Any,
    default: Any = ...,
    use_single_float: bool = ...,
    autoreset: bool = ...,
    use_bin_type: bool = ...,
    strict_types: bool = ...,
    datetime: bool = ...,
    unicode_errors: str = ...,
) -> bytes: ...

def unpackb(
    packed: bytes,
    *,
    raw: bool = ...,
    use_list: bool = ...,
    strict_map_key: bool = ...,
    object_hook: Any = ...,
    object_pairs_hook: Any = ...,
    list_hook: Any = ...,
    unicode_errors: str = ...,
    ext_hook: Any = ...,
    max_str_len: int = ...,
    max_bin_len: int = ...,
    max_array_len: int = ...,
    max_map_len: int = ...,
    max_ext_len: int = ...,
) -> Any: ...

version: str

class ExtType:
    code: int
    data: bytes
    def __new__(cls, code: int, data: bytes) -> ExtType: ...

class OutOfData(Exception): ...
class UnpackException(Exception): ...
class PackException(Exception): ...

__all__: list[str]
