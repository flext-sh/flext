"""Behavior-pinning contract tests for the scripts command framework.

These tests pin the public behavior of the registry-driven Make dispatcher.
They import only the public namespace (`scripts.dispatch.Dispatch`).
"""

from __future__ import annotations

import pytest

from flext_tests import u
from scripts.dispatch import Dispatch


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


def test_known_mutating_command_declares_apply(registry: Dispatch.Registry) -> None:
    push = u.Tests.make_registry_command(registry, "ship", "push").unwrap()
    assert push.mutates is True
    assert any(p.name == "APPLY" for p in push.params), (
        "mutating command must declare APPLY param"
    )


def test_known_readonly_command(registry: Dispatch.Registry) -> None:
    check_all = u.Tests.make_registry_command(registry, "check", "all").unwrap()
    assert check_all.mutates is False
    assert check_all.domain == "quality"


def test_unknown_verb_raises(registry: Dispatch.Registry) -> None:
    with pytest.raises(Dispatch.RegistryError):
        _registry_command_or_raise(registry, "does-not-exist", "all")


def test_unknown_what_raises(registry: Dispatch.Registry) -> None:
    with pytest.raises(Dispatch.RegistryError):
        _registry_command_or_raise(registry, "check", "no-such-what")


def test_header_what_matches_file_stem(registry: Dispatch.Registry) -> None:
    for verb in u.Tests.make_registry_verbs(registry):
        commands = u.Tests.make_registry_commands(registry, verb).unwrap()
        for what, cmd in commands.items():
            assert cmd.what == what == cmd.path.stem, f"{cmd.path}: what/stem mismatch"
            assert cmd.verb == verb == cmd.path.parent.name, (
                f"{cmd.path}: verb/dir mismatch"
            )


def _registry_command_or_raise(
    registry: Dispatch.Registry,
    verb: str,
    what: str,
) -> Dispatch.Command:
    result = u.Tests.make_registry_command(registry, verb, what)
    if result.failure:
        raise Dispatch.RegistryError(result.error or "command unknown")
    return result.value
