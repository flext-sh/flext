# FLEXT Agent Surface Registry

**Reviewed:** 2026-07-15

**Scope:** ownership, activation, and drift control

The machine-readable declaration is [`provider.toml`](provider.toml). This file
explains ownership only; it never duplicates the declared skill list or domain
rules.

## Owners

| Concern | Canonical owner |
| --- | --- |
| Universal conduct | managed universal block in [`AGENTS.md`](../AGENTS.md) |
| FLEXT workspace routing | [`docs/GOVERNANCE.md`](../docs/GOVERNANCE.md) |
| Provider identity and exported paths | [`provider.toml`](provider.toml) |
| Session entry point | [`commands/flext-law.md`](commands/flext-law.md) |
| Task procedure | frontmatter and content of the selected `skills/*/SKILL.md` |
| Structural codemod inventory | provider referenced by `provider.toml` |
| Architecture decisions | [`docs/architecture/adr/README.md`](../docs/architecture/adr/README.md) |

## Activation Contract

- `flext-core`-validated project metadata is the only project-type detector.
- The provider activates only when the normalized dependency set contains the
  marker declared in `provider.marker_distribution`.
- Only `surfaces.always` loads at activation. The context router selects the
  smallest relevant subset of `surfaces.on_demand`.
- Provider consumers expose workspace-local references to these files; they do
  not own copies of FLEXT content.

## Anti-Drift Contract

Every change must either update the owner when reality changes or verify that
the impacted owner is still current. In the same change:

1. Add, rename, or remove a skill path in `provider.toml` with its `SKILL.md`.
2. Update docs and agent pointers when an owner or behavior changes.
3. Remove superseded prose, aliases, copies, and catalog entries.
4. Keep codemod rule IDs only in the referenced codemod provider.

Counts are derived from the provider declaration and filesystem; never maintain
a prose count. Tests and checks validate declarations and behavior, but are
never a source of truth.

## Validation

Validation must prove that every declared path exists, every local `SKILL.md` is
declared exactly once, the always-loaded set contains only the context router,
and referenced provider manifests are valid. Record the command, exit code, and
decisive output in the active workspace-root Bead.
