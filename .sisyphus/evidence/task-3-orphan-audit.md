# Orphan Audit Report

Generated: 2026-03-01T02:12:45Z

## Methodology

For each skill with a `rules.yml`, cross-reference every `.yml` file in the skill's `rules/` directory against the `file:` and `fix_file:` entries in `rules.yml`.
Files that exist in `rules/` but are NOT referenced by `rules.yml` are classified as orphans.

## Results

### flext-docs-pointer-policy
- `rules/pointer-no-duplication-policy.yml` — IDs: pointer-no-duplication-policy
- `rules/pointer-reference-claude.yml` — IDs: pointer-reference-claude

### flext-patterns
- `rules/no-breakpoint-import.yml` — IDs: no-breakpoint-import
- `rules/sys-exit-fix.yml` — IDs: fix-sys-exit-with-arg
fix-sys-exit-no-arg

### flext-quality-gates
- `rules/require-ruff-config.yml` — IDs: require-ruff-config
- `rules/require-test-target.yml` — IDs: require-test-target

### lib-returns
- `rules/returns-detect.yml` — IDs: ban-unwrap-call
ban-direct-success-constructor
ban-direct-failure-constructor
- `rules/returns-fix.yml` — IDs: fix-unwrap-to-value-or

### readme-standardization
- `rules/readme-ecosystem-link.yml` — IDs: readme-ecosystem-link
- `rules/readme-has-architecture.yml` — IDs: readme-has-architecture
- `rules/readme-has-contributing.yml` — IDs: readme-has-contributing
- `rules/readme-has-installation.yml` — IDs: readme-has-installation
- `rules/readme-has-key-features.yml` — IDs: readme-has-key-features
- `rules/readme-has-license.yml` — IDs: readme-has-license
- `rules/readme-has-usage.yml` — IDs: readme-has-usage
- `rules/readme-preamble.yml` — IDs: readme-preamble

### rules-docker
- `rules/require-healthcheck.yml` — IDs: require-healthcheck

### rules-docs
- `rules/docs-absolute-paths.yml` — IDs: docs-absolute-paths
- `rules/docs-has-readme.yml` — IDs: docs-has-readme
- `rules/docs-no-todo-fixme.yml` — IDs: docs-no-todo-fixme
- `rules/no-trailing-whitespace-in-md.yml` — IDs: no-trailing-whitespace-in-md

### rules-github
- `rules/require-workflow-name.yml` — IDs: require-workflow-name

### scripts-architecture
- `rules/no-direct-singer-import-meltano.yml` — IDs: no-direct-singer-import-meltano

### workspace-maintenance
- `rules/gitignore-has-dist-pattern.yml` — IDs: gitignore-has-dist-pattern
- `rules/gitignore-has-pycache-pattern.yml` — IDs: gitignore-has-pycache-pattern

## Summary

- Skills audited: 42
- Orphan files found: 25

