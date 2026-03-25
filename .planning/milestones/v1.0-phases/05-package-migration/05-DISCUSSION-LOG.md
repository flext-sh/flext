# Phase 5: Package Migration - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-24
**Phase:** 05-package-migration
**Areas discussed:** Submodule extraction, pyproject.toml conversion, Lock file unification, Make target migration

---

## Submodule Extraction (MIG-01/02/03)

### Git History

| Option | Description | Selected |
|--------|-------------|----------|
| Fresh repo (no history) | Simplest — submodules already registered. History starts at migration commit. | |
| git subtree split | Preserves full commit history per package. Standard git, no external tools. | |
| Other | Keep current strategy — one repo per namespace, don't change anything | ✓ |

**User's choice:** "nao mude nada na estrategia de repositorio git, um repositorio por namespace e mantenha o que temos"
**Notes:** Repos and submodules already in place. No restructuring needed — just validation.

### Dependency References

| Option | Description | Selected |
|--------|-------------|----------|
| Workspace members | uv resolves internal deps natively. Drop all `@ file:` strings. | ✓ |
| Keep file: paths | Current pattern works. Change only when uv workspace is fully wired. | |

**User's choice:** Workspace members (Recommended)

---

## pyproject.toml Conversion (MIG-04)

### Conversion Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Batch via modernizer | Update modernizer to emit PEP 621 + hatchling, then `make mod` across all 33. | |
| Incremental project-by-project | Convert leaf projects first, work up dep graph. More manual but easier rollback. | ✓ |

**User's choice:** Incremental project-by-project

### Build Backend

| Option | Description | Selected |
|--------|-------------|----------|
| hatchling | Modern, fast, PEP 621 native. Standard for pure Python packages. | ✓ |
| setuptools | Most widely supported. Conservative choice. | |

**User's choice:** hatchling (Recommended)

### Dev Dependencies

| Option | Description | Selected |
|--------|-------------|----------|
| [dependency-groups] | PEP 735, uv-native. `uv sync --group dev`. | ✓ |
| [project.optional-dependencies] | Traditional extras. Works with pip and all build backends. | |

**User's choice:** [dependency-groups] (Recommended)

---

## Lock File Unification (MIG-05)

| Option | Description | Selected |
|--------|-------------|----------|
| Pure uv workspace | Single root uv.lock with workspace members. Delete all poetry.lock after `uv lock`. | ✓ |
| Gradual waves | Add workspace members incrementally. Keep poetry.lock until uv covers each project. | |

**User's choice:** Pure uv workspace (Recommended)

---

## Make Target & CI Migration (MIG-06)

| Option | Description | Selected |
|--------|-------------|----------|
| Hard-cut to uv | Replace `poetry install` with `uv sync` in all Makefiles. Swap CI actions. | ✓ |
| Keep Poetry as fallback | Hybrid `uv sync || poetry install`. Safer but adds complexity. | |

**User's choice:** Hard-cut to uv (Recommended)

---

## Claude's Discretion

- Sequencing of incremental project conversion (which leaf projects first)
- Handling of modernizer bootstrap during migration
- Specific `[tool.uv.workspace]` member list syntax
- Error handling for `uv lock` resolution conflicts

## Deferred Ideas

- PyPI publication automation (v2 requirement)
- CI/CD uv cache strategy (v2 requirement)
- Polylith workspace.toml (v2 requirement)
