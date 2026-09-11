# Release 0.12.0-dev

## Status

- Quality: Development (branch 0.12.0-dev)
- Usage: Non-production

## Scope

- Workspace development cycle: 0.12.0-dev
- Previous packaged release: v0.11.0 (see docs/releases/v0.11.0.md)
- Target publication: workspace `flext` and 31 members, 32 distributions at 0.12.0.
- Candidate size: 32 wheels and 32 sdists, 64 artifacts when both formats apply.

## Checkpoint acceptance

The 0.12.0 checkpoint is a target, not a claim of validated or published artifacts.
Execution and evidence belong to Bead `flext-1wjg1` and its dependencies.

Every required cycle must finish with its command, working directory, exit status,
and diagnostics preserved. Crashes, incomplete execution, dependency or installation
failures, broken public runtime, missing resources, unstable generation, mismatched
source/artifact identities, distribution security defects, and publication or
authentication failures block acceptance. Unknown findings also block acceptance.

Nonfunctional quality debt may remain only after individual assessment records the
finding, producing command and exit, package, impact, canonical owner, and open
remediation Bead. Accepted debt stays open; a red gate never becomes green by
acceptance. Required-check policy changes need separate operator approval.

The native release/version owner determines versions. Per-repository OIDC trusted
publishing follows the flext-core pattern. Accepted integrated SHAs, tags, artifact
hashes, and configuration identity must agree. Validate every exact candidate in a
clean consumer, then verify the published artifacts from PyPI. Never overwrite an
existing PyPI file or move a published tag; incompatible existing versions require
an operator decision.

Integrate preserved work through reviewed merge commits and fast-forward pushes.
Workspace gitlinks must reference integrated, remotely reachable member commits.
Retire a lane only after proving all unique commits are integrated, PRs reconciled,
and staged, unstaged, and untracked work absent, including nested submodules.

## Highlights in this cycle

- Docs renaissance: unified docs automation in flext-infra, strict build/validate/audit gates
- External documentation site (GitHub Pages, docs.flext.sh) with CNAME and deploy workflow
- Docstring uplift across the workspace (D401/D417 enforced, ignores removed)
- Generated API reference enriched with doc summaries and trove classifiers
- Code communities published from the knowledge graph (docs/architecture/communities/)

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
