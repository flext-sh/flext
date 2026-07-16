# Canonical Settings & Config Pattern (ADR-005 — standardization)

**Status**: canonical pointer | **Scope**: every FLEXT project (`flext-*`,
integrations, and `ai-hub`)

This page intentionally does not duplicate the declaration recipe. The
authoritative decision is
[ADR-005](adr/005-config-settings-constants-templates-schemas-ssot.md); the
inviolable consumer form and layering rules are in `AGENTS.md` U18. Delivery
order is owned by the
[migration plan](config-ssot-migration-plan.md), while live status and command
evidence reside only in Beads `mro-wkii` and `mro-7akn`.

## Consumer contract

```python notest
from package import config, settings

config.Namespace.domain
settings.Namespace.domain
```

Consumers use those exact validated singleton identities. They do not import a
private settings/config class, call a singleton accessor, re-read environment or
files, or route values through a facade property, proxy, mapping, helper, or
compatibility alias.

## Boundary distinction

Project-owned runtime values come from `config` and `settings`. The
`u.Cli.config_load`, schema, and template operations named by ADR-005 are for
true external ingress/egress and generation boundaries; they are never an
alternate way for a project consumer to retrieve its own runtime parameters.

## Declaration and composition

Follow ADR-005 and `AGENTS.md` U18 directly. Schema models, composition layers,
validation boundaries, and generated package-root exports must have one owner;
this pointer does not maintain a second code template that can drift from them.

## Delivery and evidence

Use the migration order and acceptance gates in the migration plan. Every
project cutover is breaking and atomic: migrate all consumers, delete the old
path, validate the real public runtime, commit with explicit pathspecs, and
fast-forward push. The Bead ledger records commands, exit codes, outputs, SHAs,
blockers, and the next executable step.
