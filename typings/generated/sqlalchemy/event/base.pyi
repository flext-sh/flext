import typing
import weakref
from typing import Any, ClassVar

from _typeshed import Incomplete
from sqlalchemy.event.attr import _InstanceLevelDispatch, _JoinedListener
from sqlalchemy.event.registry import _ET

__conditional_annotations__: set

class _UnpickleDispatch:
    def __call__(self, _instance_cls: type[_ET]) -> _Dispatch[_ET]: ...

class _DispatchCommon(typing.Generic):
    __orig_bases__: ClassVar[tuple] = ...
    __parameters__: ClassVar[tuple] = ...
    def __getattr__(self, name: str) -> _InstanceLevelDispatch[_ET]: ...

class _Dispatch(_DispatchCommon):
    _empty_listener_reg: ClassVar[weakref.WeakKeyDictionary] = ...
    __orig_bases__: ClassVar[tuple] = ...
    __parameters__: ClassVar[tuple] = ...
    def __init__(self, parent: _Dispatch[_ET] | None, instance_cls: type[_ET] | None = ...) -> None: ...
    def __getattr__(self, name: str) -> _InstanceLevelDispatch[_ET]: ...
    def __reduce__(self) -> str | tuple[Any, ...]: ...

class _HasEventsDispatch(typing.Generic):
    __orig_bases__: ClassVar[tuple] = ...
    __parameters__: ClassVar[tuple] = ...
    @classmethod
    def __init_subclass__(cls) -> None: ...

class _JoinedDispatcher(_DispatchCommon):
    __orig_bases__: ClassVar[tuple] = ...
    __parameters__: ClassVar[tuple] = ...
    local: Incomplete
    parent: Incomplete
    def __init__(self, local: _DispatchCommon[_ET], parent: _DispatchCommon[_ET]) -> None: ...
    def __reduce__(self) -> Any: ...
    def __getattr__(self, name: str) -> _JoinedListener[_ET]: ...

class JoinedEventsDispatch(_JoinedDispatcher):
    __parameters__: ClassVar[tuple] = ...

class Events(_HasEventsDispatch):
    __orig_bases__: ClassVar[tuple] = ...
    dispatch: ClassVar[EventsDispatch] = ...

class dispatcher(typing.Generic):
    __orig_bases__: ClassVar[tuple] = ...
    __parameters__: ClassVar[tuple] = ...
    def __init__(self, events: type[_HasEventsDispatch[_ET]]) -> None: ...
    def __get__(self, obj: Any, cls: type[Any]) -> Any: ...

class slots_dispatcher(dispatcher):
    __orig_bases__: ClassVar[tuple] = ...
    __parameters__: ClassVar[tuple] = ...
    def __get__(self, obj: Any, cls: type[Any]) -> Any: ...

class JoinedPoolEventsDispatch(_JoinedDispatcher):
    __parameters__: ClassVar[tuple] = ...
    checkin: Incomplete
    checkout: Incomplete
    close: Incomplete
    close_detached: Incomplete
    connect: Incomplete
    detach: Incomplete
    first_connect: Incomplete
    invalidate: Incomplete
    reset: Incomplete
    soft_invalidate: Incomplete

class JoinedDDLEventsDispatch(_JoinedDispatcher):
    __parameters__: ClassVar[tuple] = ...
    after_create: Incomplete
    after_drop: Incomplete
    after_parent_attach: Incomplete
    before_create: Incomplete
    before_drop: Incomplete
    before_parent_attach: Incomplete
    column_reflect: Incomplete

class JoinedConnectionEventsDispatch(_JoinedDispatcher):
    __parameters__: ClassVar[tuple] = ...
    after_cursor_execute: Incomplete
    after_execute: Incomplete
    before_cursor_execute: Incomplete
    before_execute: Incomplete
    begin: Incomplete
    begin_twophase: Incomplete
    commit: Incomplete
    commit_twophase: Incomplete
    engine_connect: Incomplete
    engine_disposed: Incomplete
    prepare_twophase: Incomplete
    release_savepoint: Incomplete
    rollback: Incomplete
    rollback_savepoint: Incomplete
    rollback_twophase: Incomplete
    savepoint: Incomplete
    set_connection_execution_options: Incomplete
    set_engine_execution_options: Incomplete

class JoinedDialectEventsDispatch(_JoinedDispatcher):
    __parameters__: ClassVar[tuple] = ...
    do_connect: Incomplete
    do_execute: Incomplete
    do_execute_no_params: Incomplete
    do_executemany: Incomplete
    do_setinputsizes: Incomplete
    handle_error: Incomplete

class JoinedInstrumentationEventsDispatch(_JoinedDispatcher):
    __parameters__: ClassVar[tuple] = ...
    attribute_instrument: Incomplete
    class_instrument: Incomplete
    class_uninstrument: Incomplete

class JoinedInstanceEventsDispatch(_JoinedDispatcher):
    __parameters__: ClassVar[tuple] = ...
    expire: Incomplete
    first_init: Incomplete
    init: Incomplete
    init_failure: Incomplete
    load: Incomplete
    pickle: Incomplete
    refresh: Incomplete
    refresh_flush: Incomplete
    unpickle: Incomplete

class JoinedHoldInstanceEventsDispatch(_JoinedDispatcher):
    __parameters__: ClassVar[tuple] = ...
    expire: Incomplete
    first_init: Incomplete
    init: Incomplete
    init_failure: Incomplete
    load: Incomplete
    pickle: Incomplete
    refresh: Incomplete
    refresh_flush: Incomplete
    unpickle: Incomplete

class JoinedMapperEventsDispatch(_JoinedDispatcher):
    __parameters__: ClassVar[tuple] = ...
    after_configured: Incomplete
    after_delete: Incomplete
    after_insert: Incomplete
    after_mapper_constructed: Incomplete
    after_update: Incomplete
    before_configured: Incomplete
    before_delete: Incomplete
    before_insert: Incomplete
    before_mapper_configured: Incomplete
    before_update: Incomplete
    instrument_class: Incomplete
    mapper_configured: Incomplete

class JoinedHoldMapperEventsDispatch(_JoinedDispatcher):
    __parameters__: ClassVar[tuple] = ...
    after_configured: Incomplete
    after_delete: Incomplete
    after_insert: Incomplete
    after_mapper_constructed: Incomplete
    after_update: Incomplete
    before_configured: Incomplete
    before_delete: Incomplete
    before_insert: Incomplete
    before_mapper_configured: Incomplete
    before_update: Incomplete
    instrument_class: Incomplete
    mapper_configured: Incomplete

class JoinedSessionEventsDispatch(_JoinedDispatcher):
    __parameters__: ClassVar[tuple] = ...
    after_attach: Incomplete
    after_begin: Incomplete
    after_bulk_delete: Incomplete
    after_bulk_update: Incomplete
    after_commit: Incomplete
    after_flush: Incomplete
    after_flush_postexec: Incomplete
    after_rollback: Incomplete
    after_soft_rollback: Incomplete
    after_transaction_create: Incomplete
    after_transaction_end: Incomplete
    before_attach: Incomplete
    before_commit: Incomplete
    before_flush: Incomplete
    deleted_to_detached: Incomplete
    deleted_to_persistent: Incomplete
    detached_to_persistent: Incomplete
    do_orm_execute: Incomplete
    loaded_as_persistent: Incomplete
    pending_to_persistent: Incomplete
    pending_to_transient: Incomplete
    persistent_to_deleted: Incomplete
    persistent_to_detached: Incomplete
    persistent_to_transient: Incomplete
    transient_to_pending: Incomplete

class JoinedAttributeEventsDispatch(_JoinedDispatcher):
    __parameters__: ClassVar[tuple] = ...
    append: Incomplete
    append_wo_mutation: Incomplete
    bulk_replace: Incomplete
    dispose_collection: Incomplete
    init_collection: Incomplete
    init_scalar: Incomplete
    modified: Incomplete
    remove: Incomplete
    set: Incomplete

class JoinedQueryEventsDispatch(_JoinedDispatcher):
    __parameters__: ClassVar[tuple] = ...
    before_compile: Incomplete
    before_compile_delete: Incomplete
    before_compile_update: Incomplete
