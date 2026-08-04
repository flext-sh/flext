# Onboarding (Collection Rules / regras de coletas)

Canonical pre-work to enter ANY FLEXT project. Per AGENTS.md §9 Pre-requisites + the auto-generated per-project
Collection Rules in each `<project>/docs/index.md`.

## 1. Read Governance First

1. [`/flext/docs/GOVERNANCE.md`](../GOVERNANCE.md) — rule routing, ADRs,
   validation surfaces, and ratified refactor gates.
2. `/flext/AGENTS.md` (repo root) — supreme engineering law.
3. `~/.claude/AGENTS.md` — universal cross-project rules (if present).
4. The target project's `pyproject.toml` for stack, version, dependencies.

## 2. Identify Project Slot Ownership

Use the cross-project slot registry in `~/.agents/skills/` when the active
provider exposes it. Confirm which `c.<Domain>`, `m.<Domain>`, `p.<Domain>`,
`t.<Domain>`, `u.<Domain>` slots the target project owns before adding or
renaming any symbol.

## 3. Bootstrap Tooling

```bash
cd <workspace-root>
make setup                       # Workspace .venv only (project .venv is forbidden — see AGENTS.md §6)
```

The workspace `.venv/` is mandatory. Run validation through the root Make
dispatcher; do not rely on bare tool commands or a machine-specific path.

## 4. Confirm Zero-Debt Baseline

```bash
cd <project>
make check                                    # ruff + pyrefly + mypy + pyright must exit 0
make test                                     # pytest must exit 0 with project coverage threshold
make docs DOCS_PHASE=audit                    # docs audit must report zero issues
```

If any gate fails, FIX FORWARD per AGENTS.md §3.5. Never `git checkout`/`reset`/`revert` to recover.

## 5. Load Skills Relevant to the Change Scope

The provider activates `flext-context-routing` first. That router selects only
the smallest on-demand set declared by the active `~/.agents` provider:

1. Load the one domain skill that owns the change, such as `lib-returns`,
   `flext-import-rules`, or `pydantic-v2-governance`.
2. Add a quality or workflow skill only when its procedure is needed.
3. Use `coding-standards` as a concern index when the owner is unclear, not as
   an always-loaded second specification.

Do not maintain or load a fixed default skill bundle.

Path-scoped skills live under the active `~/.agents/skills/` authority.
Their exported inventory is owned by that provider configuration.

## 6. Fundamental Packages

Before writing code, know the three shared packages most projects consume:

| Package | What it provides | Quick guide | Skill |
| --------- | ------------------ | ------------- | ------- |
| `flext_core` | Result flow, settings, container, dispatcher | [Using flext-core](using-flext-core.md) | `using-flext-core` |
| `flext_cli` | Model-driven Typer CLI abstraction | [Using flext-cli](using-flext-cli.md) | `using-flext-cli` |
| `flext_tests` | Shared fixtures, matchers, test runtime | [Using flext-tests](using-flext-tests.md) | `using-flext-tests` |

## 7. Per-Project Collection Rules

Every project ships an auto-generated `docs/index.md` with Collection Rules tailored to its parent MRO chain, abstracted
libraries, owned slot registry, and quality gates. Open `<project>/docs/index.md` and follow the project-specific list
before editing.

To regenerate stale per-project docs:

```bash
cd <project>
make docs DOCS_PHASE=generate    # re-renders docs/index.md, api-reference/generated/*
make docs DOCS_PHASE=fix         # safe automated docs remediation
make docs DOCS_PHASE=audit       # re-confirm zero issues
```

## 8. Cross-References

- [Getting Started](getting-started.md) — workspace bootstrap.
- [Development](development.md) — daily workflow.
- [Configuration](configuration.md) — `pyproject.toml` and docs metadata.
- [Testing](testing.md) — quality gates and docs validation.
- [Using flext-core](using-flext-core.md) — base package usage.
- [Using flext-cli](using-flext-cli.md) — CLI abstraction usage.
- [Using flext-tests](using-flext-tests.md) — shared test toolkit usage.
- [Workspace API overview](../api-reference/generated/overview.md) — auto-generated cross-project surface.
- [Project catalog](../projects/generated/catalog.md) — full project registry.
