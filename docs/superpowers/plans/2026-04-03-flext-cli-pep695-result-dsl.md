# flext-cli PEP 695 Generics + Result DSL Refactoring

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Maximize PEP 695 generics throughout flext-cli, eliminate all `object`/`dict[`/`list[` annotations, reduce `r[T]` ceremony, and remove unnecessary adapters — producing a strict Python 3.13 codebase with zero linter errors.

**Architecture:** Thin Typer Shim — isolate `object` annotations to a single `_TyperBridge` inner class in `cli.py` (~15 lines), replace all other `object` usages with proper `t.*`/`FieldInfo`/`BaseModel` contracts. Add PEP 695 generics to all utility helpers. Replace verbose `r[LongType].ok(val)` patterns with type-inferred `r.ok(val)` where context allows.

**Tech Stack:** Python 3.13, Pydantic v2, PEP 695 type syntax, flext-core `r[T]`, Typer, Rich, tabulate

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `services/cli.py` | Modify | Isolate `object` to `_TyperBridge`, PEP 695 generics on all methods |
| `typings.py` | Modify | Add `FieldInfoMapping`, `CliAnnotations` type aliases |
| `utilities.py` | Modify | PEP 695 generics on `CliModelConverter`, `ModelCommandBuilder`, `CliValidation` |
| `services/file_tools.py` | Modify | Already has generics — replace `list[`/`dict[` locals |
| `services/tables.py` | Modify | Replace `list[` locals with `MutableSequence` |
| `services/output.py` | Modify | Replace `dict[` locals with `MutableMapping`, eliminate `isinstance(val, dict)` |
| `services/commands.py` | Modify | Replace `dict[str, m.Cli.CommandEntryModel]` and `list[str]` |
| `_models/base.py` | Modify | No changes needed (already clean) |
| `protocols.py` | No change | Already uses PEP 695 generics |
| Consumer files (flext-infra, flext-quality, flext-db-oracle) | Verify | Ensure no breakage from signature changes |

---

### Task 1: Add type aliases to `typings.py`

**Files:**
- Modify: `flext-cli/src/flext_cli/typings.py`

- [ ] **Step 1: Add `FieldInfoMapping` and `CliAnnotations` aliases**

In `FlextCliTypes.Cli`, add:

```python
type FieldInfoMapping = Mapping[str, FieldInfo]
type CliAnnotations = MutableMapping[str, type]
```

These replace scattered `dict[str, object]` and `Mapping[str, FieldInfo]` patterns in cli.py and utilities.py.

- [ ] **Step 2: Import additions**

Add to imports:

```python
from collections.abc import Mapping, MutableMapping, Sequence
from pydantic.fields import FieldInfo
```

- [ ] **Step 3: Validate**

Run: `ruff check flext-cli/src/flext_cli/typings.py && pyrefly check flext-cli/src/flext_cli/typings.py`
Expected: 0 errors

- [ ] **Step 4: Commit**

```bash
git add flext-cli/src/flext_cli/typings.py
git commit -m "feat(flext-cli): add FieldInfoMapping and CliAnnotations PEP 695 aliases"
```

---

### Task 2: Refactor `services/cli.py` — Isolate Typer `object` boundary

**Files:**
- Modify: `flext-cli/src/flext_cli/services/cli.py`

- [ ] **Step 1: Replace `_ModelCommand` annotations**

The `_ModelCommand` inner class uses `object` because Typer reads `__annotations__` and `__signature__` at runtime. Typer's `OptionInfo` doesn't expose typed APIs. Keep `object` ONLY in `__call__` (the Typer boundary) and `__annotations__` (Typer introspection). Replace everywhere else:

```python
class _ModelCommand:
    """Callable wrapper with explicit signature for Typer introspection.

    Note: __annotations__ and __call__ use `object` because Typer reads these
    via inspect at runtime and requires unparameterized annotations.
    """

    __annotations__: MutableMapping[str, type]  # Typer introspects this
    __name__: str
    __signature__: Signature
    _settings: BaseModel | None
    _handler: Callable[[BaseModel], None]
    _model_cls: type[BaseModel]

    def __init__(
        self,
        *,
        settings: BaseModel | None,
        handler: Callable[[BaseModel], None],
        model_cls: type[BaseModel],
        parameters: Sequence[Parameter],
    ) -> None:
        self.__name__ = handler.__name__
        self.__signature__ = Signature(parameters)
        self._settings = settings
        self._handler = handler
        self._model_cls = model_cls

    def __call__(self, **kwargs: t.Scalar) -> None:
        if self._settings is not None:
            for field_name, field_value in kwargs.items():
                if hasattr(self._settings, field_name):
                    setattr(self._settings, field_name, field_value)
        self._handler(self._model_cls.model_validate(kwargs))
```

Key changes:
- `_handler` return `object | None` → `None` (handlers don't return values through Typer)
- `parameters: list[Parameter]` → `Sequence[Parameter]`
- `**kwargs: object` → `**kwargs: t.Scalar` (Typer only passes scalars)

- [ ] **Step 2: Replace `_resolve_typer_annotation` signature**

```python
@staticmethod
def _resolve_typer_annotation(annotation: type | TypeAliasType) -> type:
    """Resolve runtime annotations to concrete types accepted by Typer."""
```

The input is always a type or TypeAliasType. The return is always a concrete type. Remove `object` from both sides.

- [ ] **Step 3: Replace `_field_default` signature**

```python
@staticmethod
def _field_default(
    field_name: str, field_info: FieldInfo, settings: BaseModel | None
) -> t.Scalar | None:
    """Resolve CLI default from settings first, then from model field metadata."""
```

`field_info` is always `FieldInfo` (from Pydantic). Return is always a scalar default or None.

- [ ] **Step 4: Replace `_build_model_parameter` signature**

```python
@classmethod
def _build_model_parameter(
    cls,
    field_name: str,
    field_info: FieldInfo,
    settings: BaseModel | None,
) -> tuple[Parameter, type]:
```

Returns `tuple[Parameter, type]` not `tuple[Parameter, object]`.

- [ ] **Step 5: Refactor `model_command[M]` internals**

```python
@classmethod
def model_command[M: BaseModel](
    cls,
    model_cls: type[M],
    handler: Callable[[M], None],
    settings: BaseModel | None = None,
) -> Callable[..., None]:
    """Build a Typer command directly from a Pydantic request model."""
    parameters: MutableSequence[Parameter] = []
    annotations: MutableMapping[str, type] = {"return": type(None)}
    fields: Mapping[str, FieldInfo] = model_cls.model_fields
    for field_name, field_info in fields.items():
        parameter, annotation = cls._build_model_parameter(
            field_name,
            field_info,
            settings,
        )
        parameters.append(parameter)
        annotations[field_name] = annotation
    command = cls._ModelCommand(
        settings=settings,
        handler=lambda model: handler(model_cls.model_validate(model)),
        model_cls=model_cls,
        parameters=parameters,
    )
    command.__annotations__ = dict(annotations)
    return command
```

Key changes:
- `handler: Callable[[M], object | None]` → `Callable[[M], None]`
- Return `Callable[..., object | None]` → `Callable[..., None]`
- `list[Parameter]` → `MutableSequence[Parameter]`
- `dict[str, object]` → `MutableMapping[str, type]`
- `getattr(model_cls, "model_fields", {})` → direct `model_cls.model_fields` (BaseModel always has it)

- [ ] **Step 6: Refactor `derive_model[M]` and `_model_source_data`**

```python
@classmethod
def derive_model[M: BaseModel](
    cls,
    model_cls: type[M],
    *sources: BaseModel | Mapping[str, t.Scalar] | None,
    overrides: Mapping[str, t.Scalar] | None = None,
) -> M:
    """Derive a target Pydantic model from ordered model/mapping sources."""
    merged: MutableMapping[str, t.Scalar] = {}
    for source in sources:
        merged.update(cls._model_source_data(model_cls, source))
    if overrides is not None:
        merged.update(cls._model_source_data(model_cls, overrides))
    return model_cls.model_validate(merged)


@staticmethod
def _model_source_data(
    model_cls: type[BaseModel],
    source: BaseModel | Mapping[str, t.Scalar] | None,
) -> Mapping[str, t.Scalar]:
    """Extract only target-compatible fields from a model or mapping source."""
    if source is None:
        return {}
    raw_source: Mapping[str, t.Scalar]
    if isinstance(source, BaseModel):
        raw_source = source.model_dump(exclude_none=True)
    else:
        raw_source = source
    return {
        field_name: raw_source[field_name]
        for field_name in model_cls.model_fields
        if field_name in raw_source and raw_source[field_name] is not None
    }
```

Replace `object` with `t.Scalar` — model_dump returns scalars, mappings passed in are scalar-valued CLI params.

- [ ] **Step 7: Fix `create_cli_runner` and `register_command`**

```python
@staticmethod
def create_cli_runner(
    *,
    charset: str = "utf-8",
    env: t.StrMapping | None = None,
    echo_stdin: bool = False,
) -> p.Result[CliRunner]:
    return r[CliRunner].ok(
        CliRunner(
            charset=charset, env=dict(env) if env else None, echo_stdin=echo_stdin
        ),
    )


@staticmethod
def register_command(
    app: typer.Typer,
    *,
    name: str,
    help_text: str,
    command: Callable[..., None],
) -> None:
    _ = app.command(name, help=help_text)(command)
```

Changes: `dict[str, str]` → `t.StrMapping`, `Callable[..., object | None]` → `Callable[..., None]`.

- [ ] **Step 8: Add `FieldInfo` import**

```python
from pydantic.fields import FieldInfo
```

- [ ] **Step 9: Validate**

Run: `ruff check flext-cli/src/flext_cli/services/cli.py && pyrefly check flext-cli/src/flext_cli/services/cli.py`
Expected: 0 errors

- [ ] **Step 10: Commit**

```bash
git add flext-cli/src/flext_cli/services/cli.py
git commit -m "refactor(flext-cli): isolate Typer object boundary, PEP 695 strict types in cli.py"
```

---

### Task 3: Refactor `utilities.py` — PEP 695 generics + strict types

**Files:**
- Modify: `flext-cli/src/flext_cli/utilities.py`

- [ ] **Step 1: Make `CliModelConverter.cli_args_to_model` generic**

```python
@staticmethod
def cli_args_to_model[M: BaseModel](
    model_class: type[M],
    cli_args: Mapping[str, t.Cli.JsonValue],
) -> p.Result[M]:
    """Convert CLI args dict to a Pydantic model instance."""
    try:
        instance = model_class.model_validate(cli_args)
        return r[M].ok(instance)
    except ValidationError as exc:
        return r[M].fail(
            f"Validation error for {model_class.__name__}: {exc}",
        )
```

Was `r[BaseModel]` — now generic `r[M]` preserves the concrete model type.

- [ ] **Step 2: Make `ModelCommandBuilder` generic**

```python
class ModelCommandBuilder[M: BaseModel]:
    """Builder for Typer commands from Pydantic models."""

    def __init__(
        self,
        model_class: type[M],
        handler: Callable[[M], t.Cli.JsonValue],
        settings: t.Cli.JsonValue | None = None,
    ) -> None:
        super().__init__()
        self.model_class = model_class
        self.handler = handler
        self.settings = settings
```

- [ ] **Step 3: Replace `list[inspect.Parameter]` locals**

```python
required_parameters: MutableSequence[inspect.Parameter] = []
defaulted_parameters: MutableSequence[inspect.Parameter] = []
```

- [ ] **Step 4: Replace `dict(real_annotations)` casts**

```python
command_wrapper.__annotations__ = dict(real_annotations)
# becomes
setattr(command_wrapper, "__annotations__", dict(real_annotations))
```

Actually the current pattern is fine for Typer introspection. Just ensure the annotation dict uses `MutableMapping[str, type]` not `dict[str, object]`.

- [ ] **Step 5: Validate**

Run: `ruff check flext-cli/src/flext_cli/utilities.py && pyrefly check flext-cli/src/flext_cli/utilities.py`
Expected: 0 errors

- [ ] **Step 6: Commit**

```bash
git add flext-cli/src/flext_cli/utilities.py
git commit -m "refactor(flext-cli): PEP 695 generics on CliModelConverter and ModelCommandBuilder"
```

---

### Task 4: Replace `dict[`/`list[` in `services/tables.py`, `output.py`, `commands.py`

**Files:**
- Modify: `flext-cli/src/flext_cli/services/tables.py`
- Modify: `flext-cli/src/flext_cli/services/output.py`
- Modify: `flext-cli/src/flext_cli/services/commands.py`

- [ ] **Step 1: tables.py — Replace `list[t.Cli.TableRow]` and `list[str]()`**

Line 115: `normalized_rows: list[t.Cli.TableRow] = []` → `normalized_rows: MutableSequence[t.Cli.TableRow] = []`
Line 135: `return list[str]()` → `return []` (type inferred from return type `str | t.StrSequence`)

Add `MutableSequence` to imports:
```python
from collections.abc import Mapping, MutableSequence, Sequence
```

- [ ] **Step 2: output.py — Replace `dict[str, t.Cli.JsonValue]`**

Line 104: `result: dict[str, t.Cli.JsonValue] = {}` → `result: MutableMapping[str, t.Cli.JsonValue] = {}`

Replace `isinstance(value, dict)` and `isinstance(value, list)` with `isinstance(value, Mapping)` and `isinstance(value, Sequence)` (with `not isinstance(value, str)` guard for sequences).

Add `MutableMapping, Sequence` to imports.

- [ ] **Step 3: commands.py — Replace bare `dict` and `list` annotations**

Line 28: `default_factory=dict[str, m.Cli.CommandEntryModel]` — keep (Pydantic requires concrete factory)
Line 161: `cmd_args: list[str] = list(args[1:]) if len(args) > 1 else []` — keep (local mutation, concrete)

These are the `r[T]` invariance exceptions — concrete types inside `PrivateAttr(default_factory=...)` and local mutable variables that don't escape as return types. No change needed.

- [ ] **Step 4: Validate all three files**

Run: `ruff check flext-cli/src/flext_cli/services/tables.py flext-cli/src/flext_cli/services/output.py flext-cli/src/flext_cli/services/commands.py && pyrefly check flext-cli/src/flext_cli/services/tables.py flext-cli/src/flext_cli/services/output.py flext-cli/src/flext_cli/services/commands.py`
Expected: 0 errors

- [ ] **Step 5: Commit**

```bash
git add flext-cli/src/flext_cli/services/tables.py flext-cli/src/flext_cli/services/output.py flext-cli/src/flext_cli/services/commands.py
git commit -m "refactor(flext-cli): replace dict[]/list[] annotations with abstract types"
```

---

### Task 5: Verify consumer projects compile clean

**Files:**
- Verify: `flext-infra/src/flext_infra/` (main consumer)
- Verify: `flext-quality/src/flext_quality/`
- Verify: `flext-db-oracle/src/flext_db_oracle/cli.py`

- [ ] **Step 1: Run ruff on consumers**

```bash
ruff check flext-infra/src/ flext-quality/src/ flext-db-oracle/src/
```

Expected: 0 errors (signature changes are backward-compatible — `Mapping` accepts `dict`, `Sequence` accepts `list`)

- [ ] **Step 2: Run pyrefly on consumers**

```bash
pyrefly check flext-infra/src/ flext-quality/src/ flext-db-oracle/src/
```

Expected: 0 errors

- [ ] **Step 3: Fix any breakage**

If `Callable[[M], object | None]` → `Callable[[M], None]` breaks a consumer that returns a value from a handler, add the return value to the handler's `None` return via a local variable (the value is discarded by Typer anyway).

- [ ] **Step 4: Run tests**

```bash
pytest flext-cli/tests/ -x --tb=short -q
```

Expected: All pass

- [ ] **Step 5: Commit fixes if any**

```bash
git add -A
git commit -m "fix(consumers): adapt to flext-cli strict type signatures"
```

---

### Task 6: Final validation — full linter sweep

**Files:**
- All modified files

- [ ] **Step 1: Full ruff check**

```bash
ruff check flext-cli/src/
```

Expected: 0 errors

- [ ] **Step 2: Full pyrefly check**

```bash
pyrefly check flext-cli/src/
```

Expected: 0 errors

- [ ] **Step 3: Full pytest**

```bash
pytest flext-cli/tests/ -x --tb=short -q
```

Expected: All pass

- [ ] **Step 4: Cross-project validation**

```bash
ruff check flext-infra/src/ flext-quality/src/ flext-db-oracle/src/
pyrefly check flext-infra/src/ flext-quality/src/ flext-db-oracle/src/
```

Expected: 0 errors
