"""Progress tracking for Oracle OIC operations."""

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class ProgressStatus(Enum):
    """Progress status enumeration."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ProgressCallback(ABC):
    """Abstract base class for progress callbacks."""

    @abstractmethod
    async def on_category_start(self, category: str, total_expected: int = 0) -> None:
        """Called when a category dump starts."""

    @abstractmethod
    async def on_entity_start(
        self, category: str, entity_id: str, entity_name: str
    ) -> None:
        """Called when an entity processing starts."""

    @abstractmethod
    async def on_entity_complete(
        self,
        category: str,
        entity_id: str,
        *,
        success: bool,
        artifact_downloaded: bool = False,
        error: str | None = None,
    ) -> None:
        """Called when an entity processing completes."""

    @abstractmethod
    async def on_category_complete(
        self,
        category: str,
        total_processed: int,
        total_succeeded: int,
        total_failed: int,
    ) -> None:
        """Called when a category dump completes."""

    @abstractmethod
    async def on_artifact_download_start(
        self, entity_type: str, entity_id: str
    ) -> None:
        """Called when artifact download starts."""

    @abstractmethod
    async def on_artifact_download_complete(
        self, entity_type: str, entity_id: str, *, success: bool, size_bytes: int = 0
    ) -> None:
        """Called when artifact download completes."""


class ConsoleProgressCallback(ProgressCallback):
    """Console progress callback implementation using FLX output."""

    def __init__(self, output_port: Any) -> None:
        """Initialize with FLX output port."""
        self.output = output_port
        self.start_times: dict[str, datetime] = {}
        self.category_progress: dict[str, dict[str, int]] = {}

    async def on_category_start(self, category: str, total_expected: int = 0) -> None:
        """Called when a category dump starts."""
        self.start_times[category] = datetime.now(UTC)
        self.category_progress[category] = {
            "total": total_expected,
            "processed": 0,
            "succeeded": 0,
            "failed": 0,
        }
        self.output.info(f"\n📂 Starting dump for {category.upper()}")
        if total_expected > 0:
            self.output.info(f"   Total entities to process: {total_expected}")

    async def on_entity_start(
        self, category: str, entity_id: str, entity_name: str
    ) -> None:
        """Called when an entity processing starts."""
        self.output.info(f"   ⏳ Processing: {entity_name} ({entity_id})")

    async def on_entity_complete(
        self,
        category: str,
        entity_id: str,
        *,
        success: bool,
        artifact_downloaded: bool = False,
        error: str | None = None,
    ) -> None:
        """Called when an entity processing completes."""
        if category in self.category_progress:
            self.category_progress[category]["processed"] += 1
            if success:
                self.category_progress[category]["succeeded"] += 1
                icon = "✅"
                artifact_info = " [+artifact]" if artifact_downloaded else ""
                self.output.success(f"   {icon} Completed: {entity_id}{artifact_info}")
            else:
                self.category_progress[category]["failed"] += 1
                self.output.error(
                    f"   ❌ Failed: {entity_id} - {error or 'Unknown error'}"
                )

            # Show progress
            progress = self.category_progress[category]
            if progress["total"] > 0:
                percentage = (progress["processed"] / progress["total"]) * 100
                self.output.info(
                    f"   Progress: {progress['processed']}/{progress['total']} "
                    f"({percentage:.1f}%) - "
                    f"✅ {progress['succeeded']} | ❌ {progress['failed']}"
                )

    async def on_category_complete(
        self,
        category: str,
        total_processed: int,
        total_succeeded: int,
        total_failed: int,
    ) -> None:
        """Called when a category dump completes."""
        elapsed = datetime.now(UTC) - self.start_times.get(category, datetime.now(UTC))
        elapsed_str = str(elapsed).split(".")[0]  # Remove microseconds

        self.output.info(f"\n📊 Completed {category.upper()} dump:")
        self.output.info(f"   Total processed: {total_processed}")
        self.output.info(f"   Succeeded: {total_succeeded} ✅")
        if total_failed > 0:
            self.output.warning(f"   Failed: {total_failed} ❌")
        self.output.info(f"   Time elapsed: {elapsed_str}")

    async def on_artifact_download_start(
        self, entity_type: str, entity_id: str
    ) -> None:
        """Called when artifact download starts."""
        self.output.info(f"      📥 Downloading artifact for {entity_id}...")

    async def on_artifact_download_complete(
        self, entity_type: str, entity_id: str, *, success: bool, size_bytes: int = 0
    ) -> None:
        """Called when artifact download completes."""
        if success:
            size_mb = size_bytes / (1024 * 1024)
            self.output.success(f"      ✅ Downloaded: {size_mb:.2f} MB")
        else:
            self.output.warning("      ⚠️  Artifact download failed")


class SilentProgressCallback(ProgressCallback):
    """Silent progress callback that does nothing."""

    async def on_category_start(self, category: str, total_expected: int = 0) -> None:
        pass

    async def on_entity_start(
        self, category: str, entity_id: str, entity_name: str
    ) -> None:
        pass

    async def on_entity_complete(
        self,
        category: str,
        entity_id: str,
        *,
        success: bool,
        artifact_downloaded: bool = False,
        error: str | None = None,
    ) -> None:
        pass

    async def on_category_complete(
        self,
        category: str,
        total_processed: int,
        total_succeeded: int,
        total_failed: int,
    ) -> None:
        pass

    async def on_artifact_download_start(
        self, entity_type: str, entity_id: str
    ) -> None:
        pass

    async def on_artifact_download_complete(
        self, entity_type: str, entity_id: str, *, success: bool, size_bytes: int = 0
    ) -> None:
        pass
