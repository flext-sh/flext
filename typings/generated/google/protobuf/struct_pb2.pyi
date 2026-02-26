from typing import ClassVar

import google._upb._message
import google.protobuf.message
import internal.invalid.well_known_types

NULL_VALUE: int

class Struct(google._upb._message.Message, google.protobuf.message.Message, internal.invalid.well_known_types.Struct):
    class FieldsEntry(google._upb._message.Message, google.protobuf.message.Message):
        DESCRIPTOR: ClassVar[google._upb._message.Descriptor] = ...
    DESCRIPTOR: ClassVar[google._upb._message.Descriptor] = ...

class Value(google._upb._message.Message, google.protobuf.message.Message):
    DESCRIPTOR: ClassVar[google._upb._message.Descriptor] = ...

class ListValue(google._upb._message.Message, google.protobuf.message.Message, internal.invalid.well_known_types.ListValue):
    DESCRIPTOR: ClassVar[google._upb._message.Descriptor] = ...
