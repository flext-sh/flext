"""Essential LDIF interfaces."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class ILdifProcessor(ABC):
    """Essential LDIF processor interface."""

    @abstractmethod
    def parse_file(self, filepath: Path) -> list[dict[str, Any]]:
        """Parse LDIF file and return entries."""

    @abstractmethod
    def write_entries_to_file(
        self,
        entries: list[dict[str, Any]],
        output_file: Path,
        title: str,
        source: str | None = None,
    ) -> int:
        """Write entries to LDIF file."""

    @abstractmethod
    def validate_ldif(self, filepath: Path) -> bool:
        """Validate LDIF file format."""
