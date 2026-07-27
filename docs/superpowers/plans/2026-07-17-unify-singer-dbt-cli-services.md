# Unify Singer/dbt CLI + Services via flext-meltano — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans. Steps use `- [ ]`.

**Goal:** Establish ONE canonical, minimal, no-ceremony pattern for every FLEXT Singer tap/target and dbt project —
CLI, services, settings/config SSOT — with a very negative net LOC, piloted on `flext-tap-ldap`,
with the singer_sdk/dbt machinery owned exclusively by `flext-meltano`.

**Architecture:** flext-meltano owns ALL external pipeline libs (singer_sdk, dbt).
It exposes a *declarative* tap/target/dbt base where the consumer supplies only domain data
(stream specs + a record fetcher backed by flext-ldap/ldif/db-oracle).
Each consumer project reduces to `base.py` (`s`), `api.py` (thin MRO facade Service),
`cli.py` (`main()->Service.cli_main()`), `services/*` (import only `c,t,p,m,u` + `s`).
All adapters, custom Typer groups, custom stream base classes, and `_utilities/*` ceremony are DELETED.

**Tech Stack:** Python 3.13, Pydantic 2, flext-core/cli/meltano/ldap/ldif, singer_sdk (only inside flext-meltano).

## Global Constraints (LOCKED — operator 2026-07-17)

- ONLY `flext-meltano` imports `singer_sdk` / `dbt`; only each flext-* library imports its own external lib
  and provides tools.
- tap/target/dbt projects import ONLY flext-* libs (cli, meltano, ldap, ldif, db_oracle, oracle_wms, oracle_oic).
- `services/*` import ONLY `c, t, p, m, u` + `s` (from `base.py`).
  Nothing else.
- Canonical files per project: `base.py`, `api.py`, `cli.py`, `services/*`, plus declaration layers
  `constants/typings/protocols/models` + `_settings.py`/`_config.py`.
- Config/settings SSOT: `from <ns> import config, settings` -> `config.<Ns>.*` / `settings.<Ns>.*`.
  Settings = adjustable per-run params; Config = business rules. No raw dict/`m.Dict` contract.
- r[T] result flow; facade layering c->t->p->m->u; protocol-first typing (no Any/object/concrete-class annotations);
  <=200 logical LOC/module; ONE canonical path per responsibility; net-LOC NEGATIVE; English-only.
- Tests: flext-tests, ONE conftest, real behavior via public interface, NO mocks, thin single nested class,
  e2e exercises the REAL console entry.
- Every python call: `env -u PYTHONPATH uv run --no-sync <ruff|pyrefly|pytest> ...`.
  Per-project gate before each commit: ruff clean + pyrefly 0 + pytest green. Commit scoped by pathspec, push FF.

---

## File Structure (pilot: flext-tap-ldap)

flext-meltano (SSOT, W0):

- `_models/declarative_tap.py` CREATE: `m.Meltano.StreamSpec` (name, json_schema, primary_keys, replication_key)
  - `m.Meltano.TapSpec` (tap_name, config_jsonschema, streams).
- `_protocols/singer.py` MODIFY: add `p.Meltano.RecordFetcher`
  (`fetch(stream_name, config)->r[Sequence[JsonMapping]]`).
- `services/declarative_tap.py` CREATE: singer_sdk builder — from `TapSpec` + `RecordFetcher` build a real
  `singer_sdk.Tap` + dynamic `Stream` subclasses whose `get_records` delegate to the fetcher.
- `services/consumer_bases/tap_service_base.py` MODIFY: concrete `create_tap_instance()` (declarative) + `cli_main()`
  threads `--config`; fix the config=None crash.

flext-tap-ldap (pilot, W1) target (~5 files, was 18):

- `api.py`: thin `FlextTapLdapService(FlextMeltanoTapServiceBase)` — `tap_name`, `tap_spec` property
  (streams from config business rules), `fetch_records` delegating to `services/extract.py`.
- `cli.py`: `def main(args=None)->int: return FlextTapLdapService().cli_main(args)`;
  console `flext_tap_ldap.cli:main`.
- `services/extract.py`: `FlextTapLdapExtractService(s)` fetch via flext-ldap `FlextLdap`
  (imports only c,t,p,m,u + s).
- Declaration layers kept + slimmed.
- DELETE: `utilities.py`, `_utilities/*`, `client.py`, `streams.py`, `ldif_streams.py`, custom `tap.py`.

Target src ~3276 -> ~600 LOC (net approx -2600). Tests refactored to real console e2e.

---

## Waves

- W0 flext-meltano declarative tap SSOT: `TapSpec`/`StreamSpec`/`RecordFetcher` + builder + fix `cli_main`.
  e2e: real declarative tap flat `--config --discover` exit 0 with catalog. Commit.
- W1 flext-tap-ldap pilot: rewrite to canonical api/cli/services via flext-ldap; delete
  adapters/utilities/custom-streams/client; refactor all tests to real console e2e. Very negative LOC.
  Commit per slice.
- W2 Skills + ADR: new skill `flext-singer-dbt-pattern`; update ADRs; new ADR for consumer architecture
  - import boundaries.
- W3 Fan out to the other 12 projects (each own commit), fixing the fleet-wide flat-CLI bug
  - divergent console entries.
