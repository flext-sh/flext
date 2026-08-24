# ADR-006: Thin Domain Drivers over flext-meltano Bases + Action Libraries

<!-- TOC START -->
- [Status](#status)
- [Context](#context)
  - [The duplication / anti-patterns (verified, file:line)](#the-duplication-anti-patterns-verified-fileline)
- [Decision](#decision)
  - [Rules (inviolable for these projects)](#rules-inviolable-for-these-projects)
  - [Uniform connection seam](#uniform-connection-seam)
- [Consequences](#consequences)
- [Realized mechanism — Declarative tap (flext-tap-ldap pilot, 2026-07-17)](#realized-mechanism-declarative-tap-flext-tap-ldap-pilot-2026-07-17)
- [Evidence](#evidence)
<!-- TOC END -->

## Status

Accepted (tap pilot realized 2026-07-17)

**Tracking:** beads lane `mro-rn88` (dbt/target inventory) + `mro-6int.3`
(tap declarative pilot: **flext-tap-ldap**, landed). Rollout to the remaining `flext-(dbt|tap|target)-*` projects
follows the flext-tap-ldap pilot.

**Depends:** builds on ADR-005 (config/settings SSOT) and the repository FLEXT law — §1.2 Pydantic-2 models everywhere,
§3.2 types come from protocols `p.*` not concrete models, §3a JSON is Pydantic 2-way, §1.5 no duplicated declarations
across projects.

## Context

The Singer/dbt integration projects ( `flext-(dbt|tap|target)-<domain>` ) are meant to be **thin domain drivers**:
flext-meltano owns the reusable dbt/singer/tap/target machinery in FLEXT form, the domain **action library** (e.g.
`flext-db-oracle` ) owns the connection/execution contract, and the integration project should declare *almost nothing*
— only the one domain hook its base asks for.

The current pilot trio does the opposite. Verified 2026-07-10 (three explore passes + codegraph blast-radius on
`connection_profile` ):

- **flext-meltano exposes exactly 3 consumer bases** (no separate "singer" base — singer = tap + target), all
  subclassing `FlextMeltanoServiceBase(s[t.JsonMapping])`:
  - `FlextMeltanoDbtServiceBase` — `services/consumer_bases/dbt_service_base.py:32`; abstract = `dbt_project_name` +
    `connection_profile` (`:61-69`); provides `run_models/run_tests/compile_models/generate_docs/load_manifest/fetch_models/cli_main`.
  - `FlextMeltanoTapServiceBase` — `tap_service_base.py:23`; abstract = `tap_name` +
    `create_tap_instance() -> p.Meltano.SingerTapInstance` (`:54-62`); provides
    `run_discover/run_sync/connect/disconnect/cli_main`.
  - `FlextMeltanoTargetServiceBase` — `target_service_base.py:24`; abstract = `target_name` +
    `create_sink() -> p.Meltano.SingerDrainSink` (`:48-57`); provides
    `fetch_or_create_sink/flush/process_record/process_batch/connect/disconnect/cli_main`.
- **flext-db-oracle is the Oracle action library** (deps: flext-cli + flext-core only). Connection SSOT =
  `settings.DbOracle.*` (`_settings.py:33-93`), env prefix `ORACLE_`. Runtime I/O = `FlextDbOracleApi` / `db_oracle`
  (`api.py`). Connection lifecycle contract = `p.DbOracle.Connection` (`protocols.py:48`). Reusable maps
  `c.DbOracle.SINGER_TYPE_MAP` + `c.DbOracle.ENV_MAPPING`. There is **no reusable connection-config model** upstream
  — `m.DbOracle.ConnectionStatus` is runtime *status*, not config.

### The duplication / anti-patterns (verified, file:line)

1. **`connection_profile` returns a raw dict in every dbt-\* impl** and the base docstring literally says "returns dbt
   connection profile dict". This violates flext-law §1.2/§3a
   (structured data must be a Pydantic-2 model; JSON only at the edge). Blast radius (codegraph): the base is
   extended by `FlextDbtOracleServiceBase`, `FlextDbtLdapServiceBase`, `FlextDbtLdifServiceBase`,
   `FlextDbtOracleWmsServiceBase`; `connection_profile` has **zero real consumers** — safe to change.
2. **Each pilot re-declares the Oracle connection scalars** that `settings.DbOracle` already owns: dbt-oracle
   `_settings.py:34-40`; tap-oracle `_settings.py:33-37`; target-oracle `_settings.py:34-38`
   (and subclasses `FlextSettings` instead of `FlextMeltanoSettings` — base drift).
3. **Each pilot re-declares a connection-shaped model**: dbt-oracle `m.DbtOracle.OracleConnectionConfig`
   (`models.py:84`) + `DbtConnectionProfile` (`:145`); target-oracle `_models/settings.py:13`
   `OracleConnectionConfig` + `OracleConnectionModel`.
4. **tap-oracle bypasses its base entirely**: no `base.py`; `tap.py` hand-rolls discover/sync commands + `run_cli`
   (`:26/:91/:167/:220`) and `streams.py` hand-rolls `OracleStream/StreamFactory` (`:40/:268`) — ~586 LOC re-doing
   what `FlextMeltanoTapServiceBase` + meltano `singer_tap`/`singer_sdk` already give.
5. **target-oracle is 3211 src LOC** with an 861-line loader; it neuters the base by making `create_sink()` raise
   `TypeError` (`api.py:30-37`).

## Decision

Adopt the **Thin Domain Driver** contract for every `flext-(dbt|tap|target)-<domain>` project. Three layers, each with
one owner:

| Layer | Owner | Responsibility |
| --- | --- | --- |
| **Integration interfaces** (dbt/tap/target/singer machinery in FLEXT form) | `flext-meltano` | the 3 consumer bases + `c/t/p/m/u` for meltano; 100% domain-agnostic (never references oracle/ldap/…) |
| **Action library** (real connection + execution) | `flext-<domain>` (e.g. `flext-db-oracle`) | connection SSOT (`settings.<Domain>.*`), runtime API (`FlextDbOracleApi`), `p.<Domain>.Connection`, type/Singer maps |
| **Thin driver** | `flext-(dbt\\|tap\\|target)-{domain}` | implements ONLY the base's one abstract hook; reuses `c/t/p/m/u` from BOTH flext-meltano and the action library; declares no connection settings/models of its own |

### Rules (inviolable for these projects)

1. **A thin driver subclasses its meltano base and implements only the abstract hook** — dbt: `dbt_project_name` +
   `connection_profile`; tap: `tap_name` + `create_tap_instance`; target: `target_name` + `create_sink`. No
   hand-rolled CLI/commands/streams when the base already provides them.
2. **Connection settings come from the action library, never re-declared.** The driver reuses `settings.DbOracle.*`
   (or composes it by MRO). Delete every `oracle_*` scalar and every `OracleConnectionConfig`-shaped model in the
   drivers. Driver settings keep only domain-runtime knobs.
3. **`connection_profile` returns a typed model, not a dict, with no roundtrip.** Its declared type is a **protocol**
   `p.Meltano.DbtConnectionProfile` (minimal, domain-agnostic: `type` + `project` common members). Each driver
   returns its own concrete `m.<Ns>.…Profile` model **directly** — no field-by-field copy from settings, no
   `model_dump()`. The model is the value; the dict never appears.
4. **flext-meltano must never gain domain knowledge.** The protocol names only common members; oracle/ldap specifics
   stay in the domain driver + action library.
5. **Net LOC must be strongly negative** for every driver converted. No compat shims, no `old+new`.

### Uniform connection seam

`connection_profile` is currently dbt-only and dict-typed. Generalize the *type* (not the domain knowledge): add a
minimal protocol `p.Meltano.DbtConnectionProfile` (members `type: str` , `project: str` ) in flext-meltano; retype the
abstract property `def connection_profile(self) -> p.Meltano.DbtConnectionProfile` . Each dbt driver returns its own
`m.<Ns>.DbtConnectionProfile` model that adds the domain fields and structurally satisfies the protocol. tap/target keep
their factory seams ( `create_tap_instance` / `create_sink` ).

## Consequences

- **Positive:** every integration project collapses to a few dozen lines; connection facts have one home
  (`settings.DbOracle`); `connection_profile` becomes a typed model consistent with flext-law; flext-meltano stays a
  clean domain-agnostic hub; ~1000+ LOC deleted in the pilot; the pattern generalizes to all integration projects.
- **Negative / risk:** touching the flext-meltano dbt base changes a contract shared by 4 dbt consumers — must land
  base + all 4 in the **same batch** (flext-law §4B.4). target-oracle's 861-line loader is the largest, riskiest cut;
  staged behind its own acceptance gate.
- **Migration order (pilot):** (1) add `p.Meltano.DbtConnectionProfile` + retype the base; (2) dbt-oracle returns a
  direct model, delete its duplicated settings/model; (3) same for dbt-ldap/ldif/oracle-wms
  (same-batch consumers of the base); (4) tap-oracle gains a real base subclass, delete hand-rolled tap/streams; (5)
  target-oracle reuses `settings.DbOracle`, normalize its base, scope the loader cut separately. Each step: `uv run`
  per-file gate + `make check`/`make test` per project, net-LOC ≤ 0.

## Realized mechanism — Declarative tap (flext-tap-ldap pilot, 2026-07-17)

The tap pilot sharpened rule 1 into a **declarative** driver so the consumer declares data, never machinery. New
inviolable rules (bind every `flext-(tap|target|dbt)-*` ):

1. **Only `flext-meltano` imports `singer_sdk`/`dbt`.** Each `flext-<domain>` library imports its own external lib;
   integration projects import ONLY flext-* libraries.
2. **Consumers compose the base via `meltano.Tap` / `meltano.Target` / `meltano.Dbt`**
   (MRO facade `services/consumer_bases/facade.py`), never a private `consumer_bases` module import.
3. **A tap driver declares a `m.Meltano.TapSpec`** (tap_name + `config_jsonschema` from the settings model + a tuple of
   `m.Meltano.StreamSpec`) and a `p.Meltano.RecordFetcher`. `flext-meltano`
   (`services/declarative_tap.py` `FlextMeltanoDeclarativeTap.build`) turns that into a real `singer_sdk` tap with a
   WORKING flat Singer CLI. This fixed a fleet-wide bug: the old `cli_main` pre-built the tap with `config=None`,
   crashing `singer_sdk` before it parsed `--config`.
4. **Typed transport, packed once** — the consumer receives `m.Meltano.FetchRequest(stream_name, config)` and returns
   `p.Result[m.Meltano.FetchResult(records)]`. No dict/round-trip across the boundary; records stay in Singer-native
   `JsonMapping` (the wire shape).
5. **Layering law:** `services/*` import only `c,t,p,m,u` + `s` from `base.py`; helpers live in `_utilities/*`;
   `utilities.py` is an MRO of `_utilities/*` mixins + composed library facades; services are thin orchestrators.
   `base.py` `s = meltano-service-base` with the domain facade injected (`self.ldap`, algar-oud-mig pattern).
6. **Config/settings SSOT:** `config/` at PROJECT ROOT; `config.<Ns>.streams` typed via `_models/config.py`
   (`m.FrozenModel`, validated `cached_property`) = business rules; `settings.<Ns>.*` = every adjustable param
   (`.env`/env/local/CLI/API parametrize it), reusing the action library's `settings.<Domain>.*` by MRO. Console
   entry always `<pkg>.cli:main` → `Service().cli_main(args)`.

**Pilot result (flext-tap-ldap):** src 3276 → 914 LOC (−72%); deleted
`tap.py`/`client.py`/`streams.py`/`ldif_streams.py` + old `_utilities` mixins; real console
`tap-ldap --config X --discover` exit 0 emits a 4-stream catalog (was a production crash); e2e runs the real console
via the flext-cli SSOT runner (`u.Cli.capture`) with shared `c.Ldap.Tests.*` constants; 18 tests green. Commits:
flext-meltano `71ddd336`/`1ed51f5c`/`0eb11578`, flext-tap-ldap
`6cf7a75`/`714abc3`/`38829ba`/`0a47dac`/`9d68444`/`e2f8887`/`ebb47f3`.

## Evidence

Explore sessions `ses_0b2e45133ffe` (meltano bases), `ses_0b2dd6a1cffe` (flext-db-oracle surface), `ses_0b2dcd20fffe` (3
pilots inventory); codegraph blast-radius on `connection_profile` / `create_tap_instance` / `create_sink` (4 dbt
extenders, 0 real `connection_profile` consumers). Tap declarative pilot verified 2026-07-17: real console exit 0 + 18
tests green (see commits above).
