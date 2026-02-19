# FLEXT Documentation Portal


<!-- TOC START -->
- [Key Features](#key-features)
  - [Overview](#overview)
- [Highlighted Content](#highlighted-content)
  - [Getting Started & Guides](#getting-started-guides)
- [Architecture](#architecture)
  - [Architecture & Patterns](#architecture-patterns)
  - [API & Project References](#api-project-references)
  - [Reports & Quality Assurance](#reports-quality-assurance)
- [Quality Assurance & Maintenance](#quality-assurance-maintenance)
- [Installation](#installation)
- [Usage](#usage)
  - [Quick Links](#quick-links)
- [Contributing](#contributing)
- [License](#license)
<!-- TOC END -->

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Curated portal for every FLEXT document, detailed guides, standards, and project manuals.

**Reviewed**: 2026-02-17 | **Version**: 0.10.0-dev

Part of the [FLEXT](https://github.com/flext-sh/flext) ecosystem.

## Key Features

### Overview

## Highlighted Content

### Getting Started & Guides

- **[Guides](guides/README.md)** – Installation, development workflows, testing playbooks, configuration, and troubleshooting live inside the dedicated Guides folder and its companion files.
- **[Automation Skill Pattern](guides/skill-automation-pattern.md)** – Canonical pattern for future automation work (skill + checker + orchestrator + docs + baseline/report artifacts).
- **[Getting Started](guides/getting-started.md)** – Step-by-step setup, sample projects, and onboarding notes appear in the Getting Started document within that folder.

## Architecture

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

## Installation

Documentation does not require installation. However, you can run the documentation server:

```bash
mkdocs serve
```

## Usage

### Quick Links

- [Documentation Index](index.md) – Aggregates highlights, project statuses, and recent updates.
- [Architecture Guide](architecture/README.md) – Start with the architecture overview, then drill into the pattern documentation.
- [API Reference](api-reference/README.md) – Review the API handbook for each published module.
- [Standards & Practices](standards/README.md) – Follow the standards guide to keep code and docs aligned.
- [Getting Started](guides/getting-started.md) – The Getting Started article details the onboarding steps.
- [Guides Catalog](guides/README.md) – The Guides folder collects deployment, configuration, and troubleshooting playbooks.
- [Automation Skill Pattern](guides/skill-automation-pattern.md) – Reusable standard for creating script-backed skills and validation automation.
- Quality Reports – The reports folder holds the latest artifacts from the Ruff, Pyrefly, and Bandit pipelines.

## Contributing

- **Email**: <dev@flext.com>
- **Issues**: <https://github.com/flext-sh/flext/issues>
- **Contributing**: The standards guide outlines how to propose content, including the expectation that every submission passes linter checks and links to the relevant `lsp_diagnostics` configuration.
- **Review Cycle**: New or modified documentation flows through the same CI that exercises `flext-core`; reference the standards checklist and the lint-output logs before submitting.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

_FLEXT Documentation is maintained by the platform team. Keep the portal accurate, keep the links alive, and share the portal with anyone onboarding to FLEXT._
