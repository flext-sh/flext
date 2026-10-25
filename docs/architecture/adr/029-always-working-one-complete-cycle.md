# ADR-029 — Always Working: One Complete Cycle Per Slice

<!-- TOC START -->

- [Context](#context)
- [Decision](#decision)
- [The cycle](#the-cycle)
- [Prohibited](#prohibited)
- [Enforcement](#enforcement)
- [Current state and recovery order](#current-state-and-recovery-order)
- [Consequences](#consequences)

<!-- TOC END -->

- **Status:** ACCEPTED — operator orders 2026-10-24 (verbatim below)
- **Date:** 2026-10-24
- **Scope:** every FLEXT repository (superproject, every member, external consumers
  such as ai-hub) and every agent or session working in them
- **Tracker memories:** `operator-order-2026-10-24-always-working-never-skip-phase`,
  `operator-order-2026-10-24-no-incomplete-pushes`
- **Complements:** root `AGENTS.md` contract item 9, the global
  `phase-admission-protocol` rule, ADR-028

## Context

Operator orders, 2026-10-24, verbatim:

> "pare de gravar, testar, subir código incompleto e com erro, termine para poder
> deixar uma versão na tip das branch de integração"
>
> "isso tem que estar FUNCIONANDO SEMPRE, 100% DO TEMPO, SEMPRE, SEMPRE, SEMPRE,
> SEMPRE, ANTES DE PULAR UMA FASE, ANTES DE COMEÇAR OUTRA FASE, SEMPRE, SEMPRE,
> SEMPRE, SEMPRE, PQP, PARE DE PULAR OU DEIXAR PARA DEPOIS QQ COISA, E COMEÇAR ALGO
> COM OUTRA INCOMPLETA ISSO PRECISA SER PROIBIDO COM TODAS AS FORÇAS DO MUNDO POR
> agents/ skills AGENTS.md ADRs docs memoria, tudo, tudo, tudo, faça o ciclo completo
> e não deixe o projeto quebrado ou com runtime falhado, minha paciencia ACABOU !!!!!!!
> de novo em hipótese alguma ... QUEM ME VIER COM DESCULPA PARA NAO CONCLUIR VAI SER
> EXPULSO DO PROJETO"

The failure behind these orders is measured, not hypothetical. On 2026-10-24:

- several initiatives were opened in parallel while earlier ones were still red;
- `[WIP]` commits of red states were pushed to `upload-20261007`;
- all 32 `upload-20261007` → `0.12.0-dev` pull requests carried red CI;
- reds were reported as "fixed later in the wave" instead of being fixed;
- nothing reached the integration branch `0.12.0-dev`.

## Decision

1. **The project and its runtime work 100% of the time.** No integration tip and no
   published branch is left with a red gate, a failing test or a broken runtime.
2. **Exactly one active slice.** A slice is the smallest unit of work that leaves the
   project working. It is finished completely before any other slice or phase starts.
3. **Nothing is skipped, deferred or parked.** A red found anywhere in the slice's
   blast radius — including pre-existing reds — is fixed immediately at its owner,
   inside the active slice. "Later", "next wave" and "pre-existing" are not
   dispositions.
4. **No incomplete or red code is committed, tested or pushed.** Tests never run while
   `check` is red. A commit exists only for a slice that already passed its cycle.
5. **No excuse replaces completion.** An explanation of why something could not be
   finished is not a result; the slice continues until it is finished. A genuine
   blocker that only the operator can resolve is raised as one precise question and
   the slice stays open, never silently dropped.

## The cycle

A slice is complete only when every step below has passed, in this order, with the
command, working directory, exit code and decisive output recorded on its bead:

1. `make gen` twice in every touched repository; the second run produces no change.
2. `make fmt`, then `make fix`, with every finding cleared.
3. `make mod`, clean.
4. `make check`: lint, format, types (ruff, pyrefly, pyright, mypy), rule catalog and
   every configured gate at zero findings.
5. `make tests`, only after `check` is green: zero failures, errors and warnings.
6. Real runtime proof through the public consumer (CLI from a neutral directory,
   installed artifact, real service), not only tests.
7. Commit by explicit paths, fast-forward push, pull request to the integration
   branch, CI green, merge, and the same gates re-run on the merged SHA.
8. Bead closed with four-source evidence.

## Prohibited

- Starting a phase or slice while another is incomplete.
- Pushing, merging or tagging a red state, including `[WIP]` snapshots of red work.
- Running tests on a red `check`.
- Leaving a red found in the blast radius for later, or attributing it to someone
  else instead of fixing it.
- Reporting a slice as done, fixed or green without the cycle evidence above.

## Enforcement

- Root `AGENTS.md` contract item 9 and the global `phase-admission-protocol` rule
  declare the law for every agent.
- `make tests` refuses to run on a red same-scope `check` receipt (bead
  `flext-p4lve`); the generated CI already gates tests on `check`.
- The generated pre-commit hook runs only fast gates and never accepts a red tree
  (bead `flext-x2p69`).
- Pull requests merge only on green CI; gates re-run on the merged SHA.

## Current state and recovery order

As of this ADR, `upload-20261007` is red in the superproject and in most members, and
`0.12.0-dev` has not received the work. The recovery follows the cycle strictly, one
slice at a time, starting with the toolchain owners:

1. flext-infra: `gen` → `fmt` → `fix` → `mod` → `check` → `tests` green, its own lock
   relocked by `make upg`, runtime proven.
2. flext-core, flext-cli, flext-tests in dependency order, each through the full
   cycle, with the deprecated-signature window keeping every consumer working.
3. The toolchain lands on `0.12.0-dev`; then every member in dependency waves, each
   one green and merged before the next starts; then the superproject.

## Consequences

- Throughput is measured in slices merged green, not in commits pushed.
- Parallel sessions coordinate so that only one heavy gate runs at a time and each
  owns exactly one active slice.
- An unfinished slice blocks every later one until it is finished.
