"""Utility functions for flx-ldap.

This module provides shared utility functions.
"""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path


def run_command(
    cmd: list[str],
    input_data: str | None = None,
    *,
    capture_output: bool = True,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Run a command with proper error handling.

    Args:
        cmd: Command and arguments
        input_data: Input data for stdin
        capture_output: Whether to capture output
        check: Whether to check return code

    Returns:
        CompletedProcess instance

    Raises:
        subprocess.CalledProcessError: If command fails and check=True

    """
    return subprocess.run(
        cmd,
        input=input_data,
        capture_output=capture_output,
        text=True,
        check=check,
    )


def load_catalog(catalog_path: Path) -> dict[str, Any]:
    """Load Singer catalog from file.

    Args:
        catalog_path: Path to catalog file

    Returns:
        Catalog dictionary

    Raises:
        FileNotFoundError: If catalog not found
        json.JSONDecodeError: If invalid JSON

    """
    with catalog_path.open(encoding="utf-8") as f:
        return json.load(f)  # type: ignore[no-any-return]


def save_catalog(catalog: dict[str, Any], catalog_path: Path) -> None:
    """Save Singer catalog to file.

    Args:
        catalog: Catalog dictionary
        catalog_path: Path to save catalog

    """
    catalog_path.parent.mkdir(parents=True, exist_ok=True)

    with catalog_path.open("w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2)


def load_state(state_path: Path) -> dict[str, Any]:
    """Load Singer state from file.

    Args:
        state_path: Path to state file

    Returns:
        State dictionary

    Raises:
        FileNotFoundError: If state not found
        json.JSONDecodeError: If invalid JSON

    """
    with state_path.open(encoding="utf-8") as f:
        return json.load(f)  # type: ignore[no-any-return]


def save_state(state: dict[str, Any], state_path: Path) -> None:
    """Save Singer state to file.

    Args:
        state: State dictionary
        state_path: Path to save state

    """
    state_path.parent.mkdir(parents=True, exist_ok=True)

    with state_path.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def merge_configs(*configs: dict[str, Any]) -> dict[str, Any]:
    """Merge multiple configuration dictionaries.

    Later configs override earlier ones.

    Args:
        *configs: Configuration dictionaries

    Returns:
        Merged configuration

    """
    result: dict[str, Any] = {}

    for config in configs:
        result.update(config)

    return result


def validate_ldap_dn(dn: str) -> bool:
    """Validate LDAP DN format.

    Args:
        dn: Distinguished name to validate

    Returns:
        True if valid DN format

    """
    if not dn:
        return False

    try:
        # Basic validation - check for key=value pairs
        parts = dn.split(",")
        for part in parts:
            part = part.strip()
            if "=" not in part:
                return False
            key, value = part.split("=", 1)
            if not key or not value:
                return False
        return True
    except Exception:
        return False


def parse_ldap_dn(dn: str) -> dict[str, str]:
    """Parse LDAP DN into components.

    Args:
        dn: Distinguished name to parse

    Returns:
        Dictionary of DN components

    Raises:
        ValueError: If invalid DN format

    """
    if not validate_ldap_dn(dn):
        msg = f"Invalid DN format: {dn}"
        raise ValueError(msg)

    components = {}
    parts = dn.split(",")

    for part in parts:
        part = part.strip()
        key, value = part.split("=", 1)
        components[key.lower()] = value

    return components


def count_records_in_jsonl(file_path: Path, stream_name: str | None = None) -> int:
    """Count records in a JSONL file.

    Args:
        file_path: Path to JSONL file
        stream_name: Optional stream name to filter

    Returns:
        Number of records

    """
    count = 0

    with file_path.open(encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line)
                if record.get("type") == "RECORD" and (
                    stream_name is None or record.get("stream") == stream_name
                ):
                    count += 1
            except json.JSONDecodeError:
                continue

    return count


def extract_streams_from_jsonl(file_path: Path) -> set[str]:
    """Extract unique stream names from JSONL file.

    Args:
        file_path: Path to JSONL file

    Returns:
        Set of stream names

    """
    streams = set()

    with file_path.open(encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line)
                if record.get("type") == "RECORD" and "stream" in record:
                    streams.add(record["stream"])
            except json.JSONDecodeError:
                continue

    return streams


def format_bytes(num_bytes: int | float) -> str:
    """Format bytes in human-readable format.

    Args:
        num_bytes: Number of bytes

    Returns:
        Formatted string (e.g., "1.5 MB")

    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"
