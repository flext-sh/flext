---
name: lib-pyyaml
description: Safe and deterministic YAML read/write patterns across FLEXT subprojects. Use when modifying YAML parsing, settings files, CLI output formatting, or docs-maintenance tooling.

---

# Lib PyYAML

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment

## Scope

- Primary YAML-heavy areas:
  - `flext-quality/docs/maintenance/core/config_manager.py`
  - `flext-quality/src/flext_quality/utilities.py`
  - `scripts/documentation/audit.py`
  - `flext-cli/src/flext_cli/file_tools.py`
  - `flext-cli/src/flext_cli/settings.py`
  - `flext-cli/src/flext_cli/services/output.py`
  - `flext-meltano/src/flext_meltano/file_managers.py`
  - `flext-meltano/src/flext_meltano/utilities.py`
  - `flext-dbt-oracle/src/flext_dbt_oracle/models.py`
  - `flext-db-oracle/src/flext_db_oracle/cli.py`
  - `flext-core/tests/integration/test_config_integration.py`
- Dependency pinning: `flext-core/pyproject.toml`

### Subproject Usage Map

- `flext-quality`: YAML settings ingestion and persistence (`safe_load`, `dump` with explicit options).
- `flext-cli`: YAML file IO and YAML output formatting for CLI response rendering.
- `flext-meltano`: project settings lifecycle (`save_yaml_config`, `load_yaml_config`, validation).
- `flext-dbt-oracle`: schema YAML read/merge/write in model generation.
- `flext-db-oracle`: YAML display formatting in CLI output mode.
- `flext-core/tests`: YAML fixture write/read for settings integration tests.

## References

- `AGENTS.md` — canonical governance source
- `flext-quality/docs/maintenance/core/config_manager.py`: `_load_config_file`, `save_config`
- `flext-quality/src/flext_quality/utilities.py`: `load_yaml_rules`
- `flext-cli/src/flext_cli/file_tools.py`: `read_yaml_file`, `write_yaml_file`
- `flext-cli/src/flext_cli/settings.py`: `load_from_config_file`
- `flext-meltano/src/flext_meltano/file_managers.py`: `save_yaml_config`, `load_yaml_config`, `validate_yaml_file`
- `flext-dbt-oracle/src/flext_dbt_oracle/models.py`: schema `safe_load` + `dump` update flow
- `flext-core/pyproject.toml`: `pyyaml>=6.0.2`
- `https://pyyaml.org/wiki/PyYAMLDocumentation`

## Rules

- Always prefer `yaml.safe_load(...)` when reading YAML from files or user-controlled content.
- Never use `yaml.load(...)` without an explicit safe loader policy (current repo evidence shows zero `yaml.load(` occurrences).
- Use explicit dump options for stable output (`default_flow_style=False`, and set `sort_keys` intentionally).
- Validate loaded t.RecursiveContainer shape (`dict`, `list`) before passing to typed models.
- Keep encoding explicit (`encoding="utf-8"` or project constant) when opening files.
- For CLI output serialization, keep YAML formatting deterministic and user-readable.
- **Hacks**: Canonical "Zero Hacks" rule in `AGENTS.md` §3.4.

## Instructions

- Use these in-repo declarations as templates:

```python
# flext-quality/src/flext_quality/utilities.py
from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import yaml

from flext_core import p, t


@staticmethod
def load_yaml_rules(path: Path) -> p.Result[Sequence[t.RecursiveContainerMapping]]:
    with path.open(encoding="utf-8") as f:
        yaml.safe_load(f)
```

```python
# flext-cli/src/flext_cli/file_tools.py
from __future__ import annotations

from pathlib import Path

import yaml

from flext_core import c, p, t


class FlextCliFileTools:
    @staticmethod
    def _load_structured_file(path: str, loader: object) -> t.RecursiveContainer: ...

    @staticmethod
    def _write_structured_file(
        file_path: Path,
        writer: object,
        error_msg: str,
    ) -> p.Result[bool]: ...

    @staticmethod
    def read_yaml_file(file_path: str | Path) -> p.Result[t.RecursiveContainer]:
        return FlextCliFileTools._execute_file_operation(
            lambda: FlextCliFileTools._load_structured_file(
                str(file_path), yaml.safe_load
            ),
            c.Cli.FileErrorMessages.YAML_LOAD_FAILED,
        )

    @staticmethod
    def _execute_file_operation(
        op: object,
        error_msg: str,
    ) -> p.Result[t.RecursiveContainer]: ...

    @staticmethod
    def write_yaml_file(
        file_path: Path,
        data: t.RecursiveContainer,
        default_flow_style: bool = False,
        sort_keys: bool = True,
        allow_unicode: bool = True,
    ) -> p.Result[bool]:
        return FlextCliFileTools._write_structured_file(
            file_path,
            lambda f: yaml.safe_dump(
                data,
                f,
                default_flow_style=default_flow_style,
                sort_keys=sort_keys,
                allow_unicode=allow_unicode,
            ),
            c.Cli.ErrorMessages.YAML_WRITE_FAILED,
        )
```

```python
# flext-meltano/src/flext_meltano/file_managers.py
from __future__ import annotations

from pathlib import Path

import yaml

from flext_core import c, p


@classmethod
def validate_yaml_file(cls, file_path: Path) -> p.Result[bool]:
    with file_path.open("r", encoding=c.DEFAULT_ENCODING) as f:
        yaml.safe_load(f)
```

- Prefer `yaml.dump(..., default_flow_style=False)` only where existing module conventions require it.
- Keep read/write flow symmetric when possible: `safe_load` on read, `safe_dump` on write.

## Workflow

1. Find nearest YAML call-site in the touched subproject.
2. Preserve that module's established style (`safe_load` + `dump/safe_dump` options).
3. Add/keep shape checks after loading (`dict`/`list`) before model construction.
4. Ensure no new `yaml.load(` appears in changed code.
5. Validate that dump output options remain explicit for predictable diffs.

## Examples

Good:

```python
from __future__ import annotations

from pathlib import Path

import yaml


def load_config(config_path: Path) -> dict[str, object]:
    with config_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
```

Why good: safe loader, explicit encoding, and null-safe fallback to dictionary.

Bad:

```python
from __future__ import annotations

from pathlib import Path

import yaml


def load_config(config_path: Path) -> object:
    with config_path.open("r") as f:
        return yaml.load(f)  # noqa: S506
```

Why bad: unsafe loader behavior and implicit encoding increase security and portability risk.

Good:

```python
from __future__ import annotations

from io import StringIO

import yaml


def dump_schema(schema_data: dict[str, object]) -> str:
    f = StringIO()
    yaml.dump(schema_data, f, default_flow_style=False, indent=2)
    return f.getvalue()
```

Why good: explicit YAML shape and indentation in generated schema files.

Bad:

```python
from __future__ import annotations

from io import StringIO

import yaml


def dump_schema(schema_data: dict[str, object]) -> str:
    f = StringIO()
    yaml.dump(schema_data, f)
    return f.getvalue()
```

Why bad: implicit defaults can change formatting and create noisy diffs across environments.

Good:

```python
from __future__ import annotations

from collections.abc import Sequence
from io import StringIO

import yaml

from flext_core import r, t


def load_rules(raw: str) -> r[Sequence[t.RecursiveContainerMapping]]:
    f = StringIO(raw)
    parsed = yaml.safe_load(f)
    if not isinstance(parsed, dict):
        return r[Sequence[t.RecursiveContainerMapping]].fail("Expected YAML dict")
    return r[Sequence[t.RecursiveContainerMapping]].ok([parsed])
```

Why good: validates structure before typed access.

## Verification

Make gates:

- `make check PROJECT=flext-core` — lint gates catch unsafe yaml usage
- `make check PROJECT=flext-quality` — yaml-heavy project quality gates
- `make test PROJECT=flext-cli` — yaml file operations tested

Pattern checks:

- `rg -n "import yaml|yaml\.safe_load\(|yaml\.dump\(|yaml\.safe_dump\(" --glob "**/*.py" flext-quality flext-cli flext-meltano flext-dbt-oracle flext-db-oracle flext-core/tests`
- `rg -n "yaml\.load\(" --glob "**/*.py" flext-quality flext-cli flext-meltano flext-dbt-oracle flext-db-oracle flext-core`
- `rg -n "def load_yaml_rules|def read_yaml_file|def write_yaml_file|def load_yaml_config|def validate_yaml_file" flext-quality/src/flext_quality/utilities.py flext-cli/src/flext_cli/file_tools.py flext-meltano/src/flext_meltano/file_managers.py`
- `rg -n "pyyaml>=6\.0\.2" flext-core/pyproject.toml`
