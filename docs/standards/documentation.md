# Documentation Standards

FLEXT documentation has one engine: the public docs services and utilities in
`flext-infra`. Projects do not own parallel scripts, generators, API registries,
or local command grammars.

## Writable owners

- Package metadata, typed config, public exports, and docstrings own technical
  facts.
- Root files under `docs/guides/` own generated member guides.
- Templates and typed generator configuration own generated navigation, API
  reference, reports, and site configuration.
- `docs/standards/` owns cross-workspace authoring standards.

Every generated document carries a header naming its source, adjustment point,
and exact `make gen APPLY=Y` regeneration rule. Generated output is never edited
by hand.

## Command and test examples

All executable examples use declared root Make verbs. Direct generators,
linters, formatters, type checkers, test runners, and ad-hoc scripts are
prohibited. Standard verbs accept no project, file, pattern, action, phase, fix,
or changed-only selectors.

Test examples exercise public facades with `tm`, the unified `conftest.py`, and
typed shared fixtures. They contain no mocks, fakes, stubs, patching,
monkeypatch mutation, private construction, or hardcoded project-owned values.

The documentation auditor recursively enforces this contract over live
`docs/guides/` and `docs/standards/` sources. Historical exclusions come only
from the typed docs scope owner; no local allowlist may bypass the audit.

## Authoring

- Write English, direct, current guidance.
- Explain ownership and observable behavior rather than implementation trivia.
- Link to one canonical topic owner instead of copying it.
- Read configurable facts from their typed owner or omit them.
- Treat stale links, warnings, missing tools, empty output, and generated drift
  as failures.
- Remove superseded docs in the same change as their replacement.

## Docstrings

Public modules, classes, methods, functions, and exported symbols document why
they exist, their boundary, and relevant failure conditions. Type annotations
own type facts; docstrings do not restate them. The typed Ruff configuration owns
the exact enabled and ignored rules.

See [Python docstring standards](docstrings/PEP257-GOOGLE-RUFF.md).

## Generation and validation

Run the complete documentation propagation through the root dispatcher:

```bash
make gen APPLY=Y
make gen APPLY=Y
make fix APPLY=Y
make fmt APPLY=Y
make check APPLY=Y
make test APPLY=Y
make conform APPLY=Y
```

The second generation pass must be a fixed point. Test validation retains the
canonical Testmon cache. A missing docs workflow is repaired at the Make or
flext-infra owner before this sequence is rerun.

## Publication

Publication, release, deployment, and activation use only the verbs declared by
`make help`. A built site or local green run is not deployed evidence; the
integrated runtime must be validated separately.
