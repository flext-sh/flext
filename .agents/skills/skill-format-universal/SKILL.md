---
name: skill-format-universal
description: Canonical format for project SKILL.md files using Anthropic standards and FLEXT evidence. Use when creating or rewriting any skill.

---

# Skill Format Universal

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment

## Scope

- `.agents/skills/`

## References

- `AGENTS.md`
- `https://agentskills.io/specification`
- `https://github.com/anthropics/skills`
- `.agents/skills/lib-returns/SKILL.md`
- `.agents/skills/lib-pydantic-v2/SKILL.md`

## Rules

- **Frontmatter required**: every SKILL.md must have `name` and `description`. Optional: `compatibility`, `metadata`, `allowed-tools`.
- **Name constraints**: lowercase a-z + hyphens only, max 64 chars, must match parent directory name exactly (e.g. `name: flext-patterns` inside `.agents/skills/flext-patterns/SKILL.md`).
- **Description constraints**: max 1024 chars, non-empty, 3rd person, imperative "Use when…" phrasing with specific trigger keywords that help agents identify the right skill.
- Put trigger guidance in `description`, not in a body section called "When to use".
- **Line count**: keep SKILL.md body under 500 lines. Move detailed reference content to `references/*.md` and link explicitly (e.g. See `references/<topic>.md`).
- **Compatibility field**: add only if the skill requires specific environment packages, Python version, or tool prerequisites (e.g. `Requires Python 3.13+, uv, and git`). Most skills do not need this field.
- Keep body operational and evidence-backed with repository paths and runnable checks.
- Keep names aligned with directory names under `.agents/skills/<name>/SKILL.md`.
- Keep policy text aligned with `AGENTS.md` (canonical), do not invent parallel policy.
- Operational skills that govern refactoring, navigation, routing, validation, or automation must explicitly state mandatory tooling and execution law when applicable: Scope availability/freshness, Serena setup, `ast-grep` for structural propagation, MCP when configured, impact analysis before edit, and zero-debt gate expectations.
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
- For workflow/routing/refactor skills, document the required preflight tools and the completion condition for propagation and zero open gate debt.
- For `lib-*` skills, include concrete declarations (classes/methods) and subproject usage map.
- For `rules-*` skills, include concrete file anchors in target directory and enforceable grep checks.
- For skills with `rules.yml`, keep rule metadata in flat keys only (`fix_auto`, `fix_type`, `fix_file`, `fix_script`, `fix_instruction`, `fix_description`).
- Prefer `type: ast-grep`; use `type: custom` only when AST matching is not applicable, and document the reason in `description`.
- `fix_auto: true` must point to a real executable mechanism (`fix_type + fix_file` for ast-grep or `fix_type + fix_script` for custom).

## Workflow

- Start from `AGENTS.md` and the relevant `rules-*` skill for the touched path.
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

- `ls -1 .agents/skills/*/SKILL.md`
- `rg -n "^name:|^description:" .agents/skills/*/SKILL.md`
- `for f in .agents/skills/*/SKILL.md; do for s in "## Scope" "## References" "## Rules" "## Instructions" "## Workflow" "## Examples" "## Verification"; do grep -q "$s" "$f" || echo "MISSING $s in $f"; done; done`
- `rg -n "When to use|When to Use" .agents/skills/*/SKILL.md`
- `rg -n "TODO|TBD|placeholder" .agents/skills/*/SKILL.md || true`
- `# Spec compliance: name matches directory`
- `for f in .agents/skills/*/SKILL.md; do dir=$(basename $(dirname "$f")); name=$(awk '/^name:/{print $2}' "$f"); [[ "$name" != "$dir" ]] && echo "NAME MISMATCH: '$name' != '$dir' in $f"; done`
- `# Spec compliance: line count over 500`
- `for f in .agents/skills/*/SKILL.md; do lc=$(wc -l < "$f"); [[ $lc -gt 500 ]] && echo "OVER 500 lines ($lc): $f"; done`
- `# Spec compliance: description length over 1024 chars`
- `awk '/^description:/{line=$0; while(/\\$/{getline x; line=line" "x}; print length(line), FILENAME}' .agents/skills/*/SKILL.md | awk '$1>1024'`
