---
name: lib-pyyaml
description: 'Use this skill to safe and deterministic YAML read/write patterns across
  FLEXT subprojects. Use when modifying YAML parsing, settings files, CLI output formatting,
  or docs-maintenance tooling. DO NOT USE FOR: questions unrelated to lib-pyyaml creating
  projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---

# Lib PyYAML

**UTILITY SKILL**

## USE FOR

- Requests about lib pyyaml.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to lib-pyyaml.
- creating projects or architecture from scratch.

## Workflow

1. Find nearest YAML call-site in the touched subproject.
2. Preserve that module's established style (`safe_load` + `dump/safe_dump` options).
3. Add/keep shape checks after loading (`dict`/`list`) before model construction.

## Critical rules

- Prefer canonical sources.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
