---
name: flext-agent-strict-rules
description: Mandatory runtime alias and typing discipline for all coding agents. Use when writing or reviewing FLEXT code to enforce alias-only access (c/m/r/t/u/p), isinstance/TypeGuard narrowing (never type()), centralized Pydantic v2 models over polymorphic functions, and no loose module-level objects.
---

# Flext Agent Strict Rules

**Scope**: Runtime guardrails for coding agents across all 33 FLEXT projects.
**Authority**: `AGENTS.md` §3 Code Law, §4 Import Law, §9 Agent Execution Pre-requisites. This skill is the operational expansion of those sections — not a replacement.

## References

- `AGENTS.md` — canonical governance source (always read first)
- `.claude/skills/flext-strict-typing/SKILL.md` — typing contracts
- `.claude/skills/flext-import-rules/SKILL.md` — import order and boundaries
- `.claude/skills/flext-patterns/SKILL.md` — result, DI, logging patterns
- `.reports/non-runtime-aliases-and-loose-methods.md` — remediation targets
- `.reports/typing-violations-report.md` — `type()` / `__class__` cleanup list
- `.reports/polymorphic-refactor-targets.md` — polymorphism → Pydantic v2 targets
- `.reports/EXECUTION-CHECKLIST-aliases-typing-polymorphic.md` — ordered execution list

## Rules

- Apply `AGENTS.md` §3 uniformly: no "test-only" or "example-only" relaxation.
- Use simple runtime aliases only; remove any `u.Aliases.*` indirection.
- Protocol contracts belong in `p.*`; composed aliases in `t.*`; domain carriers in `m.*`. Never annotate with a concrete class when a canonical `p.*`/`t.*` contract exists.
- Dismantle polymorphic branching into centralized Pydantic v2 models (`Literal` discriminators, `Field`, `model_validator`).
- Enforce abstraction boundaries in `examples/` and `scripts/` exactly as in `src/` (`AGENTS.md` §2.7).
- In runtime `src/` code, prefer `e.fail_*`, `r.fail_op`, `r.fail_exc`. Avoid ad-hoc `r.fail("...")` except for explicit structured `error_data` passthrough.

## Operational Discipline (Expansion of AGENTS.md §3)

### 1. Simple Runtime Aliases Only

- **Forbidden**: `u.Aliases.constants()`, `u.Aliases.models()`, `u.Aliases.result()`, `u.Aliases.typings()`, `u.Aliases.protocols()`, `u.Aliases.utilities()`, and every other `u.Aliases.*` layer for defining package-level aliases.
- **Required**: Direct assignment at module bottom (`c = FlextConstants`, `m = FlextModels`, `r = FlextResult`, `t = FlextTypes`, `u = FlextUtilities`, `p = FlextProtocols`, `d = FlextDispatcher`, `e = FlextExceptions`, `h = FlextHelpers`, `s = FlextService`, `x = FlextContext`).
- **Access**: Through the project's runtime alias only, preserving the organic MRO path. Call sites use `u.Infra.parse_semver`, `c.Tests.ERR_OK_FAILED`, `m.TargetOracle.ExecuteResult` — never flatten these to the facade root.
- Text that says "resolve via MRO registry (u.Aliases)" or "use u.Aliases" is **wrong**. Remove it on sight.

### 2. No Loose Aliases or Pass-Through Methods

- Remove aliases that only rename another symbol (e.g. `FactoryDiscovery = FactoryDecoratorsDiscovery`, `cast_direct = staticmethod(...)`). Call sites must use the canonical name.
- Remove methods that only delegate with no added behavior (e.g. `def foo(self): return Bar.baz(self)`). Call `Bar.baz` directly.

### 3. Type Narrowing — `isinstance` / `TypeGuard`, Never `type()`

- **Forbidden**: `type(x) is T` and `type(x) == T` for narrowing. Type checkers do not narrow on `type()` — they narrow on `isinstance()` and `TypeGuard`.
- **Required**: `isinstance(x, T)` or a `TypeGuard`/`TypeIs` helper so the checker can narrow after the guard. For validated data, prefer `model_validate` / `model_validate_json` to centralize validation and typing.
- **Exception**: AST or reflection code that genuinely needs exact class identity (`type(node) is ast.Call`) — and only when narrowing is not required in the same block.

### 4. Polymorphic Code → Centralized Pydantic v2 Models

- Dismantle polymorphic functions that branch on 3+ types. Replace with one (or a small set of) Pydantic v2 models defining shape and validation.
- Use discriminated unions (`Literal` discriminator field), `Field`, `@field_validator`, `@model_validator`, `model_validate`, `model_validate_json`. One entry point for validation; avoid long `if isinstance(...)` chains over many types.

### 5. Scale and Parallelism

- Apply these rules across **all 33 projects**. Use multiple agents in parallel (see `flext-5agent-coordination`) — one agent per project or per report section — with minimal, verifiable changes.
- Each agent: one project or one section; run `make check` and `make test` for the touched project before handoff.
- Lint-clean with zero warnings or errors. Do not defer violations without explicit operator approval (`AGENTS.md` §8).

## Workflow

1. Identify which operational cluster (1–5 above) applies to the change.
2. Apply the canonical pattern without introducing compatibility layers.
3. Update all impacted call sites/contracts via `ast-grep` (`AGENTS.md` §3.5).
4. Run `make check` + `make test` for every touched project and record evidence.

## Examples

Good:

```python
from flext_core import p, r


def normalize_logger(owner: p.HasLogger) -> p.Result[p.Logger]:
    return r[p.Logger].ok(owner.logger)
```

Why good: consumes the canonical structural protocol `p.HasLogger` and keeps the return flow on `r[T]`.

Bad:

```python
def normalize_logger(owner: FlextLogger) -> FlextLogger:
    return owner
```

Why bad: pins the contract to a concrete implementation when the public structural protocol is the real boundary.

Good:

```python
from flext_core import m


class ParseRequest(m.ArbitraryTypesModel):
    kind: Literal["json", "yaml", "toml"]
    payload: str

    @model_validator(mode="after")
    def _validate_payload(self) -> Self:
        if self.kind == "json":
            m.validate_json(self.payload)
        return self
```

Why good: one centralized Pydantic v2 model with a discriminated field and a single validator replaces three branching `if isinstance(...)` chains.

## Verification

- `make check PROJECT=<name>` — lint + typecheck gate for touched project.
- `make test PROJECT=<name>` — tests + coverage gate.
- `rg -n "type\(.*\) is|type\(.*\) ==" --glob "**/*.py"` — locate remaining `type()` narrowings.
- `rg -n "u\.Aliases\." --glob "**/*.py"` — locate remaining alias-registry usages.

No claims of completion without executable evidence (`AGENTS.md` §3.5).
