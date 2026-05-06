#!/usr/bin/env python3
"""Audit: no project may import FlextCli<X> concrete classes outside extension files.

Allowed:
- src/<projeto>/{constants,models,protocols,typings,utilities,settings}.py
  may import FlextCli<X> for MRO namespace extension (canonical SSOT pattern).
- `FlextCli` (the singleton class) may appear in `if TYPE_CHECKING:` blocks of
  test helpers for inheritance-typed-as-class patterns. Detected via heuristic.

Forbidden everywhere else:
- Direct import of FlextCli<X> concrete classes.
- Use cli (singleton), c, m, p, t, u, s, r, d, e, h, x aliases instead.

Exit code 1 + violation list on any violation, 0 + "OK" otherwise.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ALLOWED_EXTENSION_FILES = frozenset({
    "constants.py",
    "models.py",
    "protocols.py",
    "typings.py",
    "utilities.py",
    "settings.py",
})
PUBLIC_FACADE_NAMES = frozenset({"FlextCli"})  # only the class type for type(cli)
WORKSPACE = Path("/home/marlonsc/flext")
SKIP_PROJECTS = frozenset({"flext-cli", "flext-core"})

CONCRETE_IMPORT_RE = re.compile(
    r"^from\s+flext_cli\s+import\s+(?P<imports>.+?)$",
    re.MULTILINE,
)
FLEXT_CLI_CONCRETE_RE = re.compile(r"\bFlextCli[A-Z]\w*")
SKIP_PATH_FRAGMENTS = (".bak", "__pycache__", ".scope", ".serena", ".venv", ".git")


def _is_skipped(path: Path) -> bool:
    s = str(path)
    return any(frag in s for frag in SKIP_PATH_FRAGMENTS)


def _check_file(py_file: Path, *, is_extension_allowed: bool) -> list[str]:
    violations: list[str] = []
    text = py_file.read_text(encoding="utf-8", errors="ignore")
    for match in CONCRETE_IMPORT_RE.finditer(text):
        for name in FLEXT_CLI_CONCRETE_RE.findall(match.group("imports")):
            if name in PUBLIC_FACADE_NAMES:
                continue
            if is_extension_allowed:
                continue
            violations.append(
                f"{py_file}: imports concrete `{name}` (use cli/c/m/p/t/u/s)"
            )
    return violations


def main() -> int:
    """Scan workspace projects for forbidden concrete FlextCli imports."""
    violations: list[str] = []
    for project_dir in sorted(WORKSPACE.iterdir()):
        if not project_dir.is_dir() or project_dir.name in SKIP_PROJECTS:
            continue
        src = project_dir / "src"
        if src.is_dir():
            for py_file in src.rglob("*.py"):
                if _is_skipped(py_file):
                    continue
                allowed = py_file.name in ALLOWED_EXTENSION_FILES
                violations.extend(_check_file(py_file, is_extension_allowed=allowed))
        tests = project_dir / "tests"
        if tests.is_dir():
            for py_file in tests.rglob("*.py"):
                if _is_skipped(py_file):
                    continue
                violations.extend(_check_file(py_file, is_extension_allowed=False))

    if violations:
        print(f"FlextCli* concrete-import violations: {len(violations)}")
        for v in violations[:200]:
            print(f"  - {v}")
        if len(violations) > 200:
            print(f"  ... +{len(violations) - 200} more")
        return 1
    print("OK: no FlextCli* concrete-import violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
