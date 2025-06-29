"""File system watcher for plugin hot reload functionality.

Copyright (c) 2025 FLX Team. All rights reserved.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class WatchEventType(Enum):
    """Types of file system events."""

    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"


class WatchEvent(BaseModel):
    """File system watch event."""

    event_type: WatchEventType = Field(description="Type of file system event")
    path: Path = Field(description="Path that triggered the event")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    old_path: Optional[Path] = Field(
        default=None, description="Old path for move events"
    )

    class Config:
        arbitrary_types_allowed = True


class FileMetadata(BaseModel):
    """Metadata for tracked files."""

    path: Path
    size: int
    mtime: float
    hash: str
    last_checked: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Config:
        arbitrary_types_allowed = True


class PluginWatcher:
    """File system watcher for plugin directories.

    Monitors plugin directories for changes and triggers reload events.
    Uses polling-based approach for cross-platform compatibility.
    """

    def __init__(
        self,
        watch_directories: List[Path],
        poll_interval: float = 1.0,
        patterns: Optional[List[str]] = None,
        ignore_patterns: Optional[List[str]] = None,
    ) -> None:
        """Initialize plugin watcher.

        Args:
        ----
            watch_directories: Directories to watch
            poll_interval: Polling interval in seconds
            patterns: File patterns to watch (e.g., ["*.py"])
            ignore_patterns: File patterns to ignore

        """
        self.watch_directories = [Path(d) for d in watch_directories]
        self.poll_interval = poll_interval
        self.patterns = patterns or ["*.py"]
        self.ignore_patterns = ignore_patterns or ["__pycache__", "*.pyc", ".git"]

        self._watching = False
        self._watch_task: Optional[asyncio.Task] = None
        self._file_metadata: Dict[Path, FileMetadata] = {}
        self._event_handlers: List[Callable[[WatchEvent], asyncio.Future]] = []

    def add_handler(self, handler: Callable[[WatchEvent], asyncio.Future]) -> None:
        """Add event handler.

        Args:
        ----
            handler: Async function to handle watch events

        """
        self._event_handlers.append(handler)

    def remove_handler(self, handler: Callable[[WatchEvent], asyncio.Future]) -> None:
        """Remove event handler.

        Args:
        ----
            handler: Handler to remove

        """
        if handler in self._event_handlers:
            self._event_handlers.remove(handler)

    async def start(self) -> None:
        """Start watching for file changes."""
        if self._watching:
            logger.warning("Watcher already started")
            return

        self._watching = True

        # Initial scan
        await self._scan_directories()

        # Start watch loop
        self._watch_task = asyncio.create_task(self._watch_loop())

        logger.info(
            "Plugin watcher started",
            directories=[str(d) for d in self.watch_directories],
            poll_interval=self.poll_interval,
        )

    async def stop(self) -> None:
        """Stop watching for file changes."""
        self._watching = False

        if self._watch_task:
            self._watch_task.cancel()
            try:
                await self._watch_task
            except asyncio.CancelledError:
                pass

        logger.info("Plugin watcher stopped")

    async def _watch_loop(self) -> None:
        """Main watch loop."""
        while self._watching:
            try:
                await self._scan_directories()
                await asyncio.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"Error in watch loop: {e}", exc_info=True)
                await asyncio.sleep(self.poll_interval)

    async def _scan_directories(self) -> None:
        """Scan watched directories for changes."""
        current_files = set()

        for directory in self.watch_directories:
            if not directory.exists():
                logger.warning(f"Watch directory does not exist: {directory}")
                continue

            # Find all matching files
            for pattern in self.patterns:
                for file_path in directory.rglob(pattern):
                    if self._should_ignore(file_path):
                        continue

                    current_files.add(file_path)
                    await self._check_file(file_path)

        # Check for deleted files
        deleted_files = set(self._file_metadata.keys()) - current_files
        for file_path in deleted_files:
            await self._handle_deleted(file_path)

    def _should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored.

        Args:
        ----
            path: Path to check

        Returns:
        -------
            True if path should be ignored

        """
        path_str = str(path)

        for pattern in self.ignore_patterns:
            if pattern in path_str:
                return True

        return False

    async def _check_file(self, path: Path) -> None:
        """Check file for changes.

        Args:
        ----
            path: File path to check

        """
        try:
            stat = path.stat()
            size = stat.st_size
            mtime = stat.st_mtime

            # Calculate file hash
            file_hash = await self._calculate_file_hash(path)

            # Check if file is new
            if path not in self._file_metadata:
                await self._handle_created(path, size, mtime, file_hash)
            else:
                # Check if file is modified
                metadata = self._file_metadata[path]
                if (
                    metadata.size != size
                    or metadata.mtime != mtime
                    or metadata.hash != file_hash
                ):
                    await self._handle_modified(path, size, mtime, file_hash)

        except FileNotFoundError:
            # File was deleted between scan and check
            if path in self._file_metadata:
                await self._handle_deleted(path)
        except Exception as e:
            logger.error(f"Error checking file {path}: {e}")

    async def _calculate_file_hash(self, path: Path) -> str:
        """Calculate file hash.

        Args:
        ----
            path: File path

        Returns:
        -------
            File hash as hex string

        """
        hasher = hashlib.sha256()

        try:
            with open(path, "rb") as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
        except Exception as e:
            logger.error(f"Error hashing file {path}: {e}")
            return ""

        return hasher.hexdigest()

    async def _handle_created(
        self,
        path: Path,
        size: int,
        mtime: float,
        file_hash: str,
    ) -> None:
        """Handle file creation.

        Args:
        ----
            path: Created file path
            size: File size
            mtime: Modification time
            file_hash: File hash

        """
        self._file_metadata[path] = FileMetadata(
            path=path,
            size=size,
            mtime=mtime,
            hash=file_hash,
        )

        event = WatchEvent(
            event_type=WatchEventType.CREATED,
            path=path,
        )

        await self._dispatch_event(event)

    async def _handle_modified(
        self,
        path: Path,
        size: int,
        mtime: float,
        file_hash: str,
    ) -> None:
        """Handle file modification.

        Args:
        ----
            path: Modified file path
            size: New file size
            mtime: New modification time
            file_hash: New file hash

        """
        self._file_metadata[path] = FileMetadata(
            path=path,
            size=size,
            mtime=mtime,
            hash=file_hash,
        )

        event = WatchEvent(
            event_type=WatchEventType.MODIFIED,
            path=path,
        )

        await self._dispatch_event(event)

    async def _handle_deleted(self, path: Path) -> None:
        """Handle file deletion.

        Args:
        ----
            path: Deleted file path

        """
        if path in self._file_metadata:
            del self._file_metadata[path]

        event = WatchEvent(
            event_type=WatchEventType.DELETED,
            path=path,
        )

        await self._dispatch_event(event)

    async def _dispatch_event(self, event: WatchEvent) -> None:
        """Dispatch event to handlers.

        Args:
        ----
            event: Watch event to dispatch

        """
        logger.debug(f"Dispatching {event.event_type.value} event for {event.path}")

        # Run handlers concurrently
        if self._event_handlers:
            tasks = [
                asyncio.create_task(handler(event)) for handler in self._event_handlers
            ]

            # Wait for all handlers to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Log any errors
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(
                        f"Error in event handler {i}: {result}",
                        exc_info=result,
                    )

    def get_watched_files(self) -> List[Path]:
        """Get list of currently watched files.

        Returns
        -------
            List of watched file paths

        """
        return list(self._file_metadata.keys())

    def get_file_metadata(self, path: Path) -> Optional[FileMetadata]:
        """Get metadata for a specific file.

        Args:
        ----
            path: File path

        Returns:
        -------
            File metadata or None if not tracked

        """
        return self._file_metadata.get(path)
