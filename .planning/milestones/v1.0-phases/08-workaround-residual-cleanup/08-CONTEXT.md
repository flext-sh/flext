# Phase 8: Workaround Residual Cleanup - Context

**Gathered:** 2026-03-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Eliminate all residual workaround violations found by v1.0 milestone audit: bare `except Exception:` handlers, `sys.exit()` outside `__main__.py`, and `print()` in production code. This is a gap closure phase — Phase 3 claimed these were done but the audit found residuals.

</domain>

<decisions>
## Implementation Decisions

## Exception Specificity (WA-03)

- **D-01:** Replace each bare `except Exception:` with the most specific exception type for its context (e.g., `OSError`, `ValueError`, `KeyError`, `oracledb.Error`, `RuntimeError`)
- **D-02:** In `src/` production code: zero tolerance — every handler must catch a specific type
- **D-03:** In `tests/`: bare `except Exception:` is acceptable ONLY in test helper utilities that genuinely need to catch anything (e.g., `conftest_factory.py` cleanup). All others must be specific.
- **D-04:** In `examples/` and `docs/`: lower priority, fix if trivial, defer if complex
- **D-05:** In `.claude/skills/` validation scripts: out of scope (not production code)

### sys.exit Refactoring (WA-04)

- **D-06:** `sys.exit()` is ONLY permitted inside `__main__.py` files (the `if __name__ == "__main__":` block)
- **D-07:** Non-`__main__` files with `sys.exit()` (e.g., `extra_paths.py`, `path_sync.py`, `target_refactored.py`, `cli.py`) must be refactored: the function returns an int exit code, and the `__main__.py` caller wraps it with `sys.exit()`
- **D-08:** Files that ARE `__main__.py` but have `sys.exit()` in unusual positions are fine — that's the intended pattern

### print Replacement (WA-05)

- **D-09:** `scheduled_maintenance.py:590` — replace `print(message)` with `FlextLogger` or the project's logging abstraction
- **D-10:** The `docs/maintenance/` copy at line 652 — same treatment if it's production code, skip if it's documentation-only

### Claude's Discretion

- Exact exception types per call site (researcher will catalog each)
- Whether `cli.py` files need a separate `__main__.py` or can use `if __name__ == "__main__":` guard inline

</decisions>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Workaround policy

- `AGENTS.md` — §Workaround Eradication rules (WA-01 through WA-06)
- `.planning/v1.0-MILESTONE-AUDIT.md` — Audit findings with exact violation counts and file locations

### Prior phase work

- `.planning/phases/03-infrastructure-centralization/03-03-PLAN.md` — Original WA-03/WA-04 plan
- `.planning/phases/03-infrastructure-centralization/03-04-PLAN.md` — Original WA-05 plan
- `.planning/phases/03-infrastructure-centralization/03-03-SUMMARY.md` — What was claimed done
- `.planning/phases/03-infrastructure-centralization/03-04-SUMMARY.md` — What was claimed done

</canonical_refs>

<code_context>

## Existing Code Insights

### Current Violation Census

- **except Exception:** ~80 occurrences across ~40 files (production src/ subset: ~17 in ~8 files including `flext_cli/services/output.py` (9), `flext_db_oracle/api.py` (4), `flext_meltano/singer/tap.py` (1), `flext_meltano/singer/target.py` (1), `flext_ldif/_utilities/collection_ldif.py` (1), `flext_api/schemas/jsonschema.py` (1))
- **sys.exit outside **main**:** 5 files — `extra_paths.py`, `path_sync.py`, `target_refactored.py`, `flext-dbt-oracle-wms/cli.py`, `flext-dbt-ldif/cli.py`
- **print in production:** 2 instances in `scheduled_maintenance.py` (src + docs copy)

### Established Patterns

- `u.Infra.run_cli(main)` pattern already wraps `sys.exit()` — some files already use this
- `FlextLogger` is the standard logging abstraction — available in all projects via `s.get_logger()`
- Phase 3 already fixed the majority of workarounds — these are residuals that slipped through

### Integration Points

- `flext_cli/services/output.py` has 9 bare except handlers — likely wrapping display/formatting operations that can raise various errors
- `flext_db_oracle/api.py` has 4 — likely database operation error handling needing `oracledb.Error` specificity

</code_context>

<specifics>
## Specific Ideas

No specific requirements — follow AGENTS.md workaround eradication policy exactly as written.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 08-workaround-residual-cleanup*
*Context gathered: 2026-03-24*
