# Roadmap: FLEXT Monorepo Hardening & Modernization

## Milestones

- ✅ **v1.0 Hardening** — Phases 1-8 (shipped 2026-03-25) → [archive](.planning/milestones/v1.0-ROADMAP.md)
- 📋 **v2.0 Rope Engine** — Phases 9-10 (planned)

## Phases

<details>
<summary>✅ v1.0 Hardening (Phases 1-8) — SHIPPED 2026-03-25</summary>

- [x] Phase 1: Type System Hardening (5/5 plans) — complete
- [x] Phase 2: Architecture & SOLID (5/5 plans) — complete
- [x] Phase 3: Infrastructure Centralization (5/5 plans) — complete 2026-03-24
- [x] Phase 4: Python 3.13 Modernization (3/3 plans) — complete
- [x] Phase 5: Package Migration (3/3 plans) — complete
- [x] Phase 6: Typing Gap Closure (2/2 plans) — complete
- [x] Phase 7: Modernization & Integration Fixes (2/2 plans) — complete
- [x] Phase 8: Workaround Residual Cleanup (3/3 plans) — complete 2026-03-25

Full phase details: [milestones/v1.0-ROADMAP.md](milestones/v1.0-ROADMAP.md)

</details>

### 📋 v2.0 Rope Engine (Planned)

- [x] Phase 9: Rope-native refactor engine rewrite — **3 plans** — complete 2026-03-25
- [ ] Phase 10: Unified Docs Generation Baseline

**Phase 9 Goal:** Integrate rope as pre/post hooks on FlextInfraRefactorEngine, migrate 3 cross-file transformers to rope APIs, reduce LOC in transformers/.

**Phase 9 Requirements:** ROPE-01 through ROPE-07

Plans:
- [x] 09-01-PLAN.md — Rope Project init + engine hook infrastructure
- [x] 09-02-PLAN.md — Migrate 3 transformers to rope (symbol_propagator, mro_reference_rewriter, nested_class_propagation)
- [x] 09-03-PLAN.md — Audit remaining transformers + LOC verification

**Phase 10 Goal:** Refactor all flext-infra command domains (excluding docs) to modern MRO service facade pattern. Services as thin FlextService orchestrators over u.Infra.*. Create api.py MRO facade, simplify base.py. Verify library domains (detectors, gates, rules, transformers).

**Phase 10 Requirements:** DOCS-01 through DOCS-08

**Plans:** 8 plans

Plans:
- [ ] 10-01-PLAN.md — Foundation: api.py MRO facade + base.py simplification
- [ ] 10-02-PLAN.md — Simple domains: basemk, github, release thin orchestrators
- [ ] 10-03-PLAN.md — Medium domains: check + validate thin orchestrators
- [ ] 10-04-PLAN.md — Medium domains: workspace thin orchestrators
- [ ] 10-05-PLAN.md — Complex domains: codegen + root services thin orchestrators
- [ ] 10-06-PLAN.md — Complex domains: deps thin orchestrators
- [ ] 10-07-PLAN.md — Engine domain: refactor thin orchestrators
- [ ] 10-08-PLAN.md — Library verification + FlextInfra facade finalization

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Type System Hardening | v1.0 | 5/5 | Complete | 2026-03-25 |
| 2. Architecture & SOLID | v1.0 | 5/5 | Complete | 2026-03-25 |
| 3. Infrastructure Centralization | v1.0 | 5/5 | Complete | 2026-03-24 |
| 4. Python 3.13 Modernization | v1.0 | 3/3 | Complete | 2026-03-25 |
| 5. Package Migration | v1.0 | 3/3 | Complete | 2026-03-25 |
| 6. Typing Gap Closure | v1.0 | 2/2 | Complete | 2026-03-25 |
| 7. Modernization & Integration Fixes | v1.0 | 2/2 | Complete | 2026-03-25 |
| 8. Workaround Residual Cleanup | v1.0 | 3/3 | Complete | 2026-03-25 |
| 9. Rope-native refactor engine rewrite | v2.0 | 3/3 | Complete | 2026-03-25 |
| 10. Unified Docs Generation Baseline | v2.0 | 0/8 | Planned | |
