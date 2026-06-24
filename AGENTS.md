# AGENTS.md — FLEXT Canonical Engineering Law

<!-- BEGIN UNIVERSAL AGENT LAW (portable; regenerable; do not edit inside) -->
## Universal Agent Law (portable core)

This block references `~/.ai-hub/AGENTS.md` as the single source of truth for the universal cross-project law. The full detailed version lives in `~/.ai-hub/docs/agent-law-full.md`.

### Supreme Rule — Absolute Truth, Never Lie

Honesty at 100%, always, backed by real evidence. "I could not" is always acceptable.

### Supreme Law — Resolve, Never Hide

Fix every defect at the root in GitOps/source and verify green. No bypass, workaround, or suppression.

### Core Rules (R0–R15)

- R0: Zero-tolerance for bypass/fallback/hardcode/stub. Fix root cause generically.
- R1: Fix-forward-only. Never `git checkout/restore/reset --hard/stash/revert` another's work.
- R2: Root-cause only. No TODOs, fakes, fallbacks, suppressions.
- R3: Stay in scope. No unrequested changes.
- R4: Evidence before claiming done (command + exit code + output).
- R5: Land your work — commit and push verified changes, no agent attribution.
- R6: Strict typing. No `Any`/bare `object`.
- R7: Bare commands only; no `.venv/bin/` prefixes.
- R8: Fix docs at the source.
- R9: GitOps is the only cluster-management channel.
- R10: Blocked operation protocol — STOP, diagnose, hand to user, wait.
- R11: Execute as planned, else stop and ask.
- R12: Production-readiness — every non-green is an incident.
- R13: Change accountability — atomic, impact/risk declared, no compat shims.
- R14: Dev/prod parity.
- R15: Bead ledger discipline — continuous status and evidence.

### Context-Economy Directive

Do not restate these rules. Prefer targeted tool calls and `make` verbs.

<!-- END UNIVERSAL AGENT LAW -->

## Scope and authoritative sources

1. User request (highest)
2. `AGENTS.md` (this file)
3. `~/.claude/AGENTS.md`
4. `.agents/skills/*/SKILL.md`

`AGENTS.md` below is the operational summary for the monorepo. Detailed mechanics live in SKILL docs.

## Quick execution flow (per task)

1. Confirm active bead/issue and ownership with `bd ready` and `bd show <id>`.
2. Read the relevant local scoped SKILL docs before editing.
3. Run the narrowest smell/quality discovery first (`qlty`, `rg`, `sg`, or `scope` as available).
4. Reuse canonical origin before creating helpers/abstractions.
5. Make the minimal fix, then run the first local validation gate.
6. Update impacted callers in the same cycle.
7. Record evidence and next step in Beads before any handoff.

Any unresolved blocker at step 6 keeps the change incomplete.

## Non-negotiables

- Do not introduce bypasses, shims, fallbacks, compat aliases, or pass-through wrappers.
- No ad-hoc helper inflation without proving the canonical owner is missing.
- No broad edits outside the active lane.
- Do not edit `.beads/*.jsonl` manually.
- Prefer `make`/`ruff`/`pyrefly` workflows over one-off scripts for broad refactors.
- If a command is blocked or ambiguous, stop and surface evidence instead of inventing a workaround.

## FLEXT architecture constraints (compact)

### Stack and style

- Python 3.13+, Pydantic v2, Ruff, Pyrefly, Pyright, Mypy, Make.
- Follow MRO namespace classes and project facades (`c/m/t/p/u`, etc.).
- One canonical class/namespace owner per concern before adding new constructs.
- Prefer composing via MRO + mixins over duplicate utilities.

### Naming and contracts

- Keep aliases canonical: `c`, `m`, `t`, `p`, `u`, and operational aliases (`r`, `e`, `s`, `x`) from project facades.
- Use `r[T]` for fallible app paths (avoid ad-hoc error dicts or raw exceptions for control flow).
- Keep `__init__.py` as export-only.
- Keep abstractions layered by project boundaries (`src` first, tests/examples/scripts are consumers).

### API/runtime constraints

- Prefer typed `OptionsModel.model_validate(kwargs)` for dynamic payloads.
- Avoid raw `os.environ` in `src/` runtime; go through settings abstractions.
- Do not import abstracted framework libs directly from consumer projects; use FLEXT abstractions.
- Reject speculative architecture migration without a concrete blocker and a scoped acceptance target.

## Project map

- Governed packages: `flext-*`.
- Root docs and onboarding: `docs/`.
- Shared tests: `tests/` and project-local `tests/` trees.
- Scripts/tools: `scripts/`, `workspace_custom.mk`, top-level `Makefile`.

## Build, test, and local dev commands

```bash
make help
make boot
make check
make check PROJECT=<proj> CHECK_GATES=<gates>
make test PROJECT=<proj> MATCH=<expr>
make docs DOCS_PHASE=<generate|fix|audit|build|validate> PROJECT=<proj>
make val VALIDATE_SCOPE=workspace
make ship WHAT=<save|tag|push|pr|rel>
```

Common gate values: `lint`, `format`, `pyrefly`, `mypy`, `pyright`, `markdown`, `go`, `loc-cap`, `boundary`, `coordination`.

Recommended baseline for contribution work:

- `make check CHANGED_ONLY=1`
- `make test PROJECT=<proj> MATCH=docs`
- `make val VALIDATE_SCOPE=workspace`

## Testing and quality gates

- `ruff` and `pyrefly` are the first gates for touched files.
- For project-level contract changes, run project-local checks before wider propagation.
- Keep failure evidence in Beads: command, output, and exit code.

## Commit and PR behavior

- Default profile is conservative: no commit/push without explicit authorization.
- If authorization exists, stage only lane files; avoid `git add .`.
- PRs/commits should state: scope, why, commands run, and remaining risk.

## Tooling and agent workflow (ECC alignment)

- Use repository skills: `.agents/skills/*` and `gd`/`scope`/`sg` where available.
- `make` is the canonical execution lane; avoid direct `git`-wide scripts when a Make target exists.
- Bead system (`bd`) is the mandatory work ledger.
- Repeated cross-file edits require caller/audit validation before marking done.

## Temporary lane policy

Session-specific overrides are read from active Beads only. If a migration lane is active, follow its explicit cadence and checkpoint requirements; do not create alternate timers/watchers.

## Verification expectation

A task is complete only with:

- objective command evidence (command + exit code + output),
- no unresolved scoped smells in the touched lane,
- bead notes updated with blocker status or completion evidence.
