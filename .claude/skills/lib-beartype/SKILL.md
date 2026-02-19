<!-- TOC START -->
- [Scope](#scope)
  - [Subproject Usage Map](#subproject-usage-map)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
- [Workflow](#workflow)
- [Examples](#examples)
- [Verification](#verification)
<!-- TOC END -->

---
name: lib-beartype
description: Package-wide beartype integration for flext_core runtime checks. Trigger when changing runtime type-check activation, config, or error-handling policy.
---

## Scope

- Core implementation: `flext-core/src/flext_core/_beartype_conf.py`, `flext-core/src/flext_core/runtime.py`
- Public export: `flext-core/src/flext_core/__init__.py`
- Dependency pinning: `flext-core/pyproject.toml`

### Subproject Usage Map

- `flext-core`: defines and activates runtime checking (`BEARTYPE_CONF`, `enable_runtime_checking`).
- Other `flext-*` subprojects: do not configure beartype directly; consume `flext_core` behavior.
- Tests and local tooling: may call runtime activation for stricter dev/test checks.

## References

- `flext-core/src/flext_core/_beartype_conf.py`: canonical `BEARTYPE_CONF` declaration
- `flext-core/src/flext_core/runtime.py`: `FlextRuntime.enable_runtime_checking()` and `beartype_package("flext_core", conf=conf)`
- `flext-core/src/flext_core/__init__.py`: re-export via `from flext_core._beartype_conf import BEARTYPE_CONF`
- `flext-core/pyproject.toml`: `beartype>=0.19.0`

## Rules

- Keep beartype configuration centralized in `_beartype_conf.py` and runtime bridge.
- Never decorate individual project functions/classes with `@beartype`; use package-level claw activation.
- Treat runtime checking as opt-in for development/test unless explicitly justified for production.
- Keep config values explicit and aligned with canonical settings:
  - `strategy=BeartypeStrategy.Ologn`
  - `is_color=True`
  - `claw_is_pep526=False`
  - `warning_cls_on_decorator_exception=UserWarning`
- Reuse `BEARTYPE_CONF` export in integrations instead of creating ad hoc `BeartypeConf` objects.

## Instructions

- Ground changes in these declarations:

```python
# flext-core/src/flext_core/_beartype_conf.py

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment

from beartype import BeartypeConf, BeartypeStrategy

BEARTYPE_CONF = BeartypeConf(
    strategy=BeartypeStrategy.Ologn,
    is_color=True,
    claw_is_pep526=False,
    warning_cls_on_decorator_exception=UserWarning,
)
```

```python
# flext-core/src/flext_core/runtime.py
from beartype import BeartypeConf, BeartypeStrategy
from beartype.claw import beartype_package

@staticmethod
def enable_runtime_checking() -> bool:
    conf = BeartypeConf(
        strategy=BeartypeStrategy.Ologn,
        is_color=True,
        claw_is_pep526=False,
        warning_cls_on_decorator_exception=UserWarning,
    )
    beartype_package("flext_core", conf=conf)
    return True
```

- Preferred import patterns:
  - `from flext_core import BEARTYPE_CONF, FlextRuntime`
  - Avoid `from beartype import beartype` in app-level modules.
- If behavior changes, update both runtime activation path and public export expectations.

## Workflow

1. Confirm canonical settings in `_beartype_conf.py` before any edits.
2. Apply activation changes in `FlextRuntime.enable_runtime_checking()` only.
3. Ensure package-wide activation still targets `"flext_core"`.
4. Verify public API exposure of `BEARTYPE_CONF` remains intact.
5. Verify no module-level `@beartype` usage was introduced.

## Examples

Good:

```python
from flext_core import FlextRuntime

enabled = FlextRuntime.enable_runtime_checking()
assert enabled is True
```

Why good: activates one package-wide policy through the runtime bridge, consistent with repository architecture.

Bad:

```python
from beartype import beartype

@beartype
def parse_payload(payload: dict[str, object]) -> dict[str, object]:
    return payload
```

Why bad: bypasses the project-wide activation model and creates inconsistent local behavior.

Good:

```python
from flext_core import BEARTYPE_CONF
from beartype.claw import beartype_package

beartype_package("flext_core", conf=BEARTYPE_CONF)
```

Why good: reuses canonical config constant and avoids drift in strategy/warning behavior.

Bad:

```python
from beartype import BeartypeConf
from beartype.claw import beartype_package

beartype_package("flext_core", conf=BeartypeConf())
```

Why bad: silent defaults can diverge from required O(log n) strategy and warning semantics.

## Verification

Make gates:

- `make check PROJECT=flext-core` — full lint + type + security gates
- `make check PROJECT=flext-core CHECK_GATES=type` — type-check validates beartype integration
- `make test PROJECT=flext-core` — runtime checks exercised by test suite

Pattern checks:

- `rg -n "BEARTYPE_CONF|BeartypeConf\(|BeartypeStrategy\.Ologn|claw_is_pep526|warning_cls_on_decorator_exception" flext-core/src/flext_core/_beartype_conf.py`
- `rg -n "def enable_runtime_checking|beartype_package\(\"flext_core\", conf=conf\)" flext-core/src/flext_core/runtime.py`
- `rg -n "from flext_core\._beartype_conf import BEARTYPE_CONF|\"BEARTYPE_CONF\"" flext-core/src/flext_core/__init__.py`
- `rg -n "beartype>=0\.19\.0" flext-core/pyproject.toml`
- `rg -n "@beartype" flext-*/src flext-core/src`
