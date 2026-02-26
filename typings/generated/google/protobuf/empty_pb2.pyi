from typing import ClassVar

import google._upb._message
import google.protobuf.message

class Empty(google._upb._message.Message, google.protobuf.message.Message):
    DESCRIPTOR: ClassVar[google._upb._message.Descriptor] = ...
