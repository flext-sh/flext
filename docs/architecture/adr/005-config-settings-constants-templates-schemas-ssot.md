# ADR-005: Universal Config / Settings / Constants / Templates / Schemas SSOT

## Status

Proposed

**Tracking:** beads epic `mro-wkii` (phases `mro-wkii.1`–`mro-wkii.7`).
Governance alignment (`mro-wkii.7`) lands before implementation Phase 1
(`mro-wkii.2`) per operator decision.

## Context

Configuration knowledge is fragmented across every FLEXT package and the
`~/.ai-hub` control plane. The same fact is expressed in multiple, competing
forms:

- **Execution parameters** (ports, timeouts, spawn tables, routing maps,
  policy thresholds) are hardcoded inside `_constants/*.py` as large literal
  `MappingProxyType` / `frozenset` / `tuple` structures, mixed with genuine
  defaults.
- **Settings** (env-overridable runtime knobs) and **config** (declarative
  execution parametrization) are conflated in the same files and models.
- **Large constant blobs** (routing tables, agent-surface maps, blocked-command
  lists, rendered file bodies) live as Python literals instead of data.
- **Schemas** exist ad hoc (`~/.ai-hub/schema.json`, `~/.ai-hub/config/models.json`)
  with no single validation entry point.
- **Templates** for generated artifacts are inconsistent: `flext-infra` uses
  Jinja2, `flext-core` declares `jinja2` as a dependency but never imports it,
  and `~/.ai-hub` keeps `*.tmpl` string templates outside any engine.

This blocks enforcement: there is no single place a rule can point at to say
"this parameter must live in `config/`, not hardcoded in `_constants/`".

The reference control plane `~/.ai-hub` already proved the target shape
(`config/aihub.toml` SSOT → `AiHubConfig.Runtime.load` → typed `m.AiHub.RuntimeConfig`
→ `settings.AiHub.config`), but it still carries large hardcoded structures in
`_constants/mcp.py` (`MCP_ROUTING_CLIENT_SPECS`, `SKIP_DIRS`,
`MCP_ROUTING_GENERATED_AGENT_FILES`) that this ADR eliminates.

### Established constraints (verified 2026-07)

- `flext-core` declares `jinja2` but its `src/` never imports it
  (deptry-unused). `flext-infra` and `flext-quality` are the only real Jinja2
  users.
- Runtime dependency direction is `flext-infra → flext-cli → flext-core`, with
  no cycle. **flext-core must never import flext-cli or flext-infra at runtime**
  (examples/scripts/tests only).
- 31/31 packages depend on `flext-core`; 22/30 depend on `flext-cli`.
- `flext-cli` already owns `u.Cli.yaml_*`, `u.Cli.toml_*`, `u.Cli.json_*` and
  file helpers.
- `flext-infra/_enforcement/engine.py` is the workspace enforcement engine.

## Decision

Adopt one layered SSOT for parametrization, split cleanly into five concerns,
each with one owner and one directory convention.

### 1. Five concerns, one owner each

| Concern | What it holds | Directory / surface | Owning layer |
|---|---|---|---|
| **constants** | Default values that never need to be passed; invariants | `src/<pkg>/_constants/*.py` → `c.*` facade | package (base: `flext-core`) |
| **config** | Declarative **execution parametrization** (ports, timeouts, spawn/routing tables, policy) | `config/*.yaml` (+ sibling `schemas/`) | package `config/` dir |
| **settings** | Env-overridable runtime knobs derived from config + constants | `src/<pkg>/settings.py` → `FlextSettings` subclass | package |
| **templates** | Any large string / generated body | `templates/*.j2` (Jinja2 via `flext-cli`) | `flext-cli` engine |
| **schemas** | Validation contracts for every config file | `schemas/*.schema.json` (one per config, same base name) | package `schemas/` dir |

### 2. Config directory is the only parametrization source

All execution parametrization comes from the `config/` directory and its files.
**No schema, config source, or parametrization may live outside `config/`.**
Runtime code loads from `config/` through the `flext-cli` config loader; it must
not read parameters from any other location.

`aihub.toml` (the ai-hub general config) is renamed to `config/ai-hub.yaml`, and
the previously-monolithic file is split into separate YAML files per domain
(`agents.yaml`, `mcp.yaml`, `workspace.yaml`, `skills.yaml`, …), each with a
matching schema in `schemas/` (same base name). This mirrors the already-accepted
ai-hub **ADR-0009** (`~/.ai-hub/docs/adr/0009-config-ssot-yaml-split-and-router-only-mcp.md`),
which is the reference instance of this workspace-wide standard.

### 3. Config ≠ Settings (hard split)

- **config/** = declarative execution parametrization (this ADR's subject).
- **settings** = the subset that flows into `FlextSettings` for env override.

The part of config that flows to settings is factored into a **separate file**
in the same config-directory convention (e.g. `config/settings.yaml`), so
config and settings never mix in one file.

### 4. Constants are the default source; large structures are generated

- `_constants/*.py` holds **only** scalar defaults and true invariants
  (`StrEnum`, `IntEnum`, `Literal`, `frozenset`, `Final`) — the values a caller
  does not need to pass.
- **Large or derived structures are never hardcoded.** They are generated
  dynamically by a private `_constants` builder from the `config/` files, so the
  generalized methods consume generated structures, never literals.
- Hardcoding a large structure (routing map, spawn table, blocked list) inside
  `_constants/` is a **defect blocked immediately** by enforcement.

### 5. Layered engine ownership (no runtime cycle)

- **Namespace convention (flat + prefix, no sub-namespaces).** All FLEXT namespaces stay
  flat — `c/t/p/m/u.*` in flext-core (base), `c/t/p/m/u.<Namespace>.*` in consumers. The
  config group is separated by **prefix only**: `config_` for methods/utilities on `u.*`
  and `Config` for classes/models/protocols on `c/t/p/m`. Never a `Config`/`config`
  sub-namespace object (use `u.config_load`, not `u.config.load`; `p.ConfigRecord`, not
  `p.Config.Record`).
- **flext-core (Layer 0, runtime-minimal).** Provides only what core itself needs to
  self-configure, through its own `c/t/p/m/u`: minimal `u.config_load` / `u.config_merge` /
  `u.config_env_override` (stdlib `tomllib` + `string.Template`, **no Jinja2**),
  `FlextSettings`, `FlextConstants`, and the base config/schema **contracts** (`p.Config*`,
  `m.Config*`, `t.Config*`). `jinja2` is **removed** from `flext-core` dependencies
  (declared-but-unused).
- **flext-cli (Layer 1, universal base for all projects).** Imports the core primitives and
  **amplifies** them into the universal file/config/template/schema engine:
  `u.Cli.template_render` (Jinja2, `StrictUndefined`), `u.Cli.config_load` /
  `u.Cli.config_load_dir` (multi-format YAML/TOML/JSON + env-override + merge; YAML is the
  authoring default), and `u.Cli.schema_validate` (JSON Schema). All FLEXT packages and
  `~/.ai-hub` consume these; `flext-cli` owns all file, output, CLI, formatting, and
  advanced-interface routines.
- **flext-infra (Layer 2, generation + enforcement).** Consumes the `flext-cli`
  base for generation and hosts the enforcement rules that keep the pattern
  honest.

### 6. Enforcement is data-driven and fail-closed

`flext-infra/_enforcement` gains rules (registered in
`c.ENFORCEMENT_CATALOG`) that fail the workspace gate when:

- a large literal structure (mapping/sequence over a threshold) is declared in
  `_constants/`,
- a parameter is read from outside the `config/` directory,
- a template body is inlined as a Python string instead of a `templates/*.j2`,
- a config file lacks a matching `schemas/*.schema.json`,
- config and settings are mixed in one file.

## Consequences

### Positive

- One provenance per fact: defaults in `_constants`, parametrization in
  `config/`, env override in `settings`, big strings in `templates`, validation
  in `schemas`.
- Generalized methods consume generated structures; adding a routing entry or a
  spawn kind is a data edit, not a code branch.
- `flext-core` stays runtime-minimal and Jinja2-free; the universal engine has a
  single owner (`flext-cli`); no runtime cycle.
- Enforcement can finally point at a concrete rule for "no hardcoded structures"
  and "config only under `config/`".

### Negative

- Hard cut across 31 packages + `~/.ai-hub`: constants shrink, config files
  appear, some `_constants` modules become generators.
- `flext-core` and `flext-cli` gain new public config/template/schema surface
  that must be documented and enforced before consumers migrate.
- Every package must grow a `config/` dir + sibling `schemas/` before its parameters
  can move out of `_constants`.

## Alternatives Considered

- **Keep parametrization in `_constants/`.** Rejected: no place to enforce
  "config lives in config/", and large literals keep leaking into code.
- **Put the template engine in `flext-core`.** Rejected: forces a real Jinja2
  runtime dependency on the layer that 31/31 packages import, for a capability
  only 22/30 need; violates YAGNI and the runtime-minimal core rule.
- **Per-package bespoke loaders.** Rejected: re-fragments the exact problem this
  ADR removes; the loader must be one `flext-cli` primitive.
- **TOML-only config.** Rejected: the ai-hub general config is moving to YAML
  (`ai-hub.yaml`) split per domain; the loader stays multi-format but YAML is the
  authoring default.

## Implementation Notes

Realized through the migration plan
[`docs/architecture/config-ssot-migration-plan.md`](../config-ssot-migration-plan.md).

Foundation-first, evidence per phase (`make check` exit 0 + `make test` green +
atomic commit + bead):

1. `flext-core` minimal config/schema contracts + remove unused `jinja2`.
2. `flext-cli` universal `render_template` / `config_load` / `yaml_validate_schema`.
3. `flext-infra` enforcement rules + `c.ENFORCEMENT_CATALOG` rows.
4. `~/.ai-hub` reference migration (`aihub.toml` → `config/ai-hub.yaml` split;
   `_constants` large structures → generated; `~/.ai-hub` ADR-0008 rewritten to
   conform).
5. Propagate to FLEXT packages, one bead each, config-dir + schemas + generated
   constants, deletions in the same change (net LOC negative).

## References

- [ADR-001: Railway-Oriented Programming with r[T]](./001-railway-oriented-programming.md)
- [ADR-002: v0.13.0 Platform Baseline](./002-v0-13-0-platform-baseline.md)
- [ADR-003: Workspace tooling distributed by `~/.ai-hub`](./003-workspace-tooling-hub-distribution.md)
- [ADR-004: Generic Make Framework Owned by `flext-tests`](./004-generic-make-framework-in-flext-tests.md)
- `~/.ai-hub/docs/adr/0008-unified-agent-deploy-controlplane.md` (rewritten to conform)
- `~/.ai-hub/docs/adr/0009-config-ssot-yaml-split-and-router-only-mcp.md` (reference instance of this standard)
