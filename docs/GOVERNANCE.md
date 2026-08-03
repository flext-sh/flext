# FLEXT Governance Router

## Purpose

This file maps each change to its canonical owner. It does not restate
engineering law or skill procedures.

## Authority

Apply the newest applicable source in this order:

1. Newest operator request.
2. `~/.agents` universal authority (`AGENTS.md`, `UNIVERSAL_CORE.md`, and universal skills).
3. Project `AGENTS.md` and routed local skills.
4. Bead execution and status SSOT.
5. In-scope ADR in [`architecture/adr/`](architecture/adr/README.md).
6. Supporting documentation.

When a higher source changes reality, update the affected lower sources in the
same change. Ask before acting only when the conflict cannot be resolved from
this order.

## Owner Routing

| Concern | Canonical owner | Decisive validation |
| --- | --- | --- |
| Provider activation and exported paths | `~/.agents` provider authority | typed manifest and exact-path inventory validation |
| Session routing | `~/.agents/skills/flext-context-routing/SKILL.md` | marker and selected-skill evidence |
| Architecture and public contracts | [ADR registry](architecture/adr/README.md) and owning source declaration | consumer audit plus affected project gates |
| Ecosystem coordination (internal + external projects) | [ADR-009](architecture/adr/009-ecosystem-coordination-and-library-evaluation.md) and [ecosystem-coordination.md](architecture/ecosystem-coordination.md) | reverse-dependency gate plus owner-local ADR consistency (`0.20.0-dev`) |
| Runtime coding patterns | smallest matching skill under `~/.agents/skills/` | fresh import, lint, typecheck, behavior gate |
| Quality commands | `~/.agents/skills/flext-inviolable-rules/SKILL.md` | exact command, exit code, decisive output |
| Documentation lifecycle | [`standards/documentation.md`](standards/documentation.md) | narrow markdown gate, then docs audit |
| Workspace Make behavior | [ADR-003](architecture/adr/003-workspace-tooling-hub-distribution.md) and [ADR-004](architecture/adr/004-generic-make-framework-in-flext-tests.md) | `make help` and affected dispatcher gate |
| Enforcement catalog identity and routing | `flext-core` enforcement declarations | catalog census and public import |
| Declarative enforcement payloads and execution | `flext-infra` rules, schemas, and engine | enforcement engine result |
| Structural codemods | provider referenced by the `~/.agents` authority | preview, exact cardinality, apply, idempotence |

The owning declaration, validated config, or fundamental rule is the source of
truth. Tests and checks validate it; they never define the contract, catalog,
or routing decision.

## Execution Contract

- Use the workspace-root Beads database for the root and every member project.
  Only an independent project owns a separate tracker.
- Claim and record disjoint path ownership before writes. Append evidence after
  every state-changing step.
- Inspect the real owner and all affected consumers before changing behavior.
- Update docs, skills, agents, and provider metadata when reality changes; when
  it does not, verify the impacted surfaces are current.
- Keep one owner per fact. Delete replaced prose, aliases, wrappers, fallbacks,
  and parallel paths in the same change.
- Land only after narrow gates and the affected native gate pass. Use explicit
  pathspecs, a scoped commit, a fast-forward push, and Bead evidence.

Static enforcement and structural codemods are separate responsibilities.
Declarative enforcement data owns policy; the referenced codemod provider owns
safe, deterministic source transformations. Neither duplicates the other.

## Universal test contract (P0)

Tests must validate any change to config and settings by construction. They are
never allowed to hardcode the values that happen to exist today.

- The canonical owner of a fact is `config/*.yaml` and `settings`; tests and
  golden files only validate that owner.
- Expected config-owned values must be read from the same typed SSOT production
  reads, or proven through a generator/consumer round-trip.
- When config or settings change, tests must adapt automatically or fail with a
  clear message pointing back to the config source.
- A test that requires a rewrite to accommodate a legitimate config change is a
  defect in the test, not a reason to freeze the configuration.
- This rule applies to all test tiers, markdown examples, and docstring snippets
  validated by the pytest plugin.
- Literal expectations are reserved for immutable external protocol contracts.

## Baseline Commands

Choose the narrowest decisive command from the quality-gates skill, then widen
only after it passes:

```bash
make check PROJECT=<project> CHECK_GATES=<gates>
make val VALIDATE_SCOPE=workspace
```

All FLEXT validation uses the root Make dispatcher; never run bare `ruff`,
`pyrefly`, `pyright`, `mypy`, or `pytest` commands.

Record every red or green result with its exit code and decisive output in the
active workspace-root Bead.

For the worker lane contract, see [`ways-of-working/worker-lane-contract.md`](ways-of-working/worker-lane-contract.md).
