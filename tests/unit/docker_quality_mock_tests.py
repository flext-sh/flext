from __future__ import annotations

from pathlib import Path

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

FORBIDDEN_MOCK_COPIES = (
    "docker/images/support/quality/",
    "src/flext_core/",
    "src/flext_observability/",
)


class TestDockerQualityDockerfiles:
    def test_quality_dockerfiles_install_workspace_packages(self) -> None:
        repository_root = Path(__file__).resolve().parents[2]
        for dockerfile in QUALITY_DOCKERFILES:
            content = (repository_root / dockerfile).read_text(encoding="utf-8")
            assert "WORKDIR /app/flext-quality" in content
            for install_target in REQUIRED_WORKSPACE_INSTALLS:
                assert install_target in content

    def test_quality_dockerfiles_do_not_copy_mock_packages(self) -> None:
        repository_root = Path(__file__).resolve().parents[2]
        for dockerfile in QUALITY_DOCKERFILES:
            content = (repository_root / dockerfile).read_text(encoding="utf-8")
            for forbidden_copy in FORBIDDEN_MOCK_COPIES:
                assert forbidden_copy not in content
