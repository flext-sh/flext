# Constants Declarations Remediation Plan — settings→config→c chain, total bead

absorption, fleet-wide idempotence

Execution flow: **0** governance bootstrap (rules, census, bead absorption, epic) →
**1** dedicated worktree → **2** flext-core (settings/config first, then constants
shape) → **3** flext-cli → **4** flext-tests → **5** flext-infra + fleet → **6**
fleet-wide idempotence proof. Strictly sequential; zero source mutation in phase 0.

**Scope fence**: this plan owns ONLY the constants/settings/config/namespace theme. The
general check failures currently being remediated by the concurrent check-failures lane
(banned `dict`/`object` annotations, reverse runtime imports, service locators, LOC
caps, pyrefly/mypy/test failures) are OUT of scope here — see §8. Where both lanes touch
the same file, fix-forward applies: this lane consumes whatever typed surface the other
lands and never duplicates its fixes.

---

## 0. Governance bootstrap

### 0.1 Authority load (read, in order, before any bead action)

1. `~/.agents/AGENTS.md` — universal core (evidence, fix-forward, beads-as-truth,
   canonical commands, rules 7/19 gate coverage of `examples/`/`scripts/`/`tests/`).
2. Root `AGENTS.md` — P0 config/settings test law; universal governance 1–24; beads
   block.
3. `.agents/skills/flext-law/SKILL.md` — facade law, `make mod` ownership,
   rules-as-data, verb discipline.
4. ADRs (`docs/architecture/adr/`): **005** (SSOT ownership table, LAW1/LAW2, §5
   deletion-first), **010** (phases, §3a settings dirs), **014** (family part shape,
   rope_rules YAML, gate alignment), **015** (consumer consumption law), **007**
   (worktree transactions), **001** (r[T] railway). **ADR-012** is cited by
   `flext-core/AGENTS.md` and ADR-014 but MISSING from the ADR dir (verified 2026-09-11)
   → file `adr-012-restore` doc-drift bead in 0.4.
5. Skills: `make-check`, `verification-loop`, `beads`, `beads-orchestrator`,
   `beads-organization`, `fix-forward-collaboration`, `fleet-lane-discipline`,
   `wip-beads` (batch classification of open/claimed/blocked/deferred).

### 0.2 Rules of engagement (every task in every phase is gated against ALL of these)

**Chain and namespace law (src/):**

- **R1 Chain**: runtime imports only downward on
  `settings → config → c → t → p → m → u → base → services → api → cli`
  (`flext-infra/_constants/namespace.py::NAMESPACE_LAYER_ORDER`; NS-IMPORT rank check).
  Reverse = TYPE_CHECKING-only. Carve-out: settings/config owners may runtime-import
  declaration facades `t`/`m`/`u` (never `p`, never `c`, never operational
  `r/e/x/h/d/s`).
- **R2 Namespaced inheritance (src)**: five private families
  `_constants/`/`_typings/`/`_protocols/`/`_models/`/`_utilities/`, each starting
  `base.py`; part class `<FlextStem><FamilySuffix><Part>` nesting entities one level
  deep; orphan top-level classes forbidden (hoist); pure namespace wrappers forbidden
  (flatten/relocate); facade roots inherit the layer letter, nest exactly one domain
  namespace composing ≥2 part classes by multiple inheritance, end with bottom alias
  `c/t/p/m/u` (ADR-014 §1, NS-STRUCT).
- **R3 Constants ownership**: immutable invariants → `c` (`_constants/*`);
  env-overridable knobs → `settings` fields; validated policy → `config/*.yaml`. `c` MAY
  consume settings/config (forward); any `c` value duplicated in settings/config is a
  duplicate-owner defect → SSOT is the lower layer, `c` copies deleted, consumers
  rewired (ADR-005 §1). Module-level `UPPER_CASE = literal` outside `_constants/` is a
  violation (bare assignments included — extend detector). Magic literals route to `c`
  (existing enforcement rule).
- **R4 Typing/Pydantic**: no `Any`/`object`/`dict` annotations — `t.*`/`p.*` only;
  `T | None` never `Optional`; Pydantic-2-way only (`model_validate`/`model_dump`);
  every model extends an `m.*` preset; `model_rebuild` forbidden — complete the model
  with a runtime import at the declaring module; annotations resolve at their declaring
  owner (NS-CONTRACT; correction memory `pydantic.model_rebuild`).
- **R5 Layer purity**: `_settings.py` imports only stdlib + pydantic/pydantic-settings
  (flext-core owns pydantic; other members import through facades); `_config.py` adds
  only its `._settings` owner (+ `yaml` in flext-core); zero project-facade imports
  beyond the R1 carve-out; docstrings of settings/config owners must not contradict R1
  (current `_config.py` "siblings that never expose each other" is doc drift → fix in
  same slice).

**Scope law (applies EVERYWHERE, not only src/):**

- **R6 Gate coverage**: `make check`/`make fix`/`make fmt`/`make mod` and the rules of
  R3/R4 cover `src/`, `examples/`, `scripts/`, and `tests/` with the SAME rigor; blanket
  `per-file-ignores`/excludes hiding violations there are prohibited; only per-rule
  test-idiom exceptions (e.g. `S101`) are allowed (root AGENTS.md rules 7 and 19,
  operator law 2026-07-20).
- **R7 tests/examples/scripts specifics**: tests exercise ONLY public facades with
  `tm` + canonical `c/t/p/m/u`, no mocks/`patch`, unified `conftest.py`, typed fixtures;
  project-owned values in tests/examples/scripts must be consumed via
  `c.*`/`config.*`/`settings.*` — a literal that mirrors a config/settings/c-owned value
  is a P0 defect (fix the test, never freeze config);
  `from tests|examples|scripts import …` inside src is banned
  (`c.PATTERN_FORBIDDEN_FACADE_IMPORT`); scripts are thin command adapters.
  Namespaced-inheritance facts (R2) are src-scoped by the declared
  `[tool.flext.namespace].scan_dirs`; R6 keeps lint/type/constant/magic rules
  fleet-tree-wide.

**Engine and data law:**

- **R8 LAW1**: 100% of static enforcement rules live as Pydantic-validated data —
  enforcement rules in `flext-infra/config/*.yaml`; structural rope rules one YAML per
  rule in `src/flext_infra/codemod/rope_rules/<rule-module>/*.yml` (ADR-014 §2). Zero
  rule logic in Python; no list registries (decision `flext.no_list_registries` —
  discovery via live SSOT functions).
- **R9 LAW2**: rope-semantic only (`get_scope`/`get_attributes`/`PyName`);
  `import ast`/`ast.walk`/`get_ast()`-as-AST banned in the static path; one shared
  `rope_project` per run; fixes are `rope_project.do(changes)` with replication to every
  referencing module; every mutation wrapped in
  `FlextInfraUtilitiesSafety.execute_safely` (backup → transform → validate → cleanup |
  rollback).
- **R10 Verb ownership**: everything through root Make verbs from the workspace/worktree
  root; mutation only; NEVER `WHAT=`/`PROJECT=` on setup/gen/fix/fmt/check/test
  (flext-law) — the dispatcher governs all 31 members; a broken verb is fixed at its
  owner, never bypassed.
- **R11 Fixer/codemod ownership**: structural shape rewrites (orphan hoist, wrapper
  flatten/relocate, class placement) run ONLY inside the `make mod` circuit
  (`FlextInfraCodemodBatchApply`, fixed-point + fingerprint guard), as rope_rules
  YAML-driven phases beside `FlextInfraCodemodSemanticApply` (ADR-014 §3); rule-driven
  value cutovers follow the enforcement-fixer precedent (`classvar_relocation` in
  `FlextInfraRopeFixerAdapter`). No second engine, no per-project Python.
- **R12 P0 tests**: config/settings tests validate contracts for arbitrary valid values
  through the same typed SSOT the consumer receives; never freeze configured literals; a
  test breaking on a legitimate config change is a test defect.
- **R13 Evidence/truth**: every claim carries exact command, cwd, exit code, decisive
  output; warnings/skips/empty output are RED; first exception escapes raw; runtime
  behavior proven by importing/running the real artifact before tests encode it.
- **R14 Landing + worktree**: all work EXCLUSIVELY in the phase-1 dedicated worktree
  (main checkout read-only); one lane per bead; submodule branches per
  `fleet-lane-discipline`; landing = scoped commit → FF push → PR → resolved review →
  `merge --no-ff` into `0.12.0-dev` → gates rerun on merged SHA → runtime proof; never
  land local-green/PR-open (decision `flext.land_full_closure`).

### 0.3 Live census + total bead absorption (first mutation is bd-only, zero source)

**Census (record raw output in the epic bead before creating children):**

```bash
bd count       # totals by status
bd list --json # every non-closed bead: id, title, type, priority, status, assignee
bd ready --json
git worktree list
git submodule status   # expect 31 members per config/workspace.yaml (SSOT topology)
git status --porcelain # root baseline (~40 entries at 2026-09-11 snapshot — must be
adjudicated before landing)
```

Known snapshot facts (2026-08-31 `bd count`: total 2745 = open 405, in_progress 3,
blocked 2, deferred 6; beads live ONLY in the root DB — submodule `.beads/` hold config
only; stale worktrees found at `flext-infra/worktrees/torch-cooldown` and
`~/flext-infra-worktrees/`). This snapshot is evidence, NOT authority — the live query
decides.

**Absorption policy (operator authority, total):** this plan ABSORBS the whole
constants/settings/config/namespace theme — every bead that is open, claimed
(in_progress), blocked, or deferred whose subject matches the theme. Theme match = any
of: constants declaration/placement, namespace/facade shape, settings/config ownership
or purity, rope fixer/codemod, autogeneration of facet roots, class-nesting registries,
import law. Absorbing a claimed bead preserves the current actor's work products
(fix-forward: cite their commits/branches as evidence in the new child bead, never
discard), then closes the old bead. No theme bead survives outside this plan; non-theme
beads are left untouched.

**Theme absorption candidates (from 2026-09-11 research; final set = live query ∩
theme):**

| Bead | Snapshot state

             | Transported need → plan section
                                                                                       |

## | -------------------------------------------------------------------- |

## |

| | `flext-gv3oe` | open bug p1 — namespace gate hardcodes nested facade name `Infra`
(false positives fleet-wide)  
 | validator fix → §2.1 step 1

| | `flext-ywu2d` | open epic p1 — fleet hardening: namespace/loc-cap gate slices,
class-nesting-mappings extermination, slow-test budget | namespace/loc-cap slices +
registry extermination → §2.1 detectors + §2.0.2 rules; slow-test budget → re-file
standalone if still valid, else reject with reason | | `flext-2wjm.*` | open children of
ywu2d — class-nesting-mappings work | supersede with ywu2d (live-discovery rule R8
replaces the list registry) | | `flext-9avbt` | open feature p1 — autogenerate
`constants/typings/protocols/models/utilities.py` from `_<modulo>/*.py` subclasses |
facet-root generation from live family discovery feeds the `make gen` idempotence gate →
§5.4 codegen owner | | `flext-oja4.2` | open task p2 — map flext-core/flext-cli reuse
for c/t/p/m/u consolidation | consolidation happens via ownership adjudication → §2.0.1;
transport reusable analysis as linked evidence, close | | `flext-q7hjp` | **in_progress
(claimed)** — discover installed dependency public facades for private-import cutover |
absorb per total authority: preserve actor evidence, private-import fixer dependency →
§2.1 fixers; close after transport | | `flext-ssnc7.8`, `flext-faqbn`, `flext-5s0rj`,
`flext-4wrdx`-lineage | recent in_progress/open churn in logs (states unverified) |
classify by live theme match; absorb if theme, leave if not |

Disposition commands (after each critique is recorded in the epic description):

```bash
bd update --json < id > --claim # take ownership of claimed/abandoned lanes first
bd close "absorbed by flext-constants-remediation <epic-id> §<section>: <transported
need>" --json < id > --reason
bd dep add < child-id > blocks < absorbed-id > --json # only when execution order truly
depends on it
```

No bead closes without its need written into a plan section or explicitly rejected with
a recorded reason. Zero information destruction: reparent open children before closing a
parent (precedent: `flext-012-release-min` fold into `flext-1wjg1`).

### 0.4 Epic and child beads

```bash
bd create "Epic: constants declarations remediation + settings->config->c chain
conformance" \
  --description="Absorb and finish the constants/settings/config/namespace theme per
  plan .kilo/plans/1789144856683-constants-declarations-remediation-plan.md. Chain: \
  settings→config→c→t→p→m→u→base→services→api→cli. Absorbs ALL theme beads \
  (open/claimed/blocked/deferred) per operator authority. Exclusions: third-party \
  forks, gas-city." \
  --acceptance="Plan §6 all green: chain purity, zero duplication, R1–R14 compliance,
  make check/mod/test/gen idempotent fleet-wide, zero manual edits." \
  -t epic -p 1 --json
```

Children (sequential, each `--deps blocked-by` the previous; acceptance = phase gate
verbatim):

1. `core-chain-settings-config` — §2.0 · 2. `core-constants-shape` — §2.1 · 3.
   `cli-cycle` — §3 · 4. `tests-cycle` — §4 · 5. `infra-fleet-automation` — §5 · 6.
   `constants-format-idempotence` — §5.4. Doc-drift: `adr-012-restore` (p2,
   discovered-from epic). Operating rule: `bd update <id> --claim` before any file
   write/shell step; update after every repo-state change.

### 0.5 Dependency-chain law (enforced artifact)

Chain declared once in `NAMESPACE_LAYER_ORDER`; allowed runtime imports:

| Layer | May import at runtime

                       |

## | ---------------------------- |

| | `_settings.py`/`settings.py` | stdlib + pydantic(-settings) only (flext-core); +
declaration facades t/m/u for other members (carve-out)  
 | | `_config.py`/`config.py` | settings surface + `._settings` owner + t/m/u (never
c/p/operational) | | `_constants/*` (c) | settings + config singletons; t
TYPE_CHECKING-only; never m/u runtime | | t | c, config, settings · p:
TYPE_CHECKING-only t/m · m: c, t + config/settings, p TYPE_CHECKING · u: all below ·
base/services/api/cli: chain below, services inject via p |

Proofs required: config→settings lawful and real (`_config.py` imports `app_env_prefix`,
`platform_config_root`); c→settings/config forward (never flagged reverse);
duplicate-owner defect direction: SSOT = lower layer, `c` consumes.

Ownership adjudication table (every constant in the fleet): immutable protocol invariant
→ `c`; env/CLI-overridable knob → `settings`; validated policy/derived default →
`config/*.yaml`.

### 0.6 Evidence discipline

Exact command + cwd + exit code + decisive output for every gate; RED on
warnings/skips/empty; first exception escapes with raw traceback.

---

## 1. Dedicated worktree (mandatory, every agent)

1. **Worktree law**: every agent works ONLY in `~/flext-wt-constants` (branch
   `constants-remediation-0.12` off `0.12.0-dev`); main checkout `~/flext` read-only;
   one lane per bead; submodule branches branch-matched via `fleet-lane-discipline`
   (never detached); worktree transactions via ADR-007 owner; landing per R14.
2. ```bash
   git worktree add -b constants-remediation-0.12 ~/flext-wt-constants 0.12.0-dev
   ```
   Record path+branch in the epic bead.
3. Baseline: `make setup` → `make gen` → `make check` (root dispatcher, no PROJECT=) —
   record baseline findings; `make gen` ×2 byte-identical (non-idempotent generator =
   defect fixed at owner first).

---

## 2. flext-core — settings/config chain first, then constants shape

### 2.0 Chain work-stream (runs BEFORE constants shape; c composes on top of

settings/config)

**2.0.1 Owner adjudication (deletion-first, ADR-005 §5)** — rope-driven cutovers:

1. `ENV_FILE_DEFAULT`/`ENV_FILE_ENV_VAR` duplicated: `_constants/environment.py` ↔
   `_ENV_FILE_*` in `_settings.py`. Owner = `_settings.py` (chain bottom); delete
   `_constants` copies; rewire consumers via `settings.*` (layer-0 consumers import the
   settings owner module).
2. `ENV_PREFIX` ↔ `app_env_prefix()`: settings owns the derived policy; `c` keeps only
   a true protocol invariant, if any survives critique.
3. `_constants/config.py` CONFIG\_\_ defaults: classify via the adjudication table —
   loader-protocol invariants stay in `c` only if no `config/*.yaml` row can vary them;
   configurable ones move to config + typed `_config.py` fields, loader reads
   `config.*`.
4. `DEFAULT_APP_NAME`, `DEFAULT_TIMEZONE`: env-overridable candidates → settings fields;
   `c` copies deleted, consumers rewired. Zero old+new coexistence per cut.

**2.0.2 Validator increments (data only: R8 homes — enforcement rules →
`flext-infra/config/*.yaml`; gate text aligned with rule vocabulary):**

1. `settings-layer-purity` (R5); 2. `config-layer-purity` (R5); 3.
   `constants-chain-forward` — positive assertion that `_constants/*` runtime imports of
   config/settings are FORWARD (R1); 4. `constants-value-duplication` — rope-semantic
   literal-equality discovery between `_constants/*` bindings and settings/config owner
   fields; violation names both locations + adjudicated owner (live discovery, no
   lists); 5. settings/config docstring-vs-chain drift check. Out of lane:
   banned-annotation/service-locator/reverse-import REMEDIATION belongs to the
   check-failures lane — this work-stream adds only the constants-domain rules above
   (R4/R6 remain this plan's verification scope for constants rules in
   `examples/`/`scripts/`/`tests/`).

**2.0.3 Fixer increments (R9/R11 ownership):**

1. `rewire_constant_to_settings` — enforcement rope_fixer target: delete the
   `_constants` binding named by `constants-value-duplication`, rewrite every
   referencing module via `rope_project.do(changes)`, insert canonical consumption form
   (`settings.*`/`config.*` at runtime; settings-owner module import for layer-0
   consumers).
2. Out of lane: `dict[str, Any]` annotation retyping in settings/config is the
   check-failures lane's fix (NS-CONTRACT) — this plan only requires that lane's landed
   types to satisfy R4 when the duplication cutovers touch the same declarations.

**2.0.4 P0 by-construction tests (R12)** for adjudicated settings fields and config
models — contracts over arbitrary valid values (boundary, override, env-file
resolution), no frozen literals.

**2.0.5 Phase gate**: `make mod` fixed point (zero actionable + detection-only) →
`make check` green on the constants-domain rules (purity, chain-forward, duplication,
shape; overall check status recorded with lane attribution — the concurrent lane's
findings are baseline, not blockers) → `make test` green (testmon) → `make gen` ×2
byte-identical → `make mod` ×2 zero fixes → runtime proof consuming an adjudicated value
via `settings.*`/`config.*`.

### 2.1 Constants shape remediation (flext-core)

**Validator fixes first (flext-infra owner):**

1. `flext-gv3oe` root cause: `_facade_shape` nested-name derivation — derive from outer
   class + `FAMILY_SUFFIXES` (removes fleet-wide false positives on facade roots).
2. Operational re-export modules (`r/e/x/h/d/s` shape) exempt via
   `_is_functional_module` shape test — never a filename list; extend only if the shape
   test misses real cases (`decorators.py`, `handlers.py`, `lazy.py`).
3. `loose_object_detector`: flag base-less/method-less grouping classes outside family
   directories (multi-class files included).
4. `FlextInfraClassPlacementDetector._class_constants`: catch bare
   `UPPER_CASE = literal` outside `_constants/` (not only Final/collection forms).
5. Scan-scope conformance (R6/R7): production scan covers declared scope;
   lint/type/constant gates verified non-excluded for `examples/`/`scripts/`/`tests/`.

**Structural rope rules + fixers (R2/R11 — `make mod` circuit):** new
`codemod/rope_rules/family_shape/*.yml` (one per rule, ADR-014 §2 schema) + typed
actions beside `FlextInfraCodemodSemanticApply`:

- `hoist-family-orphan-class` — nest orphan into the part class (PascalCase, underscore
  stripped), rewire `X.Orphan` chains package-wide (targets:
  `FlextMroViolation`/`FlextSmellViolation` in `_constants/enforcement.py`; 5 grouping
  classes in `_constants/errors.py`).
- `flatten/relocate-namespace-wrapper` — flatten one level up or relocate to canonical
  `_<family>/` per nested-entity family; rewire imports.

**Constants-shape findings to zero (this lane only):** orphan classes in
`_constants/enforcement.py` (`FlextMroViolation`, `FlextSmellViolation`) and
`_constants/errors.py` (5 grouping classes); wrappers outside family dirs; bare
module-level constants. General check failures (`container.py` LOC cap, `dispatcher.py`
service locator, banned `dict` annotations, `_utilities/*` reverse imports) are OWNED BY
THE CHECK-FAILURES LANE — not this plan.

**Phase gate**: same sequence as 2.0.5.

---

## 3. flext-cli — same cycle (starts after both flext-core beads close)

1. Chain/purity validators run as-is (proven in 2.0) — expected findings limited to the
   constants domain; annotation/reverse-import remediation is the check-failures lane's
   work, out of scope here.
2. Shape: `utilities.py` nested-MRO false positive (killed by gv3oe fix — verify zero
   residual); orphan/wrapper findings → mod-circuit rope rules; bare module constants →
   classvar rules.
3. New constants-domain patterns become YAML rows at flext-infra (R8) — never
   per-project Python.
4. Gate sequence identical to 2.0.5, scoped to flext-cli.

---

## 4. flext-tests — same cycle (starts after cli bead closes)

1. Settings/config conformance if owners exist; R6/R7 verification is the headline: test
   trees under full constant/typing rigor without blanket ignores.
2. Known findings: `enforcement_plugin.py:17` module-level `SLOW_TIMEOUT_INI_OPTION`;
   `_utilities/_matchers/*.py` wrappers outside family dirs;
   `_fixtures/_enforcement_parts/config.py:13` placement.
3. P0 audit of test constants: any test literal mirroring config/settings/c-owned values
   becomes a by-construction read (R12).
4. Gate sequence identical.

---

## 5. flext-infra + fleet — complete automation (starts after tests bead closes)

1. **flext-infra self-cycle** (must fix itself with its own machinery): settings/config
   purity; `promoted/base.py:19-27` bare constants;
   `_enforcement/collection_base.py:17`, `_models/_git/identity.py:13`,
   `transformers/_tier0_transformer.py:15` wrappers; stale worktrees
   `flext-infra/worktrees/torch-cooldown`, `~/flext-infra-worktrees/*` adjudicated
   (evidence-only rule: prune via ADR-007 owner after capture).
2. **Members, strictly sequential, one bead each — the 31 from `config/workspace.yaml`
   (topology SSOT)**: flext-api, flext-auth, flext-cli✻, flext-core✻, flext-db-oracle,
   flext-dbt-ldap, flext-dbt-ldif, flext-dbt-oracle, flext-dbt-oracle-wms, flext-grpc,
   flext-infra✻, flext-ldap, flext-ldif, flext-meltano, flext-observability,
   flext-oracle-oic, flext-oracle-wms, flext-plugin, flext-quality, flext-tap-ldap,
   flext-tap-ldif, flext-tap-oracle, flext-tap-oracle-oic, flext-tap-oracle-wms,
   flext-target-ldap, flext-target-ldif, flext-target-oracle, flext-target-oracle-oic,
   flext-target-oracle-wms, flext-tests✻, flext-web (✻ = already done in phases 2–4).
   Per member: chain/purity validators → constants shape → `make mod` fixed point →
   `make check` (constants-domain rules green) → `make test` → `make gen` ×2 →
   `make mod` ×2 → runtime proof. Order: flext-cli first among consumers (already done),
   then meltano (Singer base), then taps/targets/dbt (thin drivers), then domain libs,
   then platform caps.
3. **Fleet gates**: root `make check`/`make mod` zero findings across all governed
   repositories.
4. **Format idempotence (§5.4 = `constants-format-idempotence` bead)**: `config/*.yaml`,
   `schemas/*.schema.json`, `templates/*.j2`, managed `pyproject.toml` sections,
   `.mise.toml`, Python source — each rendered/rewritten twice, byte-identical; any
   format needing hand-touching proves a generator/fixer defect → fix the owner (feeds
   `flext-9avbt` transported need: facet roots derived from live family discovery).

---

## 6. Completion criteria

- [ ] Phase 0: epic + children created/claimed; census recorded; ALL theme beads
      absorbed (open/claimed/blocked/deferred) with needs transported per section or
      rejected with recorded reason; `adr-012-restore` filed.
- [ ] All work in the dedicated worktree; zero writes to main checkout; landing per R14
      on every slice.
- [ ] R1–R14 provably honored (each gate green with evidence; LAW1 data homes used; no
      `PROJECT=`/`WHAT=` bypasses).
- [ ] Constants-domain gates green on all 31 members: zero
      shape/duplication/purity/chain-forward findings; gates cover src + examples +
      scripts + tests with no blanket ignores (general check-green is the check-failures
      lane's closure — tracked jointly, not a blocker of this plan's beads).
- [ ] `make mod` zero actionable + detection-only findings fleet-wide; second run = zero
      changes.
- [ ] `make gen` byte-idempotent fleet-wide and per member, across all declared formats.
- [ ] `make test` green everywhere (testmon); P0-compliant settings/config tests.
- [ ] Zero manual edits — every change from `make mod`/`make gen`/`make fix` with.
- [ ] No `.bak` residue, no orphan files, no shims; docstring drift corrected in-slice.

## 7. Rollback / stop condition

Same gate failing 3× identically → stop, record in bead, one precise question. Fixer
with wrong semantics → stop, fix the fixer at its owner, never hand-patch consumers.
Non-progressing `make mod` fingerprint → guard returns red with changes retained; never
discard shared work.

## 8. Out of scope

- **Check-failures lane (concurrent agent)**: banned `dict`/`object` annotations,
  reverse runtime imports, service locators, LOC caps, pyrefly/mypy/test failures —
  remediation owned there; this plan adds only constants-domain rules/fixers and adopts
  that lane's landed surfaces via fix-forward (no duplicated fixes, no lane blame).
- Third-party forks (ADR-008/009); `gas-city` (permanently deactivated); parallel lanes;
  new vendor dependencies; non-theme beads (left untouched, cited only as evidence).

---

## 9. Per-stage completion contract (HARD — operator law 2026-09-11)

A stage/phase is ONLY "concluded" when ALL of these hold, verified in order:

1. **Validation report**: decisive gates re-run against the EXACT merged content,
   recorded in the stage's bead (command, cwd, exit code, output, SHA).
2. **Publication proof**: every landed SHA is an ancestor of `origin/0.12.0-dev` — root
   commits via `git merge-base --is-ancestor <sha> origin/0.12.0-dev`; submodule commits
   via the same check INSIDE each submodule repo PLUS
   `git ls-tree origin/0.12.0-dev <member>` showing the gitlink at the merged SHA.
   Local-green or open-PR state is NEVER "concluded".
3. **Bead closed**: the stage's bead closes with the four-source evidence (bead notes,
   git history, measured gates, integrated code); remaining scope explicitly re-filed or
   kept in the successor bead.
4. **Report to epic**: consolidated stage report appended to `flext-s9bxq`
   (what/validation/publication/next).

### 9.1 Fix-forward absorption law (always applies)

- Every current authorized-repository change — regardless of provenance, age, or which
  lane's tree it appears in — is OWNED INPUT: re-read live state, attribute overlapping
  intent, preserve compatible contributions, integrate forward.
- Committed work from another actor found in pooled state: absorb by integrating the
  COMBINED result forward (merge/extend at the canonical owner); never revert, stash,
  reset, or discard.
- Another actor's UNPUSHED local work: PRESERVE in place untouched; do not publish on
  their behalf (bulk adoption of unmanifested work requires divergent-object
  adjudication); coordinate via board + beads.
- Worktree reality (measured 2026-09-11): submodule git storage is POOLED with the main
  checkout (`.git/modules/...`); concurrent actors can materialize/advance shared
  submodule trees. Consequence: lane isolation holds at the superproject branch, and
  **stage validation must always run in an isolated detached checkout at the exact
  merged SHA** (pattern: `git worktree add --detach <scratch> <sha>` +
  `PYTHONPATH=<detached>/src` ahead of the editable install), never against a
  possibly-mutated pooled tree.

### 9.2 Validation methodology (canon for every stage report)

```bash
# publication proof
git merge-base --is-ancestor <sha> origin/0.12.0-dev           # root commits
git -C <member> merge-base --is-ancestor <sha> origin/0.12.0-dev  # member commits
git ls-tree origin/0.12.0-dev <member>                          # gitlink == merged SHA
# content validation at the exact merged SHA (isolated)
git -C <member> worktree add --detach "$SCRATCH/val-<member>" <sha>
PYTHONPATH="$SCRATCH/val-<member>/src" <worktree-venv>/bin/python -m pytest <scope>
# runtime surface assertions on the same isolated path
```

---

## 10. Execution status (live register)

- **Phase 0 governance** — DONE; beads `flext-s9bxq` + children; publication n/a (bd
  state); Census: 3199 beads (283 open/33 in_prog/11 def); **36 theme beads absorbed**
  with ledger; snapshot corrections (2wjm=SonarQube not absorbed).
- **Phase 1 worktree** — DONE; epic notes; publication n/a; `~/flext-wt-constants` @
  `constants-remediation-0.12`; setup 31/31; gen idempotent (state-hash stable across 3
  runs); 35-path drift = pre-existing codegen staleness (b3xmn family, external).
- **ADR-012 ghosts** — DONE; `flext-z0zkq` CLOSED; publication core#453→`cb96e05f3`,
  root#223→`0e855c5f7`, both ancestors of origin/0.12.0-dev; At tip: 0 ghost refs
  (consumption-law, ADR-014, README records resolution; ADR-013 zero refs); markdown
  gate OK.
- **S2.0.1 cutover 1: ENV_FILE single owner** — LANDED (stage of `flext-9sinf`);
  `flext-9sinf` (open, stage recorded); publication core#454→`2f5c55a`,
  tests#96→`38154d0`, root#224→`5c22f8d92`, gitlinks verified at origin tip; Isolated
  detached validation @ merged SHAs: **2659 passed**, goldens 6 passed, runtime surface
  assertions ALL PASS (owner-only surface), ruff clean, fleet sweep zero old-API
  consumers.
- **Fleet unblock: flext-tests Mapping repair** — LANDED; `flext-dddl6` (transport
  q7hjp.1; open for full cycle); publication tests#96→`38154d0`; Member test collection
  restored fleet-wide; core suite collects+passes with it.
- **`flext-9sinf` remaining** — IN PROGRESS; `flext-9sinf`; CONFIG\_\_ classification
  (2.0.1), validators as YAML data (2.0.2), rewire fixer (2.0.3), broader P0 tests
  (2.0.4), phase gate (2.0.5).
- **S2.1 shape, cli/tests cycles, fleet** — PENDING; `flext-4305f`…`flext-jelf1`;
  blocked-by chain intact.

**Environment notes (measured)**: base `ci` red at members = `uv.lock --locked` setup
failure (toolchain lane, pre-existing, identical signature on base runs — merge-guard is
the mergeability gate and is green on every landed PR); root orchestrator stops at first
member (`.`), so member-scoped validation uses the member's canonical make surface or
the isolated-detached pattern of §9.2; worktree venv MUST be addressed absolutely
(`~/flext-wt-constants/.venv/bin/...`) because the main checkout's direnv exports
(`VIRTUAL_ENV`, `PROJECT_ROOT`) shadow resolution.

---

## 11. Resumption plan (2026-09-11 21:37) — from mid-execution of `flext-gufl8`

### 11.0 State snapshot (measured)

**LANDED on `origin/0.12.0-dev` (publication-proven):** Phase 0+1; `flext-z0zkq`
(closed, core#453/root#223); 9sinf cutover-1 ENV_FILE single owner (core#454→`2f5c55a`,
tests#96→`38154d0`, root#224→`5c22f8d92`). Root tip moved on (other lanes: `fc66e039f3`,
`741d5a5c73`); core tip advanced to `887e78bd9`; tests to `deb4f82`; infra worktree
synced to `983a149b1` (budget-SSOT + strict-typing + lint-green landings absorbed).

**IN-FLIGHT (uncommitted) — infra branch `fix/release-policy-single-owner`, bead
`flext-gufl8` (claimed):**

- Residue cutover: member projection of `config/build-constraints.txt` removed from
  `codegen.yaml` (managed block + template render) + template deleted + infra's own copy
  `git rm`'d; `conform.py` render branch removed; `ReleasePolicyRenderSpec` +
  `RELEASE_BUILD_CONSTRAINTS_PATH` removed (zero refs in src).
- NEW `src/flext_infra/release/policy_render.py` — typed renderer from
  `config.Infra.release.build_constraints` (public, exported via regen);
  `orchestrator_phases.py` snapshots policy from config render + `_persist_policy_bytes`
  refactor.
- gitignore sections += `*.bak`, `config/build-constraints.txt`, `*aihub-prior*` (LAW1
  data).
- Tests rewritten: `utilities_release.py` (renderer fixture + gitleaks-only template),
  `policy_fixture_root_tests.py` (renderer contract, determinism, **projection-absence
  guard**), `test_release_dag.py` (digests from SSOT helper; policy-snapshot-bytes
  test).
- Lint fixes absorbed: budget test missing `import pytest`; public renames
  `resolve_gate_budgets`/`compose_project_artifact` (private-member-access in tests).
- Verified green: ruff on touched trees; release+policy fixture tests 16 passed;
  renderer exported by gen.
- Known tip-inherited reds (attribution-proven pre-existing, NOT from this diff):
  `protocol_tests` ×3 (release protocol, other lane WIP), duplication declared-trees ×1
  (other lane WIP `ba1e5ab70`), budget table 21× in core check (budget SSOT landed at
  infra tip — re-measure after regen).

**NOT STARTED:** flext-core `.bak` untracking (11 files); root regen+rollup for the
cutover; ai-hub-side `*aihub-prior*`/`.bak` sweep; verb-chain full revalidation; 9sinf
remaining (§2.0.1 CONFIG\_\* classification, §2.0.2–2.0.5); phases 3–5.

### 11.1 Ordered resumption tasks

**R1 — Close `flext-gufl8` infra cutover (unblocks everything):**

1. One complete `tests/unit` run (previous attempt aborted) — inventory reds; prove
   delta vs tip ≤ 0 for my diff (isolated §9.2 pattern when attributing).
2. Member `make check` on infra; fix only reds attributable to this diff; record
   attributed externals in the bead.
3. Scoped re-proof: `make gen` ×2 → `config/build-constraints.txt` must NOT regenerate
   anywhere in the worktree (root or members); `.gitignore` renders with the three
   residue patterns in members; gen byte-idempotent.
4. Commit scoped (src+tests+config+template deletion+git rm), push, PR → merge-guard
   green → merge `--no-ff`; close `flext-gufl8` with §9 evidence (publication proof:
   infra origin tip descendant + root gitlink at next rollup).

**R2 — flext-core residue (separate PR):** `git rm` the 11 tracked `.bak` files; commit
scoped; PR → merge. (Protection arrives fleet-wide via the infra gitignore regen in R3.)

**R3 — Root regen + rollup:** `make gen` at worktree root; commit: regenerated
`.gitignore`s land in members via gitlinks? NO — member gitignore files are member-repo
content: land each touched member's regen (only the members my rollups already touch:
infra, core, tests) + root facets (`src/flext/__init__.py`, `examples/`,
`scripts/*/__init__.py`, `pyproject.toml`) + gitlink rollups (infra tip, core tip+R2,
tests tip) in ONE root PR → merge. Prove: `make gen` ×2 byte-idempotent with NO
`build-constraints.txt`/`.bak` recreation anywhere; `make setup` green.

**R4 — ai-hub side (operator scope expansion):** locate `*aihub-prior*` + stray `*.bak`
in the ai-hub repository (and `~/.agents` if applicable); same treatment: root-cause the
writer, gitignore, remove; land via ai-hub's own PR flow. If the writer is ai-hub sync
tooling consumed by flext, fix at the canonical owner.

**R5 — Verb-chain full revalidation (fix one-by-one, no red attributed to this lane):**
`make setup` → `make gen` → `make fix` → `make fmt` → `make check` → `make test` at the
worktree root; per §9 the lane only owns constants-domain gates; every red gets:
root-cause → fix (mine) or attribution record (externals: uv.lock, cpzjo budget churn,
release-protocol WIP ×3, duplication WIP ×1).

**R6 — Resume `flext-9sinf`:** §2.0.1 CONFIG\_\* adjudication (config-loader defaults);
§2.0.2 validators as YAML data (`settings-layer-purity`, `config-layer-purity`,
`constants-chain-forward`, `constants-value-duplication`, docstring drift); §2.0.3
`rewire_constant_to_settings` enforcement fixer; §2.0.4 P0 tests; §2.0.5 gate → close
bead.

**R7 — `flext-4305f` constants shape:** gv3oe root-cause fix (facade-shape name
derivation) in infra `_namespace_rules/structure.py`; detector extensions (multi-class
wrappers, bare UPPER_CASE); rope_rules `family_shape` YAML; run on flext-core → gate →
close.

**R8 — Continue the chain:** cli-cycle (`flext-p53jy`), tests-cycle (`flext-dddl6`),
fleet (`flext-la3z5` 31 members sequential), format-idempotence (`flext-jelf1`) — per
§2–§5 as written.

### 11.2 Risks / coordination

- Pooled submodule git storage races with concurrent lanes (measured): validate at exact
  SHAs in detached checkouts (§9.2); never reset pooled trees (fix-forward).
- Attributed externals (do NOT chase inside this lane unless they block landing):
  `uv.lock --locked` setup red (toolchain lane); `protocol_tests` ×3 + duplication
  declared-trees ×1 (release/gates lane WIP); cpzjo budget-table churn.
- Every landing keeps merge-guard green; full CI green is a fleet goal owned jointly (§8
  scope fence).
