---
name: readme-standardization
description: 'Guidance for creating and auditing README.md files across the FLEXT ecosystem. Covers required sections, structure templates, badge standards, and tooling for consistent README generation and maintenance.'
license: MIT
metadata:
  version: 1.0.0
---
# README Standardization Skill

## Workflow

1. Discover README drift from expected structure.
2. Confirm the project's parent MRO chain, abstracted libraries, and primary skills before drafting the Collection Rules section.
3. Apply safe automatic fixes via `make docs DOCS_PHASE=fix`, then manual content adjustments only where the auto-generator cannot derive content (purpose, onboarding narrative, operation flow).

## Contracts

- Derive project identity, version, package metadata, and repository links from the
  same typed metadata owner used by the documentation generator.
- Keep purpose, installation, usage, architecture, contribution, and license content
  discoverable without freezing today's generated values in this skill.
- Link ecosystem packages to the canonical `flext-sh/flext` portal.
- Change generator-owned structure at its template/model owner and prove a second
  generation run is empty; do not hand-edit generated README projections.
