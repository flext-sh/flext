---
name: flext-namespace-rewrite-guard
description: Safe procedure for workspace-wide namespace propagation (`c.X` → `c.NS.X`, etc.). Required before any bulk rewrite.
---

# FLEXT Namespace Rewrite Guard

## When to use

Any task that propagates a collision-aware rewrite across the workspace
(e.g. when an attribute that used to be accessed as `c.X` must now be
accessed as `c.Cli.X`, `m.Ldif.X`, `p.Quality.X` etc.). Typical triggers:

- Linter output like `FlextCliTypes has no class attribute Ldif`.
- Project slot consolidation (moving adapters/constants under the project
  nested namespace).
- Recovery from earlier over-wrap / over-revert cycles.

## Hard rules

1. **Exactly one nested namespace per project.** The slot registry in
   [`.agents/skills/flext-mro-namespace-rules/SKILL.md`](../flext-mro-namespace-rules/SKILL.md)
   is SSoT. `scripts/namespace_rewrite_guard.py` refuses to touch a
   project that is not registered there.
2. **Never wrap a name that is already flat on `flext_core`.** Inherited
   core attributes (`t.NonEmptyStr`, `c.DEFAULT_ENCODING`, `m.Entity`, …)
   must stay flat — they are the canonical surface of the facade MRO.
3. **Never flatten an organic MRO path.** `m.Ldif.Entry` does NOT become
   `m.Entry`. `u.Infra.parse_semver` does NOT become `u.parse_semver`.
   The guard script only wraps (flat → nested); it never flattens.
4. **Runtime verification before static rewrite.** A rewrite is only
   emitted when `getattr(project.<alias>.<Namespace>, name)` is actually
   reachable at import time. Static-only guesses are rejected.
5. **Monotonic gates.** After `--apply`, `ruff` and `pyrefly` error
   counts must be ≤ baseline. The guard rolls back the affected files
   if they increase.
6. **No `.bak` files in tree.** If a rewrite is rolled back, the guard
   restores the pre-image in place — nothing is moved into the tree.

## Workflow

```bash
# 1) Inspect — dry-run, default — prints which files would change.
python scripts/namespace_rewrite_guard.py --project flext_ldif

# 2) Apply — per project, gates enforced with automatic rollback.
python scripts/namespace_rewrite_guard.py --project flext_ldif --apply

# 3) Workspace sweep — the guard iterates all registered projects.
python scripts/namespace_rewrite_guard.py --apply
```

## Anti-patterns (pre-existing damage log)

- Iterating `dir()` and wrapping **every** name: wraps `PortNumber`,
  `WorkerCount`, `Entry` and other names that belong to the flat core
  surface, generating hundreds of `FlextXTypes has no attribute Y`
  errors.
- Blind revert scripts (`m.Ldif.Entry → m.Entry`): destroys the
  organically inherited namespace path, cascades through every project
  that imports LDIF models.
- `sed -i` or `ast-grep --update-all` on the whole workspace without
  the per-project collision intersection (`flat_core ∩ project_ns`).

Always use the guard script instead of ad-hoc loops.

## Recovery protocol (if damage already landed)

1. Run `pyrefly check` per project; collect the failing files.
2. For each `Class X has no class attribute Y` error, decide:
   - `Y` should stay flat on core → delete the accidental `X.` prefix.
   - `Y` is a project-slot attribute → add the missing nested namespace
     wrapper in `typings.py` / `constants.py` / etc.
3. Re-run the guard in dry mode; it must report `no collisions` or
   `collisions present but no occurrences`.
4. Commit only when ruff and pyrefly are both zero across all 24
   projects.
