#!/usr/bin/env python3
"""Merge open Dependabot PRs across the FLEXT workspace with a standard commit schema.

Schema (single, non-repeating, conventional):
    chore(deps): bump <package> <old> → <new> [<ecosystem>]

Examples:
    chore(deps): bump actions/setup-python 6.2.0 → 6.3.0 [github_actions]
    chore(deps): bump msgpack 1.1.2 → 1.2.1 [pip]

Usage:
    python scripts/workspace/dependabot_merge.py --base main
    DRY_RUN=1 python scripts/workspace/dependabot_merge.py --base main

"""

from __future__ import annotations

import argparse
import configparser
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

DEPENDABOT_AUTHOR = "dependabot[bot]"
DEPENDABOT_TITLE_RE = re.compile(
    r"bump\s+(?P<package>.+?)\s+from\s+(?P<old>\S+)\s+to\s+(?P<new>\S+)\s*$",
    re.IGNORECASE,
)
MAX_WORKERS = 4


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a subprocess command (stdin=/dev/null to avoid interactive prompts)."""
    return subprocess.run(
        cmd,
        check=check,
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
    )


def discover_repos(root: Path) -> list[str]:
    """Read declared submodule paths from .gitmodules."""
    gitmodules = root / ".gitmodules"
    if not gitmodules.is_file():
        return []
    config = configparser.ConfigParser()
    config.read(gitmodules)
    paths: list[str] = []
    for section in config.sections():
        if section.startswith("submodule"):
            path = config.get(section, "path", fallback=None)
            if path:
                paths.append(path)
    return paths


def repo_slug_from_origin(path: Path) -> str | None:
    """Resolve owner/repo from a submodule's origin remote URL."""
    result = run(["git", "-C", str(path), "remote", "get-url", "origin"], check=False)
    if result.returncode != 0:
        return None
    url = result.stdout.strip()
    if url.startswith("git@github.com:"):
        return url.replace("git@github.com:", "").replace(".git", "")
    if "github.com/" in url:
        return url.split("github.com/", 1)[1].replace(".git", "")
    return None


def list_dependabot_prs(slug: str, base: str) -> list[dict[str, object]]:
    """List open Dependabot PRs targeting the given base branch."""
    result = run(
        [
            "gh",
            "pr",
            "list",
            "-R",
            slug,
            "--state",
            "open",
            "--author",
            DEPENDABOT_AUTHOR,
            "--base",
            base,
            "--json",
            "number,title,headRefName,url",
            "--limit",
            "100",
        ],
        check=False,
    )
    if result.returncode != 0:
        print(f"  WARN: cannot list PRs for {slug}: {result.stderr.strip()}", file=sys.stderr)
        return []
    try:
        return json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        return []


def ecosystem_from_head_ref(head_ref: str) -> str:
    """Map dependabot head ref prefix to a short ecosystem label."""
    if head_ref.startswith("dependabot/github_actions/"):
        return "github_actions"
    if head_ref.startswith("dependabot/pip/"):
        return "pip"
    return "deps"


def standard_message(title: str, head_ref: str) -> str | None:
    """Return a single, non-repeating conventional commit message."""
    match = DEPENDABOT_TITLE_RE.search(title)
    if not match:
        return None
    package = match.group("package").strip()
    old = match.group("old").strip()
    new = match.group("new").strip()
    eco = ecosystem_from_head_ref(head_ref)
    return f"chore(deps): bump {package} {old} → {new} [{eco}]"


def merge_pr(slug: str, pr: dict[str, object], *, dry_run: bool) -> tuple[bool, bool]:
    """Merge a single Dependabot PR using the standard commit schema.

    Returns (merged_or_enqueued, skipped).
    """
    number = pr["number"]
    title = pr["title"]
    head_ref = pr["headRefName"]
    message = standard_message(title, head_ref)
    if message is None:
        print(f"  SKIP #{number}: title does not match bump schema: {title}")
        return False, True

    base_cmd = [
        "gh",
        "pr",
        "merge",
        str(number),
        "-R",
        slug,
        "--squash",
        "--subject",
        message,
        "--delete-branch",
    ]
    print(f"  MERGE #{number}: {message}")
    if dry_run:
        print(f"    [dry-run] {' '.join(base_cmd)}")
        return True, False

    result = run(base_cmd, check=False)
    if result.returncode == 0:
        print(f"  OK #{number}")
        return True, False

    stderr = result.stderr.strip()
    if "Required status check" in stderr or "checks" in stderr.lower():
        auto_cmd = [*base_cmd, "--auto"]
        auto_result = run(auto_cmd, check=False)
        if auto_result.returncode == 0:
            print(f"  ENQUEUED #{number}: will merge when checks pass")
            return True, False
        stderr = auto_result.stderr.strip()

    if "already merged" in stderr.lower() or "not found" in stderr.lower():
        print(f"  ALREADY #{number}")
        return True, False

    print(f"  FAIL #{number}: {stderr}", file=sys.stderr)
    return False, False


def process_repo(slug: str, base: str, *, dry_run: bool) -> tuple[int, int, int]:
    """Process all open Dependabot PRs for a single repository.

    Returns (merged, skipped, failed).
    """
    print(f"==> {slug}")
    prs = list_dependabot_prs(slug, base)
    if not prs:
        print("  no open dependabot PRs")
        return 0, 0, 0

    merged = skipped = failed = 0
    for pr in prs:
        ok, is_skip = merge_pr(slug, pr, dry_run=dry_run)
        if is_skip:
            skipped += 1
        elif ok:
            merged += 1
        else:
            failed += 1
    return merged, skipped, failed


def main() -> int:
    """Entry point for the dependabot merge orchestrator."""
    parser = argparse.ArgumentParser(description="Merge Dependabot PRs across FLEXT workspace")
    parser.add_argument("--base", default="main", help="target branch for PRs")
    parser.add_argument("--dry-run", action="store_true", help="preview only")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS, help="parallel repo workers")
    args = parser.parse_args()

    root = Path.cwd()
    repos = discover_repos(root)
    if not repos:
        print("No submodules discovered from .gitmodules")
        return 0

    slugs: list[str] = []
    for path in repos:
        submodule = root / path
        if not ((submodule / ".git").is_dir() or (submodule / ".git").is_file()):
            print(f"SKIP {path}: not a git submodule")
            continue
        slug = repo_slug_from_origin(submodule)
        if not slug:
            print(f"SKIP {path}: cannot resolve GitHub slug")
            continue
        slugs.append(slug)

    total_merged = total_skipped = total_failed = 0
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(process_repo, slug, args.base, args.dry_run): slug
            for slug in slugs
        }
        for future in as_completed(futures):
            merged, skipped, failed = future.result()
            total_merged += merged
            total_skipped += skipped
            total_failed += failed

    print(
        f"\nSummary: merged={total_merged} skipped={total_skipped} failed={total_failed}"
    )
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
