# FLEXT Target Oracle


<!-- TOC START -->
- [Status & signals](#status-signals)
- [Quick start](#quick-start)
- [Architecture & patterns](#architecture-patterns)
- [Quality & concerns](#quality-concerns)
- [Resources & references](#resources-references)
- [Support & contributions](#support-contributions)
<!-- TOC END -->

FLEXT Target Oracle is the Singer target that loads data into Oracle databases while enforcing the FLEXT platform's zero-tolerance rules. Status is release-prep (v0.9.9/1.0.0), documentation is complete, but production deployment is blocked until the critical SQL injection and Singer compliance gaps are fixed.

## Status & signals

- **Version**: 0.9.9 (1.0.0 Release Preparation)
- **Python**: 3.13+
- **Status**: Documentation ready, implementation blocked (critical SQL injection vulnerability in `loader.py`, missing Singer SDK standard methods, DDL/DML mixups, transaction gaps)
- **Quality gate**: `make validate` (ruff + pyrefly + bandit + pytest + coverage + docstring checks) is configured but cannot fully pass until the security fixes land; `make lint`, `make type-check`, `make security`, and `make test` currently run but warning on the blockers
- **Coverage**: >90% per README but the final gate waits for migration/transaction fixes
- **Security**: SQL injection fix, exception consolidation, Singer compliance, and transaction management are documented with blocking warnings (see `docs/TODO.md`)
- **Type discipline**: MyPy + Pyrefly strict, zero `Any`/`cast`/`# type: ignore`; every API returns `FlextResult[T]`

## Quick start

```bash
git clone https://github.com/flext-sh/flext-target-oracle.git
cd flext-target-oracle
poetry install
make setup
make validate  # currently blocked until security fixes land
```

```python
from flext_target_oracle import FlextOracleTarget, FlextOracleTargetSettings, LoadMethod

settings = FlextOracleTargetSettings(
    oracle_host="localhost",
    oracle_port=1521,
    oracle_service="XE",
    oracle_user="singer_user",
    oracle_password="password",
    default_target_schema="SINGER_DATA",
    load_method=LoadMethod.BULK_INSERT,
    batch_size=1000,
    use_bulk_operations=True,
)

target = FlextOracleTarget(settings)
result = target.write_record({"id": 1, "name": "Admin"})
if result.is_failure:
    print("Record write failed", result.error)
```

## Architecture & patterns

- **Clean Architecture**: `constants.py`, `typings.py`, `protocols.py` (Tier 0); `models.py`, `utilities.py` (Tier 1); `config.py`, `target.py`, `loader.py`, `exceptions.py` (Tier 2/3) follow strict layering. Lower tiers never import higher modules.
- **Flext integration**: depends on `flext-core` (FlextResult, FlextContainer, logging), `flext-meltano` (Singer integration), `flext-db-oracle` (connection/pooling), and exposes interfaces for `flext-target-` Wish list.
- **Data flow**: Singer tap schema/record/state messages pass through `FlextOracleTarget`, orchestrate `OracleLoader`, and land in Oracle with batched commits and `FlextResult` chaining.
- **Issue tracking**: README/`docs/TODO.md` list critical blockers (SQL injection, exception duplication, missing Singer methods, DDL vs DML misuse, transaction support, schema evolution) that must be resolved before production readiness.

## Quality & concerns

- `make lint`, `make type-check`, `make security`, `make test`, `make coverage-html`, `make validate` exist; the final gate stops at the security warnings.
- Coverage is ~90% but gating scripts flag the blockers; the team tracks them under priority 1-4 targets in the README.
- Security status: SQL injection in `loader.py` is red-flagged with remediation steps in `docs/TODO.md`; production deployment is blocked until the analyzer/transaction code is hardened.
- Pre-commit hooks ensure no `singer-sdk`/`sqlalchemy/oracledb` imports outside allowed adapters and enforce zero tolerance for `Any` or `cast`.

## Resources & references

- [Project README](../../flext-target-oracle/README.md)
- [Project CLAUDE](../../flext-target-oracle/CLAUDE.md) (zero-tolerance rules, command checklist)
- `docs/` folder (architecture, development, Singer integration guides, TODO/security tracker)
- `reports/coverage-scan-*`, `reports/lint-output/*`, `reports/pytest/*` once the blocked gates finish
- Related projects: `flext-core`, `flext-db-oracle`, `flext-meltano`, `flext-target-ldap`, `flext-dbt-oracle`, `flext-web`, `flext-quality`

## Support & contributions

- GitHub issues: <https://github.com/flext-sh/flext-target-oracle/issues>
- Discussions: <https://github.com/flext-sh/flext-target-oracle/discussions>
- Follow `docs/standards/README.md`, this project’s `CLAUDE`, and the portal checklist before editing so the updates stay accurate.
