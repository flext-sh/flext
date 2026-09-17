# Plan: Audit and Refactor Global Root Governance Architecture

## Critical Constraints

- **`law_surface.py`** (`src/agents_governance/law_surface.py`): AGENTS.md MUST start with `<!-- AIHUB-INVIOLABLE-LAW-PRELUDE v1 -->` and end the prelude with `<!-- /AIHUB-INVIOLABLE-LAW-PRELUDE -->`, followed by exactly one blank line. This constraint is enforced by code. The prelude (lines 1-37) stays intact.
- **`pyproject.toml`** line 45: `"AGENTS.md" = "agents_governance/_data/AGENTS.md"` — root `AGENTS.md` is canonical source packaged into the wheel. Not a generated file.
- **No tests** directly validate AGENTS.md content, line count, or PRELUDE boundaries in the test suite.
- **`config/governance.json`** references rules by ID path (e.g., `"coordination/operator-precedence"`) — these IDs are stable and won't change with this refactor.
- **`agents-refactor` skill** validation criteria: root file minimal, all links work, no contradictions, no lost instructions, each linked file self-contained.

`/home/marlonsc/agents` is the global root governance authority (Bead flext-3rld2). `AGENTS.md` is 211 lines of dense inline content, with ~95 lines of "universal law" rules that are duplicated in dedicated `rules/` files, plus project-specific operational details that should not live in a root governance file. Three files state incompatible precedence orderings. The refactor targets minimal root + linked categorized authorities.

**Scope**: ONLY `/home/marlonsc/agents/` — `AGENTS.md`, linked rule/index files, owner manifests (`config/governance.json`, `config/workspace.yaml`, `config/skills.json`, `config/evals.json`). NOT individual skill bundles, NOT projection code, NOT project repo files (`~/flext-worktrees/rope-modernize`).

## Audit Findings Summary

### C1 — Precedence Contradiction (CRITICAL)
Three different precedence hierarchies:
- `AGENTS.md` line 17: `USER REQUEST > BEADS > ADRs > SKILLs > DOCS > default`
- `VALIDATE_ON_CHANGE.md` line 107: `regra do operador > beads > ADRs > skills > docs`
- `rules/coordination/operator-precedence.md` lines 20-21: `operator request > orchestration contract > canonical tracker > ADRs > skills > docs > defaults`

**Resolution**: `rules/coordination/operator-precedence.md` is the dedicated authority. AGENTS.md and VALIDATE_ON_CHANGE.md shall cite it instead of restating.

### C2 — "Never Deduce" — 4 copies (CONTRADICTION + DUPLICATION)
- `AGENTS.md` lines 154-158 (brief Portuguese)
- `AGENTS.md` lines 199-204 (expanded Portuguese)
- `VALIDATE_ON_CHANGE.md` Rule 4 (Portuguese)
- `rules/coordination/never-deduce.md` (canonical English)
- `rules/ethics/never-deduce-research-first.md` (supplementary)

### C3 — "Validate-on-Change" — 3 copies (CONTRADICTION + DUPLICATION)
- `AGENTS.md` lines 145-153
- `VALIDATE_ON_CHANGE.md` Rule 1
- `rules/coordination/validate-on-change.md` (canonical)

### C4 — "Full Landing Cycle" — 3 copies (CONTRADICTION + DUPLICATION)
- `AGENTS.md` lines 205-210 ("Ciclo completo ou nada")
- `VALIDATE_ON_CHANGE.md` Rule 3
- `rules/coordination/full-landing-cycle.md` (canonical)

### C5 — "No Rush / WIP" — 2-3 copies (DUPLICATION)
- `AGENTS.md` lines 160-165
- `VALIDATE_ON_CHANGE.md` Rule 2
- `rules/coordination/wip-persistence.md` (canonical, slightly different framing)

### C6 — Additional Duplicated Laws in AGENTS.md
- Green/green landing: AGENTS.md lines 172-175 ↔ `rules/coordination/green-green-landing.md`
- Strict typing: AGENTS.md lines 179-182 ↔ `rules/ethics/strict-typed-quality.md`
- Zero residue: AGENTS.md line 138 ↔ `rules/runtime/zero-residue.md`
- Operator precedence: AGENTS.md line 17 ↔ `rules/coordination/operator-precedence.md`
- Fix-forward permanente: AGENTS.md lines 130-131 ↔ `rules/coordination/fix-forward-collaboration.md`

### C7 — Stale/Project-Specific Facts in AGENTS.md
- Lines 89-101: "FLEXT project law" — FLEXT-specific architecture inline; canonical home is `rules/architecture/internal-clean-architecture.md`
- Lines 115-126: "Operator directive (auto-injected)" — specific dates, tool names (ast-grep/make mod/crg/LSP), project specifics
- Lines 128-183: "Operator cycle lessons" — 55 lines of operational specifics (cosmos-main, Portuguese terminology, specific dates)
- Lines 191-198: "Sem locks de frota" — fleet-specific lockfile prohibition

### C8 — Size
- `AGENTS.md`: 211 lines, ~44% is inline rules duplicated elsewhere
- "Operator cycle lessons" alone: 55 lines
- No rule index/manifest in `rules/` (no `rules/index.md` or `rules/README.md`)

### C9 — Link Validation
All links from AGENTS.md resolve: `VALIDATE_ON_CHANGE.md` ✓, `README.md` ✓, `rules/` ✓, `skills/` ✓, `docs/adr/README.md` ✓, `rules/coordination/gascity.md` ✓, `rules/architecture/internal-clean-architecture.md` ✓, `rules/workflow/full-standards-conformance-sweep.md` ✓. No broken links found in root files.

## Refactoring Strategy

**Principle**: AGENTS.md becomes the minimal inviolable prelude + structured links to categorized authorities. All "universal laws" live in their canonical `rules/` files; AGENTS.md references them.

## File Changes

**Hard constraint**: Lines 1-37 (prelude) + exactly one blank line must be preserved. `law_surface.py` validates this programmatically. Content after the blank line is the refactored section. Target final file: ~80 lines total (prelude 37 + essential 40 + links 10-15).

### 1. `AGENTS.md` — Major rewrite (minimal root)

**Keep (preserved material rules):**
- Lines 1-37: `AIHUB-INVIOLABLE-LAW-PRELUDE` — core universal law, stays intact
- Lines 39-62: Package identity, public contract, development guidance — condense, link expanded detail
- Lines 64-71: Repository development — condense to 3-4 lines with link to `rules/`
- Lines 103-111: Lifecycle — condense to 3-4 lines with links

**Remove inline, replace with links:**
- Lines 87-101 "FLEXT project law" → link to `rules/architecture/internal-clean-architecture.md` (already has full canonical text)
- Lines 113-126 "Operator directive" → link to `VALIDATE_ON_CHANGE.md` + `rules/coordination/operator-precedence.md`
- Lines 128-183 "Operator cycle lessons" → link to categorized rules (see mapping below)
- Line 189 "Full-standards-conformance-sweep" reference → already correct, keep

**Add:** Rule-to-category mapping section with links organized by domain.

**Precedence fix**: Replace inline precedence statement (line 17) with citation: "Authority order per `rules/coordination/operator-precedence.md`."

### 2. `VALIDATE_ON_CHANGE.md` — Preface + link to canonical rule

- Keep Rule 1-5 content (it's the canonical validate-on-change for this document's audience)
- Replace line 107 standalone precedence statement with: "Precedence per `rules/coordination/operator-precedence.md`."
- Remove duplication with `rules/coordination/validate-on-change.md` by noting it as the canonical English version and keeping this as the operator-mandate version

### 3. `rules/coordination/operator-precedence.md` — Add cross-reference

- Already the canonical precedence authority. No content change needed, but ensure AGENTS.md and VALIDATE_ON_CHANGE.md cite it.

### 4. New: `rules/README.md` — Category index (owner manifest for progressive disclosure)

Create an index that maps every rule category to its files and summarizes scope. This serves as the "owner manifest that directly structures progressive disclosure" — it tells agents which category owns which domain, enables targeted loading, and prevents inline duplication.

Structure:
```
# Rules Index

By category:
- [Architecture](rules/architecture/) — clean architecture, DI, topology, ownership
- [Coordination](rules/coordination/) — lifecycle, beads, operator alignment, sessions
- [Ethics](rules/ethics/) — integrity, truth, never-deduce, test-reality
- [Runtime](rules/runtime/) — execution, residue, environment, fail-fast
- [Workflow](rules/workflow/) — discovery, generation, documentation, gates
- [Security](rules/security/) — supply chain, scanners, prompt defense
- [Language](rules/language/) — runtime floor, authored language
- [Python](rules/python/) — config SSOT, Pydantic, typing
- [Flext](rules/flext/) — FLEXT-specific governance
- [Shell](rules/shell/) — bash guard rules
- [Git](rules/git/) — branch workflow, destructive guard, fork locality
- [Communication](rules/communication/) — caveman style
```

### 5. No changes to: `config/governance.json`, `config/workspace.yaml`, `config/skills.json`, `config/evals.json`

These are owner manifests. They reference rule IDs that remain valid. No stale project-specific facts to remove.

### 6. No changes to individual skill bundles, rule files, or command files

The refactoring only touches root governance architecture: `AGENTS.md`, `VALIDATE_ON_CHANGE.md` (operator mandate document), and the new `rules/README.md`.

## Content Mapping: AGENTS.md Inline Rules → Canonical Rule Files

| AGENTS.md content (lines) | Canonical location | Action |
|---|---|---|
| Lines 1-37 (Inviolable Law Prelude) | Stay in AGENTS.md | Keep |
| Lines 50-62 (Public contract) | Stay in AGENTS.md | Keep, condense |
| Lines 64-71 (Dev guidance) | Stay in AGENTS.md | Condense + link to `rules/` |
| Lines 87-101 (FLEXT project law) | `rules/architecture/internal-clean-architecture.md` | Remove inline → link |
| Lines 103-111 (Lifecycle) | Stay in AGENTS.md | Condense + link |
| Line 17 (Precedence) | `rules/coordination/operator-precedence.md` | Replace with citation |
| Lines 113-126 (Operator directive) | `VALIDATE_ON_CHANGE.md` | Remove → link |
| Lines 128-137 (Fix-forward, Pouso) | `rules/coordination/fix-forward-collaboration.md` | Remove → link |
| Lines 138 (Resíduo zero) | `rules/runtime/zero-residue.md` | Remove → link |
| Lines 140-141 (Gate bare) | `rules/runtime/strict-execution.md` | Remove → link |
| Lines 145-153 (Validate-on-change) | `rules/coordination/validate-on-change.md` | Remove → link |
| Lines 154-158 (Nunca deduze brief) | `rules/coordination/never-deduce.md` | Remove → link |
| Lines 160-165 (Nunca com pressa) | `rules/coordination/wip-persistence.md` | Remove → link |
| Lines 166-171 (Plano aprovado, P0) | `rules/coordination/plan-topic-monopoly.md` + `rules/coordination/lane-adoption.md` | Remove → link |
| Lines 172-175 (Green/green) | `rules/coordination/green-green-landing.md` | Remove → link |
| Lines 176-178 (Subagentes em massa) | `rules/coordination/parallel-delegation.md` + `rules/coordination/fanout-qa-publication.md` | Remove → link |
| Lines 179-182 (Tipagem strict) | `rules/ethics/strict-typed-quality.md` | Remove → link |
| Lines 183-189 (Full-standards) | `rules/workflow/full-standards-conformance-sweep.md` | Already linked, remove inline summary |
| Lines 191-198 (Locks de frota) | `rules/architecture/checkout-topology.md` (cross-link) | Remove → link to rules/architecture/ |
| Lines 199-204 (Nunca deduze expanded) | `rules/coordination/never-deduce.md` | Remove → link (dedup with line 154) |
| Lines 205-210 (Ciclo completo) | `rules/coordination/full-landing-cycle.md` | Remove → link |

## Validation

1. **PRELUDE constraint**: Run `python -c "from src.agents_governance.law_surface import LawSurface; LawSurface.load(Path('/home/marlonsc/agents'))"` — must succeed without ValueError. Pre-draft, post-draft, and final validation.
2. **Link validation**: Every markdown link in rewritten AGENTS.md resolves to an existing file
3. **No data loss**: Every rule cited from AGENTS.md exists in its canonical `rules/` target — verify by reading each target file
4. **Precedence consistency**: Search all `.md` files in `rules/` and root for "precedence" / "Precedência" — confirm only `rules/coordination/operator-precedence.md` states the hierarchy; others cite it
5. **No duplication**: Grep for "NUNCA.*deduzir" across `AGENTS.md` and `VALIDATE_ON_CHANGE.md` — should appear ≤1 time each after refactor
6. **File size**: Final `AGENTS.md` ~80 lines (prelude 37 + essential brief + links)
7. **Config manifests**: Verify `config/governance.json` bootstrap rules still resolve to existing files: `rtk python -c "import json; d=json.load(open('config/governance.json')); [print(x) for x in d['delivery']['guarantees']]"`
8. **Rule README**: Verify `rules/README.md` index covers all `rules/*/*.md` files
9. **Cross-link validation**: Verify all `rules/*/*.md` "See also" and "Compose with" references resolve to existing files

## Risk Mitigation

- Every removal from AGENTS.md is backed by an equivalent canonical rule file that already exists
- No new rule content is created — only relocation and linking
- `VALIDATE_ON_CHANGE.md` retains its full operator mandate text (it is the operator's document); only its precedence line changes
- `config/governance.json` references are by rule ID path; these paths don't change
