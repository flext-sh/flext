# Foundation

**The `flext-core` foundation layer: what every FLEXT package builds on.**

`flext-core` is the runtime-minimal root of the dependency chain
(`flext-core → flext-cli → flext-infra`, with `flext-tests` beside it). It
owns only what must exist at runtime for every consumer package.

## What it provides

- **Result railway** — `r[T]` (`FlextResult`), the single fallible-path
  contract; typed failures with context instead of exception-driven control
  flow.
- **Runtime base** — settings/config base classes, the DI container, and the
  structured logging facade used by all packages.
- **Operational facades** — the canonical operational aliases composed for
  consumers: `r` (result), `e` (exceptions), `x` (mixins), `h` (handlers),
  `d` (decorators), `s` (service base).
- **Runtime enforcement** — beartype-style runtime rules only; all static
  enforcement lives in `flext-infra` as data.

## Boundary rules

- `flext-core` is stdlib-only at runtime: no Jinja2, no CLI or infra imports.
- Consumer packages import `flext-core` freely; `flext-core` never imports a
  consumer.
- The detailed, always-current API surface is generated from the code — see
  the [workspace API overview](generated/overview.md) and each project's own
  `docs/api-reference/generated/`. If the generated reference is wrong, the
  fix is in the code, exports, or docstrings — never in parallel prose here.
