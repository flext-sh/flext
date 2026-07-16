---
name: flext-architecture-layers
description: >-
  Route FLEXT declarations, configuration, runtime behavior, enforcement, and
  structural codemods to their canonical project and facade owners. Use when
  adding or moving modules, changing cross-project dependencies, reviewing MRO
  composition, or deciding whether work belongs to core, cli, infra, or an
  agent provider; do not use to impose a universal project scaffold.
---

# FLEXT architecture ownership

Derive the exact module layout from the target project's declarations,
configuration, public facade, and `pyproject.toml`. This skill routes ownership;
it does not define a fixed repository tree.

## Project ownership

- `flext-core` owns shared runtime contracts and facades plus the canonical
  enforcement identities, metadata, routing, and descriptors.
- `flext-cli` owns CLI-facing configuration, template, and schema boundary
  capabilities built on core contracts.
- `flext-infra` consumes core and cli, owns declarative enforcement payloads and
  schemas, and executes validation/refactor workflows.
- `.agents/skills/flext-codemod-astgrep` owns FLEXT structural rule declarations
  and provider metadata. The generic preview/apply engine is managed by
  ai-hub.
- A domain project owns only its domain declarations, validated configuration,
  adapters, behavior, and public facade. Do not copy framework machinery into
  it.

Keep runtime package direction `flext-infra -> flext-cli -> flext-core`. Never
introduce a reverse runtime import to reuse an implementation.

## Module ownership

1. Put fundamental names and contracts in the owning `c`, `t`, `p`, or `m`
   declaration surface; put validated configuration in `config`/`settings`.
2. Put behavior in the existing focused private responsibility owner.
3. Keep the public domain module as a thin MRO/composition facade when multiple
   focused mixins implement that responsibility.
4. Compose public operations in the project's established service/API surface.
5. Update all consumers atomically and remove the superseded path. Do not keep
   old and new owners, aliases, wrappers, or fallbacks together.

Do not create a module merely because this list names a possible layer. Prove
the need from current declarations and consumers first.

## Procedure

1. Read `pyproject.toml`, the package root exports, and the candidate canonical
   owner.
2. Classify each artifact as declaration, validated configuration, behavior,
   enforcement payload, provider procedure, or validator.
3. Move it to the single owner above and replace duplicated prose/code with a
   reference.
4. Check dependency direction and private-module reachability.
5. Run the target repository's native static and runtime gates.

Tests, fixtures, snapshots, and examples validate the owner; they never define
the declaration, configuration, or fundamental rule. Correct stale validators
when they conflict with those sources.

For facade composition details, load
[../flext-mro-namespace-rules/SKILL.md](../flext-mro-namespace-rules/SKILL.md).
