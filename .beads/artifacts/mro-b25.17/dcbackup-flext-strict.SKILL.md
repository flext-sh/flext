---
name: dcbackup-flext-strict
description: >-
  Preserved project-specific skill text removed from the global `.ai-hub`
  catalog. Migration is blocked until a git-backed DcBackup project root with
  project-local skill storage is available.
license: MIT
metadata:
  version: 0.2.0
---

# DcBackup FLEXT Strict Addendum

Use `flext-patterns` as the canonical protocol. This skill only adds dcbackup
project boundaries.

## Required Sequence

1. Load and obey `flext-patterns` completely.
2. Prove real `flext_core`, `flext_cli`, and `flext_tests` imports in the
   dcbackup environment.
3. Map dcbackup-specific backup/orchestration ports before editing.
4. Keep backup provider SDK/process calls behind typed adapters; use services and
   ports for use cases.
5. Validate with the full dcbackup project gates plus the `flext-patterns` gate
   contract.

## DcBackup-Specific Boundaries

- CLI remains a thin inbound adapter; no backup, credential, path, retry, SDK,
  rclone, or GYB orchestration logic may live in CLI code.
- Provider adapters translate third-party errors once into `p.Result[T]`.
- Credentials and paths come from settings/DI, not module globals.
- Reuse the generic `src/<package>/{api.py,cli.py,services/,c/m/p/t/u}` layout;
  do not create dcbackup-only alternatives.

## Evidence

Record the active bead, dcbackup ownership matrix, import proof, full gate
commands with exit codes, and commit/push evidence. If a dcbackup constraint
conflicts with `flext-patterns`, stop and record the exact conflict instead of
inventing a local exception.
