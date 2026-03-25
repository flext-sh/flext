# Phase 8: Workaround Residual Cleanup - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-24
**Phase:** 08-workaround-residual-cleanup
**Areas discussed:** Exception specificity, sys.exit refactoring, print replacement
**Mode:** --auto (all decisions auto-selected)

---

## Exception Specificity (WA-03)

| Option | Description | Selected |
|--------|-------------|----------|
| Specific exception types per context | Replace with OSError, ValueError, etc. based on call site | ✓ |
| Generic RuntimeError everywhere | Uniform but less informative | |
| Re-raise pattern | catch, log, re-raise original | |

**User's choice:** [auto] Specific exception types per context (recommended default)
**Notes:** Production src/ gets zero tolerance. Tests/examples get lighter treatment.

---

## sys.exit Refactoring (WA-04)

| Option | Description | Selected |
|--------|-------------|----------|
| Return exit codes, wrap in **main** | Callers return int, **main**.py does sys.exit() | ✓ |
| Inline if **name** guard | Add guard around sys.exit in same file | |
| Exception-based exit | Raise SystemExit instead of sys.exit() | |

**User's choice:** [auto] Return exit codes, wrap in **main** (recommended default)
**Notes:** Follows existing u.Infra.run_cli() pattern already used in some files.

---

## print Replacement (WA-05)

| Option | Description | Selected |
|--------|-------------|----------|
| Replace with FlextLogger | Use project logging abstraction | ✓ |
| Replace with sys.stdout.write | Lower-level but still explicit | |
| Remove entirely | If output is unnecessary | |

**User's choice:** [auto] Replace with FlextLogger (recommended default)
**Notes:** Only 2 instances — straightforward fix.

---

## Claude's Discretion

- Exact exception types per call site
- Whether cli.py files need separate **main**.py

## Deferred Ideas

None
