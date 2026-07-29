---
name: flext-development-workflow
description: 'Describes the end-to-end development workflow for the FLEXT monorepo: environment bootstrap, make targets, RTK command interception, lint/typecheck/test gates, and CI/CD lifecycle. Use when setting up the dev environment, running make check or make test.'
license: MIT
metadata:
  version: 1.0.0
---
# FLEXT Development Workflow

End-to-end development workflow for the FLEXT monorepo.

## Workflow

1. Bootstrap workspace and dependencies.
2. Edit code with skill/rule alignment.
3. Run fast feedback (`make check`, `make test`).
4. Use `make cosmos-help` to discover dispatcher verbs provided by the `~/.ai-hub` workspace base.

## Critical rules

- Prefer `make` verbs over one-off scripts.
- Claim work via `bd` before editing.
- Keep bead notes current with command + output evidence.

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
