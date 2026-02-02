# FLEXT Documentation Portal

## Overview

This folder is the curated portal for every FLEXT document; the entry point at `docs/index.md` keeps the picture fresh while the subdirectories host detailed guides, standards, and project manuals. Use this page when you need a quick refresher about what the documentation contains and how to reach the pieces you care about.

## Highlighted Content

### Getting Started & Guides

- **[Guides](guides/README.md)** – Installation, development workflows, testing playbooks, configuration, and troubleshooting live inside the dedicated Guides folder and its companion files.
- **[Getting Started](guides/getting-started.md)** – Step-by-step setup, sample projects, and onboarding notes appear in the Getting Started document within that folder.

### Architecture & Patterns

- **[Architecture Overview](architecture/README.md)** – Clean architecture layers, dependency diagrams, and the CQRS + Railway-oriented programming mix are explained in the architecture chapter.
- **[Standards](standards/README.md)** – The coding, documentation, and deployment rules that keep the 30+ FLEXT projects aligned are consolidated in the standards guide.

### API & Project References

- **[API Reference](api-reference/README.md)** – Handbooks for every exported module and service in the ecosystem appear inside the API Reference section.
- **[Projects](projects/README.md)** – The project catalog lists flext-core, flext-ldif, flext-auth, flext-ldap, flext-grpc, and the rest with metadata and status notes.

### Reports & Quality Assurance

- **Reports** – The root reports directory stores the dashboards, validation summaries, and security analyses that keep this portal honest.
- **Validation Guides** – Consult the standards guide and the lint-output artifacts to understand the Ruff, Pyrefly, and Bandit gates that every merge must satisfy.

## Quality Assurance & Maintenance

- **Documentation Audits** – Each release runs Markdown linting, spell checking, and `lsp_diagnostics` on writers’ editors to eliminate drift before the docs reach the portal.
- **Pattern Analysis** – Metadata harvesters detect outdated anchors and unused references, then feed results back into the standards docs for rewrites and cleanup.
- **Batch Operations** – When an API surface changes, a single report reroutes every link in `docs/README.md`/`docs/index.md` so future readers get current details without manual hunting.

## Quick Links

- [Documentation Index](index.md) – Aggregates highlights, project statuses, and recent updates.
- [Architecture Guide](architecture/README.md) – Start with the architecture overview, then drill into the pattern documentation.
- [API Reference](api-reference/README.md) – Review the API handbook for each published module.
- [Standards & Practices](standards/README.md) – Follow the standards guide to keep code and docs aligned.
- [Getting Started](guides/getting-started.md) – The Getting Started article details the onboarding steps.
- [Guides Catalog](guides/README.md) – The Guides folder collects deployment, configuration, and troubleshooting playbooks.
- Quality Reports – The reports folder holds the latest artifacts from the Ruff, Pyrefly, and Bandit pipelines.

## Support & Contributions

- **Email**: <dev@flext.com>
- **Issues**: https://github.com/flext/flext/issues
- **Contributing**: The standards guide outlines how to propose content, including the expectation that every submission passes linter checks and links to the relevant `lsp_diagnostics` configuration. 
- **Review Cycle**: New or modified documentation flows through the same CI that exercises `flext-core`; reference the standards checklist and the lint-output logs before submitting.

---

_FLEXT Documentation is maintained by the platform team. Keep the portal accurate, keep the links alive, and share the portal with anyone onboarding to FLEXT._
