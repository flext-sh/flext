---
name: rules-docs
description: Rules for documentation under `docs/` to keep architecture and project guides aligned with current code and policy. Use when editing docs pages or docs structure.
---

# Rules Docs

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment


## Scope
- `docs/index.md`
- `docs/architecture/`
- `docs/guides/`
- `docs/projects/`
- `docs/standards/`

## References
- `docs/README.md`
- `docs/architecture/overview.md`
- `docs/architecture/clean-architecture.md`
- `docs/architecture/adr/README.md`
- `CLAUDE.md`

## Rules
- Keep docs paths and file references repository-relative.
- Align architectural claims with current source files.
- Prefer concrete file/symbol anchors over generic statements.
- Avoid duplicating canonical policy text from root governance files.

## Instructions
- Verify referenced files exist before publishing links or commands.
- Update related docs pages when structure/naming changes.
- For architecture docs, include source-aligned module names.

```bash
ls -la docs
```

## Workflow
1. Identify docs pages affected by the change.
2. Update content with concrete source anchors.
3. Validate links/paths and remove stale references.
4. Re-check docs index/navigation consistency.

## Examples
Good:

```markdown
See `flext-core/src/flext_core/result.py` for `FlextResult` behavior.
```

Why good: links documentation to a concrete source file and symbol.

Bad:

```markdown
The core handles results somewhere in the project.
```

Why bad: vague guidance with no verifiable anchor.

## Verification

Make gates:

- `make docs PROJECT=<name>` — build docs for a specific project
- `make validate VALIDATE_SCOPE=workspace` — workspace-level validation

File checks:

- `ls -la docs`
- `rg -n "flext-core/src/flext_core|CLAUDE.md|AGENTS.md" docs`
- `rg -n "TODO|FIXME" docs || true`
