# FLEXT LDIF

<!-- TOC START -->

- [Status & metrics](#status-metrics)
- [Quick start](#quick-start)
- [Key capabilities](#key-capabilities)
- [Architecture overview](#architecture-overview)
- [Usage highlights](#usage-highlights)
- [Testing & quality](#testing-quality)
- [Resources](#resources)
- [Support & contribution](#support-contribution)
<!-- TOC END -->

FLEXT LDIF is the RFC 2849/4512-compliant LDIF processor for the FLEXT platform. It combines a strict parser, a quirk registry for server-specific rules, and migration pipelines that can target Oracle (OID/OUD), OpenLDAP, Active Directory, and any RFC-compliant LDAP server.

## Status & metrics

- **Version**: 1.0.0
- **Python**: 3.13+
- **Tests**: 1 766 passing
- **Coverage**: 78% (see `reports/coverage-scan-*`)
- **Type safety**: Pyrefly strict mode and Ruff pass with zero errors
- **Quality gate**: `make validate` (lint + type-check + security + test)

## Quick start

```bash
pip install flext-ldif
```

```python
from pathlib import Path
from flext_ldif import FlextLdif

ldif = FlextLdif()
result = ldif.parse(Path("directory.ldif"))
if result.is_success:
    print(f"Parsed {len(result.unwrap())} entries")
else:
    print(f"Error: {result.error}")
```

Use `ldif.migrate(...)` for server-to-server conversions, `parse_with_auto_detection` to let the registry choose the quirks, and the `FlextLdifModels` helpers for filtering and categorizing entries.

## Key capabilities

- **RFC-first parsing**: all processing flows through RFC 2849/4512 parsers before quirks are applied.
- **Quirk registry**: auto-discovers Oracle, OpenLDAP, AD, 389DS, and custom quirks and applies them via priority-based dispatch.
- **Conversion matrix**: N×N server conversions with DN case registry, ACL transformation, and relaxed mode for broken LDIF.
- **Railway-oriented errors**: every operation returns `FlextResult[T]` so callers can compose validation, migration, and filtering.
- **Batch & parallel processors**: configurable batch or thread pool processors for large datasets (subject to memory limits, see Known Limitations in the project README).

## Architecture overview

```
Input LDIF → RFC parser → Quirk adapters → Target writer/migration pipeline
```

- **Core modules**: `api.py` (facade), `config.py`, `constants.py`, `typings.py`, `protocols.py`, `models.py`, `utilities.py`.
- **Pipeline services**: `services.migration_pipeline`, `services.server_detector`, `services.rfc_schema_parser`.
- **Extensible quirks**: `quirks.registry`, `quirks.server-specific`, `quirks.conversion_matrix`, `quirks/dn_case_registry`.
- **RFC compliance layer**: `rfc/` modules with parser/writer/schema helpers.

## Usage highlights

- **Auto-detect servers**: `parse_with_auto_detection` returns metadata that identifies the detected server quirk.
- **Server migrations**: `ldif.migrate(input_dir, output_dir, from_server, to_server)` pipelines entries through RFC + quirks and writes structured output.
- **Categorization & filtering**: use `FlextLdifModels.FilterCriteria` and `ldif.filter`/`categorize` helpers for reports.
- **Relaxed parsing**: `parse_relaxed` recovers from broken LDIF when RFC compliance is not strictly required.

## Testing & quality

- `make check` (Ruff + Pyrefly)
- `make test` (unit + integration) with unified helpers (`tests.tm`, `tests.tf`)
- `make validate` (adds Bandit, detect-secrets, coverage, docstring checks)
- Quality expectations: Pyrefly strict (100% type safety), Ruff zero violations, Bandit zero high/medium issues, test coverage ≥78%.

## Resources

- [Project README](../../flext-ldif/README.md)
- [CLAUDE guidance](../../flext-ldif/CLAUDE.md)
- `docs/getting-started.md`, `docs/api-reference.md`, `docs/architecture.md`, `docs/guides/integration.md`, `docs/migration/v0.9-to-v1.0-migration.md`, `docs/troubleshooting.md`
- Known limitations and memory note live in the README (files larger than 100 MB may exhaust memory).
- Related reports: `reports/coverage-scan-*`, `reports/lint-output/*`, `reports/pytest/*`.

## Support & contribution

- GitHub issues: <https://github.com/flext-sh/flext-ldif/issues>
- Discussions: <https://github.com/flext-sh/flext-ldif/discussions>
- Email: <support@flext-platform.org>
- Follow the project’s `docs/development.md` and the workspace `docs/standards/README.md` before proposing doc changes so this summary stays aligned with the portal.
