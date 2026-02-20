from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from typing import Any


def _load_module(module_name: str, relative_path: str) -> Any:
    module_path = Path(__file__).resolve().parents[3] / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_parse_and_bump_semver() -> None:
    mod = _load_module("libs_versioning_semver", "libs/versioning.py")
    assert mod.parse_semver("1.2.3") == (1, 2, 3)
    assert mod.bump_version("1.2.3", "patch") == "1.2.4"
    assert mod.bump_version("1.2.3", "minor") == "1.3.0"
    assert mod.bump_version("1.2.3", "major") == "2.0.0"


def test_release_tag_from_branch_patterns() -> None:
    mod = _load_module("libs_versioning_release", "libs/versioning.py")
    assert mod.release_tag_from_branch("0.11.0-dev") == "v0.11.0"
    assert mod.release_tag_from_branch("release/0.12.3") == "v0.12.3"
    assert mod.release_tag_from_branch("feature/abc") is None


def test_replace_project_version_updates_only_project_table() -> None:
    mod = _load_module("libs_versioning_replace", "libs/versioning.py")
    content = """
[project]
name = "demo"
version = "0.11.0-dev"

[tool.poetry.dependencies]
python = ">=3.13,<4.0"
flext-core = "0.11.0-dev"
""".strip()
    updated, did_change = mod.replace_project_version(content, "0.11.0")
    assert did_change is True
    assert 'version = "0.11.0"' in updated
    assert 'flext-core = "0.11.0-dev"' in updated


def test_current_workspace_version_reads_project_version(tmp_path: Path) -> None:
    mod = _load_module("libs_versioning_current", "libs/versioning.py")
    pyproject = tmp_path / "pyproject.toml"
    _ = pyproject.write_text(
        """
[project]
name = "demo"
version = "0.10.0-dev"
""".strip(),
        encoding="utf-8",
    )
    assert mod.current_workspace_version(tmp_path) == "0.10.0"
