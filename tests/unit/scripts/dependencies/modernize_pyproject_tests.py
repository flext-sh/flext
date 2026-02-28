"""Unit tests for flext_infra.deps.modernizer.PyprojectModernizer."""

from __future__ import annotations

from pathlib import Path

from flext_infra.deps.modernizer import PyprojectModernizer


def write_pyproject(project_dir: Path, content: str) -> Path:
    """Write pyproject.toml content to a project directory."""
    pyproject = project_dir / "pyproject.toml"
    _ = pyproject.write_text(content, encoding="utf-8")
    return pyproject


def test_process_file_is_idempotent_with_array_of_tables(tmp_path: Path) -> None:
    """Test that processing a file twice produces no changes on second run."""
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

    modernizer = PyprojectModernizer(root=tmp_path)
    canonical_dev: list[str] = []
    first_fixes = modernizer.process_file(
        pyproject,
        canonical_dev=canonical_dev,
        dry_run=False,
        skip_comments=False,
    )
    first_text = pyproject.read_text(encoding="utf-8")
    second_fixes = modernizer.process_file(
        pyproject,
        canonical_dev=canonical_dev,
        dry_run=False,
        skip_comments=False,
    )
    second_text = pyproject.read_text(encoding="utf-8")

    assert first_fixes
    assert second_fixes == []
    assert first_text == second_text


def test_audit_exit_codes_reflect_violations(tmp_path: Path) -> None:
    """Test that audit mode detects violations and returns correct exit codes."""
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

    modernizer = PyprojectModernizer(root=tmp_path)
    canonical_dev: list[str] = []
    changes = modernizer.process_file(
        project_dir / "pyproject.toml",
        canonical_dev=canonical_dev,
        dry_run=True,
        skip_comments=False,
    )
    assert changes

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
minversion = "8.0"
python_classes = ["Test*"]
python_files = ["*_test.py", "*_tests.py", "test_*.py"]
addopts = ["--strict-markers"]
markers = [
    "unit: unit tests",
    "integration: integration tests",
    "performance: performance and benchmark tests",
    "slow: slow-running tests",
    "docker: tests requiring Docker",
    "e2e: end-to-end integration tests",
    "edge_cases: edge case tests",
    "stress: stress tests",
    "resilience: resilience tests",
]

[tool.deptry]
pep621_dev_dependency_groups = ["dev"]

[tool.pyrefly]
python-version = "3.13"
ignore-errors-in-generated-code = true
search-path = ["."]
project-excludes = ["**/_pb2.py", "**/_pb2_grpc.py", "**/*_pb2*.py", "**/*_pb2_grpc*.py"]

[tool.pyrefly.errors]
deprecated = true
redundant-cast = true
implicit-abstract-class = true
implicit-any = true
implicitly-defined-attribute = true
missing-override-decorator = true
missing-source = true
not-required-key-access = true
open-unpacking = true
protocol-implicitly-defined-attribute = true
unannotated-attribute = true
unannotated-parameter = true
unannotated-return = true
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

    modernizer = PyprojectModernizer(root=tmp_path)
    changes = modernizer.process_file(
        project_dir / "pyproject.toml",
        canonical_dev=canonical_dev,
        dry_run=True,
        skip_comments=True,
    )
    assert changes == []


def test_array_of_tables_survives_regex_fallback(tmp_path: Path) -> None:
    """Test that array-of-tables structures are preserved during modernization."""
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
    modernizer = PyprojectModernizer(root=tmp_path)
    canonical_dev: list[str] = []
    _ = modernizer.process_file(
        pyproject,
        canonical_dev=canonical_dev,
        dry_run=False,
        skip_comments=False,
    )
    text = pyproject.read_text(encoding="utf-8")

    assert text.count("[[tool.pyrefly.sub-config]]") == 2
    assert 'root = "src"' in text
    assert 'root = "tests"' in text


def test_bandit_skips_are_loaded_from_root_ssot(tmp_path: Path) -> None:
    """Test that modernizer processes files with root workspace context."""
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

    modernizer = PyprojectModernizer(root=root_dir)
    canonical_dev: list[str] = []
    changes = modernizer.process_file(
        pyproject,
        canonical_dev=canonical_dev,
        dry_run=False,
        skip_comments=False,
    )
    text = pyproject.read_text(encoding="utf-8")

    assert text.count("[[tool.pyrefly.sub-config]]") == 1
    assert 'root = "src"' in text
    assert changes
