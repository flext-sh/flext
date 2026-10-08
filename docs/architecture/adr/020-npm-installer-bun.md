# ADR-020 — Bun installs the npm-backed mise tools fleet-wide

<!-- TOC START -->

- [Decision](#decision)
- [Consequences](#consequences)
- [References](#references)

<!-- TOC END -->

- **Status:** SUPERSEDED by
  [ADR-025](025-npm-free-fleet-toolchain.md) (2026-10-08): the fleet toolchain
  has no npm backend. Kept as historical evidence of the 2026-10-05 decision.
- **Scope:** every generated `.mise.toml`, `mise.lock`, the bootstrap
  environment, and the user-global Mise registry (ai-hub ADR-0037).
- **Decides:** `npm.package_manager = "bun"` fleet-wide; the embedded aube
  no longer installs npm tools.
- **Complements:** ADR-005 (SSOT), ADR-010 (standardization), ai-hub
  ADR-0037 (user registry).

## Decision

1. The SSOT declares `npm_package_manager: bun` and a `bun` tool entry
   (`aqua:oven-sh/bun`). Per-tool data lives in the declarative
   `toolchain.tools` table (name/selector/version/version_prefix/form);
   the `.mise.toml` `[tools]` section renders generically from it.
2. npm-backed CLIs (`npm:@ast-grep/cli`, `npm:prettier`) install through
   bun. `allow_builds` is the aube form; under bun the inline form renders
   `bun_args = "--trust"` — the declared lifecycle approval for ast-grep's
   native binary selection. prettier needs no lifecycle approval.
3. **Locks:** `mise.lock` keeps the top-level pin only — aube dependency
   graphs and `.mise/locks` sidecars die. Only `make upg` resolves or
   relocks (operator law, unchanged); `setup` installs frozen and WARNs on
   drift without writing.
4. **Bootstrap:** the safe-mode environment (`env -i`, `MISE_SAFE=1`)
   ignores project `[settings]`, so the generated bootstrap carries
   `MISE_NPM_PACKAGE_MANAGER` explicitly from the SSOT.
5. **The mypy/pydantic companion law** (same operator order, bead
   gc-eqvqx5): `pydantic.mypy` plugin mandatory in every projection;
   `prop-decorator`/`call-arg`/`attr-defined` suspended at the tooling
   SSOT — code changed to dodge them is regression and reverts.

## Consequences

- Faster, dependency-sidecar-free npm tool installs; transitive npm
  dependencies are no longer graph-pinned (accepted operator tradeoff).
- CI matrix (linux-x64/musl/arm64, macos x64/arm64, windows-x64) plus the
  docker bootstrap fixture are the required green surfaces for the wave.
- Verified live on the root: ast-grep 0.45.3 and prettier 3.5.3 execute
  through bun; `[[tools.bun]] backend = "core:bun"` in the lock.

## References

- Epic `flext-qwvb5` (T2 #1570, T6 #1594, root wave #400)
- ai-hub ADR-0037 (user registry ownership + PATH inversion)
