# ADR-016: Settings/Config Singleton Contract, Performance and SSOT Alignment

## Status

PROPOSED (2026-09-15) — accepted for planning; execution assigned to a dedicated
session via epic bead and [epic plan](../../plans/2026-09-15-flext-settings-config-ssot-epic.md).
This ADR becomes `Accepted` only when that session lands the full contract with
runtime evidence.

## Context

`FlextSettings` (flext-core `src/flext_core/_settings.py`) and `FlextConfig` are
layer-0 SSOT foundations consumed by every FLEXT package and by external
consumers (`~/ai-hub`, `~/cosmos-main` apps `cosmos-charts`/`cosmos-gitops`,
`~/algar-*`, `~/gruponos-*`). The contract is critical because it is:

- **Namespaced**: nested models per domain (`settings.OracleWms.*`,
  `config.oracle_wms.*`) with registry-driven namespace composition.
- **Inherited and incrementally composed**: each library extends the settings
  tree (`TestsFlextOracleWmsSettings(FlextOracleWmsSettings, FlextTestsSettings)`),
  and every consumer layer adds namespaces on top.
- **Singleton-based everywhere**: facades `c,t,p,m,u` and every member package
  export module-level `settings`/`config` singletons built at import time.

### Defect evidence (2026-09-15 session)

The singleton is enforced through `__new__` interception
(`_settings.py:226-238`): when `cls._instance` already exists, ANY pydantic
allocation path that reaches `cls.__new__` receives the cached singleton object
and pydantic re-initializes it in place. Empirically (flext-oracle-wms):

- Full unit suite under randomized order: 7/8 seeds red; deterministic order
  green; isolated pairs green — classic late-pollution coupling.
- `tests/unit/test_config_module.py:114` fails with the payload of whichever
  settings-building test ran earlier (`''` from `test_out_of_range_scalars`,
  `https://example.com` from `test_custom_values`).
- `clone()` performs its final `model_validate(copied, from_attributes=True)`
  OUTSIDE the `singleton_disabled()` window, re-entering the factory semantics.

Consequences: cross-test state pollution, nondeterministic suites, hidden
mutation channel through "innocent" `model_validate` calls, and unclear
identity semantics between module-level `settings` export and
`fetch_global()`.

### Performance and SSOT debt

- Every access path re-validates/re-copies nested models (`_merge_overrides`
  dumps+revalidates per clone) — measurable overhead for hot-path consumers.
- Consumers duplicate resolution logic locally instead of consuming the typed
  SSOT surface (violations of ADR-015 R1 in external projects).
- `.env` discovery (`_resolve_env_file`) consults the filesystem per
  construction; no identity-verified caching for the composed inheritance
  chains.

## Decision

1. **Single construction authority.** The singleton lifecycle is owned
   exclusively by the classmethods (`fetch_global`, `update_global`,
   `reset_for_testing`, `clone`). Allocation (`__new__`) must NOT intercept
   pydantic construction paths; registration happens explicitly where the
   singleton is created. Construction aliases (module-level
   `settings = FlextXSettings(...)`) must resolve to the same identity the
   classmethods serve, or be converted to `fetch_global()` at the owner.
2. **Pollution-free derived copies.** `clone`/`fetch_global(overrides=...)`
   validate inside `singleton_disabled()` for the entire derivation, never
   re-entering factory semantics, never mutating the source instance.
3. **Declared identity contract.** The observable laws are: repeated
   `fetch_global()` returns one initialized instance; `model_validate` never
   touches singleton state; `clone` never aliases its source; `update_global`
   atomically replaces. Tests encode exactly these invariants (before/after
   capture), never prior-state assumptions.
4. **Performance floor.** Nested override merge and namespace resolution are
   cached per composed class with identity-verified invalidation; no
   filesystem/env re-resolution on hot reads; benchmarks (cProfile evidence)
   accompany the change.
5. **SSOT alignment of clients.** Fleet members and external consumers
   (`ai-hub`, `cosmos-main` apps, `algar-*`, `gruponos-*`) consume the typed
   facade only (ADR-015 R1); local re-implementations of env/config resolution
   are exterminated in the same cutover, with migration through `make gen`
   projections — never hand-edited duplicates.

## Consequences

- Test suites become order-independent without per-file singleton hacks.
- One migration cycle must transport all construction alias sites
  (fleet + external) in the same landing; partial cutovers are defects.
- The dedicated session must prove: flext-core contract tests, fleet pytest
  across randomized seeds (≥8 consecutive green), gates ×2 idempotent, and
  runtime import identity checks in each external consumer.
