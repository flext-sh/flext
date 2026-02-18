---
name: skill-format-universal
description: Canonical format for project SKILL.md files using Anthropic standards and FLEXT evidence. Use when creating or rewriting any skill.
---

# Skill Format Universal

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment


## Scope

- `.claude/skills/`

## References

- `CLAUDE.md`
- `AGENTS.md`
- `https://code.claude.com/docs/en/skills`
- `https://github.com/anthropics/skills`
- `.claude/skills/lib-returns/SKILL.md`
- `.claude/skills/lib-pydantic-v2/SKILL.md`

## Rules

- Keep frontmatter minimal and valid: `name`, `description`.
- Put trigger guidance in `description`, not in a body section called "When to use".
- Keep body operational and evidence-backed with repository paths and runnable checks.
- Keep names aligned with directory names under `.claude/skills/<name>/SKILL.md`.
- Keep policy text aligned with `CLAUDE.md` (canonical), do not invent parallel policy.
- Use exactly these body sections for project consistency:
  - `## Scope`
  - `## References`
  - `## Rules`
  - `## Instructions`
  - `## Workflow`
  - `## Examples`
  - `## Verification`

## Instructions

- Write one clear scope and reference only files that exist in this workspace.
- Use imperative bullets, short paragraphs, and concrete API names.
- Prefer project anchors like `flext-core/src/flext_core/result.py` over generic text.
- Add a verification block with commands that can be run as-is.
- Include at least one Good and one Bad code/example pair with a "Why bad" explanation.
- For `lib-*` skills, include concrete declarations (classes/methods) and subproject usage map.
- For `rules-*` skills, include concrete file anchors in target directory and enforceable grep checks.
- For skills with `rules.yml`, keep rule metadata in flat keys only (`fix_auto`, `fix_type`, `fix_file`, `fix_script`, `fix_instruction`, `fix_description`).
- Prefer `type: ast-grep`; use `type: custom` only when AST matching is not applicable, and document the reason in `description`.
- `fix_auto: true` must point to a real executable mechanism (`fix_type + fix_file` for ast-grep or `fix_type + fix_script` for custom).

## Workflow

- Start from `CLAUDE.md` and `AGENTS.md`.
- For each skill, gather at least one internal source file and one verification command.
- Remove vague claims that cannot be proven from repository files.
- Validate section presence and frontmatter consistency across all skills before finalizing.
- Remove absolute-path references and stale placeholders.

## Examples

Good:

```markdown
Use `r[T].ok(...)`, `.flat_map(...)`, and `.lash(...)` from
`flext-core/src/flext_core/result.py` for fallible operation chains.
```

Why good: concrete symbols + concrete path + actionable guidance.

Bad:

```markdown
Handle errors functionally.
```

Why bad: abstract instruction without symbol, path, or verification criteria.

## Verification

- `ls -1 .claude/skills/*/SKILL.md`
- `rg -n "^name:|^description:" .claude/skills/*/SKILL.md`
- `for f in .claude/skills/*/SKILL.md; do for s in "## Scope" "## References" "## Rules" "## Instructions" "## Workflow" "## Examples" "## Verification"; do grep -q "$s" "$f" || echo "MISSING $s in $f"; done; done`
- `rg -n "When to use|When to Use" .claude/skills/*/SKILL.md`
- `rg -n "['\"]/[^\s\"]+" .claude/skills/*/SKILL.md || true`
- `rg -n "TODO|TBD|placeholder" .claude/skills/*/SKILL.md || true`
