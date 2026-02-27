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

name: lib-pyyaml
description: Safe and deterministic YAML read/write patterns across FLEXT subprojects. Trigger when modifying YAML parsing, config files, CLI output formatting, or docs-maintenance tooling.

---

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

- `flext-quality`: YAML config ingestion and persistence (`safe_load`, `dump` with explicit options).
- `flext-cli`: YAML file IO and YAML output formatting for CLI response rendering.
- `flext-meltano`: project config lifecycle (`save_yaml_config`, `load_yaml_config`, validation).
- `flext-dbt-oracle`: schema YAML read/merge/write in model generation.
- `flext-db-oracle`: YAML display formatting in CLI output mode.
- `flext-core/tests`: YAML fixture write/read for config integration tests.

## References

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
- Validate loaded object shape (`dict`, `list`) before passing to typed models.
- Keep encoding explicit (`encoding="utf-8"` or project constant) when opening files.
- For CLI output serialization, keep YAML formatting deterministic and user-readable.
- **Zero Tolerance for Hacks**: Prohibited use of `model_rebuild()`, `eval()`, `exec()`, `cast()`, and `inline imports`. Wait for definition time or use Protocol decoupling.
## Instructions

- Use these in-repo declarations as templates:

```python
# flext-quality/src/flext_quality/utilities.py

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment

@staticmethod
def load_yaml_rules(path: Path) -> r[list[dict[str, object]]]:
    with path.open(encoding="utf-8") as f:
        parsed: object = yaml.safe_load(f)
```

```python
# flext-cli/src/flext_cli/file_tools.py
@staticmethod
def read_yaml_file(file_path: str | Path) -> r[t.GeneralValueType]:
    return FlextCliFileTools._execute_file_operation(
        lambda: FlextCliFileTools._load_structured_file(str(file_path), yaml.safe_load),
        c.Cli.FileErrorMessages.YAML_LOAD_FAILED,
    )

@staticmethod
def write_yaml_file(...) -> r[bool]:
    return FlextCliFileTools._write_structured_file(
        file_path,
        lambda f: yaml.safe_dump(data, f, default_flow_style=default_flow_style, sort_keys=sort_keys, allow_unicode=allow_unicode),
        c.Cli.ErrorMessages.YAML_WRITE_FAILED,
    )
```

```python
# flext-meltano/src/flext_meltano/file_managers.py
@classmethod
def validate_yaml_file(cls, file_path: Path) -> r[bool]:
    with file_path.open("r", encoding=c.Utilities.DEFAULT_ENCODING) as f:
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
with config_path.open("r", encoding="utf-8") as f:
    data = yaml.safe_load(f) or {}
```

Why good: safe loader, explicit encoding, and null-safe fallback to dictionary.

Bad:

```python
with config_path.open("r") as f:
    data = yaml.load(f)
```

Why bad: unsafe loader behavior and implicit encoding increase security and portability risk.

Good:

```python
yaml.dump(schema_data, f, default_flow_style=False, indent=2)
```

Why good: explicit YAML shape and indentation in generated schema files.

Bad:

```python
yaml.dump(schema_data, f)
```

Why bad: implicit defaults can change formatting and create noisy diffs across environments.

Good:

```python
parsed: object = yaml.safe_load(f)
if not isinstance(parsed, dict):
    return r[list[dict[str, object]]].fail("Expected YAML dict")
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
