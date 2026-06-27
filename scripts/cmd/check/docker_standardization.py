#!/usr/bin/env python3
"""Validate FLEXT Docker standardization.

Equivalent to the legacy ``docker/validate_docker_standardization.sh`` script.
Checks that Docker artifacts are centralized under ``docker/`` and that the
shared ``tk`` fixture API is available.
"""
# /// flext-command
# verb = "check"
# what = "docker_standardization"
# domain = "quality"
# summary = "Validate Docker artifact centralization"
# description = "Checks that Docker artifacts are centralized and shared fixtures are importable."
# example = "make check WHAT=docker_standardization"
# mutates = false
# aliases = []
# params = []
# rules = ["dev-gate"]
# ///

from __future__ import annotations

import os
import sys
from collections.abc import Sequence
from pathlib import Path

from flext_cli import c, u


class _DockerStandardizationChecker:
    """Run the Docker standardization checks and report results."""

    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root
        self.errors = 0
        self.warnings = 0

    def _find(
        self,
        pattern: str,
        *,
        excluded: Sequence[str] = (),
        file_only: bool = True,
    ) -> list[Path]:
        matches: list[Path] = []
        for path in self.workspace_root.rglob(pattern):
            if any(part.startswith(".") for part in path.parts):
                continue
            if file_only and not path.is_file():
                continue
            rel = path.relative_to(self.workspace_root)
            if any(str(rel).startswith(ex) for ex in excluded):
                continue
            matches.append(path)
        return matches

    def _print_header(self, title: str) -> None:
        print(f"\n{title}")

    def _check_no_outside_files(
        self,
        name: str,
        pattern: str,
        allowed_prefixes: Sequence[str],
        *,
        is_warning: bool = False,
    ) -> None:
        outside = [
            p
            for p in self._find(pattern)
            if not any(
                str(p.relative_to(self.workspace_root)).startswith(prefix)
                for prefix in allowed_prefixes
            )
        ]
        if outside:
            level = "WARNING" if is_warning else "FAILED"
            color = "\033[1;33m" if is_warning else "\033[0;31m"
            reset = "\033[0m"
            print(f"  {color}{level}{reset}: Found {len(outside)} {name} outside allowed locations:")
            for p in outside[:5]:
                print(f"    - {p.relative_to(self.workspace_root)}")
            if is_warning:
                self.warnings += 1
            else:
                self.errors += 1
        else:
            print(f"  \033[0;32mPASSED{chr(27)}[0m: No rogue {name} found")

    def check_duplicate_compose(self) -> None:
        self._check_no_outside_files(
            "docker-compose file(s)",
            "docker-compose*.yml",
            ("docker",),
        )

    def check_duplicate_dockerfiles(self) -> None:
        self._check_no_outside_files(
            "Dockerfile(s)",
            "Dockerfile*",
            ("docker/images",),
        )

    def check_duplicate_fixtures(self) -> None:
        self._check_no_outside_files(
            "local docker_fixtures.py file(s)",
            "docker_fixtures.py",
            ("flext-core/src/flext_tests/fixtures",),
            is_warning=True,
        )

    def check_centralized_compose_count(self) -> None:
        docker_dir = self.workspace_root / "docker"
        count = len(list(docker_dir.glob("docker-compose*.yml")))
        if count < 15:
            print(f"  \033[0;31mFAILED\033[0m: Expected at least 15 compose files, found {count}")
            self.errors += 1
        else:
            print(f"  \033[0;32mPASSED\033[0m: Found {count} centralized docker-compose files")

    def check_centralized_dockerfile_count(self) -> None:
        images_dir = self.workspace_root / "docker" / "images"
        count = len(list(images_dir.glob("Dockerfile.*")))
        if count < 20:
            print(f"  \033[0;31mFAILED\033[0m: Expected at least 20 Dockerfiles, found {count}")
            self.errors += 1
        else:
            print(f"  \033[0;32mPASSED\033[0m: Found {count} centralized Dockerfiles")

    def check_tk_importable(self) -> None:
        result = u.Cli.run_checked(
            [sys.executable, "-c", "from flext_tests import tk; print('OK')"],
            cwd=self.workspace_root,
        )
        if result.success:
            print(f"  \033[0;32mPASSED\033[0m: tk is importable")
        else:
            print(f"  \033[0;31mFAILED\033[0m: Cannot import tk from flext_tests")
            self.errors += 1

    def check_fixtures_importable(self) -> None:
        names = (
            "flext_docker",
            "flext_oud_container",
            "ldap_container",
            "oracle_container",
            "postgres_container",
            "redis_container",
        )
        code = "from flext_tests import " + ", ".join(names) + "; print('OK')"
        result = u.Cli.run_checked(
            [sys.executable, "-c", code],
            cwd=self.workspace_root,
        )
        if result.success:
            print(f"  \033[0;32mPASSED\033[0m: Centralized fixtures are importable")
        else:
            print(f"  \033[1;33mWARNING\033[0m: Some centralized fixtures may not be available")
            self.warnings += 1

    def check_docker_scripts(self) -> None:
        scripts = [
            p
            for p in self._find("*docker*.sh")
            if not str(p.relative_to(self.workspace_root)).startswith("docker")
        ]
        if scripts:
            print(f"  \033[1;33mWARNING\033[0m: Found {len(scripts)} Docker-related shell script(s) outside docker/:")
            for p in scripts[:5]:
                print(f"    - {p.relative_to(self.workspace_root)}")
            self.warnings += 1
        else:
            print(f"  \033[0;32mPASSED\033[0m: No prohibited Docker scripts found")

    def check_deprecated_parallel_docker(self) -> None:
        import re

        pattern = re.compile(
            r"(?:from\s+flext_tests\.parallel_docker|import\s+.*\bparallel_docker\b|from\s+\S+\s+import\s+.*\bparallel_docker\b)",
        )
        hits: list[Path] = []
        for p in self._find("*.py"):
            try:
                text = p.read_text(encoding=c.Cli.ENCODING_DEFAULT)
            except OSError:
                continue
            if pattern.search(text):
                hits.append(p)
        if hits:
            print(f"  \033[1;33mWARNING\033[0m: Found {len(hits)} file(s) using deprecated parallel_docker:")
            for p in hits[:5]:
                print(f"    - {p.relative_to(self.workspace_root)}")
            self.warnings += 1
        else:
            print(f"  \033[0;32mPASSED\033[0m: No deprecated parallel_docker usage found")

    def run(self) -> int:
        print("\033[0;34mFLEXT Docker Standardization Validation\033[0m")
        checks = [
            ("[1/9] Duplicate docker-compose files", self.check_duplicate_compose),
            ("[2/9] Dockerfiles outside images/", self.check_duplicate_dockerfiles),
            ("[3/9] Local docker_fixtures.py files", self.check_duplicate_fixtures),
            ("[4/9] Centralized compose files count", self.check_centralized_compose_count),
            ("[5/9] Centralized Dockerfiles count", self.check_centralized_dockerfile_count),
            ("[6/9] tk availability", self.check_tk_importable),
            ("[7/9] Centralized fixtures availability", self.check_fixtures_importable),
            ("[8/9] Prohibited Docker scripts", self.check_docker_scripts),
            ("[9/9] Deprecated parallel_docker usage", self.check_deprecated_parallel_docker),
        ]
        for title, check in checks:
            self._print_header(title)
            check()

        print("\n\033[0;34mValidation Summary\033[0m")
        if self.errors == 0 and self.warnings == 0:
            print("  \033[0;32mALL CHECKS PASSED\033[0m")
            return 0
        if self.errors == 0:
            print(f"  \033[1;33mPASSED WITH WARNINGS\033[0m (warnings={self.warnings})")
            return 0
        print(f"  \033[0;31mVALIDATION FAILED\033[0m (errors={self.errors}, warnings={self.warnings})")
        return 1


def main() -> int:
    workspace_root = Path(
        u.Cli.process_env().get("WORKSPACE_ROOT", os.getcwd())
    ).resolve()
    return _DockerStandardizationChecker(workspace_root).run()


if __name__ == "__main__":
    from scripts.dispatch import promoted_main

    raise SystemExit(promoted_main(__file__, main))
