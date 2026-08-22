"""Semantic versioning utilities for FLEXT workspace releases."""

from __future__ import annotations

import tomllib
from pathlib import Path

import tomlkit
from tomlkit.items import Table

from flext_core import c

SEMVER_RE = c.PATTERN_SEMVER_RE


def parse_semver(version: str) -> tuple[int, int, int]:
    """Parse a semver string into (major, minor, patch) tuple."""
    match = SEMVER_RE.fullmatch(version)
    if not match:
        msg = f"invalid semver version: {version}"
        raise ValueError(msg)
    return (
        int(match.group("major")),
        int(match.group("minor")),
        int(match.group("patch")),
    )


def bump_version(current_version: str, bump: str) -> str:
    """Bump a semver version string by the specified component."""
    major, minor, patch = parse_semver(current_version)
    if bump == "major":
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    if bump == "patch":
        return f"{major}.{minor}.{patch + 1}"
    msg = f"unsupported bump: {bump}"
    raise ValueError(msg)


def release_tag_from_branch(branch: str) -> str | None:
    """Extract release tag from branch name, or None."""
    version = branch.removesuffix("-dev")
    if SEMVER_RE.fullmatch(version):
        return f"v{version}"
    release_prefix = "release/"
    if not branch.startswith(release_prefix):
        return None
    release_version = branch.removeprefix(release_prefix)
    if not SEMVER_RE.fullmatch(release_version):
        return None
    return f"v{release_version}"


def current_workspace_version(root: Path) -> str:
    """Read current workspace version from root pyproject.toml."""
    pyproject = root / "pyproject.toml"
    raw_data = tomllib.loads(pyproject.read_text(encoding=c.DEFAULT_ENCODING))
    data_map = dict(raw_data.items())
    project_value = data_map.get("project")
    if not isinstance(project_value, dict):
        msg = "unable to detect [project] section from pyproject.toml"
        raise TypeError(msg)
    project_map = {str(key): value for key, value in project_value.items()}
    version_value = project_map.get("version")
    if not isinstance(version_value, str) or not version_value:
        msg = "unable to detect version from pyproject.toml"
        raise RuntimeError(msg)
    return version_value.removesuffix("-dev")


def replace_project_version(content: str, version: str) -> tuple[str, bool]:
    """Replace project version in TOML content string."""
    raw_document = tomlkit.parse(content)
    project_value = raw_document.get("project")
    if not isinstance(project_value, Table):
        return content, False
    project_map = {str(key): value for key, value in project_value.items()}
    current_value = project_map.get("version")
    if not isinstance(current_value, str) or not current_value:
        return content, False
    _ = parse_semver(current_value.removesuffix("-dev"))
    if current_value == version:
        return content, False
    project_value["version"] = version
    updated = tomlkit.dumps(raw_document)
    return updated, updated != content
