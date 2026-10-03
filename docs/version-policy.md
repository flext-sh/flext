# Version Policy

<!-- TOC START -->

- [Workspace cycle](#workspace-cycle)
- [Package releases](#package-releases)
- [Compatibility contract](#compatibility-contract)
- [Development status](#development-status)

<!-- TOC END -->

**How FLEXT versions its workspace and packages.**

## Workspace cycle

The workspace develops on a named development branch per cycle (currently `0.12.0-dev`).
Package versions are generated from the release and project-profile owners: runtime
libraries may carry the stable cycle version, while the workspace and release-candidate
connector profiles may carry the release-candidate version. Read the generated
`pyproject.toml` for a package's current projection; never hand-edit or generalize one
profile's value across the fleet. Release notes per cycle live under `docs/releases/`
(repo-only reference, e.g. `docs/releases/latest.md`).

## Package releases

- Packages are independently versioned but released together at the end of a cycle; the
  packaged release tag follows the cycle name (previous packaged release: `v0.11.0`).
- Releases are cut through the canonical lane only: `make release-plan`,
  `make release-version`, `make release-tag`, and `make release-build` — never by
  hand-editing versions in individual packages.
- Version bumps are driven from the root so all `flext-*` packages move as one
  consistent set; internal dependencies between packages always reference the same cycle
  version.

## Compatibility contract

- **Public surface**: the facade aliases (`c`, `m`, `t`, `p`, `u`, `r`, `e`, `x`, `h`,
  `d`, `s`) and the symbols re-exported from each package root are the compatibility
  contract. Breaking changes to them require a cycle boundary and a release note entry.
- **Private modules** (`_*/*`) and generated surfaces are not covered by any
  compatibility guarantee and may change at any commit.
- **No parallel old+new surfaces**: a replaced API is removed in the same cycle, not
  deprecated-and-kept; consumers are migrated in the same change.

## Development status

The `0.12.0-dev` cycle is non-production. Quality status per cycle is stated in the
release notes; production adoption tracks packaged releases only.
