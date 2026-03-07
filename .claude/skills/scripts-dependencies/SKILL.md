<!-- TOC START -->

- [Scope](#scope)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
- [Workflow](#workflow)
- [Examples](#examples)
- [Verification](#verification)
- [Scripts](#scripts)
- [Runtime vs dev dependency detection (automatic)](#runtime-vs-dev-dependency-detection-automatic)
- [Typing libraries (types-\*) and dependency limits](#typing-libraries-types-and-dependency-limits)
<!-- TOC END -->

---

name: scripts-dependencies
description: Dependency management — analysis, consolidation, discovery, caching, and synchronization. Use when editing scripts/dependencies/ or using flext_infra.deps.

---

# Scripts Dependencies

## Scope

- `flext_infra.deps` module — Dependency management services (Python module in flext-core)
  - `flext_infra.deps.modernizer.PyprojectModernizer`
  - `flext_infra.deps.detection.DependencyDetector`
  - `flext_infra.deps.detector.RuntimeDevDetector`
  - `flext_infra.deps.internal_sync.InternalDepsSyncer`
  - `flext_infra.deps.extra_paths.ExtraPathsSyncer`
  - `flext_infra.deps.path_sync.DepPathSyncer`
- Legacy scripts (deprecated):
  - `scripts/dependencies/` directory (being migrated to flext_infra.deps)

## References

- `AGENTS.md` — canonical governance source
- `flext-core/src/flext_infra/deps/` — Module source
- `.claude/skills/rules-scripts/SKILL.md`
- `Makefile` (upgrade, typings)

## Rules

- Dependency scripts must not modify lockfiles without explicit `--apply` flag.
- Dependency/typing reports go to `.reports/dependencies/` (e.g. `detect-runtime-dev-latest.json`).
- All scripts must be runnable from repo root.
- `modernize_pyproject.py --audit` is enforced by `make validate VALIDATE_SCOPE=workspace` and must stay clean.

## Instructions

- When adding dependency analysis, follow the pattern in `analyze_dependencies.py`.
- When modifying sync logic, ensure idempotency.
- Use `flext_infra.discovery.DiscoveryService` for project enumeration.

## Workflow

1. Identify the dependency concern (missing, outdated, conflicting).
2. Create or modify the script under `scripts/dependencies/`.
3. Test with `--help` and dry-run mode.
4. Verify script compiles: `python -m compileall scripts/dependencies`.
5. Run standard gates: `make check PROJECT=<name>` and `make validate PROJECT=<name>`.

## Examples

Good (primary — Make verbs for standard workflow):

```bash
make setup                          # install all project dependencies
make setup PROJECT=flext-core       # install single project
make upgrade                        # upgrade deps + dependency report (use DEPS_REPORT=0 to skip report)
make typings PROJECT=flext-core     # stub supply-chain + typing report (use DEPS_REPORT=0 to skip report)
make check PROJECT=flext-core      # verify after dependency changes
```

Good (internal — dependency analysis scripts):

```bash
python scripts/dependencies/analyze_dependencies.py --output .reports/scripts-dependencies--json--analysis-latest.json
```

Why good: Make verbs for standard workflow; artifact naming and structured output for detailed analysis.

Bad:

```bash
pip install --upgrade $(cat requirements.txt)
```

Why bad: No analysis, no structured output, destructive.

## Verification

Make gates (primary):

- `make setup PROJECT=flext-core` — verify dependency installation
- `make upgrade` / `make typings` — produce dependency/typing report (or `DEPS_REPORT=0` to skip)
- `make check PROJECT=flext-core` — lint + format + type + security gates
- `make validate PROJECT=flext-core` — complexity + docstring gates

Script-level checks (internal):

- `python -m compileall scripts/dependencies`
- `python scripts/dependencies/analyze_dependencies.py --help`
- `rg "Owner-Skill:.*scripts-dependencies" scripts/dependencies`

## Scripts

| Path                                               | Purpose                                                  | Invocation                                                                                                |
| -------------------------------------------------- | -------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `scripts/dependencies/__init__.py`                 | Package marker                                           | —                                                                                                         |
| `scripts/dependencies/analyze_dependencies.py`     | Analyze project dependencies                             | `python scripts/dependencies/analyze_dependencies.py`                                                     |
| `scripts/dependencies/consolidate_dependencies.py` | Consolidate duplicate dependencies                       | `python scripts/dependencies/consolidate_dependencies.py`                                                 |
| `scripts/dependencies/dependency_cache.py`         | Dependency caching utilities                             | `python scripts/dependencies/dependency_cache.py`                                                         |
| `scripts/dependencies/dependency_detection.py`     | Helpers: deptry + pip check, discover_projects, classify | Imported by detect_runtime_dev_deps                                                                       |
| `scripts/dependencies/detect_runtime_dev_deps.py`  | Detect runtime vs dev deps (deptry + pip check)          | Invoked by `make upgrade` and `make typings`; or `python scripts/dependencies/detect_runtime_dev_deps.py` |
| `scripts/dependencies/discover_missing_deps.py`    | Discover missing dependencies                            | `python scripts/dependencies/discover_missing_deps.py`                                                    |
| `scripts/dependencies/sync_dependencies.py`        | Sync dependencies across projects                        | `python scripts/dependencies/sync_dependencies.py`                                                        |

## Runtime vs dev dependency detection (automatic)

- **make upgrade** — After a successful upgrade, runs `detect_runtime_dev_deps.py -q --no-fail` and writes `.reports/dependencies/detect-runtime-dev-latest.json`. Use **DEPS_REPORT=0** to skip this step.
- **make typings** — Runs `stub_supply_chain.py` (with PROJECT/PROJECTS/--all), then runs `detect_runtime_dev_deps.py --typings -q --no-fail` and writes the same report (including typings). Use **DEPS_REPORT=0** to skip the report step.
- No separate `deps-detect` or `deps-detect-report` targets; dependency and typing reports are produced automatically by these Make verbs.

## Typing libraries (types-\*) and dependency limits

- **dependency_limits.toml** — Config under `scripts/dependencies/` to constrain dependency and typing maintenance:
  - `[python].version`: e.g. `">=3.13,<3.15"`; used when suggesting/updating deps.
  - `[limits]`: optional version caps per package (e.g. `django = ">=4,<6"`).
  - `[typing_libraries].exclude`: list of packages to never auto-add as typings.
  - `[typing_libraries.module_to_package]`: override importable module name -> types-\* PyPI name (e.g. `yaml = "types-pyyaml"`).
- **Typing detection** — Uses mypy output ("Library stubs not installed for X", "Hint: pip install Y") to infer required types-_ packages; maps module names to PyPI names via defaults and dependency*limits.toml. Internal modules (`flext*_`, `flext*\*`, `flext*\*`) are never suggested as typings.
- **detect_runtime_dev_deps.py**:
  - `--typings` — Run mypy stub detection per project; add to report `projects.<name>.typings` (required_packages, to_add, current, limits_applied, python_version).
  - `--apply-typings` — Add missing typings to each project (`poetry add --group typings <pkg>`). Implies `--typings`. Use `--dry-run` to only report.
  - `--limits FILE` — Path to dependency_limits.toml (default: `scripts/dependencies/dependency_limits.toml`).
- Keeping typings updated: use **make typings** (optionally **PROJECT=…** or **PROJECTS="…"**); the report is written automatically. For applying typings, run the script directly with `--typings --apply-typings` after review; use `dependency_limits.toml` to cap Python or package versions.
