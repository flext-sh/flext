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

import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from flext_cli import c, u
from scripts.dispatch import Dispatch

if TYPE_CHECKING:
    from collections.abc import Sequence

EXPECTED_CENTRALIZED_COMPOSE_COUNT = 15
EXPECTED_CENTRALIZED_DOCKERFILE_COUNT = 20


class _DockerStandardizationChecker:
    """Run the Docker standardization checks and report results."""

    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root
        self.errors = 0
        self.warnings = 0

    def _find(
        self, pattern: str, *, excluded: Sequence[str] = (), file_only: bool = True
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

    def _check_no_outside_files(
        self,
        _name: str,
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
            for _p in outside[:5]:
                pass
            if is_warning:
                self.warnings += 1
            else:
                self.errors += 1

    def check_duplicate_compose(self) -> None:
        self._check_no_outside_files(
            "docker-compose file(s)", "docker-compose*.yml", ("docker",)
        )

    def check_duplicate_dockerfiles(self) -> None:
        self._check_no_outside_files("Dockerfile(s)", "Dockerfile*", ("docker/images",))

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
        if count < EXPECTED_CENTRALIZED_COMPOSE_COUNT:
            self.errors += 1

    def check_centralized_dockerfile_count(self) -> None:
        images_dir = self.workspace_root / "docker" / "images"
        count = len(list(images_dir.glob("Dockerfile.*")))
        if count < EXPECTED_CENTRALIZED_DOCKERFILE_COUNT:
            self.errors += 1

    def check_tk_importable(self) -> None:
        result = u.Cli.run_checked(
            [
                sys.executable,
                "-c",
                "from flext_tests import tk; u.Cli.emit_raw('OK\\n')",
            ],
            cwd=self.workspace_root,
        )
        if result.success:
            pass
        else:
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
        code = (
            "from flext_tests import " + ", ".join(names) + "; u.Cli.emit_raw('OK\\n')"
        )
        result = u.Cli.run_checked(
            [sys.executable, "-c", code], cwd=self.workspace_root
        )
        if result.success:
            pass
        else:
            self.warnings += 1

    def check_docker_scripts(self) -> None:
        scripts = [
            p
            for p in self._find("*docker*.sh")
            if not str(p.relative_to(self.workspace_root)).startswith("docker")
        ]
        if scripts:
            for _p in scripts[:5]:
                pass
            self.warnings += 1

    def check_deprecated_parallel_docker(self) -> None:
        pattern = re.compile(
            r"(?:from\s+flext_tests\.parallel_docker|import\s+.*\bparallel_docker\b|from\s+\S+\s+import\s+.*\bparallel_docker\b)"
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
            for _p in hits[:5]:
                pass
            self.warnings += 1

    def run(self) -> int:
        checks = [
            ("[1/9] Duplicate docker-compose files", self.check_duplicate_compose),
            ("[2/9] Dockerfiles outside images/", self.check_duplicate_dockerfiles),
            ("[3/9] Local docker_fixtures.py files", self.check_duplicate_fixtures),
            (
                "[4/9] Centralized compose files count",
                self.check_centralized_compose_count,
            ),
            (
                "[5/9] Centralized Dockerfiles count",
                self.check_centralized_dockerfile_count,
            ),
            ("[6/9] tk availability", self.check_tk_importable),
            ("[7/9] Centralized fixtures availability", self.check_fixtures_importable),
            ("[8/9] Prohibited Docker scripts", self.check_docker_scripts),
            (
                "[9/9] Deprecated parallel_docker usage",
                self.check_deprecated_parallel_docker,
            ),
        ]
        for _title, check in checks:
            check()

        if self.errors == 0 and self.warnings == 0:
            return 0
        if self.errors == 0:
            return 0
        return 1


def run_command() -> int:
    """Run the Docker standardization checks."""
    if Dispatch.surface_validation_enabled():
        return 0
    workspace_root = Path(
        u.Cli.process_env().get("WORKSPACE_ROOT", str(Path.cwd()))
    ).resolve()
    return _DockerStandardizationChecker(workspace_root).run()


if __name__ == "__main__":
    Dispatch.promoted_main(__file__, run_command)
