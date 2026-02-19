---
name: flext-strict-refactoring
description: Strict cleanup rules for removing duplication, stale policy text, and conflicting guidance in docs and skills. Use when normalizing documentation content.
---

# Flext Strict Refactoring

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment


## Scope

- Documentation governance files:
  - `CLAUDE.md`
  - `AGENTS.md`
  - `.claude/skills/*/SKILL.md`
- Agent pointer files:
  - `codex.md`
  - `.github/copilot-instructions.md`
  - `.gemini/styleguide.md`

## References

- `AGENTS.md` (no-duplication maintenance rule)
- `CLAUDE.md` (canonical policy)
- `.claude/skills/skill-format-universal/SKILL.md`

## Rules

- Remove duplicated guidance when canonical source exists.
- Keep terminology consistent across related files.
- Delete stale sections that conflict with active policy.
- Preserve repository-relative paths in examples and references.

## Instructions

- Compare candidate content against canonical source before copying.
- Prefer referencing canonical files over re-explaining identical policy.
- Keep each skill focused on domain-specific action, not global boilerplate.

```bash
rg -n "single source of truth|Canonical source|CLAUDE.md" AGENTS.md .claude/skills/*/SKILL.md
```

## Workflow

1. Detect duplicated sections across docs/skills.
2. Decide canonical location for each concept.
3. Remove duplicates and replace with pointers.
4. Verify section completeness and coherence.

## Examples

Good:

```markdown
Canonical source: `CLAUDE.md`.
```

Why good: one source reduces drift and conflict.

Bad:

```markdown
## Global Rules
[copy of 150 lines from CLAUDE.md]
```

Why bad: duplicated policy rapidly becomes inconsistent.

## Verification

Make gates:

- `make check PROJECT=flext-core` — verify no regressions after refactoring
- `make validate PROJECT=flext-core` — complexity + docstring gates
- `make test PROJECT=flext-core` — test suite must pass after any refactor
- `make validate VALIDATE_SCOPE=workspace` — workspace-level validation

Policy checks:

- `rg -n "TODO|TBD|placeholder" .claude/skills/*/SKILL.md || true`
- `rg -n "(^|[\"'`])/(Users|home)/" .claude/skills/*/SKILL.md || true`
- `rg -n "Canonical source:`CLAUDE.md`|single source of truth" AGENTS.md codex.md .github/copilot-instructions.md .gemini/styleguide.md`
