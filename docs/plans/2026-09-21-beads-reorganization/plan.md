# Beads Reorganization & Cleanup Campaign — 2026-09-21

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

- (this file is appended per batch; each bead gets its verdict + evidence inline in bd)
- **B3 partial (P0 bugs, session 0.12-stabilize, tip c6d1bdf0e4)** — deep-validated
  against live code + runtime:
  - `flext-bdmdg` **CLOSED** — `conform.py` reduced to 16-line facade; symbol
    `ReleasePolicyRenderSpec` has 0 references; consumer uses `m.Infra.ReleasePolicySpec`
    (runtime import OK).
  - `flext-5fxu6.4.32` **CLOSED** — `u.Infra.docs_github_repos/repo_lookup/parse_github_doc_url`
    all present (runtime `hasattr` True).
  - `flext-72b72` **CLOSED** — `codegen.yaml:1169` quotes `"click>=8.3.3,<8.4"`; full-doc
    YAML scan finds 0 loose `<8.4`; `flext-cli/pyproject.toml:18` correct.
  - `flext-mphw1` **fix landed, OPEN** — `ci.yml.j2:72-73` + `submodule_setup_recipe.j2:24`;
    blocked only on CI-green acceptance.
  - `flext-5fxu6.4.27` **LIVE** — builtin `status:` (root Makefile:644) shadows a declared
    promoted `status`; `_promoted/registry.py validate()` lacks builtin-collision check.
    Owner: flext-infra (`_promoted/registry.py` + `Makefile.j2`).
  - `flext-0in0k.8` **LIVE** — `TEST_RUNTIME_ALIAS_TARGETS`/`ALIAS_NAMES` still hardcoded and
    used as decision inputs (`_lazy_init_planner_collision.py:60`, `_codegen_generation_paths.py:52-53`).
