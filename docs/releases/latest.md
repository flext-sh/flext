# Release 0.12.0-dev

<!-- TOC START -->

- [Status](#status)
- [Scope](#scope)
- [Current 0.12 surface](#current-012-surface)
- [Checkpoint acceptance](#checkpoint-acceptance)
- [Documentation claims and required evidence](#documentation-claims-and-required-evidence)
- [Parked forward changes](#parked-forward-changes)
- [Projects impacted](#projects-impacted)

<!-- TOC END -->

## Status

- Quality: Development (release line `0.12.0-dev`)
- Usage: Non-production

This page describes the 0.12 checkpoint, not the name of every working branch. The
2026-10-20 documentation reconciliation is on `upload-20261007`; it supplies no fresh
CI, installed-runtime, artifact, or publication receipt. Publication and fleet stability
remain unproved here.

## Scope

- Workspace development cycle: 0.12.0-dev
- Previous recorded release: [v0.11.0](v0.11.0.md) (historical record, not a fresh
  registry verification).
- Target publication: workspace `flext` and 31 members, 32 distributions at 0.12.0.
- Candidate size: 32 wheels and 32 sdists, 64 artifacts when both formats apply.

## Current 0.12 surface

The release validates the existing public contract, rather than requiring a forward
namespace migration to finish first:

- Canonical root facade imports and generated lazy exports remain the 0.12 consumption
  route. Existing operational aliases (`r`, `e`, `x`, `h`, `d`, `s`) and public
  `Flext*` exports are not removed by the forward planning documents.
- The current API owner, `flext-core/src/flext_core/api.py`, defines the cooperative
  registry/dispatcher facade and `core = FlextCore.fetch_global()`. That object is not
  the proposed typed lazy `core` module namespace.
- Existing Result, service, handler, registry, configuration/settings and utility
  behavior needs public-consumer validation on the exact release candidate. Source
  presence and architectural intent do not prove that installed behavior works.

These are scope boundaries, not permission to retain a broken runtime. Repair failures
of the existing contract at their canonical owners; do not make a future public API
redesign a prerequisite for the 0.12 release.

## Checkpoint acceptance

The 0.12.0 checkpoint is a target, not a claim of validated or published artifacts.
Execution and evidence belong to Bead `flext-1wjg1` and its dependencies.

The last tracker evidence supplied for this reconciliation identifies `flext-ik359`
as the open **0.13** gate epic; its old 0.20 name is retired. It waits for the 0.12
publication work in `flext-1wjg1` and separate authorization for forward implementation.
This records the reported ordering, not a fresh tracker query or a completed dependency.
Documentation retargeting does not authorize implementation, publish artifacts, or
close either Bead. The authorized coordinator owns live tracker updates.

Every required cycle must finish with its command, working directory, exit status, and
diagnostics preserved. Crashes, incomplete execution, dependency or installation
failures, broken public runtime, missing resources, unstable generation, mismatched
source/artifact identities, distribution security defects, and publication or
authentication failures block acceptance. Unknown findings also block acceptance.

Nonfunctional quality debt may remain only after individual assessment records the
finding, producing command and exit, package, impact, canonical owner, and open
remediation Bead. Accepted debt stays open; a red gate never becomes green by
acceptance. Required-check policy changes need separate operator approval.

The native release/version owner determines versions. Per-repository OIDC trusted
publishing follows the flext-core pattern. Accepted integrated SHAs, tags, artifact
hashes, and configuration identity must agree. Validate every exact candidate in a clean
consumer, then verify the published artifacts from PyPI. Never overwrite an existing
PyPI file or move a published tag; incompatible existing versions require an operator
decision.

Integrate preserved work through reviewed merge commits and fast-forward pushes.
Workspace gitlinks must reference integrated, remotely reachable member commits. Retire
a lane only after proving all unique commits are integrated, PRs reconciled, and staged,
unstaged, and untracked work absent, including nested submodules.

## Documentation claims and required evidence

The following previously listed highlights are subjects for validation, not a blanket
delivered-feature list. Record evidence against the exact integrated candidate before
promoting any row to a release claim:

| Claim to validate | Required evidence |
| ----------------- | ----------------- |
| Unified documentation automation owned by `flext-infra` | Canonical docs lifecycle receipts showing generation, build, validation and audit, with the actual repository scope and remaining diagnostics. |
| GitHub Pages / `docs.flext.sh` publication | Successful deployment tied to the candidate SHA and an independent check of the served site, CNAME/domain routing and public links. A workflow file alone is insufficient. |
| Workspace docstring uplift, including D401/D417 | Canonical lint and executable-snippet receipts for every claimed project, including examples, scripts and tests; no fleet-wide inference from a sample. |
| Generated API reference summaries and classifiers | Owner-generated output from the candidate, verified documentation rendering and consistency with the packaged public surface and metadata. |
| Published code-community documentation | Graph provenance tied to the candidate and verified generated pages, navigation and deployed links; graph or page existence alone is not publication. |

Every receipt records the command, working directory, exit status, decisive output,
candidate identity and covered packages. Link/build checks and real installed-consumer
checks remain distinct evidence. Validation is coordinator-owned; this documentation
edit runs no gates and supplies none of these receipts.

## Parked forward changes

These changes are **not 0.12 blockers** merely because they are described or accepted
as future work. They do not excuse failures in the current release contract.

| Forward work | Disposition outside the 0.12 checkpoint |
| ------------ | -------------------------------------- |
| Remove root operational aliases or long-name exports; redesign `core` as a typed lazy module namespace | Proposed 0.13 public-contract migration. Requires approved contracts, consumer migration evidence and separate implementation authorization; not an existing 0.12 API. |
| Reorganize service/DI, registry/dispatcher and settings/config access for the new namespace | Forward 0.13 design. Preserve current caller-scoped runtime and injected dependencies until an authorized, validated cutover. No compatibility layer is introduced by these notes. |
| Static-consumer documentation mode and generic Office-byte completion | Accepted future work derived from ADR-009's historical 0.20 planning, now targeted to the unified 0.13 plan. Acceptance does not prove completion; existing tooling/adapters are not evidence of the full proposed capability. |
| New `flext-docs`, `flext-gworkspace`, backup library or neutral artifact-envelope extraction | Preserve ADR-009's rejected, conditional or deferred verdicts. Retargeting does not approve a package or bypass the two-consumer, deletion-positive extraction gate. |

See [ADR-009](../architecture/adr/009-ecosystem-coordination-and-library-evaluation.md)
and the [ADR index](../architecture/adr/README.md) for decision maturity and historical
provenance. Forward documentation is not a 0.12 release receipt or a separate 0.20
delivery promise.

## Projects impacted

- flext
- flext-api
- flext-auth
- flext-cli
- flext-core
- flext-db-oracle
- flext-dbt-ldap
- flext-dbt-ldif
- flext-dbt-oracle
- flext-dbt-oracle-wms
- flext-grpc
- flext-infra
- flext-ldap
- flext-ldif
- flext-meltano
- flext-observability
- flext-oracle-oic
- flext-oracle-wms
- flext-plugin
- flext-quality
- flext-tap-ldap
- flext-tap-ldif
- flext-tap-oracle
- flext-tap-oracle-oic
- flext-tap-oracle-wms
- flext-target-ldap
- flext-target-ldif
- flext-target-oracle
- flext-target-oracle-oic
- flext-target-oracle-wms
- flext-tests
- flext-web
