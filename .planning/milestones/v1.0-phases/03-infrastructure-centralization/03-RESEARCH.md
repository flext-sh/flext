# Phase 3: Infrastructure Centralization - Research

**Researched:** 2026-03-24
**Domain:** Python monorepo infrastructure centralization + workaround eradication
**Confidence:** HIGH

## Summary

Phase 3 has two work streams: INFRA (centralize runtime helpers) and WA (eradicate antipatterns). Research reveals that significant prior work from sisyphus plans has already been completed — `run_cli()`, `exit_code()`, CLI standardization, `apply_changes` normalization, and the `dry_run=cli.apply` bug are all done. The remaining INFRA work is: `emit()` and `iter_projects()` utilities, `workspace_root` parameter normalization (replacing `root: Path` in ~20 service methods), `NamespaceSourceDetector` (model + detector exist, needs test suite + workspace-wide application), and the `make pyre` policy gate enhancement.

For workaround eradication, current violation counts are significantly lower than sisyphus plan estimates: `except ImportError` = 3 (all in flext-tests), `model_rebuild()` = 7 (all in tests), `except Exception:` = 0 in production, `sys.exit()` outside `__main__` = 2 (flext-quality tools), `print()` in production = 52 instances across 20 files, `subprocess.run()` direct = 5 outside wrapper. The `print()` count is the largest effort — many are legitimate CLI/logging output that need case-by-case analysis.

**Primary recommendation:** Split into 3-4 GSD plans: (1) remaining INFRA utilities + parameter normalization, (2) NamespaceSourceDetector test suite + workspace application, (3) workaround eradication sweep, (4) policy gate + final verification.

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** INFRA stream first (01-05), then WA stream (01-06)
- **D-02:** Within INFRA: foundation utilities first, then normalization, then new tooling, then policy gate
- **D-03:** Within WA: dependency order — flext-core -> flext-infra -> flext-tests -> consumers
- **D-04:** `u.Infra.run_cli(main_fn)` centralizes bootstrap + dispatch + error-to-exit (ALREADY DONE)
- **D-05:** `u.Infra.iter_projects(cli)` centralizes project discovery + filtering + iteration
- **D-06:** CLI args standardized: `--workspace PATH`, `--dry-run`/`--apply`, `--format json|text`, `--check`, `--projects NAME` (ALREADY DONE)
- **D-07:** Fix known bug: `release/__main__.py:143` has `dry_run=cli.apply` (ALREADY DONE)
- **D-08:** `workspace_root` is the canonical parameter name
- **D-09:** `NamespaceSourceDetector` in `flext_infra` with own test suite
- **D-10:** `make pyrefly-repo` policy gate enforces 0 `Any`/`object`/`ignore` violations
- **D-11:** `try/except ImportError` -> `importlib.util.find_spec()` feature flags
- **D-12:** `model_rebuild()` zero everywhere
- **D-13:** `bare except Exception:` -> specific exception types
- **D-14:** `sys.exit()` zero outside `__main__.py`
- **D-15:** `print()` zero in production except documented CLI output services
- **D-16:** `subprocess.run()` zero direct calls outside designated wrapper

### Claude's Discretion

- Internal decomposition of centralized utilities
- Whether to batch WA categories into one plan per category or per project
- Exact exception type hierarchy for WA-03 replacements
- NamespaceSourceDetector internal architecture

### Deferred Ideas (OUT OF SCOPE)

None
</user_constraints>

<phase_requirements>

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| INFRA-01 | `u.Infra.run_cli()` centralizes bootstrap (eliminates 18 patterns) | ALREADY DONE — `run_cli` exists in `_utilities/cli.py:340`, all `__main__.py` files already use it |
| INFRA-02 | `u.Infra.iter_projects()` centralizes project iteration (eliminates 13 clones) | PARTIALLY DONE — need to verify `iter_projects` exists and all callers migrated |
| INFRA-03 | `workspace_root` canonical parameter name | ~20 `root: Path` params remain in service interfaces; ~20+ `project_root` params exist (many are semantically correct for project dirs) |
| INFRA-04 | `NamespaceSourceDetector` + auto-fixer live with test suite | Detector exists in 6 files; needs test suite verification and workspace-wide application |
| INFRA-05 | `make pyre` policy gate enforces 0 violations | `make pyre` target exists (Makefile:796); needs enhancement for file+line output on failure |
| WA-01 | Zero `try/except ImportError` in production | 3 instances in flext-tests/src (not production per se — tests infrastructure) |
| WA-02 | Zero `model_rebuild()` anywhere | 7 instances in 2 test files (flext-core/tests, flext-ldif/tests) |
| WA-03 | Zero bare `except Exception:` | 0 in production src/ — ALREADY DONE |
| WA-04 | Zero `sys.exit()` outside `__main__.py` | 2 real violations in flext-quality tools (style_validator.py, content_analyzer.py) |
| WA-05 | Zero `print()` in production | 52 instances across 20 files — largest effort, needs case-by-case triage |
| WA-06 | Zero `subprocess.run()` outside wrapper | 5 instances outside wrapper (flext-meltano, flext-quality, gruponos, workspace_makefile) |
</phase_requirements>

## Standard Stack

No new libraries needed. All work uses existing codebase infrastructure:

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| libcst | >=1.5.1 | CST-based code transformations | Already in flext-infra for NamespaceSourceDetector |
| ast (stdlib) | 3.13 | AST parsing for detection | Standard Python |
| importlib.util (stdlib) | 3.13 | `find_spec()` for feature flags | Replaces `try/except ImportError` per D-11 |
| structlog | >=25.4 | Logging replacement for `print()` | Existing `FlextLogger` abstraction |

## Architecture Patterns

### Pattern 1: Centralized CLI Utility (ALREADY ESTABLISHED)

`FlextInfraUtilitiesCli` in `_utilities/cli.py` provides `run_cli()`, `exit_code()`, `create_parser()`, `resolve()`, `CliArgs` Pydantic model. All `__main__.py` files already use this.

### Pattern 2: Parameter Normalization via LSP Rename

For INFRA-03, use `findReferences` to trace each `root: Path` to call sites. Only rename where the parameter receives `cli.workspace` (workspace root). `project_root: Path` that correctly refers to a project directory stays as-is.

### Pattern 3: Workaround Fix Patterns

```python
# WA-01: try/except ImportError -> feature flag
import importlib.util

HAS_PYTEST = importlib.util.find_spec("pytest") is not None

# WA-04: sys.exit() outside __main__ -> raise or return
# BEFORE: sys.exit(1)
# AFTER: raise SystemExit(1)  # or return r.fail("description")

# WA-05: print() -> FlextLogger or output.*
# BEFORE: print(f"Processing {name}")
# AFTER: output.info(f"Processing {name}")

# WA-06: subprocess.run() -> u.Infra.run_raw() or u.Infra.run_checked()
# BEFORE: subprocess.run(["cmd", "arg"], capture_output=True)
# AFTER: u.Infra.run_raw(["cmd", "arg"])
```

### Anti-Patterns to Avoid

- **Blanket print->logger conversion**: Some `print()` calls are intentional CLI output (e.g., `flext-cli/src/flext_cli/services/output.py`). Document exemptions.
- **Renaming `project_root` that means project dir**: Only rename where it actually receives workspace root.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CLI argument parsing | Manual argparse per `__main__` | `u.Infra.create_parser()` + `u.Infra.resolve()` | Already centralized |
| Project discovery | `discover_projects()` clones | `u.Infra.iter_projects()` | Centralized wrapper |
| Subprocess execution | Direct `subprocess.run()` | `u.Infra.run_raw()` / `u.Infra.run_checked()` | Error handling, typing |
| JSON/text output switching | Inline if/else branching | `u.Infra.emit()` (to be created) | Standardized format switching |

## Current Violation Baseline (2026-03-24)

| Category | Req | Count | Files | Notes |
|----------|-----|-------|-------|-------|
| `except ImportError` | WA-01 | 3 | flext-tests/src (3 files) | Test infrastructure, not production |
| `model_rebuild()` | WA-02 | 7 | flext-core/tests (6), flext-ldif/tests (1) | All in test code |
| `except Exception:` | WA-03 | 0 | — | ALREADY DONE in production |
| `sys.exit()` outside `__main__` | WA-04 | 2 | flext-quality tools (2 files) | style_validator.py, content_analyzer.py |
| `print()` in production | WA-05 | 52 | 20 files | Needs triage: legitimate CLI output vs violations |
| `subprocess.run()` direct | WA-06 | 5 | 4 files (excl. wrapper) | flext-meltano, flext-quality, gruponos, workspace_makefile |
| `root: Path` (not `workspace_root`) | INFRA-03 | ~20 | Service interfaces in docs, release, git, etc. | Many `project_root` are semantically correct |
| `apply_changes=` | — | 0 | — | ALREADY DONE |

## Common Pitfalls

### Pitfall 1: print() False Positives

**What goes wrong:** Blindly replacing all `print()` breaks intentional CLI output.
**Why it happens:** Some modules (flext-cli output service, terminal utilities) use `print()` as their documented output mechanism.
**How to avoid:** Triage each `print()` instance. Document exemptions with `# CLI output` comments. Only replace non-CLI `print()` with `FlextLogger` or `output.*`.
**Warning signs:** Tests fail after print replacement; CLI commands produce no visible output.

### Pitfall 2: project_root vs workspace_root Confusion

**What goes wrong:** Renaming `project_root` that correctly refers to a specific project directory.
**Why it happens:** Both `root` and `project_root` are used for workspace root AND project root in different contexts.
**How to avoid:** Trace each parameter to its call site via LSP. Only rename when call site passes `cli.workspace`.

### Pitfall 3: flext-tests except ImportError

**What goes wrong:** The 3 `except ImportError` in flext-tests/src are test infrastructure that probes optional deps.
**Why it happens:** Test validator needs to check if packages are importable.
**How to avoid:** These may need `importlib.util.find_spec()` replacement per D-11, but verify the semantic context.

## Code Examples

### emit() Implementation Pattern (to be created)

```python
# In _utilities/cli.py, add to FlextInfraUtilitiesCli:
@staticmethod
def emit(
    data: BaseModel | t.ScalarMapping,
    *,
    text_fn: Callable[..., str] | None = None,
    cli: FlextInfraUtilitiesCli.CliArgs,
) -> None:
    if cli.output_format == "json":
        if isinstance(data, BaseModel):
            sys.stdout.write(data.model_dump_json())
        else:
            sys.stdout.write(orjson.dumps(data).decode())
        sys.stdout.write("\n")
    elif text_fn is not None:
        output.write(text_fn(data))
    else:
        output.write(str(data))
```

### iter_projects() Implementation Pattern (to be created)

```python
@staticmethod
def iter_projects(
    cli: FlextInfraUtilitiesCli.CliArgs,
) -> p.Result[list[m.Infra.Workspace.ProjectInfo]]:
    result = FlextInfraUtilitiesDiscovery.discover_projects(cli.workspace)
    if result.is_failure:
        return result
    projects = result.value
    filter_names = cli.project_names()
    if filter_names is not None:
        projects = [p for p in projects if p.name in filter_names]
    return r[list[m.Infra.Workspace.ProjectInfo]].ok(sorted(projects))
```

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.4+ |
| Settings file | `pyproject.toml` [tool.pytest.ini_options] |
| Quick run command | `make test PROJECT=flext-infra` |
| Full suite command | `make test` |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INFRA-01 | run_cli centralizes bootstrap | smoke | `python -c "from flext_infra import u; u.Infra.run_cli(lambda _: 0)"` | N/A (runtime check) |
| INFRA-02 | iter_projects wraps discovery | unit | `make test PROJECT=flext-infra` | Wave 0 |
| INFRA-03 | workspace_root canonical | grep | `sg --pattern 'def $FN($$$, root: Path, $$$)' --lang py flext-infra/src/` | N/A (static check) |
| INFRA-04 | NamespaceSourceDetector + tests | unit | `make test PROJECT=flext-infra` | Partially exists |
| INFRA-05 | make pyre policy gate | smoke | `make pyre` | Exists |
| WA-01 | Zero except ImportError | grep | Grep sweep | N/A (static check) |
| WA-02 | Zero model_rebuild | grep | Grep sweep | N/A (static check) |
| WA-03 | Zero bare except Exception | grep | Grep sweep | ALREADY DONE |
| WA-04 | Zero sys.exit outside **main** | grep | Grep sweep | N/A (static check) |
| WA-05 | Zero print in production | grep | Grep sweep | N/A (static check) |
| WA-06 | Zero subprocess.run direct | grep | Grep sweep | N/A (static check) |

### Sampling Rate

- **Per task commit:** `make check PROJECT=flext-infra` (or affected project)
- **Per wave merge:** `make check` + grep sweeps for zero-violation
- **Phase gate:** Full grep sweep + `make pyre` + `make check PROJECT=flext-core`

### Wave 0 Gaps

- [ ] `flext-infra/tests/unit/test_iter_projects.py` — covers INFRA-02
- [ ] `flext-infra/tests/unit/test_emit.py` — covers new emit utility
- [ ] NamespaceSourceDetector test suite verification — covers INFRA-04

## Already Completed (from prior sisyphus work)

The following are DONE and should NOT be re-planned:

| Item | Evidence |
|------|----------|
| `u.Infra.run_cli()` | Exists at `_utilities/cli.py:340` |
| `u.Infra.exit_code()` | Exists at `_utilities/cli.py:360` |
| CLI standardization (`--workspace`, `--dry-run`/`--apply`) | All 11+ `__main__.py` use `u.Infra.create_parser()` |
| `u.ensure_structlog_configured()` removed from `__main__` | 0 grep matches |
| `apply_changes=` normalization | 0 grep matches |
| `dry_run=cli.apply` bug fix | 0 grep matches |
| `except Exception:` in production | 0 grep matches in `*/src/` |
| NamespaceSourceDetector class | Exists in 6 flext-infra files |

## Remaining Work Summary

### INFRA Stream

1. **emit() + iter_projects()** — Create 2 new utility methods in `_utilities/cli.py`
2. **workspace_root normalization** — Rename ~20 `root: Path` params in service interfaces (docs, release, git utils, validate, refactor)
3. **NamespaceSourceDetector test suite** — Verify/create tests, run workspace-wide
4. **make pyre policy gate** — Enhance to enforce 0 violations with file+line output

### WA Stream

1. **WA-01**: 3 `except ImportError` in flext-tests/src -> `find_spec()` flags
2. **WA-02**: 7 `model_rebuild()` in test files -> restructure forward refs
3. **WA-04**: 2 `sys.exit()` in flext-quality tools -> `raise SystemExit()` or `return r.fail()`
4. **WA-05**: 52 `print()` instances -> triage + replace with logger/output (LARGEST EFFORT)
5. **WA-06**: 5 `subprocess.run()` direct -> route through `u.Infra.run_raw()`/`run_checked()`

## Open Questions

1. **print() exemptions**
   - What we know: flext-cli output service uses print intentionally; some print calls are in CLI tools
   - What's unclear: Exact list of exempted files/modules
   - Recommendation: Triage during execution, document exemptions with inline comments

2. **NamespaceSourceDetector test suite status**
   - What we know: Detector class exists in 6 files
   - What's unclear: Whether dedicated tests exist, if workspace-wide application completed
   - Recommendation: Check during plan execution; create tests if missing

## Sources

### Primary (HIGH confidence)

- Codebase grep sweeps — current violation counts (2026-03-24)
- `.sisyphus/plans/infra-runtime-centralization.md` — completed tasks verified via grep
- `.sisyphus/plans/workaround-eradication.md` — root cause matrix and fix patterns
- `.sisyphus/plans/cli-infra-standardization.md` — CLI centralization (completed)
- `.sisyphus/plans/namespace-source-enforcement.md` — NamespaceSourceDetector design
- `flext-infra/src/flext_infra/_utilities/cli.py` — existing run_cli/exit_code implementation

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH - no new libraries, all existing infra
- Architecture: HIGH - patterns established by completed sisyphus work
- Pitfalls: HIGH - based on actual codebase grep analysis
- Violation counts: HIGH - fresh grep baseline from today

**Research date:** 2026-03-24
**Valid until:** 2026-04-07 (code changes rapidly)
