---
name: flext-context-routing
description: Route an activated FLEXT workspace to the smallest relevant local skill set. Use after validated project metadata reports the flext-core dependency, or when auditing provider activation and context cost. Do not use in projects without that marker.
license: MIT
metadata:
  version: 2.0.0
---
# FLEXT Context Routing

This is the sole always-loaded FLEXT skill. It selects on-demand skills without
restating their instructions.

## Workflow

1. Consume project metadata validated by `flext-core`; never parse
   `pyproject.toml` again or apply a filename heuristic.
2. Require the normalized dependency marker `flext-core`. If absent, load no
   FLEXT surface.
3. Read `.agents/provider.toml` and root `docs/GOVERNANCE.md`.
4. Match task intent and touched paths against skill frontmatter, then load at
   most three entries from `surfaces.on_demand`.
5. Resolve the Beads ledger at the workspace root. Member projects share that
   ledger; only independent projects own a separate database.
6. Include docs, skills, and agent instructions in impact analysis. Update an
   owner when reality changes, or verify it remains current.

## Critical rules

- Provider metadata declares what is available; skills own how to perform their
  bounded task.
- Global copies, alias skills, and eager loading of all FLEXT skills are
  forbidden.
- Tests and checks validate declarations; they never define the catalog or
  project type.
- An unlisted or missing skill path is catalog drift and blocks projection.

## Example

**Input:** change result composition in a project that depends on `flext-core`.

**Output:** load `coding-standards` and `using-flext-core`; do not load unrelated
library, infrastructure, or documentation skills.

## Troubleshooting

- Marker absent: do not guess from package names; keep FLEXT surfaces unloaded.
- More than three skills appear necessary: narrow the task or load another only
  after proving a distinct responsibility.
- Catalog mismatch: fix `.agents/provider.toml` and the owning skill in the same
  change.
