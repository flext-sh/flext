"""Standard LDIF processor implementing essential interfaces."""

import re
from pathlib import Path
from typing import Any

from .base import BaseProcessor
from .ldif_interface import ILdifProcessor


class StandardLdifProcessor(BaseProcessor, ILdifProcessor):
    """Standard LDIF processor with essential functionality."""

    def __init__(self) -> None:
        super().__init__("StandardLdifProcessor")

    def parse_file(self, filepath: Path) -> list[dict[str, Any]]:
        """Parse LDIF file and return entries."""
        entries: list = []

        if not filepath.exists():
            self.log_error("File parsing", f"File not found: {filepath}")
            return entries

        try:
            with open(filepath, encoding="utf-8") as file:
                content = file.read()

            # Split by empty lines to get individual entries
            raw_entries = re.split(r"\n\s*\n", content.strip())

            for raw_entry in raw_entries:
                if not raw_entry.strip() or raw_entry.startswith("#"):
                    continue

                entry = self._parse_entry(raw_entry)
                if entry:
                    entries.append(entry)

            self.log_success("File parsing", len(entries))

        except Exception as e:
            self.log_error("File parsing", str(e))
            raise

        return entries

    def _parse_entry(self, raw_entry: str) -> dict[str, Any] | None:
        """Parse individual LDIF entry."""
        lines = [line.strip() for line in raw_entry.strip().split("\n") if line.strip()]

        if not lines:
            return None

        entry = {"dn": "", "attributes": {}}

        for line in lines:
            if line.startswith("dn:"):
                entry["dn"] = line[3:].strip()
            elif ":" in line:
                attr_name, attr_value = line.split(":", 1)
                attr_name = attr_name.strip().lower()
                attr_value = attr_value.strip()

                if attr_name not in entry["attributes"]:
                    entry["attributes"][attr_name] = []

                entry["attributes"][attr_name].append(attr_value)

        return entry if entry["dn"] else None

    def write_entries_to_file(
        self,
        entries: list[dict[str, Any]],
        output_file: Path,
        title: str,
        source: str | None = None,
    ) -> int:
        """Write entries to LDIF file."""
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as file:
                # Write header
                file.write(f"# {title}\n")
                if source:
                    file.write(f"# Source: {source}\n")
                file.write(f"# Generated entries: {len(entries)}\n\n")

                # Write entries
                for i, entry in enumerate(entries):
                    if i > 0:
                        file.write("\n")

                    file.write(f"dn: {entry['dn']}\n")

                    for attr_name, attr_values in entry["attributes"].items():
                        for attr_value in attr_values:
                            file.write(f"{attr_name}: {attr_value}\n")

            self.log_success("File writing", f"{len(entries)} entries to {output_file}")
            return len(entries)

        except Exception as e:
            self.log_error("File writing", str(e))
            raise

    def validate_ldif(self, filepath: Path) -> bool:
        """Validate LDIF file format."""
        try:
            entries = self.parse_file(filepath)

            # Basic validation: all entries must have DN
            valid = all(entry.get("dn") for entry in entries)

            if valid:
                self.log_success("LDIF validation", f"{len(entries)} entries validated")
                self.log_error("LDIF validation", "Some entries missing DN")

            return valid

        except Exception as e:
            self.log_error("LDIF validation", str(e))
            return False

    def filter_entries_by_type(
        self,
        entries: list[dict],
        entry_type: str,
    ) -> list[dict]:
        """Filter entries by type (user, group, etc)."""
        filtered: list = []

        for entry in entries:
            dn = entry.get("dn", "").lower()
            attributes = entry.get("attributes", {})
            object_classes = [oc.lower() for oc in attributes.get("objectclass", [])]

            # Determine entry type based on DN and objectClass
            if entry_type == "user":
                if any(
                    oc in {"person", "inetorgperson", "user"} for oc in object_classes
                ):
                    filtered.append(entry)
            elif entry_type == "group":
                if any(
                    oc in {"group", "groupofnames", "groupofuniquenames"}
                    for oc in object_classes
                ):
                    filtered.append(entry)
            elif entry_type == "schema":
                if "cn=schema" in dn or any(
                    oc in {"subschema"} for oc in object_classes
                ):
                    filtered.append(entry)

        self.log_success(f"Entry filtering ({entry_type})", len(filtered))
        return filtered

    def process(self, operation: str, **kwargs) -> Any:
        """Process LDIF operations."""
        operations = {
            "parse": lambda: self.parse_file(kwargs.get("filepath")),
            "write": lambda: self.write_entries_to_file(
                kwargs.get("entries", []),
                kwargs.get("output_file"),
                kwargs.get("title", "LDIF Export"),
                kwargs.get("source"),
            ),
            "validate": lambda: self.validate_ldif(kwargs.get("filepath")),
            "filter": lambda: self.filter_entries_by_type(
                kwargs.get("entries", []),
                kwargs.get("entry_type", "user"),
            ),
        }

        if operation not in operations:
            raise ValueError(f"Unknown LDIF operation: {operation}")

        return operations[operation]()
