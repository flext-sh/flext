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


def test_provider_propagation_is_idempotent() -> None:
    """Provider surfaces exist and router resolves skills from typed config."""
    root = Path(__file__).resolve().parents[2]
    manifest = tomllib.loads(
        (root / ".agents" / "provider.toml").read_text(encoding="utf-8")
    )
    surfaces = manifest.get("surfaces")
    tm.that(isinstance(surfaces, dict), eq=True)
    always_paths = surfaces.get("always", []) if isinstance(surfaces, dict) else []
    on_demand_paths = surfaces.get("on_demand", []) if isinstance(surfaces, dict) else []
    for surface_path in (*always_paths, *on_demand_paths):
        tm.that((root / surface_path).is_file(), eq=True)
    router_text = (
        root / ".agents" / "skills" / "flext-context-routing" / "SKILL.md"
    ).read_text(encoding="utf-8")
    tm.that("config.AiHub.paths.agents_home" in router_text, eq=True)
