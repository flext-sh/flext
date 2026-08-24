---
name: flext-agent-integration
description: Integrate the FLEXT provider with an agent manager or audit its projection lifecycle. Use for provider discovery, workspace-local skill exposure, and stale projection removal. Do not use for FLEXT domain implementation or generic agent configuration.
license: MIT
metadata:
  version: 2.0.0
---

# FLEXT Agent Integration

Use this skill at the provider boundary. Domain behavior remains in the
on-demand skill that owns it.

## Workflow

1. Read `.agents/provider.toml` as the provider declaration.
2. Detect eligibility only from `flext-core`-validated project metadata and the
   declared `marker_distribution`.
3. Expose the router and listed skills as workspace-local references to this
   repository; do not copy their content into the manager.
4. Load only `surfaces.always` at activation. Let `flext-context-routing`
   select entries from `surfaces.on_demand`.
5. Delegate structural rewrite configuration to the codemod provider referenced
   by `.agents/provider.toml`; never duplicate its rule IDs.
6. On deactivation or catalog change, remove only references previously managed
   by this provider and verify no stale projection remains.

## Critical rules

- The provider declaration owns availability; skill frontmatter owns routing
  intent; the referenced file owns implementation guidance.
- No machine-specific tool inventory, global FLEXT copy, compatibility alias,
  or second catalog is allowed.
- Tests and checks are validators, never SSOT.
- Missing, duplicate, escaping, or unlisted paths block projection.

## Example

**Input:** an agent manager enters a project whose validated dependencies include
`flext-core`.

**Output:** expose this provider locally, load `flext-context-routing`, and defer
all other skills until task intent selects them.

## Troubleshooting

- Marker mismatch: keep the provider inactive and report the validated metadata.
- Projection collision: stop and report both owners; never overwrite an
  unmanaged surface.
- Catalog drift: repair the declaration or owner before exposing the provider.
