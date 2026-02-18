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
import re
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


def validate_flat_fix_keys(rule: dict[str, object]) -> None:
    """Reject nested fix: sub-dict — only flat fix_* keys are allowed."""
    if isinstance(rule.get("fix"), dict):
        rule_id = str(rule.get("id", "unknown"))
        msg = (
            f"Rule '{rule_id}' uses nested 'fix:' sub-dict. "
            "Use flat keys: fix_auto, fix_type, fix_instruction, "
            "fix_file, fix_description."
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
    """Run python -m py_compile for syntax errors. Returns (ok, output)."""
    result = run_cmd(
        [sys.executable, "-m", "py_compile", str(filepath)],
        cwd=filepath.parent,
        timeout=30,
    )
    return result.returncode == 0, (result.stdout or "") + (result.stderr or "")


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


def count_ripgrep_violations(
    pattern: str,
    target_file: Path,
    project_root: Path,
) -> int:
    """Count ripgrep violations in a single file."""
    result = run_cmd(
        ["rg", "-c", pattern, str(target_file)],
        cwd=project_root,
        timeout=30,
    )
    if result.returncode == 127:
        eprint("Warning: ripgrep (rg) not found")
        return 0
    try:
        return int((result.stdout or "").strip().split(":")[-1])
    except (ValueError, IndexError):
        return 0


def _parse_re_flags(flags_raw: object) -> int:
    if not isinstance(flags_raw, list):
        return 0
    flags = 0
    flag_map = {
        "MULTILINE": re.MULTILINE,
        "DOTALL": re.DOTALL,
        "IGNORECASE": re.IGNORECASE,
        "VERBOSE": re.VERBOSE,
    }
    for item in flags_raw:
        name = str(item).upper()
        if name in flag_map:
            flags |= flag_map[name]
    return flags


def count_regex_violations(
    pattern: str,
    flags_raw: object,
    target_file: Path,
) -> int:
    re_flags = _parse_re_flags(flags_raw)
    try:
        compiled = re.compile(pattern, re_flags)
    except re.error:
        return 0
    try:
        content = target_file.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0
    return len(compiled.findall(content))


def apply_regex_fix(
    target_file: Path,
    fix_pattern: str,
    fix_replacement: str,
    flags_raw: object,
) -> bool:
    """Apply regex substitution to a file. Returns True if content changed."""
    re_flags = _parse_re_flags(flags_raw)
    try:
        compiled = re.compile(fix_pattern, re_flags)
    except re.error:
        return False
    try:
        content = target_file.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    new_content = compiled.sub(fix_replacement, content)
    if new_content == content:
        return False
    target_file.write_text(new_content, encoding="utf-8")
    return True


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


# ---------------------------------------------------------------------------
# Core fix logic per rule
# ---------------------------------------------------------------------------


def find_candidate_files(
    rule_obj: dict[str, object],
    skill_dir: Path,
    project_path: Path,
    tracked_files: list[str],
    include_globs: list[str],
) -> list[Path]:
    """Find files that have violations for a given rule."""
    import fnmatch

    rule_type = str(rule_obj.get("type", ""))
    candidates: list[Path] = []

    # Filter tracked files by include globs
    includes = include_globs or ["**/*.py"]
    filtered = [
        f for f in tracked_files if any(fnmatch.fnmatch(f, pat) for pat in includes)
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

    elif rule_type == "ripgrep":
        pattern = str(rule_obj.get("pattern", ""))
        if not pattern:
            return []
        match_mode = str(rule_obj.get("match", "present")).strip() or "present"
        for rel in filtered:
            full = project_path / rel
            if not full.exists() or not full.is_file():
                continue
            count = count_ripgrep_violations(pattern, full, project_path)
            if match_mode == "absent":
                if count == 0:
                    candidates.append(full)
            elif count > 0:
                candidates.append(full)

    elif rule_type == "regex":
        pattern = str(rule_obj.get("pattern", ""))
        if not pattern:
            return []
        flags_raw = rule_obj.get("flags", [])
        match_mode = str(rule_obj.get("match", "present")).strip() or "present"
        for rel in filtered:
            full = project_path / rel
            if not full.exists() or not full.is_file():
                continue
            count = count_regex_violations(pattern, flags_raw, full)
            if match_mode == "absent":
                if count == 0:
                    candidates.append(full)
            elif count > 0:
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
    if rule_type == "ripgrep":
        pattern = str(rule_obj.get("pattern", ""))
        return count_ripgrep_violations(pattern, target, project_path) if pattern else 0
    if rule_type == "regex":
        pattern = str(rule_obj.get("pattern", ""))
        return (
            count_regex_violations(pattern, rule_obj.get("flags", []), target)
            if pattern
            else 0
        )
    return 0


def _resolve_fix_mechanism(
    rule_obj: dict[str, object],
    skill_dir: Path,
) -> tuple[str, Path | None, str, str, object]:
    """Determine fix mechanism from explicit ``fix_type`` key.

    Returns (mechanism, fix_target, fix_pattern, fix_replacement, flags_raw).
    mechanism is one of: "ast-grep", "regex", "custom", "none".
    ``fix_type`` is independent of the detection ``type`` — a ripgrep
    detection rule can use an ast-grep fix, a regex fix, or a custom fix.
    """
    fix_type = str(rule_obj.get("fix_type", "") or "").strip()
    flags_raw = rule_obj.get("flags", [])

    if fix_type == "ast-grep":
        fix_file_rel = str(rule_obj.get("fix_file", "") or "")
        if not fix_file_rel:
            return "none", None, "", "", flags_raw
        return "ast-grep", (skill_dir / fix_file_rel).resolve(), "", "", flags_raw

    if fix_type == "regex":
        fix_pattern = str(rule_obj.get("fix_pattern", "") or "")
        fix_replacement = rule_obj.get("fix_replacement")
        if not fix_pattern or fix_replacement is None:
            return "none", None, "", "", flags_raw
        return "regex", None, fix_pattern, str(fix_replacement), flags_raw

    if fix_type == "custom":
        fix_script_rel = str(rule_obj.get("fix_script", "") or "")
        if not fix_script_rel:
            return "none", None, "", "", flags_raw
        return "custom", (skill_dir / fix_script_rel).resolve(), "", "", flags_raw

    if fix_type:
        return "none", None, "", "", flags_raw

    # Backwards compat: infer from keys when fix_type is absent
    fix_file_rel = str(rule_obj.get("fix_file", "") or "")
    if fix_file_rel:
        return "ast-grep", (skill_dir / fix_file_rel).resolve(), "", "", flags_raw

    return "none", None, "", "", flags_raw


def _apply_fix(
    mechanism: str,
    fix_file: Path | None,
    fix_pattern: str,
    fix_replacement: str,
    flags_raw: object,
    target: Path,
    project_path: Path,
) -> bool:
    """Apply a fix using the resolved mechanism. Returns True if changes were made."""
    if mechanism == "ast-grep" and fix_file and fix_file.exists():
        return apply_ast_grep_fix(fix_file, target, project_path)
    if mechanism == "regex" and fix_pattern:
        return apply_regex_fix(target, fix_pattern, fix_replacement, flags_raw)
    if mechanism == "custom" and fix_file and fix_file.exists():
        return apply_custom_fix(fix_file, target, project_path)
    return False


def process_fix_rule(
    rule_obj: dict[str, object],
    skill_dir: Path,
    project_path: Path,
    project_name: str,
    tracked_files: list[str],
    include_globs: list[str],
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
        )
        entry["candidates"] = len(candidates)
        if fix_instruction and candidates:
            entry["manual_instructions"] = [
                {"file": str(c), "instruction": fix_instruction} for c in candidates
            ]
        return entry

    mechanism, fix_target, fix_pattern, fix_replacement, flags_raw = (
        _resolve_fix_mechanism(rule_obj, skill_dir)
    )

    if mechanism == "none":
        entry["error"] = (
            "fix_auto=true but no fix mechanism — set fix_type "
            "(ast-grep + fix_file, regex + fix_pattern/fix_replacement, "
            "custom + fix_script)"
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
            fix_pattern,
            fix_replacement,
            flags_raw,
            target,
            project_path,
        )

        if not fix_applied:
            shutil.copy2(backup_path, target)
            continue

        after_hash = sha256_file(target)
        if after_hash == before_hash:
            continue

        syntax_ok, syntax_output = check_syntax(target)

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

    # Resolve projects
    project_lookup = all_project_paths(root)
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
                    dry_run=dry_run,
                    tmpdir=tmpdir_path,
                )
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
            )
            if not success:
                any_failure = True
        raise SystemExit(EXIT_FAIL if any_failure else EXIT_OK)

    success, _ = fix_skill(
        skill_name=args.skill,
        root=root,
        dry_run=args.dry_run,
        project_filter=args.project,
    )
    raise SystemExit(EXIT_OK if success else EXIT_FAIL)


if __name__ == "__main__":
    main()
