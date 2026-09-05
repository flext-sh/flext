# Performance Profiling Standard

Performance changes require measured runtime evidence from the canonical command
surface. Optimization never weakens validation, clears Testmon, introduces an
alternate fast path, or bypasses Make orchestration.

## Before changing code

1. Identify the public root Make verb that exercises the real workflow.
2. Use the profiling instrumentation owned by its typed flext-infra execution
   context.
3. Capture wall time, cumulative hotspots, call counts, subprocess time, and I/O
   time for the unchanged baseline.
4. Store profiling artifacts only in the configured external runtime-state
   directory.

If `make help` exposes no profiling-capable workflow, add that capability at the
root Make and flext-infra owners. A direct profiler or ad-hoc script is not valid
evidence.

## Optimize the measured owner

Change the dominant measured path. Preserve typed OO/MRO boundaries, dependency
injection, fail-fast behavior, and the full validation surface. Do not add a
fallback, retry, hidden cache, partial run, or duplicated implementation.

Caching is allowed only when its invalidation authority is typed, explicit, and
proved through the public runtime contract. Test selection remains owned by the
retained Testmon cache.

## Evidence

Record on the active Bead:

- exact root Make command, working directory, exit code, and decisive output;
- baseline and optimized wall time;
- absolute and percentage change;
- cumulative hotspots and call-count changes;
- subprocess and I/O accounting;
- the integrated runtime measurement after landing.

An optimization without a material, repeatable improvement is removed in the
same change.

## Canonical validation

```bash
make fix APPLY=Y
make fmt APPLY=Y
make check APPLY=Y
make test APPLY=Y
make conform APPLY=Y
```

Do not invoke profilers, test runners, or other underlying tools directly. Do
not add project, file, pattern, action, phase, fix, or changed-only selectors.
