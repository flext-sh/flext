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

import configparser
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Annotated

from flext_cli import m, p, u

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
PR_LIST_LIMIT = 100

_BASE_VALUE_REQUIRED = "--base requires a value"
_WORKERS_VALUE_REQUIRED = "--workers requires a value"


class MergeOptions(m.Value):
    """Validated command-line options for the dependabot merge orchestrator."""

    model_config = m.ConfigDict(extra="forbid")

    base: Annotated[str, m.Field(description="Target branch for PRs")] = "main"
    dry_run: Annotated[bool, m.Field(description="Preview only")] = False
    workers: Annotated[int, m.Field(description="Parallel repo workers")] = MAX_WORKERS
    close_on_conflict: Annotated[bool, m.Field(description="Close conflicting PRs")] = (
        True
    )


def _run_cmd(
    cmd: list[str], *, cwd: Path | None = None
) -> p.Result[p.Cli.CommandOutput]:
    """Run a subprocess command with closed stdin to avoid interactive prompts."""
    return u.Cli.run_raw(cmd, cwd=cwd, input_data="")


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
    result = _run_cmd(["git", "-C", str(path), "remote", "get-url", "origin"])
    if result.failure or result.value.exit_code != 0:
        return None
    url = result.value.stdout.strip()
    if url.startswith("git@github.com:"):
        return url.replace("git@github.com:", "").replace(".git", "")
    if "github.com/" in url:
        return url.split("github.com/", 1)[1].replace(".git", "")
    return None


def list_dependabot_prs(slug: str, base: str) -> list[dict[str, int | str]]:
    """List open Dependabot PRs targeting the given base branch."""
    result = _run_cmd([
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
        str(PR_LIST_LIMIT),
    ])
    if result.failure or result.value.exit_code != 0:
        return []
    try:
        return json.loads(result.value.stdout or "[]")
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
    result = _run_cmd(["gh", "pr", "update-branch", str(number), "-R", slug])
    if result.failure:
        return False
    if result.value.exit_code == 0:
        return True
    # update-branch may report "Already up to date"; treat as success.
    return "already up to date" in result.value.stderr.lower()


def close_pr(slug: str, number: int, *, dry_run: bool, reason: str) -> bool:
    """Close a stale/conflicting Dependabot PR so it can be regenerated."""
    if dry_run:
        return True
    result = _run_cmd([
        "gh",
        "pr",
        "close",
        str(number),
        "-R",
        slug,
        "--comment",
        reason,
    ])
    if result.failure:
        return False
    return result.value.exit_code == 0


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

    result = _run_cmd(base_cmd)
    if result.failure:
        return False, False, False
    if result.value.exit_code == 0:
        return True, False, False

    merge_stderr = result.value.stderr.strip()
    stderr = merge_stderr
    if (
        "Required status check" in stderr
        or "checks" in stderr.lower()
        or "add the `--auto` flag" in stderr
        or "--auto" in stderr
    ):
        auto_result = _run_cmd([*base_cmd, "--auto"])
        if not auto_result.failure and auto_result.value.exit_code == 0:
            return True, False, False
        stderr = auto_result.value.stderr.strip() if not auto_result.failure else ""

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
            retry = _run_cmd(base_cmd)
            if not retry.failure and retry.value.exit_code == 0:
                return True, False, False
            retry_stderr = retry.value.stderr.strip() if not retry.failure else ""
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


def _parse_options(argv: list[str] | None = None) -> MergeOptions:
    """Parse command-line options into a validated model."""
    raw_args = list(sys.argv[1:] if argv is None else argv)
    raw: dict[str, str | bool | int] = {
        "base": "main",
        "dry_run": False,
        "workers": MAX_WORKERS,
        "close_on_conflict": True,
    }
    i = 0
    while i < len(raw_args):
        arg = raw_args[i]
        if arg == "--base":
            i += 1
            if i >= len(raw_args):
                raise SystemExit(_BASE_VALUE_REQUIRED)
            raw["base"] = raw_args[i]
        elif arg == "--dry-run":
            raw["dry_run"] = True
        elif arg == "--workers":
            i += 1
            if i >= len(raw_args):
                raise SystemExit(_WORKERS_VALUE_REQUIRED)
            raw["workers"] = int(raw_args[i])
        elif arg == "--close-on-conflict":
            raw["close_on_conflict"] = True
        elif arg == "--no-close-on-conflict":
            raw["close_on_conflict"] = False
        elif arg in {"-h", "--help"}:
            raise SystemExit(__doc__ or "Usage: ...")
        else:
            unknown_arg = f"Unknown argument: {arg}"
            raise SystemExit(unknown_arg)
        i += 1
    return MergeOptions.model_validate(raw)


def main(argv: list[str] | None = None) -> int:
    """Entry point for the dependabot merge orchestrator."""
    options = _parse_options(argv)
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
    with ThreadPoolExecutor(max_workers=options.workers) as executor:
        futures = {
            executor.submit(
                process_repo,
                slug,
                options.base,
                dry_run=options.dry_run,
                close_on_conflict=options.close_on_conflict,
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
