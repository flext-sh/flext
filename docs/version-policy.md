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

- The workspace and packages release independently on the configured maintenance line.
  The workspace consumer declares that line in `config/infra.yaml`; the generic release
  engine leaves it unrestricted. Attached Git members inherit the workspace declaration.
  Each repository owns its version, patch progression, immutable tag and GitHub Release.
  A standalone checkout reads its own consumer declaration; the generic engine does not
  infer the maintenance line from a package name or an installed dependency.
- Releases are cut through the canonical lane only: `make release-plan`,
  `make release-version`, `make release-tag`, and `make release-build` — never by
  hand-editing versions in individual packages.
- Patch numbers need not agree. Internal dependencies reference each dependency's own
  declared version, not the releasing repository's patch number. Package-index
  publication remains disabled by the existing release policy.
- The current operator-selected policy finalizes the existing stable `0.12.x` line:
  `Infra.release.finalize_maintenance: true` together with `maintenance_line: [0, 12]`
  in the workspace consumer configuration requests independent patch releases.
  This is an explicit maintenance release decision, not automatic commit classification
  or a fallback. Historical `feat`, `perf`, `chore`, breaking markers and legacy merge
  subjects remain unchanged and are treated as opaque history for that decision.
- The generic engine defaults to automatic classification with finalization disabled.
  It uses the selected consumer's `bump_types`; breaking markers retain major-bump
  semantics in that mode. Explicit finalization without a declared line is invalid.
  Every candidate must remain on its declared line, and newer versions are never
  downgraded. First stable releases, RC finalization and already-merged release commits
  awaiting a tag retain their declared version instead of receiving a duplicate bump.
  Existing tags are never overwritten.
- Applying the version phase requires an explicitly supplied
  `GitLaneOwnershipReceipt` through the public release request's `ownership` input.
  The receipt must identify the same checkout and prove its prior state was published
  and integrated. The release caller forwards that evidence unchanged; it never
  invents ownership or creates a preservation checkpoint automatically.

## Compatibility contract

- **Public surface**: the facade aliases (`c`, `m`, `t`, `p`, `u`, `r`, `e`, `x`, `h`,
  `d`, `s`) and the symbols re-exported from each package root are the compatibility
  contract. Explicit maintenance finalization is not a compatibility claim: real public
  API, behavior and applicable compatibility gates must pass without losing existing
  functionality. Configuration or a successful release plan alone does not complete
  the workspace's release readiness.
- **Private modules** (`_*/*`) and generated surfaces are not covered by any
  compatibility guarantee and may change at any commit.
- **No parallel old+new surfaces**: a replaced API is removed in the same cycle, not
  deprecated-and-kept; consumers are migrated in the same change.

## Development status

The `0.12.0-dev` cycle is non-production. Quality status per cycle is stated in the
release notes; production adoption tracks packaged releases only.
