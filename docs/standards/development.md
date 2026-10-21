# Development Standards

<!-- TOC START -->

- [Ownership and architecture](#ownership-and-architecture)
- [Configuration and types](#configuration-and-types)
- [Imports and modules](#imports-and-modules)
- [Failure semantics](#failure-semantics)
- [Tests](#tests)
- [Canonical workflow](#canonical-workflow)
- [Related](#related)

<!-- TOC END -->

This standard summarizes the root `AGENTS.md` and branch-matched `flext-law`. Those
authorities, the nearest package scope, and the active Bead own execution.

Provider-neutral engineering law is owned by `~/agents/`, including its
`engineering-core`, `production-readiness`, `living-documentation`, and
`fix-forward-collaboration` rules. Installed and generated instructions consume
that authority; they are not competing sources. External forks retain their
upstream-specific architecture and delivery workflow.

## Ownership and architecture

- Read the canonical owner and every consumer before mutation.
- Consult documentation, ADRs, the approved plan and specifications, and align
  their intended contract before implementation. Do not change functionality or
  business rules without the plan's or operator's explicit authorization.
- Keep the strict
  `settings -> config -> c -> t -> p -> m -> u -> base -> services -> api -> cli`
  direction.
- Put generic reusable declarations and behavior in the package's canonical `c`, `t`,
  `p`, `m`, or `u` facade.
- Wire dependencies once through typed `p` protocols at the public composition root.
- Remove replaced owners after every consumer is rewired. Compatibility aliases,
  duplicate registries, fallback paths, and temporary bridges are prohibited.
- Apply DDD, Clean Architecture, DI, DRY, YAGNI, SSOT, KISS and SOLID; avoid god
  components and abstractions without a real consumer.

## Configuration and types

- Typed config and settings own operational and project-controlled values.
- Tests, examples, templates, and docs read the same owner; they never copy today's
  value.
- Parse owned payloads with Pydantic 2 models and expose boundaries through `t` aliases
  and `p` protocols.
- Avoid `Any`, bare `object`, optional compatibility shapes, and untyped mapping
  contracts.
- Declaration layers contain data only. Runtime behavior belongs in `u`, base, services,
  `api.py`, or `cli.py`.

Pydantic 2 and the Mypy `pydantic.mypy` plugin are mandatory. The typed policy in
`flext-infra/config/tooling.yaml` owns the suspension of `prop-decorator` and
`call-arg`; generators, profiles, overlays, and CLI consumers must preserve that
policy. Do not disable the plugin or rewrite valid runtime contracts to accommodate
these diagnostics.

Treat code changes motivated by those diagnostics as regressions. Establish the
causal commit and prior public contract, restore only the affected hunks, and preserve
independent runtime and architecture fixes. Source findings are not runtime proof.

## Imports and modules

- Import config and settings in their canonical single form.
- Consume short facades from the public package boundary.
- Forward imports may be runtime; reverse imports are type-checking only.
- Use one public `api.py`, a thin optional `cli.py`, and one class per internal module.
  The module size limit is owned by `loc_cap.max_lines` in
  `flext-infra/config/codegen.yaml`; guidance must not copy its current value.
- Never hand-edit generated facade roots, initializers, managed sections, or generated
  docs.

## Failure semantics

The first exception, traceback, and causal non-zero exit propagate. Do not catch to
normalize, retry, fall back, suppress, skip, or partially complete a failed operation.
Warnings, missing tools, empty output, and stale generated files are red until their
owner is corrected.

## Tests

Tests exercise observable behavior only through public facades. They use `tm`, the
unified `conftest.py`, and typed shared fixtures. Mocks, fakes, stubs, patching,
monkeypatch mutation, private construction, copied setup, and hardcoded project values
are prohibited.

Every test run stays inside the retained Testmon cache owned by the root test verb.

## Canonical workflow

Start at the workspace root:

```bash
make setup
make help
make gen
make mod
make gen
make gen
make fix
make fmt
make check
make test
make gen
make waza
```

A final generation pass alone does not prove a fixed point. Prove convergence of the
same final candidate as required by the stabilization runbook's
[canonical cycle](../ways-of-working/stabilization-checkpoint-0.12.md#a-canonical-cycle).
Use declared canonical verbs and their documented inputs. Do not attach effect
selectors or retired execution toggles to standard lifecycle verbs, or invoke
underlying tools directly. A scoped verb does not replace required full-lifecycle
gates.

All known defects in the applicable scope must be corrected before phase closure.
Recording a Bead, passing selected tests, or preparing an unapplied patch is not
completion. Fixes and hotfixes reach the declared integration branch in the same
delivery cycle, with proof that the integrated public behavior works. Missing
authority or prerequisites are explicit blockers, never fabricated readiness.

Dirty Git state and concurrent WIP are expected throughout this workflow. Preserve
and adopt compatible work, revalidate affected inputs and fix forward. Do not
require cleanup, exclusive writers, a frozen tree or unrelated commits to proceed.

Every change, including documentation and configuration, requires the applicable
native lint, type, test, documentation, and build gates. Exercise the real public
consumer before encoding its behavior in tests. Record the command, working directory,
exit status, decisive output, and candidate SHA; static checks alone do not establish
working runtime behavior.

## Related

- `AGENTS.md`
- `.agents/skills/flext-law/SKILL.md`
- [Testing standards](testing.md)
- [Documentation standards](documentation.md)
