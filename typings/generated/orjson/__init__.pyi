import json.decoder
from . import orjson as orjson
from builtins import JSONEncodeError as JSONEncodeError
from typing import ClassVar

__all__ = ['__version__', 'dumps', 'Fragment', 'JSONDecodeError', 'JSONEncodeError', 'loads', 'OPT_APPEND_NEWLINE', 'OPT_INDENT_2', 'OPT_NAIVE_UTC', 'OPT_NON_STR_KEYS', 'OPT_OMIT_MICROSECONDS', 'OPT_PASSTHROUGH_DATACLASS', 'OPT_PASSTHROUGH_DATETIME', 'OPT_PASSTHROUGH_SUBCLASS', 'OPT_SERIALIZE_DATACLASS', 'OPT_SERIALIZE_NUMPY', 'OPT_SERIALIZE_UUID', 'OPT_SORT_KEYS', 'OPT_STRICT_INTEGER', 'OPT_UTC_Z']

dumps: builtin_function_or_method
loads: builtin_function_or_method

class Fragment:
    __new__: ClassVar[builtin_function_or_method] = ...
OPT_APPEND_NEWLINE: int
OPT_INDENT_2: int
OPT_NAIVE_UTC: int
OPT_NON_STR_KEYS: int
OPT_OMIT_MICROSECONDS: int
OPT_PASSTHROUGH_DATACLASS: int
OPT_PASSTHROUGH_DATETIME: int
OPT_PASSTHROUGH_SUBCLASS: int
OPT_SERIALIZE_DATACLASS: int
OPT_SERIALIZE_NUMPY: int
OPT_SERIALIZE_UUID: int
OPT_SORT_KEYS: int
OPT_STRICT_INTEGER: int
OPT_UTC_Z: int

class JSONDecodeError(json.decoder.JSONDecodeError): ...
__version__: str

# Names in __all__ with no definition:
#   JSONEncodeError
