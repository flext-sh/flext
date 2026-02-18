#!/usr/bin/env python3
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
"""Generate scripts inventory, wiring map, and external script candidates."""

from __future__ import annotations

import argparse
import json
import operator
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from artifact_naming import artifact_path

OWNER_MARKER_RE = re.compile(
    r"^# Owner-Skill:\s+\.claude/skills/([a-z0-9][-a-z0-9]*)/SKILL\.md\s*$",
)
SCRIPT_PATH_RE = re.compile(r"scripts/[A-Za-z0-9_./-]+\.(?:py|sh)")
TARGET_RE = re.compile(r"^([A-Za-z0-9_.-]+)\s*:(?![=])")
ROOT_SCRIPT_STEM_PREFIXES = (
    "convert_",
    "refactor_",
    "standardize_",
    "restructure_",
    "consolidate_",
    "merge_",
    "create_",
)


@dataclass(frozen=True)
class ScriptMeta:
    path: str
    extension: str
    tracked: bool
    item_type: str
    classification: str
    owner_skill: str | None
    has_main_function: bool
    has_argparse: bool
    has_interactive_prompts: bool
    has_artifact_output: bool
    line_count: int
    code_line_count: int
    accepts_mode_flag: bool
    accepts_root_flag: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate scripts inventory and wiring JSON artifacts under .sisyphus/reports/."
        ),
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root path (default: .)",
    )
    return parser.parse_args()


def run_git(root: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def tracked_script_candidates(root: Path) -> set[str]:
    output = run_git(
        root,
        [
            "ls-files",
            "scripts/*.sh",
            "scripts/*.py",
            "scripts/**/*.sh",
            "scripts/**/*.py",
        ],
    )
    return {line.strip() for line in output.splitlines() if line.strip()}


def untracked_script_candidates(root: Path) -> set[str]:
    output = run_git(
        root,
        [
            "ls-files",
            "--others",
            "--exclude-standard",
            "--",
            "scripts",
        ],
    )
    paths: set[str] = set()
    for line in output.splitlines():
        candidate = line.strip()
        if not candidate:
            continue
        if candidate.endswith((".py", ".sh")):
            paths.add(candidate)
    return paths


def count_code_lines(content: str, extension: str) -> int:
    count = 0
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if extension == ".py" and line.startswith("#"):
            continue
        if extension == ".sh" and line.startswith("#") and not line.startswith("#!"):
            continue
        count += 1
    return count


def owner_skill_from_header(content: str) -> str | None:
    for line in content.splitlines()[:10]:
        match = OWNER_MARKER_RE.match(line.rstrip("\n"))
        if match:
            return match.group(1)
    return None


def invokes_other_scripts(content: str) -> bool:
    if "run_step(" in content or "run_step_allow_fail(" in content:
        return True
    return bool(SCRIPT_PATH_RE.search(content))


def classify_script(path: str, content: str, code_line_count: int) -> tuple[str, str]:
    file_name = Path(path).name
    parent = Path(path).parent.as_posix()

    if file_name == "__init__.py":
        return "module", "module"

    if code_line_count < 20:
        return "script", "stub"

    if path.startswith("scripts/lib/"):
        return "script", "library"

    if path.startswith("scripts/core/"):
        if file_name.startswith("check_"):
            return "script", "validator"
        return "script", "library"

    if file_name.startswith("_"):
        return "script", "one_shot"

    if parent == "scripts" and file_name.startswith(ROOT_SCRIPT_STEM_PREFIXES):
        return "script", "one_shot"

    if file_name.startswith(("enforce_", "check_", "validate_", "test_")):
        return "script", "validator"

    if file_name.startswith(("fix_", "autofix")):
        return "script", "fixer"

    if any(flag in content for flag in ("--apply", "--fix", "--dry-run")):
        return "script", "fixer"

    if file_name.startswith("run_") and invokes_other_scripts(content):
        return "script", "orchestrator"

    if invokes_other_scripts(content) and path.endswith(".sh"):
        return "script", "orchestrator"

    return "script", "unknown"


def build_inventory(root: Path) -> dict[str, Any]:
    tracked = tracked_script_candidates(root)
    untracked = untracked_script_candidates(root)
    all_paths = sorted(tracked | untracked)

    metas: list[ScriptMeta] = []
    for rel_path in all_paths:
        full_path = root / rel_path
        if not full_path.exists() or not full_path.is_file():
            continue
        extension = full_path.suffix
        if extension not in {".py", ".sh"}:
            continue
        content = full_path.read_text(encoding="utf-8", errors="replace")
        line_count = len(content.splitlines())
        code_line_count = count_code_lines(content, extension)
        item_type, classification = classify_script(rel_path, content, code_line_count)

        has_main = (
            bool(re.search(r"^\s*def\s+main\s*\(", content, flags=re.MULTILINE))
            if extension == ".py"
            else False
        )
        has_argparse = (
            bool(
                re.search(
                    r"^\s*(import\s+argparse|from\s+argparse\s+import\s+)",
                    content,
                    flags=re.MULTILINE,
                ),
            )
            if extension == ".py"
            else False
        )
        has_interactive = bool(
            re.search(
                r"\binput\s*\(|\bread\s+-p\b|\bselect\s+|\bdialog\b|\bwhiptail\b",
                content,
            ),
        )

        metas.append(
            ScriptMeta(
                path=rel_path,
                extension=extension,
                tracked=rel_path in tracked,
                item_type=item_type,
                classification=classification,
                owner_skill=owner_skill_from_header(content),
                has_main_function=has_main,
                has_argparse=has_argparse,
                has_interactive_prompts=has_interactive,
                has_artifact_output=".sisyphus/" in content,
                line_count=line_count,
                code_line_count=code_line_count,
                accepts_mode_flag="--mode" in content,
                accepts_root_flag="--root" in content,
            ),
        )

    by_classification = Counter(
        item.classification for item in metas if item.item_type == "script"
    )
    by_extension = Counter(item.extension for item in metas)

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "repo_root": str(root.resolve()),
        "total_scripts": sum(1 for item in metas if item.item_type == "script"),
        "by_classification": dict(sorted(by_classification.items())),
        "by_extension": dict(sorted(by_extension.items())),
        "scripts": [
            {
                "path": item.path,
                "extension": item.extension,
                "classification": item.classification,
                "type": item.item_type,
                "tracked": item.tracked,
                "owner_skill": item.owner_skill,
                "has_main_function": item.has_main_function,
                "has_argparse": item.has_argparse,
                "has_interactive_prompts": item.has_interactive_prompts,
                "has_artifact_output": item.has_artifact_output,
                "line_count": item.line_count,
                "code_line_count": item.code_line_count,
                "accepts_mode_flag": item.accepts_mode_flag,
                "accepts_root_flag": item.accepts_root_flag,
            }
            for item in sorted(metas, key=lambda entry: entry.path)
        ],
    }


def extract_script_paths(text: str) -> list[str]:
    return sorted({match.group(0) for match in SCRIPT_PATH_RE.finditer(text)})


def parse_makefile_wiring(
    root: Path, inventory_scripts: set[str]
) -> list[dict[str, Any]]:
    makefile = root / "Makefile"
    lines = makefile.read_text(encoding="utf-8", errors="replace").splitlines()
    current_target: str | None = None
    entries: list[dict[str, Any]] = []

    for line in lines:
        target_match = TARGET_RE.match(line)
        if target_match:
            current_target = target_match.group(1)
            continue
        if not current_target:
            continue
        if not line.startswith(("\t", " ")):
            continue
        scripts = extract_script_paths(line)
        entries.extend(
            {
                "target": current_target,
                "script": script,
                "blocking": "|| true" not in line,
            }
            for script in scripts
            if script in inventory_scripts
        )
    return sorted(entries, key=operator.itemgetter("target", "script"))


def parse_orchestrator_wiring(
    root: Path, inventory_scripts: set[str]
) -> list[dict[str, Any]]:
    orchestrator_path = root / "scripts/validation/run_automated_validation.sh"
    content = orchestrator_path.read_text(encoding="utf-8", errors="replace")
    pattern = re.compile(
        r"run_step(_allow_fail)?\s+\"([^\"]+)\"\s+\"([^\"]+)\"",
    )
    entries: list[dict[str, Any]] = []
    for match in pattern.finditer(content):
        allow_fail = bool(match.group(1))
        step_name = match.group(2)
        cmd = match.group(3)
        entries.extend(
            {
                "step": step_name,
                "script": script,
                "allow_fail": allow_fail,
            }
            for script in extract_script_paths(cmd)
            if script in inventory_scripts
        )
    return sorted(entries, key=operator.itemgetter("step", "script"))


def parse_legacy_makefile_wiring(
    root: Path,
    inventory_scripts: set[str],
) -> list[dict[str, object]]:
    legacy_path = root / "scripts/core/Makefile.scripts"
    content = legacy_path.read_text(encoding="utf-8", errors="replace").splitlines()
    stem_to_paths: dict[str, list[str]] = defaultdict(list)
    for script in inventory_scripts:
        if script.endswith(".py"):
            stem_to_paths[Path(script).stem].append(script)

    current_target: str | None = None
    entries: list[dict[str, Any]] = []
    invoke_re = re.compile(r"script_runner\.py\s+([A-Za-z0-9_-]+)")

    for line in content:
        target_match = TARGET_RE.match(line)
        if target_match:
            current_target = target_match.group(1)
            continue
        if not current_target:
            continue
        if "script_runner.py" not in line:
            continue

        match = invoke_re.search(line)
        if not match:
            continue
        script_key = match.group(1)
        candidates = stem_to_paths.get(script_key) or stem_to_paths.get(
            script_key.replace("-", "_"),
        )
        if candidates:
            script_path = min(candidates)
            entries.append(
                {
                    "target": current_target,
                    "script": script_path,
                    "included_by_root": False,
                },
            )
    return sorted(entries, key=operator.itemgetter("target", "script"))


def module_to_script_path(module_name: str) -> str:
    return f"scripts/{module_name.replace('.', '/')}.py"


def parse_inter_script_deps(
    root: Path,
    inventory_scripts: set[str],
) -> list[dict[str, str]]:
    deps: set[tuple[str, str, str]] = set()
    source_re = re.compile(
        r"(?:^|\s)(?:source|\.)\s+[\"']?((?:\./)?scripts/[A-Za-z0-9_./-]+\.(?:sh|py))",
        flags=re.MULTILINE,
    )
    py_from_re = re.compile(
        r"^\s*from\s+scripts\.([A-Za-z0-9_.]+)\s+import\s+", re.MULTILINE
    )
    py_import_re = re.compile(r"^\s*import\s+scripts\.([A-Za-z0-9_.]+)", re.MULTILINE)

    for script in sorted(inventory_scripts):
        content = (root / script).read_text(encoding="utf-8", errors="replace")
        if script.endswith(".sh"):
            for match in source_re.finditer(content):
                dep_path = match.group(1).lstrip("./")
                if dep_path in inventory_scripts and dep_path != script:
                    deps.add((script, dep_path, "source"))
            for dep_path in extract_script_paths(content):
                if dep_path in inventory_scripts and dep_path != script:
                    deps.add((script, dep_path, "invocation"))
        if script.endswith(".py"):
            for match in py_from_re.finditer(content):
                dep_path = module_to_script_path(match.group(1))
                if dep_path in inventory_scripts and dep_path != script:
                    deps.add((script, dep_path, "python_import"))
            for match in py_import_re.finditer(content):
                dep_path = module_to_script_path(match.group(1))
                if dep_path in inventory_scripts and dep_path != script:
                    deps.add((script, dep_path, "python_import"))

    return [
        {"source": source, "depends_on": depends_on, "type": dep_type}
        for source, depends_on, dep_type in sorted(deps)
    ]


def build_wiring(root: Path, inventory: dict[str, Any]) -> dict[str, Any]:
    inventory_items = inventory.get("scripts", [])
    if not isinstance(inventory_items, list):
        msg = "inventory payload is missing scripts list"
        raise RuntimeError(msg)

    script_entries = [
        item
        for item in inventory_items
        if isinstance(item, dict) and item.get("type") == "script"
    ]
    inventory_scripts = {str(item["path"]) for item in script_entries}

    root_makefile = parse_makefile_wiring(root, inventory_scripts)
    orchestrator = parse_orchestrator_wiring(root, inventory_scripts)
    legacy_makefile = parse_legacy_makefile_wiring(root, inventory_scripts)
    inter_script = parse_inter_script_deps(root, inventory_scripts)

    wired_scripts: set[str] = (
        {str(item["script"]) for item in root_makefile}
        | {str(item["script"]) for item in orchestrator}
        | {str(item["script"]) for item in legacy_makefile}
        | {str(item["depends_on"]) for item in inter_script}
    )

    unwired_scripts = sorted(inventory_scripts - wired_scripts)

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "wiring_sources": {
            "root_makefile": root_makefile,
            "orchestrator": orchestrator,
            "legacy_makefile_scripts": legacy_makefile,
            "inter_script_deps": inter_script,
        },
        "wired_scripts": sorted(wired_scripts),
        "unwired_scripts": unwired_scripts,
    }


def parse_submodule_paths(root: Path) -> list[str]:
    gitmodules = root / ".gitmodules"
    if not gitmodules.exists():
        return []
    submodule_paths: list[str] = []
    for line in gitmodules.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped.startswith("path = "):
            submodule_paths.append(stripped.split("=", 1)[1].strip().strip("/"))
    return submodule_paths


def should_exclude_external(path: str, submodules: list[str]) -> bool:
    if path.startswith("scripts/"):
        return True
    if path.startswith((".git/", "node_modules/", ".venv/")):
        return True
    return any(path == prefix or path.startswith(f"{prefix}/") for prefix in submodules)


def find_references(root: Path, target: str) -> list[str]:
    result = subprocess.run(
        ["git", "grep", "-l", "-F", target, "--", "."],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode not in {0, 1}:
        raise RuntimeError(result.stderr.strip() or "git grep failed")
    refs = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return sorted(ref for ref in refs if ref != target)


def guess_external_category(path: str) -> tuple[str, str, str]:
    if path.startswith("docker/images/scripts/"):
        return (
            "image_bootstrap",
            "keep_in_place",
            "Docker image entrypoint/bootstrap script",
        )
    if any(token in path for token in ("deploy", "release", "k8s", "helm")):
        return (
            "deployment",
            "keep_in_place",
            "Deployment helper outside root scripts/",
        )
    if any(token in path for token in ("build", "compile", "package")):
        return ("build_helper", "keep_in_place", "Build helper script")
    if any(token in path for token in ("validate", "check", "lint", "gate")):
        return (
            "automation_gate",
            "move_to_scripts",
            "Validation-like script outside root scripts/",
        )
    return ("unknown", "move_to_scripts", "No strong category match")


def parse_makefiles_with_parent_scripts(
    root: Path, submodules: list[str]
) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    for makefile in sorted(root.rglob("Makefile*")):
        if not makefile.is_file():
            continue
        rel = makefile.relative_to(root).as_posix()
        if rel == "Makefile":
            continue
        if should_exclude_external(rel, submodules):
            continue
        content = makefile.read_text(encoding="utf-8", errors="replace")
        if "../scripts/" not in content:
            continue
        matches = sorted(set(re.findall(r"\.\./scripts/[A-Za-z0-9_./-]+", content)))
        refs.append({"makefile": rel, "references": matches})
    return refs


def build_external_candidates(root: Path) -> dict[str, Any]:
    submodules = parse_submodule_paths(root)
    tracked_shell = {
        line.strip()
        for line in run_git(root, ["ls-files", "*.sh", "**/*.sh"]).splitlines()
        if line.strip()
    }
    untracked_shell = {
        line.strip()
        for line in run_git(
            root,
            ["ls-files", "--others", "--exclude-standard", "--", "."],
        ).splitlines()
        if line.strip().endswith(".sh")
    }
    all_shell = sorted(tracked_shell | untracked_shell)

    candidates: list[dict[str, Any]] = []
    for path in all_shell:
        if should_exclude_external(path, submodules):
            continue
        category, recommendation, notes = guess_external_category(path)
        candidates.append(
            {
                "path": path,
                "guessed_category": category,
                "referenced_by": find_references(root, path),
                "recommended_action": recommendation,
                "notes": notes,
            },
        )

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "candidates": sorted(candidates, key=lambda item: str(item["path"])),
        "makefiles_referencing_root_scripts": parse_makefiles_with_parent_scripts(
            root,
            submodules,
        ),
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        print(f"error: invalid --root path: {args.root}", file=sys.stderr)
        return 1

    try:
        inventory = build_inventory(root)
        wiring = build_wiring(root, inventory)
        external = build_external_candidates(root)

        inventory_path = root / artifact_path(
            "reports", "scripts-infra", "json", "scripts-inventory"
        )
        wiring_path = root / artifact_path(
            "reports", "scripts-infra", "json", "scripts-wiring"
        )
        external_path = root / artifact_path(
            "reports",
            "scripts-infra",
            "json",
            "external-scripts-candidates",
        )

        write_json(inventory_path, inventory)
        write_json(wiring_path, wiring)
        write_json(external_path, external)

        print(f"Wrote: {inventory_path.relative_to(root)}")
        print(f"Wrote: {wiring_path.relative_to(root)}")
        print(f"Wrote: {external_path.relative_to(root)}")
        return 0
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
