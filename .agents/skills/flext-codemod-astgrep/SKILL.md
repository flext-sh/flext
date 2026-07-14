---
name: flext-codemod-astgrep
description: >-
  Reusable, battle-tested ast-grep codemod library + authoring guide for FLEXT
  API-drift migrations (assert->tm matchers, settings import/base renames,
  namespaced-settings access, CLI-API refactors). Use when migrating any repo
  (flext-*, projeto_b-*, projeto_a-*, or external consumers) to a new flext version,
  or when authoring/optimizing structural rewrites with ast-grep. DO NOT USE FOR
  questions unrelated to structural codemods or greenfield architecture.
---

# FLEXT ast-grep Codemod Library

Canonical, verified structural-rewrite recipes for FLEXT API migrations, plus a
hard-won authoring guide so future migrations (in this repo and external
consumer repos) reuse the same rules instead of re-deriving them.

> Engine facts confirmed empirically (ast-grep CLI, this workspace, 2026-07):
> the Rust regex engine backing `regex:` matchers **does not support
> look-around** (`(?!...)`, `(?<=...)`); `field:` matching a `dotted_name`
> needs `regex:` (a `pattern:` will not match a dotted module path); relational
> `has:` for a nested field needs `stopBy: end`; a single `--pattern` cannot
> span multiple statements.

## When to use

- Migrating a repo to a new flext version and the same mechanical edit repeats
  across many files (imports, base classes, accessors, matcher calls).
- The change is **syntactic shape**, not string contents (use `rg` for strings).
- You want a **safe, idempotent, parse-verified** rewrite instead of sed/regex.

## Quick start

```bash
# dry-run (preview diffs) — ALWAYS do this first
ast-grep scan --rule .agents/skills/flext-codemod-astgrep/rules/<rule>.yml <target-dir>

# apply
ast-grep scan --rule .agents/skills/flext-codemod-astgrep/rules/<rule>.yml <target-dir> --update-all
```

Always follow an `--update-all` with: `ruff check <dir> --fix` (import order the
rewrite disturbs) then re-parse every file with `ast.parse`.

## Rule catalog (rules/)

| Rule file | Migrates | Guard against |
|-----------|----------|---------------|
| `assert-to-tm.yml` | `assert x == y` -> `tm.that(x, eq=y)` + `.success`/`.failure` -> `tm.ok/fail` etc | whitespace-only `lacks` (gotcha #4) |
| `settings-base-rename.yml` | `from flext_core.settings import FlextSettingsBase` -> `from flext_core import FlextSettings` | multi-import + `as`-alias data loss |

Each rule has a sibling `tests/<rule-id>-test.yml` with `valid` (must not match)
and `invalid` (must match) samples — the negative cases are the point.

## Authoring guide — the 6 lessons that matter

### 1. Exact-string patterns OVER-MATCH — always add negative guards
`pattern: from a.b import C` also matches `from a.b import C, D` (rewriting it
drops `D` — silent data loss) and does NOT match `from a.b import C as X`.
Fix: constrain the enclosing `kind` and negate the danger:
```yaml
rule:
  kind: import_from_statement
  all:
    - has: { field: module_name, regex: '^a\.b$' }
    - has: { field: name, regex: '^C$', stopBy: end }
    - not: { regex: ',' }        # exclude multi-import
    - not: { regex: ' as ' }     # exclude aliased import
```

### 2. `field:` on a dotted path needs `regex:`, not `pattern:`
`has: {field: module_name, pattern: flext_core.settings}` fails; the module is a
`dotted_name`. Use `has: {field: module_name, regex: '^flext_core\.settings$'}`.

### 3. Relational `has:` for a nested field needs `stopBy: end`
The import `name` is nested under `import_from_statement`; without
`stopBy: end`, `has: {field: name, ...}` returns "No matches found ... Try
adding `stopBy: end`".

### 4. No look-around in `regex:`
`^(?!Foo$).+` errors: `look-around ... is not supported`. Express "not X" with a
`not:` rule node, never a negative-lookahead regex.

### 5. Multi-statement collapses are NOT ast-grep's job
A 3-statement -> 1-statement collapse cannot be a single pattern. Use a small
Python line-transform OR ast-grep `rewriters` + `transform` only when the nodes
are siblings under one parent.

### 6. Import injection must respect multi-line `from (...)` blocks
Auto-adding an import after "the last import line" breaks if that line is an
unclosed `from x import (` opener — the injected line lands inside the paren
group -> SyntaxError. Track paren depth; insert only at depth 0.

## Matcher API map (assert -> tm)

Verified against `flext-tests` `tm.that` kwargs:

| assert form | tm form |
|-------------|---------|
| `assert x == y` | `tm.that(x, eq=y)` |
| `assert x != y` | `tm.that(x, ne=y)` |
| `assert x is None` / `is not None` | `tm.that(x, none=True)` / `none=False` |
| `assert isinstance(x, T)` | `tm.that(x, is_=T)` |
| `assert x in y` / `x not in y` | `tm.that(y, has=x)` / `lacks=x` |
| `assert r.success` / `r.failure` | `tm.ok(r)` / `tm.fail(r)` (returns the value) |
| `assert x is True` / `is False` | `tm.that(x, eq=True)` / `eq=False` |

**Gotcha #4 detail**: the `has`/`lacks` matcher normalizes whitespace-only
payloads to `""`, so `tm.that(out, lacks="  \n")` silently checks `""` and
fails. Rewrite whitespace-negation asserts to an explicit boolean, e.g.
`tm.that(out.endswith("  \n"), eq=False)`.

## Migration playbook (per repo)

1. `git status` clean baseline; pick the smallest scoped dir.
2. Dry-run each rule; read the diff — an unexpected match = tighten the guard.
3. Apply -> `ruff --fix` -> `ruff format` -> re-parse.
4. Run pytest; failures are *semantic* API drift (namespaced access, renamed
   symbols) not codemod bugs — fix those by hand faithful to the current API
   (use `crg`/`lsp`/`codegraph` to find the real symbol, never guess).
5. Prefer the centralized `e` (FlextExceptions) + `r[T]` result flow when
   touching error paths; do not hand-roll try/except.
6. Commit with explicit pathspec (never `-A`), small and often.

## Cross-repo reuse

These rules are location-independent. To run them against an external consumer
repo (e.g. `../projeto_b`, `../projeto_a`):
```bash
ast-grep scan --rule /home/marlonsc/flext/.agents/skills/flext-codemod-astgrep/rules/settings-base-rename.yml ../projeto_b/src
```
Non-flext-package repos (projeto_b/projeto_a) keep **raw `assert`** in their own
tests; only apply the assert->tm rule to `flext-*` package tests. Always apply
the *import/base/accessor* rules to any consumer on the new flext version.

## Safety protocol — VALIDATE the target before global apply

> Learned the hard way: a `isinstance(x, m.SettingsValue)` ->
> `isinstance(x, m.BaseModel)` rule was applied to 2 sites before verifying the
> real base — but `FlextTestsSettings.Tests` actually inherits *raw*
> `pydantic.BaseModel`, so BOTH the old and the new assertion were wrong. The
> rule "worked" (matched + rewrote) yet the test still failed.

Before promoting ANY rule from one-file to global `--update-all`:

1. **Prove the target with the interpreter, not assumption.** For a base/type
   swap, run `python -c "print(type(x).__mro__)"` on a real instance and
   confirm the *new* symbol is actually in the MRO. Never infer the target
   from the symbol name.
2. **Detection-first for judgement rules.** If the correct replacement varies
   per site (base class, result-combinator, error factory), ship the rule as
   `severity: warning` **detection-only** (no `fix:`) so it surfaces candidates
   a human/agent judges. Only add `fix:` when the rewrite is a *pure,
   context-free token swap* proven on >=3 real sites.
3. **Widen the test corpus.** The `tests/<rule-id>-test.yml` MUST include the
   real-world variants that bit you: multi-import, alias, `is True` suffix,
   already-migrated code (must NOT re-match).
4. **Dry-run on the WHOLE target, grep the diff for surprises**, then apply to
   ONE file, run its pytest, and only then `--update-all` the rest.
5. **A green codemod is not a green test.** After apply, the pytest is the
   real gate — a matched+rewritten line can still be semantically wrong.

Rule maturity ladder: `detection-only (hint)` -> validated on 1 file + pytest
green -> `detection+fix (warning)` with a widened test corpus -> global
`--update-all`. Do not skip rungs.
