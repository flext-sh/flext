"""Runtime contract tests for the workspace provider manifest."""

from __future__ import annotations

import tomllib
from pathlib import Path

from packaging.requirements import Requirement

from flext_tests import tm


def test_provider_owned_paths_exist() -> None:
    """Every provider-owned path resolves from the provider repository root."""
    root = Path(__file__).resolve().parents[2]
    manifest = tomllib.loads(
        (root / ".agents" / "provider.toml").read_text(encoding="utf-8")
    )
    required_surfaces = manifest.get("required_surfaces")
    session_command = manifest.get("session_command")
    codemod_provider = manifest.get("codemod_provider")
    tm.that(isinstance(required_surfaces, list), eq=True)
    tm.that(isinstance(session_command, str), eq=True)
    tm.that(isinstance(codemod_provider, str), eq=True)
    owned_paths = (
        *(value for value in required_surfaces or () if isinstance(value, str)),
        *(
            value
            for value in (session_command, codemod_provider)
            if isinstance(value, str)
        ),
    )
    tm.that(len(owned_paths), eq=len(required_surfaces or ()) + 2)
    for relative_path in owned_paths:
        tm.that((root / relative_path).is_file(), eq=True)


def test_provider_marker_distribution_is_declared() -> None:
    """The provider activates from a real root project dependency."""
    root = Path(__file__).resolve().parents[2]
    manifest = tomllib.loads(
        (root / ".agents" / "provider.toml").read_text(encoding="utf-8")
    )
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    marker_distribution = manifest.get("marker_distribution")
    project = pyproject.get("project")
    tm.that(isinstance(marker_distribution, str), eq=True)
    tm.that(isinstance(project, dict), eq=True)
    dependencies = project.get("dependencies") if isinstance(project, dict) else None
    tm.that(isinstance(dependencies, list), eq=True)
    declared_distributions = {
        Requirement(dependency).name
        for dependency in dependencies or ()
        if isinstance(dependency, str)
    }
    tm.that(
        isinstance(marker_distribution, str)
        and marker_distribution in declared_distributions,
        eq=True,
    )
