# Development Standards

This standard summarizes the root `AGENTS.md` and branch-matched `flext-law`.
Those authorities, the nearest package scope, and the active Bead own execution.

## Ownership and architecture

- Read the canonical owner and every consumer before mutation.
- Keep the strict `settings -> config -> c -> t -> p -> m -> u -> base ->
  services -> api -> cli` direction.
- Put generic reusable declarations and behavior in the package's canonical
  `c`, `t`, `p`, `m`, or `u` facade.
- Wire dependencies once through typed `p` protocols at the public composition
  root.
- Remove replaced owners after every consumer is rewired. Compatibility aliases,
  duplicate registries, fallback paths, and temporary bridges are prohibited.

## Configuration and types

- Typed config and settings own operational and project-controlled values.
- Tests, examples, templates, and docs read the same owner; they never copy
  today's value.
- Parse owned payloads with Pydantic 2 models and expose boundaries through
  `t` aliases and `p` protocols.
- Avoid `Any`, bare `object`, optional compatibility shapes, and untyped mapping
  contracts.
- Declaration layers contain data only. Runtime behavior belongs in `u`, base,
  services, `api.py`, or `cli.py`.

## Imports and modules

- Import config and settings in their canonical single form.
- Consume short facades from the public package boundary.
- Forward imports may be runtime; reverse imports are type-checking only.
- Use one public `api.py`, a thin optional `cli.py`, one class per internal
  module, and no more than 200 logical lines per module.
- Never hand-edit generated facade roots, initializers, managed sections, or
  generated docs.

## Failure semantics

The first exception, traceback, and causal non-zero exit propagate. Do not catch
to normalize, retry, fall back, suppress, skip, or partially complete a failed
operation. Warnings, missing tools, empty output, and stale generated files are
red until their owner is corrected.

## Tests

Tests exercise observable behavior only through public facades. They use `tm`,
the unified `conftest.py`, and typed shared fixtures. Mocks, fakes, stubs,
patching, monkeypatch mutation, private construction, copied setup, and
hardcoded project values are prohibited.

Every test run stays inside the retained Testmon cache owned by the root test
verb.

## Canonical workflow

Start at the workspace root:

```bash
make setup
make help
make gen APPLY=Y
make mod APPLY=Y
make gen APPLY=Y
make gen APPLY=Y
make fix APPLY=Y
make fmt APPLY=Y
make check APPLY=Y
make test APPLY=Y
make conform APPLY=Y
make waza APPLY=Y
```

The final generation pass proves the fixed point. Use only verbs declared by
`make help`, with `APPLY=Y` exactly when the typed Make config requires it. Do
not attach project, file, pattern, action, phase, fix, or changed-only selectors,
and do not invoke underlying tools directly.

## Related

- `AGENTS.md`
- `.agents/skills/flext-law/SKILL.md`
- [Testing standards](testing.md)
- [Documentation standards](documentation.md)
