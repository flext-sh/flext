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

name: rules-typings
description: Rules for typing support assets in `typings/` (stubs, compatibility shims, and local type metadata). Use when editing `.pyi` files or typing helper packages.

---

# Rules Typings

## Scope

- `typings/__init__.pyi`
- `typings/factory.pyi`
- `typings/returns/`
- `typings/radon/`
- `typings/ruff/`
- `typings/ldif3/`

## References

- `AGENTS.md` — canonical governance source
- `flext-core/src/flext_core/typings.py`
- `pyproject.toml`
- `typings/`

## Rules

- Keep stubs synchronized with runtime/public API signatures.
- Prefer precise types over broad fallback annotations. `Any` and `t.NormalizedValue` are TOTALLY FORBIDDEN — use `t.*` contracts from `typings.py`.
- Keep package-specific typing shims isolated under their own stub namespace.
- Do not introduce broken/incomplete stubs without clear compatibility intent.

## Instructions

- Update `.pyi` signatures when corresponding runtime signatures change.
- Keep import paths and exported names aligned with package contracts.
- Validate that stub packages do not shadow unrelated modules.

```bash
ls -la typings
```

## Workflow

1. Identify runtime API change requiring stub update.
2. Update matching `.pyi` declarations.
3. Validate imports/exports in stubs remain coherent.
4. Re-run type checks for impacted packages.

## Examples

Good:

```python
# factory.pyi
def create(name: str): ...
```

Why good: explicit callable contract using `t.*` types for static tools.

Bad:

```python
# factory.pyi
def create(*args, **kwargs): ...
```

Why bad: loses useful type information and weakens analyzer value.

## Verification

Make gates:

- `make typings` — run typings supply-chain automation
- `make check PROJECT=flext-core CHECK_GATES=type` — type-check after stub changes

File checks:

- `ls -la typings`
- `rg -n "\.pyi$" -g "*.pyi" typings`
- `rg -n "TODO|FIXME|pass" typings || true`
