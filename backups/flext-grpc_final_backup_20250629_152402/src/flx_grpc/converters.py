"""Protocol Buffer utility functions for converting between data types."""

from __future__ import annotations

from typing import TYPE_CHECKING

from google.protobuf import struct_pb2, timestamp_pb2

if TYPE_CHECKING:
    from datetime import datetime


def datetime_to_timestamp(dt: datetime) -> timestamp_pb2.Timestamp:
    """Convert datetime to protobuf timestamp."""
    timestamp = timestamp_pb2.Timestamp()
    timestamp.FromDatetime(dt)
    return timestamp


def dict_to_struct(data: dict[str, object]) -> struct_pb2.Struct:
    """Convert dictionary to protobuf struct."""
    struct = struct_pb2.Struct()
    struct.update(data)  # type: ignore[arg-type]
    return struct


def struct_to_dict(struct: struct_pb2.Struct) -> dict[str, object]:
    """Convert protobuf struct to dictionary."""
    return dict(struct)
