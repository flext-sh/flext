---
name: lib-pyyaml
description: 'Guidance for safe and deterministic YAML read/write patterns across FLEXT subprojects. Use when modifying YAML parsing, settings files, CLI output formatting, or docs-maintenance tooling.'
license: MIT
metadata:
  version: 1.0.0
---
# Lib PyYAML

## Workflow

1. Find nearest YAML call-site in the touched subproject.
2. Preserve that module's established style (`safe_load` + `dump/safe_dump` options).
3. Add/keep shape checks after loading (`dict`/`list`) before model construction.

## Enforced contracts

- yaml.load is unsafe and must not be used.

## Resources

- [`rules/ban-unsafe-yaml-load.yml`](rules/ban-unsafe-yaml-load.yml)
