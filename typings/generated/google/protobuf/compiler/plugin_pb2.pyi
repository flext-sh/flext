from typing import ClassVar

import google._upb._message
import google.protobuf.message

class Version(google._upb._message.Message, google.protobuf.message.Message):
    DESCRIPTOR: ClassVar[google._upb._message.Descriptor] = ...

class CodeGeneratorRequest(google._upb._message.Message, google.protobuf.message.Message):
    DESCRIPTOR: ClassVar[google._upb._message.Descriptor] = ...

class CodeGeneratorResponse(google._upb._message.Message, google.protobuf.message.Message):
    class File(google._upb._message.Message, google.protobuf.message.Message):
        DESCRIPTOR: ClassVar[google._upb._message.Descriptor] = ...
    DESCRIPTOR: ClassVar[google._upb._message.Descriptor] = ...
