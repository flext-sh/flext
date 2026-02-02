# FLEXT DB Oracle

FLEXT DB Oracle (v0.9.9) is the enterprise Oracle database integration foundation for the FLEXT ecosystem. It wraps SQLAlchemy 2.0 + python-oracledb behind FlextResult-driven services, connection pooling, schema introspection, and CLI helpers so every Oracle-focused project reuses identical patterns.

## Status & metrics

- **Version**: 0.9.9 (Phase 2 CLI work in progress)
- **Python**: 3.13+ only
- **Tests**: 558 default suites + 30 integration files (8,633+ lines)
- **Coverage**: ~100% target (currently improving toward 90%+)
- **Quality gate**: `make validate` (ruff + pyrefly + bandit + pytest + coverage + docstring checks)
- **Type safety**: Pyrefly strict + MyPy strict (zero `Any`, zero `cast`, zero `# type` ignores)
- **Security**: Bandit zero high/medium findings reported in `reports/lint-output/`

## Quick start

```bash
git clone https://github.com/flext-sh/flext.git
cd flext-db-oracle
poetry install
make setup
```

```python
from flext_db_oracle.api import FlextDbOracleApi
from flext_db_oracle.models import FlextDbOracleModels

config = FlextDbOracleModels.OracleConfig(host="localhost", port=1521, service_name="XEPDB1", username="system", password="Oracle123")
api = FlextDbOracleApi(config)

connection_result = api.test_connection()
if connection_result.is_success:
    print("✅ Connected to Oracle")

result = api.query("SELECT table_name FROM user_tables WHERE rownum <= :limit", {"limit": 5})
if result.is_success:
    tables = result.unwrap()
    print(f"Found {len(tables)} tables")
```

## Architecture overview

- **FlextDbOracleApi** (`api.py`) - single facade that exposes query, schema, connection, and CLI operations; the only file permitted to import SQLAlchemy/Oracle directly.
- **Service layer** (`services/`, `providers/`) - orchestrates connection pooling, schema introspection, and migration helpers atop FlextResult.
- **Protocols & models** - `models.py`, `constants.py`, `typings.py`, `protocols.py` share the same short alias discipline (`r`, `c`, `t`, `p`).
- **CLI integration** - uses `flext-cli` conventions; Phase 2 replaces SimpleNamespace placeholders with Rich formatters and progress indicators while keeping the same `make oracle-connect` commands.

## Key features

- Enterprise-grade Oracle connectivity with failover-aware connection pooling, metadata extraction, and parameterized query execution.
- Schema introspection helpers (tables, columns, constraints) and migration-ready builders for Oracle-specific quirks.
- Railway error handling (`FlextResult[T]`) and compliance with flext-core patterns (no `TYPE_CHECKING`, no `Any`, zero-cast policy).
- Integration with `flext-tap-oracle`, `flext-target-oracle`, and `flext-dbt-oracle` so downstream ETL flows re-use workloads.
- Quality gates: `make lint`, `make type-check`, `make security`, `make test`, `make validate`, plus Oracle integration tests (Pytest markers `unit`, `integration`).

## References & resources

- [Project README](../../flext-db-oracle/README.md) for the full narrative
- [CLAUDE governance](../../flext-db-oracle/CLAUDE.md) for zero-tolerance rules (SQLAlchemy only in `api.py`)
- Reports: `reports/pytest/*`, `reports/coverage-scan-*`, `reports/lint-output/*`
- Related docs: `docs/getting-started.md`, `docs/architecture.md`, `docs/development.md`, `docs/troubleshooting.md` inside the project
- Related projects: `flext-core`, `flext-cli`, `flext-tap-oracle`, `flext-target-oracle`, `flext-dbt-oracle`

## Support & contributions

- GitHub issues: <https://github.com/flext-sh/flext-db-oracle/issues>
- Discussions: <https://github.com/flext-sh/flext-db-oracle/discussions>
- Follow `docs/standards/README.md`, the workspace `CLAUDE.md`, and the per-project checklist before submitting changes so the portal brief stays accurate.
