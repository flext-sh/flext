# Guides Index

<!-- TOC START -->

- [Canonical Guides](#canonical-guides)
- [Scope](#scope)

<!-- TOC END -->

Guides are curated documents for workflow, migration, and day-to-day maintenance. They
complement generated API reference; they do not duplicate it.

Every guide follows the [governance router](../GOVERNANCE.md) and its
[engineering conformance review](../GOVERNANCE.md#engineering-conformance-review).
Root guides are the writable source for generated member guides; strengthen the
shared owner rather than copying engineering law into each package.

## Canonical Guides

### Onboarding & Getting Started

- [Onboarding (Collection Rules)](onboarding.md) — required pre-work, governance hierarchy, and workspace orientation for any FLEXT project.
- [Getting Started](getting-started.md) — initial environment setup, `make setup`, and first validation pass.

### Daily Workflow & Make Lifecycle

- [Make Commands](make-commands.md) — selector-free public Make verbs, operation ownership, single-pass contracts, and lane verification (`ADR-003`, `ADR-004`, `ADR-025`, `ADR-029`, `ADR-030`).
- [Development](development.md) — day-to-day coding workflow, facade MRO (`c -> t -> p -> m -> u`), and code generation.
- [Configuration](configuration.md) — layer-0 `FlextSettings`, YAML configuration layers, and environment precedence (`ADR-024`).
- [Testing](testing.md) — incremental and full Testmon suite execution, `flext-tests` factories, and real-consumer validation (`ADR-029`).
- [Security Guide](security.md) — credential hygiene, Bandit/Semgrep gates, and secret isolation.

### Framework & Library Usage

- [Using flext-core](using-flext-core.md) — `FlextResult` (`r`), `FlextService` (`s`), `FlextContainer`, `FlextModels` (`m`), and `FlextUtilities` (`u`).
- [Using flext-cli](using-flext-cli.md) — CLI command construction, output formatting, and YAML/TOML ingress.
- [Using flext-tests](using-flext-tests.md) — test builders, fixtures, and assertion helpers.
- [Using Pydantic](using-pydantic.md) — strict Pydantic v2 models, `ConfigDict`, and boundary validation (`ADR-008`).

### Refactoring, Automation & Migration

- [Migration to v0.13.0](migration-to-v0.13.0.md) — step-by-step migration to the `0.13.0` facade and DI baseline (`ADR-028`).
- [Codemod Rules](codemod-rules.md) — declarative AST and text codemod catalog (`make mod`, `make mod-rules`).
- [Skill Automation Pattern](skill-automation-pattern.md) — routing agent skills to deterministic CLI and Make verification loops.
- [Troubleshooting](troubleshooting.md) — diagnosing lock drift, environment provenance failures, and gate diagnostics.

## Scope

- architecture direction belongs in `docs/architecture/`
- generated API details belong in `docs/api-reference/` and each project's local
  generated docs
- project-specific operational playbooks remain local to the owning project
