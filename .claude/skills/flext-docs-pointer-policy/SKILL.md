<!-- TOC START -->

- [Scope](#scope)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
- [Workflow](#workflow)
- [Examples](#examples)
- [Full Policy](#full-policy)
- [Verification](#verification)
<!-- TOC END -->

---

name: flext-docs-pointer-policy
description: Canonical documentation-governance policy for agent configs: one root source, lightweight pointers everywhere else.

---

# Flext Docs Pointer Policy

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment

## Scope

- Root governance docs (`CLAUDE.md`, `AGENTS.md`)
- Agent pointer files under root and tool directories

## References

- `AGENTS.md` states a single source of truth: root `CLAUDE.md`.
- `AGENTS.md` maps all agent config entrypoints and enforces pointer-file limits.
- `docs/architecture/adr/README.md` tracks architecture decisions for governance changes.
- Pointer files reference root policy:
  - `.github/copilot-instructions.md`
  - `.gemini/styleguide.md`
  - `.cursor/rules/flext.mdc`
  - `.clinerules`
  - `.windsurfrules`
  - `.continue/rules/flext.md`
  - `CONVENTIONS.md`
  - `codex.md`

## Rules

- All normative rule updates happen in `CLAUDE.md` first.
- Agent-specific files remain pointers, not policy mirrors.
- Never duplicate governance rules across multiple agent files.
- Pointer files must remain concise and reference scoped skills instead of restating them.

## Instructions

- `.github/copilot-instructions.md` points to root canonical governance.
- `.gemini/styleguide.md` defines tool-specific behavior without duplicating policy text.
- `.cursor/rules/flext.mdc` keeps frontmatter + brief pointer instructions only.
- `.clinerules`, `.windsurfrules`, `.continue/rules/flext.md` remain concise bridge docs.
- `CONVENTIONS.md` and `codex.md` behave as entrypoint pointers for their tools.

## Workflow

1. Update `CLAUDE.md` when governance changes.
2. Check `AGENTS.md` mapping for impacted pointers.
3. Update only references or short tool-specific usage hints in pointer files.
4. Remove duplicated rule text from pointers.

## Examples

```md
<!-- Good: concise pointer -->

Canonical source: `CLAUDE.md` at repository root.
Use `.claude/skills/` for scoped behavior.
```

```md
<!-- Bad: duplicated governance spec -->

## Full Policy

<hundreds of lines copied from CLAUDE.md>
```

Why bad: duplicated policy drifts over time and breaks the single-source governance model.

```md
<!-- Bad: agent-specific contradiction -->

Use local rules in this file as priority over CLAUDE.md.
```

Why bad: inverts repository governance and creates conflicting behavior between tools.

## Verification

Make gates:

- `make validate VALIDATE_SCOPE=workspace` — workspace validation ensures doc consistency

Policy checks:

- `rg -n "single source of truth|CLAUDE.md|Never duplicate rules|under 50 lines" AGENTS.md`
- `rg -n "Canonical source|CLAUDE.md" .github/copilot-instructions.md .gemini/styleguide.md .cursor/rules/flext.mdc .clinerules .windsurfrules .continue/rules/flext.md CONVENTIONS.md codex.md`
- `rg -n "full policy|single source" CLAUDE.md AGENTS.md`
- `wc -l .github/copilot-instructions.md .gemini/styleguide.md .cursor/rules/flext.mdc .clinerules .windsurfrules .continue/rules/flext.md CONVENTIONS.md codex.md`
