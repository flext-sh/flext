# Constant Consolidation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `consolidate` subcommand to the codegen CLI that scans for inline constants, matches them against governance canonical values, replaces them with `c.Infra.*` references, and validates each file with rollback on failure.

**Architecture:** Extends the existing census/governance/transformation pipeline. The `CanonicalValueRule` model gains frozenset/regex/tuple types. Two new getters on governance. One new CLI handler orchestrating existing `replace_canonical_values()` + `normalize_constant_aliases()` with per-file gate validation.

**Tech Stack:** Pydantic v2 models, YAML governance, subprocess for linter validation, existing `u.Infra.*` APIs.

---

### Task 1: Extend CanonicalValueRule model for new types

**Files:**
- Modify: `flext-infra/src/flext_infra/codegen/_models.py:202-206`

- [ ] **Step 1: Widen the `value` type in CanonicalValueRule**

The current model only accepts `int | str`. Extend to accept `list` (for frozenset/tuple entries in YAML):

```python
    class CanonicalValueRule(FlextModels.ArbitraryTypesModel):
        value: Annotated[int | str | Sequence[str], Field(...)]
        type: Annotated[str, Field(...)]
        canonical_ref: Annotated[str, Field(...)]
        semantic_names: t.StrSequence = Field(default_factory=list)
```

- [ ] **Step 2: Run ruff check on the modified file**

Run: `ruff check flext-infra/src/flext_infra/codegen/_models.py --select E,F,W --no-fix`
Expected: No new errors.

- [ ] **Step 3: Commit**

```
feat(codegen): widen CanonicalValueRule.value to accept Sequence[str]
```

---

### Task 2: Add governance YAML entries for frozenset/regex/tuple

**Files:**
- Modify: `flext-infra/src/flext_infra/rules/constants-governance.yml:27+`

- [ ] **Step 1: Add new rule NS-006 for inline consolidation**

After the existing `NS-005` rule, add:

```yaml
  - id: NS-006
    description: "Inline value matches canonical constant — should use c.Infra.* reference"
    fixable: true
```

- [ ] **Step 2: Add frozenset canonical entries**

After the existing `canonical_values` entries, add:

```yaml
  - value: ["__pycache__", ".git", ".mypy_cache", "node_modules", ".venv", ".tox", ".nox", ".ruff_cache", "dist", "build", "site"]
    type: frozenset
    canonical_ref: "Excluded.COMMON_EXCLUDED_DIRS"
    semantic_names:
      - SKIP_DIRS
      - EXCLUDED_DIRS
      - IGNORE_DIRS
      - COMMON_EXCLUDED_DIRS

  - value: ["TypeVar", "ParamSpec", "TypeVarTuple"]
    type: frozenset
    canonical_ref: "TYPEVAR_CALLABLES"
    semantic_names:
      - TYPEVAR_CALL_NAMES
      - TYPEVAR_CALLABLES

  - value: ["src", "tests", "scripts", "examples"]
    type: tuple
    canonical_ref: "MRO_SCAN_DIRECTORIES"
    semantic_names:
      - SCAN_DIRECTORIES
      - KNOWN_DIRS
      - SCOPE_DIRS

  - value: ["constants.py", "typings.py", "protocols.py"]
    type: tuple
    canonical_ref: "TIER0_MODULE_FILES"
    semantic_names:
      - TIER0_MODULES
```

- [ ] **Step 3: Add regex canonical entries**

```yaml
  - value: "^class\\s+(\\w+)"
    type: regex
    canonical_ref: "SourceCode.CLASS_NAME_RE"
    semantic_names:
      - CLASS_RE
      - CLASS_PATTERN
      - CLASS_NAME_RE

  - value: "^class\\s+(\\w+)\\s*\\(([^)]*)\\)\\s*:"
    type: regex
    canonical_ref: "SourceCode.CLASS_WITH_BASES_RE"
    semantic_names:
      - CLASS_DEF_RE
      - CLASS_WITH_BASES_RE

  - value: "^_?[A-Z][A-Z0-9_]*$"
    type: regex
    canonical_ref: "SourceCode.CONSTANT_NAME_RE"
    semantic_names:
      - CONSTANT_PATTERN
      - CONSTANT_NAME_RE
      - MRO_SCAN_CONSTANT_PATTERN
```

- [ ] **Step 4: Validate YAML loads correctly**

Run: `python -c "from yaml import safe_load; from pathlib import Path; d = safe_load(Path('flext-infra/src/flext_infra/rules/constants-governance.yml').read_text()); print(f'OK: {len(d[\"canonical_values\"])} entries')"`
Expected: `OK: N entries` (N > 5).

- [ ] **Step 5: Commit**

```
feat(codegen): add frozenset/regex/tuple canonical entries to governance YAML
```

---

### Task 3: Add governance getter methods

**Files:**
- Modify: `flext-infra/src/flext_infra/_utilities/codegen_governance.py:51+`

- [ ] **Step 1: Add `get_canonical_frozenset_values()`**

After `get_canonical_str_values()` (line 51), add:

```python
@staticmethod
def get_canonical_frozenset_values() -> Mapping[frozenset[str], str]:
    config = FlextInfraUtilitiesCodegenGovernance.load_governance_config()
    return {
        frozenset(entry.value): entry.canonical_ref
        for entry in config.canonical_values
        if entry.type == "frozenset"
        and isinstance(entry.value, Sequence)
        and not isinstance(entry.value, str)
    }


@staticmethod
def get_canonical_regex_values() -> t.StrMapping:
    config = FlextInfraUtilitiesCodegenGovernance.load_governance_config()
    return {
        entry.value: entry.canonical_ref
        for entry in config.canonical_values
        if entry.type == "regex" and isinstance(entry.value, str)
    }


@staticmethod
def get_canonical_tuple_values() -> Mapping[tuple[str, ...], str]:
    config = FlextInfraUtilitiesCodegenGovernance.load_governance_config()
    return {
        tuple(entry.value): entry.canonical_ref
        for entry in config.canonical_values
        if entry.type == "tuple"
        and isinstance(entry.value, Sequence)
        and not isinstance(entry.value, str)
    }
```

- [ ] **Step 2: Add `Sequence` to imports**

The file already imports `Mapping` from `collections.abc`. Add `Sequence` to the import:

```python
from collections.abc import Mapping, MutableMapping, Sequence
```

- [ ] **Step 3: Run ruff + pyright check**

Run: `ruff check flext-infra/src/flext_infra/_utilities/codegen_governance.py --select E,F,W --no-fix`
Expected: No errors.

- [ ] **Step 4: Commit**

```
feat(codegen): add frozenset/regex/tuple governance getters
```

---

### Task 4: Add CLI input model for consolidate

**Files:**
- Modify: `flext-infra/src/flext_infra/_models/cli_inputs_codegen.py:113+`

- [ ] **Step 1: Add `CodegenConsolidateInput` after `CodegenPipelineInput`**

```python
    class CodegenConsolidateInput(ApplyMixin, CliInputBase):
        """CLI input for constant consolidation."""

        output_format: Annotated[
            str,
            Field(default="text", description="Output format (json|text)"),
        ] = "text"
        project: Annotated[
            str | None,
            Field(default=None, description="Single project to consolidate"),
        ] = None
```

- [ ] **Step 2: Run ruff check**

Run: `ruff check flext-infra/src/flext_infra/_models/cli_inputs_codegen.py --select E,F,W --no-fix`
Expected: No errors.

- [ ] **Step 3: Commit**

```
feat(codegen): add CodegenConsolidateInput CLI model
```

---

### Task 5: Add consolidate handler to codegen CLI

**Files:**
- Modify: `flext-infra/src/flext_infra/codegen/cli.py:125+` (register) and `337+` (handler)

- [ ] **Step 1: Register the consolidate route**

In `register_codegen()`, before the closing of the method (after the `constants-quality-gate` registration at line 125), add:

```python
        cli.register_result_route(
            app,
            route=m.Cli.ResultCommandRouteModel(
                name="consolidate",
                help_text="Consolidate inline constants into c.Infra.* references",
                model_cls=m.Infra.CodegenConsolidateInput,
                handler=self._handle_consolidate,
                failure_message="consolidate failed",
                success_formatter=_format_text,
            ),
        )
```

- [ ] **Step 2: Add the handler method**

After the last handler method, add:

```python
@staticmethod
def _handle_consolidate(params: m.Infra.CodegenConsolidateInput) -> r[str]:
    """Handle constant consolidation with per-file validation."""
    import subprocess

    workspace = Path(params.workspace).resolve()
    dry_run = not params.apply
    lines: list[str] = []

    if dry_run:
        lines.append("[DRY-RUN] Scanning for inline canonicals...\n")

    # Phase 1: Scan — reuse existing detection
    projects_result = u.Infra.discover_projects(workspace)
    if projects_result.is_failure:
        return r[str].fail("Failed to discover projects")

    projects: Sequence[m.Infra.ProjectInfo] = projects_result.value
    if params.project:
        projects = [p for p in projects if p.name == params.project]

    total_found = 0
    total_applied = 0
    total_failed = 0
    total_suggested = 0
    file_results: list[dict[str, t.Infra.InfraValue]] = []

    for project in projects:
        project_root = workspace / project.name
        src_dir = project_root / c.Infra.Paths.DEFAULT_SRC_DIR
        if not src_dir.is_dir():
            continue

        pkg_name = project.name.replace("-", "_")
        pkg_dir = src_dir / pkg_name
        if not pkg_dir.is_dir():
            continue

        parent_class = u.Infra.derive_constants_class(pkg_name, pkg_dir)
        project_import = f"from {pkg_name} import {parent_class}"

        for py_file in sorted(pkg_dir.rglob(c.Infra.Extensions.PYTHON_GLOB)):
            if c.Infra.Dunders.PYCACHE in py_file.parts:
                continue

            # Extract definitions from this file
            definitions = u.Infra.extract_constant_definitions(py_file, project.name)
            hardcoded = u.Infra.detect_hardcoded_canonicals(definitions)

            if not hardcoded:
                continue

            total_found += len(hardcoded)

            if dry_run:
                for item in hardcoded:
                    ref = u.Infra.canonical_reference_for(item.name, item.value_repr)
                    lines.append(
                        f"  {py_file.relative_to(workspace)}:{item.line}"
                        f"  {item.name} = {item.value_repr} -> {ref}"
                    )
                continue

            # Phase 2: Apply with validation
            try:
                backup = py_file.read_text(c.Infra.Encoding.DEFAULT)
            except (OSError, UnicodeDecodeError):
                continue

            # Apply replacement
            modified, changes = u.Infra.replace_canonical_values(
                py_file,
                parent_class,
                definitions,
            )
            if not modified:
                continue

            # Apply alias normalization
            norm_modified, norm_changes = u.Infra.normalize_constant_aliases(
                py_file,
                project_import,
                pkg_dir,
            )
            all_changes = list(changes) + list(norm_changes)

            # Validate
            validation_ok = True
            rel_path = str(py_file)
            for tool_cmd in (
                ["ruff", "check", rel_path, "--no-fix", "--select", "E,F,W"],
                ["pyright", rel_path],
            ):
                try:
                    result = subprocess.run(
                        tool_cmd,
                        capture_output=True,
                        text=True,
                        timeout=60,
                        cwd=str(workspace),
                    )
                    if result.returncode != 0:
                        validation_ok = False
                        lines.append(
                            f"  FAILED {py_file.relative_to(workspace)}"
                            f" [{tool_cmd[0]}]: {result.stdout[:200]}"
                        )
                        break
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass

            if not validation_ok:
                # Revert
                py_file.write_text(backup, encoding=c.Infra.Encoding.DEFAULT)
                total_failed += 1
                file_results.append({
                    "file": str(py_file.relative_to(workspace)),
                    "status": "reverted",
                    "changes": all_changes,
                })
            else:
                total_applied += len(all_changes)
                for change in all_changes:
                    lines.append(
                        f"  APPLIED {py_file.relative_to(workspace)}: {change}"
                    )
                file_results.append({
                    "file": str(py_file.relative_to(workspace)),
                    "status": "applied",
                    "changes": all_changes,
                })

    # Summary
    lines.append("")
    if dry_run:
        lines.append(
            f"Found {total_found} canonical matches across {len(projects)} projects"
        )
        lines.append(f"  {total_found - total_suggested} exact (auto-fixable)")
        lines.append(f"  {total_suggested} semantic (suggested only)")
    else:
        lines.append(
            f"Applied {total_applied} replacements, {total_failed} files reverted"
        )

    if params.output_format == "json":
        text = t.Infra.CONTAINER_MAPPING_ADAPTER.dump_json({
            "total_found": total_found,
            "total_applied": total_applied,
            "total_failed": total_failed,
            "total_suggested": total_suggested,
            "files": file_results,
        }).decode()
        return r[str].ok(text)

    return r[str].ok("\n".join(lines))
```

- [ ] **Step 3: Run ruff check**

Run: `ruff check flext-infra/src/flext_infra/codegen/cli.py --select E,F,W --no-fix`
Expected: No errors.

- [ ] **Step 4: Commit**

```
feat(codegen): add consolidate CLI handler with per-file validation and rollback
```

---

### Task 6: Export new model and verify integration

**Files:**
- Verify: `flext-infra/src/flext_infra/_models/cli_inputs_codegen.py` — model exists
- Verify: `flext-infra/src/flext_infra/codegen/cli.py` — handler registered

- [ ] **Step 1: Verify the model is accessible via `m.Infra.CodegenConsolidateInput`**

Run: `python -c "from flext_infra import m; print(m.Infra.CodegenConsolidateInput.model_fields.keys())"`
Expected: prints `dict_keys(['workspace', 'apply', 'output_format', 'project'])`

If the model is NOT auto-exported (lazy init doesn't pick it up), manually add it to the MRO model class or `__init__.py` exports.

- [ ] **Step 2: Verify CLI help shows the new command**

Run: `python -m flext_infra codegen --help`
Expected: `consolidate` appears in the command list.

- [ ] **Step 3: Run dry-run on flext-infra itself**

Run: `python -m flext_infra codegen consolidate --project flext-infra`
Expected: Lists inline canonical matches found (or "0 matches" if all already consolidated).

- [ ] **Step 4: Commit**

```
feat(codegen): verify consolidate command integration
```

---

### Task 7: End-to-end test with --apply

**Files:**
- No new files — integration test via CLI

- [ ] **Step 1: Run consolidate with apply on a single project**

Run: `python -m flext_infra codegen consolidate --project flext-infra --apply`
Expected: Shows applied replacements or reverted files with error details.

- [ ] **Step 2: Verify no regressions**

Run: `ruff check flext-infra/src/flext_infra/ --select E,F,W --no-fix`
Expected: No new F-errors (E501 line length is acceptable).

- [ ] **Step 3: Run JSON output mode**

Run: `python -m flext_infra codegen consolidate --project flext-infra --json`
Expected: Valid JSON output with `total_found`, `total_applied`, `files` keys.

- [ ] **Step 4: Final commit**

```
feat(codegen): constant consolidation command complete
```
