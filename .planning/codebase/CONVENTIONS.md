# Coding Conventions

**Analysis Date:** 2026-03-23

## Naming Patterns

**Files:**
- Public facades: `{name}.py` (e.g., `models.py`, `utilities.py`, `constants.py`)
- Private/internal modules: `_{name}.py` or `_{category}/{name}.py` (e.g., `_utilities/guards.py`, `_models/result.py`)
- Test files: `test_*.py`, `*_test.py`, `*_tests.py` (matched by pytest configuration)
- Subpackage organization: Logical domain grouping in subdirectories like `_models/`, `_utilities/`, `_constants/`, `_protocols/`

**Functions:**
- camelCase is FORBIDDEN. Use snake_case exclusively: `def parse_input()`, `def validate_range()`, `def from_kwargs()`
- Async functions: same snake_case pattern: `async def process_data()`
- Factory functions: `create_*()`, `make_*()`, `from_*()` patterns
- Validation/guard functions: `is_*()`, `ensure_*()`, `check_*()`, `validate_*()`

**Variables:**
- snake_case for all local and module-level variables
- UPPER_CASE for module-level constants and classvars that are truly constant
- Private attributes: prefix with underscore (`self._state`), use Pydantic `PrivateAttr()` for BaseModel fields
- No single-letter variables except loop indices (`i`, `j`) or accepted aliases: `r` (result), `m` (models), `c` (constants), `t` (types), `u` (utilities), `p` (protocols), `h` (helpers), `s` (services), `e` (errors), `d` (dependency), `x` (execution)

**Types:**
- Type aliases: Use PEP 695 `type X = ...` syntax (Python 3.13+) in `typings.py` only
- Never use bare `Any`, `object`, or generic `Mapping[str, Any]`. Use specific `t.*` contracts from typings
- Class names: PascalCase with semantic prefixes: `Flext{Module}{Domain}{Facade}` (e.g., `FlextCoreModels`, `FlextUtilitiesGuards`, `FlextTestInfraHelpers`)
- No backward-compat aliases: never create `LegacyX = NewX` style assignments

**Namespace Aliases (Canonical):**
- `m` = Models (`FlextModels`, `FlextXyzModels`)
- `c` = Constants (`FlextConstants`, `FlextXyzConstants`)
- `t` = Types (`FlextTypes`, `FlextXyzTypes`)
- `u` = Utilities (`FlextUtilities`, `FlextXyzUtilities`)
- `p` = Protocols (`FlextProtocols`, `FlextXyzProtocols`)
- `h` = Helpers (`FlextHelpers` - test/infra helpers only)
- `s` = Services (`FlextServices`, `FlextXyzServices`)
- `r` = Result (railway-oriented programming from `returns` library)
- `e` = Errors/Exceptions
- `d` = Dependency (DI container)
- `x` = Execution/Runtime primitives

Runtime aliases (e.g., `r`, `e`, `d`, `s`, `x`) must be imported from `flext_core` or the project's own package. Test code imports from local `tests` package: `from tests import c, m, t, u, p`.

## Code Style

**Formatting:**
- Line length: 88 characters (configured in ruff)
- Indentation: 4 spaces
- Quote style: Double quotes `"string"` (enforced by Ruff/Black)
- Trailing commas: Yes on multi-line (split-on-trailing-comma = true)
- Line endings: LF only

**Linting:**
- Tool: Ruff (with Black formatter)
- Configuration: `pyproject.toml` `[tool.ruff]` section
- Key settings:
  - `line-length = 88`
  - `target-version = "py313"`
  - `preview = true` (enables newer rules)
  - `fix = true` (auto-fix enabled)
  - Per-file-ignores configured for test, example, exception, script, and generated code sections
- Type checking: Pyright (strict mode) + Mypy + Pyrefly (Python 3.13 diagnostics)

**200-Line Cap (SUPREME LAW):**
- Any module, class, method, or function exceeding 200 logical lines (blank/comments excluded) is a violation
- Must be refactored via OO composition, MRO inheritance, or facade extraction to `_modules/` subdirectories
- FORBIDDEN approaches: removing blank lines, compressing docstrings, arbitrary code splits without domain decomposition
- VALID reduction: deleting dead code, removing unnecessary wrappers, replacing inline type unions with canonical `t.*` contracts

## Import Organization

**Order:**
1. `from __future__ import annotations` (always first)
2. Standard library: `import stdlib_module` or `from stdlib import X`
3. Third-party: `import pandas as pd`, `from pydantic import BaseModel`
4. First-party (flext projects): `from flext_core import FlextModels`
5. Local: `from . import local_module` or `from .module import func`

**Path Aliases:**
- Root imports by class name: `from flext_core import FlextProtocols` (never `from flext_core.protocols import Protocols`)
- Submodule imports only for direct access: `from flext_core._utilities.guards import FlextUtilitiesGuardsEnsure`
- In test code: Use `from tests import c, m, t, u` for local test infrastructure
- Forbidde: Importing private `_` internals outside the module; importing aliases from sibling projects in tests

**Canonical Collections.abc imports:**
All collection type hints must use `collections.abc`: `Mapping`, `Sequence`, `MutableSequence`, `Callable`, `Generator`, `Iterator`
Never use `typing.List`, `typing.Dict`, or `typing.Tuple` – use `list`, `dict`, `tuple` directly or the corresponding `abc` types.

## Error Handling

**Strategy:**
- Fallible operations MUST return `r[T]` (Result type from `returns` library)
- Never use `T | None` for error states; use `r[T]` instead
- Bare `try/except` in business logic is FORBIDDEN when `r` composition (`map`/`flat_map`/`lash`) can handle the flow
- Catch explicit exceptions, never bare `except:` or `except Exception:`
- Domain exceptions inherit from flext exception hierarchy: `FlextError` base with specific subclasses

**Patterns:**
```python
# Correct: Railway-oriented error handling
def process_data(value: str) -> r[ProcessedData]:
    return validate(value).flat_map(parse).flat_map(transform)


# Correct: Explicit exception catching
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Specific failure: {e}")
    return r[T].fail(str(e))

# FORBIDDEN: Bare except or T | None for errors
try:
    result = risky_operation()
except:  # WRONG
    pass


def get_config() -> ConfigData | None:  # WRONG - use r[ConfigData]
    ...
```

## Logging

**Framework:** `structlog` (structured logging)

**Patterns:**
- Use `FlextLogger` abstraction (never `print()` or `logging` directly in production)
- Logger access: `from flext_core import FlextServices` then use `s.get_logger()`
- Log levels: debug < info < warning < error < critical
- Structured context: Use keyword arguments for context fields
- No raw tracebacks in logs; use result/error objects for structured output

```python
from flext_core import s

logger = s.get_logger(__name__)
logger.info("action_started", user_id=user_id, batch_size=count)
logger.warning("high_latency", duration_ms=elapsed, threshold_ms=1000)
```

## Comments

**When to Comment:**
- Explain the WHY, not the WHAT (code should be self-documenting)
- Highlight non-obvious design decisions or trade-offs
- Mark TODO/FIXME with responsibility and timeline: `# TODO(owner): description (target_date)`
- Warn about subtle invariants or performance implications
- Never document trivial logic or iterate over obvious loop structure

**JSDoc/TSDoc:**
- Use module docstrings (triple-quoted at module top) to explain purpose and scope
- Use class docstrings to explain responsibility and key methods
- Use function/method docstrings with:
  - One-line summary
  - Extended description (if needed)
  - Args: with type and description
  - Returns: type and description
  - Raises: exception types and conditions
  - Example: code snippet if behavior is non-obvious

```python
def ensure_valid_port(value: int) -> r[int]:
    """Ensure value is a valid network port number.

    Args:
        value: Integer to validate against port range (1-65535)

    Returns:
        r[int]: Success with validated port, or failure with error message

    Raises:
        Returns r[int].fail() on validation failure (never raises)
    """
```

## Function Design

**Size:**
- Target: 15-30 lines of logical code
- Absolute cap: 200 lines (strict enforcement)
- Single responsibility: one domain concept per function
- Parameters: Maximum 5-7 (use dataclass/Pydantic model if more needed)

**Parameters:**
- Use dataclass or Pydantic models for multiple related parameters
- Keyword-only after 2-3 positional args: `def func(arg1, arg2, *, kwarg1, kwarg2)`
- Type hints MANDATORY for all parameters: `def func(value: str) -> r[Result]:`
- Never use `*args` or `**kwargs` in production code (only test fixtures)

**Return Values:**
- Always include explicit return type: `-> r[T]`, `-> T | None` (if semantically required), `-> None`
- Consistent return across all code paths (no implicit `None` returns)
- Use `r[T]` for operations that can fail, never bare exceptions
- Multi-value returns: Use Pydantic model or named tuple, never bare tuples

## Module Design

**Exports:**
- Public API defined in module docstring and `__all__` list
- Top-level `__init__.py` files are AUTO-GENERATED and EXPORT-ONLY
- Use native `__getattr__` module-level lazy loading pattern (generated via `make codegen`)
- Never manually edit auto-generated `__init__.py` files

**Barrel Files:**
- Organize subpackage exports through `__init__.py` in `_modules/`
- Central facade classes compose all domain subclasses via MRO inheritance
- Example: `FlextModels` inherits from `FlextModelFoundation`, `FlextModelsCqrs`, `FlextModelsEntity`, etc.

**Pydantic v2 Mastery:**
- Every class MUST extend `BaseModel` or FLEXT base models via MRO
- Use `Field()` with constraints, descriptions, and defaults
- Use `model_config = ConfigDict(...)` for serialization/validation settings
- Use `PrivateAttr()` for internal mutable state
- Use `field_validator` or `model_validator` for custom logic
- Forbidde: Standalone `*Config` classes, unnecessary `@property`, manual `self._x` assignments

**MRO Inheritance:**
- Single namespace class per tier: exactly ONE `FlextXyzModels`, `FlextXyzUtilities`, `FlextXyzConstants` per project
- All domain logic resides in this single class via inheritance from `_models/`, `_utilities/`, `_constants/` subclasses
- Loose functions/classes outside MRO hierarchy are FORBIDDEN – absorb into namespace classes
- Subprojects inherit parent facades to cascade namespaces: `class FlextTapOracleProtocols(FlextMeltanoProtocols, FlextOracleProtocols): pass`

---

*Convention analysis: 2026-03-23*
