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

# FLEXT structural codemods

This skill explains how to operate the provider. It does not duplicate the
provider catalog or define domain behavior.

## Authority

Authority is resolved in this order:

1. The owning domain objective, public declaration/model, validated
   configuration, and fundamental rule define the required behavior.
2. rules/*.yml declares each structural detection or rewrite.
3. provider.toml declares the provider identity and the complete exported ID
   set; sgconfig.yml declares how ast-grep loads it.
4. This skill defines the safe operating procedure.
5. tests/*-test.yml and tests/**snapshots** only validate the declarations.

A fixture, snapshot, or green test is never SSOT. When validation conflicts
with an owner above it, correct or remove the stale validator.

The generic preview/apply engine is owned and managed by ai-hub. FLEXT owns
only this provider data and procedure. A workspace receives this surface only
after canonical pyproject metadata identifies flext-core usage.

## Managed execution

Run from the target workspace root. The generated Make surface supplies this
provider's config, rules, and validators to the managed engine.

    make workspace-codemod TEST=1
    make workspace-codemod RULE=result-failure-rebind SCAN_DIR=src
    make workspace-codemod STRICT=1 RULE=result-failure-rebind SCAN_DIR=src

Report mode is always the first mutation step. It prints the exact finding
count, fixable count, sorted file set, and SHA-256 of the normalized JSON match
manifest.

Apply exactly one rule against the unchanged preview:

    make workspace-codemod APPLY=1 RULE=result-failure-rebind \
      EXPECTED_FIXES=3 EXPECTED_FILES=src/a.py,src/b.py \
      EXPECTED_MATCHES_SHA256=<preview-sha> SCAN_DIR=src

Mutation is allowed only when all of these conditions hold:

1. RULE is one exact provider ID and that rule has an explicit fix.
2. EXPECTED_FIXES is the positive exact preview cardinality.
3. EXPECTED_FILES is the exact sorted preview file set.
4. EXPECTED_MATCHES_SHA256 equals the unchanged normalized preview.
5. No non-fixable finding is mixed into the selected application.
6. The engine applies only the selected rule.
7. A rescan finds zero remaining matches for that rule.
8. Git diff checks and the target repository's native gates pass.

There is no force mode, skip-verification mode, broad application, automatic
rollback, or clean-tree assumption. A post-apply failure remains visible and
is repaired forward within the same owned change.

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
ast-grep scan --rule codemod/rules/settings-base-rename.yml ../projeto_b/src
```
Non-flext-package repos (projeto_b/projeto_a) keep **raw `assert`** in their own
tests; only apply the assert->tm rule to `flext-*` package tests. Always apply
the *import/base/accessor* rules to any consumer on the new flext version.

## Validator policy

After the canonical rule is correct:

1. Add one validator with the same ID.
2. Include at least one matching invalid sample and one non-matching valid
   boundary.
3. Review actual ast-grep output against the rule declaration.
4. Update that validator's snapshot only after the output is accepted.
5. Run the tests again without snapshot mutation.
6. Prove provider, rule, validator, and snapshot ID sets are bijective.

Snapshot regeneration is validation maintenance, not source migration.
Direct source mutation with ast-grep --update-all, bulk ruff --fix, sed, or a
compensating script bypasses the managed engine and is prohibited.

## Evidence and maintenance

Record preview, apply, idempotence, native gates, exit codes, and decisive
output in the active workspace-root bead. Member projects use the root
workspace Beads database; only an independent project owns another database.

REFERENCE.md is a compact ownership map. The exact live inventory is read from
provider.toml and rules/*.yml, never copied into prose.
