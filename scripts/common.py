#!/usr/bin/env python3
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
"""Common utilities for FLEXT scripts - Facade for flext-core patterns.

ANTI-DUPLICATION ENFORCEMENT: Uses flext-core exclusively, NO local implementations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from flext_core import FlextLogger as logger_core

logger = logger_core(__name__)


def discover_projects(
    workspace_root: Path,
    projects_filter: Sequence[str] | None = None,
) -> list[Path]:
    """Discover FLEXT projects using filesystem enumeration.

    Uses direct filesystem discovery to find flext-* projects with pyproject.toml.
    """
    try:
        project_paths: list[Path] = [
            item
            for item in workspace_root.iterdir()
            if item.is_dir()
            and item.name.startswith("flext-")
            and (item / "pyproject.toml").exists()
            and (projects_filter is None or item.name in projects_filter)
        ]

        return project_paths

    except Exception:
        logger.exception("Failed to discover projects")
        return []


def get_workspace_root() -> Path:
    """Get workspace root using flext-core discovery."""
    try:
        # Use current working directory as workspace root
        return Path.cwd()
    except Exception:
        logger.exception("Failed to discover workspace root")
        return Path.cwd()
