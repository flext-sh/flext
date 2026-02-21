from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch


def load_module() -> types.ModuleType:
    module_path = (
        Path(__file__).resolve().parents[4]
        / "scripts"
        / "dependencies"
        / "modernize_pyproject.py"
    )
    spec = importlib.util.spec_from_file_location("modernize_pyproject", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_pyproject(project_dir: Path, content: str) -> Path:
    pyproject = project_dir / "pyproject.toml"
    _ = pyproject.write_text(content, encoding="utf-8")
    return pyproject


def test_process_file_is_idempotent_with_array_of_tables(tmp_path: Path) -> None:
    mod = load_module()
    project_dir = tmp_path / "demo"
    project_dir.mkdir()

    pyproject = write_pyproject(
        project_dir,
        """
[build-system]
requires = ["poetry-core>=2"]

[project]
name = "demo"
version = "0.1.0"
license = "MIT"

[tool.pyrefly]
search-path = ["src"]

[tool.pytest.ini_options]
addopts = ["-q"]
""".strip()
        + "\n",
    )

    spec = mod.ProjectSpec(project_dir=project_dir)
    first_fixes = mod.process_file(pyproject, spec, dry_run=False)
    first_text = pyproject.read_text(encoding="utf-8")
    second_fixes = mod.process_file(pyproject, spec, dry_run=False)
    second_text = pyproject.read_text(encoding="utf-8")

    assert first_fixes
    assert second_fixes == []
    assert first_text == second_text


def test_audit_exit_codes_reflect_violations(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    mod = load_module()
    project_dir = tmp_path / "pkg"
    project_dir.mkdir()

    _ = write_pyproject(
        project_dir,
        """
[build-system]
requires = ["poetry-core>=1.9.0"]

[project]
name = "pkg"
version = "0.1.0"
license = { text = "MIT" }
""".strip()
        + "\n",
    )

    _ = write_pyproject(
        tmp_path,
        """
[project]
name = "workspace"
version = "0.1.0"

[tool.pytest.ini_options]
addopts = ["--strict-config", "--strict-markers", "--tb=short", "-p no:sugar", "-q", "-ra"]

[tool.bandit]
skips = ["B404", "B603", "B607", "B105", "B608"]
""".strip()
        + "\n",
    )

    monkeypatch.setattr(mod, "ROOT", tmp_path)
    monkeypatch.setattr(mod, "VENV_BIN", tmp_path / ".venv" / "bin")
    monkeypatch.setattr(
        mod.sys, "argv", ["modernize_pyproject.py", "--audit", "--skip-fmt"]
    )
    assert mod.main() == 1

    _ = write_pyproject(
        project_dir,
        """
[build-system]
requires = ["poetry-core>=2"]

[project]
name = "pkg"
version = "0.1.0"
license = "MIT"

[tool.coverage.run]
source = ["src/pkg"]

[tool.coverage.report]
fail_under = 100
precision = 2

[tool.pytest.ini_options]
addopts = ["--strict-config", "--strict-markers", "--tb=short", "-p no:sugar", "-q", "-ra"]

[tool.bandit]
skips = ["B404", "B603", "B607", "B105", "B608"]
""".strip()
        + "\n",
    )
    (project_dir / "src" / "pkg").mkdir(parents=True)

    _ = write_pyproject(
        tmp_path,
        """
[project]
name = "workspace"
version = "0.1.0"

[tool.bandit]
skips = ["B404", "B603", "B607", "B105", "B608"]

[tool.pytest.ini_options]
addopts = ["--strict-config", "--strict-markers", "--tb=short", "-p no:sugar", "-q", "-ra"]
""".strip()
        + "\n",
    )

    monkeypatch.setattr(
        mod.sys, "argv", ["modernize_pyproject.py", "--audit", "--skip-fmt"]
    )
    assert mod.main() == 0


def test_array_of_tables_survives_regex_fallback(tmp_path: Path) -> None:
    mod = load_module()
    project_dir = tmp_path / "safe"
    project_dir.mkdir(parents=True)
    pyproject = write_pyproject(
        project_dir,
        """
[build-system]
requires = ["poetry-core>=1.9.0"]

[project]
name = "safe"
version = "0.1.0"

[tool.pyrefly]
search-path = ["src"]

[[tool.pyrefly.sub-config]]
root = "src"

[[tool.pyrefly.sub-config]]
root = "tests"

[tool.coverage.report]
fail_under = 100
""".strip()
        + "\n",
    )
    spec = mod.ProjectSpec(project_dir=project_dir)
    mod.process_file(pyproject, spec, dry_run=False)
    text = pyproject.read_text(encoding="utf-8")

    assert text.count("[[tool.pyrefly.sub-config]]") == 2
    assert 'root = "src"' in text
    assert 'root = "tests"' in text


def test_bandit_skips_are_loaded_from_root_ssot(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    mod = load_module()
    root_dir = tmp_path / "workspace"
    project_dir = root_dir / "pkg"
    project_dir.mkdir(parents=True)

    _ = write_pyproject(
        root_dir,
        """
[project]
name = "workspace"
version = "0.1.0"

[tool.pytest.ini_options]
addopts = ["--strict-config", "--strict-markers", "--tb=short", "-p no:sugar", "-q", "-ra"]

[tool.bandit]
skips = ["B105", "B999"]
""".strip()
        + "\n",
    )

    pyproject = write_pyproject(
        project_dir,
        """
[build-system]
requires = ["poetry-core>=2"]

[project]
name = "pkg"
version = "0.1.0"

[tool.pyrefly]
search-path = ["src"]

[[tool.pyrefly.sub-config]]
root = "src"
""".strip()
        + "\n",
    )

    monkeypatch.setattr(mod, "ROOT", root_dir)
    spec = mod.ProjectSpec(project_dir=project_dir)
    mod.process_file(pyproject, spec, dry_run=False)
    text = pyproject.read_text(encoding="utf-8")

    assert "[tool.bandit]" in text
    assert '"B105"' in text
    assert '"B999"' in text
    assert '"B404"' not in text
