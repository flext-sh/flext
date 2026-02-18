import google.protobuf.descriptor as descriptor_mod
import internal.invalid.api_implementation as api_implementation
import internal.invalid.containers as containers
import internal.invalid.decoder as decoder
import internal.invalid.encoder as encoder
import internal.invalid.enum_type_wrapper as enum_type_wrapper
import internal.invalid.extension_dict as extension_dict
import internal.invalid.message_listener as message_listener_mod
import internal.invalid.type_checkers as type_checkers
import internal.invalid.well_known_types as well_known_types
import internal.invalid.wire_format as wire_format
import google.protobuf.message as message_mod
import google.protobuf.text_format as text_format
from _typeshed import Incomplete
from typing import ClassVar

class GeneratedProtocolMessageType(type):
    _DESCRIPTOR_KEY: ClassVar[str] = ...
    @classmethod
    def __init__(cls, name, bases, dictionary) -> None: ...

class _FieldProperty(property):
    DESCRIPTOR: Incomplete
    def __init__(self, descriptor, getter, setter, doc) -> None: ...

class _Listener:
    def __init__(self, parent_message) -> None: ...
    def Modified(self): ...

class _OneofListener(_Listener):
    def __init__(self, parent_message, field) -> None: ...
    def Modified(self): ...
