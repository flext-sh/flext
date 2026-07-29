# AGENTS.md — FLEXT Engineering Guide

This file is the project authority for agent work in `/workspace/flext`. Universal
policy lives in `~/.agents`; do not duplicate it here. A nested `AGENTS.md` narrows
rules for its directory. Accepted ADRs and architecture standards own technical
decisions; skills route and apply those decisions but do not override them. The
newest explicit operator instruction has highest authority.

## Mission

FLEXT is a typed Python platform for data integration, platform tooling, and
enterprise connectors. Build every integration from reusable, validated
primitives owned by `flext-core`:

- use the structural facades `c`, `t`, `p`, `m`, and `u`;
- return `r[T]` from fallible application paths;
- keep one canonical owner for each contract or behavior;
- prefer less code, strict types, and reusable composition over ad hoc helpers.

## Working agreement

1. **Inspect before editing.** Read the active issue or Bead, relevant docs,
   canonical owner, consumers, generated outputs, and current Git state.
2. **Use Beads when available.** Run `bd ready` and `bd show <id>`, keep status and
   evidence current, and never edit `.beads/*.jsonl` directly. If `bd` is missing,
   report that limitation and continue with the smallest safe scope.
3. **Load only relevant skills.** Read `.agents/skills/flext-context-routing/SKILL.md`
   first, then the path- or technology-specific skills for the task.
4. **Change the source of truth.** Update configuration, models, generators, or
   implementation owners—not derived projections. Regenerate affected outputs.
5. **Keep the change surgical.** Do not add compatibility aliases, bypasses,
   fallbacks, suppressions, pass-through wrappers, hardcoded configuration, or
   speculative abstractions.
6. **Update every consumer.** Public moves or renames and facade changes must update
   all callers in the same batch. Never leave old and new routes side by side.
7. **Preserve shared work.** Re-read mutable files, stage explicit paths, and fix
   forward. Never discard, stash, reset, or revert unknown work.
8. **Document behavior changes.** Update the canonical documentation, examples, and
   executable snippets in the same change. Pointer documents must not duplicate law.
9. **Validate before claiming success.** Record the command, working directory,
   exit status, decisive output, and tested scope. A partial or sampled check does
   not prove workspace-wide success.
10. **Land green slices.** Commit scoped paths after validation. Push and create a PR
    when the environment and operator workflow require it. Do not merge, release,
    deploy, or rewrite history without explicit authorization.

Ask one precise question only for conflicting authority, destructive action,
security/privacy choices, public-contract ambiguity, or production promotion.
Resolve ordinary uncertainty from code, documentation, and real consumers.

## FLEXT ecosystem conventions

The `flext-sh` organization is a coordinated package ecosystem, not a collection
of independent implementations:

- `flext-core` owns shared runtime primitives, facades, results, models, settings,
  protocols, dependency injection, and logging contracts.
- `flext-cli` owns CLI frameworks, terminal rendering, prompts, serialization,
  tabular output, and process execution exposed to package command routers.
- `flext-tests` owns shared test infrastructure and the distributed Make framework.
- `flext-infra` owns workspace automation, generation, dependency management,
  validation services, and structural refactoring infrastructure.
- Domain and integration packages consume those capabilities through public
  facades; they do not recreate platform services locally.

Only content explicitly marked as generated or named by an accepted ADR is a managed
projection. Current examples include marked `pyproject.toml` sections, the root
`Makefile`, and the generated pre-commit configuration. Change the declared owner and
regenerate; never infer generated status from a file type. Package-local custom
sections and curated documentation remain authored extension points.

Before creating a module, helper, model, script, rule, or command, search the
workspace for its existing ecosystem owner. Prefer extension through the public
contract; create a new owner only when the responsibility is genuinely absent.

## Skill routing

Skills are task-specific decision aids, not duplicate policy documents:

1. Start with `flext-context-routing` and `flext-ecosystem-patterns` for ownership.
2. Load one path skill (`rules-*` or `scripts-*`) for the touched tree.
3. Load technology skills (`lib-*`, typing, testing, CLI, async) only when applicable.
4. Use `flext-quality-gates` to select evidence after the implementation path is known.

Each `SKILL.md` must have a precise trigger, an executable workflow, concrete
contracts, and links to detailed rules or references. Remove generic advice and
stale section citations. The manifest and its `rules.yml`, rule files, examples,
and validator must describe the same contract.

## Architecture and code rules

- Target Python 3.13+ and Pydantic v2.
- Use strict annotations; do not introduce `Any` or bare `object`.
- Narrow with `isinstance` or a `TypeGuard`, never `type(value) is ...`.
- Parse dynamic input once with a typed Pydantic model such as
  `OptionsModel.model_validate(payload)`.
- Keep `__init__.py` export-only.
- Follow project dependency direction and MRO namespace ownership.
- Import abstracted libraries through FLEXT facades; consumer packages must not
  bypass them with direct framework imports.
- Access runtime environment through settings abstractions, not raw `os.environ`
  in production source.
- Fallible application operations return `r[T]`; do not use `T | None`, raw
  exceptions, or error dictionaries for routine failure flow.
- Treat `src/`, `tests/`, `examples/`, and `scripts/` as first-class typed code.
  Never hide defects through blanket exclusions or per-file ignores.
- Profile before performance work. Optimize measured hot paths without weakening
  coverage or architectural boundaries.

## Configuration and generated content

Configuration, settings, schemas, and generators own configurable facts. Tests,
goldens, examples, and docstrings must read those values from the same typed source
used by production or prove a generator/consumer round trip. They may lock stable
structure and external protocol contracts, but never today's project-owned values.

Validate generated or deployed artifacts with their real consumer before encoding
the behavior in tests. Do not hand-edit generated files. Regeneration must be
deterministic and idempotent.

## Canonical command surface

Use repository Make verbs or a documented project CLI. If a canonical command is
broken, fix its owner rather than bypassing its guards.

```bash
make help
make boot
make check CHANGED_ONLY=1
make check PROJECT=<project> CHECK_GATES=<gates>
make test PROJECT=<project> MATCH=<expression>
make docs DOCS_PHASE=<generate|fix|audit|build|validate> PROJECT=<project>
make val VALIDATE_SCOPE=workspace
make ship WHAT=<save|tag|push|pr|rel>
```

Common check gates are `lint`, `format`, `pyrefly`, `pyright`, `mypy`, `markdown`,
`go`, `loc-cap`, `boundary`, and `coordination`.

For each edit batch of at most five files, keep imports and collection green and
run the narrowest applicable canonical checks. Python completion normally requires
Ruff, Pyrefly, Pyright, Mypy, and scoped Pytest coverage, followed by broader
validation when contracts cross package boundaries. Run mutating validations only
inside repository-provided isolation; evidence artifacts belong under
`.beads/artifacts/`.

Helm operations are always serialized through the canonical Helm lock. Never run
Helm concurrently or create per-worker cache workarounds.

## Shell and automation

- Use `#!/usr/bin/env bash` and `set -euo pipefail` for Bash owned by FLEXT.
- Quote expansions, use arrays for argument lists, and prefer `[[ ... ]]` and
  `printf` over word-splitting pipelines and ambiguous `echo` behavior.
- Resolve the repository root once, make paths independent of the caller's current
  directory, and clean temporary resources with a trap.
- Provide non-interactive flags, deterministic ordering, actionable stderr, and
  stable exit codes: `0` pass, `1` validation failure, `2` usage, `3` infrastructure.
- Never print secrets, embed credentials, use `eval`, download-and-execute code, or
  turn expected failures into success with an unqualified `|| true`.
- Gate scripts are read-only by default. Mutation requires an explicit apply flag
  and a dry-run that reports the exact planned changes.
- Scripts are invoked through their canonical Make verb rather than a second entry
  point. Add an owner marker only where the owning rule manifest requires it.

## Git, commits, and pull requests

- Use explicit pathspecs; never run `git add .` in the shared worktree.
- Commit only the completed, validated task scope.
- Use fast-forward push only; never rewrite shared history.
- State scope, rationale, validation, and remaining risk in commits and PRs.
- Do not claim completion while scoped work is dirty, uncommitted, unpushed when a
  push is required, missing generated output, or failing an applicable gate.

## Project map

- `flext-*`: governed packages
- `docs/`: canonical architecture and onboarding documentation
- `tests/` and package-local `tests/`: test suites
- `scripts/`: workspace automation
- `workspace_custom.mk` and `Makefile`: canonical command dispatch
- `.agents/skills/`: concise, task-specific operating procedures

## Completion checklist

- The requested behavior and all affected consumers are complete.
- Canonical docs and generated outputs are current.
- Applicable narrow and cross-project gates pass with recorded evidence.
- No scoped smell, suppression, duplicate route, or temporary workaround remains.
- Explicit paths are committed; required push and PR steps are complete.
- The active Bead contains evidence and final status when Beads is available.
