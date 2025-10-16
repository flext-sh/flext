from collections.abc import Callable, Mapping, Sequence
from typing import (
    Any,
    TypeVar,
    dataclass_transform,
    overload,
)

from attr import (
    NOTHING as NOTHING,
    Attribute as Attribute,
    AttrsInstance as AttrsInstance,
    Converter as Converter,
    Factory as Factory,
    NothingType as NothingType,
    __author__ as __author__,
    __copyright__ as __copyright__,
    __description__ as __description__,
    __email__ as __email__,
    __license__ as __license__,
    __title__ as __title__,
    __url__ as __url__,
    __version__ as __version__,
    __version_info__ as __version_info__,
    asdict as asdict,
    assoc as assoc,
    astuple as astuple,
    attrib,
    cmp_using as cmp_using,
    converters as converters,
    evolve as evolve,
    exceptions as exceptions,
    fields as fields,
    fields_dict as fields_dict,
    filters as filters,
    has as has,
    make_class as make_class,
    resolve_types as resolve_types,
    setters as setters,
    validate as validate,
    validators as validators,
)

_T = TypeVar("_T")
_C = TypeVar("_C", bound=type)
type _EqOrderType = bool | Callable[[Any], Any]
type _ValidatorType[_T] = Callable[[Any, Attribute[_T], _T], Any]
type _CallableConverterType = Callable[[Any], Any]
type _ConverterType = _CallableConverterType | Converter[Any, Any]
type _ReprType = Callable[[Any], str]
type _ReprArgType = bool | _ReprType
type _OnSetAttrType = Callable[[Any, Attribute[Any], Any], Any]
type _OnSetAttrArgType = _OnSetAttrType | list[_OnSetAttrType] | setters._NoOpType
type _FieldTransformer = Callable[[type, list[Attribute[Any]]], list[Attribute[Any]]]
type _ValidatorArgType[_T] = _ValidatorType[_T] | Sequence[_ValidatorType[_T]]

@overload
def field(
    *,
    default: None = ...,
    validator: None = ...,
    repr: _ReprArgType = ...,
    hash: bool | None = ...,
    init: bool = ...,
    metadata: Mapping[Any, Any] | None = ...,
    converter: None = ...,
    factory: None = ...,
    kw_only: bool | None = ...,
    eq: bool | None = ...,
    order: bool | None = ...,
    on_setattr: _OnSetAttrArgType | None = ...,
    alias: str | None = ...,
    type: type | None = ...,
) -> Any: ...
@overload
def field(
    *,
    default: None = ...,
    validator: _ValidatorArgType[_T] | None = ...,
    repr: _ReprArgType = ...,
    hash: bool | None = ...,
    init: bool = ...,
    metadata: Mapping[Any, Any] | None = ...,
    converter: _ConverterType
    | list[_ConverterType]
    | tuple[_ConverterType, ...]
    | None = ...,
    factory: Callable[[], _T] | None = ...,
    kw_only: bool | None = ...,
    eq: _EqOrderType | None = ...,
    order: _EqOrderType | None = ...,
    on_setattr: _OnSetAttrArgType | None = ...,
    alias: str | None = ...,
    type: type | None = ...,
) -> _T: ...
@overload
def field(
    *,
    default: _T,
    validator: _ValidatorArgType[_T] | None = ...,
    repr: _ReprArgType = ...,
    hash: bool | None = ...,
    init: bool = ...,
    metadata: Mapping[Any, Any] | None = ...,
    converter: _ConverterType
    | list[_ConverterType]
    | tuple[_ConverterType, ...]
    | None = ...,
    factory: Callable[[], _T] | None = ...,
    kw_only: bool | None = ...,
    eq: _EqOrderType | None = ...,
    order: _EqOrderType | None = ...,
    on_setattr: _OnSetAttrArgType | None = ...,
    alias: str | None = ...,
    type: type | None = ...,
) -> _T: ...
@overload
def field(
    *,
    default: _T | None = ...,
    validator: _ValidatorArgType[_T] | None = ...,
    repr: _ReprArgType = ...,
    hash: bool | None = ...,
    init: bool = ...,
    metadata: Mapping[Any, Any] | None = ...,
    converter: _ConverterType
    | list[_ConverterType]
    | tuple[_ConverterType, ...]
    | None = ...,
    factory: Callable[[], _T] | None = ...,
    kw_only: bool | None = ...,
    eq: _EqOrderType | None = ...,
    order: _EqOrderType | None = ...,
    on_setattr: _OnSetAttrArgType | None = ...,
    alias: str | None = ...,
    type: type | None = ...,
) -> Any: ...
@overload
@dataclass_transform(field_specifiers=(attrib, field))
def define[C: type](
    maybe_cls: _C,
    *,
    these: dict[str, Any] | None = ...,
    repr: bool = ...,
    unsafe_hash: bool | None = ...,
    hash: bool | None = ...,
    init: bool = ...,
    slots: bool = ...,
    frozen: bool = ...,
    weakref_slot: bool = ...,
    str: bool = ...,
    auto_attribs: bool = ...,
    kw_only: bool = ...,
    cache_hash: bool = ...,
    auto_exc: bool = ...,
    eq: bool | None = ...,
    order: bool | None = ...,
    auto_detect: bool = ...,
    getstate_setstate: bool | None = ...,
    on_setattr: _OnSetAttrArgType | None = ...,
    field_transformer: _FieldTransformer | None = ...,
    match_args: bool = ...,
) -> _C: ...
@overload
@dataclass_transform(field_specifiers=(attrib, field))
def define(
    maybe_cls: None = ...,
    *,
    these: dict[str, Any] | None = ...,
    repr: bool = ...,
    unsafe_hash: bool | None = ...,
    hash: bool | None = ...,
    init: bool = ...,
    slots: bool = ...,
    frozen: bool = ...,
    weakref_slot: bool = ...,
    str: bool = ...,
    auto_attribs: bool = ...,
    kw_only: bool = ...,
    cache_hash: bool = ...,
    auto_exc: bool = ...,
    eq: bool | None = ...,
    order: bool | None = ...,
    auto_detect: bool = ...,
    getstate_setstate: bool | None = ...,
    on_setattr: _OnSetAttrArgType | None = ...,
    field_transformer: _FieldTransformer | None = ...,
    match_args: bool = ...,
) -> Callable[[_C], _C]: ...

mutable = ...

@overload
@dataclass_transform(frozen_default=True, field_specifiers=(attrib, field))
def frozen[C: type](
    maybe_cls: _C,
    *,
    these: dict[str, Any] | None = ...,
    repr: bool = ...,
    unsafe_hash: bool | None = ...,
    hash: bool | None = ...,
    init: bool = ...,
    slots: bool = ...,
    frozen: bool = ...,
    weakref_slot: bool = ...,
    str: bool = ...,
    auto_attribs: bool = ...,
    kw_only: bool = ...,
    cache_hash: bool = ...,
    auto_exc: bool = ...,
    eq: bool | None = ...,
    order: bool | None = ...,
    auto_detect: bool = ...,
    getstate_setstate: bool | None = ...,
    on_setattr: _OnSetAttrArgType | None = ...,
    field_transformer: _FieldTransformer | None = ...,
    match_args: bool = ...,
) -> _C: ...
@overload
@dataclass_transform(frozen_default=True, field_specifiers=(attrib, field))
def frozen(
    maybe_cls: None = ...,
    *,
    these: dict[str, Any] | None = ...,
    repr: bool = ...,
    unsafe_hash: bool | None = ...,
    hash: bool | None = ...,
    init: bool = ...,
    slots: bool = ...,
    frozen: bool = ...,
    weakref_slot: bool = ...,
    str: bool = ...,
    auto_attribs: bool = ...,
    kw_only: bool = ...,
    cache_hash: bool = ...,
    auto_exc: bool = ...,
    eq: bool | None = ...,
    order: bool | None = ...,
    auto_detect: bool = ...,
    getstate_setstate: bool | None = ...,
    on_setattr: _OnSetAttrArgType | None = ...,
    field_transformer: _FieldTransformer | None = ...,
    match_args: bool = ...,
) -> Callable[[_C], _C]: ...

class ClassProps:
    Hashability: Any
    KeywordOnly: Any
    is_exception: bool
    is_slotted: bool
    has_weakref_slot: bool
    is_frozen: bool
    kw_only: Any
    collected_fields_by_mro: bool
    added_init: bool
    added_repr: bool
    added_eq: bool
    added_ordering: bool
    hashability: Any
    added_match_args: bool
    added_str: bool
    added_pickling: bool
    on_setattr_hook: _OnSetAttrType | None
    field_transformer: Callable[[Attribute[Any]], Attribute[Any]] | None
    def __init__(
        self,
        is_exception: bool,
        is_slotted: bool,
        has_weakref_slot: bool,
        is_frozen: bool,
        kw_only: Any,
        collected_fields_by_mro: bool,
        added_init: bool,
        added_repr: bool,
        added_eq: bool,
        added_ordering: bool,
        hashability: Any,
        added_match_args: bool,
        added_str: bool,
        added_pickling: bool,
        on_setattr_hook: _OnSetAttrType,
        field_transformer: Callable[[Attribute[Any]], Attribute[Any]],
    ) -> None: ...
    @property
    def is_hashable(self) -> bool: ...

def inspect(cls: type) -> ClassProps: ...
