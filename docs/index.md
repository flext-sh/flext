# FLEXT Ecosystem Documentation Portal

<!-- TOC START -->

- [Quick Start](#quick-start)
- [Status & Quality](#status-quality)
- [Documentation Sections](#documentation-sections)
  - [Reports & Status](#reports-status)
  - [Architecture & Design](#architecture-design)
  - [Development & Testing Guides](#development-testing-guides)
  - [API & Libraries](#api-libraries)
  - [Projects & Integrations](#projects-integrations)
  - [Standards & Practices](#standards-practices)
  - [Support & Community](#support-community)
- [Projects by Category](#projects-by-category)
- [Key Features](#key-features)
- [Support & Recent Updates](#support-recent-updates)
<!-- TOC END -->

**Version**: 1.0.0 | **Status**: Updated 2026-04-05

Welcome to the master index for the FLEXT documentation ecosystem. The portal blends the curated narrative inside `docs/README.md` with detailed guides, architecture blueprints, API references, and the per-project manuals that sit beside each library. Use this page to orient yourself, find the right section, and understand how the documentation is kept in sync with the lint, test, and coverage reports in `reports/`.

## Quick Start

- **Install & bootstrap**: `docs/guides/getting-started.md` walks through environment setup, dependency installation, and a working LDIF example so you can ship a job in minutes.
- **v0.13.0 baseline**: `docs/architecture/baseline-v0.13.0.md` is the governing workspace architecture baseline for the next platform cycle.
- **Project catalog**: `docs/projects/README.md` (plus `docs/projects/flext-core.md`, `docs/projects/flext-ldif.md`, `docs/projects/flext-api/README.md`) gives the scope, status, and quick links for each library.
- **Architecture index**: `docs/architecture/README.md` points to the canonical baseline, ADRs, and supporting references.
- **API reference**: `docs/api-reference/README.md` leads to the complete surfaces for flext-core, flext-ldif, flext-auth, and the other published packages.
- **Testing + validation**: `docs/guides/testing.md` describes the testing strategy and how the published `reports/` directory tracks every Ruff, Pyrefly, and pytest run.
- **Development workflow**: `docs/guides/development.md` collects tooling, git conventions, and the automation humans and bots use to keep docs healthy.
- **Automation pattern**: `docs/guides/skill-automation-pattern.md` standardizes how to ship future script-backed skills (skill + scripts + docs + reports).
- **Migration guide**: `docs/guides/migration-to-v0.13.0.md` translates the baseline into implementation tracks by project category.

## Status & Quality

All documentation changes are cross-checked against the generated artifacts in `reports/` (`coverage-scan-20260202_144808`, `lint-output`, `pytest`). The portal only describes content that has a living source, and every refresh runs `lsp_diagnostics` and Markdown linting before the content is merged so hyperlinks, anchors, and code blocks stay accurate.

## Documentation Sections

### Reports & Status

- The root `reports/` directory is where automated scans land. Use the `coverage-scan-*` summaries and the `lint-output` folder to verify the status claims that back up this portal.

### Architecture & Design

- `docs/architecture/baseline-v0.13.0.md` is the governing forward baseline for the workspace.
- `docs/architecture/README.md` is the architecture index that points to the baseline, ADRs, and supporting references.

### Development & Testing Guides

- `docs/guides/*` hosts the practical playbooks: `getting-started.md`, `development.md`, `testing.md`, `configuration.md`, `troubleshooting.md`, `migration-to-v0.13.0.md`, and the companion README that maps the subtopics.
- `docs/guides/skill-automation-pattern.md` is the canonical playbook for creating reusable automation skills and validation orchestrators.

### API & Libraries

- `docs/api-reference/README.md` sweeps through all the published APIs, while each project contributes more precise API docs inside its own directory (for example, `flext-core` and `flext-ldif`).

### Projects & Integrations

- `docs/projects/README.md` provides the master grid; each highlighted project (flext-core, flext-ldif, flext-api) ships its own guide so you can see version details, architecture, and integration notes without leaving the docs tree.

### Standards & Practices

- `docs/standards/README.md` documents coding, documentation, and release standards. Follow the norms listed there whenever you add or refresh content so the entire portal remains consistent.

### Support & Community

- `docs/guides/troubleshooting.md`, `docs/README.md`, and `docs/standards/README.md` point people to the current documentation entry points, contribution expectations, and maintenance guidance. Check those before opening new documentation work.

## Projects by Category

- **Core Foundation** – `docs/projects/flext-core.md` plus workspace `AGENTS.md` describe shared patterns and container wiring.
- **LDAP & Directory Services** – `docs/projects/flext-ldif.md`, `docs/projects/flext-ldap.md`, and workspace `AGENTS.md` cover LDIF processing and LDAP integration rules.
- **API & CLI** – `docs/projects/flext-api/README.md`, `docs/projects/flext-cli.md`, and workspace `AGENTS.md` explain how REST and CLI surfaces align with flext-core abstractions.
- **Infrastructure & Observability** – `docs/projects/flext-grpc.md`, `docs/projects/flext-observability.md`, and workspace `AGENTS.md` describe RPC, telemetry, and monitoring boundaries.
- **Plugins & Data Integrations** – `docs/projects/flext-plugin.md`, `docs/projects/flext-meltano.md`, and workspace `AGENTS.md` map plugin and Singer/Meltano orchestration boundaries.

## Key Features

- Enterprise-grade architecture governed by Railway-oriented programming and clear layering.
- 30+ project manuals with synchronized versioning and documentation links.
- Automated validation via Ruff, Pyrefly, Bandit, and coverage scans alongside Markdown linting.
- Support resources that tie documentation, reporting, and contribution workflows together.

## Support & Recent Updates

- Use the repository issue tracker and the docs entry points in `docs/README.md` and `docs/standards/README.md` for documentation follow-up.
- The docs team refreshes the portal whenever a project releases. We update the quick links, run `lsp_diagnostics`, and confirm every new section lists the relevant `reports/` evidence.
- Recent edits: added the workspace `0.13.0` baseline, the platform-baseline ADR, and the migration guide, then repointed the architecture and guides indexes to the new canonical path.

---

_FLEXT Documentation Portal maintained by the platform team. Keep links alive, keep references current, and reference this portal before onboarding new contributors._
