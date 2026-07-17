# FLEXT Tap Oracle

FLEXT Tap Oracle (`flext-tap-oracle`) is the Singer tap for Oracle Database extraction in the FLEXT data mesh. It uses `flext-db-oracle` for database connectivity and `flext-meltano` for the Singer tap contract, exposing discover and sync commands over typed Oracle streams with `r[T]` results on every fallible path.

## Status & health

- **Version**: 0.20.0-dev (monorepo development cycle)
- **Python**: 3.13+
- **Package**: `flext_tap_oracle` (namespace package, `py.typed` shipped)
- **Location in this repo**: `flext-tap-oracle/` at the workspace root

### Quality signals

- Gates run through the workspace Make contract: `make check PROJECT=flext-tap-oracle`, `make test PROJECT=flext-tap-oracle`, `make val`.
- Strict typing per workspace `AGENTS.md`: no `Any`/`object`, Pydantic 2-way models, `r[T]` on every fallible path; Oracle access goes through `flext-db-oracle`, Singer orchestration through `flext-meltano`.
- No coverage or test-count metrics are asserted here; the gates above produce the authoritative numbers.

## Quick start

Console entry points: `tap-oracle` and `flext-tap-oracle`.

```bash
tap-oracle --discover > catalog.json
tap-oracle --sync --catalog catalog.json --state state.json
```

Programmatically:

```python
from flext_tap_oracle import FlextTapOracleCli, FlextTapOracleSettings

settings = FlextTapOracleSettings()  # namespaced under settings.TapOracle.*
result = FlextTapOracleCli.handle_discover_command()
```

The `settings.TapOracle.*` group carries `oracle_host`, `oracle_port`, `oracle_service_name`, `oracle_user`, `oracle_password`, `batch_size`, and `stream_prefix` (validated Pydantic fields).

## Architecture & modules

Source lives under `flext-tap-oracle/src/flext_tap_oracle/`:

- `tap.py` — the CLI layer: `FlextTapOracleDiscoverCommand` and `FlextTapOracleSyncCommand` implement the two Singer operations, and `FlextTapOracleCli` dispatches `--discover` / `--sync`; `main()` is the console entry.
- `streams.py` — `FlextTapOracleStreams`, a unified namespace with `OracleStream` (typed column metadata, safe identifier quoting, batched reads) and a `StreamFactory` that builds configured streams per table.
- `api.py` — `FlextTapOracleService` (a `FlextMeltanoTapServiceBase`), exported as the operational alias `tap_oracle`.
- `config/tap-oracle.yaml` — execution parametrization (SSOT per ADR-005); `rules.json` carries tap rules.
- Canonical facet facades: `c`, `m`, `p`, `t`, `u`, plus `settings` (`FlextTapOracleSettings`); operational aliases `d`, `e`, `h`, `r`, `s`, `x` come from the parent chain (`flext_db_oracle`).

### Key architectural patterns

- Discover and sync are separate command classes with a thin CLI dispatcher; the service facade remains the only orchestration owner.
- Oracle connectivity is never direct: all database access flows through `flext-db-oracle`, and Singer protocol types come from `flext-meltano` models.
- Settings/config are the only parametrization source: `settings.TapOracle.*` is validated once at singleton construction.

## Testing & quality

- Scoped suites run via `make check PROJECT=flext-tap-oracle` and `make test PROJECT=flext-tap-oracle`; full workspace validation is `make val`.
- Tests assert the public surface only (discover/sync commands, stream behavior, exported models) per the workspace testing law.

## Resources

- [Project README](../../flext-tap-oracle/README.md)
- Source: `flext-tap-oracle/src/flext_tap_oracle/`
- Workspace governance: [AGENTS.md](../../AGENTS.md), [GOVERNANCE.md](../GOVERNANCE.md)
- Related packages: `flext-core`, `flext-db-oracle`, `flext-meltano`, `flext-observability`, `flext-target-oracle`, `flext-dbt-oracle`

## Support & issues

- Issues: <https://github.com/flext-sh/flext/issues>
- Follow the workspace `AGENTS.md` and the project README before editing code or docs so this page stays accurate.
