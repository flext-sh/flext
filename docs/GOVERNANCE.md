# FLEXT Governance Router

> **Authority**: This file routes governance concerns to their canonical owners. No duplicate text — lines only.
>
> **Composition**: Global (`~/.agents/AGENTS.md`) → FLEXT root (`AGENTS.md`) → `flext-law` skill → scope `AGENTS.md` → active Bead.
>
> **Version**: 0.12.x line; ADR-015 ratified.

---

## Router Table

| Concern | Canonical Owner | Artifact | Enforcement |
|---------|-----------------|----------|-------------|
| **Universal conduct** | `~/.agents/AGENTS.md` | `UNIVERSAL_CORE.md` | Make verbs + skills |
| **FLEXT architecture** | Root `AGENTS.md` | `.agents/skills/flext-law/SKILL.md` | `make check` + gates |
| **Consumer grammar (R1)** | `flext-core` | `docs/standards/consumption-law.md` §R1 | ENFORCE-099 |
| **Duplication (R2)** | `flext-infra` | `flext_infra.gates.duplication` | ENFORCE-100+ |
| **Layer law (R3)** | `flext-infra` | `flext_infra.gates.namespace` | NS-STRUCT/NS-CONTRACT |
| **Gates as products (R4)** | `flext-infra` + `flext-core` | `[tool.flext.project]` + budget gate | ENFORCE-101+ |
| **Release consumption (R5)** | Workspace + all members | `config/codegen.yaml` + `AI_HUB_CONSUMER.md` | Release pipeline |
| **Contribution path (R6)** | Gas City + this repo | `docs/GOVERNANCE.md` + bead workflow | Workflow gates |
| **Config/settings SSOT** | `flext-core` | `config/*.yaml` → codegen | ADR-005, ADR-012 |
| **Codegen monopoly** | `flext-infra` | `codegen.yaml` + templates | `make gen APPLY=Y` |
| **Codemod governance** | `flext-infra` | `ast-grep` rules + `make mod` | ADR-014 |
| **ADR process** | This repo | `docs/architecture/adr/` | ADR-015 §References |
| **Beads tracker** | Gas City | `bd` CLI + Dolt | Beads verification rule |
| **Workspace lifecycle** | Gas City | `gc-*` CLI | Workspace policy |

---

## Workstream → Gate Mapping (ADR-015)

| WS | Law | Gate(s) | ENFORCE IDs | Owner |
|----|-----|---------|-------------|-------|
| F1 | R1 Facade-only import | `consumer_import_violations` | 099 | flext-infra detector |
| F2 | R2 No duplication | `duplication` (extended) | 100+ | flext-infra gate |
| F3 | R3 Layer law | `namespace`, `canonical_alias` | 080, 026-033 | flext-infra gates |
| F4 | R4 Gates as products | `budget` (new), `conform` | 101+ | flext-infra + flext-core |
| F5 | R5 Release consumption | `release`, `consumer_docs` | — | Workspace pipeline |
| F6 | R6 Contribution path | `workflow`, `bead_verification` | — | Gas City + this repo |
| F7 | Doc hardening | `docs_auditor`, `gate_docs` | — | flext-infra docs |

---

## Anti-Hardcode Router (Binding)

| Prohibited Pattern | Replacement (SSOT) |
|--------------------|-------------------|
| `BOUNDARY_SKIP_PROJECTS` | Derived from `__all__` + `_LAZY_IMPORTS` |
| `CLICK_FILES` / `TOML_ALLOWED` | `[tool.flext.project]` config keys |
| `BOUNDARY_FLEXT_CLI_CONCRETE_RE` | `FlextUtilitiesFamilySurface` derivation |
| `startswith("flext_")` literal | `c.Infra.NAMESPACE_FAMILY_PREFIX` |
| `ENFORCEMENT_PROJECT_ALIAS_OWNERS` (31 names) | `project_alias_owners()` runtime |
| `ENFORCEMENT_COMPATIBILITY_ALIAS_RENAMES` (frozen) | `compatibility_alias_renames()` runtime |
| Hardcoded test fixture lists | Synthetic runtime-derived violations |

---

## Gate Registry (Canonical)

| Gate ID | Class | Source Kind | Violation Field | Config Key |
|---------|-------|-------------|-----------------|------------|
| `namespace` | `FlextInfraNamespaceGate` | `flext_infra_detector` | — | `tool.flext.project.namespace` |
| `canonical_alias` | `FlextInfraCanonicalAliasGate` | `flext_infra_detector` | `foreign_canonical_alias_violations` | `tool.flext.project.canonical_alias` |
| `duplication` | `FlextInfraDuplicationGate` | `jscpd` | — | `tool.flext.project.duplication` |
| `consumer_import_violations` | (declarative) | `flext_infra_detector` | `consumer_import_violations` | `tool.flext.project.consumer_import` |
| `silent_failure` | `FlextInfraSilentFailureGate` | `flext_infra_detector` | `silent_failure_violations` | `tool.flext.project.silent_failure` |
| `boundary` | `FlextInfraBoundaryGate` | `flext_infra_detector` | — | `tool.flext.project.boundary` |
| `loc_cap` | `FlextInfraLocCapGate` | `flext_infra_detector` | — | `tool.flext.project.loc_cap` |
| `tier_whitelist` | `FlextInfraTierWhitelistGate` | `flext_infra_detector` | — | `tool.flext.project.tier_whitelist` |
| `mypy` | `FlextInfraMypyGate` | `mypy` | — | `tool.flext.project.mypy` |
| `pyrefly` | `FlextInfraPyreflyGate` | `pyrefly` | — | `tool.flext.project.pyrefly` |
| `pyright` | `FlextInfraPyrightGate` | `pyright` | — | `tool.flext.project.pyright` |
| `ruff_lint` | `FlextInfraRuffLintGate` | `ruff` | — | `tool.flext.project.ruff_lint` |
| `ruff_format` | `FlextInfraRuffFormatGate` | `ruff` | — | `tool.flext.project.ruff_format` |
| `codemod` | `FlextInfraCodemodGate` | `codemod` | — | `tool.flext.project.codemod` |
| `budget` | `FlextInfraBudgetGate` (new) | `budget` | — | `tool.fleft.project.budget` |

> **Registry divergence = hard error** — every gate must have a row in this table, a `_gate_classes` entry, a `SARIF_TOOL_INFO` row, and a `codegen.yaml` projection.

---

## Bead Lifecycle (R6)

```mermaid
flowchart LR
    A[bd create] --> B[gc bd create --rig aihub]
    B --> C[gc sling aihub/<role> <bead> --on <formula>]
    C --> D[Formula creates workspace + branch]
    D --> E[Implement on lane]
    E --> F[make fix/fmt/check APPLY=Y]
    F --> G[WIP commit (scoped paths)]
    G --> H[PR → review → merge --no-ff]
    H --> I[Gates on merged SHA]
    I --> J[Roll-up gitlinks in super]
    J --> K[bd close with 4 evidences]
```

**Four evidences for closure**:
1. Registered bead state
2. Git history on integration lane
3. Measured reality (command, cwd, exit code, decisive output)
4. Current integrated code

---

## Anti-Patterns (Never Do)

- ❌ Hand-edit generated projections (`# AUTO-GENERATED` files, `[MANAGED]` pyproject sections)
- ❌ Bypass `make` verbs (`uv`, `ruff`, `pyrefly`, `pytest` directly)
- ❌ Use `WHAT=` selectors unless explicitly necessary
- ❌ `--no-verify` on commits
- ❌ `git add -A` (scoped paths only)
- ❌ `git reset/checkout/restore/clean/stash` on shared work (fix-forward only)
- ❌ Create markdown TODOs (use `bd` for ALL tracking)
- ❌ Skip gate because "pre-existing" or "cosmetic" (fix at root cause)

---

## Escalation Path

1. **Rule conflict** → present both with numbers, ask operator
2. **Genuine ambiguity** → one targeted question, continue
3. **Destructive/irreversible action** → STOP, ask operator
4. **External blocker** → exhaust all authorized technical actions first

> **Operator word is supreme** — newest explicit instruction overrides ALL lower authority including injected context.