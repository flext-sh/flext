---
name: flext-audit-pipeline
description: Use when running or wiring the SSOT enforcement audit (`make audit`) that surfaces `ENFORCE-039/041/043/044` violations across the workspace via `FlextInfraEnforcementAuditor` and dispatches mkdocs python-codeblock parity via `FlextInfraDocAuditor`. Pointer-only — no parallel policy.
---

# FLEXT Audit Pipeline

**Reviewed**: 2026-04-25 | **Scope**: `make audit` verb + canonical CLI route + reused infrastructure

## Scope

- `flext-infra/src/flext_infra/refactor/enforcement_auditor.py` — `FlextInfraEnforcementAuditor`
- `flext-infra/src/flext_infra/_models/refactor.py` — `m.Infra.RefactorAuditInput`
- `flext-infra/src/flext_infra/cli.py` — `_route(name="audit", ...)` under `CLI_GROUP_REFACTOR`
- `flext-infra/src/flext_infra/_constants/make.py` — `audit` verb + `SCOPE`/`NAMESPACE`/`GATES`/`PROPAGATE` selectors
- `flext-infra/src/flext_infra/templates/base_verbs.mk.j2` — `audit:` recipe (templated)
- `flext-infra/src/flext_infra/docs/auditor.py` — `FlextInfraDocAuditor` (reused for `GATES=docs`)

## References

- `AGENTS.md` §3.2 / §3.4 / §3.5 / §3.6 / §3.8 — anchors for ENFORCE-039..044 + Documentation Code Integrity
- `.agents/skills/flext-enforcement-catalog/SKILL.md` — catalog SSOT (`c.ENFORCEMENT_CATALOG`)
- `.agents/skills/flext-quality-gates/SKILL.md` — gate execution model
- `.agents/skills/flext-refactoring-workflow/SKILL.md` — rope-based auto-fix safety contract
- `~/.claude/plans/use-os-recursos-de-peppy-thacker.md` — audit pipeline plan (A-PT lane)

## Rules

- **No parallel infrastructure**: the audit pipeline reuses `m.Infra.Census.{Violation,ProjectReport,WorkspaceReport}`, `u.Infra.discover_project_roots`, `mm.WriteMixin → ScopeMixin`, and the `_route` registration pattern. Do not introduce new orchestrators, safety managers, readers, or violation models.
- **One auditor per source kind**: `FlextInfraEnforcementAuditor` covers every `EnforcementBeartypeSource` rule via the `c.ENFORCEMENT_RULES` tag dispatch. Adding a new beartype rule does not require a new auditor — extend the existing one.
- **No argparse**: the verb is wired exclusively through the canonical `_route(name=, model_cls=m.Infra.<Verb>Input, handler=lambda params: <Cls>.execute_command(params))` pattern in `cli.py`. Raw `argparse` in `engine.py` is forbidden.
- **Pydantic input model rule**: every CLI verb takes `m.Infra.<Verb>Input` extending `mm.WriteMixin` (or `mm.ReadMixin`) — no extra fields beyond `ScopeMixin` unless truly required. Field aliases use kebab-case (`alias="projects-filter"`).
- **`GATES=docs` route**: dispatches to `FlextInfraDocAuditor.audit_scope(checks=("python-codeblocks",))` per AGENTS.md §3.8 mandate. The audit verb does not own the docs auditor — it routes.
- **Rollback**: rope-backed auto-fix uses `FlextInfraRefactorSafetyManager`'s `.bak` flow. Never `git checkout`.

## Instructions

- To add a new beartype-dispatched rule: register `EnforcementRuleSpec` in `c.ENFORCEMENT_CATALOG` with `EnforcementBeartypeSource(hook="check_<tag>")`, add the `check_<tag>` static method on `FlextUtilitiesBeartypeEngine`, add the dispatch arm in `FlextUtilitiesEnforcementCollect._namespace_items`, and update `FlextInfraEnforcementAuditor._detect_node` if AST-walk detection is required for workspace-wide audit.
- To add a new selector: extend `m.Infra.RefactorAuditInput` (only if the value is not already on `ScopeMixin`/`WriteMixin`).
- To regenerate the Makefile recipe: edit `templates/base_verbs.mk.j2`, then run `make gen` from the workspace root.

## Workflow

1. Edit catalog + hook + dispatch arm in `flext-core` (when adding a new rule).
2. Edit `FlextInfraEnforcementAuditor._detect_node` in `flext-infra` (only if workspace-wide AST detection differs from the runtime hook signature).
3. Run `make check PROJECT=flext-core` and `make check PROJECT=flext-infra` after every edit.
4. Run `make audit` to surface violations workspace-wide; `make audit GATES=docs` for codeblock parity; `make audit FIX=1` to apply rope-backed auto-fix where supported.

## Examples

```bash
# Workspace-wide audit (dry-run, all rules)
make audit

# Filter to a project
make audit PROJECTS="flext-core"

# Apply auto-fix (ENFORCE-043 only — others are detect-only by design)
make audit FIX=1 PROJECTS="flext-meltano"

# mkdocs python-codeblock parity
make audit GATES=docs
```

Real-world apply evidence (see `.reports/audit/improvement-summary.md` for the
full per-project breakdown):

```text
=== Workspace audit run 2026-04-25 ===
Projects audited:        18
BEFORE total violations: 85   (52 ENFORCE-043 + 33 ENFORCE-044)
Auto-fixes applied:       0   (rope create_inline conservative — refused all
                               class-method / dunder / multi-call-site wrappers,
                               which is the correct safe outcome)
AFTER total violations:  85
make check OK post-apply: 18/18 ✓
make test  OK post-apply: 16/18 (2 pre-existing failures unchanged — verifiably
                                  not caused by apply since 0 fixes were written)
```

The conservative behavior is by contract: rope's `create_inline` refuses unsafe
inlines rather than risk subclass-dispatch / `super()` / call-site-as-callable
breakage. Aggressive rewrites belong in a follow-up plan with custom text
rewriters that carry stricter safety predicates than rope's generic inline.

## Verification

- `make check PROJECT=flext-infra` — zero ruff + pyrefly errors.
- `make audit` — exits 0 when zero violations; exits 1 when violations found.
- `make audit GATES=docs` — exits 0 when every Python code fence in `docs/**/*.md` parses + lints clean.
