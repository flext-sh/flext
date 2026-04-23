---
name: flext-scope-bootstrap
description: Use when Scope is missing, stale, or must be bootstrapped correctly in the FLEXT monorepo. Covers repo-root vs workspace-root initialization, official Scope config artifacts, validation with status/index, and mandatory reindex triggers after structural work.
---

# FLEXT Scope Bootstrap

## Scope

- `.scope/config.toml`
- `scope-workspace.toml`
- `.agents/skills/`

## References

- `AGENTS.md`
- `.scope/config.toml`
- `.agents/skills/code-navigation/SKILL.md`
- `.agents/skills/flext-context-routing/SKILL.md`
- `.agents/skills/flext-refactoring-workflow/SKILL.md`

## Rules

- `AGENTS.md` is the canonical governance source; this skill is limited to Scope bootstrap and freshness discipline.
- Use the official Scope CLI bootstrap, not hand-written config skeletons.
- Repository-local setup in FLEXT starts at the repository root with `scope init`, which generates `.scope/config.toml` and `.scope/.gitignore`.
- Workspace setup starts at the workspace root with `scope workspace init`, but only after each member repository has already been initialized with `scope init`. The workspace command generates `scope-workspace.toml` by discovering member repositories that already contain `.scope/config.toml`.
- Validate Scope before querying: run `scope status`, then `scope index` for repo-local work or `scope workspace index` for workspace-wide work.
- Reindex after structural changes that can invalidate symbol, caller, or reference data.
- Do not patch broken Scope setups by guessing config keys. Regenerate the baseline with the CLI and then keep only intentional project-specific deltas.
- Do not duplicate wider routing or execution policy here; point back to `AGENTS.md` and the relevant routing skills when broader governance is needed.

## Instructions

- Default FLEXT repository work uses `/home/marlonsc/flext` as the repo root and the committed `.scope/config.toml` baseline.
- Determine whether the task is repo-local or workspace-wide before running any Scope command.
- If repo-local Scope config is missing or invalid, run `scope init` at the repo root.
- If workspace-wide config is missing or invalid, ensure each member repo has `.scope/config.toml`, then run `scope workspace init` at the workspace root.
- After bootstrap or repair, run `scope status` and the matching index command before using `scope map`, `scope refs`, `scope callers`, or other structural queries.
- For long multi-project sessions, prefer `scope workspace index --watch` when it is supported in the environment.

## Workflow

1. Pick the correct root: repo root for local work, workspace root for multi-repo work.
2. Bootstrap missing or invalid Scope config with `scope init` or `scope workspace init`.
3. Run `scope status`.
4. Rebuild the matching index with `scope index` or `scope workspace index`.
5. Perform structural discovery and blast-radius analysis.
6. After structural edits, rerun the relevant Scope index and then re-run the query you relied on.

## Examples

Good:

```bash
cd /home/marlonsc/flext
scope status
scope index
```

Why good: uses the existing repo baseline and validates freshness before relying on structural output.

Bad:

```bash
mkdir -p .scope
printf '[project]\nname = "flext"\n' > .scope/config.toml
```

Why bad: hand-authored config drifts from the official CLI baseline and bypasses validation.

Good:

```bash
cd /tmp/workspace-root
scope workspace init
scope workspace index
```

Why good: workspace bootstrap runs from the correct root after member repositories have already been initialized.

Bad:

```bash
cd /tmp/workspace-root
scope workspace index
```

Why bad: indexing before workspace bootstrap leaves no `scope-workspace.toml` manifest to describe the member repositories.

## Verification

- `test -f .scope/config.toml`
- `scope status`
- `scope index`
- `rm -rf /tmp/scope-project-verify && mkdir -p /tmp/scope-project-verify && cd /tmp/scope-project-verify && scope init && scope status && scope index`
- `rm -rf /tmp/scope-workspace-verify && mkdir -p /tmp/scope-workspace-verify/repo-a && cd /tmp/scope-workspace-verify/repo-a && scope init && cd /tmp/scope-workspace-verify && scope workspace init && scope workspace index`
