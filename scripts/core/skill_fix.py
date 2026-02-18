#!/usr/bin/env python3
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
"""Data-driven skill fixer for rules.yml-based auto-fix gates.

Reads fix metadata from flat keys on each rule entry:
  fix_auto, fix_type, fix_file, fix_instruction, fix_description.

Nested ``fix:`` sub-dicts are rejected — flat keys are the only
supported format.

Safety protocol per file:
  1. Record SHA-256 hash before fix
  2. Backup original to temp dir
  3. Apply ast-grep rewrite
  4. Verify: syntax check, re-scan violation count
  5. If worse or broken -> restore backup, write .rej file
  6. Report accepted/rejected per file in fix-report.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:
    yaml = None  # type: ignore[assignment]

SKILLS_DIR = Path(".claude/skills")
FIX_REPORT_DEFAULT = ".claude/skills/{skill}/fix-report.json"


VALID_FIX_TYPES = frozenset({"ast-grep", "custom"})


def validate_flat_fix_keys(rule: dict[str, object]) -> None:
    """Reject nested fix: sub-dict and invalid fix_type values."""
    if isinstance(rule.get("fix"), dict):
        rule_id = str(rule.get("id", "unknown"))
        msg = (
            f"Rule '{rule_id}' uses nested 'fix:' sub-dict. "
            "Use flat keys: fix_auto, fix_type, fix_instruction, "
            "fix_file, fix_description."
        )
        raise ValueError(msg)
    ft = rule.get("fix_type")
    if ft == "manual":
        rule_id = str(rule.get("id", "unknown"))
        msg = (
            f"Rule '{rule_id}': fix_type: manual is invalid. "
            "Remove fix_type entirely when fix_auto: false."
        )
        raise ValueError(msg)
    if ft and ft not in VALID_FIX_TYPES:
        rule_id = str(rule.get("id", "unknown"))
        msg = (
            f"Rule '{rule_id}': fix_type: '{ft}' is invalid. "
            f"Valid values: {sorted(VALID_FIX_TYPES)}"
        )
        raise ValueError(msg)


EXIT_OK = 0
EXIT_FAIL = 1
EXIT_USAGE = 2
EXIT_INFRA = 3


def eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


def run_cmd(
    command: list[str],
    cwd: Path,
    timeout: int = 300,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            check=False,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return subprocess.CompletedProcess(
            command, 127, "", f"Command not found: {command[0]}"
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(command, 124, "", "Timeout")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_rules_yml(path: Path) -> dict[str, object]:
    if yaml is None:
        msg = "PyYAML is required: pip install pyyaml"
        raise RuntimeError(msg)
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        msg = f"rules.yml must be a mapping: {path}"
        raise ValueError(msg)
    return data


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# File discovery (reuse from skill_validate.py pattern)
# ---------------------------------------------------------------------------

_git_files_cache: dict[str, tuple[float, list[str]]] = {}
CACHE_TTL_SECONDS = 300


def get_tracked_files(project_path: Path) -> list[str]:
    key = str(project_path)
    now = time.monotonic()
    cached = _git_files_cache.get(key)
    if cached and (now - cached[0]) < CACHE_TTL_SECONDS:
        return cached[1]
    result = run_cmd(["git", "ls-files"], cwd=project_path, timeout=120)
    if result.returncode != 0:
        msg = f"git ls-files failed in {project_path}: {result.stderr}"
        raise RuntimeError(msg)
    files = sorted({
        line.strip() for line in (result.stdout or "").splitlines() if line.strip()
    })
    _git_files_cache[key] = (now, files)
    return files


def discover_projects(root: Path) -> dict[str, list[str]]:
    """Discover workspace projects (matches Makefile logic)."""
    result: dict[str, list[str]] = {"flext": [], "external": [], "root": ["."]}
    gitmodules = root / ".gitmodules"
    submodule_paths: set[str] = set()
    if gitmodules.exists():
        for line in gitmodules.read_text().splitlines():
            line = line.strip()
            if line.startswith("path = "):
                submodule_paths.add(line.split("=", 1)[1].strip())
    for sp in sorted(submodule_paths):
        p = root / sp
        if p.is_dir() and (p / "pyproject.toml").exists():
            result["flext"].append(sp)
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        name = child.name
        if name in submodule_paths:
            continue
        if not (child / "pyproject.toml").exists():
            continue
        toml_text = (child / "pyproject.toml").read_text(errors="replace")
        if "flext-core" in toml_text or "flext_core" in toml_text:
            result["external"].append(name)
    return result


def all_project_paths(root: Path) -> dict[str, Path]:
    discovered = discover_projects(root)
    lookup: dict[str, Path] = {}
    for name in discovered.get("flext", []):
        lookup[name] = root / name
    for name in discovered.get("external", []):
        lookup[name] = root / name
    lookup["."] = root
    return lookup


# ---------------------------------------------------------------------------
# Syntax check
# ---------------------------------------------------------------------------


def check_syntax(filepath: Path) -> tuple[bool, str]:
    """Parse file with ast.parse for pure syntax checking (no imports).

    Uses ast.parse instead of py_compile to avoid false failures from
    module-name shadowing (e.g. a project's enum.py shadowing stdlib enum).
    """
    import ast as _ast

    try:
        source = filepath.read_text(encoding="utf-8")
        _ast.parse(source, filename=str(filepath))
        return True, ""
    except SyntaxError as exc:
        return False, f"SyntaxError: {exc}"


def check_import(filepath: Path) -> tuple[bool, str]:
    import ast as _ast
    import builtins

    try:
        source = filepath.read_text(encoding="utf-8")
        tree = _ast.parse(source, filename=str(filepath))
    except SyntaxError as exc:
        return False, f"SyntaxError: {exc}"

    imported_names: set[str] = set()
    has_star_import = False
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Import):
            imported_names.update(
                alias.asname or alias.name.split(".")[0] for alias in node.names
            )
        elif isinstance(node, _ast.ImportFrom) and node.module:
            imported_names.add(node.module.split(".")[0])
            for alias in node.names:
                if alias.name == "*":
                    has_star_import = True
                    continue
                imported_names.add(alias.asname or alias.name)

    load_names_in_body: set[str] = set()
    for node in _ast.walk(tree):
        # Only consider LOAD contexts. Store/Del contexts are definitions/assignments.
        if isinstance(node, _ast.Name) and isinstance(node.ctx, _ast.Load):
            load_names_in_body.add(node.id)
        elif isinstance(node, _ast.Attribute) and isinstance(node.value, _ast.Name):
            load_names_in_body.add(node.value.id)

    builtin_names = set(dir(builtins))

    defined_names: set[str] = set()
    for node in _ast.iter_child_nodes(tree):
        if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.ClassDef)):
            defined_names.add(node.name)
        elif isinstance(node, _ast.Assign):
            for target in node.targets:
                if isinstance(target, _ast.Name):
                    defined_names.add(target.id)

    suspicious: list[str] = []
    for name in load_names_in_body:
        if name in builtin_names or name in defined_names or name in imported_names:
            continue
        if name[0:1].isupper() and name not in {"True", "False", "None", "Ellipsis"}:
            if not has_star_import:
                suspicious.append(name)

    if suspicious:
        joined = ", ".join(sorted(suspicious))
        return False, f"Possibly undefined names (missing imports?): {joined}"
    return True, ""


# ---------------------------------------------------------------------------
# Count violations for a single file using a specific rule
# ---------------------------------------------------------------------------


def count_ast_grep_violations(
    rule_file: Path,
    target_file: Path,
    project_root: Path,
) -> int:
    """Count ast-grep violations in a single file."""
    if not rule_file.exists():
        return 0
    result = run_cmd(
        [
            "sg",
            "scan",
            "--rule",
            str(rule_file),
            "--json=stream",
            "--no-ignore",
            "hidden",
            str(target_file),
        ],
        cwd=project_root,
        timeout=60,
    )
    if result.returncode == 127:
        eprint("Warning: ast-grep (sg) not found")
        return 0
    count = 0
    for line in (result.stdout or "").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            json.loads(line)
            count += 1
        except json.JSONDecodeError:
            continue
    return count


def _build_script_command(script: Path) -> list[str]:
    if script.suffix == ".py":
        return [sys.executable, str(script)]
    return [str(script)]


def apply_custom_fix(
    fix_script: Path,
    target_file: Path,
    project_root: Path,
) -> bool:
    """Run a custom fix script on a single file. Returns True on success."""
    command = _build_script_command(fix_script)
    command.extend(["--root", str(project_root), "--file", str(target_file), "--apply"])
    result = run_cmd(command, cwd=project_root, timeout=60)
    return result.returncode == 0


# ---------------------------------------------------------------------------
# .rej file writer
# ---------------------------------------------------------------------------


def write_rej_file(
    target_file: Path,
    reason: str,
    rule_id: str,
    before_hash: str,
    after_hash: str,
    before_violations: int,
    after_violations: int,
    syntax_ok: bool,
    syntax_output: str,
    diff_text: str,
) -> Path:
    """Write a .rej file next to the target file with failure details."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    rej_path = target_file.parent / f"{target_file.name}.rej-{timestamp}-{rule_id}.rej"
    lines = [
        f"File: {target_file}",
        f"Rule: {rule_id}",
        f"Timestamp: {timestamp}",
        f"Reason: {reason}",
        f"Before SHA-256: {before_hash}",
        f"After SHA-256: {after_hash}",
        f"Violations before: {before_violations}",
        f"Violations after: {after_violations}",
        f"Syntax OK: {syntax_ok}",
        "",
    ]
    if syntax_output:
        lines.extend(("Syntax check output:", syntax_output, ""))
    if diff_text:
        lines.extend(("Diff:", diff_text, ""))
    rej_path.write_text("\n".join(lines), encoding="utf-8")
    return rej_path


def normalize_exclude_globs(
    excludes: list[str],
    known_projects: set[str],
) -> list[str]:
    """Strip project-name prefixes from exclude globs.

    Exclude patterns like ``flext-core/src/foo.py`` never match tracked
    files which are project-relative (``src/foo.py``).  This converts
    them to ``src/foo.py`` and emits a warning.
    """
    result: list[str] = []
    for pat in excludes:
        stripped = pat
        for proj in known_projects:
            prefix = proj + "/"
            if pat.startswith(prefix):
                stripped = pat[len(prefix) :]
                eprint(
                    f"  Warning: exclude '{pat}' stripped to '{stripped}' (project-relative)"
                )
                break
        result.append(stripped)
    return result


def find_candidate_files(
    rule_obj: dict[str, object],
    skill_dir: Path,
    project_path: Path,
    tracked_files: list[str],
    include_globs: list[str],
    exclude_globs: list[str] | None = None,
) -> list[Path]:
    """Find files that have violations for a given rule."""
    import fnmatch

    rule_type = str(rule_obj.get("type", ""))
    candidates: list[Path] = []

    # Filter tracked files by include globs
    includes = include_globs or ["**/*.py"]
    excludes = exclude_globs or []
    filtered = [
        f
        for f in tracked_files
        if any(fnmatch.fnmatch(f, pat) for pat in includes)
        and not any(fnmatch.fnmatch(f, epat) for epat in excludes)
    ]

    if rule_type == "ast-grep":
        rule_file_rel = str(rule_obj.get("file", ""))
        rule_file = skill_dir / rule_file_rel
        if not rule_file.exists():
            return []
        for rel in filtered:
            full = project_path / rel
            if not full.exists() or not full.is_file():
                continue
            count = count_ast_grep_violations(rule_file, full, project_path)
            if count > 0:
                candidates.append(full)

    elif rule_type == "custom":
        for rel in filtered:
            full = project_path / rel
            if full.exists() and full.is_file():
                candidates.append(full)

    return candidates


def apply_ast_grep_fix(
    fix_file: Path,
    target_file: Path,
    project_root: Path,
) -> bool:
    """Apply ast-grep rewrite to a single file. Returns True if changes were made."""
    result = run_cmd(
        [
            "sg",
            "scan",
            "--rule",
            str(fix_file),
            "--update-all",
            "--no-ignore",
            "hidden",
            str(target_file),
        ],
        cwd=project_root,
        timeout=60,
    )
    return result.returncode in {0, 1}  # sg returns 1 on matches


def get_diff(original: Path, modified: Path) -> str:
    """Get unified diff between two files."""
    result = run_cmd(
        ["diff", "-u", str(original), str(modified)],
        cwd=original.parent,
        timeout=10,
    )
    return result.stdout or ""


def _count_violations_for_rule(
    rule_obj: dict[str, object],
    scan_file: Path | None,
    target: Path,
    project_path: Path,
) -> int:
    """Count violations for a single file using the rule's detection type."""
    rule_type = str(rule_obj.get("type", ""))
    if rule_type == "ast-grep" and scan_file and scan_file.exists():
        return count_ast_grep_violations(scan_file, target, project_path)
    if rule_type == "custom":
        return 0
    return 0


def _resolve_fix_mechanism(
    rule_obj: dict[str, object],
    skill_dir: Path,
) -> tuple[str, Path | None]:
    fix_type = str(rule_obj.get("fix_type", "") or "").strip()

    if fix_type == "ast-grep":
        fix_file_rel = str(rule_obj.get("fix_file", "") or "")
        if not fix_file_rel:
            return "none", None
        return "ast-grep", (skill_dir / fix_file_rel).resolve()

    if fix_type == "custom":
        fix_script_rel = str(rule_obj.get("fix_script", "") or "")
        if not fix_script_rel:
            return "none", None
        return "custom", (skill_dir / fix_script_rel).resolve()

    if fix_type:
        return "none", None

    # Backwards compat: infer from keys when fix_type is absent
    fix_file_rel = str(rule_obj.get("fix_file", "") or "")
    if fix_file_rel:
        return "ast-grep", (skill_dir / fix_file_rel).resolve()

    return "none", None


def _parse_existing_imports(source: str) -> dict[str, set[str]]:
    """Parse all imports from source using AST.

    Returns a dict mapping module name to set of imported names.
    Bare ``import X`` is stored as ``{"X": set()}``.
    ``from X import a, b`` is stored as ``{"X": {"a", "b"}}``.
    """
    import ast as _ast

    result: dict[str, set[str]] = {}
    try:
        tree = _ast.parse(source)
    except SyntaxError:
        return result

    for node in _ast.walk(tree):
        if isinstance(node, _ast.Import):
            for alias in node.names:
                result.setdefault(alias.name, set())
        elif isinstance(node, _ast.ImportFrom):
            module = node.module or ""
            names = result.setdefault(module, set())
            for alias in node.names:
                names.add(alias.name)
    return result


def _import_already_present(imp: str, source: str, parsed: dict[str, set[str]]) -> bool:
    """Check if an import is already present using pre-parsed AST data."""
    import ast as _ast

    try:
        tree = _ast.parse(imp.strip())
    except SyntaxError:
        return False

    for node in _ast.walk(tree):
        if isinstance(node, _ast.Import):
            for alias in node.names:
                if alias.name in parsed:
                    return True
        elif isinstance(node, _ast.ImportFrom):
            module = node.module or ""
            existing_names = parsed.get(module, set())
            for alias in node.names:
                if alias.name in existing_names:
                    return True
    return False


def _find_last_import_line(source: str) -> int:
    """Return the 1-based line number of the last top-level import using AST.

    Returns 0 if no imports found (insert at top of file).
    """
    import ast as _ast

    try:
        tree = _ast.parse(source)
    except SyntaxError:
        return 0

    last_import_line = 0
    for node in tree.body:
        if isinstance(node, (_ast.Import, _ast.ImportFrom)):
            end = getattr(node, "end_lineno", node.lineno) or node.lineno
            last_import_line = max(last_import_line, end)
    return last_import_line


def ensure_imports(target: Path, import_lines: list[str]) -> bool:
    """Add missing import lines to *target* using full AST analysis.

    Uses ``ast.parse`` to detect existing imports and find the correct
    insertion point after the last top-level import statement.
    Handles multi-import lines, aliased imports, and multiline imports.

    Returns True if the file was modified.
    """
    if not import_lines:
        return False

    text = target.read_text(encoding="utf-8")

    parsed = _parse_existing_imports(text)
    missing = [
        imp for imp in import_lines if not _import_already_present(imp, text, parsed)
    ]
    if not missing:
        return False

    lines = text.splitlines(keepends=True)
    last_import_lineno = _find_last_import_line(text)
    insert_idx = last_import_lineno  # 1-based → 0-based index after that line

    block = "".join(imp.rstrip() + "\n" for imp in missing)
    lines.insert(insert_idx, block)
    target.write_text("".join(lines), encoding="utf-8")
    return True


def _apply_fix(
    mechanism: str,
    fix_file: Path | None,
    target: Path,
    project_path: Path,
) -> bool:
    """Apply a fix using the resolved mechanism. Returns True if changes were made."""
    if mechanism == "ast-grep" and fix_file and fix_file.exists():
        return apply_ast_grep_fix(fix_file, target, project_path)
    if mechanism == "custom" and fix_file and fix_file.exists():
        return apply_custom_fix(fix_file, target, project_path)
    return False


def run_project_tests(project_path: Path, timeout: int = 300) -> tuple[bool, str]:
    has_tests = (
        (project_path / "tests").is_dir()
        or (project_path / "test").is_dir()
        or bool(list(project_path.glob("test_*.py")))
    )
    if not has_tests:
        return False, "no tests found"

    if not (project_path / "pyproject.toml").exists():
        return False, "no pyproject.toml"

    result = run_cmd(
        [sys.executable, "-m", "pytest", "--tb=short", "-q", "--no-header", "-x"],
        cwd=project_path,
        timeout=timeout,
    )
    passed = result.returncode == 0
    output = (result.stdout or "") + (result.stderr or "")
    if len(output) > 2000:
        output = "...(truncated)...\n" + output[-2000:]
    return passed, output


def process_fix_rule(
    rule_obj: dict[str, object],
    skill_dir: Path,
    project_path: Path,
    project_name: str,
    tracked_files: list[str],
    include_globs: list[str],
    exclude_globs: list[str],
    dry_run: bool,
    tmpdir: Path,
) -> dict[str, object]:
    """Process one fix rule on one project. Returns fix report entry."""
    validate_flat_fix_keys(rule_obj)
    rule_id = str(rule_obj.get("id", "unknown"))
    fix_auto = bool(rule_obj.get("fix_auto"))
    fix_instruction = str(rule_obj.get("fix_instruction", "") or "")
    scan_file_rel = str(rule_obj.get("file", "") or "")

    entry: dict[str, object] = {
        "rule_id": rule_id,
        "project": project_name,
        "fix_auto": fix_auto,
        "candidates": 0,
        "accepted": [],
        "rejected": [],
        "rej_files": [],
        "manual_instructions": [],
    }

    if not fix_auto:
        candidates = find_candidate_files(
            rule_obj,
            skill_dir,
            project_path,
            tracked_files,
            include_globs,
            exclude_globs,
        )
        entry["candidates"] = len(candidates)
        if fix_instruction and candidates:
            entry["manual_instructions"] = [
                {"file": str(c), "instruction": fix_instruction} for c in candidates
            ]
        return entry

    mechanism, fix_target = _resolve_fix_mechanism(rule_obj, skill_dir)

    if mechanism == "none":
        entry["error"] = (
            "fix_auto=true but no fix mechanism — set fix_type "
            "(ast-grep + fix_file, custom + fix_script)"
        )
        eprint(f"  Warning: {entry['error']} for rule '{rule_id}'")
        return entry

    if mechanism == "ast-grep" and fix_target and not fix_target.exists():
        eprint(f"  Warning: fix_file not found: {fix_target}")
        entry["error"] = f"fix_file not found: {fix_target}"
        return entry

    if mechanism == "custom" and fix_target and not fix_target.exists():
        eprint(f"  Warning: fix_script not found: {fix_target}")
        entry["error"] = f"fix_script not found: {fix_target}"
        return entry

    scan_file = (skill_dir / scan_file_rel).resolve() if scan_file_rel else None

    candidates = find_candidate_files(
        rule_obj,
        skill_dir,
        project_path,
        tracked_files,
        include_globs,
        exclude_globs,
    )
    entry["candidates"] = len(candidates)

    if not candidates:
        return entry

    print(f"    [{rule_id}] {len(candidates)} candidates (mechanism={mechanism})")

    if dry_run:
        entry["dry_run"] = True
        entry["would_fix"] = [str(c) for c in candidates]
        return entry

    accepted: list[dict[str, object]] = []
    rejected: list[dict[str, object]] = []
    rej_files: list[str] = []

    for target in candidates:
        before_hash = sha256_file(target)

        before_violations = _count_violations_for_rule(
            rule_obj,
            scan_file,
            target,
            project_path,
        )

        backup_name = target.name + ".backup"
        backup_path = tmpdir / backup_name
        if backup_path.exists():
            backup_path = tmpdir / f"{before_hash[:12]}_{backup_name}"
        shutil.copy2(target, backup_path)

        fix_applied = _apply_fix(
            mechanism,
            fix_target,
            target,
            project_path,
        )

        if not fix_applied:
            shutil.copy2(backup_path, target)
            continue

        fix_imports_raw = rule_obj.get("fix_imports")
        if fix_imports_raw and isinstance(fix_imports_raw, list):
            ensure_imports(target, [str(i) for i in fix_imports_raw])

        after_hash = sha256_file(target)
        if after_hash == before_hash:
            continue

        syntax_ok, syntax_output = check_syntax(target)
        import_ok, import_output = check_import(target)

        after_violations = _count_violations_for_rule(
            rule_obj,
            scan_file,
            target,
            project_path,
        )

        diff_text = get_diff(backup_path, target)

        if not syntax_ok:
            rej_path = write_rej_file(
                target,
                "Syntax error after fix",
                rule_id,
                before_hash,
                after_hash,
                before_violations,
                after_violations,
                syntax_ok,
                syntax_output,
                diff_text,
            )
            shutil.copy2(backup_path, target)
            rejected.append({
                "file": str(target),
                "reason": "syntax_error",
                "before_violations": before_violations,
                "after_violations": after_violations,
                "rej_file": str(rej_path),
            })
            rej_files.append(str(rej_path))
            print(f"      REJECTED (syntax error): {target.name}")

        elif not import_ok:
            rej_path = write_rej_file(
                target,
                f"Import check failed: {import_output}",
                rule_id,
                before_hash,
                after_hash,
                before_violations,
                after_violations,
                True,
                import_output,
                diff_text,
            )
            shutil.copy2(backup_path, target)
            rejected.append({
                "file": str(target),
                "reason": "import_check_failed",
                "before_violations": before_violations,
                "after_violations": after_violations,
                "rej_file": str(rej_path),
            })
            rej_files.append(str(rej_path))
            print(f"      REJECTED (import check): {target.name} - {import_output}")

        elif after_violations >= before_violations:
            reason = (
                "violations_increased"
                if after_violations > before_violations
                else "violations_not_reduced"
            )
            rej_path = write_rej_file(
                target,
                f"Violations {reason}: {before_violations} -> {after_violations}",
                rule_id,
                before_hash,
                after_hash,
                before_violations,
                after_violations,
                syntax_ok,
                "",
                diff_text,
            )
            shutil.copy2(backup_path, target)
            rejected.append({
                "file": str(target),
                "reason": reason,
                "before_violations": before_violations,
                "after_violations": after_violations,
                "rej_file": str(rej_path),
            })
            rej_files.append(str(rej_path))
            print(
                f"      REJECTED ({reason}): {target.name} ({before_violations} -> {after_violations})"
            )

        else:
            accepted.append({
                "file": str(target),
                "before_hash": before_hash,
                "after_hash": after_hash,
                "before_violations": before_violations,
                "after_violations": after_violations,
                "delta": after_violations - before_violations,
            })
            print(
                f"      ACCEPTED: {target.name} ({before_violations} -> {after_violations})"
            )

    entry["accepted"] = accepted
    entry["rejected"] = rejected
    entry["rej_files"] = rej_files
    return entry


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------


def fix_skill(
    skill_name: str,
    root: Path,
    dry_run: bool,
    project_filter: str | None,
    rule_filters: list[str] | None = None,
    max_rejections: int | None = None,
) -> tuple[bool, dict[str, object]]:
    """Run fixes for a single skill. Returns (success, report)."""
    skill_dir = root / SKILLS_DIR / skill_name
    rules_path = skill_dir / "rules.yml"

    if not rules_path.exists():
        eprint(f"No rules.yml for skill '{skill_name}'")
        return False, {"error": f"No rules.yml for skill '{skill_name}'"}

    rules = load_rules_yml(rules_path)
    rules_list = rules.get("rules", [])
    if not isinstance(rules_list, list):
        eprint(f"rules must be a list in {rules_path}")
        return False, {"error": "rules must be a list"}

    scan_targets = rules.get("scan_targets", {})
    if not isinstance(scan_targets, dict):
        scan_targets = {}
    include_globs = scan_targets.get("include", ["**/*.py"])
    if not isinstance(include_globs, list):
        include_globs = ["**/*.py"]
    exclude_globs = scan_targets.get("exclude", [])
    if not isinstance(exclude_globs, list):
        exclude_globs = []

    project_lookup = all_project_paths(root)
    exclude_globs = normalize_exclude_globs(exclude_globs, set(project_lookup.keys()))
    if project_filter:
        if project_filter not in project_lookup:
            eprint(f"Unknown project: {project_filter}")
            return False, {"error": f"Unknown project: {project_filter}"}
        selected = [project_filter]
    else:
        projects_cfg = scan_targets.get("projects", [])
        if isinstance(projects_cfg, list) and projects_cfg:
            selected = [p for p in projects_cfg if p in project_lookup]
        else:
            selected = sorted(project_lookup.keys())

    # Identify rules with fix metadata (flat fix_* keys only)
    for r in rules_list:
        if isinstance(r, dict):
            validate_flat_fix_keys(r)
    fixable_rules = [
        r for r in rules_list if isinstance(r, dict) and r.get("fix_auto") is not None
    ]

    if rule_filters:
        allowed = {rf.strip() for rf in rule_filters if rf.strip()}
        fixable_rules = [
            r
            for r in fixable_rules
            if isinstance(r, dict) and str(r.get("id", "")).strip() in allowed
        ]

    if not fixable_rules:
        print(f"No rules with fix metadata in skill '{skill_name}'")
        return True, {"skill": skill_name, "message": "no fixable rules"}

    mode_label = "DRY-RUN" if dry_run else "APPLY"
    print(f"\n{'=' * 72}")
    print(f"Skill Fix: {skill_name} [{mode_label}]")
    print(f"Projects: {', '.join(selected)}")
    print(f"Fixable rules: {len(fixable_rules)}")
    print(f"{'=' * 72}")

    all_entries: list[dict[str, object]] = []
    total_accepted = 0
    total_rejected = 0
    total_manual = 0

    with tempfile.TemporaryDirectory(prefix="skill_fix_") as tmpdir:
        tmpdir_path = Path(tmpdir)

        for project_name in selected:
            project_path = project_lookup[project_name].resolve()
            tracked = get_tracked_files(project_path)

            print(f"\n  Project: {project_name} ({len(tracked)} tracked files)")

            project_snapshots: dict[str, Path] = {}
            if not dry_run:
                for tracked_file in tracked:
                    tracked_path = project_path / tracked_file
                    if tracked_path.suffix != ".py" or not tracked_path.exists():
                        continue
                    rel_hash = hashlib.sha256(tracked_file.encode("utf-8")).hexdigest()[
                        :12
                    ]
                    snap_name = f"snap_{project_name}_{rel_hash}_{tracked_path.name}"
                    snap_path = tmpdir_path / snap_name
                    shutil.copy2(tracked_path, snap_path)
                    project_snapshots[str(tracked_path)] = snap_path

            project_entries: list[dict[str, object]] = []

            for rule_obj in fixable_rules:
                if not isinstance(rule_obj, dict):
                    continue
                entry = process_fix_rule(
                    rule_obj=rule_obj,
                    skill_dir=skill_dir,
                    project_path=project_path,
                    project_name=project_name,
                    tracked_files=tracked,
                    include_globs=include_globs,
                    exclude_globs=exclude_globs,
                    dry_run=dry_run,
                    tmpdir=tmpdir_path,
                )
                project_entries.append(entry)
                all_entries.append(entry)

                acc = entry.get("accepted", [])
                rej = entry.get("rejected", [])
                man = entry.get("manual_instructions", [])
                if isinstance(acc, list):
                    total_accepted += len(acc)
                if isinstance(rej, list):
                    total_rejected += len(rej)
                if isinstance(man, list):
                    total_manual += len(man)

                if (
                    max_rejections is not None
                    and max_rejections >= 0
                    and total_rejected > max_rejections
                ):
                    entry["error"] = (
                        f"max_rejections exceeded ({total_rejected} > {max_rejections})"
                    )
                    report_path = root / FIX_REPORT_DEFAULT.format(skill=skill_name)
                    report: dict[str, object] = {
                        "skill": skill_name,
                        "mode": "dry-run" if dry_run else "apply",
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                        "projects_scanned": selected,
                        "entries": all_entries,
                        "summary": {
                            "total_accepted": total_accepted,
                            "total_rejected": total_rejected,
                            "total_manual": total_manual,
                        },
                        "error": entry["error"],
                    }
                    write_json(report_path, report)
                    eprint(f"Aborting: {entry['error']}")
                    return False, report

            project_accepted = 0
            for entry in project_entries:
                accepted_obj = entry.get("accepted", [])
                if isinstance(accepted_obj, list):
                    project_accepted += len(accepted_obj)
            if not dry_run and project_accepted > 0:
                print(f"\n    Running project tests for {project_name}...")
                test_ok, test_output = run_project_tests(project_path)
                if not test_ok:
                    print(f"    TESTS FAILED - restoring all files in {project_name}")
                    if test_output:
                        print(f"    Test output (tail):\n{test_output[-500:]}")
                    restored_count = 0
                    for original_path_str, snap_path in project_snapshots.items():
                        original_path = Path(original_path_str)
                        if original_path.exists() and snap_path.exists():
                            shutil.copy2(snap_path, original_path)
                            restored_count += 1
                    print(f"    Restored {restored_count} files from snapshot")

                    for entry in project_entries:
                        accepted_list = entry.get("accepted", [])
                        if not isinstance(accepted_list, list) or not accepted_list:
                            continue
                        moved_count = len(accepted_list)
                        entry["restored"] = True
                        entry["restore_reason"] = "project_tests_failed"
                        for accepted_item in accepted_list:
                            if isinstance(accepted_item, dict):
                                accepted_item["reason"] = "project_tests_failed"
                        rejected_list = entry.get("rejected")
                        if isinstance(rejected_list, list):
                            rejected_list.extend(accepted_list)
                        else:
                            entry["rejected"] = list(accepted_list)
                        entry["accepted"] = []
                        total_rejected += moved_count
                        total_accepted -= moved_count
                else:
                    print(f"    TEST PASS for {project_name}")

    # Write fix report
    report_path = root / FIX_REPORT_DEFAULT.format(skill=skill_name)
    report: dict[str, object] = {
        "skill": skill_name,
        "mode": "dry-run" if dry_run else "apply",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "projects_scanned": selected,
        "entries": all_entries,
        "summary": {
            "total_accepted": total_accepted,
            "total_rejected": total_rejected,
            "total_manual": total_manual,
        },
    }
    write_json(report_path, report)

    print(f"\n  Fix report: {report_path}")
    print(f"  Accepted: {total_accepted}")
    print(f"  Rejected: {total_rejected}")
    print(f"  Manual: {total_manual}")

    # Print manual instructions
    if total_manual > 0:
        print("\n  Manual fix instructions:")
        for entry in all_entries:
            manual = entry.get("manual_instructions", [])
            if not isinstance(manual, list) or not manual:
                continue
            rule_id = entry.get("rule_id", "unknown")
            print(f"    Rule: {rule_id}")
            for item in manual[:5]:  # Show first 5
                if isinstance(item, dict):
                    print(f"      {item.get('file', '?')}")
                    print(f"        -> {item.get('instruction', '?')}")
            remaining = len(manual) - 5
            if remaining > 0:
                print(f"      ... and {remaining} more files")

    return True, report


def discover_skills(skills_dir: Path) -> list[str]:
    if not skills_dir.exists():
        return []
    return sorted(
        child.name
        for child in skills_dir.iterdir()
        if child.is_dir() and (child / "rules.yml").exists()
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generic data-driven skill fixer")
    skill_group = parser.add_mutually_exclusive_group(required=True)
    _ = skill_group.add_argument("--skill", help="Fix one skill by folder name")
    _ = skill_group.add_argument("--all", action="store_true", help="Fix all skills")
    _ = parser.add_argument("--project", help="Limit to one project")
    _ = parser.add_argument(
        "--rule",
        action="append",
        default=[],
        help="Limit to specific rule id (repeatable)",
    )
    _ = parser.add_argument(
        "--max-rejections",
        type=int,
        default=-1,
        help="Abort when total rejected files exceeds this value (-1 disables)",
    )
    mode_group = parser.add_mutually_exclusive_group(required=True)
    _ = mode_group.add_argument(
        "--dry-run", action="store_true", help="Show what would be fixed"
    )
    _ = mode_group.add_argument("--apply", action="store_true", help="Apply fixes")
    _ = parser.add_argument("--root", default=".", help="Workspace root")
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args(sys.argv[1:])
    root = Path(args.root).resolve()

    if args.all:
        skills_dir = root / SKILLS_DIR
        skill_names = discover_skills(skills_dir)
        if not skill_names:
            print("No skills with rules.yml found")
            raise SystemExit(EXIT_OK)
        any_failure = False
        for name in skill_names:
            success, _ = fix_skill(
                skill_name=name,
                root=root,
                dry_run=args.dry_run,
                project_filter=args.project,
                rule_filters=list(args.rule or []),
                max_rejections=args.max_rejections,
            )
            if not success:
                any_failure = True
        raise SystemExit(EXIT_FAIL if any_failure else EXIT_OK)

    success, _ = fix_skill(
        skill_name=args.skill,
        root=root,
        dry_run=args.dry_run,
        project_filter=args.project,
        rule_filters=list(args.rule or []),
        max_rejections=args.max_rejections,
    )
    raise SystemExit(EXIT_OK if success else EXIT_FAIL)


if __name__ == "__main__":
    main()
