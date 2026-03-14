"""Semantic versioning utilities for FLEXT workspace releases."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import tomlkit
from tomlkit.items import Table

SEMVER_RE = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)$"
)


def parse_semver(version: str) -> tuple[int, int, int]:
    """Parse a semver string into (major, minor, patch) tuple."""
    match = SEMVER_RE.match(version)
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
    match = re.fullmatch(r"release/(?P<version>\d+\.\d+\.\d+)", branch)
    if not match:
        return None
    return f"v{match.group('version')}"


def current_workspace_version(root: Path) -> str:
    """Read current workspace version from root pyproject.toml."""
    pyproject = root / "pyproject.toml"
    raw_data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    if not isinstance(raw_data, dict):
        msg = "unable to detect [project] section from pyproject.toml"
        raise TypeError(msg)
    data_map = {str(key): value for key, value in raw_data.items()}
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
    if not isinstance(raw_document, Table):
        return content, False
    document = raw_document
    project_value = document.get("project")
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
    updated = str(tomlkit.dumps(document))
    return updated, updated != content
