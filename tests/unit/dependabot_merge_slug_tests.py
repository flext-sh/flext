"""URL slug resolution contracts for the workspace Dependabot merge script.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from scripts.workspace.dependabot_merge import FlextRootDependabotMerge

from flext_tests import tm


class TestsFlextRootDependabotMergeSlug:
    """Slug resolution trusts only a parsed GitHub host, never a substring."""

    class Tests:
        """Regression suite for CodeQL py/incomplete-url-substring-sanitization."""

        @staticmethod
        def test_forged_host_substring_is_rejected() -> None:
            """A trusted marker inside an attacker URL never yields a slug."""
            for forged in (
                "https://evil.com/?github.com/owner/repo",
                "https://github.com.evil.com/owner/repo",
                "https://evil.com/github.com/owner/repo",
            ):
                tm.that(
                    FlextRootDependabotMerge.slug_from_remote_url(forged), none=True
                )

        @staticmethod
        def test_canonical_remotes_resolve() -> None:
            """Real GitHub https/scp/ssh remotes resolve to owner/repo."""
            for url in (
                "https://github.com/owner/repo.git",
                "https://github.com/owner/repo",
                "git@github.com:owner/repo.git",
                "ssh://git@github.com/owner/repo",
                "https://www.github.com/owner/repo",
            ):
                tm.that(
                    FlextRootDependabotMerge.slug_from_remote_url(url), eq="owner/repo"
                )

        @staticmethod
        def test_non_github_and_non_url_inputs_are_rejected() -> None:
            """A non-allowlisted scheme or a non-URL string never yields a slug."""
            for rejected in ("ftp://github.com/owner/repo", "not-a-url", ""):
                tm.that(
                    FlextRootDependabotMerge.slug_from_remote_url(rejected), none=True
                )
