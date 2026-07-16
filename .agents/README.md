# FLEXT Agent Provider

This directory is the Git-tracked FLEXT provider consumed by agent managers.
It owns project-specific agent surfaces, not universal agent behavior.

## Canonical Owners

- [`provider.toml`](provider.toml) — provider identity, activation marker,
  router, exported skill paths, and codemod provider path.
- [`commands/flext-law.md`](commands/flext-law.md) — compact session router.
- [`skills/*/SKILL.md`](skills/) — on-demand procedures and trigger metadata.
- [`INSTRUCTION_SURFACE.md`](INSTRUCTION_SURFACE.md) — human-readable ownership
  and drift contract.
- [`docs/GOVERNANCE.md`](../docs/GOVERNANCE.md) — workspace concern routing.

The structural codemod provider referenced by `provider.toml` owns codemod rule
IDs and artifacts. Static enforcement policy remains with its validated domain
declarations; neither surface duplicates the other.

When reality changes, update its owner and every affected docs, skill, agent,
catalog, and consumer pointer in the same change. If behavior did not change,
verify those surfaces are current. Tests and checks validate the owners; they
never define provider identity, domain behavior, config, or fundamental rules.
