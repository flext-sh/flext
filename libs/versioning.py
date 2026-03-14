from __future__ import annotations

"""Semantic versioning utilities for FLEXT workspace releases."""

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
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    project = data.get("project")
    if not isinstance(project, dict):
        msg = "unable to detect [project] section from pyproject.toml"
        raise TypeError(msg)
    version = project.get("version")
    if not isinstance(version, str) or not version:
        msg = "unable to detect version from pyproject.toml"
        raise RuntimeError(msg)
    return version.removesuffix("-dev")


def replace_project_version(content: str, version: str) -> tuple[str, bool]:
    """Replace project version in TOML content string."""
    document = tomlkit.parse(content)
    project = document.get("project")
    if not isinstance(project, Table):
        return content, False
    current = project.get("version")
    if not isinstance(current, str) or not current:
        return content, False
    _ = parse_semver(current.removesuffix("-dev"))
    if current == version:
        return content, False
    project["version"] = version
    updated = tomlkit.dumps(document)
    return updated, updated != content
