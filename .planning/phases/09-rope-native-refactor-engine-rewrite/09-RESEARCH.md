# Phase 9: Rope-native refactor engine rewrite - Research

**Researched:** 2026-03-25
**Domain:** Python refactoring — rope library integration with LibCST engine
**Confidence:** HIGH

## Summary

Rope 1.14.0 is already installed and declared as a dependency in flext-infra. The library provides `rope.refactor.rename.Rename` for cross-file semantic rename and `rope.contrib.findit.find_occurrences` for finding all usages of a symbol — both are the exact primitives needed to replace the hand-rolled `QualifiedNameProvider` grep logic in the 3 target transformers.

The engine integration point is clear: `FlextInfraRefactorEngine.refactor_project()` and `refactor_workspace()` already orchestrate per-project work. Pre/post hooks can be added as method calls before/after the per-file CST loop. A single `rope.base.project.Project` instance with `ropefolder=None` (no disk cache) serves the entire engine run.

The 3 target transformers total 385 LOC. After rope migration, each should shrink significantly — symbol_propagator's `QualifiedNameProvider` metadata dance becomes a `find_occurrences` call, mro_reference_rewriter's manual symbol lookup becomes a `Rename.get_changes()`, and nested_class_propagation's parent-aware skip logic simplifies when rope handles scope resolution.

**Primary recommendation:** Add a `_rope_project` property to `FlextInfraRefactorEngine` that lazily creates a single `Project(root, ropefolder=None)` instance. Implement rope hooks as private methods called in `refactor_project()`/`refactor_workspace()` before and after the CST pass. Migrate the 3 transformers to thin wrappers that call rope APIs, then inline or delete the wrapper if it adds no value.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Hybrid approach — rope for cross-file semantic ops, LibCST for syntax-level pattern edits
- **D-02:** Rope must SIMPLIFY existing code, not add layers. Where rope makes a LibCST transformer simpler, use it. Never add rope complexity to stay "pure LibCST."
- **D-03:** No "rope abstraction layer" — rope is used directly as a Python library where it helps
- **D-04:** Rope-native in Phase 9: `symbol_propagator.py`, `mro_reference_rewriter.py`, `nested_class_propagation.py` — these are the only ones doing cross-file name resolution
- **D-05:** All other transformers stay LibCST — but MUST be reviewed and simplified where rope APIs can reduce their complexity
- **D-06:** `mro_remover.py` and `mro_private_inline.py` — NO rope pre-check. Keep as-is LibCST.
- **D-07:** Import transformers stay LibCST, simplify if possible
- **D-08:** Typing transformers stay LibCST, simplify if possible
- **D-09:** Structural transformers stay LibCST, simplify if possible
- **D-10:** Rope ops as pre/post hooks on `FlextInfraRefactorEngine`, NOT new rule types
- **D-11:** No `FlextInfraRopeRefactorRule` subtype
- **D-12:** No YAML schema changes — rope hooks registered programmatically
- **D-13:** Existing `make refactor` CLI interface unchanged
- **D-14:** Hooks run once per project (rope's execution model), not per file
- **D-15:** Single monorepo-rooted `rope.base.project.Project("/home/marlonsc/flext")` instance
- **D-16:** All 33 `flext-*/src` directories in `source_folders`
- **D-17:** `ignored_resources` must exclude: `.venv`, `*.pyc`, `dist/`, `__pycache__`, `.mypy_cache`, `.git`
- **D-18:** `save_objectdb = False` — avoid stale cache
- **D-19:** Single Project shared across all rope hook invocations in one engine run
- **D-20:** Every change must make flext-infra simpler or equal — never more complex
- **D-21:** If using rope in a transformer makes it more complex, don't use rope there
- **D-22:** Target: reduce total LOC in `transformers/` and `refactor/` after Phase 9

### Claude's Discretion
- How exactly to structure rope hook methods on the engine
- Whether to delete migrated transformers entirely or keep them as thin wrappers
- Order of migration (which transformer first)

### Deferred Ideas (OUT OF SCOPE)
- Parallel engine (`FlextInfraRopeEngine`)
- `FlextInfraRopeRefactorRule` subtype
- Rope pre-check for `mro_remover`/`mro_private_inline`
- Lazy project pool (LRU)
- `engine: rope` YAML discriminator
</user_constraints>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| rope | 1.14.0 | Cross-file semantic rename, find occurrences | Already declared dep in flext-infra, mature Python refactoring library |
| libcst | (existing) | Syntax-level CST transformations | Already the backbone of all transformers |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| rope.base.project.Project | 1.14.0 | Workspace-level Python project model | Single instance per engine run |
| rope.refactor.rename.Rename | 1.14.0 | Cross-file symbol rename with scope awareness | Replaces QualifiedNameProvider grep in symbol_propagator |
| rope.contrib.findit.find_occurrences | 1.14.0 | Find all usages of a symbol across project | Replaces hand-rolled occurrence scanning |
| rope.base.change.ChangeSet | 1.14.0 | Collected file changes from rename ops | Applied via `do()` or iterated for dry-run |

No new dependencies needed.

## Architecture Patterns

### Rope Project Initialization Pattern

```python
from rope.base.project import Project


def _create_rope_project(workspace_root: Path) -> Project:
    """Create a rope Project for the monorepo root, no disk state."""
    source_folders = [
        str(p / "src")
        for p in workspace_root.iterdir()
        if p.is_dir() and p.name.startswith("flext-") and (p / "src").exists()
    ]
    return Project(
        str(workspace_root),
        ropefolder=None,  # No .ropeproject directory
        ignored_resources=[
            "*.pyc",
            ".venv",
            "dist/",
            "__pycache__",
            ".mypy_cache",
            ".git",
            ".tox",
            "*.egg-info",
        ],
        source_folders=source_folders,
        save_objectdb=False,
    )
```

**Key detail:** `ropefolder=None` means rope creates NO disk artifacts. `save_objectdb=False` is already the default in rope 1.14.0 but should be explicit for clarity.

### Rope Rename Pattern

```python
from rope.refactor.rename import Rename
from rope.base.project import Project


def rope_rename_symbol(
    project: Project,
    file_path: Path,
    old_name: str,
    new_name: str,
) -> rope.base.change.ChangeSet:
    """Rename a symbol across the entire project."""
    resource = project.get_resource(str(file_path.relative_to(project.address)))
    # offset = byte position of the symbol name in the file
    source = resource.read()
    offset = source.index(old_name)
    renamer = Rename(project, resource, offset)
    return renamer.get_changes(new_name)
```

### Rope Find Occurrences Pattern

```python
from rope.contrib.findit import find_occurrences, Location


def rope_find_usages(
    project: Project,
    file_path: Path,
    symbol_name: str,
) -> Sequence[Location]:
    """Find all occurrences of a symbol across the project."""
    resource = project.get_resource(str(file_path.relative_to(project.address)))
    source = resource.read()
    offset = source.index(symbol_name)
    return find_occurrences(project, resource, offset)
```

`Location` has: `.resource` (File), `.region` (start, end offsets), `.offset`, `.lineno`, `.unsure` (bool).

### Engine Hook Integration Point

Current flow in `refactor_project()`:
1. Safety stash
2. Collect files
3. `refactor_files()` (per-file CST loop)
4. Safety validation

New flow:
1. Safety stash
2. Collect files
3. **Pre-hook: run rope semantic ops** (per-project, once)
4. `refactor_files()` (per-file CST loop — remaining transformers)
5. **Post-hook: optional rope validation**
6. Safety validation

### Anti-Patterns to Avoid
- **Wrapping rope in an abstraction layer:** Use `rope.refactor.rename.Rename` directly. D-03 forbids abstraction.
- **Running rope per-file:** Rope's execution model is per-project. D-14 requires hooks run once per project.
- **Creating multiple Project instances:** D-19 requires a single shared instance per engine run.
- **Adding rope to transformers that don't need it:** D-21 — if it makes the transformer more complex, don't use rope.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Cross-file symbol rename | QualifiedNameProvider + manual import rewriting | `rope.refactor.rename.Rename.get_changes()` | Rope handles scope, imports, and re-exports correctly |
| Find all occurrences | Hand-rolled grep + CST metadata resolution | `rope.contrib.findit.find_occurrences()` | Returns typed Location objects with resource/offset/lineno |
| Scope-aware name resolution | ParentNodeProvider + manual skip logic | Rope's internal pymodule/pyname system | Rope already understands Python scoping rules |

**Key insight:** The 3 target transformers each re-implement parts of what rope does natively. The migration should DELETE the hand-rolled logic, not wrap it.

## Common Pitfalls

### Pitfall 1: Rope indexing the entire .venv
**What goes wrong:** Without `ignored_resources`, rope will parse every file in `.venv/` (thousands of packages), causing 30+ second init.
**Why it happens:** Rope defaults already include `.venv` BUT the monorepo root may have additional dirs to exclude.
**How to avoid:** Explicit `ignored_resources` list including `.venv`, `dist/`, `*.egg-info`. Verified: rope 1.14.0 defaults already include `.venv`, `.git`, `*.pyc`, `.mypy_cache` — but add `dist/`, `__pycache__`, `*.egg-info` explicitly.
**Warning signs:** Slow `Project()` construction (>5s), high memory usage.

### Pitfall 2: Offset calculation for Rename/find_occurrences
**What goes wrong:** `Rename(project, resource, offset)` requires a byte offset pointing to the exact symbol name. Wrong offset = wrong symbol or crash.
**Why it happens:** `str.index()` finds the first occurrence which may not be the definition.
**How to avoid:** For definitions, parse with rope's `pymodule.get_scope()` or use the known file position from the transformer's rename map. For imports, search within the import section only.
**Warning signs:** `RopeError` about "cannot determine the name".

### Pitfall 3: ChangeSet.do() writes files directly
**What goes wrong:** Calling `changeset.do()` writes to disk immediately, bypassing the engine's dry-run/safety mechanism.
**Why it happens:** Rope's change model assumes direct application.
**How to avoid:** For dry-run mode, iterate `changeset.changes` and read `ChangeContents.new_contents` / `ChangeContents.resource.path` without calling `.do()`. For apply mode, either call `.do()` or manually write via `u.write_file()`.
**Warning signs:** Files modified during dry-run.

### Pitfall 4: rope.base.project.Project is not thread-safe
**What goes wrong:** Concurrent access to the same Project instance from multiple threads causes stale state.
**Why it happens:** Rope was designed for single-threaded editor use.
**How to avoid:** Sequential execution only — which is already the case (D-14, no parallelization in config).
**Warning signs:** Intermittent wrong results.

### Pitfall 5: Stale rope analysis after CST modifications
**What goes wrong:** If rope pre-hooks rename symbols, then CST transformers read the original file content, they'll be out of sync.
**Why it happens:** Rope writes changes to disk; CST reads from disk.
**How to avoid:** If rope hooks write files, the CST pass must re-read from disk (which it already does — `file_path.read_text()` in `refactor_file()`). Ensure rope hooks run BEFORE the CST file collection, or re-collect after rope changes.
**Warning signs:** CST transformers processing stale content.

## Code Examples

### Creating the Project instance on the engine

```python
# In FlextInfraRefactorEngine
from rope.base.project import Project as RopeProject


@property
def rope_project(self) -> RopeProject | None:
    """Lazily create rope Project for workspace-level ops."""
    if not hasattr(self, "_rope_project"):
        self._rope_project: RopeProject | None = None
    return self._rope_project


def _init_rope_project(self, workspace_root: Path) -> RopeProject:
    """Initialize rope project for the monorepo root."""
    source_folders = [
        str(d / "src")
        for d in sorted(workspace_root.iterdir())
        if d.is_dir() and d.name.startswith("flext-") and (d / "src").exists()
    ]
    project = RopeProject(
        str(workspace_root),
        ropefolder=None,
        ignored_resources=[
            "*.pyc",
            ".venv",
            "dist/",
            "__pycache__",
            ".mypy_cache",
            ".git",
            ".tox",
            "*.egg-info",
        ],
        source_folders=source_folders,
        save_objectdb=False,
    )
    self._rope_project = project
    return project
```

### Applying Rename changes safely with r[T]

```python
def _rope_rename(
    self,
    project: RopeProject,
    resource_path: str,
    old_name: str,
    new_name: str,
    *,
    dry_run: bool = False,
) -> r[Sequence[str]]:
    """Execute a rope rename and return change descriptions."""
    try:
        resource = project.get_resource(resource_path)
        source = resource.read()
        offset = source.index(old_name)
        renamer = Rename(project, resource, offset)
        changes = renamer.get_changes(new_name)
        descriptions = [str(c) for c in changes.changes]
        if not dry_run:
            changes.do()
        return r[Sequence[str]].ok(descriptions)
    except (ValueError, RopeError) as exc:
        return r[Sequence[str]].fail(str(exc))
```

### Iterating ChangeSet without applying (dry-run inspection)

```python
from rope.base.change import ChangeContents

for change in changeset.changes:
    if isinstance(change, ChangeContents):
        file_path = change.resource.path  # relative to project root
        new_content = change.new_contents
        # Can diff against original or just report
```

## Baseline Metrics

| Directory | Current LOC | Target Direction |
|-----------|-------------|------------------|
| `transformers/` | 4,120 | Decrease (3 files shrink/deleted) |
| `refactor/` | 9,894 | Slight increase (hook methods) then net decrease from simplification |
| 3 target transformers | 385 | Significant decrease or deletion |
| `engine.py` | 748 | +30-50 lines for hook infrastructure |

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.4+ |
| Config file | `flext-infra/pyproject.toml` [tool.pytest.ini_options] |
| Quick run command | `/home/marlonsc/flext/.venv/bin/pytest flext-infra/tests/unit/refactor/ -x -q` |
| Full suite command | `/home/marlonsc/flext/.venv/bin/pytest flext-infra/tests/ -x -q` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ROPE-01 | Project init with ropefolder=None, correct ignored_resources | unit | `pytest flext-infra/tests/unit/refactor/test_rope_project.py -x` | Wave 0 |
| ROPE-02 | symbol_propagator replaced by rope rename | integration | `pytest flext-infra/tests/unit/refactor/test_rope_symbol_propagation.py -x` | Wave 0 |
| ROPE-03 | mro_reference_rewriter replaced by rope | integration | `pytest flext-infra/tests/unit/refactor/test_rope_mro_rewrite.py -x` | Wave 0 |
| ROPE-04 | nested_class_propagation replaced by rope | integration | `pytest flext-infra/tests/unit/refactor/test_rope_nested_propagation.py -x` | Wave 0 |
| ROPE-05 | Engine pre/post hooks execute in correct order | unit | `pytest flext-infra/tests/unit/refactor/test_infra_refactor_engine.py -x` | Exists (extend) |
| ROPE-06 | Dry-run mode does not write files | unit | `pytest flext-infra/tests/unit/refactor/test_rope_dry_run.py -x` | Wave 0 |
| ROPE-07 | LOC reduction verified | manual | `find transformers/ refactor/ -name '*.py' -exec cat {} + \| wc -l` | N/A |

### Sampling Rate
- **Per task commit:** `/home/marlonsc/flext/.venv/bin/pytest flext-infra/tests/unit/refactor/ -x -q`
- **Per wave merge:** `/home/marlonsc/flext/.venv/bin/pytest flext-infra/tests/ -x -q`
- **Phase gate:** Full suite green + ruff + pyright zero before verify

### Wave 0 Gaps
- [ ] `flext-infra/tests/unit/refactor/test_rope_project.py` — covers ROPE-01
- [ ] `flext-infra/tests/unit/refactor/test_rope_symbol_propagation.py` — covers ROPE-02
- [ ] `flext-infra/tests/unit/refactor/test_rope_mro_rewrite.py` — covers ROPE-03
- [ ] `flext-infra/tests/unit/refactor/test_rope_nested_propagation.py` — covers ROPE-04
- [ ] `flext-infra/tests/unit/refactor/test_rope_dry_run.py` — covers ROPE-06

## Open Questions

1. **Offset calculation strategy for batch renames**
   - What we know: `Rename` needs exact byte offset. For a single known symbol in a known file, `str.index()` works.
   - What's unclear: When multiple renames are needed (e.g., symbol_propagator has N rename mappings), do we need to create N `Rename` instances or can we chain them?
   - Recommendation: Create one `Rename` per symbol. After each `changes.do()`, rope's Project state updates. Process sequentially.

2. **How rope handles re-exports through `__init__.py`**
   - What we know: Rope resolves imports through the module system.
   - What's unclear: The flext monorepo uses auto-generated `__init__.py` with `__getattr__` lazy loading. Rope may not follow dynamic `__getattr__`.
   - Recommendation: Test with a real flext module first. If rope can't resolve `__getattr__` exports, fall back to explicit `source_folders` + direct module paths.

3. **Integration with existing `m.Infra.MROImportRewrite` model**
   - What we know: `mro_reference_rewriter.py` uses `m.Infra.MROImportRewrite` which contains `facade_name` and `symbol`.
   - What's unclear: Whether rope's rename can be parameterized with the same data or needs a different input format.
   - Recommendation: Convert `MROImportRewrite` mappings to rope rename inputs (file_path + offset + new_name). The model itself may become unnecessary if rope handles the full operation.

## Sources

### Primary (HIGH confidence)
- rope 1.14.0 installed in `/home/marlonsc/flext/.venv/` — API verified via `inspect.signature()` and source inspection
- `flext-infra/src/flext_infra/transformers/` — all 3 target transformers read in full
- `flext-infra/src/flext_infra/refactor/engine.py` — full engine source read (748 LOC)
- `rope.base.prefs.Prefs` source — confirmed `save_objectdb=False` default, `ignored_resources` defaults include `.venv`

### Secondary (MEDIUM confidence)
- rope `ropefolder=None` behavior confirmed from `Project.__init__` source — "Pass None for not using such a folder at all"
- `rope.contrib.findit.find_occurrences` returns `list[Location]` — confirmed from source

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - rope 1.14.0 already installed, API verified from source
- Architecture: HIGH - engine.py hook points are clear, rope API is straightforward
- Pitfalls: MEDIUM - offset calculation and `__getattr__` lazy loading interaction need runtime validation

**Research date:** 2026-03-25
**Valid until:** 2026-04-25 (stable — rope is mature, flext-infra is internal)
