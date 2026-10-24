# ADR-027 — Facade Single-Owner Law

<!-- TOC START -->

- [Context](#context)
- [Decision](#decision)
- [Derivation of the owner family](#derivation-of-the-owner-family)
- [Detection in make gen](#detection-in-make-gen)
- [Rewiring in make mod](#rewiring-in-make-mod)
- [Diagnostics](#diagnostics)
- [Fixtures and verification](#fixtures-and-verification)
- [Rollout](#rollout)

<!-- TOC END -->

- **Status:** PROPOSED — operator order 2026-10-24; design under review by the
  flext-infra cutover owner before implementation
- **Date:** 2026-10-24
- **Scope:** every facade family (`c`, `t`, `p`, `m`, `u` and the operational families)
  of every internal FLEXT project, enforced by flext-infra in `make gen` and `make mod`
- **Complements:** ADR-014 (family shape), ADR-018 (generator declarations: derive,
  never list; generators propagate, never compensate), ADR-023 (repair phases)
- **Tracking:** `flext-vjj1s.11`

## Context

Operator order 2026-10-24 (verbatim): "esses tipos de problema tem que ser tratado por
flext-infra em make gen/mod tb, não tem que ser o caso apenas disso, tem que ser sempre
dessa infra".

The trigger: flext-core re-exports the same upstream object from several facade
families. Measured with ast-grep over the fleet on 2026-10-24:

| Object | Exported by | Consumers |
| --- | --- | --- |
| `pydantic.ValidationError` | `c`, `t` (alias), `m` | 200 use `m.ValidationError` |
| `pydantic.Field` | `m`, `u` | 52 use `u.Field` |
| `AliasPath`, `AliasChoices`, `StringConstraints`, `Discriminator`, `FailFast`, `SerializeAsAny`, `InstanceOf` | `t`, `m` | 31 use `m.AliasPath`; others 1-6 |
| validator and serializer decorators, `computed_field` | `m`, `u` | 1-2 each |

The import direction (`c → t → p → m → u`, reverse imports `TYPE_CHECKING`-only) is
already correct; ownership is not. Two owners of one object drift independently and
make the consumer choose, which is exactly what a facade exists to prevent.

## Decision

1. Every object exported by a facade family has exactly one owner family.
2. The owner is derived from the object's kind (below). No mapping list.
3. `make gen` detects every object exported by more than one family, or by a family that
   does not own its kind.
4. `make mod` removes each non-owner export and rewires every consumer in the fleet to
   the owner, with import alignment, idempotently.
5. A case that cannot be rewired mechanically emits a diagnostic stating where, why and
   how to fix. It still fails the gate; a diagnostic is guidance, not a waiver.

## Derivation of the owner family

The kind is read from the resolved object, never from its name:

| Kind predicate (on the resolved object) | Owner |
| --- | --- |
| subclass of `BaseException`; warning class; sentinel instance; version constant; `StrEnum` subclass | `c` |
| `TypeAliasType`; `Annotated` metadata marker instance or class used only in annotations | `t` |
| `typing.Protocol` subclass | `p` |
| pydantic/pydantic-settings model or settings base; `ConfigDict`; `Field`/`PrivateAttr`; validator/serializer decorators and `Annotated` validator/serializer classes | `m` |
| any other callable (functions, adapters, factories) | `u` |

- Families and letters come from `u.Infra.facade_families()`.
- Object identity and alias resolution come from the python-model owner `u.Infra`
  introduced by the flext-infra cutover (G.1), whose types are declared in `t.Infra`.
  Griffe is confined to those two facade owners (ADR-028); detection consumes only
  `u.Infra`/`t.Infra`, never `griffe` itself. Alias resolution to the upstream object
  makes "one object exported by N families" a single query.
- If a predicate ever needs a mapping row, it lives in `config/tooling.yaml`, typed, not
  in code.

## Detection in make gen

The facade planner (`_utilities/codegen_facades.py`) already enumerates each family's
exports. It adds one pass:

1. Group every exported attribute by its resolved upstream path (`u.Infra` python model).
2. For each group, derive the owner from the kind predicate.
3. Record a finding for every member exported by a non-owner family and for every group
   with more than one exporting family.

Findings are typed models (`m.Infra.FacadeOwnershipFinding`: object path, owner family,
offending family, facade module, line). `make gen` fails while findings exist and are
not rewired; it never compensates by re-exporting.

## Rewiring in make mod

One Rope semantic phase, ordered after `facade-base` and before `private-import`, reuses
the existing import-alignment / constant-consumers machinery and its contract rows in
`config/rules/rope/contracts.yaml`:

1. For each finding, rewrite every consumer reference `<family>.<Name>` resolving to the
   object into `<owner>.<Name>`, adding the owner import when absent and dropping an
   import left unused.
2. Remove the export from the non-owner facade module.
3. Re-run the detection on the result; the phase is idempotent (a second pass changes
   nothing) and is checked by the existing semantic residue pass.

Publication constraint (flext-infra cutover owner, 2026-10-24): the phase publishes its
edits only through the shared `u.Cli.publish_file_changes` owner (`m.Cli.FileChange`
under `u.Cli.file_changes_lock`). It uses no semantic transaction, receipts or
`source_consumption` state, and no authenticated reads from
`_utilities/_rope/project.py`; those are retired by the publication cutover.

## Diagnostics

Emitted when rewiring is not mechanical (the consumer shadows the owner letter locally,
the object is re-bound under another name, or the owner family has no facade in that
project):

```text
facade-single-owner: flext_ldap/_models/entry.py:41
  m.ValidationError resolves to pydantic.ValidationError, owned by family c
  why: an object has one facade owner; m re-exports an exception
  fix: import c from the project facade and use c.ValidationError
```

## Fixtures and verification

- Rope contract fixture: a three-family toy package exporting one object from `m` and
  `u`, consumers in another package; after `make mod`, only the owner exports it, all
  consumers use the owner, and a second `make mod` produces no diff.
- Gen fixture: duplicated and misplaced exports produce the exact findings.
- Runtime proof: import every rewired facade from a neutral directory.
- Fleet proof: `make gen` twice and `make mod` twice with no diff; `make check` green.

## Rollout

1. After the flext-infra publication cutover lands (`[coord] landed`): implement
   detection on the `u.Infra` python model and the Rope phase.
2. Apply to flext-core (pydantic facades first), then the fleet in dependency order.
3. The pydantic-specific single owners (ValidationError → `c`, Field → `m`, annotation
   markers → `t`, runtime functions → `u`) fall out of the generic derivation; nothing
   pydantic-specific is hard-coded.
