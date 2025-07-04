#!/usr/bin/env python3
"""Script to standardize all pyproject.toml files to maximum strictness with Python 3.13."""
import re
from pathlib import Path
from typing import Dict, List, Tuple


def apply_strict_updates(content: str, project_name: str, project_module: str) -> str:
    """Apply strict standardization updates to pyproject.toml content."""
    # Python version strictness
    content = re.sub(
        r'requires-python = "[^"]*"',
        'requires-python = ">=3.13"',
        content
    )

    # Add Python 3 :: Only classifier
    content = re.sub(
        r'("Programming Language :: Python :: 3\.13",)',
        r'\1\n    "Programming Language :: Python :: 3 :: Only",',
        content
    )

    # Update dev dependencies with maximum strictness tools
    dev_deps_pattern = r"\[tool\.poetry\.group\.dev\.dependencies\](.*?)(?=\[tool\.poetry\.group\.|$)"

    strict_dev_deps = """[tool.poetry.group.dev.dependencies]
# Testing - Maximum strictness
pytest = "^8.3.0"
pytest-cov = "^6.0.0"
pytest-asyncio = "^0.24.0"
pytest-benchmark = "^4.0.0"
pytest-mock = "^3.14.0"
pytest-xdist = "^3.6.0"
pytest-timeout = "^2.3.0"
pytest-randomly = "^3.15.0"
pytest-sugar = "^1.0.0"
pytest-clarity = "^1.0.1"

# Code quality - Maximum strictness
ruff = "^0.8.4"
black = "^24.10.0"
isort = "^5.13.0"
mypy = "^1.13.0"
bandit = { extras = ["toml"], version = "^1.7.0" }
pre-commit = "^4.0.0"
vulture = "^2.14"
radon = "^6.0.1"

# Type stubs
types-requests = "^2.32.0"
types-setuptools = "^75.6.0"
types-redis = "^4.6.0"
types-pyyaml = "^6.0.12"
types-python-dateutil = "^2.9.0"

# Documentation
mkdocs = "^1.6.0"
mkdocs-material = "^9.5.0"
sphinx = "^8.0.0"
sphinx-rtd-theme = "^3.0.0"
myst-parser = "^4.0.0"

# Development tools
ipython = "^8.29.0"
rich = "^13.9.0"
rich-traceback = "^1.0.3\""""

    content = re.sub(dev_deps_pattern, strict_dev_deps, content, flags=re.DOTALL)

    # Add semgrep to security dependencies
    content = re.sub(
        r'(\[tool\.poetry\.group\.security\.dependencies\].*?safety = "[^"]*")',
        r'\1\nsemgrep = "^1.91.0"',
        content,
        flags=re.DOTALL
    )

    # Add hypothesis to test dependencies
    if "hypothesis" not in content:
        content = re.sub(
            r"(\[tool\.poetry\.group\.test\.dependencies\].*?)",
            r'\1\nhypothesis = "^6.112.0"',
            content,
            flags=re.DOTALL
        )

    # Update ruff configuration for maximum strictness
    ruff_config = """[tool.ruff]
target-version = "py313"
line-length = 88
fix = true
unsafe-fixes = false
respect-gitignore = true
src = ["src", "tests", "scripts"]
extend-exclude = [
    "__pycache__",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "build",
    "dist",
    "htmlcov",
    "node_modules",
]"""

    content = re.sub(
        r"\[tool\.ruff\].*?(?=\[tool\.ruff\.lint\])",
        ruff_config + "\n\n",
        content,
        flags=re.DOTALL
    )

    # Update ruff lint configuration
    ruff_lint_config = """[tool.ruff.lint]
# SELECT ALL RULES - MAXIMUM STRICTNESS
select = ["ALL"]
ignore = [
    # MANDATORY: Only formatter conflicts that cannot be auto-fixed
    "COM812",  # trailing-comma-missing (handled by formatter)
    "ISC001",  # implicit-str-concat (conflicts with formatter)
    "D203",    # one-blank-line-before-class (conflicts with D211)
    "D213",    # multi-line-docstring-summary-second-line (conflicts with D212)

    # STRICT MODE: Only allow critical exceptions
    "E501",    # line-too-long (handled by formatter)
    "PLR0913", # too-many-arguments (context-dependent)
    "PLR0915", # too-many-statements (context-dependent)
    "C901",    # too-complex (context-dependent)

    # TEMPORARY: Project-specific exceptions (remove progressively)
    "T201",    # print statements (remove in production)
    "S101",    # assert statements (allowed in tests)
    "INP001",  # implicit-namespace-package (project structure)
]"""

    content = re.sub(
        r"\[tool\.ruff\.lint\].*?(?=\[tool\.ruff\.lint\.per-file-ignores\])",
        ruff_lint_config + "\n\n",
        content,
        flags=re.DOTALL
    )

    # Update per-file ignores
    per_file_ignores = """[tool.ruff.lint.per-file-ignores]
"tests/*" = [
    "S101",    # assert statements
    "PLR2004", # magic values
    "D",       # docstrings
    "ANN",     # type annotations
    "ARG",     # unused arguments
    "FBT",     # boolean trap
    "SLF001",  # private access
]
"*/tests/*" = [
    "S101",    # assert statements
    "PLR2004", # magic values
    "D",       # docstrings
    "ANN",     # type annotations
    "ARG",     # unused arguments
    "FBT",     # boolean trap
    "SLF001",  # private access
]
"__init__.py" = ["D104"]
"conftest.py" = ["D"]
"scripts/*" = ["T201", "D", "ERA001"]
"examples/*" = ["T201", "D", "ERA001"]"""

    content = re.sub(
        r"\[tool\.ruff\.lint\.per-file-ignores\].*?(?=\[tool\.ruff\.format\])",
        per_file_ignores + "\n\n",
        content,
        flags=re.DOTALL
    )

    # Update isort config
    isort_config = f"""[tool.isort]
profile = "black"
line_length = 88
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
known_first_party = ["{project_module}"]
known_local_folder = ["{project_module}"]
force_single_line = false
combine_as_imports = true
order_by_type = true
atomic = true
remove_redundant_aliases = true
honor_noqa = true"""

    content = re.sub(
        r"\[tool\.isort\].*?(?=\[tool\.mypy\])",
        isort_config + "\n\n",
        content,
        flags=re.DOTALL
    )

    # Update mypy for maximum strictness
    mypy_config = """[tool.mypy]
python_version = "3.13"
# MAXIMUM STRICTNESS
strict = true
warn_return_any = true
warn_unused_configs = true
warn_redundant_casts = true
warn_unused_ignores = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_no_return = true
warn_unreachable = true
strict_equality = true
show_error_codes = true
show_error_context = true
pretty = true
color_output = true
error_summary = true
ignore_missing_imports = false
# Additional strictness
disallow_any_generics = true
disallow_subclassing_any = true
disallow_untyped_calls = true
disallow_any_unimported = true
disallow_any_expr = false  # Too strict for practical use
disallow_any_decorated = true
disallow_any_explicit = false  # Too strict for practical use
warn_unused_ignores = true
warn_return_any = true
warn_unreachable = true
strict_optional = true
strict_concatenate = true"""

    content = re.sub(
        r"\[tool\.mypy\].*?(?=\[\[tool\.mypy\.overrides\]\])",
        mypy_config + "\n\n",
        content,
        flags=re.DOTALL
    )

    # Update pytest configuration for maximum strictness
    content = re.sub(
        r"--cov-fail-under=\d+",
        "--cov-fail-under=95",
        content
    )

    content = re.sub(
        r"--maxfail=\d+",
        "--maxfail=5",
        content
    )

    # Add additional pytest options if not present
    if "--timeout=30" not in content:
        content = re.sub(
            r'(--maxfail=5",)',
            r'\1\n    "--timeout=30",\n    "--disable-warnings",\n    "--randomly-seed=1234",\n    "--randomly-dont-reorganize",',
            content
        )

    # Add security marker if not present
    if '"security: marks tests as security tests"' not in content:
        content = re.sub(
            r'("performance: marks tests as performance tests",)',
            r'\1\n    "security: marks tests as security tests",',
            content
        )

    # Add log CLI configuration
    if "log_cli = true" not in content:
        content = re.sub(
            r'(asyncio_mode = "auto")',
            r'\1\nlog_cli = true\nlog_cli_level = "INFO"\nlog_cli_format = "%(asctime)s [%(levelname)8s] %(name)s: %(message)s"\nlog_cli_date_format = "%Y-%m-%d %H:%M:%S"',
            content
        )

    # Update coverage configuration
    content = re.sub(
        r"fail_under = \d+",
        "fail_under = 95  # STRICT: 95% coverage minimum",
        content
    )

    # Add coverage data file and concurrency if not present
    if "data_file" not in content:
        content = re.sub(
            r'(\*/.eggs/\*",\n\])',
            r'\1\ndata_file = "reports/.coverage"\nparallel = true\nconcurrency = ["thread", "multiprocessing"]',
            content
        )

    return content


def update_pyproject_files():
    """Update all core FLEXT pyproject.toml files."""
    projects = [
        ("flext-auth", "flext_auth"),
        ("flext-grpc", "flext_grpc"),
        ("flext-web", "flext_web"),
        ("flext-cli", "flext_cli"),
        ("flext-plugin", "flext_plugin"),
        ("flext-observability", "flext_observability"),
        ("flext-meltano", "flext_meltano"),
    ]

    workspace_root = Path("/home/marlonsc/flext")

    for project_name, project_module in projects:
        pyproject_path = workspace_root / project_name / "pyproject.toml"

        if pyproject_path.exists():
            print(f"Updating {project_name}/pyproject.toml...")

            # Read current content
            content = pyproject_path.read_text()

            # Apply strict updates
            updated_content = apply_strict_updates(content, project_name, project_module)

            # Write back
            pyproject_path.write_text(updated_content)

            print(f"✅ Updated {project_name}/pyproject.toml")
        else:
            print(f"❌ {project_name}/pyproject.toml not found")


if __name__ == "__main__":
    update_pyproject_files()
    print("\n🎉 All pyproject.toml files updated with maximum strictness!")
