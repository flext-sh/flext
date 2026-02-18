import grpc as grpc
import grpc._cython.cygrpc as _cygrpc
from grpc._simple_stubs import stream_stream as stream_stream, stream_unary as stream_unary, unary_stream as unary_stream, unary_unary as unary_unary
from typing import ClassVar

__all__ = ['ChannelOptions', 'ExperimentalApiWarning', 'UsageError', 'insecure_channel_credentials', 'wrap_server_method_handler', 'unary_unary', 'unary_stream', 'stream_unary', 'stream_stream']

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
