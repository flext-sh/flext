# FLEXT

FLEXT is a multi-package Python workspace for data integration, platform tooling, and
operational connectors.

**Mission:** The FLEXT goal, success metrics, and inviolable governance chain are
codified in
[`AGENTS.md` § Universal Agent Engineering Core](AGENTS.md#universal-agent-engineering-core)
— the always-loaded engineering law that governs every agent action in every session.

The root documentation in this repository governs only the FLEXT platform and the
`flext-*` packages. If this repository also contains non-FLEXT directories, they are
documented locally in their own trees and are out of scope for the root portal.

## Workspace Status

- Integration branch: `0.12.0-dev`; package version: `0.12.0`
- Forward architecture baseline: `0.13.0`
- Latest tagged release documented at root: `v0.11.0`

## Governed Scope

- Platform core: `flext-core`, `flext-infra`, `flext-tests`, `flext-quality`
- Platform capabilities: `flext-cli`, `flext-api`, `flext-auth`, `flext-web`,
  `flext-grpc`, `flext-observability`, `flext-plugin`, `flext-meltano`
- Domain packages: `flext-ldap`, `flext-ldif`, `flext-db-oracle`, `flext-oracle-wms`,
  `flext-oracle-oic`
- Integration packages: all `flext-tap-*`, `flext-target-*`, and `flext-dbt-*`

## Documentation

- Root portal: `docs/index.md`
- Architecture baseline: `docs/architecture/baseline-v0.13.0.md`
- Migration guide: `docs/guides/migration-to-v0.13.0.md`
- Root governance: `AGENTS.md`

## Development operations

Run `make help` before provisioning to inspect the typed command catalog. The
[Make guide](docs/guides/make-commands.md) owns the common operation contract and
workspace, member and independent-checkout examples. Product commands remain with
their declaring projects.

Invoke each required operation explicitly: setup installs locked inputs, upgrades
resolve new locks, and generation and structural modification each publish the
projections required by their own change. Checks are read-only. `make tests` executes
the complete applicable suite once with the persistent Testmon database, after the real
public consumer has proved the implemented behavior. A help result or source edit does
not establish generation, runtime or fleet acceptance.

## Docs Automation

Documentation automation is implemented in `flext-infra` and is pyproject-first:

- package metadata comes from `pyproject.toml`
- project-specific docs metadata can live under `[tool.flext.docs]`
- generated documentation configuration derives from the same typed policy and project
  metadata
- generated API docs use public exports and real docstrings as the SSOT

The existing documentation engine is used by generation, repair, formatting, checking
and local builds in their respective Make operations. Publication, deployment and tags
remain explicitly triggered product operations.

## Repository Direction

The root portal is being aligned to:

- publish only factual FLEXT workspace guidance
- generate API reference from code and docstrings
- keep architecture and migration prose curated
- stop documenting non-FLEXT projects at the root level

Repository source and governance: <https://github.com/flext-sh/flext>
