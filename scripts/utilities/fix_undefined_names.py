#!/usr/bin/env python3
"""Fix F821 undefined name errors systematically - TASK: FLX-UNDEFINED-004."""

import re
import subprocess
from pathlib import Path


def analyze_undefined_names() -> dict[str, list[str]]:
    """Analyze F821 errors to understand undefined names."""
    result = subprocess.run(
        ["ruff", "check", "/home/marlonsc/pyauto/flx/src/flx/", "--select=F821"],
        capture_output=True,
        text=True,
        cwd="/home/marlonsc/pyauto/flx",
        check=False,
    )

    undefined_names: dict[str, list[str]] = {}
    if result.stdout:
        for line in result.stdout.splitlines():
            if "F821" in line and "Undefined name" in line:
                # Extract file path and undefined name
                parts = line.split(":")
                if len(parts) >= 4:
                    file_path = parts[0]
                    # Extract undefined name from message
                    match = re.search(r"Undefined name `([^`]+)`", line)
                    if match:
                        name = match.group(1)
                        if file_path not in undefined_names:
                            undefined_names[file_path] = []
                        undefined_names[file_path].append(name)

    return undefined_names


def fix_common_imports(file_path: Path, undefined_names: list[str]) -> bool:
    """Fix common import issues for undefined names."""
    content = file_path.read_text()
    modified = False

    # Common import fixes
    import_fixes = {
        "Enum": "from enum import Enum",
        "BaseModel": "from pydantic import BaseModel",
        "Field": "from pydantic import Field",
        "ConfigDict": "from pydantic import ConfigDict",
        "field_validator": "from pydantic import field_validator",
        "computed_field": "from pydantic import computed_field",
        "Dict": "from typing import Dict",
        "List": "from typing import List",
        "Optional": "from typing import Optional",
        "Union": "from typing import Union",
        "Any": "from typing import Any",
        "ClassVar": "from typing import ClassVar",
        "Protocol": "from typing import Protocol",
        "TypeVar": "from typing import TypeVar",
        "Generic": "from typing import Generic",
        "Callable": "from typing import Callable",
        "Iterable": "from typing import Iterable",
        "Iterator": "from typing import Iterator",
        "Mapping": "from typing import Mapping",
        "Sequence": "from typing import Sequence",
        "Type": "from typing import Type",
        "dataclass": "from dataclasses import dataclass",
        "field": "from dataclasses import field",
        "datetime": "from datetime import datetime",
        "date": "from datetime import date",
        "timedelta": "from datetime import timedelta",
        "UTC": "from datetime import UTC",
        "UUID": "from uuid import UUID",
        "uuid4": "from uuid import uuid4",
        "Path": "from pathlib import Path",
        "Decimal": "from decimal import Decimal",
        "abstractmethod": "from abc import abstractmethod",
        "ABC": "from abc import ABC",
        "asyncio": "import asyncio",
        "json": "import json",
        "os": "import os",
        "sys": "import sys",
        "re": "import re",
        "time": "import time",
        "logging": "import logging",
        "warnings": "import warnings",
        "inspect": "import inspect",
        "functools": "import functools",
        "partial": "from functools import partial",
        "wraps": "from functools import wraps",
        "contextmanager": "from contextlib import contextmanager",
        "asynccontextmanager": "from contextlib import asynccontextmanager",
        "DaemonConfig": "from flx.infra.daemon.config import DaemonConfig",
        "FlxDaemon": "from flx.infra.daemon.service import FlxDaemon",
        "FlxDaemonService": "from flx.infra.daemon.service import FlxDaemonService",
        "create_app_command_bus": "from flx.application.command_bus import create_app_command_bus",
    }

    # Check which imports we need
    needed_imports = []
    for name in undefined_names:
        if name in import_fixes:
            import_statement = import_fixes[name]
            if import_statement not in content:
                needed_imports.append(import_statement)

    # Add missing imports after existing imports or at top
    if needed_imports:
        lines = content.splitlines()

        # Find insertion point (after last import or at beginning)
        insert_index = 0
        for i, line in enumerate(lines):
            if line.startswith(("import ", "from ", "#")):
                insert_index = i + 1
            elif line.strip() and not line.startswith(('"""', "'''")):
                break

        # Insert needed imports
        for import_stmt in sorted(set(needed_imports)):
            lines.insert(insert_index, import_stmt)
            insert_index += 1

        file_path.write_text("\n".join(lines))
        modified = True

    return modified


def fix_flx_module_imports(file_path: Path, undefined_names: list[str]) -> bool:
    """Fix imports for FLX framework modules."""
    content = file_path.read_text()
    modified = False

    # FLX framework imports
    flx_imports = {
        "Entity": "from flx.core.base import Entity",
        "DomainObject": "from flx.core.base import DomainObject",
        "AggregateRoot": "from flx.core.base import AggregateRoot",
        "Identifiable": "from flx.core.base import Identifiable",
        "Timestamped": "from flx.core.base import Timestamped",
        "Versionable": "from flx.core.base import Versionable",
        "DomainEvent": "from flx.core.domain.events import DomainEvent",
        "FlxDomainEvent": "from flx.core.domain.events import FlxDomainEvent",
        "BaseAdapter": "from flx.adapters.base import BaseAdapter",
        "DatabasePort": "from flx.ports.outbound.database import DatabasePort",
        "AnalyticsPort": "from flx.ports.outbound.analytics import AnalyticsPort",
        "FlxConnectionError": "from flx.core.domain.exceptions import FlxConnectionError",
        "DatabaseError": "from flx.core.domain.exceptions import DatabaseError",
        "Id": "from flx.core.types import Id",
        "PagedResult": "from flx.core.types import PagedResult",
        "TransactionHandle": "from flx.core.types import TransactionHandle",
        "DatabaseEngine": "from flx.infra.database.engine import DatabaseEngine",
        "AnalyticsService": "from flx.infra.observability.analytics_service import AnalyticsService",
        "TestEngine": "from flx.testing.engines.base import TestEngine",
        "CacheEngine": "from flx.testing.engines.cache_engine import CacheEngine",
        "DatabaseTestEngine": "from flx.testing.engines.database_engine import DatabaseTestEngine",
        "HttpTestEngine": "from flx.testing.engines.http_engine import HttpTestEngine",
        "TestOrchestrator": "from flx.testing.engines.test_orchestrator import TestOrchestrator",
    }

    # Check which FLX imports we need
    needed_imports = []
    for name in undefined_names:
        if name in flx_imports:
            import_statement = flx_imports[name]
            if import_statement not in content:
                needed_imports.append(import_statement)

    # Add missing FLX imports
    if needed_imports:
        lines = content.splitlines()

        # Find insertion point after standard/third-party imports
        insert_index = 0
        in_imports = False
        for i, line in enumerate(lines):
            if line.startswith(("import ", "from ")):
                in_imports = True
                insert_index = i + 1
            elif in_imports and line.strip() == "":
                # Empty line after imports - good place to add FLX imports
                insert_index = i
                break
            elif in_imports and not line.startswith(("import ", "from ", " ", "#")):
                # End of import block
                insert_index = i
                break

        # Insert needed FLX imports
        for import_stmt in sorted(set(needed_imports)):
            lines.insert(insert_index, import_stmt)
            insert_index += 1

        file_path.write_text("\n".join(lines))
        modified = True

    return modified


def fix_forward_references(file_path: Path, undefined_names: list[str]) -> bool:
    """Fix forward reference issues in type annotations."""
    content = file_path.read_text()
    modified = False

    # Add __future__ import for forward references if needed
    if not content.startswith("from __future__ import annotations"):
        lines = content.splitlines()
        lines.insert(0, "from __future__ import annotations")
        lines.insert(1, "")
        content = "\n".join(lines)
        modified = True

    # Fix forward references by quoting them
    for name in undefined_names:
        # Look for type annotations using undefined names
        patterns = [
            f"-> {name}",
            f": {name}",
            f"list\\[{name}\\]",
            f"dict\\[.*{name}.*\\]",
            f"Optional\\[{name}\\]",
            f"Union\\[.*{name}.*\\]",
        ]

        for pattern in patterns:
            if re.search(pattern, content):
                # Quote the type name
                content = re.sub(f"\\b{name}\\b", f'"{name}"', content)
                modified = True

    if modified:
        file_path.write_text(content)

    return modified


def fix_variable_definitions(file_path: Path, undefined_names: list[str]) -> bool:
    """Fix undefined variables by adding proper definitions."""
    content = file_path.read_text()
    modified = False

    # Common variable definitions
    variable_fixes = {
        "_logger": "from flx.core.logging import get_logger\n        self._logger = get_logger(self.__class__.__name__)",
        "_connection": "self._connection: Any = None",
        "_client": "self._client: Any = None",
        "_analytics_client": "self._analytics_client: Any = None",
        "_event_bus": "self._event_bus: Any = None",
        "_repository": "self._repository: Any = None",
    }

    for name in undefined_names:
        if name in variable_fixes:
            fix = variable_fixes[name]
            if fix not in content:
                # Add the fix in __init__ method if it exists
                if "def __init__(" in content:
                    content = content.replace(
                        "def __init__(", f"{fix}\n        def __init__("
                    )
                    modified = True

    if modified:
        file_path.write_text(content)

    return modified


def main() -> None:
    """Fix F821 undefined name errors systematically."""

    undefined_names_by_file = analyze_undefined_names()

    if not undefined_names_by_file:
        return

    total_fixed = 0

    for file_path_str, names in undefined_names_by_file.items():
        file_path = Path(file_path_str)
        if not file_path.exists():
            continue

        fixed_count = 0

        # Try different fix strategies
        if fix_common_imports(file_path, names):
            fixed_count += 1

        if fix_flx_module_imports(file_path, names):
            fixed_count += 1

        if fix_forward_references(file_path, names):
            fixed_count += 1

        if fix_variable_definitions(file_path, names):
            fixed_count += 1

        if fixed_count > 0:
            total_fixed += fixed_count

    # Check remaining errors
    result = subprocess.run(
        ["ruff", "check", "/home/marlonsc/pyauto/flx/src/flx/", "--select=F821"],
        capture_output=True,
        text=True,
        cwd="/home/marlonsc/pyauto/flx",
        check=False,
    )

    remaining_errors = len(result.stdout.splitlines()) if result.stdout else 0

    # Update todo status
    if remaining_errors < 100:
        pass


if __name__ == "__main__":
    main()
