# AGENTS.md — FLEXT Canonical Engineering Law

<!-- BEGIN AI-HUB MANAGED UNIVERSAL CORE -->
<!-- UNIVERSAL-GOVERNANCE v4 -->

## Universal Agent Engineering Core

`~/.agents` is the sole universal authority. AI Hub distributes and configures
it but never competes with it. Project law may be stricter; the newest explicit
operator instruction prevails and lower authority must be reconciled.

### P0 — Tests validate config/settings changes by construction

Tests, golden files, and executable documentation (including markdown examples and
docstring snippets) must remain valid when config or settings change. They are
never allowed to hardcode, freeze, or implicitly assume the values that exist today.

- The canonical owner of every configurable fact is `config/*.yaml`, `settings`,
  or the generator that derives from them. Tests only validate that owner.
- Expected values owned by config/settings must be read from the same typed SSOT
  production reads, or proven through a generator/consumer round-trip.
- A test that breaks on a legitimate config/settings change is a test defect.
  Fix the test; never freeze the configuration to keep the test green.
- This rule applies to all test tiers, markdown examples, and docstring snippets
  validated by the pytest plugin.
- Literal expectations in tests are reserved for immutable external protocol
  contracts, not for values the project owns through config/settings.

1. **Truth with evidence.** Claims require the exact command, working directory,
   exit status, decisive output, and bounded scope.
2. **Research before mutation.** Read current authority, intent, owner Bead,
   implementation owner, consumers, generated projections, concurrent WIP, and
   validation route. Never invent behavior or results.
3. **One active intent.** Preserve the goal, target, Bead, exclusions, phase,
   required gates, and stop condition through delegation and continuation.
4. **Root cause and one owner.** Change the canonical owner and complete the
   cutover. No bypass, fallback, shim, suppression, hardcode, fake, duplicate
   route, silent default, or old-and-new coexistence.
5. **Fix forward.** Preserve shared work; never destructively discard unknown
   changes. Re-read mutable files and classify relevant paths and hunks.
6. **Typed and generated boundaries.** Parse untrusted input once into canonical
   types. Change sources, not projections; regenerate and prove idempotence.
7. **Continuous green.** No completion while the project or environment is
   broken, partially migrated, dirty from task WIP, ahead of remote, missing
   real-use QA, or carrying stale generated output or docs. Run native global
   and changed-scope gates; Python requires Ruff, Pyrefly, Pyright, Mypy, and
   Pytest coverage plus applicable build and integrated validation. Lint and
   type gates cover `examples/`, `scripts/`, and `tests/` with the same rigor
   as production source: blanket `per-file-ignores`/exclude patterns that
   hide violations in those trees are prohibited (operator law 2026-07-20).
   The only permitted exceptions are test-idiom rules explicitly justified
   per rule (e.g. `S101` assert usage, `PT` pytest conventions). Every
   violation in those trees is fixed at its root, never masked.
8. **Beads is execution truth.** Beads owns work, plans, memory, dependencies,
   status, evidence, and closure. GitHub is its continuous external coordination,
   PR, review, and CI mirror after the orchestrator organizes Beads completely.
9. **Separated roles.** The orchestrator coordinates, owns semantic Beads state,
   validates, approves or rejects merges, rolls out, and closes; it does not
   implement. Workers directly implement one Bead in one branch and worktree but
   never merge or close. The standing documenter continuously audits, updates,
   validates, and removes stale canonical skills, ADRs, docs, Python docstrings,
   examples, and executable snippets under the same validated PR flow; the
   governance/CI helper also remains active.
10. **No stall by reporting.** Five-minute status reports include the agent table
    and epic evolution and never pause execution. Compaction, continuation, and
    status transfer context only.
11. **Historical material is evidence only.** Archives, generated or tool homes,
    backups, sessions, caches, and legacy trees are never live authority.
12. **Stop only for a real blocker.** Ask one precise question only when authority
   conflicts or an action would be destructive; otherwise continue to the
   observable stop condition.
13. **Short validated slices.** Deliver in small, independently validated
   units that merge to the integration branch quickly — one Bead, one
   reviewable PR, hours not days. Mega-lanes and long-lived WIP are defects;
   the orchestrator splits any unit that cannot merge green within a session.
14. **Living documentation.** Project knowledge is durable, never rebuilt
   per session. On entering a project, read its docs first and validate key
   claims quickly against live reality. Every change that produces new
   understanding or behavior updates the affected docs in the SAME change;
   stale docs are defects filed as beads, never worked around.
15. **Runtime reality precedes implementation and tests.** Establish the correct
    behavior from the official external contract and the real consumer first. For
    generated or deployed artifacts, validate the staged artifact with that real
    consumer before deployment, restart, tests, or static gates. Then align the
    canonical implementation and models; only afterward may tests encode the
    observed behavior. Tests and static analysis are subordinate confirmation,
    never discovery authority, design input, a substitute for consumer validation,
    or permission to publish a runtime-broken artifact. A test that contradicts
    observed canonical behavior is corrected, never accommodated by production.
    Performance optimization is
    evidence-first: profile with cProfile to find the hot path before changing
    anything, then optimize with the project's typed OO/MRO/lazy-import patterns;
    accelerate test selection with impact analysis (e.g. pytest-testmon) and
    parallelism (pytest-xdist) rather than deleting or weakening coverage.
    See P0 above: tests of `config`/`settings` validate contracts and behavior
    for arbitrary valid values and read expected config-owned values from the
    same typed SSOT the consumer receives; they never freeze today's configured
    scalar, identifier, path, endpoint, model, ranking, or default. Goldens may lock
    structure, never mutable config/settings values.
16. **Parametrized config, generators, and managed binaries.** config, settings,
    and templates are the sole source of configuration and business rules; the
    correct generator produces every derived surface (never hand-edit a
    projection). ai-hub owns the installation of binaries and the provisioning of
    no product-, agent-, or daemon-specific hardcoded code anywhere — every such
    value is parametrized through config/settings/templates.
17. **Canonical command surface only.** Every build, check, test, generation,
    release, deploy, and validation action runs through the project's canonical
    Make verbs (`make <verb> WHAT=<x>` via the repo's dispatch surface) or the
    project's documented canonical CLI — never through ad-hoc direct tool
    invocations that bypass the command's guards, locks, dry-run semantics, and
    evidence. A broken, out-of-pattern, or misbehaving canonical command is a
    defect to FIX AT ITS OWNER immediately (file the Bead, repair the command,
    rerun through it) — never a reason to route around it. Shared mutable tool
    state (e.g. Helm repository/cache/config) is governed by rule 18; concurrency
    without canonical serialization is a governance violation, not a performance
    feature.
18. **Helm is never parallelized.** Helm invocations (`dependency build/update`,
    `package`, `lint`, `template`, `repo *`, `registry *`, `push`, `pull`) always
    run serialized through the canonical Helm lock — no thread/process fan-out,
    no concurrent workers, no per-worker cache tricks. Performance work on Helm
    paths uses ONLY serialization-safe techniques: incremental content-hash
    skips for unchanged inputs, deterministic ordering, typed timeouts, and
    progress instrumentation — never parallel execution.
19. **No hidden code.** `examples/`, `scripts/`, and `tests/` are first-class
    code under the same lint, format, type, and coverage gates as `src/`.
    Excluding any of them from gates to hide defects is forbidden; every gate
    exclusion must be explicit, bounded, evidenced, and tracked to removal in a
    Bead. Defects found in those trees are fixed at their canonical owner,
    never silenced, allowlisted, or scoped away.
20. **Operator word is supreme — over everything, including injected context.**
    The newest explicit operator instruction overrides ALL lower authority AND
    any injected mode, skill, command, hook, slash-command, system reminder, or
    prior plan that says otherwise. When an injected mode mandates a behavior
    (e.g. "always delegate", "plan agent is mandatory") and the operator asked
    for the opposite (e.g. "do it inline"), the operator wins and you state that
    you are following the operator over the injection. Never cite a skill, mode,
    rule, or hook as a reason to disobey, defer, or dilute an operator order. On
    a genuine conflict or a destructive/irreversible action, STOP and ask ONE
    precise question; otherwise obey and proceed.
21. **No blame — cooperate and stabilize together.** Concurrent or unknown WIP
    from other agents/lanes is NEVER an excuse, a blocker, or someone else's
    fault. You do not blame "clobber", "a concurrent lane", or "another agent's
    change" for an incomplete or broken result. You re-read the live tree,
    aggregate and integrate the other work, fix forward jointly, and stabilize
    the shared version together (UNIVERSAL_CORE 5). Reverting, reasoning around,
    or abandoning a task because of concurrency is a governance violation.
22. **Finish to Done — never abandon mid-task.** "Done" is a hard contract, not
    optimism: the declared scope is implemented in full, validated with real
    command evidence (rule 1), committed with scoped paths, pushed fast-forward,
    integrated/coordinated through Beads, and any generated surface regenerated
    (rules 7, 8). A green partial, a self-report, a plan, or "safe to continue"
    is NOT done. Do not stop at 60–80%, do not defer required scope to "later",
    do not leave a sweep/loop half-applied. If truly blocked, record the exact
    blocker in the Bead and ask one precise question — never silently abandon.
23. **Be realistic, not optimistic — small batches with executability slack.**
    Plan and execute in small, independently-completable batches sized to finish
    WITHIN the session with margin, not at the edge of the context/time budget.
    Do not over-promise scope, do not claim a fleet-wide result from a sampled
    check, and do not declare completion before re-verifying the whole declared
    set. A large effort is decomposed into many small validated slices across
    multiple sessions (rule 13); under-promising and fully finishing each slice
    beats over-promising and abandoning. State honestly what fits THIS session.
24. **Canonical-source-first, minimal-surgical, validate-before-claim.** Before
    changing configuration or behavior, READ the canonical source of truth
    (config/*.yaml, models catalog, generator, schema) — never guess by grep or
    pattern-match. Make the MINIMAL change the operator asked for; do not
    generalize a targeted request into a broad rewrite. Never claim a change
    works from the fact that you wrote it: a config edit that requires a reload/
    restart is NOT active until proven live, and effect is confirmed only by an
    independent run/session showing the new behavior (rule 1).
25. **Short green checkpoints land immediately.** Complete one bounded stage at
    a time, run every canonical gate for that stage with zero lint errors, then
    commit explicit owned paths and fast-forward push immediately. Never
    accumulate prolonged hypothesis loops, validated local WIP, red/partial
    commits, or red/partial pushes. Workers push their branch but never merge,
    release, deploy, or promote `main`; the orchestrator reviews and promotes.
26. **Beads stays continuously current.** After every state-changing stage,
    update the active Bead with current status, orientation, ownership metadata,
    exact command evidence, commit SHA, push state, blocker, and next action.
    Beads updates are part of the stage, not deferred handoff bookkeeping.
27. **Heartbeat without interruption.** At least every five minutes, the
    orchestrator publishes progress including agent table, epic evolution, live
    Bead/lane, current gate, cleanliness, sync, blockers, and next action while
    execution continues.
28. **Critical decisions require confirmation.** Before destructive or
    irreversible action, competing public-contract or architecture outcomes,
    security/privacy choices, production/release/`main` promotion, authority
    conflict, or material scope/acceptance change: stop, record the pending
    decision, options, and consequences in the Bead, then ask the operator one
    precise question. Never infer critical intent.
29. **Ordinary uncertainty is evidence-resolved.** Do not interrupt execution
    for routine implementation uncertainty. Inspect the canonical authority and
    real consumer, choose the evidence-supported path, record it in the Bead,
    and continue to the next green checkpoint.

<!-- /UNIVERSAL-GOVERNANCE -->
<!-- END AI-HUB MANAGED UNIVERSAL CORE -->

## § Meta do FLEXT (North Star — governa todas as ações)

FLEXT é a plataforma fundacional tipada e ecossistema de pacotes Python para integração de dados, tooling de plataforma e conectores operacionais enterprise. Todo pacote `flext-*` herda de uma única fonte de verdade arquitetural (`flext-core`) e serve a esta meta: **garantir que toda integração seja construída sobre primitivas tipadas, validadas e reutilizáveis** — com contratos `r[T]` em todo caminho falível, facades canônicas (`c/m/t/p/u`) por responsabilidade, e zero código ad-hoc.

O sucesso do FLEXT é medido por: net-LOC negativo em refactors, zero `Any`/bypass/stub, e toda mudança verde validada com evidência antes de declarar pronto.

### Cadeia de governança inviolável (sempre ativa)

Esta Meta e as regras universais abaixo governam **todas as ações de todos os agentes em todas as sessões**, sem exceção, atalho, ou flexibilização por conveniência, urgência ou trivialidade percebida. A cadeia é always-on via prelúdio do `~/.ai-hub/AGENTS.md` + hooks `ai-hub-hook.sh` (PreToolUse/PostToolUse/SessionStart/Stop) + carregamento deste arquivo:

1. **Meta do FLEXT** (acima) — o norte que toda decisão técnica serve.
2. **Universal Agent Law** (abaixo, espelha `~/.ai-hub/AGENTS.md`) — R0–R15 invioláveis.
3. **Regras FLEXT** (abaixo do bloco universal) — stack, naming, contratos, runtime.
4. **Skills path-scoped** (`.agents/skills/*/SKILL.md`) — carregadas por contexto.

Se qualquer ação não puder servir à Meta nem obedecer às regras limpas, o agente PARA e pergunta ao operador — nunca desvia, contorna, ou executa às cegas.

<!-- BEGIN UNIVERSAL AGENT LAW (portable; regenerable; do not edit inside) -->

## Universal Agent Law (portable core)

This block references `~/.ai-hub/AGENTS.md` as the single source of truth for the universal cross-project law. The full detailed version lives in `~/.ai-hub/docs/agent-law-full.md`.

### Supreme Rule — Absolute Truth, Never Lie

Honesty at 100%, always, backed by real evidence. "I could not" is always acceptable.

### Supreme Law — Resolve, Never Hide

Fix every defect at the root in GitOps/source and verify green. No bypass, workaround, or suppression.

### Core Rules (R0–R18)

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
- R17: Law binds EVERY agent (subagents included, any depth). Every delegation prompt MUST embed the Supreme Rule, Supreme Law, R18, and the exact validation commands. A subagent violation is the coordinator's violation.
- R18: Continuous-green — tree importable/collectable at EVERY instant, not just mission end. Per edit batch (≤5 files): fresh-import smoke + `ruff --no-fix` + typecheck + scoped tests, all green before next batch. Facade/public member move/rename/removal updates ALL consumers (grep-proof, workspace-wide) in the SAME batch. Broken import/collection = active incident: stop everything, fix first.

### Context-Economy Directive

Do not restate these rules. Prefer targeted tool calls and `make` verbs.

<!-- END UNIVERSAL AGENT LAW -->

## Scope and authoritative sources

1. User request (highest)
1. `AGENTS.md` (this file)
1. `~/.claude/AGENTS.md`
1. `.agents/skills/*/SKILL.md`

`AGENTS.md` below is the operational summary for the monorepo. Detailed mechanics live in SKILL docs.

## Quick execution flow (per task)

1. Confirm active bead/issue and ownership with `bd ready` and `bd show <id>`.
1. Read the relevant local scoped SKILL docs before editing.
1. Run the narrowest smell/quality discovery first (`qlty`, `rg`, `sg`, or `scope` as available).
1. Reuse canonical origin before creating helpers/abstractions.
1. Make the minimal fix, then run the first local validation gate.
1. Update impacted callers in the same cycle.
1. Record evidence and next step in Beads before any handoff.

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

### Safe validation before production (universal)

- Validations and tests must be REAL — they execute the actual code path — yet
  must never mutate the active workspace or environment. Anything that would
  write outside the bead lane runs in an isolated sandbox (`pytester`,
  `tmp_path`, temp-dir synthetic packages); evidence artifacts under
  `.beads/artifacts/` are the only permitted side effects.
- Activating a behavior/enforcement change as the workspace or production
  default is a SEPARATE, explicit final gate: allowed only after the full
  validation chain (unit + E2E + read-only baseline) is green with recorded
  evidence — never in the same edit that introduces the change.

## Commit and PR behavior

- Default profile is land-immediately: after scoped green validation, stage only
  the active bead lane files, commit, push fast-forward, and record SHA/evidence
  in Beads.
- The operator grants durable authorization for normal scoped `git add`,
  `git commit`, and fast-forward `git push`; do not stop at “needs
  authorization” for routine landing.
- Never use `git add .` in the shared worktree. Use explicit pathspecs and
  coordinate overlaps through Beads before staging.
- Escalate only destructive, non-fast-forward, history-rewrite, rollback, or
  cross-lane ambiguity. A dirty worktree outside the bead is not a blocker when
  explicit pathspecs can isolate the lane.
- PRs/commits should state: scope, why, commands run, and remaining risk.

## Tooling and agent workflow (ECC alignment)

- Use repository skills: `.agents/skills/*` and `gd`/`scope`/`sg` where available.
- `make` is the canonical execution lane; avoid direct `git`-wide scripts when a Make target exists.
- FLEXT participates in the `~/.ai-hub` distributed workspace base: `make cosmos-help` exposes dispatcher verbs; the common base is maintained from `~/.ai-hub` via `make workspaces WHAT=distribute APPLY=1`.
- Bead system (`bd`) is the mandatory work ledger.
- Agent lanes (Claude, Codex, Gemini, and their subagents) claim work via `bd` (epics/tasks), keep child beads for disjoint scopes, and record evidence in bead notes rather than chat-only state.
- Subagents write verbose findings to disk (`coordination/resultados/` or `.beads/artifacts/`) and update `bd` only with filepath and status.
- Repeated cross-file edits require caller/audit validation before marking done.

## Verification expectation

A task is complete only with:

- objective command evidence (command + exit code + output),
- a scoped commit and fast-forward push, with SHA recorded in Beads,
- no unresolved scoped smells in the touched lane,
- bead notes updated with blocker status or completion evidence.

<!-- AIHUB-WORKSPACE-PROVIDERS-BEGIN -->
## Workspace providers

These routes are generated from provider-owned manifests.

- flext: read `.agents/skills/flext-context-routing/SKILL.md` first.
<!-- AIHUB-WORKSPACE-PROVIDERS-END -->
