# ADR-014 — Family Part Shape Law and Rope-Driven Codemod Rules

<!-- TOC START -->
- [Context](#context)
- [Decision](#decision)
  - [1. Family directory and part-class law](#1-family-directory-and-part-class-law)
  - [2. Declarative Rope rules (one YAML file per rule)](#2-declarative-rope-rules-one-yaml-file-per-rule)
  - [3. Shared change cycle (Rope replication)](#3-shared-change-cycle-rope-replication)
  - [4. Centralized backup cycle](#4-centralized-backup-cycle)
  - [5. Gate alignment (one law, two engines)](#5-gate-alignment-one-law-two-engines)
- [Consequences](#consequences)
- [Verification contract](#verification-contract)
- [References](#references)
<!-- TOC END -->

- **Status:** Accepted and active
- **Date:** 2026-09-09
- **Target line:** FLEXT `0.12.0-dev`, with `0.13.0` as the forward baseline.
- **Scope:** Every internal FLEXT package with the five private families
  (`_constants/`, `_typings/`, `_protocols/`, `_models/`, `_utilities/`):
  their internal layout, the declarative Rope rule format that governs
  structural rewrites, the shared semantic change cycle in `flext-infra`, and
  the namespace/codemod gate alignment. Third-party forks stay outside FLEXT
  architecture (fleet boundary, `flext-law`).
- **Tracking:** the active branch-matched Bead (`flext-joe2x` at authoring).
- **Complements:** ADR-005 (config/settings SSOT), ADR-010 (unified
  standardization via codegen), ADR-012 (config/settings canonical pattern),
  `flext-law` (facade and import law).
- **Operator basis:** operator directives of 2026-09-09 (this session): flat
  part declarations, no pure namespace wrappers, hoist-not-alias, rules in
  dedicated folders as one YAML file per rule driving the dedicated Rope
  engine, changes replicated through the common Rope cycle, and the
  centralized workspace backup cycle.

## Context

The namespace gate (`flext-infra`, `validate/namespace_validator.py`) requires
every member package to declare the five private families, each beginning with
`base.py`, and every canonical facade to compose its private family through a
nested namespace with multiple inheritance. Members drifted from that law:
flat facet files without families, orphan top-level helper classes (for
example a private `_Materialization` StrEnum declared beside its part class),
and pure namespace-wrapper children (a base-less class whose body only groups
constants or classes, such as a `class Dbt:` layer inside a part). Hand-fixing
such shapes member by member is unscalable and produces one-off rewrites that
do not replicate to consumers.

The fleet already owns the required machinery: the ADR-010 codemod cascade
(detection rules shipped one per file, applied through `make mod`
until a guarded fixed point), the shared Rope change cycle
(`FlextInfraUtilitiesRopeRuntime` change primitives plus `rope_project.do(changes)`
in `_utilities/rope_class_move.py` and `_utilities/namespace_moves.py`, which
replicate every change to all referencing modules), and the centralized
execution pipeline `FlextInfraUtilitiesSafety`
(`backup_files → transform → validate → cleanup | rollback`, the same cycle
behind the workspace timestamped `.bak` artifacts).

## Decision

### 1. Family directory and part-class law

1. Each package declares the five private families, each family begins with
   `base.py` (namespace-gate law, unchanged).
2. A family part file (any module inside a family directory) declares its part
   class — a top-level class named `<FlextStem><FamilySuffix><Part>` — and
   nests its content **directly**: entities only, one level deep. Entities are
   Pydantic models (`m.*Model` presets), enums (StrEnum/Enum), protocols
   (`Protocol`), and behavior classes (bodies containing function
   definitions, such as `Service`/`Transformer` helper classes).
3. A top-level class other than the part class in a family part file is an
   **orphan** and is forbidden: it is hoisted into the part class as a public
   nested entity (PascalCase, underscore stripped), never kept beside an
   alias.
4. A direct child of the part class that has no entity base and no function
   definitions — a base-less, data-only or class-only grouping — is a **pure
   namespace wrapper** and is forbidden. Its members are flattened one level
   up (prefix-merge on collision), and the wrapper is deleted. Consumer
   attribute chains (`X.Wrapper.Y` → `X.Y`) are rewired package-wide.
5. Facade roots (`constants.py`, `typings.py`, `protocols.py`, `models.py`,
   `utilities.py`) keep the canonical shape: inherit the canonical layer
   letter(s), nest exactly one domain namespace composing at least two part
   classes through multiple inheritance, and end with the canonical bottom
   alias (`c`/`t`/`p`/`m`/`u`).

### 2. Declarative Rope rules (one YAML file per rule)

Structural shape rules for the Rope engine live in dedicated folders under
`src/flext_infra/codemod/rope_rules/<rule-module>/*.yml`, one file per rule,
mirroring the ast-grep rule file style of the ADR-010 cascade:

```yaml
id: hoist-family-orphan-class
severity: error
message: "top-level orphan class in a family part; hoist as a public nested entity"
files: ["**/_[constants|models|typings|protocols|utilities]/**/*.py"]
rope:
  action: hoist_into_part_class
  rename: { strip_underscore: true, case: pascal }
```

Rules are parsed once at the boundary through the canonical YAML owner
(`u.Cli.yaml_*`, flext-cli) into typed Pydantic models (`m.Infra` rope-rule
models); the loader fails loud on any invalid rule. Detection thresholds and
file globs are rule data — never hardcoded detector branches.

### 3. Shared change cycle (Rope replication)

Family-shape rewrites run inside the `make mod` circuit
(`FlextInfraCodemodBatchApply`), as a phase beside
`FlextInfraCodemodSemanticApply`, and extend the common base rather than
introducing a second path:

- Detection consumes the typed rules and produces typed findings.
- Rewrites extend `FlextInfraUtilitiesRopeRuntime` /
  `FlextInfraUtilitiesRefactorNamespaceMoves` primitives so every mutation is
  a Rope `Change` applied via `rope_project.do(changes)` — replicating the
  change to every referencing module — followed by the existing rewritten-file
  normalization.
- The fixed-point, no-progress guard, and final validation of the mod circuit
  (canonical formatting, zero Ruff/Pyrefly/LSP diagnostics) govern the phase
  identically.

### 4. Centralized backup cycle

Every mutating family-shape execution wraps its file set in the centralized
workspace cycle `FlextInfraUtilitiesSafety.execute_safely` (backup → transform
→ validate → cleanup | rollback). Ad-hoc write paths, private backup schemes,
and repository-wide rollback remain forbidden.

### 5. Gate alignment (one law, two engines)

The namespace validator (`validate/_namespace_rules`) enforces the same two
laws at `make check` time — orphan top-level classes and pure namespace
wrappers in family part files — with message text consistent with the rule
files, so detection-only and check-time findings never diverge. Canonical
platform exceptions stay encoded once (`NAMESPACE_PLATFORM_FACADE_SINGLETONS`,
`cli.py` `main` entrypoint, `api.py` composition-root singleton).

## Consequences

- Members converge on one machine-checkable shape; the first execution target
  is `flext-dbt-oracle-wms` (its `_constants` enumeration hoist, `Dbt` wrapper
  flatten, and three consumer rewires).
- Consumer paths flatten with the law (`c.DbtOracleWms.Dbt.PROJECT_NAME` →
  `c.DbtOracleWms.PROJECT_NAME`); no external member imports the target
  package, and the mod circuit's fixed point proves the rewire.
- Rules, detector, and gate text share one vocabulary; adding a new structural
  law means adding one YAML rule plus its typed action — no engine fork.

## Verification contract

- `make mod` reaches the guarded fixed point with zero pending
  findings on the target member.
- `make check` passes the namespace and codemod gates on the member
  with the family law active; `make test` stays green through the
  canonical testmon cache.
- `make gen` proves the generation fixed point after any export-affecting
  move; zero residue (no `.bak`, no orphan files) remains in the tree.

## References

- ADR-005 (config/settings SSOT), ADR-010 (unified standardization), ADR-012
  (config/settings canonical pattern).
- `flext-law` skill — facade composition, import direction, `make mod`
  structural-rewrite law.
- `flext-infra`: `validate/namespace_validator.py`,
  `validate/_namespace_rules/*`, `codemod/batch_apply.py`,
  `codemod/semantic_apply.py`, `codemod/sgconfig.yml`,
  `_utilities/safety.py`, `_utilities/rope_core.py`,
  `_utilities/rope_class_move.py`, `_utilities/namespace_moves.py`.
