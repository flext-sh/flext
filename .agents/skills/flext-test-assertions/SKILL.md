---
name: flext-test-assertions
description:
  Convert or write FLEXT test assertions through the canonical tm matchers and the
  flext-infra rewire-test-assert catalog, with the fewest statements.
---

# FLEXT Test Assertions

Use when a FLEXT test asserts anything, or when `ban-test-assert`, a complexity finding
or a review points at test assertions. The
[workspace assertion standard](../../../docs/guides/using-flext-tests.md#workspace-assertion-standard)
owns the patterns and the
[codemod rules guide](../../../docs/guides/codemod-rules.md) owns the catalog; this skill
holds only the procedure.

1. Bind `tm` through the project's tests facade (`from tests import tm`), never a local
   matcher or a copied helper.
2. Prefer one expression per assertion: `tm.ok`/`tm.fail` for results, `tm.that` with
   `eq`/`ne`/`has`/`lacks` for values, `tm.that(condition, truth=True|False)` for truth,
   and `assertion_message=` when the original message must reach the failure. Use
   `tm.not_none`/`tm.instance` when the returned value must stay narrowed.
3. Keep a branch only when the condition needs it (None or isinstance narrowing, a bare
   name or attribute, `and`/`or`/conditional): one negated branch,
   `if not (condition): tm.reject(...)`. Never an empty `if condition: pass` branch.
4. Convert existing code with the owner, never by hand: `make mod RULES=<id>` for each
   `rewire-test-assert-*` id, `make mod RULES=import-header--tests` when `tm` is left
   unbound, and `rewire-test-reject-pass-branch*` for empty branches an older rewrite
   left. Measure the selection with code-review-graph (`impact --files`) before and
   the gate after.
5. Then `make fmt`, `make gen` (second run writes nothing), the affected tests, and
   `make check`. A rule that rewrites wrongly is fixed in `flext-infra` with a fixture
   and snapshot (`make mod-snapshots`), never patched in the consumer.
