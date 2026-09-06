# Types

<!-- TOC START -->
- [Rules](#rules)
- [Where the aliases live](#where-the-aliases-live)
<!-- TOC END -->

**The canonical typing surface of the FLEXT workspace.**

FLEXT has one typing contract, exposed through the `t` facade of every
package. `flext-core` defines the base aliases; consumer packages extend
their own `t` facade by MRO and rebind the local alias — there is no second
typing surface anywhere.

## Rules

- **Never `Any` or bare `object`.** Composite types use `t.*` aliases
  (`t.MappingOf[K, V]`, `t.SequenceOf[T]`, …); nullability is explicit with
  `| None` on the outside.
- **Modern forms only** (Python 3.13+): builtin generics, `X | Y` unions,
  `type` statements, structural protocols.
- **Data contracts are models**: `dict`, `TypedDict`, `NamedTuple`,
  `dataclass`, and JSON-typed payloads are forbidden as owned data
  structures — use `m.*` Pydantic 2-way models instead.
- **Declaration only**: the `t` facet holds aliases and contracts, never
  behavior; anything that computes lives in `u`.

## Where the aliases live

The always-current alias inventory is generated from the code, not maintained
by hand:

- Per package: `docs/api-reference/generated/` (public API and module pages).
- Workspace summary: [API overview](../api-reference/generated/overview.md).

If a needed alias is missing, it is added to the owning `t` facet — never
redeclared locally in a consumer module.
