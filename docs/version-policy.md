# Version Policy

**How FLEXT versions its workspace and packages.**

## Workspace cycle

The workspace develops on a named development branch per cycle
(currently `0.12.0-dev`). Member package `pyproject.toml` files carry the
development-cycle version (`version = "0.12.0-dev"`), while the root workspace
manifest and `config/workspace.yaml` carry the release-candidate coordination
version (`0.12.0rc0`). This distinction keeps package development metadata
stable while the workspace release lane prepares a candidate.
Release notes per cycle live under
`docs/releases/` (repo-only reference, e.g. `docs/releases/latest.md`).

## Package releases

- Packages are independently versioned but released together at the end of a
  cycle; the packaged release tag follows the cycle name (previous packaged
  release: `v0.11.0`).
- Releases are cut through the canonical lane only: `make release` (status/gates). Do not use retired `make ship`, and never hand-edit versions in individual packages.
- Version bumps are driven from the root so all `flext-*` packages move as
  one consistent set; internal dependencies between packages always reference
  the same cycle version.

## Compatibility contract

- **Public surface**: the facade aliases (`c`, `m`, `t`, `p`, `u`, `r`, `e`,
  `x`, `h`, `d`, `s`) and the symbols re-exported from each package root are
  the compatibility contract. Breaking changes to them require a cycle
  boundary and a release note entry.
- **Private modules** (`_*/*`) and generated surfaces are not covered by any
  compatibility guarantee and may change at any commit.
- **No parallel old+new surfaces**: a replaced API is removed in the same
  cycle, not deprecated-and-kept; consumers are migrated in the same change.

## Development status

The `0.12.0-dev` cycle is non-production. Quality status per cycle is stated
in the release notes; production adoption tracks packaged releases only.

## Dependency security floors

Root `pyproject.toml` `[tool.uv] constraint-dependencies` pins fleet-wide floors
for transitive advisories (currently `transformers>=5.5.0` and
`cryptography>=50.0.0`). Change the floor in the SSOT, regenerate/lock through
`make deps`, and keep day-to-day landing on `0.12.0-dev`. Dependabot merge
helpers that target `main` are operator-gated and are not the default land/finish path on 0.12.0-dev.

## Integration branch

The active development line is `0.12.0-dev`. Promote to `main` only when the
operator explicitly requests a release promote — not as part of ordinary
bugfix/docs closeout.
