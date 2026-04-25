# Onboarding (Collection Rules / regras de coletas)

Canonical pre-work to enter ANY FLEXT project. Per AGENTS.md §9 Pre-requisites + the auto-generated per-project Collection Rules in each `<project>/docs/index.md`.

## 1. Read Governance First

1. [`/flext/AGENTS.md`](../../AGENTS.md) — supreme engineering law.
2. [`~/.claude/AGENTS.md`](https://github.com) — universal cross-project rules (if present).
3. The target project's `pyproject.toml` for stack, version, dependencies.

## 2. Identify Project Slot Ownership

Use the cross-project slot registry in [`.agents/skills/flext-mro-namespace-rules/SKILL.md`](../../.agents/skills/flext-mro-namespace-rules/SKILL.md). Confirm which `c.<Domain>`, `m.<Domain>`, `p.<Domain>`, `t.<Domain>`, `u.<Domain>` slots the target project owns BEFORE adding/renaming any symbol.

## 3. Bootstrap Tooling

```bash
cd <project>
scope status                    # Re-bootstrap per .agents/skills/flext-scope-bootstrap/SKILL.md if absent
make boot                       # Workspace .venv only (project .venv is forbidden — see AGENTS.md §6)
```

Workspace venv is mandatory: `/home/marlonsc/flext/.venv/`. Bare commands (`ruff`, `pyrefly`, `pytest`) auto-proxy via RTK.

## 4. Confirm Zero-Debt Baseline

```bash
cd <project>
make check                                    # ruff + pyrefly + mypy + pyright must exit 0
make val VALIDATE_SCOPE=project               # complexity + docstring gates must exit 0
make test                                     # pytest must exit 0 with project coverage threshold
make docs DOCS_PHASE=audit                    # docs audit must report zero issues
```

If any gate fails, FIX FORWARD per AGENTS.md §3.5. Never `git checkout`/`reset`/`revert` to recover.

## 5. Load Skills Relevant to the Change Scope

Default load order:

1. Scope skill: e.g. `rules-flext-core` for flext-core, `rules-src` for general src work.
2. `flext-mro-namespace-rules` — ownership and naming.
3. `flext-import-rules` — import discipline.
4. `flext-patterns` — result/logging/DI patterns.
5. Tier-specific: `pydantic-v2-governance`, `flext-strict-typing`, `flext-type-system`, `flext-constants-discipline`, `testing-patterns`.

Path-scoped skills live in [`.agents/skills/`](../../.agents/skills/).

## 6. Per-Project Collection Rules

Every project ships an auto-generated `docs/index.md` with Collection Rules tailored to its parent MRO chain, abstracted libraries, owned slot registry, and quality gates. Open `<project>/docs/index.md` and follow the project-specific list before editing.

To regenerate stale per-project docs:

```bash
cd <project>
make docs DOCS_PHASE=generate    # re-renders docs/index.md, api-reference/generated/*
make docs DOCS_PHASE=fix         # safe automated docs remediation
make docs DOCS_PHASE=audit       # re-confirm zero issues
```

## 7. Cross-References

- [Getting Started](getting-started.md) — workspace bootstrap.
- [Development](development.md) — daily workflow.
- [Configuration](configuration.md) — `pyproject.toml` and docs metadata.
- [Testing](testing.md) — quality gates and docs validation.
- [Workspace API overview](../api-reference/generated/overview.md) — auto-generated cross-project surface.
- [Project catalog](../projects/generated/catalog.md) — full project registry.
