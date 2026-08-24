# Three-Owner Enforcement Ledger

Updated: `2026-08-05T13:49:34Z`
Status: **P0_COMPLETE_LEDGER_RESTORED**
Forward line: `0.20.0-dev`
Typed SSOT: `docs/references/three-owner-enforcement-ledger.json`
Handoff: `docs/superpowers/plans/2026-08-05-three-owner-p0-handoff.md`
Program epic: `mro-wshr`

## Execution gate

- **P0:** closed in Beads (`mro-ylo0`). Ledger restored 2026-08-05 during handoff (was missing from disk).
- **T0+ blocked** until: `0.12.0` release published **and** operator explicitly requests epic `mro-wkii` / T0.
- Operator gate bead: `mro-hsiu.1` blocks `mro-k60y`.
- `operator_declared_012_final_sha`: unset.

## Census (re-validate on final SHA)

- Workspace HEAD: `c59d2e61b7022ece3dbf9f1a3de162cec6e83ba7`
- flext-core: `f17751e861a698b495be910ba0131a1ddb8b7b30`
- flext-infra: `1773269231947e41491845287e0216c8ad832d54`
- flext-tests: `85faddfe67f1a4ae7bc024a9e7420a4bcfa717a3`
- origin/0.12.0-dev: `c59d2e61b7022ece3dbf9f1a3de162cec6e83ba7`
- origin/0.20.0-dev: `a5ed5b80e64edf1c055304c02558cb380925a1dc`
- Catalog: version 1, **92** rules
- By source_kind: `{'flext_infra_detector': 36, 'flext_tests_validator': 7, 'runtime_warning': 1, 'ruff': 4, 'skill_pointer': 13, 'beartype': 24, 'code_smell': 7}`
- By future_owner: `{'flext-infra': 67, 'flext-core': 25}`
- Root conftests: **31**; all conftests: **95**

## Bead ID map

| Key | ID |
| --- | --- |
| `d0` | `mro-s5zp` |
| `d0_cutover` | `mro-53ne` |
| `d0_dogfood` | `mro-w8bt` |
| `d0_implement` | `mro-hidn` |
| `d0_validate` | `mro-5k2b` |
| `e0` | `mro-buxn` |
| `e0_cutover` | `mro-ajur` |
| `e0_dogfood` | `mro-1ha3` |
| `e0_implement` | `mro-ml19` |
| `e0_validate` | `mro-wgo7` |
| `e1` | `mro-b0eg` |
| `e1_cutover` | `mro-4ta4` |
| `e1_dogfood` | `mro-0xw4` |
| `e1_implement` | `mro-n2ns` |
| `e1_validate` | `mro-pfry` |
| `e2` | `mro-00ka` |
| `e2_cutover` | `mro-654e` |
| `e2_dogfood` | `mro-04s9` |
| `e2_implement` | `mro-k5yb` |
| `e2_validate` | `mro-m1oj` |
| `e3` | `mro-he00` |
| `e3_cutover` | `mro-shkd` |
| `e3_dogfood` | `mro-pqcd` |
| `e3_implement` | `mro-wjph` |
| `e3_validate` | `mro-4jhx` |
| `e4` | `mro-6s34` |
| `e4_cutover` | `mro-ajuq` |
| `e4_dogfood` | `mro-pkfj` |
| `e4_implement` | `mro-a1ie` |
| `e4_validate` | `mro-6wvz` |
| `e5` | `mro-wt0l` |
| `e5_cutover` | `mro-6rr7` |
| `e5_dogfood` | `mro-j8tz` |
| `e5_implement` | `mro-0sgl` |
| `e5_validate` | `mro-qdse` |
| `e6` | `mro-43ng` |
| `e6_cutover` | `mro-yg2m` |
| `e6_dogfood` | `mro-s5wk` |
| `e6_implement` | `mro-w3cz` |
| `e6_validate` | `mro-fosq` |
| `ec` | `mro-ehid` |
| `ec_cutover` | `mro-2lqu` |
| `ec_dogfood` | `mro-qq3d` |
| `ec_implement` | `mro-q4wu` |
| `ec_validate` | `mro-07fp` |
| `et` | `mro-0kl7` |
| `et_cutover` | `mro-5hzi` |
| `et_dogfood` | `mro-0c9o` |
| `et_implement` | `mro-xbxz` |
| `et_validate` | `mro-jtmq` |
| `p0` | `mro-ylo0` |
| `p0_cutover` | `mro-nr9y` |
| `p0_dogfood` | `mro-gn1z` |
| `p0_implement` | `mro-05rh` |
| `p0_validate` | `mro-m2h9` |
| `prog` | `mro-wshr` |
| `t0` | `mro-hsiu` |
| `t0_cutover` | `mro-qyxr` |
| `t0_dogfood` | `mro-meyo` |
| `t0_implement` | `mro-k60y` |
| `t0_operator_gate` | `mro-hsiu.1` |
| `t0_validate` | `mro-k4qs` |
| `v0` | `mro-now1` |
| `v0_cutover` | `mro-m3nw` |
| `v0_dogfood` | `mro-b0p0` |
| `v0_implement` | `mro-o0oi` |
| `v0_validate` | `mro-biwz` |

## T0 start (operator)

1. Publish 0.12.0 release
1. Operator explicitly requests execution of mro-wkii / T0
1. Set census.operator_declared_012_final_sha in this ledger
1. Close mro-hsiu.1 (orchestrator)
1. Claim mro-k60y (T0.I); absorb mro-dxrp DoD
1. Primary checkout origin/0.20.0-dev; make work lane; merge declared SHA; preserve 0.20 overlays

## Dependency order

- `P0.V -> T0.V -> E0.V`
- `after E0: EC.1/EC.2, ET.1/ET.2, E1, E2 parallel on disjoint git roots`
- `E2.V -> EC.3`
- `E1.V + E2.V -> E4`
- `E2.V -> E3`
- `ET.2.V -> ET.2.C; E3.C + E4.C + ET.2.C -> E5`
- `E5 strict/zero -> EC.4 STRICT`
- `EC.C + ET.C + E5.C -> E6 -> V0 -> D0`

## Related

- parent: `mro-wkii`
- closed_folded_p3: `mro-wkii.4`
- existing_transition_task: `mro-dxrp`
- deferred_beartype_warnings: `mro-31mj`
- program: `mro-wshr`
- p0_epic: `mro-ylo0`
- t0_epic: `mro-hsiu`
- t0_operator_gate: `mro-hsiu.1`

## Delete summary

### flext-core

- src/flext_core/_constants/_enforcement_catalog_rows_parts/
- static catalog builder exports (u.build_canonical_catalog static path)
- static source kinds: flext_infra_detector, flext_tests_validator, ruff, code_smell, skill_pointer
- static-only warning categories

### flext-infra

- src/flext_infra/_enforcement/ (custom scanners after engine cutover)
- src/flext_infra/refactor/namespace_enforcer*.py
- src/flext_infra/refactor/declarative_enforcement.py
- pytest_runner / pytest_diag / pytest_selector / _pytest_entry (move to flext-tests then delete)
- rope pep695 monkeypatch after fork pin
- pylint / pylintrc; qlty complexity overlap with radon

### flext-tests

- static TEST-* validators that migrate to infra test-policy
- runtime imports of flext_infra implementation
- stale tt documentation aliases

### members

- 31 root flext-*/conftest.py bootstraps (delete after pytest11 early-load)
- duplicated marker/settings/container hooks; keep domain fixtures only

## Rules flext-core (25)

- `ENFORCE-022` (runtime_warning)
- `ENFORCE-039` (beartype)
- `ENFORCE-041` (beartype)
- `ENFORCE-042` (beartype)
- `ENFORCE-043` (beartype)
- `ENFORCE-044` (beartype)
- `ENFORCE-045` (beartype)
- `ENFORCE-046` (beartype)
- `ENFORCE-047` (beartype)
- `ENFORCE-048` (beartype)
- `ENFORCE-049` (beartype)
- `ENFORCE-050` (beartype)
- `ENFORCE-051` (beartype)
- `ENFORCE-052` (beartype)
- `ENFORCE-053` (beartype)
- `ENFORCE-054` (beartype)
- `ENFORCE-055` (beartype)
- `ENFORCE-064` (beartype)
- `ENFORCE-066` (beartype)
- `ENFORCE-067` (beartype)
- `ENFORCE-068` (beartype)
- `ENFORCE-069` (beartype)
- `ENFORCE-070` (beartype)
- `ENFORCE-079` (beartype)
- `ENFORCE-071` (beartype)

## Rules flext-infra (67) ids
`ENFORCE-001`, `ENFORCE-002`, `ENFORCE-003`, `ENFORCE-004`, `ENFORCE-005`, `ENFORCE-006`, `ENFORCE-007`, `ENFORCE-008`, `ENFORCE-009`, `ENFORCE-010`, `ENFORCE-080`, `ENFORCE-011`, `ENFORCE-012`, `ENFORCE-013`, `ENFORCE-014`, `ENFORCE-026`, `ENFORCE-027`, `ENFORCE-028`, `ENFORCE-029`, `ENFORCE-030`, `ENFORCE-031`, `ENFORCE-032`, `ENFORCE-033`, `ENFORCE-091`, `ENFORCE-092`, `ENFORCE-093`, `ENFORCE-094`, `ENFORCE-095`, `ENFORCE-096`, `ENFORCE-081`, `ENFORCE-082`, `ENFORCE-083`, `ENFORCE-084`, `ENFORCE-090`, `ENFORCE-097`, `ENFORCE-098`, `ENFORCE-015`, `ENFORCE-016`, `ENFORCE-017`, `ENFORCE-018`, `ENFORCE-019`, `ENFORCE-020`, `ENFORCE-021`, `ENFORCE-023`, `ENFORCE-024`, `ENFORCE-025`, `ENFORCE-034`, `ENFORCE-035`, `ENFORCE-036`, `ENFORCE-037`, `ENFORCE-038`, `ENFORCE-065`, `ENFORCE-057`, `ENFORCE-058`, `ENFORCE-059`, `ENFORCE-060`, `ENFORCE-061`, `ENFORCE-062`, `ENFORCE-063`, `ENFORCE-040`, `ENFORCE-072`, `ENFORCE-073`, `ENFORCE-074`, `ENFORCE-075`, `ENFORCE-076`, `ENFORCE-077`, `ENFORCE-078`
