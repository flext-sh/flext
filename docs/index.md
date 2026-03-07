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

**Version**: 1.0.0 | **Status**: Updated 2026-02-02

Welcome to the master index for the FLEXT documentation ecosystem. The portal blends the curated narrative inside `docs/README.md` with detailed guides, architecture blueprints, API references, and the per-project manuals that sit beside each library. Use this page to orient yourself, find the right section, and understand how the documentation is kept in sync with the lint, test, and coverage reports in `reports/`.

## Quick Start

- **Install & bootstrap**: `docs/guides/getting-started.md` walks through environment setup, dependency installation, and a working LDIF example so you can ship a job in minutes.
- **Project catalog**: `docs/projects/README.md` (plus `docs/projects/flext-core.md`, `docs/projects/flext-ldif.md`, `docs/projects/flext-api/README.md`) gives the scope, status, and quick links for each library.
- **Architecture overview**: `docs/architecture/README.md` explains the CQRS + Railway-oriented programming architecture, the clean layering, and the patterns that keep 30+ projects aligned.
- **API reference**: `docs/api-reference/README.md` leads to the complete surfaces for flext-core, flext-ldif, flext-auth, and the other published packages.
- **Testing + validation**: `docs/guides/testing.md` describes the testing strategy and how the published `reports/` directory tracks every Ruff, Pyrefly, and pytest run.
- **Development workflow**: `docs/guides/development.md` collects tooling, git conventions, and the automation humans and bots use to keep docs healthy.
- **Automation pattern**: `docs/guides/skill-automation-pattern.md` standardizes how to ship future script-backed skills (skill + scripts + docs + reports).

## Status & Quality

All documentation changes are cross-checked against the generated artifacts in `reports/` (`coverage-scan-20260202_144808`, `lint-output`, `pytest`). The portal only describes content that has a living source, and every refresh runs `lsp_diagnostics` and Markdown linting before the content is merged so hyperlinks, anchors, and code blocks stay accurate.

## Documentation Sections

### Reports & Status

- The root `reports/` directory is where automated scans land. Use the `coverage-scan-*` summaries and the `lint-output` folder to verify the status claims that back up this portal.

### Architecture & Design

- `docs/architecture/README.md` introduces the clean layers, dependency diagram, and the architectural governance points. Dive into `architecture/patterns` to revisit the SOLID, Railway, and CQRS rationale that inspired the platform.

### Development & Testing Guides

- `docs/guides/*` hosts the practical playbooks: `getting-started.md`, `development.md`, `testing.md`, `configuration.md`, `troubleshooting.md`, and the companion README that maps the subtopics.
- `docs/guides/skill-automation-pattern.md` is the canonical playbook for creating reusable automation skills and validation orchestrators.

### API & Libraries

- `docs/api-reference/README.md` sweeps through all the published APIs, while each project contributes more precise API docs inside its own directory (for example, `flext-core` and `flext-ldif`).

### Projects & Integrations

- `docs/projects/README.md` provides the master grid; each highlighted project (flext-core, flext-ldif, flext-api) ships its own guide so you can see version details, architecture, and integration notes without leaving the docs tree.

### Standards & Practices

- `docs/standards/README.md` documents coding, documentation, and release standards. Follow the norms listed there whenever you add or refresh content so the entire portal remains consistent.

### Support & Community

- `docs/guides/troubleshooting.md`, `docs/guides/faq.md`, and `README-DOCUMENTATION.md` point people to email support (`dev@flext.com`), GitHub Issues, and the contribution checklist. Keep consulting these before raising new tickets or pushing docs updates.

## Projects by Category

- **Core Foundation** – `docs/projects/flext-core.md` and `flext-core/AGENTS.md` describe the shared patterns and the container that wires the platform.
- **LDAP & Directory Services** – `docs/projects/flext-ldif.md` plus `flext-ldap/AGENTS.md` cover bulk LDIF processing and LDAP-specific integrations.
- **API & CLI** – `docs/projects/flext-api/README.md` together with `flext-cli/AGENTS.md` explain how the REST and CLI surfaces unify around flext-core abstractions.
- **Infrastructure & Observability** – `flext-grpc/AGENTS.md` and `flext-observability/AGENTS.md` detail the RPC, monitoring, and telemetry projects that sit beside event buses and workflow runners.
- **Plugins & Data Integrations** – `flext-plugin/AGENTS.md` and `flext-meltano/AGENTS.md` narrate the plugin system, Singer taps/targets, and the Meltano workflows that orchestrate cross-project transforms.

## Key Features

- Enterprise-grade architecture governed by Railway-oriented programming and clear layering.
- 30+ project manuals with synchronized versioning and documentation links.
- Automated validation via Ruff, Pyrefly, Bandit, and coverage scans alongside Markdown linting.
- Support resources that tie documentation, reporting, and contribution workflows together.

## Support & Recent Updates

- Email support: <dev@flext.com>; raise documentation issues through the GitHub tracker referenced in `README-DOCUMENTATION.md`.
- The docs team refreshes the portal whenever a project releases. We update the quick links, run `lsp_diagnostics`, and confirm every new section lists the relevant `reports/` evidence.
- Recent edits: reorganized the documentation portal, expanded quick links, and added a central reminder to verify docs before merging (this file).

---

_FLEXT Documentation Portal maintained by the platform team. Keep links alive, keep references current, and reference this portal before onboarding new contributors._
