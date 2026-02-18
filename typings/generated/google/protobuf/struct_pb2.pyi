import google._upb._message
import google.protobuf.descriptor as _descriptor
import google.protobuf.descriptor_pool as _descriptor_pool
import internal.invalid.builder as _builder
import internal.invalid.well_known_types
import google.protobuf.message
import google.protobuf.runtime_version as _runtime_version
import google.protobuf.symbol_database as _symbol_database
from typing import ClassVar

NULL_VALUE: int

class Struct(google._upb._message.Message, google.protobuf.message.Message, internal.invalid.well_known_types.Struct):
    class FieldsEntry(google._upb._message.Message, google.protobuf.message.Message):
        DESCRIPTOR: ClassVar[google._upb._message.Descriptor] = ...
    DESCRIPTOR: ClassVar[google._upb._message.Descriptor] = ...

class Value(google._upb._message.Message, google.protobuf.message.Message):
    DESCRIPTOR: ClassVar[google._upb._message.Descriptor] = ...

class ListValue(google._upb._message.Message, google.protobuf.message.Message, internal.invalid.well_known_types.ListValue):
    DESCRIPTOR: ClassVar[google._upb._message.Descriptor] = ...
