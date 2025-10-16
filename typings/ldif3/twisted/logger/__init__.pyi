from collections.abc import Iterator, Sequence
from contextlib import contextmanager

from ._interfaces import LogEvent

"""
Context manager for capturing logs.
"""

@contextmanager
def capturedLogs() -> Iterator[Sequence[LogEvent]]: ...
