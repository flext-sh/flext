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
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

DEPENDABOT_AUTHOR = "dependabot[bot]"
DEPENDABOT_TITLE_RE = re.compile(
    r"bump\s+(?P<package>.+?)\s+from\s+(?P<old>\S+)\s+to\s+(?P<new>\S+)\s*$",
    re.IGNORECASE,
)
DEPENDABOT_GROUP_RE = re.compile(
    r"bump\s+(?:the\s+)?(?P<group>[\w\-]+)\s+group\s+.*\s+with\s+(?P<count>\d+)\s+updates?",
    re.IGNORECASE,
)
MAX_WORKERS = 4
RETRIES_ON_CONFLICT = 2


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a subprocess command (stdin=/dev/null to avoid interactive prompts)."""
    return subprocess.run(
        cmd, check=check, capture_output=True, text=True, stdin=subprocess.DEVNULL
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


def list_dependabot_prs(slug: str, base: str) -> list[dict[str, int | str]]:
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
    """Return a single, non-repeating conventional commit message.

    Supports single-package bumps and Dependabot grouped updates.
    """
    single = DEPENDABOT_TITLE_RE.search(title)
    if single:
        package = single.group("package").strip()
        old = single.group("old").strip()
        new = single.group("new").strip()
        eco = ecosystem_from_head_ref(head_ref)
        return f"chore(deps): bump {package} {old} → {new} [{eco}]"

    group = DEPENDABOT_GROUP_RE.search(title)
    if group:
        group_name = group.group("group").strip()
        count = group.group("count").strip()
        eco = ecosystem_from_head_ref(head_ref)
        return (
            f"chore(deps): bump {group_name} dependency group ({count} updates) [{eco}]"
        )

    return None


def update_pr_branch(slug: str, number: int) -> bool:
    """Update a PR branch from its base (rebase/merge) to resolve conflicts."""
    result = run(["gh", "pr", "update-branch", str(number), "-R", slug], check=False)
    if result.returncode == 0:
        return True
    # update-branch may report "Already up to date"; treat as success.
    return "already up to date" in result.stderr.lower()


def close_pr(slug: str, number: int, *, dry_run: bool, reason: str) -> bool:
    """Close a stale/conflicting Dependabot PR so it can be regenerated."""
    if dry_run:
        return True
    close_result = run(
        ["gh", "pr", "close", str(number), "-R", slug, "--comment", reason], check=False
    )
    return close_result.returncode == 0


def merge_pr(
    slug: str,
    pr: dict[str, int | str],
    *,
    dry_run: bool,
    close_on_conflict: bool = True,
) -> tuple[bool, bool, bool]:
    """Merge a single Dependabot PR using the standard commit schema.

    Returns (merged_or_enqueued, skipped, closed).
    """
    number = int(pr["number"])
    title = str(pr["title"])
    head_ref = str(pr["headRefName"])
    message = standard_message(title, head_ref)
    if message is None:
        return False, True, False

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
    if dry_run:
        return True, False, False

    result = run(base_cmd, check=False)
    if result.returncode == 0:
        return True, False, False

    merge_stderr = result.stderr.strip()
    stderr = merge_stderr
    if (
        "Required status check" in stderr
        or "checks" in stderr.lower()
        or "add the `--auto` flag" in stderr
        or "--auto" in stderr
    ):
        auto_cmd = [*base_cmd, "--auto"]
        auto_result = run(auto_cmd, check=False)
        if auto_result.returncode == 0:
            return True, False, False
        stderr = auto_result.stderr.strip()

    if "already merged" in stderr.lower() or "not found" in stderr.lower():
        return True, False, False

    # Conflict: try to update the branch and retry a few times.
    conflict_indicators = (
        "conflict",
        "merge conflicts",
        "not mergeable",
        "cannot be cleanly created",
    )
    if any(indicator in merge_stderr.lower() for indicator in conflict_indicators):
        for _attempt in range(1, RETRIES_ON_CONFLICT + 1):
            if not update_pr_branch(slug, number):
                break
            retry = run(base_cmd, check=False)
            if retry.returncode == 0:
                return True, False, False
            retry_stderr = retry.stderr.strip()
            if not any(
                indicator in retry_stderr.lower() for indicator in conflict_indicators
            ):
                break

        if close_on_conflict:
            reason = (
                "Closing stale Dependabot PR due to persistent merge conflicts; "
                "Dependabot will recreate a fresh update if still needed."
            )
            if close_pr(slug, number, dry_run=dry_run, reason=reason):
                return False, False, True

    return False, False, False


def process_repo(
    slug: str, base: str, *, dry_run: bool, close_on_conflict: bool = True
) -> tuple[int, int, int, int]:
    """Process all open Dependabot PRs for a single repository.

    Returns (merged, skipped, failed, closed).
    """
    prs = list_dependabot_prs(slug, base)
    if not prs:
        return 0, 0, 0, 0

    # Sort ascending so older PRs merge first, reducing lock-file conflicts.
    prs.sort(key=lambda p: int(p["number"]))

    merged = skipped = failed = closed = 0
    for pr in prs:
        ok, is_skip, was_closed = merge_pr(
            slug, pr, dry_run=dry_run, close_on_conflict=close_on_conflict
        )
        if is_skip:
            skipped += 1
        elif ok:
            merged += 1
        elif was_closed:
            closed += 1
        else:
            failed += 1
    return merged, skipped, failed, closed


def main() -> int:
    """Entry point for the dependabot merge orchestrator."""
    parser = argparse.ArgumentParser(
        description="Merge Dependabot PRs across FLEXT workspace"
    )
    parser.add_argument("--base", default="main", help="target branch for PRs")
    parser.add_argument("--dry-run", action="store_true", help="preview only")
    parser.add_argument(
        "--workers", type=int, default=MAX_WORKERS, help="parallel repo workers"
    )
    parser.add_argument(
        "--close-on-conflict",
        action="store_true",
        default=True,
        help="close Dependabot PRs that cannot be merged due to persistent conflicts",
    )
    parser.add_argument(
        "--no-close-on-conflict",
        dest="close_on_conflict",
        action="store_false",
        help="leave conflicting PRs open for manual resolution",
    )
    args = parser.parse_args()

    root = Path.cwd()
    repos = discover_repos(root)
    if not repos:
        return 0

    slugs: list[str] = []
    for path in repos:
        submodule = root / path
        if not ((submodule / ".git").is_dir() or (submodule / ".git").is_file()):
            continue
        slug = repo_slug_from_origin(submodule)
        if not slug:
            continue
        slugs.append(slug)

    total_merged = total_skipped = total_failed = total_closed = 0
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(
                process_repo,
                slug,
                args.base,
                dry_run=args.dry_run,
                close_on_conflict=args.close_on_conflict,
            ): slug
            for slug in slugs
        }
        for future in as_completed(futures):
            merged, skipped, failed, closed = future.result()
            total_merged += merged
            total_skipped += skipped
            total_failed += failed
            total_closed += closed

    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
