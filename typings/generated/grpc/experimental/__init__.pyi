from typing import ClassVar

import grpc as grpc
from grpc._simple_stubs import (
    stream_stream as stream_stream,
    stream_unary as stream_unary,
    unary_stream as unary_stream,
    unary_unary as unary_unary,
)

__all__ = ['ChannelOptions', 'ExperimentalApiWarning', 'UsageError', 'insecure_channel_credentials', 'stream_stream', 'stream_unary', 'unary_stream', 'unary_unary', 'wrap_server_method_handler']

class ChannelOptions:
    SingleThreadedUnaryStream: ClassVar[str] = ...

class UsageError(Exception): ...
def insecure_channel_credentials(): ...

class ExperimentalApiWarning(Warning): ...
def wrap_server_method_handler(wrapper, handler): ...

# Names in __all__ with no definition:
#   stream_stream
#   stream_unary
#   unary_stream
#   unary_unary
