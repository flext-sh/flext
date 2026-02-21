from __future__ import annotations

import importlib.util
import re
import sys
import types
from pathlib import Path


def _load_module(relative_path: str, module_name: str) -> types.ModuleType:
    module_path = Path(__file__).resolve().parents[4] / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_replace_version_updates_only_project_version() -> None:
    mod = _load_module("scripts/release/version.py", "release_version")
    content = """
[project]
name = "demo"
version = "0.11.0-dev"

[tool.poetry.dependencies]
python = ">=3.13,<4.0"
flext-core = "0.11.0-dev"
""".strip()

    updated, did_change = mod._replace_version(content, "0.11.0")

    assert did_change is True
    assert 'version = "0.11.0"' in updated
    assert 'flext-core = "0.11.0-dev"' in updated


def test_update_changelog_is_idempotent_by_version_heading() -> None:
    mod = _load_module("scripts/release/changelog.py", "release_changelog")
    first = mod._update_changelog("# Changelog\n\n", "0.11.0", "v0.11.0")
    second = mod._update_changelog(first, "0.11.0", "v0.11.0")

    assert first == second
    assert len(re.findall(r"^## 0\.11\.0 - ", second, flags=re.MULTILINE)) == 1
