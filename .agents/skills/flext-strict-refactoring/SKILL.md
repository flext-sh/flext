---
name: flext-strict-refactoring
description: Strict cleanup rules for removing duplication, stale policy text, and conflicting guidance in docs and skills. Use when normalizing documentation content.

---

# Flext Strict Refactoring

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment

## Scope

- Documentation governance files:
  - `AGENTS.md`
  - `CLAUDE.md`
  - `.agents/INSTRUCTION_SURFACE.md`
  - `.agents/skills/*/SKILL.md`
- Agent pointer files:
  - `codex.md`
  - `.github/copilot-instructions.md`
  - `.gemini/styleguide.md`
  - `.clinerules`
  - `.windsurfrules`
  - `.continue/rules/flext.md`
  - `.cursor/rules/flext.mdc`
  - `CONVENTIONS.md`

## References

- `AGENTS.md` (canonical policy)
- `.agents/INSTRUCTION_SURFACE.md` (canonical loading manifest)
- `.agents/skills/skill-format-universal/SKILL.md`

## Rules

- Remove duplicated guidance when canonical source exists.
- Keep terminology consistent across related files.
- Delete stale sections that conflict with active policy.
- Preserve repository-relative paths in examples and references.
- When AGENTS or a core workflow/prompt/skill adds stricter execution law, propagate that change through the remaining relevant pointer and meta-skill surfaces in the same governance cycle.
- Meta-skills and pointer docs must reinforce mandatory impact analysis, surgical necessity, complete propagation, and required tool usage without copying AGENTS wholesale.
- Meta-skills that mention kwargs discipline must distinguish true dynamic option bags from fixed-shape APIs: `model_validate(kwargs)` for the former, explicit typed params + `model_validate({...})` for the latter.

Hard execution floor:

1. Read `AGENTS.md` §0 first.
2. Run `qlty smells --all --sarif --include-tests > /tmp/qlty_smells-tests.json` before edits.
3. One offender per cycle.
4. Origin search before helper (`u.*`, `m.*`, parent method, centralized utility).
5. New helper/proxy/wrapper without proof of no origin is invalid.
6. True option bag -> one `model_validate(kwargs)`; fixed-shape API -> explicit params + one packed `model_validate({...})`.
7. No manual kwargs key/type normalization when Pydantic can own payload.
8. No `Any`/`object` fallback in runtime refactor paths.
9. No completion claim without raw gate output (`ruff` -> `pyrefly` minimum after first edit).

No-mercy short card:

1. Canonical source first; no local policy mirrors.
2. One offender per cycle; no side quests.
3. Origin method/class before helper creation.
4. `**kwargs` only through one typed Pydantic validation path.
5. No `Any`/`object` fallback in runtime refactors.
6. No manual key/type normalization when `model_validate(...)` can own payload.
7. No completion claim without raw gate output.
- Pointer surfaces must send agents to `AGENTS.md` §0 explicitly when that section defines the startup law.
- For refactor/cleanup entrypoints, prefer one short start card (`qlty` first, one offender, origin before helper, `ruff` -> `pyrefly`) over diluted prose.

Brutal self-critique requirement (must appear before first patch):

1. Recurring failure risk in this cycle.
2. Exact stop-rule that blocks it.
3. Exact native replacement primitive (`Annotated`, validator, `TypeAdapter`, `model_copy`, `Discriminator`, `RootModel`, `TypeIs`, `match/case`).
4. Exact propagation command and first gate command.

## Instructions

- Compare candidate content against canonical source before copying.
- Prefer referencing canonical files over re-explaining identical policy.
- Keep each skill focused on domain-specific action, not global boilerplate.
- When normalizing docs, prioritize the still-unupdated meta surfaces first: pointer entrypoints, formatting rules, routing manifests, and documentation/refactor governance skills.
- Shorter and harder wins: remove filler before adding new rules.
- If a pointer file says only “read AGENTS.md”, tighten it to “read `AGENTS.md` §0 first” when the task mode is execution-heavy.

```bash
rg -n "single source of truth|Canonical source|AGENTS.md" AGENTS.md .agents/skills/*/SKILL.md
```

## Workflow

1. Detect duplicated sections across docs/skills.
2. Decide canonical location for each concept.
3. Propagate new mandatory execution rules to remaining meta surfaces that drive future edits.
4. Remove duplicates and replace with pointers.
5. Verify section completeness and coherence.

## Examples

Good:

```markdown
Canonical source: `AGENTS.md`.
```

Why good: one source reduces drift and conflict.

Bad:

```markdown
## Global Rules

[copy of 150 lines from AGENTS.md]
```

Why bad: duplicated policy rapidly becomes inconsistent.

## Verification

Make gates:

- `make check PROJECT=flext-core` — verify no regressions after refactoring
- `make val PROJECT=flext-core` — complexity + docstring gates
- `make test PROJECT=flext-core` — test suite must pass after any refactor
- `make val VALIDATE_SCOPE=workspace` — workspace-level validation

Policy checks:

- `rg -n "TODO|TBD|placeholder" .agents/skills/*/SKILL.md || true`
- `rg -n "(^|[\"'`])/(Users|home)/" .agents/skills/\*/SKILL.md || true`
- `rg -n "Canonical source:`AGENTS.md`|single source of truth" AGENTS.md codex.md .github/copilot-instructions.md .gemini/styleguide.md`
- `rg -n "scope|Serena|ast-grep|MCP|zero.*ruff|zero.*pyrefly|enforcement|pytest" AGENTS.md codex.md .agents/README.md .agents/skills/*.md .github/prompts/*.md`
