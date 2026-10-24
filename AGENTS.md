# AGENTS.md — FLEXT workspace

FLEXT is a Git superproject of independently versioned Python packages. The member
population is declared in `.gitmodules`. `flext-core` owns runtime primitives;
`flext-infra` owns generation, structural migration and the Make control plane;
`flext-tests` owns shared test infrastructure.

## Authority and entry point

Follow [.agents/commands/flext-law.md](.agents/commands/flext-law.md). Universal
execution rules come from the selected `agents-governance` bundle. This repository
owns only the branch-matched FLEXT domain delta in
[local flext-law](.agents/skills/flext-law/SKILL.md), with rationale in the
[ADR index](docs/architecture/adr/README.md). The nearest member `AGENTS.md` adds
only its domain facts and explicit exclusions. AI Hub delivers instructions; it
never becomes their author.

The active operator request and selected canonical Bead own current intent,
placement, exclusions and evidence. Historical plans, old issue identifiers,
installed projections and another branch do not select today's work. Preserve
and reconcile current WIP before effects. Source validation, reviewed integration
and installed delivery require separate evidence.

In an attached member, resolve this root from the containing Git superproject.
For a standalone checkout, retrieve the FLEXT root and its local flext-law from
the same branch or release as that package. Never substitute `main`, an installed
copy or a same-named skill from a different catalog. Missing or ambiguous branch
identity is an unresolved authority input.

## Domain navigation

| Subject | Canonical owner |
| --- | --- |
| Family shape, MRO and facade direction | [Local flext-law](.agents/skills/flext-law/SKILL.md), ADR-014 |
| Settings, config and project deltas | ADR-005, ADR-016, ADR-024 |
| Protocol ports, model-owned validation and API composition | ADR-019, including its 2026-10-18 amendment |
| Consumer imports and generator declarations | ADR-015, ADR-018 |
| Thin Singer drivers | ADR-006, public `flext-meltano` bases |
| Generation and tooling policy | `flext-infra` typed configuration and templates |
| Testing | [Testing guide](docs/guides/testing.md), public `flext-tests` fixtures |
| Stabilization procedure | [Stabilization checkpoint](docs/ways-of-working/stabilization-checkpoint-0.12.md) |

These references define one contract. A divergent implementation is pending repair;
its existence never supplies an alternative architectural rule or proof of conformance.

## Native command routing

Run operations from the active workspace/worktree root through the declared Make
verbs. The root `make check` checks this root project; it does not prove every
member green. An attached member's declared verb is routed from the workspace root
with `make -f <member>/Makefile <verb>`. A standalone checkout uses its own root.
Discover the current inventory in the selected Makefile; never invent a selector.
Command deadlines, profiling, test selection, evidence and closure are owned by
`rules/workflow/canonical-commands.md` and the global verification procedure.

Generated facets, imports, Makefiles, CI and managed project configuration are
changed at `flext-infra` or a declared configuration delta, then regenerated.
An attached member uses its containing workspace runtime; an independent runtime
root owns its physical environment. Resolve ownership before setup or publication.

## Production Readiness And Connectivity Tests

Across FLEXT, external-service tests require a configured local, untracked `.env`
and a reachable test environment. The shared applicability owner skips those
connectivity tests before service-dependent fixtures when prerequisites are absent
or unreachable. Docker-dependent connectivity tests also skip in CI. Neither a
folder nor an `integration` marker alone makes a test a connectivity test; pure
unit and integration behavior remains active.

An availability skip reports an unmet prerequisite, never successful connectivity
or production validation. With prerequisites available, authentication, protocol,
application and assertion failures remain failures. Keep credentials out of Git and
diagnostics. This local applicability contract follows the operator's 2026-10-10
ruling; global result handling composes it through
`rules/testing/observable-runtime.md`.
