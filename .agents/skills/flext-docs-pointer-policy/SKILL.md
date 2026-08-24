---
name: flext-docs-pointer-policy
description: >-
  Keep FLEXT docs, skills, agents, and catalogs synchronized through one owner
  per fact and lightweight pointers elsewhere. Use whenever implementation or
  governance changes can make an instruction surface stale.
license: MIT
metadata:
  version: 2.0.0
---

# FLEXT Docs Pointer Policy

## Ownership

| Fact | Owner |
| --- | --- |
| Provider identity and exported paths | `.agents/provider.toml` |
| Skill trigger and procedure | that skill's `SKILL.md` |
| Architecture decision | accepted ADR and its registry |
| Runtime/API behavior | owning source declaration or validated config |
| Workspace routing | `docs/GOVERNANCE.md` |
| Universal conduct | managed universal block in root `AGENTS.md` |

Tests, snapshots, checks, reports, examples, and generated output are evidence
or consumers. They are never the source of truth.

## Workflow

1. Inventory every docs, skill, agent, prompt, and catalog reference affected by
   the change.
2. Identify the single owner for each fact.
3. Change the owner and replace repeated prose with a link in the same cycle.
4. Delete obsolete aliases, copies, counts, and historical machine-state claims.
5. If behavior did not change, verify affected pointers and owners are current.
6. Run link/markdown/catalog validation and record exact evidence in the active
   root-workspace Bead.

## Non-Negotiables

- A pointer names the owner and purpose; it does not paraphrase the rule.
- Do not encode dynamic counts or installed user tooling as project policy.
- Do not keep old and new instruction surfaces for compatibility.
- A stale instruction found in the touched domain is fixed at its owner before
  completion.

## References

- [`docs/GOVERNANCE.md`](../../../docs/GOVERNANCE.md)
- [`provider.toml`](../../provider.toml)
- [`ADR-005`](../../../docs/architecture/adr/005-config-settings-constants-templates-schemas-ssot.md)
