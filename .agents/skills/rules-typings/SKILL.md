---
name: rules-typings
description: Rules for typing support assets in `typings/` (stubs, compatibility shims, and local type metadata). Use when editing `.pyi` files or typing helper packages.

---

# Rules Typings

## Scope

- `typings/__init__.pyi`
- `typings/bandit/`
- `typings/msgpack/`
- `typings/radon/`
- `typings/ruff/`
- `typings/vulture/`
- `typings/generated/`

## References

- `AGENTS.md` — canonical governance source
- `flext-core/src/flext_core/typings.py`
- `pyproject.toml`
- `typings/`

## Rules

- **PyPI stubs FIRST**: Always prefer installing a PyPI stub package (`types-*`, `*-stubs`) over writing manual stubs in `typings/`. Manual stubs are a last resort for libraries with NO PyPI stubs.
- **Never shadow shipped types**: If a library ships `py.typed` (e.g., matplotlib, pydantic), custom stubs in `typings/` will CONFLICT — pyright prioritizes installed package types. Use PyPI stub packages or per-line `# pyright: ignore[specificCode]` instead.
- **Per-line ignores only**: For third-party libs with incomplete types and no stubs, use per-line `# pyright: ignore[reportXxx]` with specific error codes. File-level `# pyright:` settings comments are FORBIDDEN.
- Keep stubs synchronized with runtime/public API signatures.
- Prefer precise types over broad fallback annotations. `Any` and `object` are FORBIDDEN — use `t.*` contracts from `typings.py`.
- Internal FLEXT typing gaps are NOT solved with local stubs. Fix the source contract in `protocols.py`, `typings.py`, or `models.py`, then consume it through `p.*`, `t.*`, or `m.*`.
- Manual stubs must never preserve a concrete internal implementation annotation when a structural `p.*` or composed `t.*` contract should exist instead.
- Keep package-specific typing shims isolated under their own stub namespace.
- Do not introduce broken/incomplete stubs without clear compatibility intent.

## Third-Party Type Coverage

Libraries with PyPI stubs (declare in `pyproject.toml` dev deps):

| Library    | Stub Package       | Notes                                              |
| ---------- | ------------------ | -------------------------------------------------- |
| matplotlib | `matplotlib-stubs` | Partial — some methods still need per-line ignores |
| docker     | `types-docker`     |                                                    |
| ldap3      | `types-ldap3`      |                                                    |
| protobuf   | `types-protobuf`   |                                                    |
| psutil     | `types-psutil`     |                                                    |
| PyYAML     | `types-pyyaml`     |                                                    |
| requests   | `types-requests`   |                                                    |
| cachetools | `types-cachetools` |                                                    |
| paramiko   | `types-paramiko`   |                                                    |
| setuptools | `types-setuptools` |                                                    |

Libraries with NO PyPI stubs (manual `typings/` stubs kept):

| Library | Manual Stubs       | Notes                            |
| ------- | ------------------ | -------------------------------- |
| bandit  | `typings/bandit/`  | Quality tool — no upstream types |
| msgpack | `typings/msgpack/` | Binary serialization             |
| radon   | `typings/radon/`   | Complexity metrics               |
| ruff    | `typings/ruff/`    | Linter Python API                |
| vulture | `typings/vulture/` | Dead code detection              |

Libraries with NO stubs at all (use per-line pyright ignores):

| Library     | Strategy                                              |
| ----------- | ----------------------------------------------------- |
| cairosvg    | `# pyright: ignore[reportUnknownMemberType]` per line |
| weasyprint  | `# pyright: ignore[reportUnknownMemberType]` per line |
| python-docx | `# pyright: ignore[reportUnknownMemberType]` per line |

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
