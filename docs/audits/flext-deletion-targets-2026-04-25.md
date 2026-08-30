# FLEXT Deletion-Target Catalog — Phase 2.4 (A-TS)

<!-- TOC START -->
- Section 1 — Pattern violations (Phase 2.1)
  - 1.1 — Tier-whitelist (banned-lib imports outside flext-core)
  - 1.2 — Silent-failure violations
  - 1.3 — Codegen census (namespace violations)
- Section 2 — Upstream-symbol duplicates (Phase 2.3)
- Section 3 — Service-responsibility duplicates
- Section 4 — Pre-existing complexity (Phase 2.5 exit-gate)
- [Bugs surfaced during audit (informational)](#bugs-surfaced-during-audit-informational)
- [Phase 2.4 exit gate](#phase-24-exit-gate)
<!-- TOC END -->

**Generated**: 2026-04-25
**Workspace**: `/home/marlonsc/flext`
**Baseline**: ruff 0, pyrefly 0 across 33 projects (Phase 2.0d gate)
**LOC baseline**: 354,880 LOC across 2,317 files (`/tmp/flext-loc-baseline-phase2-*.txt`)

This catalog is the contract for Phase 3 surgical deletions. Every entry below is a Phase 3 candidate; the user gate at
the end of this document MUST pass before Phase 3 begins.

## Section 1 — Pattern violations (Phase 2.1)

Pattern audits run via `python -m flext_infra validate <verb>` — outputs harvested via in-process API where the CLI
route was empty by design. Three audit categories produced concrete violation lists:

### 1.1 — Tier-whitelist (banned-lib imports outside flext-core)

7 violations total. Pattern: bare `import yaml` / `import orjson` / `import pydantic_settings` outside the flext-core
allowlist.

| # | File | Banned lib |
| --- | ------ | ------------ |
| 1 | `flext-cli/src/flext_cli/_utilities/yaml.py` | `yaml` |
| 2 | `flext-cli/src/flext_cli/typings.py` | `yaml` |
| 3 | `flext-core/tests/unit/test_enforcement.py` | `pydantic.warnings` *(test fixture; possibly intentional)* |
| 4 | `flext-target-oracle-wms/tests/integration/test_oracle.py` | `orjson` |
| 5 | `flext-target-oracle-wms/tests/unit/test_workflow.py` | `orjson` |

**Phase 3 action** : route every banned-lib import through the appropriate `flext-core` facade ( `u.Yaml.*` , `u.Json.*`
, `m.Settings` ). Per AGENTS.md §2.7 abstraction-boundary law.

Source: `/tmp/phase2-tier-whitelist-violations.txt`. Re-run via:

```bash
python -m flext_infra validate tier-whitelist --workspace /home/marlonsc/flext
```

### 1.2 — Silent-failure violations

116 violations. Three sub-kinds: `silent-failure-except` (exception branch returns sentinel), `silent-failure-guard` (
`Result` failure branch swallowed), `silent-failure-unwrap-or` ( `unwrap_or({})` hides failure).

Top offending modules (by violation count):

- `flext-cli/_utilities/`: 12 sites — `json.py`, `options.py`, `toml.py`, `yaml.py`
- `flext-core/_utilities/` : 11 sites — `checker.py` , `domain.py` , `enforcement_collect.py` , `guards_*.py` ,
  `parser_targets.py` ; `flext-core/result.py`
- `flext-infra/_utilities/`: 16 sites — `docs_api.py`, `docs_generate.py`, `iteration.py`, `policy.py`, `rope_*.py`
- `flext-infra/refactor/` + `validate/`: 7 sites
- `flext-ldif/_utilities/` + `services/`: 12 sites
- `flext-quality/docs/core/`: 4 sites

**Phase 3 action**: per site, choose one of three remediation paths:

1. Convert to `r.fail(reason, exception=exc)` propagation (preferred — surfaces the failure to the caller).
2. Add a justification comment if the silence is intentional (e.g., best-effort cleanup) and route the silence through a
   centralized helper so the pattern is auditable.
3. Convert `unwrap_or` to explicit `.recover(...)` chains where the fallback value is a real domain decision, not a
   hidden failure.

Source: `/tmp/phase2-silent-failure-violations.txt`. Re-run via in-process API (CLI text mode hides the violation list).

### 1.3 — Codegen census (namespace violations)

111 violations across 32 projects (51 fixable via `codegen auto-fix`).

Top offenders:

| Project | Violations | Fixable |
| --------- | ------------ | --------- |
| flext-core | 34 | 21 |
| flext-plugin | 10 | 6 |
| flext-cli | 8 | 0 |
| flext-infra | 7 | 0 |
| flext-ldif | 7 | 2 |
| flext-target-ldap | 7 | 0 |
| flext-target-oracle | 6 | 1 |
| flext-dbt-ldap | 5 | 1 |
| flext-tests | 5 | 4 |
| flext-api | 4 | 4 |
| flext-auth | 4 | 4 |
| flext-oracle-wms | 4 | 3 |

**Phase 3 action**: run `python -m flext_infra codegen auto-fix --apply` at workspace scope to land the 51
auto-fixable violations; the remaining 60 require human triage. ~~Note: the CLI route currently crashes
(`u.Cli.output_message_payload` missing in `flext-cli/services/output.py:38`) — the in-process API works.
Bug ownership: flext-cli maintainer / A-CH execution-pattern hub remit.~~ *(Resolved 2026-06-27:
`u.Cli.output_message_payload` is available and `FlextCliOutput.display_message` runs without error.)*

Source: `/tmp/phase2-codegen-census.txt`.

## Section 2 — Upstream-symbol duplicates (Phase 2.3)

The canonical primitive `FlextInfraRefactorCensus.parent_alias_collisions(report)` is now available (Phase 2.3
deliverable):

```python
from pathlib import Path
from flext_infra import FlextInfraRefactorCensus

census = FlextInfraRefactorCensus(
    workspace=str(Path("/home/marlonsc/flext")),
    projects=["flext-cli"],  # or omit for workspace
    include_local_scopes=False,
)
report = census.execute().unwrap()  # Rope walk — slow (~minutes per project)
collisions = census.parent_alias_collisions(report)
for obj, parent_paths in collisions:
    u.Cli.print(
        f"{obj.kind} {obj.name} @ {obj.file_path}:{obj.line} — {len(parent_paths)} parents"
    )
```

The method:

- Builds a parent inventory by importing the 8 upstream packages ( `flext_core` , `flext_cli` , `flext_tests` ,
  `flext_infra` , `flext_web` , `flext_meltano` , `flext_observability` , `flext_quality` ) and walking `c/m/p/t/u`
  aliases at depth 1, filtering to `type` instances whose `__module__` starts with `flext_` . Verified: **269 unique
  flext-class names** in inventory (smoke-tested).
- Iterates the workspace census report's per-project objects, skipping flext-core (no self-collision), filtering private
  names, and matching `obj.name` against the inventory.
- Returns `((Object, parent_paths), …)` sorted by collision-surface descending.

**Why no full-workspace results in this catalog** : `FlextInfraRefactorCensus.execute()` performs reference-counting per
object via Rope, which takes >120s per consumer project. Running it across all 16 consumer projects would take ~hours.
Phase 3 verbs that consume a Phase 2.4 catalog row will invoke this primitive on demand at the affected scope (one
project / one module at a time) — which is the design intent.

**Phase 3 action template** (per upstream-duplication finding):

1. Identify the consumer's local symbol via `parent_alias_collisions` for the affected scope.
2. Verify the parent symbol's API is a strict superset of the consumer's local definition.
3. Delete the local definition + rewrite all consumers to the parent alias by running:

   ```bash
   python -m flext_infra refactor accessor-migrate \
       --workspace . \
       --project <consumer> \
       --module <consumer.module> \
       --target-alias <parent.path>
   ```

4. Verify net-negative LOC delta and 0 ruff + 0 pyrefly post-change (verb's safety gate enforces this).

## Section 3 — Service-responsibility duplicates

**Deferred to Phase 4** ( `flext-infra Unified Execution Reorganization` ). Section 3 requires the ownership-mapping
audit in Task 4.1, which is BLOCKING on user confirmation per the plan. Capturing it here would prejudge ownership
decisions across `flext-core` , `flext-cli` , `flext-infra` , `flext-quality` , `flext-meltano` that the user must
approve.

The Phase 4 audit produces the canonical "concern → owner / duplicate / action" table at
`docs/architecture/unified-execution-audit.md` .

## Section 4 — Pre-existing complexity (Phase 2.5 exit-gate)

`make val VALIDATE_GATES=complexity,docstring` against `flext-infra` flags 7 methods at radon E/F complexity.
Pre-existing (Phase 2.0d zero-baseline already had them). Phase 3 decomposition candidates — each entry is one refactor
target:

| File | Method | Rating | Notes |
| ------ | -------- | -------- | ------- |
| `_utilities/deps_path_sync.py:299` | `FlextInfraUtilitiesDependencyPathSync.execute` | E | Likely splittable along the per-project loop |
| `_utilities/namespace.py:183` | `FlextInfraUtilitiesCodegenNamespace.policy` | F | Highest complexity in repo — strong decomposition candidate |
| `_utilities/rope_imports.py:161` | `FlextInfraUtilitiesRopeImports.relocate_from_import_aliases` | E | Multiple Rope code-paths braided together |
| `_utilities/discovery.py:340` | `FlextInfraUtilitiesDiscovery.resolve_parent_constants_mro` | E | MRO-walk decision tree |
| `_utilities/docs_api.py:206` | `FlextInfraUtilitiesDocsApi.public_contract` | F | Doc-generator branching |
| `codegen/fixer.py:96` | `FlextInfraCodegenFixer._fix_project` | E | Per-project transformation orchestrator |
| `deps/detector_runtime.py:32` | `FlextInfraDependencyDetectorRuntime.run` | F | Detector dispatch tree |

**Phase 3 action** : each entry is a self-contained decomposition. Per the user's strict reuse directive (
`feedback_strict_ssot_dry_yagni_rootmost.md` ), the decomposition MUST consume existing primitives (
`FlextInfraUtilitiesProtectedEdit` , `FlextInfraRefactorSafetyManager` , `u.Infra.projects()` ,
`u.Infra.iter_matching_files` , etc.) rather than introducing new helpers. Where two methods share a sub-routine,
extract the shared piece to flext-core or flext-infra `_utilities/` (most-root namespace) and consume it from both —
eliminating the duplication that drives the high complexity.

## Bugs surfaced during audit (informational)

Not a deletion target, but surfaced for ownership routing:

1. ~~ **`python -m flext_infra codegen census` CLI crashes** —
   `AttributeError: type object 'FlextUtilities' has no attribute 'Cli'` at
   `flext-cli/src/flext_cli/services/output.py:38` . In-process `FlextInfraCodegenCensus().run()` works. A-CH or
   flext-cli maintainer.~~
   *(Resolved 2026-06-27: `u.Cli.output_message_payload` is present and the CLI route no longer crashes.)*
2. **A-CH draft files in `flext-infra/refactor/`** — `catalog_loader.py` references missing
   `EnforcementAstGrepFixSource.handler` attribute; `_enforcement_harvest.py` has subprocess hygiene + import-ordering
   errors. Logged as conflict C11 in `~/.claude/plans/AGENT_COORDINATION.md` .

## Phase 2.4 exit gate

Before Phase 3 begins, the user MUST review:

- [ ] Section 1 violations are accurate (re-run verbs to spot-check if needed).
- [ ] Section 2 deferral is acceptable (full census walk is per-project on demand in Phase 3).
- [ ] Section 3 deferral to Phase 4 is acceptable.
- [ ] User confirms the Phase 3 deletion-target priorities (e.g., silent-failure first vs tier-whitelist first vs
  codegen auto-fix first).

Phase 3 begins only after explicit user "go".
