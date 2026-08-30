# ai-hub as a FLEXT Provider Consumer

<!-- TOC START -->
- [Ownership](#ownership)
- [Boundary Contract](#boundary-contract)
- [Drift Discipline](#drift-discipline)
<!-- TOC END -->

This document records the integration boundary only. It is not a second FLEXT
law or an ai-hub architecture specification.

## Ownership

| Fact | Canonical owner |
| --- | --- |
| FLEXT provider identity, marker, and exported paths | active `~/.agents` provider authority |
| FLEXT activation and skill selection | `~/.agents/skills/flext-context-routing/SKILL.md` |
| Provider projection lifecycle | [Governance router](GOVERNANCE.md) |
| FLEXT runtime/API behavior | owning `flext-core` declaration |
| ai-hub architecture and local policy | ai-hub source, validated config, root `AGENTS.md`, and `docs/GOVERNANCE.md` |

## Boundary Contract

- ai-hub consumes project metadata validated by `flext-core` and activates the
  provider only when the normalized dependencies contain the marker declared
by its active provider authority.
- ai-hub exposes workspace-local references to provider-owned surfaces. It does
  not copy or redefine FLEXT commands, skills, rules, docs, or codemod data.
- FLEXT changes update their owner in this repository and verify the ai-hub
  consumer boundary. ai-hub changes update their owner in the independent
  ai-hub workspace and verify provider projection.
- Each independent workspace records work in its own root Beads database.
  Member projects use their workspace-root tracker and never initialize a
  nested database.

## Drift Discipline

When either side changes, inventory affected declarations, config, docs,
skills, agents, and consumers. Update the owner and replace repeated content
affected pointers and provider inventory are still current.
with a pointer in the same change. If behavior did not change, verify the
affected pointers and provider inventory are still current.
affected pointers and provider inventory are still current.

Tests, snapshots, checks, examples, and generated projections validate the
owners. They never become the source of provider identity, domain behavior,
configuration, or fundamental rules.
