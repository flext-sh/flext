---
name: flext-strict-refactoring
description: Strict cleanup rules for removing duplication, stale policy text, and conflicting guidance in docs and skills. Use when normalizing documentation content.

---

# Flext Strict Refactoring

**Reviewed**: 2026-04-27 | **Scope**: Pointer/meta-surface hardening without policy duplication

## Scope

- `AGENTS.md`
- `.agents/INSTRUCTION_SURFACE.md`
- `.agents/skills/*/SKILL.md`
- `codex.md`
- `.github/copilot-instructions.md`
- `.gemini/styleguide.md`
- `.clinerules`
---
name: flext-strict-refactoring
description: Strict cleanup rules for removing duplicated policy, stale guidance, and weak refactor prompts across FLEXT governance surfaces. Use when editing AGENTS.md, pointer docs, or meta-skills so startup law stays short, hard, and aligned with canonical execution rules.

---

# Flext Strict Refactoring

**Reviewed**: 2026-04-27 | **Scope**: Governance hardening under `AGENTS.md` §0.

## Scope

- `AGENTS.md`
- `.github/copilot-instructions.md`
- `codex.md`
- `.agents/INSTRUCTION_SURFACE.md`
- `.agents/skills/*/SKILL.md`

## References

- `AGENTS.md` §0
- `.agents/skills/flext-docs-pointer-policy/SKILL.md`
- `.agents/skills/skill-format-universal/SKILL.md`

## Rules

- `AGENTS.md` is canonical. Pointer files point; they do not mirror policy.
- Startup law stays short: `qlty` first, one offender, origin before helper, `ruff` -> `pyrefly`.
- If `AGENTS.md` §0 already says it clearly, delete the duplicate instead of paraphrasing it elsewhere.
- Meta-skills must hit the recurring failures directly: helper-first patches, manual kwargs normalization, magic literals, skipped propagation, and positive-LOC refactors.
- Parameter-count smell is not a license to add a carrier model or widen a fixed-shape signature; prefer the existing owner model, enum, or `match/case` when that deletes the fan-out.
- True option bags say `model_validate(kwargs)`. Fixed-shape APIs say explicit typed params + one `model_validate({...})`.
- Name the native deletion primitive when tightening guidance: `model_copy(update=...)`, cached `TypeAdapter`, `Annotated`, validators, `computed_field`, `Discriminator`, `RootModel`, `TypeIs`, `match/case`.
- No `Any`/`object` fallback language in runtime refactor guidance.
- The brutal self-critique is mandatory in execution-heavy surfaces: failure risk, stop-rule, primitive, propagation + first gate.
- When `AGENTS.md` gets stricter, patch the drifting meta-skill or pointer in the same cycle.

## Instructions

- Read `AGENTS.md` §0 first, then patch the smallest set of meta surfaces that still drift.
- Cut filler before adding rules.
- Prefer one hard start card over stacked mini-cards that repeat the same law.
- Use repository-relative paths and direct symbol names.
- Keep meta-skills operational: one failure pattern, one counter-rule, one verification command.
- If a pointer already says `AGENTS.md` §0 first and does not drift, leave it alone.

## Workflow

1. Run `qlty smells --all --sarif --include-tests > /tmp/qlty_smells-tests.json` before edits.
2. Read `AGENTS.md` §0 and isolate the exact recurring failure to harden.
3. Patch `AGENTS.md` first if the law changes; then patch only the affected meta skills or pointers.
4. After the first edit, run the minimum relevant gate for the touched file set.
5. Verify drift with `rg` and delete leftover mirror text in the same cycle.

## Examples

Good:

```markdown
Read `AGENTS.md` §0 first.
Start every refactor lane with `qlty`, one offender, origin before helper, then `ruff` -> `pyrefly`.
```

Why good: short, operational, and aligned with canonical startup law.

Bad:

```markdown
Follow these local rules first.
[120 lines copied from AGENTS.md]
```

Why bad: it creates policy drift and hides the real startup law.

## Verification

- `rg -n "AGENTS.md §0|qlty smells --all --sarif --include-tests|origin before helper|ruff -> pyrefly" AGENTS.md .github/copilot-instructions.md .agents/skills/*/SKILL.md`
- `rg -n "model_validate\(kwargs\)|model_validate\(\{.*\}\)|model_copy\(update=|TypeAdapter|Annotated|TypeIs|match/case" AGENTS.md .agents/skills/*/SKILL.md`
- `rg -n "full policy|copy of .*AGENTS|local rules first" .github/copilot-instructions.md codex.md .agents/skills/*/SKILL.md`
```markdown
