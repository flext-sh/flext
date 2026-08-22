---
name: using-flext-meltano
description: >-
  Build FLEXT Singer tap/target and dbt integration projects as thin declarative
  drivers over flext-meltano. Use when creating or refactoring any
  flext-(tap|target|dbt)-* project, wiring config/settings SSOT, the CLI, or the
  record/connection transport. DO NOT USE FOR flext-meltano internals or
  non-integration projects.
---

# Using flext-meltano (Singer/dbt consumer pattern)

**UTILITY SKILL.** Canonical, minimal, no-ceremony pattern for every
`flext-(tap|target|dbt)-<domain>` project. Realizes ADR-006.

## Inviolable boundaries

- ONLY `flext-meltano` imports `singer_sdk` / `dbt`. Each `flext-<domain>`
  library imports its own external lib. Integration projects import ONLY
  flext-* libraries.
- `services/*` import ONLY `c, t, p, m, u` + `s` (from `base.py`). Services are
  thin orchestrators; helpers live in `_utilities/*`.
- `utilities.py` = MRO of the project's `_utilities/*` mixins + composed library
  facades (flext-meltano `u`, `Flext<Domain>Utilities`). Same MRO rule for
  `c/t/p/m/u`. Reuse composed-project `c/t/p/m/u` (incl. flext-core/flext-cli).
- ONE top-level class per module; nothing declared at module level.
- Compose via MRO / class inheritance, never assignment.

## Canonical files

| File | Content |
|---|---|
| `base.py` | `class Flext<Ns>ServiceBase(...)`; choose `meltano.Tap`, `meltano.Target`, or `meltano.Dbt` as the parent, inject the domain facade as `self.<domain>` (PrivateAttr + `@property`), and set `s = Flext<Ns>ServiceBase`. |
| `api.py` | thin `Flext<Ns>Service(meltano.Tap)`; `create_tap_instance` -> `self.build_declarative_tap(u.<Ns>.tap_spec(), Flext<Ns>ExtractService())`. |
| `cli.py` | `def main(args=None) -> int: return Flext<Ns>Service().cli_main(args)`. Console entry `<pkg>.cli:main`. |
| `services/extract.py` | thin `RecordFetcher`: `fetch(m.Meltano.FetchRequest) -> r[m.Meltano.FetchResult]` — connect, search, `u.<Ns>.pack_entries`. |
| `_utilities/extract_support.py` | `u.<Ns>.tap_spec()` (from config streams + settings schema), `u.<Ns>.pack_entries()`, search/connection builders. |
| `_models/config.py` | typed `m.FrozenModel` business-rule shapes; `Root.<Ns>` validated in `_config.py` via `cached_property`. |
| `config/<pkg>.yaml` | at PROJECT ROOT; business rules (streams: name/filter/primary_keys/attributes/schema). |
| `_settings.py` | only tap-specific adjustable params; connection reuses the action library `settings.<Domain>.*` by MRO. |

## Declarative tap (flext-meltano surface)

```python
from flext_meltano import m, meltano

spec = m.Meltano.TapSpec(
    tap_name="tap-x",
    config_jsonschema=type(settings).model_json_schema(),
    streams=(
        m.Meltano.StreamSpec(name="users", json_schema={...}, primary_keys=("dn",)),
    ),
)
# consumer implements p.Meltano.RecordFetcher.fetch(request) -> r[FetchResult]
instance = FlextMeltanoDeclarativeTap.build(
    spec, fetcher
)  # or self.build_declarative_tap(...)
```

- `p.Meltano.RecordFetcher.fetch(m.Meltano.FetchRequest) -> p.Result[m.Meltano.FetchResult]`
  — typed transport, packed once, no round-trips. Records stay Singer-native.
- `meltano.Tap` / `meltano.Target` / `meltano.Dbt` are the composition bases.

## Config / settings SSOT

- `from <ns> import config, settings` then `config.<Ns>.*` (business rules) /
  `settings.<Ns>.*` (adjustable params: `.env` / env / local / CLI / API).
- `config/` at project ROOT; `CONFIG_DIR: ClassVar[str] = "config"` on the config
  class resets an ancestor's absolute override so the loader anchors to this
  project's own root (avoids loading the wrong package's config).

## Tests

- Exercise the REAL console via the flext-cli SSOT runner:
  `u.Cli.capture([c.<Domain>.Tests.CONSOLE_SCRIPT, "--config", str(path), "--discover"])`.
- All fixed data from shared `c.<Domain>.Tests.*` constants; parse JSON with
  `t.Cli.JSON_MAPPING_ADAPTER` / `JSON_LIST_ADAPTER`. No mocks, one nested class.

## Validation

```bash
env -u PYTHONPATH uv run --no-sync ruff check <file>
env -u PYTHONPATH uv run --no-sync pyrefly check <file>
env -u PYTHONPATH uv run --no-sync pytest tests/ --no-cov -p no:cacheprovider -q
```

Never `uv sync --reinstall-package` from a member dir — it destroys the shared
`.venv` editables/metadata. Repair from workspace ROOT with `uv sync --all-packages`.

## References

- `docs/architecture/adr/006-thin-domain-drivers-over-meltano-bases.md`
- `docs/architecture/adr/005-config-settings-constants-templates-schemas-ssot.md`
- Pilot: `flext-tap-ldap` (src -72% LOC, real-console e2e green).
