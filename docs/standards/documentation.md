# Documentation Standards

<!-- TOC START -->

- [Writable owners](#writable-owners)
- [Command and test examples](#command-and-test-examples)
- [Authoring](#authoring)
- [Docstrings](#docstrings)
- [Generation and validation](#generation-and-validation)
- [Publication](#publication)

<!-- TOC END -->

FLEXT documentation has one engine: the public docs services and utilities in
`flext-infra`. Projects do not own parallel scripts, generators, API registries, or
local command grammars.

## Writable owners

Use the [governance router](../GOVERNANCE.md) for authority and the
[engineering conformance review](../GOVERNANCE.md#engineering-conformance-review)
for domain, namespace, SSOT/YAGNI/DRY/SOLID, Pydantic, DI, and Clean Architecture.
Link this shared route from maintained navigation; do not reproduce law on each page.
Member entrypoints and generated guides inherit it from their canonical generator
and root guide sources. Vendor, archive, cache, and historical material remain
outside maintained engineering guidance; generated pages are projections, not owners.

- Package metadata, typed config, public exports, and docstrings own technical facts.
- Root files under `docs/guides/` own generated member guides.
- Templates and typed generator configuration own generated navigation, API reference,
  reports, and site configuration.
- `docs/standards/` owns cross-workspace authoring standards.

Every generated document carries a header naming its source, adjustment point, and exact
`make gen` regeneration rule. Generated output is never edited by hand.

## Command and test examples

All executable examples use declared root Make verbs. Direct generators, linters,
formatters, type checkers, test runners, and ad-hoc scripts are prohibited. `make help`
owns the common command grammar; use only declared repository-specific extensions. Do
not attach undeclared project, file, pattern, action, phase, fix, or changed-only
selectors. The common `tests` verb runs the complete applicable suite once with the
persistent Testmon database; it has no file selector or incremental prepass.

Documentation hooks reuse the public Infra CLI and the interpreter provisioned by
Make. They never resolve dependencies or create a second environment during collection.

Test examples exercise public facades with `tm`, the unified `conftest.py`, and typed
shared fixtures. They contain no mocks, fakes, stubs, patching, monkeypatch mutation,
private construction, or hardcoded project-owned values.

Markdown and docstring examples obey the same FLEXT import, typing, formatting, and
behavior rules as source code. The documentation auditor recursively enforces this
contract over live `docs/guides/` and `docs/standards/` sources. Historical exclusions
come only from the typed docs scope owner; no local allowlist may bypass the audit.

## Authoring

- Write English, direct, current guidance.
- Explain ownership and observable behavior rather than implementation trivia.
- Link to one canonical topic owner instead of copying it.
- Read configurable facts from their typed owner or omit them.
- Treat stale links, warnings, missing tools, empty output, and generated drift as
  failures.
- Remove superseded docs in the same change as their replacement.

## Docstrings

Public modules, classes, methods, functions, and exported symbols document why they
exist, their boundary, and relevant failure conditions. Type annotations own type facts;
docstrings do not restate them. The typed Ruff configuration owns the exact enabled and
ignored rules.

See [Python docstring standards](docstrings/PEP257-GOOGLE-RUFF.md).

## Generation and validation

There is no common `docs` verb. For authored documentation, use the canonical root
lifecycle and its documentation checks:

```bash
make fix
make fmt
make check
make tests
```

Run `make gen` before these gates only when an owned generator source or generated
projection changed. Use `make build` when a built documentation artifact is in scope.
`make tests` runs only after the same scope's `make check` is green. To check a member
while remaining at the workspace root, select that member's Makefile:

```bash
make -f flext-core/Makefile check
```

The documentation audit does not substitute for executable-example behavior. The full
`tests` verb exercises applicable documentation examples with the same public contract
as project source. A member receipt proves only that member, not whole-workspace
acceptance.

When source, generation policy or shared projections also change, run the
applicable full engineering lifecycle through the same dispatcher:

```bash
make gen
make fmt
make fix
make mod
make check
make tests
make build
```

Each operation runs explicitly through its declared owner. Prove the applicable
generation fixed point using the existing owner; do not add repeated generation passes
or a replacement docs verb. A missing or broken canonical operation is repaired at its
owner before the same command is rerun. Test validation retains the canonical Testmon
cache.

## Publication

Publication, release, deployment, and activation use only the verbs declared by
`make help`. A built site or local green run is not deployed evidence; the integrated
runtime must be validated separately.
