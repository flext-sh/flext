# Performance profiling standard

<!-- TOC START -->
- [When this applies](#when-this-applies)
- [Baseline command](#baseline-command)
- [Required analysis](#required-analysis)
- [Minimum improvement threshold](#minimum-improvement-threshold)
- [Recording evidence](#recording-evidence)
- [Invalidation for cached/fast-path work](#invalidation-for-cachedfast-path-work)
- [No profiling-only commits](#no-profiling-only-commits)
<!-- TOC END -->

This standard defines the minimal evidence required for performance-related
changes in FLEXT, especially for mutating commands that execute through the
worktree transaction path.

## When this applies

Any change whose primary goal is to make a command, test suite, or generated
pipeline faster must follow this protocol. It also applies when a refactor or
feature change is expected to materially affect the runtime of an existing
command.

## Baseline command

For `flext-infra codegen init` and similar mutating commands, capture a profile
with:

```bash
FLEXT_WORKSPACE_ROOT="/path/to/workspace" \
  uv run --all-packages python -m cProfile \
  -o /tmp/flext_<feature>_<state>.prof \
  -m flext_infra codegen init --workspace "/path/to/workspace" --check-only
```

- Replace `<feature>` with a short identifier (`init`, `conform`, etc.).
- Replace `<state>` with `baseline` before the change and `optimized` after.
- Use `--check-only` (or the equivalent `--mode=check`) so the command does not
  mutate source files while still exercising the complete pipeline.

For other commands, use the same shape: `python -m cProfile -o <path> -m
<module> <args>`.

## Required analysis

After capturing both profiles, produce:

1. **Total time comparison.**

   ```bash
   python -m pstats /tmp/flext_<feature>_baseline.prof
   # then: sort time; stats 20
   ```

   Record the total time for each state and the absolute + percentage delta.

2. **Top cumulative hotspots.**

   ```bash
   python -m pstats /tmp/flext_<feature>_optimized.prof
   # then: sort cumulative; stats 30
   ```

   Identify the functions that moved into or out of the top list.

3. **Subprocess/IO accounting.** When `subprocess.run` or `u.Cli.run_raw`
   dominates, list which commands are invoked and whether any are serial but
   independent.

4. **Call-count deltas.** If the optimization targets repeated work, show the
   reduction in call counts for the relevant functions.

## Minimum improvement threshold

A performance change must satisfy at least one of:

- ≥5% wall-clock improvement on the full command, or
- ≥1s absolute improvement on the full command, or
- ≥50% reduction in a clearly identified hotspot that is a known bottleneck,
  even if the full-command gain is smaller.

If the change does not meet any threshold, revert it. Do not keep speculative
or neutral optimizations "for later".

## Recording evidence

Append the following to the active workspace Bead:

- exact capture command;
- baseline total time and profile path;
- optimized total time and profile path;
- delta (absolute and percentage);
- top hotspots before and after;
- any gates run and their exit codes.

## Invalidation for cached/fast-path work

Any optimization that introduces caching, memoization, or a fast path must also
include:

- a documented invalidation key (e.g., `mtime`, Git HEAD, file hash, schema
  version);
- a test that proves the cache is invalidated when the key changes;
- a note in the Bead about the invalidation strategy.

## No profiling-only commits

Do not commit temporary profile files (`.prof`) to the repository. Store them
under `/tmp` or another ignored location. The Bead owns the evidence, not the
repository.
