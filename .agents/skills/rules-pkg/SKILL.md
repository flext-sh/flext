---
name: rules-pkg
description: 'Rules for package metadata and package-layer structure under `pkg/`. Use when editing package descriptors, plugin manifests, or packaging utilities.'
license: MIT
metadata:
  version: 1.0.0
---
# Rules Pkg

## Workflow

1. Identify package area being modified.
2. Apply minimal metadata/structure change.
3. Confirm references in build scripts/docs still resolve.

## Enforced contracts

- Package modules should enable postponed annotation evaluation.

## Resources

- [`rules/require-future-annotations.yml`](rules/require-future-annotations.yml)
