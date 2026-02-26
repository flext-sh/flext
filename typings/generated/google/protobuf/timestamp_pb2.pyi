from typing import ClassVar

import google._upb._message
import google.protobuf.message
import internal.invalid.well_known_types

class Timestamp(google._upb._message.Message, google.protobuf.message.Message, internal.invalid.well_known_types.Timestamp):
    DESCRIPTOR: ClassVar[google._upb._message.Descriptor] = ...
