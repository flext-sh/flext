"""Unit tests for scripts.libs.versioning."""

from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path


def _load_module() -> types.ModuleType:
    repo_root = Path(__file__).resolve().parents[3]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    return importlib.import_module("scripts.libs.versioning")


def test_parse_and_bump_semver() -> None:
    mod = _load_module()
    assert mod.parse_semver("1.2.3") == (1, 2, 3)
    assert mod.bump_version("1.2.3", "patch") == "1.2.4"
    assert mod.bump_version("1.2.3", "minor") == "1.3.0"
    assert mod.bump_version("1.2.3", "major") == "2.0.0"


def test_release_tag_from_branch_patterns() -> None:
    mod = _load_module()
    assert mod.release_tag_from_branch("0.11.0-dev") == "v0.11.0"
    assert mod.release_tag_from_branch("release/0.12.3") == "v0.12.3"
    assert mod.release_tag_from_branch("feature/abc") == ""


def test_replace_project_version_updates_only_project_table(tmp_path: Path) -> None:
    mod = _load_module()
    content = """
[project]
name = "demo"
version = "0.11.0-dev"

[tool.poetry.dependencies]
python = ">=3.13,<4.0"
flext-core = "0.11.0-dev"
""".strip()
    pyproject = tmp_path / "pyproject.toml"
    _ = pyproject.write_text(content, encoding="utf-8")
    mod.replace_project_version(tmp_path, "0.11.0")
    updated = pyproject.read_text(encoding="utf-8")
    assert 'version = "0.11.0"' in updated
    assert 'flext-core = "0.11.0-dev"' in updated


def test_current_workspace_version_reads_project_version(tmp_path: Path) -> None:
    mod = _load_module()
    pyproject = tmp_path / "pyproject.toml"
    _ = pyproject.write_text(
        """
[project]
name = "demo"
version = "0.10.0-dev"
""".strip(),
        encoding="utf-8",
    )
    assert mod.current_workspace_version(tmp_path) == "0.10.0-dev"
