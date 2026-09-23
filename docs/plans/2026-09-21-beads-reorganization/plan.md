# Beads Reorganization & Cleanup Campaign — 2026-09-21

<!-- TOC START -->

- [Inventory snapshot (2026-09-21, bd list --status open)](#inventory-snapshot-2026-09-21-bd-list-status-open)
- [Per-entity protocol (every bead passes through all 5 checks)](#per-entity-protocol-every-bead-passes-through-all-5-checks)
- [Classification decision tree (per bead)](#classification-decision-tree-per-bead)
- [Execution batches](#execution-batches)
- [Validation surfaces (runtime-first)](#validation-surfaces-runtime-first)
- [Progress log](#progress-log)
- [Continuation 2026-09-22 (implementation agent)](#continuation-2026-09-22-implementation-agent)

<!-- TOC END -->

> Status: ACTIVE. Method: iterative, item-by-item, evidence-first. Precision over speed.
> Operator mandate: audit + restructure Beads/Epics/Tasks/Bugs/Hotfixes for
> architectural integrity and protocol alignment. Never hand-edit projections.

## Inventory snapshot (2026-09-21, bd list --status open)

- Total 306: 144 bug, 114 task, 26 epic, 20 feature, 1 chore, 1 rig
- Priorities: P0=31, P1=191, P2=74, P3=10
- Context: PR #257 MERGED (squash 6621995118); base 0.12.0-dev advanced (census wave
  681cd25df4)

## Per-entity protocol (every bead passes through all 5 checks)

1. **Claim management** — obsolete/incorrect claims removed (`bd update --claim`
   hygiene, reassign to the correct lane if claimed by a dead session).
2. **Traceability** — relevant PRs and remote branches linked in the body/comments
   (`bd update <id> --append-notes` or `bd comment`).
3. **Hierarchical alignment** — tasks/bugs parented to the correct epic (`bd dep`
   discover-from/parent edges audited); misfiled entities reparented.
4. **Fix protocol compliance** — bugfix/hotfix work sits OUTSIDE the epic hierarchy
   where protocol requires (standalone bug beads with `discovered-from` links, never as
   epic children that gate epic closure).
5. **Pruning** — entity deleted ONLY if 100% superseded AND no longer contributes to the
   integration branches of active projects. Close (not delete) when historical value
   exists; delete only for pure noise/duplicates.

## Classification decision tree (per bead)

```
read title+body
  → does the defect/request still exist in code at 0.12.0-dev tip?
      no  → CLOSED (evidence: the landing commit/PR that resolved it)
      yes → is it owned/duplicated by an open epic child or another bead?
              yes → dedupe: keep one, close the twin as duplicate (cross-link)
              no  → LIVE: verify claims/links/parent, update, keep open
  → is it a bug/hotfix wrongly parented inside an epic?
      yes → detach to standalone bug + discovered-from edge
```

## Execution batches

- **B1 Epic map** — enumerate 26 open epics + children; build the hierarchy table.
- **B2 Campaign beads** — markdown SSOT epic, stabilize-lane beads, flext-sbrbf
  (payload), #257-adjacent: close/adjust with this session's evidence.
- **B3 P0 bugs (31)** — deep-validate against code; the highest-value slice.
- **B4 P1 mass (191)** — grouped by epic; sampled code validation + linkage pass.
- **B5 P2/P3 + tasks (148)** — hierarchical alignment + duplicate pruning.
- **B6 Integration** — after each batch: commit plan doc updates; no-ff merge of any
  pending branches with full lifecycle (setup/gen/fix/fmt/check/test) + CI green.

## Validation surfaces (runtime-first)

- `make gen` fixed point; `make fix`/`fmt` 32/32; `make check` findings triaged with
  owners; `make test` per-member debts documented with owner beads.
- jscpd dedup is tracked under the duplication owner route (flext-y3qpq.2.6 / S17) — not
  run ad-hoc against projections.

## Progress log

- **B3 partial (P0 standalone, session zcode-lane-A, tip b577892348)** —
  Makefile/runtime probes:
  - `flext-5fxu6.4.27` **runtime probe**: root `make status` exit=0 (functional);
    member-level promoted-verb repro pending — owner flext-infra.
  - `flext-yjjim` **CONFIRMED LIVE** — generated Makefile has NO FILE test selector
    (grep `test-file|TEST_FILE` = 0) and no explicit full-suite verb beyond `test:`.
  - `flext-5fxu6.4.14` **CLOSED** (batch 2) — duplicated fmt comment = 0 occurrences.
  - `flext-5fxu6.4.13` **CONFIRMED LIVE** — generated `.jscpd.json` ignores
    `.claude/**`, no worktree pattern; root-cause in generator config (flext-infra).
  - `flext-5fxu6.4.12` **LIVE** — `fix-enforcement` advertised in `make help`;
    orchestrator-rejection probe owned by infra lane.
  - Hygiene note: an accidental `peek` note landed in flext-49quw NOTES (ignore).
- **B3 partial (P0 bugs, session 0.12-stabilize, tip c6d1bdf0e4)** — deep-validated
  against live code + runtime:
  - `flext-bdmdg` **CLOSED** — `conform.py` reduced to 16-line facade; symbol
    `ReleasePolicyRenderSpec` has 0 references; consumer uses
    `m.Infra.ReleasePolicySpec` (runtime import OK).
  - `flext-5fxu6.4.32` **CLOSED** —
    `u.Infra.docs_github_repos/repo_lookup/parse_github_doc_url` all present (runtime
    `hasattr` True).
  - `flext-72b72` **CLOSED** — `codegen.yaml:1169` quotes `"click>=8.3.3,<8.4"`;
    full-doc YAML scan finds 0 loose `<8.4`; `flext-cli/pyproject.toml:18` correct.
  - `flext-mphw1` **fix landed, OPEN** — `ci.yml.j2:72-73` +
    `submodule_setup_recipe.j2:24`; blocked only on CI-green acceptance.
  - `flext-5fxu6.4.27` **LIVE** — builtin `status:` (root Makefile:644) shadows a
    declared promoted `status`; `_promoted/registry.py validate()` lacks
    builtin-collision check. Owner: flext-infra (`_promoted/registry.py` +
    `Makefile.j2`).
  - `flext-0in0k.8` **LIVE** — `TEST_RUNTIME_ALIAS_TARGETS`/`ALIAS_NAMES` still
    hardcoded and used as decision inputs (`_lazy_init_planner_collision.py:60`,
    `_codegen_generation_paths.py:52-53`).
- **B3/B5 partial (session 0.12-stabilize, tip c358cd4658)** — 6 beads CLOSED with
  evidence (runtime-first):
  - `flext-bdmdg`, `flext-5fxu6.4.32`, `flext-72b72` (see B3 partial above).
  - `flext-44he4` — `flext-cli/pyproject.toml:18` now `click>=8.3.3,<8.4` (was
    `>=8.4.2`).
  - `flext-5s0rj` — 0 trailing whitespace in generated `.github/workflows/*.yml`.
  - `flext-5ra33` — `FlextInfraCodegenPipeline.execute()` present (runtime `hasattr`
    True).
  - **Hierarchy clean**: 0 bugs with a parent (concurrent lane reparented the 24 to
    root).
  - **PR audit (flext-5anhp)**: `#261`/`#259` 100% superseded (gitlinks only / config
    already in integration); `#258`/`#260`/`#262` carry unique content (markdownlint
    `ignorePaths`, rope lane, ADR-018 integration-state paragraph). Convergence blocked:
    branch switching would disrupt the concurrent lanes using the shared workspace root.
  - **Census**: 296 open (137 bug / 113 task / 24 epic / 20 feature / 1 chore / 1 rig);
    graph 0 cycles; `find-duplicates` pairs are `0in0k.*` sibling-title false positives.
- **Security lane (session 0.12-stabilize, tip 57c94b57db)** — operator priority:
  - `flext-tqh48` **CLOSED** (flext-web@d41a289) — hardcoded credential check,
    `nonexistent` sentinel and fabricated `f"token_<user>"` removed; auth now validates
    against the settings SSOT (`FLEXT_WEB_WEB__AUTH_USERNAME/AUTH_PASSWORD`) with
    `secrets.compare_digest` and `secrets.token_urlsafe(32)`, failing loud when
    unconfigured. `secret_key` committed literal removed (env-only, fail loud in
    `create_flask_app`). 155 tests pass; make fix 5/5; security gate 0 errors.
  - **CodeQL alert #6 CLOSED** (root 57c94b57db) —
    `py/incomplete-url-substring-sanitization` in
    `scripts/workspace/dependabot_merge.py`: `repo_slug_from_origin` accepted
    `github.com/` at any position. New `slug_from_remote_url` parses with `urlparse`,
    requiring hostname `github.com`/`www.github.com` and scheme `{https,ssh,git}`; scp
    `git@github.com:` keeps its explicit prefix. Regression test
    `tests/unit/dependabot_merge_slug_tests.py` (3 forged-host vectors) passes. Alert #6
    was the only OPEN CodeQL alert (5/2/1 already fixed).
  - **Pending recommendations (owner flext-infra)**: enable CodeQL on the 31 members
    ("no analysis found"); reconcile the p57t semgrep family (`~/semgrep-violations`
    ledger absent; local `p/security-audit`/`p/default` runs 0 findings).
- **Code-quality lane (session 0.12-stabilize)**:
  - `flext-meltano@44df5a27` — pydantic 2.13 deprecation escalated to error by the fleet
    warnings filter (`Final[X]` with default in a pydantic namespace-holder) broke every
    downstream suite collection; converted `settings`/`base`/`enums` constants to
    `ClassVar`. flext-dbt-oracle-wms collection recovered.
  - `flext-dbt-oracle-wms@0b67363` — renamed forbidden accessor `get_entity_data` →
    `fetch_entity_data` (AGENTS.md §3.1) across protocol, caller and test double;
    runtime-census 0 errors; 26 tests pass.
  - **Owner overlap**: a concurrent lane is migrating the same `Final`→`ClassVar`
    deprecation repo-by-repo (e.g. `flext-ldap 31444783`); this session completed
    flext-meltano to unblock the shared test collector.
- **Runtime/latent-defect lane (session 0.12-stabilize)**:
  - `flext-liyb1` **CLOSED** (flext-meltano@`e632e803`) — `target_service_base.cli_main`
    discarded `command_args` and returned 0 unconditionally. Now dispatches the real
    Singer stream via `u.Meltano.process_stdin(self)` and implements
    `SingerTargetHandler` (`handle_schema`→`fetch_or_create_sink`,
    `handle_record`→`process_record`, `handle_state`→`flush`), non-zero on failure —
    symmetric with the tap/dbt bases.
  - **flext-infra@`719b10021`** — `_models/gates.py` imported the removed `mp` facade
    (ImportError broke every consumer reaching flext_infra models, e.g. the whole
    flext-meltano collection) and referenced the sibling nested `SccFile` from a nested
    class body (ruff F821). Routed fields through `m`, lifted `SccFile` to module level,
    made the two boolean test params keyword-only. `make fix` 5/5 green.
  - **Latent blocker observed**: member `.venv` lost `flext_infra` (a concurrent lane's
    setup); validated gates through the root venv without reinstalling manually.
- **Fleet-green execution (session 0.12-stabilize, 2026-09-22)** — implementing
  `.kilo/plans/fleet-green-and-beads-closure.md`:
  - **W4 `Final`→`ClassVar`: VERIFIED COMPLETE.** Imported `models`/`constants` with
    `PydanticDeprecatedSince211` escalated to error across all 32 repos → **32/32
    CLEAN** (no deprecation). Remaining `Final[` occurrences are nested-class attributes
    pydantic does not process as fields; no action needed.
  - **W3 runtime-census inventory measured** (gate isolated, per repo): ~1000 findings.
    Dominant codes: ENFORCE-047/049 (facade base/MRO), 066 (compat aliases), 079
    (constants outside `_constants`), 067 (module class cap), 042
    (Config→FlextSettings), 069 (nested depth), 046, 068, 070. Zero-finding repos:
    flext-api, flext-dbt-oracle-wms, flext-plugin.
  - **ENFORCE-042 fixed and PUSHED** (canonical `(FlextSettings, <upstream>Config)` MRO,
    matching flext-api): `flext-dbt-oracle@45f9350`, `flext-grpc@cf5ce3c`,
    `flext-dbt-ldap@881d4b2` — each `runtime-census` went 1→0 and `make fix` 5/5 green.
  - **flext-meltano@deb6a138 runtime-census 0** (was 4): `FlextMeltanoConfig` MRO,
    `singer_tap.py` split into `singer_tap.py` + `tap_source_mixin.py` (ENFORCE-067),
    sqlalchemy import outside its owner removed (ENFORCE-070).
  - **flext-core unblocked**: the WIP left runtime `from flext_core import t` imports in
    `__version__.py`, `constants.py` and `_constants/**` that created an import cycle
    (`_typings.base → _constants → flext_core.lazy → _lazy_parts → _typings.lazy → _typings.base`)
    and an unresolved pydantic `t` annotation in `_enforcement_data`. Deferred them to
    `TYPE_CHECKING` (annotations are lazy) and made the pydantic-facing `t` a runtime
    import; flext_core imports cleanly again.
  - **MRO cascade completed**: adding `FlextSettings` to `FlextMeltanoConfig` made the
    12 leaf `(<X>Config(FlextSettings, FlextMeltanoConfig))` classes inconsistent, so
    the leaves now inherit it via `FlextMeltanoConfig` — all pushed.
  - **Verified 0 findings**: flext-meltano, flext-dbt-oracle, flext-grpc,
    flext-target-oracle-wms. Remaining: flext-dbt-ldap (ENFORCE-069 nested depth).
- **Waves lane (reval260921, session f1d47a5f, ledger
  `.beads/artifacts/reval260921/ledger.csv`)** — analysis waves C1 (55) / C2 (134) / D
  (38) / A (33) complete item-by-item (4-source, verdicts in `verdicts/*.json`); B1
  running, B2 queued (rate-limit serialisation). **6 batches applied, ~77 mutations,
  graph clean after each**: claims released (co1th SUPERSEDED→cu85s; 4 stale → open),
  ancestry-proven DONE closures (czzns, v1xzd, tqhe9), 28 canonical reparents total
  (features+tasks; journal-trio adjudicated: expose→harvest precedes any delete, ADR
  required), cpzjo cutover (7 children mapped child-by-child → SUPERSEDED→1wjg1), d421
  SUPERSEDED→wkii, crossrefs (mbowt, ro6mj, ywet, m7xk7, 4as1t), 38p39 relink (arms
  60s/120s unlanded). Orphans 6→4; flext-xtzkz retirement ledger →itpd1 (stale, feeds
  B6). **jbfz** = next epic closure candidate (16/16 children closed, Snyk #292 merged)
  — held for clean re-scan (4th source). flext-web 6560c1d committed conflict markers
  healed via canonical gen + runtime proof (a9a56f5/f2f51ef). Integration: guarded
  ladder (SELECTED_PROJECTS, infra WIP guard, transient retry) cycling the verbs on the
  new base; #257 MERGED noted.

- **Security batch (session zcode-lane-A, 2026-09-21晚)** — dual-scanner re-validation:
  - `flext-p57t.12` CLOSED (Mimosa sealed 0 + Semgrep 1.177.0 live 0), `flext-p57t.5`
    CLOSED (live 0), `flext-jbfz` epic CLOSED (17/17 children + SAST merged #292) —
    closes the "4th source re-scan" hold above.
  - `flext-p57t.8` (dbt-ldif) live 28 findings — triage recorded in-bead: curl fix
    already at template tip (regen pending), `.semgrepignore` projection spec written,
    23 MEDIUM/WARNING = one generator wave (SHA-pin + cooldowns + ignore).
  - Sonar `flext-2wjm`: all 10 open children re-validated against the LIVE SonarCloud
    API (123 open total: wms 17, plugin 15, observability 14, oic 13, ldap 12, wms-db
    11, tap-wms 10, ldif-t 9, ldif-target 9, tap 7, dbt 6) — each bead dated-evidenced.
    S8482-dominant; same generator wave resolves.
  - Replicable method: anonymous SonarCloud API + local semgrep p/default + Mimosa
    sealed.
- **Security lane (waves session, evening 2026-09-21)** — Semgrep epic `flext-p57t`
  CLOSED: 33/33 children. Last three repos remediated via MERGED PRs #487 (core), #793
  (infra), #116 (dbt-ldif): dependabot cooldown landed through the SSOT knob
  (`dependabot_cooldown_days` in codegen.yaml), third-party `dbt_packages/` excluded via
  `.semgrepignore`, per-finding triages documented. Generator fix for the flext-meltano
  wheel collision merged (#794, `flext-fgy4x` closed with A/B runtime proof: uv sync +
  wheel build). NEW beads: `flext-c2kp3` (journal lease timeout recurrence under
  multi-agent load — executor wait/backoff needed), `flext-fgy4x` (closed). NEXT: `2wjm`
  SonarCloud (11 active children, SonarCloud RED at tips), `jbfz` re-scan (platform
  scans run on PRs only — needs a sweep PR or Snyk platform check).

## Continuation 2026-09-22 (implementation agent)

- **R0 inventory.** Live `bd list --status open --flat --limit 0 --json` = 291 open; CSV
  at `scratch/kilo/wip-beads-open-20260922.csv`. `bd doctor --check=validate` OK;
  `bd graph check` clean; `bd orphans` only `flext-pwmej` (slice commit, kept open);
  pollution gate 4 false positives (`flext-ss5r9`, `flext-38p39`, `flext-olwmz`,
  `flext-6qrb`).
- **R1 B2.** 14 KEEP bugs got `reval260921` + evidence notes; ALREADY-CLOSED/DONE
  already closed; 128 SKIP remain lead-owned.
- **R2 hierarchy.** 0 bugs under epics (open/in_progress/blocked). 5 parentless
  tasks/features reparented: `flext-zxdl5`→`flext-ssnc7`, `flext-yj3s0`→`flext-itpd1`,
  `flext-sbrbf`→`flext-y3qpq.3`, `flext-z7u1g`→`flext-itpd1`,
  `flext-mvaxv`→`flext-ssnc7`; `relates-to` edges to `flext-itpd1.2` and
  `flext-y3qpq.2.6`.
- **R3 partial (`0in0k`).** Validated at flext-infra 0.12.0-dev: `flext-0in0k.9` PRs
  `#784`/`#785` MERGED with 31/31 runtime import proof (kept in_progress pending the
  `flext-0in0k.8` blocks edge); `.26` PR `#784` merged but runtime-census green still
  unproven; `.8`, `.5`, `.6`, `.7` still LIVE (symbols present at tip) — notes added.
- **R5 security.** `flext-c2kp3` CLOSED: flext-infra `origin/0.12.0-dev` `2107ed73e`
  (lease waits up to 1800s with 1s poll, fails loud on deadline; 3 lease tests pass;
  make fix 5/5). Live SonarCloud API reachable via `rtk curl`; the local
  `~/sonarqube-violations` dump is absent, so `flext-2wjm` triage must use the API.
- **R5 SonarCloud live classification.** Live API totals for the 11 open `flext-2wjm`
  children (2026-09-22): tap-oracle-wms 6, plugin 15, oracle-wms 17, oracle-oic 13,
  dbt-oracle-wms 7, target-ldif 5, tap-oracle 7, tap-ldif 5, dbt-oracle 6, observability
  14, ldap 12. Dominant rules `githubactions:S8482`, `python:S108`, `python:S3776`,
  `plsql:S1192`, `docker:S7018`. Notes recorded on every child; S8482 remediation
  belongs to the generator owner.
- **R3 additional.** `flext-ldgbb`, `flext-5fxu6.4.24`, `flext-5fxu6.4.25`,
  `flext-ujjrk` are LIVE at the flext-infra tip (missing test/gate/rule), each with an
  rg-evidence note.
- **R8 root-PR triage (containment proof).** `#261` `audit/pr-supersession` = 5 gitlinks
  only, every SHA contained in `origin/0.12.0-dev`; `config/plan-collection.yaml`
  already disabled → 100% superseded, retire. `#259` `validate/flext-itpd1-3-producer` =
  config identical to integration and flext-infra gitlink `c2ca5a128` contained → 100%
  superseded, retire. `#258` `repair/make-check-20250919` = unique
  `.markdownlint.json`/`.markdownlintignore`, `pyproject.toml` (+3), generated docs →
  needs no-ff integration. `#260` `feature/rope-modernize` = unique rope commits +
  plan-collection source → hunk-by-hunk no-ff integration. `#262`
  `worktree-generator-law-p0` = unique ADR-018 integration-state paragraph,
  stabilization checkpoint docs, catalog/worker-lane docs → no-ff doc integration.
  Evidence in `flext-whndf`. **Blocker:** this session cannot run
  `git merge`/`checkout`/`worktree` or `gh pr close/merge/comment`; retirement and
  merges need an agent with those permissions or the operator.
- **New defect filed.** `flext-ownfp` (bug, `bugfix`): the first `bd` write rewrote the
  generated `.beads/config.yaml`, adding `issue-prefix`, a `dolt:` block and
  `dolt.mode: server`. Owner: flext-infra templates + `config/beads.yaml` identity;
  regenerate via `make gen`, never hand-edit. Evidence: `git diff .beads/config.yaml`.
- **Next.** R3 continues on `flext-y3qpq.*`/`flext-5fxu6.4`; R5 `flext-2wjm` live
  classification (SonarCloud API reachable via `rtk curl`; local
  `~/sonarqube-violations` dump absent); R8 execution once merge/PR permissions are
  available.
