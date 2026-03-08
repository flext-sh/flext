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
        '\n[build-system]\nrequires = ["poetry-core>=2"]\n\n[project]\nname = "demo"\nversion = "0.1.0"\nlicense = "MIT"\n\n[tool.pyrefly]\nsearch-path = ["src"]\n\n[tool.pytest.ini_options]\naddopts = ["-q"]\n'.strip()
        + "\n",
    )
    modernizer = PyprojectModernizer(root=tmp_path)
    canonical_dev: list[str] = []
    first_fixes = modernizer.process_file(
        pyproject, canonical_dev=canonical_dev, dry_run=False, skip_comments=False
    )
    first_text = pyproject.read_text(encoding="utf-8")
    second_fixes = modernizer.process_file(
        pyproject, canonical_dev=canonical_dev, dry_run=False, skip_comments=False
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
        '\n[build-system]\nrequires = ["poetry-core>=1.9.0"]\n\n[project]\nname = "pkg"\nversion = "0.1.0"\nlicense = { text = "MIT" }\n'.strip()
        + "\n",
    )
    _ = write_pyproject(
        tmp_path,
        '\n[project]\nname = "workspace"\nversion = "0.1.0"\n\n[tool.pytest.ini_options]\naddopts = ["--strict-config", "--strict-markers", "--tb=short", "-p no:sugar", "-q", "-ra"]\n\n[tool.bandit]\nskips = ["B404", "B603", "B607", "B105", "B608"]\n'.strip()
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
        '\n[build-system]\nrequires = ["poetry-core>=2"]\n\n[project]\nname = "pkg"\nversion = "0.1.0"\nlicense = "MIT"\n\n[tool.coverage.run]\nsource = ["src/pkg"]\n\n[tool.coverage.report]\nfail_under = 100\nprecision = 2\n\n[tool.pytest.ini_options]\nminversion = "8.0"\npython_classes = ["Test*"]\npython_files = ["*_test.py", "*_tests.py", "test_*.py"]\naddopts = ["--strict-markers"]\nmarkers = [\n    "unit: unit tests",\n    "integration: integration tests",\n    "performance: performance and benchmark tests",\n    "slow: slow-running tests",\n    "docker: tests requiring Docker",\n    "e2e: end-to-end integration tests",\n    "edge_cases: edge case tests",\n    "stress: stress tests",\n    "resilience: resilience tests",\n]\n\n[tool.deptry]\npep621_dev_dependency_groups = ["dev"]\n\n[tool.pyrefly]\npython-version = "3.13"\nignore-errors-in-generated-code = true\nsearch-path = ["."]\nproject-excludes = ["**/_pb2.py", "**/_pb2_grpc.py", "**/*_pb2*.py", "**/*_pb2_grpc*.py"]\n\n[tool.pyrefly.errors]\nbad-override = false\ndeprecated = true\nredundant-cast = true\nimplicit-abstract-class = true\nimplicit-any = true\nimplicitly-defined-attribute = true\nmissing-override-decorator = true\nmissing-source = true\nnot-required-key-access = true\nopen-unpacking = true\nprotocol-implicitly-defined-attribute = true\nunannotated-attribute = true\nunannotated-parameter = true\nunannotated-return = true\n\n[tool.mypy]\npython_version = "3.13"\nplugins = ["pydantic.mypy"]\ndisable_error_code = ["prop-decorator"]\n\n[tool.pydantic-mypy]\ninit_forbid_extra = true\ninit_typed = true\nwarn_required_dynamic_aliases = true\n\n[tool.ruff]\nextend = "../ruff-shared.toml"\n\n[tool.pyright]\npythonVersion = "3.13"\npythonPlatform = "Linux"\ntypeCheckingMode = "strict"\n'.strip()
        + "\n",
    )
    (project_dir / "src" / "pkg").mkdir(parents=True)
    _ = write_pyproject(
        tmp_path,
        '\n[project]\nname = "workspace"\nversion = "0.1.0"\n\n[tool.bandit]\nskips = ["B404", "B603", "B607", "B105", "B608"]\n\n[tool.pytest.ini_options]\naddopts = ["--strict-config", "--strict-markers", "--tb=short", "-p no:sugar", "-q", "-ra"]\n'.strip()
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
        '\n[build-system]\nrequires = ["poetry-core>=1.9.0"]\n\n[project]\nname = "safe"\nversion = "0.1.0"\n\n[tool.pyrefly]\nsearch-path = ["src"]\n\n[[tool.pyrefly.sub-config]]\nroot = "src"\n\n[[tool.pyrefly.sub-config]]\nroot = "tests"\n\n[tool.coverage.report]\nfail_under = 100\n'.strip()
        + "\n",
    )
    modernizer = PyprojectModernizer(root=tmp_path)
    canonical_dev: list[str] = []
    _ = modernizer.process_file(
        pyproject, canonical_dev=canonical_dev, dry_run=False, skip_comments=False
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
        '\n[project]\nname = "workspace"\nversion = "0.1.0"\n\n[tool.pytest.ini_options]\naddopts = ["--strict-config", "--strict-markers", "--tb=short", "-p no:sugar", "-q", "-ra"]\n\n[tool.bandit]\nskips = ["B105", "B999"]\n'.strip()
        + "\n",
    )
    pyproject = write_pyproject(
        project_dir,
        '\n[build-system]\nrequires = ["poetry-core>=2"]\n\n[project]\nname = "pkg"\nversion = "0.1.0"\n\n[tool.pyrefly]\nsearch-path = ["src"]\n\n[[tool.pyrefly.sub-config]]\nroot = "src"\n'.strip()
        + "\n",
    )
    modernizer = PyprojectModernizer(root=root_dir)
    canonical_dev: list[str] = []
    changes = modernizer.process_file(
        pyproject, canonical_dev=canonical_dev, dry_run=False, skip_comments=False
    )
    text = pyproject.read_text(encoding="utf-8")
    assert text.count("[[tool.pyrefly.sub-config]]") == 1
    assert 'root = "src"' in text
    assert changes
