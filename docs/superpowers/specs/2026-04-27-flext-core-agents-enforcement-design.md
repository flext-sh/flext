# Design: flext-core AGENTS.md Strict Enforcement Sweep

**Date**: 2026-04-27  
**Scope**: `flext-core/src/` (enforcement), all 33 consumers (propagation)  
**Approach**: Phase B — rule-category sweeps, gate between phases

---

## Context

`flext-core` is the root project consumed by all 33 other projects. It has accumulated ~29 god modules (files >200 LOC), compatibility aliases, typing violations, and pass-through wrappers that violate AGENTS.md §3.1/§3.2/§3.5. This design applies all rules strictly with no backward compatibility and immediate signature propagation to consumers.

---

## Architecture

4 sequential phases. Gate between phases: `ruff + pyrefly + pytest flext-core` must be 0 errors before advancing.

```
Phase 1: §3.1 God Module Decomposition
Phase 2: §3.5 Compat/Alias Extermination  
Phase 3: §3.2 Typing Violations (Any/cast/object/noqa)
Phase 4: Cross-Project Propagation (all 33 consumers)
```

---

## Phase 1: §3.1 God Module Reduction

**Rule**: Every file, class, method >200 logical LOC is a violation.  
**Primary fix**: DELETE and REPLACE with existing primitives. MRO extraction is last resort only when the file remains >200 LOC after all deletions.

### Reduction Ladder (exhaust in order before splitting)

For each god module, apply in sequence — stop as soon as LOC drops below 200:

1. **Delete dead/unreachable code** — `scope callers <Symbol>` shows zero callers → delete symbol + tests
2. **Delete compat aliases and pass-throughs** — `OldX = NewX`, `def old(): return new()` → delete, update callers via `sg`
3. **Replace custom code with Pydantic 2 / Python 3.13 primitives** — see §0.1 deletion ladder:
   - Custom `__init__` body → `model_post_init` or `@model_validator(mode="after")`
   - Custom dispatch table → `singledispatch` / discriminated union
   - Manual validation loops → `Annotated[T, BeforeValidator(...)]`
   - `to_dict()`/`from_dict()` wrappers → `model_dump()`/`model_validate()` directly
   - `@property` returning derived data → `@u.computed_field`
   - Manual JSON parsing → `model_validate_json`
4. **Absorb into existing canonical origin** — if a method duplicates `u.*`, `m.*`, or a parent class method, delete local copy and use canonical origin directly
5. **MRO mixin extraction** — ONLY if still >200 LOC after steps 1–4: extract cohesive concern into `_<tier>/<concern>.py` mixin; public facade inherits

### Targets (by descending size — full list via `tokei flext-core/src/` at execution time)

| File | LOC | Expected reduction route |
|---|---|---|
| `_constants/enforcement.py` | 1,357 | Delete duplicate rule entries; collapse repeated patterns via Pydantic `RootModel`/`TypeAdapter`; then extract if needed |
| `_utilities/beartype_engine.py` | 1,331 | Delete validators duplicated in `u.*`; replace manual isinstance chains with `TypeIs`; then extract |
| `container.py` | 1,084 | Delete proxy methods duplicated from `_models/container.py`; replace manual wiring with DI primitives |
| `result.py` | 966 | Delete convenience wrappers duplicating `r[T]` DSL; replace `cast()` with `TypeIs` |
| `decorators.py` | 882 | Delete decorators whose body is a Pydantic 2 primitive; collapse repeated patterns |
| `runtime.py` | 808 | Delete alias re-exports already in `__init__.py`; absorb into facade |
| `_models/enforcement.py` | 801 | Delete model fields duplicated from `_constants/enforcement.py`; use `RootModel` for homogeneous collections |
| `handlers.py` | 665 | Replace `if/elif` dispatch with `singledispatch`; delete unused handler variants |
| `settings.py` | 613 | Delete manual env-reading duplicating `FlextSettings` base; use `@FlextSettings.auto_register` |
| `registry.py` | 603 | Replace manual scan loops with `TypeAdapter`-cached lookups; delete proxy methods |
| `_utilities/enforcement.py` | 567 | Delete methods duplicated from `FlextUtilitiesBeartypeEngine`; absorb into canonical origin |
| `_protocols/result.py` | 531 | Delete protocol methods already declared in parent protocol; use `@override` only |
| `__init__.py` | 521 | AUTO-GENERATED — skip (regenerate via `make gen` after changes) |
| `loggings.py` | 510 | Delete config helpers duplicating `structlog` native API; replace with `FlextLogger` directly |
| All remaining >200 LOC | via `tokei` | Same ladder: delete → replace → absorb → extract |

### Method per file

```
1. qlty smells <file> — identify specific smell categories present
2. scope callers <Symbol> for each symbol — map full blast radius
3. Apply reduction ladder steps 1–4 in order
4. ruff check <file> + pyrefly check <file> — gate immediately
5. pytest flext-core/tests/ -x — verify no regressions
6. If still >200 LOC: extract cohesive concern as MRO mixin (step 5)
7. sg propagate any signature changes to consumers NOW (same cycle)
```

**Validation**: `tokei flext-core/src/` — zero files >200 logical LOC. Net LOC delta MUST be negative.

---

## Phase 2: §3.5 Compat/Alias Extermination

**Rule**: Compatibility wrappers (`def old(): return new()`), `OldX = NewX` aliases, non-canonical class names — DELETE on contact.

**Targets**:
- All `OldX = NewX` module-level aliases
- All pass-through `def f(a, b): return g(a, b)` functions
- All class names not matching `Flext<Project><Tier>` in `src/`
- All class names not matching `TestsFlext<Project><Tier>` in `tests/`

**Method**:
```bash
sg -p '$X = $Y' --lang py flext-core/src          # find aliases
sg -p 'def $f($$$): return $g($$$)' --lang py     # find pass-throughs
```
Delete each, update callers via `sg` rename in same cycle.

**Validation**: `ruff + pyrefly + pytest flext-core` green.

---

## Phase 3: §3.2 Typing Violations

**Rule**: `Any`, bare `object`, `cast()` outside `result.py`, `# type: ignore`, `# noqa` — root-cause fix only, never suppress.

**Targets**:
- `from typing import Any` usage → replace with `t.GuardInput` or specific union
- `cast(X, v)` → replace with `TypeIs[X]` narrowing or `isinstance` guard
- `bare object` → replace with most-restrictive type available
- `# type: ignore` / `# pyrefly: ignore` / `# noqa` → fix root cause structurally

**Method**: `sg -p 'cast($T, $v)' --lang py flext-core/src` → replace.

**Validation**: `make pol PROJECT=flext-core` must show 0 `Any` / 0 `type: ignore` in src/.

---

## Phase 4: Cross-Project Propagation

**Rule**: Every signature change in flext-core must propagate immediately to all 33 consumers in the same iteration.

**Method**:
```bash
sg -p '<OldSignature>' -r '<NewSignature>' --lang py flext-*/src
make check PROJECT=<affected-project>
```

**Targets**: All projects that import changed symbols from `flext_core`.

**Validation**: `make check` green across all affected projects. `make pyre` workspace-wide shows 0 errors.

---

## Verification (End-to-End)

```bash
# Per phase gate
ruff check flext-core/src/ && pyrefly check flext-core/src/
pytest flext-core/tests/ --tb=short

# Phase 3 gate
make pol PROJECT=flext-core

# Phase 4 gate  
make check  # workspace-wide
make pyre   # workspace-wide pyrefly
```

**Done condition**: `make check` workspace-wide exits 0, `make pyre` exits 0, `pytest flext-core` 100%.
