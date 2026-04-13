# FlextInfraCli MRO Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace scattered argparse/Typer CLIs with one declarative `FlextInfraCli` composed via MRO from per-group `cli.py` mixins, following algar-oud-mig pattern exactly.

**Architecture:** Each group directory gets a `cli.py` with a `FlextInfraCli{Group}` class that has ONE method: `_register_{group}(app)`. Root `cli.py` composes all via MRO into `FlextInfraCli`. Services gain `execute_command(params: m.Infra.XxxInput) -> p.Result[T]`. Each `__main__.py` becomes a 3-line entry point.

**Tech Stack:** `flext_cli.cli` singleton, `m.Cli.ResultCommandRouteModel`, `m.Infra.*Input` Pydantic models, `r[T]` results.

---

## File Structure

### Create (10 files)
- `flext-infra/src/flext_infra/cli.py` — Root `FlextInfraCli` MRO facade
- `flext-infra/src/flext_infra/basemk/cli.py` — `FlextInfraCliBasemk`
- `flext-infra/src/flext_infra/codegen/cli.py` — `FlextInfraCliCodegen`
- `flext-infra/src/flext_infra/docs/cli.py` — `FlextInfraCliDocs`
- `flext-infra/src/flext_infra/github/cli.py` — `FlextInfraCliGithub`
- `flext-infra/src/flext_infra/refactor/cli.py` — `FlextInfraCliRefactor`
- `flext-infra/src/flext_infra/release/cli.py` — `FlextInfraCliRelease`
- `flext-infra/src/flext_infra/validate/cli.py` — `FlextInfraCliValidate`
- `flext-infra/src/flext_infra/workspace/cli.py` — `FlextInfraCliWorkspace`
- `flext-infra/src/flext_infra/maintenance/cli.py` — `FlextInfraCliMaintenance`

### Modify (12 files)
- `flext-infra/src/flext_infra/__main__.py` — thin entry → `FlextInfraCli().run()`
- `flext-infra/src/flext_infra/basemk/__main__.py` — thin entry
- `flext-infra/src/flext_infra/codegen/__main__.py` — thin entry
- `flext-infra/src/flext_infra/docs/__main__.py` — thin entry
- `flext-infra/src/flext_infra/github/__main__.py` — thin entry
- `flext-infra/src/flext_infra/refactor/__main__.py` — thin entry
- `flext-infra/src/flext_infra/release/__main__.py` — thin entry + keep `_resolve_version`/`_resolve_tag` (tests import them)
- `flext-infra/src/flext_infra/validate/__main__.py` — thin entry
- `flext-infra/src/flext_infra/workspace/__main__.py` — thin entry
- `flext-infra/src/flext_infra/maintenance/__main__.py` — thin entry
- `flext-infra/src/flext_infra/_models/cli_inputs.py` — already exists, verify models
- `flext-infra/src/flext_infra/Makefile` (root) — update orchestrate `--projects` flag

### Delete (.bak per CLAUDE.md)
- `flext-infra/src/flext_infra/_utilities/output.py` → `.bak`
- `flext-infra/src/flext_infra/_utilities/terminal.py` → `.bak`
- `flext-infra/src/flext_infra/_utilities/cli.py` → `.bak`
- `flext-infra/src/flext_infra/_utilities/formatting.py` → `.bak`

---

## Reference: algar-oud-mig Pattern

```python
# One class. Services as instance attrs. Routes as data declarations.
class AlgarOudMigrationCli:
    def __init__(self):
        self._app = cli.create_app_with_common_params(name=..., help_text=...)
        self._migration = MigrationService()
        self._register_commands()

    def run(self, args=None) -> p.Result[bool]:
        return cli.execute_app(self._app, prog_name=..., args=args)

    def _register_commands(self):
        cli.register_result_route(
            self._app,
            route=m.Cli.ResultCommandRouteModel(
                name="migrate",
                model_cls=m.AlgarOudMig.MigrateInput,
                handler=self._migration.execute_command,
                success_message="Done",
                failure_message="Failed",
            ),
        )
```

Key: handler IS the service method. `execute_command(params: Input) -> p.Result[T]`.

---

## Task 1: Group CLI Mixin — maintenance (simplest, proves pattern)

**Files:**
- Create: `flext-infra/src/flext_infra/maintenance/cli.py`
- Modify: `flext-infra/src/flext_infra/maintenance/__main__.py`
- Modify: `flext-infra/src/flext_infra/maintenance/python_version.py` (add `execute_command`)

- [ ] **Step 1: Add `execute_command` to service**

In `python_version.py`, add method that accepts the Pydantic model:

```python
def execute_command(self, params: m.Infra.MaintenanceRunInput) -> p.Result[int]:
    """CLI handler — accepts input model, delegates to execute."""
    return self.execute(check_only=params.check, verbose=params.verbose)
```

- [ ] **Step 2: Create `maintenance/cli.py`**

```python
"""CLI mixin for maintenance commands."""

from __future__ import annotations

from flext_cli import cli

from flext_infra import FlextInfraPythonVersionEnforcer, m


class FlextInfraCliMaintenance:
    """Maintenance CLI group — composed into FlextInfraCli via MRO."""

    def _register_maintenance(self, app: object) -> None:
        """Register maintenance commands on the given Typer app."""
        service = FlextInfraPythonVersionEnforcer()
        cli.register_result_route(
            app,
            route=m.Cli.ResultCommandRouteModel(
                name="run",
                help_text="Enforce Python version constraints",
                model_cls=m.Infra.MaintenanceRunInput,
                handler=service.execute_command,
                success_message="Maintenance completed",
                failure_message="Maintenance failed",
            ),
        )
```

- [ ] **Step 3: Rewrite `maintenance/__main__.py` to thin entry**

```python
"""CLI entry point for maintenance."""

from __future__ import annotations

import sys

from flext_infra import t


def main(argv: t.StrSequence | None = None) -> int:
    """Run maintenance CLI."""
    from flext_infra import FlextInfraCli

    try:
        result = FlextInfraCli().run(["maintenance", *(argv or [])])
        return 0 if result.is_success else 1
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Validate**

```bash
.venv/bin/ruff check flext-infra/src/flext_infra/maintenance/ --fix
.venv/bin/pyrefly check flext-infra/src/flext_infra/maintenance/
.venv/bin/pytest flext-infra/tests/unit/test_infra_maintenance_cli.py -x -q
```

---

## Task 2: Group CLI Mixins — basemk, docs, validate, workspace, release, codegen, github, refactor

Same pattern as Task 1, repeated for each group. Each group gets:

1. `{group}/cli.py` with `FlextInfraCli{Group}` class
2. Service gains `execute_command(params) -> p.Result[T]`
3. `__main__.py` becomes thin entry

### Task 2a: basemk/cli.py

**Files:**
- Create: `flext-infra/src/flext_infra/basemk/cli.py`
- Modify: `flext-infra/src/flext_infra/basemk/generator.py` (add `execute_command`)
- Modify: `flext-infra/src/flext_infra/basemk/__main__.py` (thin entry)

- [ ] **Step 1: Add `execute_command` to `FlextInfraBaseMkGenerator`**

```python
def execute_command(self, params: m.Infra.BaseMkGenerateInput) -> p.Result[str]:
    """CLI handler — generate base.mk from params."""
    settings = (
        FlextInfraBaseMkTemplateEngine.default_settings().model_copy(
            update={"project_name": params.project_name},
        )
        if params.project_name
        else None
    )
    result = self.generate_basemk(settings)
    if result.is_failure:
        return result
    if params.output:
        write_result = self.write(result.value, output=Path(params.output))
        if write_result.is_failure:
            return r[str].fail(write_result.error or "write failed")
    else:
        self.write(result.value, stream=sys.stdout)
    return result
```

- [ ] **Step 2: Create `basemk/cli.py`**

```python
"""CLI mixin for basemk commands."""

from __future__ import annotations

from flext_cli import cli

from flext_infra import FlextInfraBaseMkGenerator, m


class FlextInfraCliBasemk:
    """Basemk CLI group — composed into FlextInfraCli via MRO."""

    def _register_basemk(self, app: object) -> None:
        """Register basemk commands."""
        group = cli.create_group(help_text="base.mk generation utilities")
        cli.register_result_route(
            group,
            route=m.Cli.ResultCommandRouteModel(
                name="generate",
                help_text="Generate base.mk from templates",
                model_cls=m.Infra.BaseMkGenerateInput,
                handler=FlextInfraBaseMkGenerator().execute_command,
                success_message="base.mk generated",
                failure_message="base.mk generation failed",
            ),
        )
        cli.add_group(app, name="basemk", group=group)
```

- [ ] **Step 3: Thin `basemk/__main__.py`**

Same 3-line pattern as maintenance but with `["basemk", ...]`.

- [ ] **Step 4: Validate**

```bash
.venv/bin/pytest flext-infra/tests/unit/basemk/ -x -q
```

### Task 2b–2h: docs, validate, workspace, release, codegen, github, refactor

Identical pattern for each group. Each needs:
1. `execute_command(params: m.Infra.XxxInput) -> p.Result[T]` on the service
2. `{group}/cli.py` with `FlextInfraCli{Group}`
3. Thin `__main__.py`
4. Validate tests pass

For **release**: keep `_resolve_version` and `_resolve_tag` as module-level functions in `__main__.py` (tests import them). The handler in the mixin calls them.

For **github**: `u.Infra.github_*` utility methods are the handlers — wrap in thin lambdas in the mixin.

For **codegen**: 8 subcommands — each gets one `register_result_route`.

For **workspace**: `orchestrate` command uses `--projects` flag (space-separated). Makefile updated to pass `--projects "$(SELECTED_PROJECTS)"`.

---

## Task 3: Root FlextInfraCli

**Files:**
- Create: `flext-infra/src/flext_infra/cli.py`

- [ ] **Step 1: Create root cli.py**

```python
"""FlextInfraCli — MRO-composed CLI facade for all flext-infra commands."""

from __future__ import annotations

from typing import ClassVar

from flext_cli import cli
from flext_core import u, r

from flext_infra import t
from flext_infra import FlextInfraCliBasemk
from flext_infra import FlextInfraCliCodegen
from flext_infra import FlextInfraCliDocs
from flext_infra import FlextInfraCliGithub
from flext_infra import FlextInfraCliRefactor
from flext_infra import FlextInfraCliRelease
from flext_infra import FlextInfraCliValidate
from flext_infra import FlextInfraCliWorkspace
from flext_infra import FlextInfraCliMaintenance


class FlextInfraCli(
    FlextInfraCliBasemk,
    FlextInfraCliCodegen,
    FlextInfraCliDocs,
    FlextInfraCliGithub,
    FlextInfraCliMaintenance,
    FlextInfraCliRefactor,
    FlextInfraCliRelease,
    FlextInfraCliValidate,
    FlextInfraCliWorkspace,
):
    """MRO-composed CLI — each mixin registers its group's commands."""

    app_name: ClassVar[str] = "flext-infra"
    app_help: ClassVar[str] = "FLEXT Infrastructure Tooling"

    def __init__(self) -> None:
        """Initialize CLI app and register all group commands via MRO mixins."""
        u.ensure_structlog_configured()
        self._app = cli.create_app_with_common_params(
            name=self.app_name,
            help_text=self.app_help,
        )
        self._register_basemk(self._app)
        self._register_codegen(self._app)
        self._register_docs(self._app)
        self._register_github(self._app)
        self._register_maintenance(self._app)
        self._register_refactor(self._app)
        self._register_release(self._app)
        self._register_validate(self._app)
        self._register_workspace(self._app)

    def run(self, args: t.StrSequence | None = None) -> p.Result[bool]:
        """Execute the CLI application."""
        return cli.execute_app(self._app, prog_name=self.app_name, args=args)
```

- [ ] **Step 2: Rewrite top-level `__main__.py`**

```python
"""CLI entry point for flext-infra."""

from __future__ import annotations

import sys

from flext_infra import FlextInfraCli


def main() -> int:
    """Run flext-infra CLI."""
    try:
        result = FlextInfraCli().run()
        return 0 if result.is_success else 1
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 3: Validate all CLIs**

```bash
.venv/bin/python -m flext_infra --help
.venv/bin/python -m flext_infra basemk --help
.venv/bin/python -m flext_infra codegen --help
.venv/bin/python -m flext_infra docs --help
.venv/bin/python -m flext_infra github --help
.venv/bin/python -m flext_infra maintenance --help
.venv/bin/python -m flext_infra refactor --help
.venv/bin/python -m flext_infra release --help
.venv/bin/python -m flext_infra validate --help
.venv/bin/python -m flext_infra workspace --help
```

---

## Task 4: Delete Dead Code

- [ ] **Step 1: Archive old files**

```bash
mv flext-infra/src/flext_infra/_utilities/output.py flext-infra/src/flext_infra/_utilities/output.py.bak
mv flext-infra/src/flext_infra/_utilities/terminal.py flext-infra/src/flext_infra/_utilities/terminal.py.bak
mv flext-infra/src/flext_infra/_utilities/cli.py flext-infra/src/flext_infra/_utilities/cli.py.bak
```

- [ ] **Step 2: Remove from MRO in `utilities.py`**

Remove `FlextInfraUtilitiesCli`, `FlextInfraUtilitiesOutput`, `FlextInfraUtilitiesTerminal` from `class Infra(...)` bases.

- [ ] **Step 3: Remove dead ANSI constants from `_constants/base.py`**

Remove: `RESET`, `RED`, `GREEN`, `YELLOW`, `BLUE`, `BOLD`, `OK`, `FAIL`, `WARN`, `SKIP`.

- [ ] **Step 4: Validate**

```bash
.venv/bin/ruff check flext-infra/src/ --fix
.venv/bin/pyrefly check flext-infra/src/
.venv/bin/mypy flext-infra/src/
.venv/bin/pyright flext-infra/src/
```

---

## Task 5: Full Validation

- [ ] **Step 1: All linters**

```bash
make check PROJECT=flext-infra CHANGED_ONLY=0
```

- [ ] **Step 2: All tests**

```bash
.venv/bin/pytest flext-infra/tests/ -q --tb=short
```

Expected: 2081+ tests passing, 0 failed.

- [ ] **Step 3: Smoke test every CLI group**

```bash
.venv/bin/python -m flext_infra --help
.venv/bin/python -m flext_infra.basemk --help
.venv/bin/python -m flext_infra.codegen --help
.venv/bin/python -m flext_infra.docs --help
.venv/bin/python -m flext_infra.github --help
.venv/bin/python -m flext_infra.refactor --help
.venv/bin/python -m flext_infra.release --help
.venv/bin/python -m flext_infra.validate --help
.venv/bin/python -m flext_infra.workspace --help
```

- [ ] **Step 4: Make workspace check**

```bash
make check PROJECT=flext-cli
make test PROJECTS="flext-cli flext-infra"
```

---

## Execution Order

1. Task 1 (maintenance) — proves the pattern
2. Task 2a–2h (all groups) — parallelizable
3. Task 3 (root FlextInfraCli) — depends on all Task 2
4. Task 4 (delete dead code) — depends on Task 3
5. Task 5 (validation) — final
