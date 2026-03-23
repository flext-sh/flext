<!-- TOC START -->

- [Scope](#scope)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
- [Workflow](#workflow)
- [Examples](#examples)
- [Verification](#verification)
<!-- TOC END -->

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
- `AGENTS.md`

## Rules

- Keep docs paths and file references repository-relative.
- Align architectural claims with current source files.
- Prefer concrete file/symbol anchors over generic statements.
- Avoid duplicating canonical policy text from root governance files.
- **Zero Tolerance for Hacks**: Prohibited use of `model_rebuild()`, `eval()`, `exec()`, and `inline imports`. `cast()` is forbidden outside `flext-core` result internals.

## Instructions

- Verify referenced files exist before publishing links or commands.
- Update related docs pages when structure/naming changes.
- For architecture docs, include source-aligned module names.

```bash
ls -la docs
```

## Workflow

1. **Pre-scan**: identify affected docs pages and ownership boundaries.
2. **Remediation**: update content with concrete source anchors and canonical governance references.
3. **Verification**: validate links/paths and remove stale references.
4. **Drift prevention**: re-check docs index/navigation consistency and schedule periodic audits.

## Examples

Good:

```markdown
See `flext-core/src/flext_core/result.py` for `r` behavior.
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
- `rg -n "flext-core/src/flext_core|AGENTS.md" docs`
- `rg -n "TODO|FIXME" docs || true`

```bash
python3 - <<'PY'
import pathlib
import re

root = pathlib.Path('.')
docs = root / 'docs'
pattern = re.compile(r'\[[^\]]+\]\(([^)\s]+)\)')
broken: Sequence[str] = []

for file_path in docs.rglob('*.md'):
    text = file_path.read_text(encoding='utf-8', errors='ignore')
    for target in pattern.findall(text):
        if target.startswith(('http://', 'https://', '#', 'mailto:')):
            continue
        resolved = (file_path.parent / target).resolve()
        if not resolved.exists():
            broken.append(f'{file_path}:{target}')

print('NO_BROKEN_LINKS' if not broken else '\n'.join(broken))
PY
```
