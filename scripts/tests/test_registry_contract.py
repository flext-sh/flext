"""Behavior-pinning contract tests for the scripts command framework.

These tests pin the *current* public behavior of the dispatch/registry so the
planned `scripts/lib` extraction (monolithic `dispatch.py` -> cohesive modules)
can be verified to preserve semantics. They import only the public surface
(`scripts.dispatch`); after the split that module stays the import seam.
"""

from __future__ import annotations

import pytest

from scripts.dispatch import (
    DEFAULT_COMMAND,
    Registry,
    RegistryError,
    discover,
)


@pytest.fixture(scope="module")
def registry() -> Registry:
    return discover()


def test_discover_succeeds_and_validates(registry: Registry) -> None:
    # discover() runs Registry.validate() internally; reaching here means green.
    assert registry.verbs(), "no verbs discovered"


def test_every_verb_has_default_all_command(registry: Registry) -> None:
    for verb in registry.verbs():
        assert DEFAULT_COMMAND in registry.commands(verb), (
            f"verb {verb!r} missing WHAT={DEFAULT_COMMAND}"
        )


def test_single_domain_per_verb(registry: Registry) -> None:
    for verb in registry.verbs():
        domains = {cmd.domain for cmd in registry.commands(verb).values()}
        assert len(domains) == 1, f"verb {verb!r} has multiple domains: {domains}"


def test_known_mutating_command_declares_apply(registry: Registry) -> None:
    push = registry.command("ship", "push")
    assert push.mutates is True
    assert any(p.name == "APPLY" for p in push.params), (
        "mutating command must declare APPLY param"
    )


def test_known_readonly_command(registry: Registry) -> None:
    check_all = registry.command("check", "all")
    assert check_all.mutates is False
    assert check_all.domain == "quality"


def test_unknown_verb_raises(registry: Registry) -> None:
    with pytest.raises(RegistryError):
        registry.command("does-not-exist", "all")


def test_unknown_what_raises(registry: Registry) -> None:
    with pytest.raises(RegistryError):
        registry.command("check", "no-such-what")


def test_header_what_matches_file_stem(registry: Registry) -> None:
    for verb in registry.verbs():
        for what, cmd in registry.commands(verb).items():
            assert cmd.what == what == cmd.path.stem, f"{cmd.path}: what/stem mismatch"
            assert cmd.verb == verb == cmd.path.parent.name, (
                f"{cmd.path}: verb/dir mismatch"
            )
