# ADR-012 — Performance optimization of worktree transactions and mutating CLI commands

- **Status:** Accepted
- **Date:** 2026-07-17
- **Scope:** `flext-infra` worktree transaction executor, `flext-cli` output
  formatting, and all mutating CLI commands that execute through the worktree
  transaction path.
- **Tracking:** `mro-96j2`, `mro-nij4`

<!-- mro-96j2 (agent: kimi) — evolucional, surgical performance improvements for mutating commands. -->

## Context

`make build WHAT=artifacts` and similar mutating commands execute inside a
complete isolated Git worktree before any source change is applied. Profiling
showed that the wall-clock time was dominated by:

1. **Serial subprocess stages in the transaction wrapper.** Lint snapshots,
   the fresh-import probe, and repository-delta capture ran one after another.
2. **Rich rendering of large machine-generated diffs.** The final report can
   contain multi-megabyte patches; routing it through Rich style parsing spent
   tens of seconds parsing markup that was already plain text.
3. **The inner command itself.** Once the wrapper overhead was removed, most
   of the remaining time is spent inside the actual `codegen init` process
   (Rope indexing, import resolution, subprocess calls to formatters/linters,
   TOML parsing, Pydantic model construction).

The worktree transaction is the canonical safety boundary for mutating commands;
any optimization must keep the checkpoint/validate/apply/cleanup contract
intact. The output layer is shared by every FLEXT CLI surface, so any fast path
must be opt-in by message size and must not change normal styling.

## Decision

### 1. Transaction wrapper stages run in parallel when independent

The wrapper performs three classes of work after the inner command finishes:

- post-command lint snapshots (`ruff`, `pyrefly`);
- fresh-import probe of every productive package root;
- repository-delta capture for patch check/apply.

Lint snapshots are independent of each other and are executed in parallel with
a bounded `ThreadPoolExecutor`. The fresh-import probe and repository-delta
capture are independent of each other and are also executed in parallel. The
inner command itself remains serial because it mutates the worktree state.

The executor is created and shut down inside the smallest scope that needs it,
so resources are released before cleanup. Result ordering is preserved so that
lint regression comparison remains deterministic.

### 2. Large machine-readable output bypasses Rich styling

`flext-cli` exposes a plain output path that writes directly to `stdout` with a
short textual prefix (`[INFO]`, `[ERROR]`, etc.) when the rendered payload
exceeds a configurable threshold. The normal `display_message` path keeps Rich
styling for small, human-facing messages. The threshold is owned by
`c.Cli.OUTPUT_PLAIN_MESSAGE_THRESHOLD`.

Worktree transaction reports use the plain path when the rendered report is
large. This eliminates style parsing for patches and command evidence while
keeping headers/summaries styled when they are short.

### 3. Future optimizations must be evidence-driven and non-breaking

Every performance change in this area must:

- start from a `cProfile` baseline of the affected command;
- end with a `cProfile` comparison that proves the improvement;
- keep the checkpoint/validate/apply/cleanup contract unchanged;
- not introduce compatibility shims, fallbacks, or old+new coexistence;
- update this ADR and `docs/standards/performance-profiling.md` when it changes
  the profiling protocol or adds/removes a fast path;
- be landed through scoped commits and fast-forward pushes with Bead evidence.

Cache-like optimizations (e.g., reusing a Rope index) are allowed only when they
have a documented invalidation strategy keyed by versioned inputs (file mtime,
Git HEAD, pyproject hash) and a test that proves invalidation works.

### 4. No optimization may bypass gates or suppress diagnostics

A faster command that produces a red lint/type/test gate is not acceptable. The
transaction wrapper exists to detect breakage; any change that hides breakage
is a regression, not an optimization.

### 5. Generated-artifact linting is a single batched stage, not per template

`flext-infra` lazy-init generation renders every `**init**.py` from a Jinja
template. The renderer keeps a per-artifact `ruff format` pass because that
output is the byte-canonical form the drift comparison relies on. The `ruff
check` validation, by contrast, does not shape the bytes, so it runs once as a
batched stage (`FlextInfraCodegenLazyInit.batch_lint_generated`) over the whole
changed artifact set after generation, instead of spawning one cold `ruff
check` subprocess per generated file. A generated artifact that fails the check
is still reported and still fails generation; only the subprocess count drops.

## Consequences

- First-pass changes (`mro-nij4`) reduced `codegen init --check-only` from
  ~320s to ~205s (~36%) by parallelizing wrapper stages and using plain output
  for large reports.
- The remaining time is mostly inside the inner command, so deeper improvements
  must target Rope/indexing, subprocess scheduling, and import/model construction
  inside `flext-infra/codegen`.
- Batched generated-artifact linting (`mro-96j2.4`) removes one cold `ruff
  check` subprocess per generated `**init**.py`. For a full-workspace run that
  generates ~225 initializers, the lint subprocess count drops from ~450
  (format + check per file) to ~226 (format per file + one batched check),
  proven byte-identical to the previous per-template output (`render_init`
  output unchanged) with zero generated-file drift introduced.
- All mutating commands that use the worktree transaction benefit from the
  parallel lint and plain-output fast paths automatically.
- Future regressions in transaction time can be caught by comparing profiles
  using the protocol in `docs/standards/performance-profiling.md`.
