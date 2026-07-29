---
name: flext-plan-hygiene
description: 'Use before creating, splitting, resuming, or consolidating multi-session FLEXT plans so one execution ledger owns the outcome, dependencies, lanes, evidence, and stop condition.'
license: MIT
metadata:
  version: 2.0.0
---
# FLEXT Plan Hygiene

## Workflow

1. Search the active ledger for the same outcome, public contract, or writable paths.
2. Extend the existing owner when intent matches; create a new unit only for a distinct
   independently acceptable outcome.
3. Split oversized work by dependency-ready deliverables, not arbitrary file counts.
4. Give each step an owner, paths, prerequisites, acceptance evidence, and stop condition.
5. Replace superseded narrative with a pointer and preserve only durable decisions.

## Contracts

- One outcome has one executable plan and one current target contract.
- Plans distinguish discovery, decision, implementation, validation, and landing.
- Parallel lanes are explicit, disjoint for writes, and joined by an integration gate.
- A completed step records objective evidence; a status label alone is insufficient.
- Resumption starts from live code and ledger state, never an old chat summary.
