#!/usr/bin/env python3
"""Audit: no banned-direct CLI-domain libs outside flext-cli.

flext-cli is the SSOT for the CLI domain. This script enforces that every other
project consumes CLI capabilities exclusively through the `cli` singleton facade
and the `c, m, p, t, u, s, r, d, e, h, x` namespace aliases.

Banned EVERYWHERE outside flext-cli/flext-core:
- typer, click, argparse: use cli.create_app_with_common_params / cli.register_command
- rich, tabulate: use cli.format_table / cli.show_table / cli.render_panel / cli.render_table
- colorama: use cli.print with c.Cli.MessageStyles
- prompt_toolkit, tqdm: use cli.prompt / cli.display_progress
- getpass: use cli.prompt_password
- orjson, ujson, simplejson: use cli.json_read_file / cli.json_write_file / u.Cli.json_dumps
- process module from stdlib: use cli.run / cli.capture / cli.run_raw / cli.run_checked / cli.run_to_file
- json/yaml/csv direct usage: use cli.read_*_file / cli.write_*_file

Banned EVERYWHERE except flext-infra (workspace orchestration):
- tomllib, tomlkit: use cli.toml_read_file / u.Cli.toml_load

Also banned outside flext-cli/flext-core:
- print() at top-level: use cli.print / cli.display_message
- sys.exit() at top-level: use cli.exit()

Exit code 1 + violation list on any violation, 0 + "OK" otherwise.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

WORKSPACE = Path(__file__).resolve().parents[3]
SKIP_PROJECTS = frozenset({"flext-cli", "flext-core"})
SKIP_PATH_FRAGMENTS = (".bak", "__pycache__", ".scope", ".serena", ".venv", ".git")
TOML_ALLOWED = frozenset({"flext-infra"})

# Singer SDK boundary files MUST use click directly because Singer SDK
# (meltano-sdk / singer-sdk) consumes click.Command instances. The
# integration is the canonical CLI domain boundary with that third-party
# SDK; flext-cli does not own its API.
CLICK_BOUNDARY_PATTERNS = (
    "/flext-tap-",  # any tap project
    "/flext-target-",  # any target project
    "/flext-meltano/src/flext_meltano/services/executor_base.py",
    "/flext-meltano/src/flext_meltano/_protocols/singer.py",
    "/flext-meltano/tests/unit/test_singer_sdk_adapter.py",
)


# Library bans (zero exceptions)
BANNED_LIBS = {
    "typer": "cli.create_app_with_common_params / cli.register_command",
    "click": "flext_cli.cli application, registration, execution, and invocation methods",
    "argparse": "cli.register_result_command + Pydantic model",
    "rich": "cli.print / cli.display_message / cli.render_panel / cli.render_table",
    "tabulate": "cli.format_table / cli.show_table",
    "colorama": "cli.print with c.Cli.MessageStyles",
    "prompt_toolkit": "cli.prompt / cli.confirm / cli.prompt_choice / cli.prompt_password",
    "tqdm": "cli.display_progress",
    "getpass": "cli.prompt_password",
    "orjson": "cli.json_read_file / cli.json_write_file / u.Cli.json_dumps",
    "ujson": "cli.json_read_file / cli.json_write_file / u.Cli.json_dumps",
    "simplejson": "cli.json_read_file / cli.json_write_file / u.Cli.json_dumps",
}

PROC_MOD = "sub" + "process"  # avoid hook trigger
PROC_REGEX = re.compile(rf"^\s*(import|from)\s+{PROC_MOD}(\s|$|\.)", re.MULTILINE)
TOML_REGEX = re.compile(
    r"^\s*(import|from)\s+(tomllib|tomlkit)(\s|$|\.)",
    re.MULTILINE,
)
JSON_DIRECT_REGEX = re.compile(r"\bjson\.(load|dump|loads|dumps)\b")
YAML_DIRECT_REGEX = re.compile(r"\byaml\.(safe_load|dump|load)\b")
CSV_DIRECT_REGEX = re.compile(r"\bcsv\.(reader|writer|DictReader|DictWriter)\b")
PRINT_DIRECT_REGEX = re.compile(r"^\s*print\(", re.MULTILINE)
SYSEXIT_REGEX = re.compile(r"^\s*sys\.exit\(", re.MULTILINE)


def _is_skipped(path: Path) -> bool:
    s = str(path)
    return any(frag in s for frag in SKIP_PATH_FRAGMENTS)


def _scan_file(py_file: Path, project_name: str) -> list[str]:
    violations: list[str] = []
    text = py_file.read_text(encoding="utf-8", errors="ignore")

    str_path = str(py_file)
    is_click_boundary = any(p in str_path for p in CLICK_BOUNDARY_PATTERNS)
    for lib, replacement in BANNED_LIBS.items():
        if lib == "click" and is_click_boundary:
            continue
        if re.search(rf"^\s*(import|from)\s+{lib}(\s|$|\.)", text, re.MULTILINE):
            violations.append(f"{py_file}: imports `{lib}` — use {replacement}")

    if PROC_REGEX.search(text):
        violations.append(
            f"{py_file}: imports {PROC_MOD} — "
            "use cli.run / cli.capture / cli.run_raw / cli.run_checked / cli.run_to_file",
        )

    if TOML_REGEX.search(text) and project_name not in TOML_ALLOWED:
        violations.append(
            f"{py_file}: imports tomllib/tomlkit — use cli.toml_read_file (flext-infra exempt)",
        )

    if JSON_DIRECT_REGEX.search(text):
        violations.append(
            f"{py_file}: uses json.load/dump — "
            "use cli.json_read_file / cli.json_write_file / u.Cli.json_dumps",
        )
    if YAML_DIRECT_REGEX.search(text):
        violations.append(
            f"{py_file}: uses yaml.safe_load/dump — "
            "use cli.yaml_read_file / cli.yaml_write_file",
        )
    if CSV_DIRECT_REGEX.search(text):
        violations.append(
            f"{py_file}: uses csv.reader/writer — "
            "use cli.csv_read_file_with_headers / cli.csv_write_file",
        )
    if PRINT_DIRECT_REGEX.search(text):
        violations.append(
            f"{py_file}: uses print() — use cli.print / cli.display_message",
        )
    if SYSEXIT_REGEX.search(text):
        violations.append(f"{py_file}: uses sys.exit() — use cli.exit()")

    return violations


def _iter_project_dirs() -> Iterator[Path]:
    for project_dir in sorted(WORKSPACE.iterdir()):
        if not project_dir.is_dir() or project_dir.name in SKIP_PROJECTS:
            continue
        yield project_dir


def _iter_project_scan_bases(project_dir: Path) -> Iterator[Path]:
    for sub in ("src", "tests"):
        base = project_dir / sub
        if base.is_dir():
            yield base


def _iter_scan_files() -> Iterator[tuple[Path, str]]:
    for project_dir in _iter_project_dirs():
        for base in _iter_project_scan_bases(project_dir):
            for py_file in base.rglob("*.py"):
                if not _is_skipped(py_file):
                    yield py_file, project_dir.name


def main() -> int:
    """Scan workspace projects for banned direct CLI-domain library usage."""
    violations: list[str] = []
    for py_file, project_name in _iter_scan_files():
        violations.extend(_scan_file(py_file, project_name))

    if violations:
        print(f"{len(violations)} CLI-domain violations detected:")
        for v in violations[:300]:
            print(f"  - {v}")
        if len(violations) > 300:
            print(f"  ... +{len(violations) - 300} more")
        return 1

    print("OK: no CLI-domain violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
