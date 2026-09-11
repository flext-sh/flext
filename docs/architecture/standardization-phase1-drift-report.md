# Standardization Phase 1 — Drift Audit Report (zero-writes)

Owner: ADR-010 · Bead `mro-377y.1` · Target line `0.20.0-dev`.
This is a read-only drift report. No source was modified to produce it.

## Method

Presence/shape audit across all FLEXT members and the external/standalone
applications, checking the ADR-010 standard: managed files
(`Makefile`/`pyproject.toml`/`.mise.toml`/`.python-version`/`custom.mk`/`.envrc`),
facade modules (`constants`/`typings`/`protocols`/`models`/`utilities` +
`api`/`base` + `_settings`/`_config`), settings/config exposure convention, and
class-prefix naming. `flext-infra codegen conform --mode check` is the canonical
apply-time gate; this report is the human-readable inventory that feeds Phase 2.

## Finding 1 — `.python-version` missing on ~10 FLEXT members

Present on most members but absent on: `flext-dbt-ldap`, `flext-dbt-ldif`,
`flext-ldap`, `flext-meltano`, `flext-tap-ldap`, `flext-tap-oracle`,
`flext-tap-oracle-oic`, `flext-tap-oracle-wms`, `flext-target-oracle-wms`,
`flext-web`. Toolchain SSOT (`codegen.yaml`) pins Python `3.13`; the file should
be rendered uniformly. Severity: low (mise pins Python anyway), but it is
managed-file drift that `conform --mode apply` should close.

## Finding 2 — settings/config exposure convention split

Canonical FLEXT pattern (core/cli/api/dcdoc): private `_settings.py`/`_config.py`
re-exported through `**init**` as `settings`/`config`.

Divergences:

- **dataop** uses a public `dataop/settings.py` (plus a `_settings/` package) and
  exports `DataopSettings`. Drift: public settings module instead of `_settings`,
  and class prefix `Dataop*` instead of the project's `DataOP*` namespace.
- **dc_backup** uses a public `dc_backup/settings.py`; no `_settings.py`/
  `_config.py` private modules.

Severity: medium. This is exactly the surface ADR-010 §3/§3a standardizes; it
also affects the XDG settings-directory contract (consumers must reach dirs via
the canonical `settings` singleton).

## Finding 3 — dc_backup structural drift (highest)

`dc_backup` top-level exposes only `api.py`/`base.py`/`settings.py`. Missing
facade modules: `constants`/`typings`/`protocols`/`models`/`utilities`/`config`
(`c/t/p/m/u`). Its domain lives under `domain/`, `application/`, `adapters/`,
`composition/` (clean-architecture layout) rather than the FLEXT facade layout.
The `dcb` package is a documented compat shim.

Severity: high for standardization. dc_backup needs the largest Phase 2
migration to the canonical facade structure, or an explicit ADR-recorded
exception if its ports-and-adapters layout is intentionally retained.

## Finding 4 — external/standalone managed-file gaps

- `config/workspace.yaml` absent in all three external apps — expected: they are
  standalone, not workspace roots. `conform --scope self` currently errors
  because it expects a workspace manifest. Phase 2 must run these through the
  `standalone` profile (ADR-003/010), not the member path.
- `custom.mk` absent in dataop and dc_backup; present in dcdoc and all FLEXT
  members.
- `.python-version` absent in dcdoc and dataop; present in dc_backup.
- `.envrc` absent in dataop.

Severity: medium. These are standalone-profile managed-file gaps.

## Finding 5 — class-prefix naming

- dcdoc: `Dcdoc<Verb>Service` — consistent.
- dataop: mixed `DataOP<Concern>` (facades) vs `Dataop*` (settings) — inconsistent
  casing for the same project namespace.
- dc_backup: `DcBackup<Concern>` — consistent within its layout.

Severity: low-medium. One casing per namespace is the rule; dataop settings is
the outlier.

## Phase 2 input (ordered, deletion-first, no writes here)

1. Render missing `.python-version` on the ~10 members via `conform --mode apply`.
2. Normalize dataop settings to the private `_settings`/`_config` convention and
   `DataOP*` class prefix; keep the XDG dirs reached through the `settings`
   singleton (ADR-010 §3a).
3. Decide dc_backup: migrate to facade layout, or record an explicit ADR
   exception for its ports-and-adapters structure. This is the largest item.
4. Run the three external apps through the `standalone` profile; add missing
   `custom.mk`/`.envrc`/`.python-version`.
5. Add the settings-directory enforcement rule (Bead `mro-377y.6`) only after the
   convention is uniform.

## Verification of this report

- Read-only: `git status` in each repo shows no change caused by this audit.
- Presence matrix reproduced by the inventory commands recorded in Bead
  `mro-377y.1` notes.

## Addendum — settings `*_dir` audit (Bead mro-377y.6, read-only)

Scanned `src/` of flext-core, flext-cli, flext-infra, flext-tests, cosmos-docgen,
dataop, dc_backup (309/…/145 py files). Findings:

- No project derives XDG paths ad-hoc (`Path.home()`, `os.environ["XDG_*"]`,
  `~/.cache`, `expanduser`) in `src/` — zero hits. Good baseline.
- However, each project defines its OWN directory fields instead of consuming the
  root-singleton `settings.*_dir` contract (ADR-010 §3a):
  - **dataop** `WorkspaceSettings`: own `data_dir`, `workspace_root`,
    `state_root`, `temp_dir`, plus `ClickHouseSettings.user_files_path` — own
    derivation, not the root-singleton `*_dir`.
  - **dc_backup** `DcBackupSettings`: `workspace_root = Path.cwd()` and
    `backup_root = workspace_root/"backup"` — derives from CWD, not from the
    XDG root-singleton namespace.
  - **dcdoc**: own runtime settings; does not consume `settings.*_dir`.

### Phase 2/3 input for mro-377y.6

1. Blocked on the flext-core kernel `*_dir` root-singleton binding (mro-377y.7,
   owned by the flext-core lane).
2. After the kernel lands: migrate dataop/dc_backup/dcdoc directory resolution to
   consume `settings.cache_dir/work_dir/data_dir/config_dir/state_dir/runtime_dir`
   from the root singleton; keep only genuinely domain-specific sub-paths
   (e.g. iceberg namespace, backup subtree) as suffixes under those roots.
3. Enforcement rule (mro-377y.3/.6): fail `check`/`val` on any `src/` directory
   field or path derivation that bypasses the root-singleton `*_dir`.
