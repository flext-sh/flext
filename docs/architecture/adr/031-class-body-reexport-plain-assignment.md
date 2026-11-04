# ADR-031 — Class-Body Type Re-Exports Use Plain Assignment, Never PEP 695

<!-- TOC START -->

- [Context](#context)
- [Decision](#decision)
- [Consequences](#consequences)
- [Rejected alternatives](#rejected-alternatives)
- [Verification contract](#verification-contract)

<!-- TOC END -->

- **Status:** ACCEPTED — 2026-11-02; codifies measured runtime behavior on
  CPython 3.13, not a style preference. Ratification by the operator is welcome;
  the runtime evidence is decisive either way.
- **Date:** 2026-11-02
- **Scope:** every FLEXT member and consumer that re-exports a module-level class
  (or any object) as a class-body attribute — notably the test-utilities namespace
  pattern (`class Tests(...)` with re-export aliases) in `flext-core`
  `tests/utilities.py` and its analogues in other members.
- **Complements:** ADR-014 (family part shape), ADR-018 (generator declarations
  law — generated re-exports follow the same rule), ADR-021 (lint repair channel —
  `UP040` fixes must not violate this law).
- **Measured evidence:** `flext-core` batch 1 of the strict ruff/pyright plan
  (audit `docs/auditoria/RUFF_PYREFLY_FLEXT_CORE_BATCH1_20261102.md` in the
  `gruponos/merges` workspace), bead `dc_recon-ob4`.

## Context

`UP040` (`non-pep695-type-alias`) flags legacy `X: TypeAlias = Y` and proposes the
PEP 695 `type X = Y` statement. For module-level aliases of types, that conversion
is safe and correct. For **class-body re-exports written as self-referential
aliases** — `class Tests: X: TypeAlias = X`, where the right-hand `X` is a
module-level import re-exported into the class namespace — the conversion is not
safe.

Runtime measurement on CPython 3.13:

- `class Bar: Mod: TypeAlias = Mod` → `Bar.Mod is Mod` is `True`. The class
  attribute **is** the re-exported class object; consumers can use it as a value
  (instantiate, read class attributes such as `HANDLER_TYPES`, `isinstance`).
- `class Baz: type Mod = Mod` → `Baz.Mod is Mod` is `False`. The class attribute
  becomes a lazy `TypeAliasType` wrapper whose right-hand side resolves
  self-referentially inside the class body; `Baz.Mod.HANDLER_TYPES` fails. The same
  happens with an aliased import on the right-hand side: the wrapper is still a
  `TypeAliasType`, not the class object.

Real consumers in the fleet access these re-exports as values, e.g.
`u.TestsFlextFlextHandlers.HANDLER_TYPES` in
`flext-core/tests/unit/test_handlers_validation_context.py`. A fleet-wide
`UP040` autofix that converted these class-body re-exports would silently replace
class objects with lazy wrappers and break every such consumer.

## Decision

1. **Class-body re-exports are plain assignments.** A class-body attribute that
   re-exports a module-level object is written `X = X` (right-hand side resolving
   to the module-level import), with no `TypeAlias` annotation and no PEP 695
   `type` statement. This preserves the exact runtime semantics: the class
   attribute **is** the re-exported object.
2. **`TypeAlias` is for type aliases, not class re-exports.** Using
   `X: TypeAlias = Y` to re-export a class is a misuse that `UP040` correctly
   flags; the fix is to drop the annotation (plain assignment), not to convert to
   PEP 695.
3. **PEP 695 `type` statements are for module-level (or genuinely lazy) type
   aliases only.** They are never used to re-export a class object through a class
   namespace.
4. **Lint repair respects this law.** When `make fix` (ADR-021 channel) or a
   codemod closes `UP040`, it must not convert class-body re-export assignments
   into PEP 695 statements. Rules/codemods that perform this conversion are
   `unfixable` for the class-body re-export pattern.

## Consequences

- `UP040` closures in class-body re-export sites are plain-assignment rewrites,
  which are runtime-neutral and type-checker-neutral (the right-hand side resolves
  to the module-level import in both runtime and strict checkers).
- The fleet keeps one re-export mechanism for class namespaces; no
  `TypeAliasType` wrapper leaks into consumer code that uses re-exported classes as
  values.
- Generators (ADR-018) that emit class-body re-exports emit plain assignments.

## Rejected alternatives

- Blind `UP040` autofix to PEP 695 in class bodies — proven by runtime measurement
  to replace class objects with self-referential lazy wrappers and break value
  consumers (`Bar.Mod is Mod` → `True` vs `Baz.Mod is Mod` → `False`).
- Aliased imports (`from m import X as _X` + `type X = _X`) — still produces a
  `TypeAliasType` wrapper, so value consumers still break; it only hides the
  self-reference, not the semantic change.
- Deleting the re-exports as "dead code" — consumers access them through the class
  namespace; deletion is a public-surface break, not a lint fix.

## Verification contract

- Runtime proof stays green: for a class-body re-export `X = X`,
  `Outer.X is <module-level X>` is `True` and `Outer.X.<class attribute>` resolves.
- `ruff check` closes `UP040` at every class-body re-export site with the
  plain-assignment form; no `type` statement appears inside a class body for
  re-exports.
- `pyright`/`pyrefly` report no new diagnostics on the rewritten sites.
- Consumers that read re-exported classes as values (e.g. `.HANDLER_TYPES`) keep
  passing their tests.
