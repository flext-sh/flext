from typing import ClassVar

import google._upb._message
import google.protobuf.message
import internal.invalid.well_known_types

class Any(google._upb._message.Message, google.protobuf.message.Message, internal.invalid.well_known_types.Any):
    DESCRIPTOR: ClassVar[google._upb._message.Descriptor] = ...
