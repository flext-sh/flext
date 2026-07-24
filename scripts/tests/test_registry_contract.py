"""Behavior-pinning contract tests for the scripts command framework.

These tests pin the public behavior of the registry-driven Make dispatcher.
They import only the public namespace (`scripts.dispatch.Dispatch`).
"""

from __future__ import annotations

import os
import sys

import pytest

from flext_tests import c, u
from scripts.dispatch import Dispatch


def _snapshot_env(keys: tuple[str, ...]) -> dict[str, str | None]:
    """Return a typed snapshot for environment keys mutated by a test."""
    return {key: os.environ.get(key) for key in keys}


def _restore_env(snapshot: dict[str, str | None]) -> None:
    """Restore environment keys from a typed snapshot."""
    for key, value in snapshot.items():
        os.environ.pop(key, None)
        if value is not None:
            os.environ[key] = value


@pytest.fixture(scope="module")
def registry() -> Dispatch.Registry:
    return Dispatch.discover()


def test_discover_succeeds_and_validates(registry: Dispatch.Registry) -> None:
    """Assert registry discovery reaches the canonical validation pass."""
    assert u.Tests.make_registry_verbs(registry), "no verbs discovered"


def test_every_verb_has_default_all_command(registry: Dispatch.Registry) -> None:
    for verb in u.Tests.make_registry_verbs(registry):
        commands = u.Tests.make_registry_commands(registry, verb).unwrap()
        assert Dispatch.DEFAULT_COMMAND in commands, (
            f"verb {verb!r} missing WHAT={Dispatch.DEFAULT_COMMAND}"
        )


def test_single_domain_per_verb(registry: Dispatch.Registry) -> None:
    for verb in u.Tests.make_registry_verbs(registry):
        commands = u.Tests.make_registry_commands(registry, verb).unwrap()
        domains = {cmd.domain for cmd in commands.values()}
        assert len(domains) == 1, f"verb {verb!r} has multiple domains: {domains}"


def test_all_mutating_commands_declare_required_apply(
    registry: Dispatch.Registry,
) -> None:
    """Assert every mutating command exposes the dispatcher mutation opt-in."""
    for verb in u.Tests.make_registry_verbs(registry):
        commands = u.Tests.make_registry_commands(registry, verb).unwrap()
        for command in commands.values():
            if not command.mutates:
                continue
            apply_param = next(
                (
                    param
                    for param in command.params
                    if param.name == c.Tests.MAKE_APPLY_PARAM
                ),
                None,
            )
            assert apply_param is not None, (
                f"{command.verb} WHAT={command.what} must declare APPLY"
            )
            assert apply_param.required is True, (
                f"{command.verb} WHAT={command.what} APPLY must be required"
            )
            assert c.Tests.MAKE_DISPATCH_ENV_VALUE in apply_param.choices, (
                f"{command.verb} WHAT={command.what} APPLY choices must include Y"
            )


def test_known_readonly_command(registry: Dispatch.Registry) -> None:
    check_all = u.Tests.make_registry_command(registry, "check", "all").unwrap()
    assert check_all.mutates is False
    assert check_all.domain == "quality"


def test_workspace_governance_verbs_use_target_metadata(
    registry: Dispatch.Registry,
) -> None:
    expected_targets = {
        ("clean", "all"): "_clean_default",
        ("coordination", "all"): "_coordination",
        ("status", "all"): "_status",
    }
    for key, target in expected_targets.items():
        command = u.Tests.make_registry_command(registry, *key).unwrap()
        assert command.target == target


def test_docs_command_declares_conditional_mutation(
    registry: Dispatch.Registry,
) -> None:
    docs_all = u.Tests.make_registry_command(registry, "docs", "all").unwrap()
    assert docs_all.mutates is False
    assert tuple((item.name, item.values) for item in docs_all.mutates_when) == (
        ("DOCS_PHASE", ("all", "fix", "generate")),
    )
    assert any(param.name == "FIX" for param in docs_all.params)


def test_unknown_verb_raises(registry: Dispatch.Registry) -> None:
    with pytest.raises(Dispatch.RegistryError):
        _registry_command_or_raise(registry, "does-not-exist", "all")


def test_unknown_what_raises(registry: Dispatch.Registry) -> None:
    with pytest.raises(Dispatch.RegistryError):
        _registry_command_or_raise(registry, "check", "no-such-what")


def test_main_reports_registry_errors(capsys: pytest.CaptureFixture[str]) -> None:
    """Expose dispatcher contract failures instead of returning an opaque exit 2."""
    assert Dispatch.main(("does-not-exist",)) == 2
    assert "verb 'does-not-exist' unknown" in capsys.readouterr().err


def test_run_shell_mirrors_captured_output(capsys: pytest.CaptureFixture[str]) -> None:
    """Mirror child stdout and stderr while preserving its exit code."""
    code = Dispatch.run_shell((
        sys.executable,
        "-c",
        "import sys; u.Cli.emit_raw('child-out\\n'); sys.stderr.write('child-err\\n')",
    ))

    captured = capsys.readouterr()
    assert code == 0
    assert "child-out" in captured.out
    assert "child-err" in captured.err


@pytest.mark.parametrize(
    ("alias", "canonical_verb"),
    [("gen", "build"), ("lint", "check"), ("rel", "ship"), ("validate", "val")],
)
def test_verb_alias_resolves_to_canonical_verb(
    registry: Dispatch.Registry, alias: str, canonical_verb: str
) -> None:
    """Promoted verb aliases must resolve to their canonical verb."""
    resolved = u.Tests.make_registry_resolve_verb(registry, alias)
    assert resolved.success, resolved.error
    assert resolved.value == canonical_verb


def test_header_what_matches_file_stem(registry: Dispatch.Registry) -> None:
    for verb in u.Tests.make_registry_verbs(registry):
        commands = u.Tests.make_registry_commands(registry, verb).unwrap()
        for what, cmd in commands.items():
            assert cmd.what == what == cmd.path.stem, f"{cmd.path}: what/stem mismatch"
            assert cmd.verb == verb == cmd.path.parent.name, (
                f"{cmd.path}: verb/dir mismatch"
            )


def test_make_surface_validation_succeeds(registry: Dispatch.Registry) -> None:
    assert u.Tests.make_registry_verbs(registry), "no verbs discovered"
    assert Dispatch.main(("--validate-surface",)) == 0


def test_target_env_overrides_makeflags_cli_values(
    capsys: pytest.CaptureFixture[str],
) -> None:
    keys = (
        c.Tests.MAKE_SURFACE_VALIDATE_ENV,
        c.Tests.MAKE_WHAT_PARAM,
        "CHECK_GATES",
        "MAKEFLAGS",
    )
    original = _snapshot_env(keys)
    try:
        os.environ[c.Tests.MAKE_SURFACE_VALIDATE_ENV] = c.Tests.MAKE_DISPATCH_ENV_VALUE
        os.environ[c.Tests.MAKE_WHAT_PARAM] = "pyrefly"
        os.environ["CHECK_GATES"] = "lint"
        os.environ["MAKEFLAGS"] = " -- CHECK_GATES=lint"

        assert Dispatch.main(("check",)) == 0

        output = capsys.readouterr().out
        assert "SURFACE-VALIDATE: make _check_default CHECK_GATES=pyrefly" in output
    finally:
        _restore_env(original)


def test_docs_fix_opt_in_reaches_private_docs_target(
    capsys: pytest.CaptureFixture[str],
) -> None:
    keys = (
        c.Tests.MAKE_SURFACE_VALIDATE_ENV,
        c.Tests.MAKE_WHAT_PARAM,
        "DOCS_PHASE",
        "FIX",
    )
    original = _snapshot_env(keys)
    try:
        os.environ[c.Tests.MAKE_SURFACE_VALIDATE_ENV] = c.Tests.MAKE_DISPATCH_ENV_VALUE
        os.environ[c.Tests.MAKE_WHAT_PARAM] = "all"
        os.environ["DOCS_PHASE"] = "fix"
        os.environ["FIX"] = "1"

        assert Dispatch.main(("docs",)) == 0

        output = capsys.readouterr().out
        assert "SURFACE-VALIDATE: make _docs DOCS_PHASE=fix FIX=1" in output
    finally:
        _restore_env(original)


def test_status_reaches_private_status_target(
    capsys: pytest.CaptureFixture[str],
) -> None:
    keys = (c.Tests.MAKE_SURFACE_VALIDATE_ENV, c.Tests.MAKE_WHAT_PARAM)
    original = _snapshot_env(keys)
    try:
        os.environ[c.Tests.MAKE_SURFACE_VALIDATE_ENV] = c.Tests.MAKE_DISPATCH_ENV_VALUE
        os.environ[c.Tests.MAKE_WHAT_PARAM] = "all"

        assert Dispatch.main(("status",)) == 0

        output = capsys.readouterr().out
        assert "SURFACE-VALIDATE: make _status" in output
    finally:
        _restore_env(original)


def test_clean_without_apply_stays_dry_run(capsys: pytest.CaptureFixture[str]) -> None:
    keys = (c.Tests.MAKE_APPLY_PARAM, c.Tests.MAKE_WHAT_PARAM)
    original = _snapshot_env(keys)
    try:
        os.environ.pop(c.Tests.MAKE_APPLY_PARAM, None)
        os.environ[c.Tests.MAKE_WHAT_PARAM] = "all"

        assert Dispatch.main(("clean",)) == 0

        output = capsys.readouterr().out
        assert "DRY-RUN: nenhuma mutacao executada." in output
        assert "make clean WHAT=all" in output
    finally:
        _restore_env(original)


@pytest.mark.parametrize(
    ("verb", "what", "target", "requires_apply", "env_updates"),
    [
        ("clean", "all", "_clean_default", True, ()),
        ("coordination", "all", "_coordination", False, ()),
        ("status", "all", "_status", False, ()),
        ("ship", "all", "_rel", True, ()),
        ("ship", "rel", "_rel", True, ()),
        ("ship", "pr", "_pr", True, ()),
        (
            "ship",
            "tag",
            "_tag",
            True,
            (("DRY_RUN", "1"), ("TAG", "surface-validation")),
        ),
        ("ship", "push", "_push", True, (("DRY_RUN", "1"),)),
    ],
)
def test_release_status_coordination_routes_reach_private_targets(
    capsys: pytest.CaptureFixture[str],
    verb: str,
    what: str,
    target: str,
    requires_apply: bool,
    env_updates: tuple[tuple[str, str], ...],
) -> None:
    keys = (
        c.Tests.MAKE_SURFACE_VALIDATE_ENV,
        c.Tests.MAKE_WHAT_PARAM,
        c.Tests.MAKE_APPLY_PARAM,
        "DRY_RUN",
        "MESSAGE",
        "TAG",
    )
    original = _snapshot_env(keys)
    try:
        os.environ[c.Tests.MAKE_SURFACE_VALIDATE_ENV] = c.Tests.MAKE_DISPATCH_ENV_VALUE
        os.environ[c.Tests.MAKE_WHAT_PARAM] = what
        if requires_apply:
            os.environ[c.Tests.MAKE_APPLY_PARAM] = c.Tests.MAKE_DISPATCH_ENV_VALUE
        else:
            os.environ.pop(c.Tests.MAKE_APPLY_PARAM, None)
        for key, value in env_updates:
            os.environ[key] = value

        assert Dispatch.main((verb,)) == 0

        output = capsys.readouterr().out
        assert f"SURFACE-VALIDATE: make {target}" in output
    finally:
        _restore_env(original)


def test_ship_save_runs_python_command_directly(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """ship/save is implemented in Python and does not route through a Make target."""
    keys = (
        c.Tests.MAKE_SURFACE_VALIDATE_ENV,
        c.Tests.MAKE_WHAT_PARAM,
        c.Tests.MAKE_APPLY_PARAM,
        "MESSAGE",
    )
    original = _snapshot_env(keys)
    try:
        os.environ[c.Tests.MAKE_SURFACE_VALIDATE_ENV] = c.Tests.MAKE_DISPATCH_ENV_VALUE
        os.environ[c.Tests.MAKE_WHAT_PARAM] = "save"
        os.environ[c.Tests.MAKE_APPLY_PARAM] = c.Tests.MAKE_DISPATCH_ENV_VALUE
        os.environ["MESSAGE"] = "chore: surface validation"

        assert Dispatch.main(("ship",)) == 0

        output = capsys.readouterr().out
        assert "SURFACE-VALIDATE:" in output
        assert "scripts.cmd.ship.save" in output
        assert "make _save" not in output
    finally:
        _restore_env(original)


def _registry_command_or_raise(
    registry: Dispatch.Registry, verb: str, what: str
) -> Dispatch.Command:
    result = u.Tests.make_registry_command(registry, verb, what)
    if result.failure:
        raise Dispatch.RegistryError(result.error or "command unknown")
    return result.value
