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

- `AGENTS.md` is canonical. If it already says it clearly, delete the duplicate.
- Duplicate frontmatter, repeated verification bullets, or stacked start cards are immediate cleanup targets.
- Meta surfaces must hit recurring failures directly: helper-first patches, manual kwargs normalization, loose constants/objects, magic literals, skipped propagation, positive-LOC refactors.
- No `Any` / `object` fallback language in runtime refactor guidance.
- Cut filler before adding new rules.
- If `AGENTS.md` gets stricter, patch the drifting meta surface in the same cycle.
- If a pointer already says `AGENTS.md` §0 first and does not drift, leave it alone.

## Instructions

- Read `AGENTS.md` §0 first.
- Run `qlty smells --all --sarif --include-tests > /tmp/qlty_smells-tests.json` before edits.
- Keep startup law short: one offender, origin before helper, `ruff` -> `pyrefly`.
- Pointer files point. They do not mirror policy.
- True option bags say `model_validate(kwargs)`. Fixed-shape APIs say explicit typed params + one `model_validate({...})`.
- No loose module-scope constants/objects. Put them in the existing owner class or compose the correct `c.*` owner.
- Parameter-count smell is not permission to add a carrier model, widen a fixed signature, or invent a helper.
- Name the native deletion primitive: `model_copy(update=...)`, cached `TypeAdapter`, `Annotated`, validators, `computed_field`, `Discriminator`, `RootModel`, `TypeIs`, `match/case`.
- The brutal self-critique is mandatory on execution-heavy surfaces: risk, stop-rule, primitive, propagation + first gate.
- Read `AGENTS.md` §0 first, then patch the smallest drifting meta surface.
- Prefer one hard start card over stacked repeated mini-cards.
- Keep meta-skills operational: one failure pattern, one counter-rule, one verification command.
- Use repository-relative paths and direct symbol names.

## Workflow

1. Run `qlty smells --all --sarif --include-tests > /tmp/qlty_smells-tests.json`.
2. Read `AGENTS.md` §0 and isolate the exact recurring failure.
3. Patch `AGENTS.md` first only if the law changes.
4. Patch only the drifting meta skills or pointers.
5. After the first edit, run the minimum relevant gate.
6. Verify drift with `rg` and delete leftover mirror text in the same cycle.

## Examples

Good:

```markdown
Read `AGENTS.md` §0 first.
Run `qlty`, pick one offender, search origin before helper, then gate the first edit with `ruff` -> `pyrefly`.
```

Why good: one hard start card, one canonical source, one execution order.

Bad:

```markdown
Local rules first.
[copied startup law]
[second mini-card repeating the same law]
```

Why bad: it creates policy drift, hides the real source of truth, and makes agents obey duplicate text instead of the canonical surface.

## Verification

- `rg -n "AGENTS.md §0|qlty smells --all --sarif --include-tests|origin before helper|ruff -> pyrefly" AGENTS.md .github/copilot-instructions.md .agents/skills/*/SKILL.md`
- `rg -n "model_validate\(kwargs\)|model_validate\(\{.*\}\)|model_copy\(update=|TypeAdapter|Annotated|TypeIs|match/case" AGENTS.md .agents/skills/*/SKILL.md`
- `rg -n "full policy|copy of .*AGENTS|local rules first" .github/copilot-instructions.md codex.md .agents/skills/*/SKILL.md`
- `rg -n "^---$|\[copied startup law\]|stacked mini-card|Duplicate frontmatter" .agents/skills/flext-strict-refactoring/SKILL.md .agents/INSTRUCTION_SURFACE.md`
