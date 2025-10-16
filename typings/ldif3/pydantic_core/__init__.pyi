import datetime
from collections.abc import Callable, Mapping
from typing import Any, Generic, Literal, LiteralString, Self, TypeVar, final

from _typeshed import SupportsAllComparisons
from pydantic_core import ErrorDetails, ErrorTypeInfo, InitErrorDetails, MultiHostHost
from pydantic_core.core_schema import CoreConfig, CoreSchema, ErrorType, ExtraBehavior

__all__ = [
    "ArgsKwargs",
    "MultiHostUrl",
    "PydanticCustomError",
    "PydanticKnownError",
    "PydanticOmit",
    "PydanticSerializationError",
    "PydanticSerializationUnexpectedValue",
    "PydanticUndefined",
    "PydanticUndefinedType",
    "PydanticUseDefault",
    "SchemaError",
    "SchemaSerializer",
    "SchemaValidator",
    "Some",
    "TzInfo",
    "Url",
    "ValidationError",
    "__version__",
    "_recursion_limit",
    "build_info",
    "build_profile",
    "from_json",
    "list_all_errors",
    "to_json",
    "to_jsonable_python",
]
__version__: str
build_profile: str
build_info: str
_recursion_limit: int
_T = TypeVar("_T", default=Any, covariant=True)
type _StringInput = dict[str, _StringInput]

@final
class Some(Generic[_T]):
    __match_args__ = ...
    @property
    def value(self) -> _T: ...
    @classmethod
    def __class_getitem__(cls, item: Any, /) -> type[Self]: ...

@final
class SchemaValidator:
    def __init__(self, schema: CoreSchema, config: CoreConfig | None = ...) -> None: ...
    def __new__(cls, schema: CoreSchema, config: CoreConfig | None = ...) -> Self: ...
    @property
    def title(self) -> str: ...
    def validate_python(
        self,
        input: Any,
        *,
        strict: bool | None = ...,
        extra: ExtraBehavior | None = ...,
        from_attributes: bool | None = ...,
        context: Any | None = ...,
        self_instance: Any | None = ...,
        allow_partial: bool | Literal["off", "on", "trailing-strings"] = ...,
        by_alias: bool | None = ...,
        by_name: bool | None = ...,
    ) -> Any: ...
    def isinstance_python(
        self,
        input: Any,
        *,
        strict: bool | None = ...,
        extra: ExtraBehavior | None = ...,
        from_attributes: bool | None = ...,
        context: Any | None = ...,
        self_instance: Any | None = ...,
        by_alias: bool | None = ...,
        by_name: bool | None = ...,
    ) -> bool: ...
    def validate_json(
        self,
        input: str | bytes | bytearray,
        *,
        strict: bool | None = ...,
        extra: ExtraBehavior | None = ...,
        context: Any | None = ...,
        self_instance: Any | None = ...,
        allow_partial: bool | Literal["off", "on", "trailing-strings"] = ...,
        by_alias: bool | None = ...,
        by_name: bool | None = ...,
    ) -> Any: ...
    def validate_strings(
        self,
        input: _StringInput,
        *,
        strict: bool | None = ...,
        extra: ExtraBehavior | None = ...,
        context: Any | None = ...,
        allow_partial: bool | Literal["off", "on", "trailing-strings"] = ...,
        by_alias: bool | None = ...,
        by_name: bool | None = ...,
    ) -> Any: ...
    def validate_assignment(
        self,
        obj: Any,
        field_name: str,
        field_value: Any,
        *,
        strict: bool | None = ...,
        extra: ExtraBehavior | None = ...,
        from_attributes: bool | None = ...,
        context: Any | None = ...,
        by_alias: bool | None = ...,
        by_name: bool | None = ...,
    ) -> dict[str, Any] | tuple[dict[str, Any], dict[str, Any] | None, set[str]]: ...
    def get_default_value(
        self, *, strict: bool | None = ..., context: Any = ...
    ) -> Some | None: ...

type _IncEx = (
    set[int] | set[str] | Mapping[int, _IncEx | bool] | Mapping[str, _IncEx | bool]
)

@final
class SchemaSerializer:
    def __init__(self, schema: CoreSchema, config: CoreConfig | None = ...) -> None: ...
    def __new__(cls, schema: CoreSchema, config: CoreConfig | None = ...) -> Self: ...
    def to_python(
        self,
        value: Any,
        *,
        mode: str | None = ...,
        include: _IncEx | None = ...,
        exclude: _IncEx | None = ...,
        by_alias: bool | None = ...,
        exclude_unset: bool = ...,
        exclude_defaults: bool = ...,
        exclude_none: bool = ...,
        exclude_computed_fields: bool = ...,
        round_trip: bool = ...,
        warnings: bool | Literal["none", "warn", "error"] = ...,
        fallback: Callable[[Any], Any] | None = ...,
        serialize_as_any: bool = ...,
        context: Any | None = ...,
    ) -> Any: ...
    def to_json(
        self,
        value: Any,
        *,
        indent: int | None = ...,
        ensure_ascii: bool = ...,
        include: _IncEx | None = ...,
        exclude: _IncEx | None = ...,
        by_alias: bool | None = ...,
        exclude_unset: bool = ...,
        exclude_defaults: bool = ...,
        exclude_none: bool = ...,
        exclude_computed_fields: bool = ...,
        round_trip: bool = ...,
        warnings: bool | Literal["none", "warn", "error"] = ...,
        fallback: Callable[[Any], Any] | None = ...,
        serialize_as_any: bool = ...,
        context: Any | None = ...,
    ) -> bytes: ...

def to_json(
    value: Any,
    *,
    indent: int | None = ...,
    ensure_ascii: bool = ...,
    include: _IncEx | None = ...,
    exclude: _IncEx | None = ...,
    by_alias: bool = ...,
    exclude_none: bool = ...,
    round_trip: bool = ...,
    timedelta_mode: Literal["iso8601", "float"] = ...,
    temporal_mode: Literal["iso8601", "seconds", "milliseconds"] = ...,
    bytes_mode: Literal["utf8", "base64", "hex"] = ...,
    inf_nan_mode: Literal["null", "constants", "strings"] = ...,
    serialize_unknown: bool = ...,
    fallback: Callable[[Any], Any] | None = ...,
    serialize_as_any: bool = ...,
    context: Any | None = ...,
) -> bytes: ...
def from_json(
    data: str | bytes | bytearray,
    *,
    allow_inf_nan: bool = ...,
    cache_strings: bool | Literal["all", "keys", "none"] = ...,
    allow_partial: bool | Literal["off", "on", "trailing-strings"] = ...,
) -> Any: ...
def to_jsonable_python(
    value: Any,
    *,
    include: _IncEx | None = ...,
    exclude: _IncEx | None = ...,
    by_alias: bool = ...,
    exclude_none: bool = ...,
    round_trip: bool = ...,
    timedelta_mode: Literal["iso8601", "float"] = ...,
    temporal_mode: Literal["iso8601", "seconds", "milliseconds"] = ...,
    bytes_mode: Literal["utf8", "base64", "hex"] = ...,
    inf_nan_mode: Literal["null", "constants", "strings"] = ...,
    serialize_unknown: bool = ...,
    fallback: Callable[[Any], Any] | None = ...,
    serialize_as_any: bool = ...,
    context: Any | None = ...,
) -> Any: ...

class Url(SupportsAllComparisons):
    def __init__(self, url: str) -> None: ...
    def __new__(cls, url: str) -> Self: ...
    @property
    def scheme(self) -> str: ...
    @property
    def username(self) -> str | None: ...
    @property
    def password(self) -> str | None: ...
    @property
    def host(self) -> str | None: ...
    def unicode_host(self) -> str | None: ...
    @property
    def port(self) -> int | None: ...
    @property
    def path(self) -> str | None: ...
    @property
    def query(self) -> str | None: ...
    def query_params(self) -> list[tuple[str, str]]: ...
    @property
    def fragment(self) -> str | None: ...
    def unicode_string(self) -> str: ...
    def __deepcopy__(self, memo: dict) -> str: ...
    @classmethod
    def build(
        cls,
        *,
        scheme: str,
        username: str | None = ...,
        password: str | None = ...,
        host: str,
        port: int | None = ...,
        path: str | None = ...,
        query: str | None = ...,
        fragment: str | None = ...,
    ) -> Self: ...

class MultiHostUrl(SupportsAllComparisons):
    def __init__(self, url: str) -> None: ...
    def __new__(cls, url: str) -> Self: ...
    @property
    def scheme(self) -> str: ...
    @property
    def path(self) -> str | None: ...
    @property
    def query(self) -> str | None: ...
    def query_params(self) -> list[tuple[str, str]]: ...
    @property
    def fragment(self) -> str | None: ...
    def hosts(self) -> list[MultiHostHost]: ...
    def unicode_string(self) -> str: ...
    def __deepcopy__(self, memo: dict) -> Self: ...
    @classmethod
    def build(
        cls,
        *,
        scheme: str,
        hosts: list[MultiHostHost] | None = ...,
        username: str | None = ...,
        password: str | None = ...,
        host: str | None = ...,
        port: int | None = ...,
        path: str | None = ...,
        query: str | None = ...,
        fragment: str | None = ...,
    ) -> Self: ...

@final
class SchemaError(Exception):
    def error_count(self) -> int: ...
    def errors(self) -> list[ErrorDetails]: ...

class ValidationError(ValueError):
    @classmethod
    def from_exception_data(
        cls,
        title: str,
        line_errors: list[InitErrorDetails],
        input_type: Literal["python", "json"] = ...,
        hide_input: bool = ...,
    ) -> Self: ...
    @property
    def title(self) -> str: ...
    def error_count(self) -> int: ...
    def errors(
        self,
        *,
        include_url: bool = ...,
        include_context: bool = ...,
        include_input: bool = ...,
    ) -> list[ErrorDetails]: ...
    def json(
        self,
        *,
        indent: int | None = ...,
        include_url: bool = ...,
        include_context: bool = ...,
        include_input: bool = ...,
    ) -> str: ...

class PydanticCustomError(ValueError):
    def __init__(
        self,
        error_type: LiteralString,
        message_template: LiteralString,
        context: dict[str, Any] | None = ...,
        /,
    ) -> None: ...
    @property
    def context(self) -> dict[str, Any] | None: ...
    @property
    def type(self) -> str: ...
    @property
    def message_template(self) -> str: ...
    def message(self) -> str: ...

@final
class PydanticKnownError(ValueError):
    def __init__(
        self, error_type: ErrorType, context: dict[str, Any] | None = ..., /
    ) -> None: ...
    @property
    def context(self) -> dict[str, Any] | None: ...
    @property
    def type(self) -> ErrorType: ...
    @property
    def message_template(self) -> str: ...
    def message(self) -> str: ...

@final
class PydanticOmit(Exception):
    def __new__(cls) -> Self: ...

@final
class PydanticUseDefault(Exception):
    def __new__(cls) -> Self: ...

@final
class PydanticSerializationError(ValueError):
    def __init__(self, message: str, /) -> None: ...

@final
class PydanticSerializationUnexpectedValue(ValueError):
    def __init__(self, message: str, /) -> None: ...

@final
class ArgsKwargs:
    def __init__(
        self, args: tuple[Any, ...], kwargs: dict[str, Any] | None = ...
    ) -> None: ...
    def __new__(
        cls, args: tuple[Any, ...], kwargs: dict[str, Any] | None = ...
    ) -> Self: ...
    @property
    def args(self) -> tuple[Any, ...]: ...
    @property
    def kwargs(self) -> dict[str, Any] | None: ...

@final
class PydanticUndefinedType:
    def __copy__(self) -> Self: ...
    def __deepcopy__(self, memo: Any) -> Self: ...

PydanticUndefined: PydanticUndefinedType

def list_all_errors() -> list[ErrorTypeInfo]: ...

@final
class TzInfo(datetime.tzinfo):
    def __init__(self, seconds: float = ...) -> None: ...
    def __new__(cls, seconds: float = ...) -> Self: ...
    def tzname(self, dt: datetime.datetime | None) -> str | None: ...
    def utcoffset(self, dt: datetime.datetime | None) -> datetime.timedelta | None: ...
    def dst(self, dt: datetime.datetime | None) -> datetime.timedelta | None: ...
    def fromutc(self, dt: datetime.datetime) -> datetime.datetime: ...
    def __deepcopy__(self, _memo: dict[Any, Any]) -> TzInfo: ...
