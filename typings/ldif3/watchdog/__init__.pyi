import logging
import re
from collections.abc import Generator
from dataclasses import dataclass
from typing import TYPE_CHECKING

""":module: watchdog.events
:synopsis: File system events and event handlers.
:author: yesudeep@google.com (Yesudeep Mangalapilly)
:author: contact@tiger-222.fr (Mickaël Schoentgen)

Event Classes
-------------
.. autoclass:: FileSystemEvent
   :members:
   :show-inheritance:
   :inherited-members:

.. autoclass:: FileSystemMovedEvent
   :members:
   :show-inheritance:

.. autoclass:: FileMovedEvent
   :members:
   :show-inheritance:

.. autoclass:: DirMovedEvent
   :members:
   :show-inheritance:

.. autoclass:: FileModifiedEvent
   :members:
   :show-inheritance:

.. autoclass:: DirModifiedEvent
   :members:
   :show-inheritance:

.. autoclass:: FileCreatedEvent
   :members:
   :show-inheritance:

.. autoclass:: FileClosedEvent
   :members:
   :show-inheritance:

.. autoclass:: FileClosedNoWriteEvent
   :members:
   :show-inheritance:

.. autoclass:: FileOpenedEvent
   :members:
   :show-inheritance:

.. autoclass:: DirCreatedEvent
   :members:
   :show-inheritance:

.. autoclass:: FileDeletedEvent
   :members:
   :show-inheritance:

.. autoclass:: DirDeletedEvent
   :members:
   :show-inheritance:


Event Handler Classes
---------------------
.. autoclass:: FileSystemEventHandler
   :members:
   :show-inheritance:

.. autoclass:: PatternMatchingEventHandler
   :members:
   :show-inheritance:

.. autoclass:: RegexMatchingEventHandler
   :members:
   :show-inheritance:

.. autoclass:: LoggingEventHandler
   :members:
   :show-inheritance:

"""
if TYPE_CHECKING: ...
EVENT_TYPE_MOVED = ...
EVENT_TYPE_DELETED = ...
EVENT_TYPE_CREATED = ...
EVENT_TYPE_MODIFIED = ...
EVENT_TYPE_CLOSED = ...
EVENT_TYPE_CLOSED_NO_WRITE = ...
EVENT_TYPE_OPENED = ...

@dataclass(unsafe_hash=True)
class FileSystemEvent:
    src_path: bytes | str
    dest_path: bytes | str = ...
    event_type: str = ...
    is_directory: bool = ...
    is_synthetic: bool = ...

class FileSystemMovedEvent(FileSystemEvent):
    event_type = ...

class FileDeletedEvent(FileSystemEvent):
    event_type = ...

class FileModifiedEvent(FileSystemEvent):
    event_type = ...

class FileCreatedEvent(FileSystemEvent):
    event_type = ...

class FileMovedEvent(FileSystemMovedEvent): ...

class FileClosedEvent(FileSystemEvent):
    event_type = ...

class FileClosedNoWriteEvent(FileSystemEvent):
    event_type = ...

class FileOpenedEvent(FileSystemEvent):
    event_type = ...

class DirDeletedEvent(FileSystemEvent):
    event_type = ...
    is_directory = ...

class DirModifiedEvent(FileSystemEvent):
    event_type = ...
    is_directory = ...

class DirCreatedEvent(FileSystemEvent):
    event_type = ...
    is_directory = ...

class DirMovedEvent(FileSystemMovedEvent):
    is_directory = ...

class FileSystemEventHandler:
    def dispatch(self, event: FileSystemEvent) -> None: ...
    def on_any_event(self, event: FileSystemEvent) -> None: ...
    def on_moved(self, event: DirMovedEvent | FileMovedEvent) -> None: ...
    def on_created(self, event: DirCreatedEvent | FileCreatedEvent) -> None: ...
    def on_deleted(self, event: DirDeletedEvent | FileDeletedEvent) -> None: ...
    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None: ...
    def on_closed(self, event: FileClosedEvent) -> None: ...
    def on_closed_no_write(self, event: FileClosedNoWriteEvent) -> None: ...
    def on_opened(self, event: FileOpenedEvent) -> None: ...

class PatternMatchingEventHandler(FileSystemEventHandler):
    def __init__(
        self,
        *,
        patterns: list[str] | None = ...,
        ignore_patterns: list[str] | None = ...,
        ignore_directories: bool = ...,
        case_sensitive: bool = ...,
    ) -> None: ...
    @property
    def patterns(self) -> list[str] | None: ...
    @property
    def ignore_patterns(self) -> list[str] | None: ...
    @property
    def ignore_directories(self) -> bool: ...
    @property
    def case_sensitive(self) -> bool: ...
    def dispatch(self, event: FileSystemEvent) -> None: ...

class RegexMatchingEventHandler(FileSystemEventHandler):
    def __init__(
        self,
        *,
        regexes: list[str] | None = ...,
        ignore_regexes: list[str] | None = ...,
        ignore_directories: bool = ...,
        case_sensitive: bool = ...,
    ) -> None: ...
    @property
    def regexes(self) -> list[re.Pattern[str]]: ...
    @property
    def ignore_regexes(self) -> list[re.Pattern[str]]: ...
    @property
    def ignore_directories(self) -> bool: ...
    @property
    def case_sensitive(self) -> bool: ...
    def dispatch(self, event: FileSystemEvent) -> None: ...

class LoggingEventHandler(FileSystemEventHandler):
    def __init__(self, *, logger: logging.Logger | None = ...) -> None: ...
    def on_moved(self, event: DirMovedEvent | FileMovedEvent) -> None: ...
    def on_created(self, event: DirCreatedEvent | FileCreatedEvent) -> None: ...
    def on_deleted(self, event: DirDeletedEvent | FileDeletedEvent) -> None: ...
    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None: ...
    def on_closed(self, event: FileClosedEvent) -> None: ...
    def on_closed_no_write(self, event: FileClosedNoWriteEvent) -> None: ...
    def on_opened(self, event: FileOpenedEvent) -> None: ...

def generate_sub_moved_events(
    src_dir_path: bytes | str, dest_dir_path: bytes | str
) -> Generator[DirMovedEvent | FileMovedEvent]: ...
def generate_sub_created_events(
    src_dir_path: bytes | str,
) -> Generator[DirCreatedEvent | FileCreatedEvent]: ...
