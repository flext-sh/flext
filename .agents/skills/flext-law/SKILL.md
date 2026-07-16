---
name: flext-law
description: Apply the mandatory FLEXT engineering law before changing a flext-core workspace. Use for every FLEXT implementation, refactor, review, migration, or instruction-surface change; route detailed procedure to the smallest matching skill.
---
# FLEXT Law

## Mandatory baseline

Always apply FLEXT patterns, Python 3.13, object-oriented MRO composition,
SSOT, YAGNI, DRY, SOLID, Clean Architecture, and Dependency Injection. Use
these principles to reduce code and preserve complete, correct module behavior;
never use them to justify a speculative abstraction or a parallel path.

The source of truth is the objective, its owning domain declaration, validated
configuration, or fundamental rule. Tests, fixtures, snapshots, examples,
reports, and generated projections only validate or consume those owners; they
never define behavior, catalogs, configuration, or project type.

## Execution

1. Read root `AGENTS.md` and `docs/GOVERNANCE.md`.
2. Resolve the workspace-root Bead and record ownership before writes.
3. Identify the canonical declaration/configuration and every affected
   consumer before changing behavior.
4. Load `flext-context-routing`, then at most three specialized skills whose
   frontmatter matches the task.
5. Change the owner once, update all consumers atomically, and remove the
   superseded path. Do not add a fallback, shim, alias, suppression, or
   old-plus-new coexistence.
6. Update affected docs, skills, agent instructions, and pointers when reality
   changes; otherwise verify they remain current.
7. Validate through the public facade and native production gates, then record
   command, exit code, and decisive output in the Bead.

## Architecture boundary

Use canonical public facades and protocols. Keep declarations in their owning
facets, validated settings/configuration in their exported namespaced models,
and behavior in focused MRO-composed utilities/services. Dependencies point
inward; construction and external translation stay at boundaries.

The skill catalog is the set of direct `.agents/skills/<name>/SKILL.md` files
whose `name` equals the directory. Structural ast-grep declarations live only
under `flext-codemod-astgrep/rules`; its tests and snapshots are validators.
