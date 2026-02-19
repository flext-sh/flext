---
name: rules-examples
description: Rules for runnable examples in `examples/` so they stay aligned with current APIs and tooling. Use when editing or adding example scripts.
---

# Rules Examples

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment


## Scope
- `examples/acl_processing_example.py`
- `examples/advanced_processing_example.py`
- `examples/complete_workflow_example.py`
- `examples/README.md`

## References
- `examples/README.md`
- `flext-core/src/flext_core/__init__.py`
- `flext-core/src/flext_core/result.py`

## Rules
- Keep examples executable from repository root.
- Use current public APIs; avoid stale/internal imports.
- Include realistic input/output flow, not placeholder pseudo-code.
- Keep example naming and README references synchronized.

## Instructions
- Anchor imports to public package surfaces (`flext_core`, package root exports).
- Update `examples/README.md` when files are added/renamed.
- Remove outdated APIs from examples when core contracts change.

```bash
python examples/complete_workflow_example.py --help || true
```

## Workflow
1. Choose target example and its API dependencies.
2. Update script with current public imports and behavior.
3. Verify script syntax and invocation.
4. Sync README references.

## Examples
Good:

```python
from flext_core import r
```

Why good: stable public import with canonical alias.

Bad:

```python
from flext_core._models import m
```

Why bad: example couples to private internals and will drift quickly.

## Verification

Make gates:

- `make check PROJECT=flext-core` — verify core imports used by examples still pass

File checks:

- `ls -la examples`
- `rg -n "from flext_core|from flext_core\._" examples/*.py`
- `rg -n "TODO|FIXME" examples || true`
