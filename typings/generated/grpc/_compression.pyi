import grpc as grpc
import grpc._cython.cygrpc as cygrpc

__all__ = ['NoCompression', 'Deflate', 'Gzip']

NoCompression: int
Deflate: int
Gzip: int
