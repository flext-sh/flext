from typing import ClassVar

import google._upb._message
import google.protobuf.message
import internal.invalid.field_mask

class FieldMask(google._upb._message.Message, google.protobuf.message.Message, internal.invalid.field_mask.FieldMask):
    DESCRIPTOR: ClassVar[google._upb._message.Descriptor] = ...
