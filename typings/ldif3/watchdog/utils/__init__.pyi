import os
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any

""":module: watchdog.utils.dirsnapshot
:synopsis: Directory snapshots and comparison.
:author: yesudeep@google.com (Yesudeep Mangalapilly)
:author: contact@tiger-222.fr (Mickaël Schoentgen)

.. ADMONITION:: Where are the moved events? They "disappeared"

        This implementation does not take partition boundaries
        into consideration. It will only work when the directory
        tree is entirely on the same file system. More specifically,
        any part of the code that depends on inode numbers can
        break if partition boundaries are crossed. In these cases,
        the snapshot diff will represent file/directory movement as
        created and deleted events.

Classes
-------
.. autoclass:: DirectorySnapshot
   :members:
   :show-inheritance:

.. autoclass:: DirectorySnapshotDiff
   :members:
   :show-inheritance:

.. autoclass:: EmptyDirectorySnapshot
   :members:
   :show-inheritance:

"""
if TYPE_CHECKING: ...

class DirectorySnapshotDiff:
    def __init__(
        self,
        ref: DirectorySnapshot,
        snapshot: DirectorySnapshot,
        *,
        ignore_device: bool = ...,
    ) -> None: ...
    @property
    def files_created(self) -> list[bytes | str]: ...
    @property
    def files_deleted(self) -> list[bytes | str]: ...
    @property
    def files_modified(self) -> list[bytes | str]: ...
    @property
    def files_moved(self) -> list[tuple[bytes | str, bytes | str]]: ...
    @property
    def dirs_modified(self) -> list[bytes | str]: ...
    @property
    def dirs_moved(self) -> list[tuple[bytes | str, bytes | str]]: ...
    @property
    def dirs_deleted(self) -> list[bytes | str]: ...
    @property
    def dirs_created(self) -> list[bytes | str]: ...

    class ContextManager:
        def __init__(
            self,
            path: str,
            *,
            recursive: bool = ...,
            stat: Callable[[str], os.stat_result] = ...,
            listdir: Callable[[str | None], Iterator[os.DirEntry]] = ...,
            ignore_device: bool = ...,
        ) -> None: ...
        def __enter__(self) -> None: ...
        def __exit__(self, *args: object) -> None: ...
        def get_snapshot(self) -> DirectorySnapshot: ...

class DirectorySnapshot:
    def __init__(
        self,
        path: str,
        *,
        recursive: bool = ...,
        stat: Callable[[str], os.stat_result] = ...,
        listdir: Callable[[str | None], Iterator[os.DirEntry]] = ...,
    ) -> None: ...
    def walk(self, root: str) -> Iterator[tuple[str, os.stat_result]]: ...
    @property
    def paths(self) -> set[bytes | str]: ...
    def path(self, uid: tuple[int, int]) -> bytes | str | None: ...
    def inode(self, path: bytes | str) -> tuple[int, int]: ...
    def isdir(self, path: bytes | str) -> bool: ...
    def mtime(self, path: bytes | str) -> float: ...
    def size(self, path: bytes | str) -> int: ...
    def stat_info(self, path: bytes | str) -> os.stat_result: ...
    def __sub__(self, previous_dirsnap: DirectorySnapshot) -> DirectorySnapshotDiff: ...

class EmptyDirectorySnapshot(DirectorySnapshot):
    def __init__(self) -> None: ...
    @staticmethod
    def path(_: Any) -> None: ...
    @property
    def paths(self) -> set: ...
