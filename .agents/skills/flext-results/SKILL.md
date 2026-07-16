---
name: flext-results
description: >-
  Use the current flext-core Result contract for success transforms, fallible
  composition, error recovery, error mapping, and side-effect taps. Use when a
  path returns or consumes r[T] or p.Result[T].
license: MIT
metadata:
  version: 2.0.0
---
# FLEXT Result Contract

## Contract

Import the public Result aliases from the package facade. `flext-core` owns the
implementation and protocol; this skill explains their current composition
surface without wrapping it.

The source declarations are `flext_core.result.FlextResult` and
`flext_core._protocols.result.FlextProtocolsResult`. The public consumer
surface is the package facade aliases `r` and `p.Result[T]`; private source
paths are named here only to identify ownership, never as import paths.

## Operation Routing

| Intent | Public operation |
| --- | --- |
| create success or failure | `r.ok`, `r.fail`, `r.fail_op` |
| normalize another Result | `r.from_result`, `r.from_failure` |
| validate a model | `r.from_validation` or `.to_model` |
| execute one fallible callable | `r.create_from_callable` |
| decorate a callable | `r.safe` |
| transform a success value | `.map` |
| chain another fallible operation | `.flat_map` |
| chain homogeneous Result steps | `.flow_through` |
| recover with another Result | `.lash` |
| recover with a plain value | `.recover` |
| transform failure text | `map_error` |
| retain a success matching a predicate | `.filter` |
| collapse both branches to one value | `.fold` |
| map success or return a default | `.map_or` |
| observe success or failure | `.tap`, `.tap_error` |
| combine independent Results | `r.accumulate_errors` |
| apply a Result function to a sequence | `r.traverse` |
| manage a resource lifecycle | `r.with_resource` |
| extract at a true terminal boundary | `.unwrap`, `.unwrap_or`, `.unwrap_or_else` |

`bind` and `alt` are not FlextResult composition methods. Do not import a
parallel container API or add aliases for them.

## Workflow

1. Keep the first external exception boundary responsible for translation to a
   failed Result with context.
2. Use `map` when the callback returns a plain value; callback exceptions are
   translated to failure by the canonical implementation.
3. Use `flat_map` when the callback already returns a Result.
4. Use `lash` for explicit recovery and `map_error` only to enrich/normalize
   failure text without hiding its cause.
5. Use taps for observation only. They preserve the branch when the callback
   completes and translate callback exceptions to failure.
6. Return the same validated domain model through internal layers; do not dump
   or reconstruct it between Result steps.

## Non-Negotiables

- No exception-to-default fallback, sentinel success, raw error mapping, or
  boolean failure channel.
- No manual success/failure rewrapping when a transform expresses the flow.
- No compatibility methods that mirror another Result library.
- No `unwrap` inside composable domain flow; extraction belongs at a terminal
  integration boundary.
- Behavior tests validate the public facade; they never own Result semantics.

## Verification

Use fresh public imports, `ruff`, the type checker, and the narrow behavior test
for the composed path. Record exact evidence in the root-workspace Bead.

## References

- [`using-flext-core`](../using-flext-core/SKILL.md)
- [`coding-standards`](../coding-standards/SKILL.md)
- [`flext-quality-gates`](../flext-quality-gates/SKILL.md)
