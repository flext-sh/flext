---
name: flext-strict-refactoring
description: 'Strict cleanup guidance for removing duplicated policy, stale guidance, and weak refactor prompts across FLEXT governance surfaces. Use when editing AGENTS.md, pointer docs, or meta-skills so startup law stays short, hard, and aligned with canonical execution rules.'
license: MIT
metadata:
  version: 1.0.0
---
# Flext Strict Refactoring

## Workflow

1. Run `qlty smells --all --sarif --include-tests > /tmp/qlty_smells-tests.json`.
2. Read the root working agreement and isolate the exact recurring failure.
3. Patch `AGENTS.md` first only if the law changes.

## Enforced contracts

- Identify the canonical policy or implementation owner before removing duplication.
- Replace repeated prose with a link to the owner; replace repeated code with the existing facade or service.
- Prove the removed route has no live consumers and that generated projections are current.
