# AUTO-GENERATED FILE — Regenerate with: make gen
"""Scripts.workspace package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from types import MappingProxyType

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from .dependabot_merge import (
        DEPENDABOT_AUTHOR,
        DEPENDABOT_GROUP_RE,
        DEPENDABOT_TITLE_RE,
        MAX_WORKERS,
        MergeOptions,
        PR_LIST_LIMIT,
        RETRIES_ON_CONFLICT,
        close_pr,
        discover_repos,
        ecosystem_from_head_ref,
        list_dependabot_prs,
        main,
        merge_pr,
        process_repo,
        repo_slug_from_origin,
        standard_message,
        update_pr_branch,
    )
__all__: tuple[str, ...] = (
    "DEPENDABOT_AUTHOR",
    "DEPENDABOT_GROUP_RE",
    "DEPENDABOT_TITLE_RE",
    "MAX_WORKERS",
    "PR_LIST_LIMIT",
    "RETRIES_ON_CONFLICT",
    "MergeOptions",
    "close_pr",
    "discover_repos",
    "ecosystem_from_head_ref",
    "list_dependabot_prs",
    "main",
    "merge_pr",
    "process_repo",
    "repo_slug_from_origin",
    "standard_message",
    "update_pr_branch",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".dependabot_merge": (
                "DEPENDABOT_AUTHOR",
                "DEPENDABOT_GROUP_RE",
                "DEPENDABOT_TITLE_RE",
                "MAX_WORKERS",
                "MergeOptions",
                "PR_LIST_LIMIT",
                "RETRIES_ON_CONFLICT",
                "close_pr",
                "discover_repos",
                "ecosystem_from_head_ref",
                "list_dependabot_prs",
                "main",
                "merge_pr",
                "process_repo",
                "repo_slug_from_origin",
                "standard_message",
                "update_pr_branch",
            )
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
