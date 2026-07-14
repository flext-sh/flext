---
name: flext-development-workflow
description: 'Describes the end-to-end development workflow for the FLEXT monorepo:
  environment bootstrap, make targets, RTK command interception, lint/typecheck/test
  gates, and CI/CD lifecycle. Use when setting up the dev environment, running make
  check or make test. DO NOT USE FOR: questions unrelated to flext-development-workflow
  creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.1.0
---
# FLEXT Development Workflow

**UTILITY SKILL**

End-to-end development workflow for the FLEXT monorepo.

## USE FOR

- Setting up the development environment.
- Discovering make targets and dispatcher verbs.
- Understanding lint/typecheck/test/CI lifecycle.

## DO NOT USE FOR

- Questions unrelated to FLEXT workflow.
- Creating projects or architecture from scratch.

## Workflow

<!-- mro-wkii.17.26 (agent: codex) — make a clean baseline precede automated refactoring. -->
1. Align the active Beads, ADRs, governance, skills, and file ownership.
2. Finish every active merge semantically and prove that the index has no
   unmerged paths or conflict markers.
3. Establish a clean baseline with fresh imports, Ruff check and format,
   Pyrefly, Mypy, Pyright, and scoped pytest all at exit zero.
4. Run broad refactors only through the `flext-infra conform` transactional
   worktree: analyze, plan, patch-check, validate, preview, then apply.
5. Re-run the same gates after every batch and prove a second conform pass is
   empty before landing.
6. Use `make cosmos-help` to discover dispatcher verbs provided by the
   `~/.ai-hub` workspace base.

## Critical rules

- Prefer `make` verbs over one-off scripts.
- Claim work via `bd` before editing.
- Keep bead notes current with command + output evidence.
- Never run an auto-fix as an implicit gate. A fix must be an explicit planned
  transaction whose patch is reviewed before application.

## Bootstrap

```bash
make boot
```

## Common make targets

| Target | Purpose |
|--------|---------|
| `make help` | List available targets |
| `make boot` | Bootstrap workspace |
| `make check` | Run gates on changed files |
| `make check PROJECT=<proj> CHECK_GATES=<gates>` | Run specific gates on a project |
| `make test PROJECT=<proj> MATCH=<expr>` | Run matching tests |
| `make docs DOCS_PHASE=<generate\|fix\|audit\|build\|validate>` | Docs lifecycle |
| `make val VALIDATE_SCOPE=workspace` | Full workspace validation |
| `make ship WHAT=<save\|tag\|push\|pr\|rel>` | Release helpers |
| `make cosmos-help` | `~/.ai-hub` dispatcher verbs |

## Per-task flow

1. Confirm active bead with `bd ready` and `bd show <id>`.
2. Read the relevant local scoped SKILL docs before editing.
3. Run the narrowest smell/quality discovery first.
4. Reuse canonical origin before adding helpers.
5. Make the minimal fix, then run the first local validation gate.
6. Update impacted callers in the same cycle.
7. Record evidence and next step in Beads before any handoff.

## Commit behavior

- Stage only active bead lane files with explicit pathspecs.
- Never use `git add .`.
- Commit and push after scoped green validation.
- Write commits as the user with no agent attribution.

## References

- `AGENTS.md` — root engineering law and verification expectation
- `.agents/skills/coding-standards/SKILL.md` — coding standards
- `.agents/skills/flext-quality-gates/SKILL.md` — gate commands
