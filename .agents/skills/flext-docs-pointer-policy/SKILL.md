---
name: flext-docs-pointer-policy
description: Use when creating or editing documentation across AGENTS.md, skills, README files, or agent configs. Enforces the one-root-source policy: single authoritative document with lightweight pointers everywhere else. No duplication of governance across files.

---

# Flext Docs Pointer Policy

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment

## Scope

- Root governance docs (`AGENTS.md` canonical)
- Agent pointer files under root and tool directories

## References

- `AGENTS.md` states a single source of truth: root `AGENTS.md`.
- Pointer/index files must never diverge from `AGENTS.md` policy.
- `docs/architecture/adr/README.md` tracks architecture decisions for governance changes.
- External governance patterns:
  - IETF process model (`https://www.ietf.org/about/process/`) for canonical source discipline.
  - Linux `MAINTAINERS` structure (`https://www.kernel.org/doc/html/latest/maintainer/`) for ownership pointers.
  - Python Developer Guide (`https://devguide.python.org/`) for hierarchical docs navigation.
  - Rust governance (`https://www.rust-lang.org/governance`) for role-based documentation ownership.
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

- All normative rule updates happen in `AGENTS.md` first.
- Agent-specific files remain pointers, not policy mirrors.
- Never duplicate governance rules across multiple agent files.
- Pointer files must remain concise and reference scoped skills instead of restating them.
- Pointer files must reflect current mandatory routing for prompts, Scope, Serena, `ast-grep`, MCP, and zero-debt quality gates by pointing to the canonical surfaces that define them.

## Instructions

- `.github/copilot-instructions.md` points to root canonical governance.
- `.gemini/styleguide.md` defines tool-specific behavior without duplicating policy text.
- `.cursor/rules/flext.mdc` keeps frontmatter + brief pointer instructions only.
- `.clinerules`, `.windsurfrules`, `.continue/rules/flext.md` remain concise bridge docs.
- `CONVENTIONS.md` and `codex.md` behave as entrypoint pointers for their tools.
- `.agents/README.md` should point to `AGENTS.md`, `.agents/INSTRUCTION_SURFACE.md`, and prompt-routing surfaces rather than restating policy.

## Workflow

1. **Pre-scan**: inventory pointer files and identify drift from canonical wording.
2. **Remediation**: update references and remove duplicated policy content.
3. **Propagation**: when AGENTS or a core skill/prompt becomes stricter, update remaining pointers in the same cycle.
4. **Verification**: run scanner checks for `AGENTS.md` presence and legacy reference absence.
5. **Drift prevention**: keep checks in CI/automation and re-run after every governance edit.

## Examples

```md
<!-- Good: concise pointer -->

Canonical source: `AGENTS.md` at repository root.
Use `.agents/skills/` for scoped behavior.
```

```md
<!-- Bad: duplicated governance spec -->

## Full Policy

<hundreds of lines copied from AGENTS.md>
```

Why bad: duplicated policy drifts over time and breaks the single-source governance model.

```md
<!-- Bad: agent-specific contradiction -->

Use local rules in this file as priority over AGENTS.md.
```

Why bad: inverts repository governance and creates conflicting behavior between tools.

## Verification

Make gates:

- `make val VALIDATE_SCOPE=workspace` — workspace validation ensures doc consistency

Policy checks:

- `rg -n "single source of truth|AGENTS.md|Never duplicate rules|under 50 lines" AGENTS.md`
- `rg -n "Canonical source|AGENTS.md" .github/copilot-instructions.md .gemini/styleguide.md .cursor/rules/flext.mdc .clinerules .windsurfrules .continue/rules/flext.md CONVENTIONS.md codex.md`
- `rg -n "full policy|single source" AGENTS.md`
- `wc -l .github/copilot-instructions.md .gemini/styleguide.md .cursor/rules/flext.mdc .clinerules .windsurfrules .continue/rules/flext.md CONVENTIONS.md codex.md`
- `python3 scripts/core/text_pattern_scanner.py --pattern "AGENTS\.md" --match present --include .github/copilot-instructions.md --include .gemini/styleguide.md --include .cursor/rules/flext.mdc --include .clinerules --include .windsurfrules --include .continue/rules/flext.md --include CONVENTIONS.md --include codex.md`
- `python3 scripts/core/text_pattern_scanner.py --pattern "[Cc]LAUDE\.md" --match absent --include .github/copilot-instructions.md --include .gemini/styleguide.md --include .cursor/rules/flext.mdc --include .clinerules --include .windsurfrules --include .continue/rules/flext.md --include CONVENTIONS.md --include codex.md`
