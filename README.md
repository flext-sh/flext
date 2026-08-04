# FLEXT

FLEXT is a multi-package Python workspace for data integration, platform tooling, and operational connectors.

**Mission:** The FLEXT goal, success metrics, and inviolable governance chain are codified in
[`AGENTS.md` (Make / Authority sections)](AGENTS.md) — the always-loaded engineering law that governs every agent action in every
session.

The root documentation in this repository governs only the FLEXT platform and the `flext-*` packages. If this
repository also contains non-FLEXT directories, they are documented locally in their own trees and are out of scope for
the root portal.

## Workspace Status

- Current workspace code version: `0.12.0-dev`
- Forward architecture baseline: `0.13.0`
- Latest tagged release documented at root: `v0.11.0`

## Governed Scope

- Platform core: `flext-core`, `flext-infra`, `flext-tests`, `flext-quality`
- Platform capabilities: `flext-cli`, `flext-api`, `flext-auth`, `flext-web`, `flext-grpc`, `flext-observability`,
  `flext-plugin`, `flext-meltano`
- Domain packages: `flext-ldap`, `flext-ldif`, `flext-db-oracle`, `flext-oracle-wms`, `flext-oracle-oic`
- Integration packages: all `flext-tap-*`, `flext-target-*`, and `flext-dbt-*`

## Documentation

- Root portal: `docs/index.md`
- Architecture baseline: `docs/architecture/baseline-v0.13.0.md`
- Migration guide: `docs/guides/migration-to-v0.13.0.md`
- Root governance: `AGENTS.md`

## Docs Automation

Documentation automation is implemented in `flext-infra` and is pyproject-first:

- package metadata comes from `pyproject.toml`
- project-specific docs metadata can live under `[tool.flext.docs]`
- `docs/docs_settings.json` is intentionally minimal and only covers policy that cannot be deduced from project metadata
- generated API docs use public exports and real docstrings as the SSOT

## Repository Direction

The root portal is being aligned to:

- publish only factual FLEXT workspace guidance
- generate API reference from code and docstrings
- keep architecture and migration prose curated
- stop documenting non-FLEXT projects at the root level

Repository source and governance: <https://github.com/flext-sh/flext>
