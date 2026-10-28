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

- **Status:** ACCEPTED — operator orders 2026-10-24, amended 2026-10-26
- **Date:** 2026-10-24
- **Amended:** 2026-10-26 — global primary admission, native Testmon selection and
  serial peripheral-first modification
- **Scope:** every FLEXT repository (superproject, every member, external consumers
  such as ai-hub) and every agent or session working in them
- **Tracker memories:** `operator-order-2026-10-24-always-working-never-skip-phase`,
  `operator-order-2026-10-24-no-incomplete-pushes`,
  `operator-order-2026-10-26-global-ruff-pyrefly-strict-lazy-exports`
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

On 2026-10-26 the operator extended the admission requirement to global Ruff,
Pyrefly and Pytest evidence and required, verbatim, "pytests sempre com testmon
para nao repetir todos toda hora e lentidão é problema gravíssimo". The tracker
memory above retains the complete order. The later approved execution plan
requires global Ruff/Pyrefly admission first, then global native incremental
pytest admission, before dependent work. The latest 2026-10-28 approval requires
three peripheral `mod` pilots in order: `flext-dbt-ldif`, `flext-tap-ldif`,
`flext-target-ldif`. All three complete before modification reaches foundational
consumers. These requirements supersede the older full-check-before-initial-pytest
and foundation-first-mod ordering, not the complete quality contract required
for publication.

## Decision

1. **The project and its runtime work 100% of the time.** No integration tip and no
   published branch is left with a red gate, a failing test or a broken runtime.
2. **Exactly one active slice.** A slice is the smallest unit of work that leaves the
   project working. It is finished completely before any other slice or phase starts.
3. **Nothing is skipped, deferred or parked.** A red found anywhere in the slice's
   blast radius — including pre-existing reds — is fixed immediately at its owner,
   inside the active slice. "Later", "next wave" and "pre-existing" are not
   dispositions.
4. **No incomplete or red code is committed or pushed.** Initial behavioral
   admission requires fresh global source admission, not a claim that the full
   composite check is already green. Every applicable check and behavioral gate
   still passes before publication, integration or advancement beyond the slice.
5. **No excuse replaces completion.** An explanation of why something could not be
   finished is not a result; the slice continues until it is finished. A genuine
   blocker that only the operator can resolve is raised as one precise question and
   the slice stays open, never silently dropped.
6. **Global evidence and native impact selection.** Ruff, Pyrefly and Pytest cover
   the complete declared scope before dependent work advances. Pytest always
   retains the canonical persistent external Testmon database and uses native
   dependency selection over the global applicable inventory. Preserve external
   and slow-test applicability, configuration/toolchain identity, cache integrity,
    and the applicable admission guard. Initial source admission and complete
    check acceptance are distinct typed workflow phases; neither substitutes for
    the other. Repeated full runs, cache resets and deadline inflation do not
    resolve slowness; profile and repair the causal owner.
7. **One original evidence owner.** Both admission phases use the existing native
   checker, capture, diagnostic and publisher primitives. Declare their gate sets
   and dependencies once in typed workflow policy. Source admission covers every
   governed repository with the declared Ruff/Pyrefly gates and no file filters.
   Preserve original invocation, policy and source identity, complete accounting,
   digests, newest same-phase evidence and first-failure semantics. A source-only
   receipt never proves full `check`, integration or release acceptance. An invalid
   or incomplete receipt never falls back to an older successful one.
8. **Small transactions preserve cooperative runtime visibility.** Amendment
   2026-10-28, accepted contract pending implementation: use
   [ADR-018's common barrier and owned-effect recovery](018-generator-declarations.md#single-read-single-batch-publication-amended-2026-10-28-campaign-flext-pipol)
   for live Make/Rope readers and publication. Each entire incremental
   transaction takes at most five seconds, including staged validation,
   publication, native refresh and bounded rollback; the public Make operation
   retains its sixty-second deadline, including lock waits, staging, publication,
   incremental refresh and recovery. The existing performance policy owns
   those budgets; frozen analyzer rules are unchanged. Full gates and real
   runtime proof remain mandatory for every slice. Neither a committed small
   transaction nor its fast gate closes a slice or authorizes advancement.

   The narrow authorization to reverse an unsuccessful transaction's own
   authenticated effects supersedes the older blanket rollback prohibition
   only at this boundary. It never authorizes discarding shared WIP or undoing
   an independently completed transaction. An interrupted transaction or
   conflicting external edit keeps recovery and the containing slice open.

## The cycle

A slice is complete only when every step below has passed, in this order, with the
command, working directory, exit code and decisive output recorded on its bead:

Admission precedes this completion cycle: first global Ruff/Pyrefly, then global
native incremental Testmon pytest. Repair every failure before dependent work.
After source changes, refresh affected evidence and restore global primary
admission; do not replace it with a green member or a stale whole-workspace run.

1. `make gen` twice in every touched repository; the second run produces no change.
2. `make fmt`, then `make fix`, with every finding cleared.
3. `make mod`, clean.
4. `make check`: lint, format, types (ruff, pyrefly, pyright, mypy), rule catalog and
   every configured gate at zero findings.
5. `make tests`: native incremental Testmon selection
   over the complete applicable population, with zero failures, errors and
   warnings. Record collection, selection, execution and deselection separately.
   A typed cache hit requires database integrity and complete accounting; report
   it as a cache hit, never as tests executed and passed. No repeated full pass is
   added to the normal invocation.
6. Real runtime proof through the public consumer (CLI from a neutral directory,
   installed artifact, real service), not only tests.
7. Commit by explicit paths, fast-forward push, pull request to the integration
   branch, CI green, merge, and the same gates re-run on the merged SHA.
8. Bead closed with four-source evidence.

## Prohibited

- Starting a phase or slice while another is incomplete.
- Pushing, merging or tagging a red state, including `[WIP]` snapshots of red work.
- Running initial pytest without fresh global source admission, or presenting
  primary admission as a green full composite check.
- Leaving a red found in the blast radius for later, or attributing it to someone
  else instead of fixing it.
- Reporting a slice as done, fixed or green without the cycle evidence above.

## Enforcement

- Root `AGENTS.md` contract item 9 and the global `phase-admission-protocol` rule
  declare the law for every agent.
- `make tests` and the native workspace test owner require the typed initial
  global source-admission phase. Full-check evidence remains mandatory for
  completion and publication. Align the runner, original capture, generated Make
  and CI workflow consumers together; never remove a guard in isolation or add a
  boolean skip switch (bead `flext-p4lve`).
- The existing runner, execution-mode contract and generated Make owner implement
  Testmon selection and cache accounting. This accepted contract is not evidence
  that generation, global execution or integration has completed.
- The generated pre-commit hook runs only fast gates and never accepts a red tree
  (bead `flext-x2p69`).
- Pull requests merge only on green CI; gates re-run on the merged SHA.

## Current state and recovery order

The dated failures above are recovery evidence, not a substitute for current Beads,
refs, runtime or native receipts. Recover one slice at a time:

The operator-approved 2026-10-28 campaign (`flext-brr3y`) starts with complete
alignment of memories, instructions, documentation, topic ADRs, rules, skills,
commands, existing plan files and Beads before structural reorganization. If a
public command cannot
reach the documentation gates, that first slice includes only the causally
necessary command-bootstrap repair after the documentation alignment. It stays
open until those gates execute successfully; the blocked documentation does not
authorize a structural migration or a later phase.

1. Restore global source and native incremental behavioral admission. Correct
   command, rule, generator and runtime owners without weakening contracts.
2. Repair toolchain implementations at their canonical owners, then complete
   `flext-dbt-ldif`, `flext-tap-ldif` and `flext-target-ldif` in that approved
   order. Each pilot requires behavior, complete gates, unchanged-input
   convergence and integration before the next. Do not apply `mod` to
   foundational consumers until all three pilots are accepted, or silently
   substitute a different pilot after a failure.
3. Continue serially from validated peripheral consumers inward. A new source
   shape extends the same generalized rule and regression corpus, never a
   package-specific exception or a fleet-wide mutation sweep.
4. Publish only fully green scoped slices through the declared integration route,
   verify current-head CI and post-merge behavior, then advance. Lock changes still
   use `make upg` and ADR-030's explicit guard; this ordering does not waive it.

## Consequences

- Throughput is measured in slices merged green, not in commits pushed.
- Parallel sessions coordinate so that only one heavy gate runs at a time and each
  owns exactly one active slice.
- An unfinished slice blocks every later one until it is finished.
