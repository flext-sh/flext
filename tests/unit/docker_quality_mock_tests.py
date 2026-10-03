"""FLEXT infra test helpers for docker_quality_mock_tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

from flext_tests import tm


class TestsFlextRootDockerQualityDockerfiles:
    """Tests for quality Dockerfile mock integrity."""

    QUALITY_DOCKERFILES = (
        "docker/images/Dockerfile.flext-quality",
        "docker/images/Dockerfile.flext-quality-simple",
        "docker/images/Dockerfile.flext-quality-fixed",
        "docker/images/Dockerfile.flext-quality-enterprise",
    )
    REQUIRED_WORKSPACE_INSTALLS = (
        "-e /app/flext-core",
        "-e /app/flext-cli",
        "-e /app/flext-web",
        "-e /app/flext-tests",
        "-e /app/flext-quality",
    )
    FORBIDDEN_MOCK_COPIES = ("src/flext_core/", "src/flext_observability/")

    def test_quality_dockerfiles_install_workspace_packages(self) -> None:
        """Test quality dockerfiles install workspace packages."""
        repository_root = Path(__file__).resolve().parents[2]
        for dockerfile in self.QUALITY_DOCKERFILES:
            content = (repository_root / dockerfile).read_text(encoding="utf-8")
            tm.that("WORKDIR /app/flext-quality" in content, eq=True)
            for install_target in self.REQUIRED_WORKSPACE_INSTALLS:
                tm.that(install_target in content, eq=True)

    def test_quality_dockerfiles_do_not_copy_mock_packages(self) -> None:
        """Test quality dockerfiles do not copy mock packages."""
        repository_root = Path(__file__).resolve().parents[2]
        for dockerfile in self.QUALITY_DOCKERFILES:
            content = (repository_root / dockerfile).read_text(encoding="utf-8")
            for forbidden_copy in self.FORBIDDEN_MOCK_COPIES:
                tm.that(forbidden_copy not in content, eq=True)
