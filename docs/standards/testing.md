# Testing Standards

Tests confirm current observable behavior; they do not own the product contract
or its configuration. Establish runtime reality first, then encode it through a
public facade.

## Public boundary

- Import the package's public `api.py` facade and canonical `c`, `t`, `p`, `m`,
  and `u` surfaces.
- Never import private modules or assert class construction, call routing,
  internal state, or implementation order.
- Validate owned inputs and outputs with Pydantic models and typed protocols.
- Keep the canonical thin `Tests<Unit>` nesting and the standard
  `tests/{unit,integration,e2e}` layout.

## Fixtures and assertions

- Use `tm` for assertions and shared builders from `flext-tests`.
- Put suite wiring in one `conftest.py` and reusable typed fixtures in
  `tests/fixtures/`.
- Prefer fixture factories that create fresh values from typed config, settings,
  constants, models, or public utilities.
- Use public `u` context utilities for environment, filesystem, clock, and
  process boundaries.
- Keep tests deterministic without mocks, fakes, stubs, patching, monkeypatch
  mutation, hidden globals, or copied setup.

## Configuration independence

Project-owned paths, identifiers, endpoints, thresholds, versions, and defaults
come from their typed config or settings owner. Tests and golden files validate
structure and behavior for valid values; they never preserve today's configured
scalar as an expected literal.

Immutable external protocol facts may be literal only when the external
contract, not FLEXT configuration, owns them.

## Failure semantics

- The first exception and raw traceback escape.
- Warnings, skips, empty collection, missing tools, and suppressed failures are
  red.
- No retry, fallback, catch-based normalization, compatibility path, or partial
  execution may turn a failure green.
- A failing test is repaired at the runtime owner or, when the test contradicts
  observed behavior, at the test owner.

## Canonical execution

Every test run starts at the workspace root and flows through the retained
Testmon cache:

```bash
make test APPLY=Y
```

Never invoke the underlying test runner, clear Testmon state, or add project,
file, pattern, changed-only, fix, or phase selectors. Run the complete quality
gate through its root owner:

```bash
make check APPLY=Y
```

If either verb is missing or broken, repair the dispatcher owner and rerun the
same canonical command.

## Generated copies

Generated member guides are projections of root documentation. Change the root
source and regenerate with `make gen APPLY=Y`; never edit a projection directly.

## Related

- `AGENTS.md` — workspace engineering law
- `.agents/skills/flext-law/SKILL.md` — FLEXT architecture law
- [Testing guide](../guides/testing.md)
