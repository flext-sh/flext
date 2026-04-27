# flext-core AGENTS.md Strict Enforcement Sweep — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce all god modules in flext-core to ≤200 logical LOC by exhausting the deletion/replacement ladder first, then propagate all signature changes to all 33 consuming projects.

**Architecture:** 4 sequential phases: (1) god-module reduction via deletion + Pydantic 2 replacement ladder, (2) compat alias extermination, (3) typing violation root-cause fixes, (4) workspace-wide signature propagation. Net LOC MUST be negative per file. MRO mixin extraction is last resort only.

**Tech Stack:** Python 3.13, Pydantic v2, `qlty`, `scope`, `sg` (ast-grep), `ruff`, `pyrefly`, `pytest`, `make check`

---

## Ground Rules (read before touching any file)

- **Reduction ladder order** (exhaust each step before the next):
  1. Delete dead code (zero callers via `scope callers <Symbol>`)
  2. Delete compat aliases and pass-throughs (`OldX = NewX`, `def old(): return new()`)
  3. Replace custom code with Pydantic 2 / Python 3.13 primitive (see §0.1 ladder)
  4. Absorb into existing canonical origin (`u.*`, `m.*`, parent class method)
  5. Extract as MRO mixin **only if file is still >200 LOC** after steps 1–4
- **Per-edit gate**: `ruff check <file> && pyrefly check <file>` after EVERY edit — no exceptions
- **Per-file gate**: `pytest flext-core/tests/ -x --tb=short` after each file is done
- **Propagation**: `sg -p '<OldSymbol>' -r '<NewSymbol>' --lang py flext-*/src` for any deleted/renamed symbol in same cycle
- **Never**: add `# type: ignore`, `# noqa`, `# pyrefly: ignore` — fix root cause only
- **Never**: introduce new helpers/wrappers/proxies
- **Never**: leave a compat alias behind when deleting a symbol

---

## Task 0: Violation Inventory

**Files:**
- Read: `flext-core/src/flext_core/` (all `.py`)

- [ ] **Step 1: Run qlty smells across flext-core**

```bash
cd /home/marlonsc/flext
qlty smells --all --sarif --include-tests > /tmp/qlty_smells_flext_core.json
jq '[.runs[].results[] | select(.locations[].physicalLocation.artifactLocation.uri | contains("flext-core"))] | length' /tmp/qlty_smells_flext_core.json
```

Expected: count of total flext-core smells (the baseline to beat)

- [ ] **Step 2: Get full god-module list via tokei**

```bash
tokei flext-core/src/ --output json | python3 -c "
import json, sys
data = json.load(sys.stdin)
files = []
for lang, info in data.items():
    if isinstance(info, dict) and 'reports' in info:
        for r in info['reports']:
            if r['stats']['code'] > 200:
                files.append((r['stats']['code'], r['name']))
for lc, name in sorted(files, reverse=True):
    print(f'{lc:5d}  {name}')
"
```

Expected: list of all files with >200 logical LOC, sorted descending. Save this output to `/tmp/god_modules.txt`.

- [ ] **Step 3: Baseline test count**

```bash
pytest flext-core/tests/ --co -q 2>/dev/null | tail -3
```

Expected: test count (must not decrease after the sweep)

- [ ] **Step 4: Commit baseline evidence**

```bash
git add /tmp/god_modules.txt 2>/dev/null || true
git -C flext-core commit --allow-empty -m "chore(flext-core): record god-module baseline before enforcement sweep"
```

---

## Task 1: Reduce `_constants/enforcement.py` (1,357 LOC)

**Files:**
- Modify: `flext-core/src/flext_core/_constants/enforcement.py`
- Modify: `flext-core/src/flext_core/constants.py` (if facade composes it)

- [ ] **Step 1: Map callers and smell profile**

```bash
scope callers FlextCoreConstantsEnforcement 2>/dev/null || \
  sg -p 'FlextCoreConstantsEnforcement' --lang py flext-core/src flext-core/tests | head -40
qlty smells flext-core/src/flext_core/_constants/enforcement.py
```

Note the smell categories. Focus on `identical-code`, `long-method`, `large-class`, `complex-method`.

- [ ] **Step 2: Apply deletion ladder — dead symbols**

```bash
# For each top-level symbol in the file:
scope callers <SymbolName> 2>/dev/null | grep -v "enforcement.py"
```

If caller count (excluding self) = 0 → delete the symbol AND its tests. Repeat for each symbol.

- [ ] **Step 3: Collapse repeated rule-entry patterns**

Look for patterns like:
```python
RULE_FOO = EnforcementRule(id="ENFORCE-001", kind="...", description="...")
RULE_BAR = EnforcementRule(id="ENFORCE-002", kind="...", description="...")
# ... 50 more similar entries
```

Replace with a `RootModel`-backed catalog if all entries share the same shape:
```python
from flext_core import m


class FlextCoreConstantsEnforcementCatalog(m.RootModel[list[m.EnforcementRule]]):
    """Typed catalog — validated at import, zero custom dispatch."""

    root: list[m.EnforcementRule] = [
        m.EnforcementRule(id="ENFORCE-001", kind="...", description="..."),
        # ...
    ]

    def by_id(self, rule_id: str) -> m.EnforcementRule | None:
        return next((r for r in self.root if r.id == rule_id), None)
```

This eliminates dozens of module-level variable declarations in favor of one validated model.

- [ ] **Step 4: Gate**

```bash
ruff check flext-core/src/flext_core/_constants/enforcement.py
pyrefly check flext-core/src/flext_core/_constants/enforcement.py
pytest flext-core/tests/ -x --tb=short -q
tokei flext-core/src/flext_core/_constants/enforcement.py
```

Expected: 0 ruff errors, 0 pyrefly errors, all tests pass, LOC ≤ 200.
If still >200: extract remaining concerns as MRO mixin per reduction ladder step 5.

- [ ] **Step 5: Propagate any removed/renamed symbols**

```bash
# For each deleted or renamed symbol:
sg -p '<OldSymbol>' --lang py flext-*/src flext-*/tests 2>/dev/null | grep -v "enforcement.py"
# Update each caller site to use new canonical path
sg -p '<OldSymbol>' -r '<NewCanonicalPath>' --lang py flext-*/src
```

- [ ] **Step 6: Commit**

```bash
git add flext-core/src/flext_core/_constants/enforcement.py
git commit -m "refactor(flext-core): reduce enforcement constants god module — net LOC negative"
```

---

## Task 2: Reduce `_utilities/beartype_engine.py` (1,331 LOC)

**Files:**
- Modify: `flext-core/src/flext_core/_utilities/beartype_engine.py`
- Modify: `flext-core/src/flext_core/utilities.py` (facade)

- [ ] **Step 1: Map callers and smells**

```bash
scope callers FlextUtilitiesBeartypeEngine 2>/dev/null | head -30
qlty smells flext-core/src/flext_core/_utilities/beartype_engine.py
```

- [ ] **Step 2: Delete validator methods already in `u.*` or parent**

```bash
sg -p 'def $method(self, $$$):' --lang py flext-core/src/flext_core/_utilities/beartype_engine.py | head -40
```

For each method found: check if an equivalent exists in another `_utilities/*.py` file:
```bash
sg -p 'def $method($$$):' --lang py flext-core/src/flext_core/_utilities/
```

If duplicate found → delete local copy, update callers to use canonical origin.

- [ ] **Step 3: Replace manual isinstance chains with TypeIs**

Look for patterns like:
```python
def check_type(value: object) -> bool:
    if isinstance(value, str):
        return True
    if isinstance(value, int):
        return True
    return False
```

Replace with:
```python
from typing import TypeIs
from flext_core import t


def is_valid_type(value: object) -> TypeIs[t.GuardInput]:
    return isinstance(value, t.GuardInput)
```

- [ ] **Step 4: Replace multi-branch isinstance dispatch with match/case**

Look for:
```python
if isinstance(x, ModelA):
    return self._handle_a(x)
elif isinstance(x, ModelB):
    return self._handle_b(x)
elif isinstance(x, ModelC):
    return self._handle_c(x)
```

Replace with:
```python
match x:
    case ModelA():
        return self._handle_a(x)
    case ModelB():
        return self._handle_b(x)
    case ModelC():
        return self._handle_c(x)
    case _:
        return r.fail_op("unexpected type", context={"type": type(x).__name__})
```

- [ ] **Step 5: Gate**

```bash
ruff check flext-core/src/flext_core/_utilities/beartype_engine.py
pyrefly check flext-core/src/flext_core/_utilities/beartype_engine.py
pytest flext-core/tests/ -x --tb=short -q
tokei flext-core/src/flext_core/_utilities/beartype_engine.py
```

Expected: 0 errors, all tests pass, LOC ≤ 200.

- [ ] **Step 6: Propagate and commit**

```bash
# Propagate any deleted/renamed methods
sg -p '<OldMethod>' -r '<CanonicalMethod>' --lang py flext-*/src flext-*/tests
git add flext-core/src/flext_core/_utilities/beartype_engine.py
git commit -m "refactor(flext-core): reduce beartype_engine god module via TypeIs + dedup"
```

---

## Task 3: Reduce `container.py` (1,084 LOC)

**Files:**
- Modify: `flext-core/src/flext_core/container.py`
- Read: `flext-core/src/flext_core/_models/container.py` (396 LOC — may duplicate)

- [ ] **Step 1: Identify duplication between container.py and _models/container.py**

```bash
scope callers FlextContainer 2>/dev/null | head -30
# Compare method names between the two files
sg -p 'def $method($$$):' --lang py flext-core/src/flext_core/container.py | sort > /tmp/container_methods.txt
sg -p 'def $method($$$):' --lang py flext-core/src/flext_core/_models/container.py | sort > /tmp/model_container_methods.txt
diff /tmp/container_methods.txt /tmp/model_container_methods.txt
```

- [ ] **Step 2: Delete proxy methods in container.py that delegate to _models**

Look for:
```python
def register(self, interface: type, impl: type) -> None:
    return self._inner.register(interface, impl)  # proxy!
```

Delete the proxy. Update callers to use `_inner` directly, or absorb `_models/container.py` into the MRO inheritance chain.

- [ ] **Step 3: Replace manual wiring with DI primitives from dependency_injector via u.***

Look for manual `providers.Singleton(...)` construction inline — replace with `@u.factory` decorator pattern already in `flext_core`.

- [ ] **Step 4: Gate**

```bash
ruff check flext-core/src/flext_core/container.py
pyrefly check flext-core/src/flext_core/container.py
pytest flext-core/tests/ -x --tb=short -q
tokei flext-core/src/flext_core/container.py
```

Expected: 0 errors, all tests pass, LOC ≤ 200.

- [ ] **Step 5: Propagate and commit**

```bash
sg -p '<OldContainerMethod>' -r '<NewPath>' --lang py flext-*/src flext-*/tests
git add flext-core/src/flext_core/container.py flext-core/src/flext_core/_models/container.py
git commit -m "refactor(flext-core): reduce container god module — delete proxy methods"
```

---

## Task 4: Reduce `result.py` (966 LOC)

**Files:**
- Modify: `flext-core/src/flext_core/result.py`

- [ ] **Step 1: Find convenience wrappers that duplicate r[T] DSL**

```bash
scope callers r 2>/dev/null | head -20
sg -p 'def $f($$$): return r.$g($$$)' --lang py flext-core/src/flext_core/result.py
```

Any function that just wraps `r.fail_op`, `r.fail_exc`, `r.ok` → delete, update callers.

- [ ] **Step 2: Replace cast() with TypeIs inside result.py (one of the few allowed uses)**

Verify that `cast()` inside `result.py` is ONLY in the core result type narrowing path. Any `cast()` outside that exact path → replace with `TypeIs` narrowing:

```python
# Before (forbidden outside core path):
return cast(Success[T], result)


# After:
def is_success(result: r[T]) -> TypeIs[Success[T]]:
    return result.is_ok()


if is_success(result):
    # TypeIs narrows here automatically
    use(result.unwrap())
```

- [ ] **Step 3: Delete deprecated combinator aliases**

```bash
sg -p '$old = $new' --lang py flext-core/src/flext_core/result.py
```

Any `old_name = new_name` alias → delete, propagate `sg` rename to callers.

- [ ] **Step 4: Gate**

```bash
ruff check flext-core/src/flext_core/result.py
pyrefly check flext-core/src/flext_core/result.py
pytest flext-core/tests/ -x --tb=short -q
tokei flext-core/src/flext_core/result.py
```

- [ ] **Step 5: Commit**

```bash
git add flext-core/src/flext_core/result.py
git commit -m "refactor(flext-core): reduce result.py — delete wrappers, replace cast with TypeIs"
```

---

## Task 5: Reduce `decorators.py` (882 LOC)

**Files:**
- Modify: `flext-core/src/flext_core/decorators.py`

- [ ] **Step 1: Find decorators that are Pydantic 2 primitives in disguise**

```bash
scope callers FlextCoreDecorators 2>/dev/null | head -20
qlty smells flext-core/src/flext_core/decorators.py | head -30
```

Look for decorators that just call `field_validator`, `model_validator`, `computed_field` — these can be deleted; callers use Pydantic directly via `u.*`.

- [ ] **Step 2: Find duplicate decorator logic already in u.* or parent class**

```bash
sg -p 'def $decorator($$$):' --lang py flext-core/src/flext_core/decorators.py
# Cross-reference with utilities:
sg -p 'def $decorator($$$):' --lang py flext-core/src/flext_core/_utilities/
```

Delete any decorator in `decorators.py` that is already in `_utilities/`.

- [ ] **Step 3: Replace repeated `functools.wraps` + forwarding patterns with `@override`**

```python
# Before (forbidden pass-through):
@functools.wraps(original)
def wrapper(*args, **kwargs):
    return original(*args, **kwargs)


# After: delete wrapper, update callers to use original directly
```

- [ ] **Step 4: Gate**

```bash
ruff check flext-core/src/flext_core/decorators.py
pyrefly check flext-core/src/flext_core/decorators.py
pytest flext-core/tests/ -x --tb=short -q
tokei flext-core/src/flext_core/decorators.py
```

- [ ] **Step 5: Commit**

```bash
git add flext-core/src/flext_core/decorators.py
git commit -m "refactor(flext-core): reduce decorators.py — delete Pydantic-primitive wrappers"
```

---

## Task 6: Reduce `runtime.py` (808 LOC) + `_models/enforcement.py` (801 LOC)

**Files:**
- Modify: `flext-core/src/flext_core/runtime.py`
- Modify: `flext-core/src/flext_core/_models/enforcement.py`

### runtime.py

- [ ] **Step 1: Find alias re-exports already in __init__.py**

```bash
sg -p '$alias = $Class' --lang py flext-core/src/flext_core/runtime.py | head -20
sg -p '$alias = $Class' --lang py flext-core/src/flext_core/__init__.py | head -20
```

Any alias in `runtime.py` that also appears in `__init__.py` (the auto-generated export) → delete from `runtime.py`. The canonical source is `__init__.py`.

- [ ] **Step 2: Delete methods that are just `super()` forwarding**

```bash
sg -p 'def $m(self, $$$): return super().$m($$$)' --lang py flext-core/src/flext_core/runtime.py
```

Delete each. Callers inherit from parent directly.

### _models/enforcement.py

- [ ] **Step 3: Delete model fields duplicated from _constants/enforcement.py**

If a `FlextCoreModelsEnforcement` field stores data that is already in a `c.Enforcement.*` constant → replace field with `computed_field` referencing the constant, or delete the field and use the constant directly at call sites.

```python
# Before (duplication):
class EnforcementRule(m.BaseModel):
    severity: str = "error"  # duplicates c.Enforcement.DEFAULT_SEVERITY


# After:
class EnforcementRule(m.BaseModel):
    severity: str = m.Field(default_factory=lambda: c.Enforcement.DEFAULT_SEVERITY)
```

- [ ] **Step 4: Replace homogeneous collections with RootModel**

```python
# Before (god-class with 50 fields, all same type):
class FlextCoreModelsEnforcementCatalog(m.BaseModel):
    rule_001: EnforcementRule = ...
    rule_002: EnforcementRule = ...
    # ... 48 more


# After:
class FlextCoreModelsEnforcementCatalog(m.RootModel[list[EnforcementRule]]):
    root: list[EnforcementRule] = []
```

- [ ] **Step 5: Gate both files**

```bash
ruff check flext-core/src/flext_core/runtime.py flext-core/src/flext_core/_models/enforcement.py
pyrefly check flext-core/src/flext_core/runtime.py flext-core/src/flext_core/_models/enforcement.py
pytest flext-core/tests/ -x --tb=short -q
tokei flext-core/src/flext_core/runtime.py flext-core/src/flext_core/_models/enforcement.py
```

- [ ] **Step 6: Commit**

```bash
git add flext-core/src/flext_core/runtime.py flext-core/src/flext_core/_models/enforcement.py
git commit -m "refactor(flext-core): reduce runtime + enforcement models — delete re-exports and duplicates"
```

---

## Task 7: Reduce Remaining God Modules (handlers, settings, registry, and all >200 LOC from tokei output)

**Files:**
- Modify: `flext-core/src/flext_core/handlers.py` (665)
- Modify: `flext-core/src/flext_core/settings.py` (613)
- Modify: `flext-core/src/flext_core/registry.py` (603)
- Modify: `flext-core/src/flext_core/_utilities/enforcement.py` (567)
- Modify: `flext-core/src/flext_core/_protocols/result.py` (531)
- Modify: `flext-core/src/flext_core/loggings.py` (510)
- Modify: all other files in `/tmp/god_modules.txt` not yet addressed

For each file, apply the same reduction ladder:

- [ ] **Step 1: handlers.py — replace if/elif dispatch with singledispatch**

```bash
scope callers FlextCoreHandlers 2>/dev/null | head -20
qlty smells flext-core/src/flext_core/handlers.py | head -20
```

Look for:
```python
def handle(self, command: object) -> r[t.Any]:
    if isinstance(command, CommandA):
        return self._handle_a(command)
    elif isinstance(command, CommandB):
        return self._handle_b(command)
    # ... 20 more branches
```

Replace with `@singledispatch`:
```python
from functools import singledispatch
from flext_core import r, t


@singledispatch
def _handle_dispatch(command: object) -> r[None]:
    return r.fail_op(
        "unregistered command type", context={"type": type(command).__name__}
    )


@_handle_dispatch.register
def _(command: CommandA) -> r[CommandAResult]: ...
```

- [ ] **Step 2: settings.py — delete manual env-reading**

```bash
sg -p 'os.environ[$$$]' --lang py flext-core/src/flext_core/settings.py
sg -p 'os.getenv($$$)' --lang py flext-core/src/flext_core/settings.py
```

Any `os.environ`/`os.getenv` in `src/` is FORBIDDEN. Replace with `FlextSettings` field with `env_prefix` resolution:

```python
# Before (forbidden):
db_host = os.environ.get("FLEXT_DB_HOST", "localhost")


# After:
class FlextCoreSettings(FlextSettings):
    model_config = m.ConfigDict(env_prefix="FLEXT_", extra="ignore")
    db_host: str = m.Field(default=c.Core.DEFAULT_DB_HOST)
```

- [ ] **Step 3: registry.py — replace manual scan loops with TypeAdapter-cached lookups**

```bash
qlty smells flext-core/src/flext_core/registry.py | head -20
```

Look for repeated iteration patterns:
```python
def find_by_name(self, name: str) -> type | None:
    for cls in self._registry:
        if cls.__name__ == name:
            return cls
    return None
```

Replace with `TypeAdapter`-backed cached index built at registration time — O(1) lookup:
```python
from functools import cached_property
from pydantic import TypeAdapter  # via u.* in flext-core only


class FlextCoreRegistry(m.BaseModel):
    _entries: list[type] = m.PrivateAttr(default_factory=list)
    _index: dict[str, type] = m.PrivateAttr(default_factory=dict)

    def register(self, cls: type) -> None:
        self._entries.append(cls)
        self._index[cls.__name__] = cls

    def find_by_name(self, name: str) -> type | None:
        return self._index.get(name)
```

- [ ] **Step 4: _utilities/enforcement.py — absorb into FlextUtilitiesBeartypeEngine**

```bash
scope callers FlextUtilitiesEnforcement 2>/dev/null | head -20
```

Methods in `_utilities/enforcement.py` that duplicate `beartype_engine.py` → delete, update callers to `FlextUtilitiesBeartypeEngine.<method>` directly.

- [ ] **Step 5: _protocols/result.py — delete protocol methods already in parent**

```bash
sg -p 'def $m(self, $$$) -> $R: ...' --lang py flext-core/src/flext_core/_protocols/result.py | head -20
```

Any protocol method declared in a parent protocol → delete. Use `@override` in concrete implementations instead of re-declaring the signature.

- [ ] **Step 6: loggings.py — replace config helpers with FlextLogger directly**

```bash
scope callers FlextCoreLoggings 2>/dev/null | head -20
```

Config helpers that wrap `structlog` native API → delete. Callers use `FlextLogger` from `flext_core` directly.

- [ ] **Step 7: Gate all remaining files**

```bash
ruff check flext-core/src/flext_core/handlers.py flext-core/src/flext_core/settings.py \
  flext-core/src/flext_core/registry.py flext-core/src/flext_core/_utilities/enforcement.py \
  flext-core/src/flext_core/_protocols/result.py flext-core/src/flext_core/loggings.py
pyrefly check flext-core/src/
pytest flext-core/tests/ --tb=short -q
tokei flext-core/src/ | grep -E "^\s+[2-9][0-9]{2,}" || echo "No files >200 LOC — CLEAN"
```

- [ ] **Step 8: Final Phase 1 gate**

```bash
make check PROJECT=flext-core
```

Expected: all gates green. Stop here if any gate is red — fix before Phase 2.

- [ ] **Step 9: Commit**

```bash
git add flext-core/src/
git commit -m "refactor(flext-core): Phase 1 complete — all god modules ≤200 LOC, net LOC negative"
```

---

## Task 8: Phase 2 — Compat Alias Extermination (§3.5)

**Files:**
- Modify: all `flext-core/src/flext_core/**/*.py` with aliases or pass-throughs

- [ ] **Step 1: Find all module-level compat aliases**

```bash
sg -p '$Old = $New' --lang py flext-core/src/ | grep -v "^#" | grep -v "__all__"
```

For each result: verify `$Old != $New` (not a runtime alias like `c = FlextCoreConstants`) — only compat `OldName = NewName` aliases. Delete each and propagate callers:

```bash
sg -p '$OldName' -r '$NewName' --lang py flext-*/src flext-*/tests
```

- [ ] **Step 2: Find all pass-through functions**

```bash
sg -p 'def $f($A): return $g($A)' --lang py flext-core/src/
sg -p 'def $f($A, $B): return $g($A, $B)' --lang py flext-core/src/
sg -p 'def $f($$$): return $g($$$)' --lang py flext-core/src/
```

For each: delete `$f`, update callers to call `$g` directly. Same cycle.

- [ ] **Step 3: Find non-canonical class names in src/**

```bash
# src/ classes must be Flext<Project><Tier>
sg -p 'class $Name($$$):' --lang py flext-core/src/ | \
  grep -v "class Flext" | grep -v "class _" | grep -v "^#"
```

Rename each non-canonical class to `Flext<Project><Tier>` pattern and propagate:
```bash
sg -p 'OldClassName' -r 'NewClassName' --lang py flext-*/src flext-*/tests
```

- [ ] **Step 4: Find non-canonical test class names**

```bash
# tests/ classes must be TestsFlext<Project><Tier>
sg -p 'class $Name($$$):' --lang py flext-core/tests/ | \
  grep -v "class TestsFlext" | grep -v "^#"
```

Rename each to `TestsFlext<Project><Tier>`.

- [ ] **Step 5: Gate**

```bash
ruff check flext-core/src/ flext-core/tests/
pyrefly check flext-core/src/ flext-core/tests/
pytest flext-core/tests/ --tb=short -q
make check PROJECT=flext-core
```

- [ ] **Step 6: Commit**

```bash
git add flext-core/src/ flext-core/tests/
git commit -m "refactor(flext-core): Phase 2 complete — zero compat aliases, zero pass-through wrappers"
```

---

## Task 9: Phase 3 — Typing Violations (§3.2)

**Files:**
- Modify: all `flext-core/src/flext_core/**/*.py` with `Any`, `cast`, `object`, suppression hints

- [ ] **Step 1: Find all Any usage outside allowed locations**

```bash
sg -p 'Any' --lang py flext-core/src/ | grep -v "result.py" | grep -v "t.GuardInput"
```

For each: replace with most-restrictive type available — check `t.*` first:
```python
# Before (forbidden):
def process(value: Any) -> Any: ...


# After (use t.GuardInput union or specific union):
from flext_core import t


def process(value: t.GuardInput) -> t.Scalar: ...
```

- [ ] **Step 2: Find all cast() outside result.py**

```bash
sg -p 'cast($T, $v)' --lang py flext-core/src/ | grep -v "result.py"
```

For each: replace with `TypeIs` narrowing:
```python
# Before (forbidden):
result = cast(SuccessResult, maybe_result)

# After:
from typing import TypeIs


def is_success_result(v: object) -> TypeIs[SuccessResult]:
    return isinstance(v, SuccessResult)


if is_success_result(maybe_result):
    use(maybe_result)  # TypeIs narrows automatically
```

- [ ] **Step 3: Find all bare object parameters**

```bash
sg -p 'def $f($a: object, $$$):' --lang py flext-core/src/
sg -p '$a: object' --lang py flext-core/src/ | head -20
```

Replace `object` with `t.GuardInput` or specific union type.

- [ ] **Step 4: Find all suppression hints**

```bash
sg -p '# type: ignore' --lang py flext-core/src/ flext-core/tests/
sg -p '# pyrefly: ignore' --lang py flext-core/src/ flext-core/tests/
sg -p '# noqa' --lang py flext-core/src/ flext-core/tests/
```

For each: delete the hint. Fix the underlying type error structurally (correct base class, correct Pydantic MRO, correct `@override` placement).

- [ ] **Step 5: Verify with make pol**

```bash
make pol PROJECT=flext-core
```

Expected: 0 `Any` violations, 0 `type: ignore` in src/.

- [ ] **Step 6: Gate**

```bash
ruff check flext-core/src/ flext-core/tests/
pyrefly check flext-core/src/
pytest flext-core/tests/ --tb=short -q
make check PROJECT=flext-core
```

- [ ] **Step 7: Commit**

```bash
git add flext-core/src/ flext-core/tests/
git commit -m "refactor(flext-core): Phase 3 complete — zero Any/cast/object/noqa violations"
```

---

## Task 10: Phase 4 — Cross-Project Propagation (all 33 consumers)

**Files:**
- Modify: `flext-*/src/` for all projects consuming changed flext-core symbols

- [ ] **Step 1: Collect all changed/deleted symbols from Phases 1–3**

```bash
git log --oneline flext-core/ | head -20
git diff HEAD~10..HEAD -- flext-core/src/ | grep "^-.*def \|^-.*class " | head -40
```

Build a list: `removed_symbols.txt` — one `OldSymbol → NewPath` per line (or `OldSymbol → DELETED`).

- [ ] **Step 2: Find all consumers of each removed symbol workspace-wide**

```bash
# For each symbol in removed_symbols.txt:
sg -p '<OldSymbol>' --lang py flext-*/src flext-*/tests 2>/dev/null | grep -v "flext-core/"
```

- [ ] **Step 3: Propagate renames via sg**

```bash
# For each renamed symbol:
sg -p 'OldSymbol' -r 'NewSymbol' --lang py flext-*/src flext-*/tests
```

- [ ] **Step 4: Fix broken imports for deleted symbols**

For symbols that were deleted entirely (no rename):
```bash
# Find all import sites:
sg -p 'from flext_core import $$$OldSymbol$$$' --lang py flext-*/src flext-*/tests
# Update to use the canonical replacement or remove if dead import
```

- [ ] **Step 5: Gate each affected consumer**

```bash
# For each project with changes:
for proj in flext-cli flext-infra flext-meltano flext-web flext-api flext-auth flext-tests \
            flext-ldap flext-ldif flext-db-oracle flext-grpc flext-observability flext-plugin \
            flext-quality flext-oracle-oic flext-oracle-wms \
            flext-tap-ldap flext-tap-ldif flext-tap-oracle flext-tap-oracle-oic flext-tap-oracle-wms \
            flext-target-ldap flext-target-ldif flext-target-oracle flext-target-oracle-oic flext-target-oracle-wms \
            flext-dbt-ldap flext-dbt-ldif flext-dbt-oracle flext-dbt-oracle-wms; do
  echo "=== $proj ==="
  ruff check $proj/src/ && pyrefly check $proj/src/ || echo "FAILED: $proj"
done
```

Fix any failures fix-forward before continuing. No compat shims.

- [ ] **Step 6: Workspace-wide final gate**

```bash
make check
make pyre
```

Expected: both exit 0.

- [ ] **Step 7: Final commit**

```bash
git add flext-*/src/ flext-*/tests/
git commit -m "refactor(workspace): Phase 4 complete — propagate flext-core signature changes to all consumers"
```

---

## Final Verification

```bash
# Zero god modules
tokei flext-core/src/ --output json | python3 -c "
import json, sys
data = json.load(sys.stdin)
violations = []
for lang, info in data.items():
    if isinstance(info, dict) and 'reports' in info:
        for r in info['reports']:
            if r['stats']['code'] > 200:
                violations.append((r['stats']['code'], r['name']))
if violations:
    print('VIOLATIONS REMAIN:')
    for lc, name in sorted(violations, reverse=True):
        print(f'  {lc:5d}  {name}')
    sys.exit(1)
else:
    print('CLEAN: zero files >200 logical LOC')
"

# Zero typing violations
make pol PROJECT=flext-core

# Full workspace green
make check
make pyre

# Tests passing
pytest flext-core/tests/ -q
```

Done condition: all 4 commands exit 0.
