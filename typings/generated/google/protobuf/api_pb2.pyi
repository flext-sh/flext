from typing import ClassVar

import google._upb._message
import google.protobuf.message

class Api(google._upb._message.Message, google.protobuf.message.Message):
    DESCRIPTOR: ClassVar[google._upb._message.Descriptor] = ...

class Method(google._upb._message.Message, google.protobuf.message.Message):
    DESCRIPTOR: ClassVar[google._upb._message.Descriptor] = ...

class Mixin(google._upb._message.Message, google.protobuf.message.Message):
    DESCRIPTOR: ClassVar[google._upb._message.Descriptor] = ...
