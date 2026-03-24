# Phase 2: Architecture & SOLID - Research

**Researched:** 2026-03-24
**Domain:** DIP enforcement, Pydantic v2 Field() canonicalization, ABC-to-Protocol conversion, PEP 695 type aliases, import normalization
**Confidence:** HIGH

## Summary

Phase 2 applies Dependency Inversion Principle via protocols across 33 projects, canonicalizes Pydantic v2 Field() patterns, converts ABCs to Protocols where safe, caches TypeAdapter instances, fixes mutable defaults, and normalizes import patterns. The sisyphus plans provide exhaustive audits with exact file locations and counts. Phase 1 guarantees a clean type system baseline (0 pyrefly/pyright errors).

The work is requirement-clustered into 4 waves: (0) issubclass prerequisite fixes, (1) Protocol DIP enforcement, (2) Field() canonicalization + TypeAdapter + mutable defaults, (3) PEP 695 stragglers + import normalization. All changes are mechanical/structural with zero behavioral modifications.

**Primary recommendation:** Follow the CONTEXT.md wave order strictly. Use ast-grep for all mechanical migrations. Run `make codegen` after every protocol/model/constants change. Validate per-project with `make check PROJECT=<name>`.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Phase 2 uses **requirement-based waves**, not project-based waves. Unlike Phase 1 (where errors cascaded project-to-project), Phase 2 requirements are largely independent: protocols (ARCH-01/04/05), Field migration (ARCH-03/06/07), type aliases (ARCH-08), import normalization (ARCH-02). Each wave targets a requirement cluster.
- **D-02:** Wave order: (0) issubclass() prerequisite fixes -> (1) Protocol DIP enforcement (ARCH-01, ARCH-04, ARCH-05) -> (2) Pydantic v2 Field() canonicalization (ARCH-03, ARCH-06, ARCH-07) -> (3) PEP 695 type aliases + import normalization (ARCH-08, ARCH-02).
- **D-03:** Researchers and planners MUST read the existing `.sisyphus` plans as reference input -- they contain audits, counts, and proven ast-grep patterns. Do not re-derive what's already documented.
- **D-04:** 6 `issubclass()` calls in flext-core must be refactored to Protocol-safe patterns BEFORE any ABC->Protocol conversion. This is a **blocking prerequisite** (Wave 0). The sisyphus plan identifies all 6 call sites.
- **D-05:** All ~1,551 `Field(...)` usages are in scope, **including tests**. `PrivateAttr()` (94 usages) is explicitly **excluded** -- it is not a Field pattern.
- **D-06:** Migration pattern: `x: T = Field(...)` -> `x: Annotated[T, Field(...)]`. For optional fields: `x: T | None = Field(...)` -> `x: Annotated[T | None, Field(...)]` (NOT `Annotated[T, Field(...)] | None`).
- **D-07:** 6 pure ABCs -> `@runtime_checkable` Protocol (full conversion). 8 template ABCs -> extract Protocol interface to `protocols.py` + retain concrete base class. 5 ABCs retained as-is (load-bearing inheritance). Per sisyphus plan audit.
- **D-08:** `p.Base`, `p.HasModelDump`, `p.Handler` are FROZEN -- they have isinstance/inheritance usage and must NOT be modified.
- **D-09:** ~100 inline `TypeAdapter()` instantiations cached as `ClassVar` on the owning class. ~40 already-cached instances left as-is. 5 dynamic instances accepted (cannot be cached). Most repeated pattern: `TypeAdapter(dict[str, object])` (11 instances across 6 files).
- **D-10:** All remaining `TypeAlias` assignments migrated to `type X = ...` form (PEP 695). 1,271 already use PEP 695 -- this wave catches stragglers.
- **D-11:** `c,m,t,u,p` in `tests/`, `examples/`, `scripts/` must import from local namespace root (e.g., `from tests import c, m, t`) -- never from `flext_core` directly. Per ARCH-02.

### Claude's Discretion
- Within each wave, the exact sequencing and parallelism of individual projects is at Claude's discretion (respecting dependency order: flext-core -> flext-infra -> consumers).
- The ast-grep rule design for Field() migration and protocol substitution is at Claude's discretion, informed by the sisyphus plan patterns.
- Whether to batch small consumer projects or handle them individually within a wave.

### Deferred Ideas (OUT OF SCOPE)
- Dispatcher hot-path optimization (pre-resolve at registration) -- deferred to Phase 3.
- Protocol introspection caching (3 cache layers) -- 0 production callers, deferred to Phase 3.
- Pydantic v2 governance guideline document -- deferred to after Phase 2.
- CI performance benchmarks for TypeAdapter caching -- deferred to Phase 3.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ARCH-01 | All public API type annotations use protocol types (`p.Context`, `p.DI`, `p.Config`, `p.StructlogLogger`) not concrete types | Protocol mapping table in sisyphus plan: 12 DIP violations in flext-core, 23 in consumers. ast-grep patterns for mechanical replacement. |
| ARCH-02 | `c,m,t,u,p` always imported from local namespace root in tests/examples/scripts | Grep-based detection of `from flext_core import c,m,t,u,p` in test dirs. Mechanical find-and-replace. |
| ARCH-03 | All ~1,551 `Field(...)` usages migrated to `Annotated[X, Field(...)]` | Sisyphus plan has per-project counts. ast-grep pattern: `$NAME: $TYPE = Field($$$)` -> `$NAME: Annotated[$TYPE, Field($$$)]`. PrivateAttr excluded. |
| ARCH-04 | 6 pure ABCs converted to `@runtime_checkable` Protocol | Sisyphus plan identifies all 6. Prerequisite: 16 issubclass() calls in flext-core (6 relevant) must be refactored first. |
| ARCH-05 | 8 template ABCs have Protocol interface extracted | Sisyphus plan identifies all 8. Pattern: extract abstract methods to Protocol in protocols.py, keep concrete base with implementation. |
| ARCH-06 | ~100 inline `TypeAdapter()` instantiations cached as ClassVar/module constants | Audit: 451 TypeAdapter matches, ~100 inline hot-path. Cache as `ClassVar[TypeAdapter[T]]` on owning class. |
| ARCH-07 | 13 mutable `Field(default=[])` replaced with `default_factory=list` | Current grep shows 2 remaining in flext-dbt-oracle (others may have been fixed in Phase 1). Verify actual count at execution time. |
| ARCH-08 | Type aliases use PEP 695 `type X = ...` form | 113 TypeAlias occurrences remain across 30 files (many in flext-infra tooling and test fixtures). 1,271 already PEP 695. |
</phase_requirements>

## Standard Stack

No new libraries needed. Phase 2 uses existing tooling:

| Tool | Purpose | Why Standard |
|------|---------|--------------|
| ast-grep (`sg`) | Mechanical code transformations (Field migration, protocol substitution) | Project standard per CLAUDE.md. Proven in Phase 1. |
| `make check PROJECT=<name>` | Per-project linting (ruff + pyright + pyrefly) | Workspace standard quality gate |
| `make test PROJECT=<name>` | Per-project test suite | Workspace standard validation |
| `make codegen` | Regenerate `__init__.py` exports after protocol/model changes | MANDATORY after any protocol/model/constants changes |
| `make validate VALIDATE_SCOPE=workspace` | Full workspace validation (final gate) | End-of-phase validation |

## Architecture Patterns

### Pattern 1: DIP via Protocol Substitution (ARCH-01)

**What:** Replace concrete type annotations with protocol types in public APIs.
**When:** Any public function/method parameter or return type that references FlextContext, FlextContainer, FlextSettings, FlextLogger.

Protocol mapping (from sisyphus plan):

| Concrete | Protocol | Namespace |
|----------|----------|-----------|
| `FlextContext` | `p.Context` | `FlextProtocolsContext.Context` |
| `FlextContainer` | `p.DI` | `FlextProtocolsDI.DI` |
| `FlextSettings` | `p.Config` | `FlextProtocolsConfig.Config` |
| `FlextLogger` | `p.StructlogLogger` | `FlextProtocolsLogging.StructlogLogger` |
| `FlextDispatcher` | `p.CommandBus` | `FlextProtocolsHandler.CommandBus` |

**Exceptions:**
- Factory methods that MUST return concrete types (e.g., `FlextContext.create()`) keep concrete return types
- `__init__.py` exports (these export concrete classes -- correct)
- Implementation files internally (e.g., `container.py` internal logic)

### Pattern 2: Field() -> Annotated Migration (ARCH-03)

**What:** Canonical Pydantic v2 Field pattern.

```python
# BEFORE
name: str = Field(default="", description="Name")
items: Sequence[str] = Field(default_factory=list)
config: Config | None = Field(default=None)

# AFTER
name: Annotated[str, Field(default="", description="Name")]
items: Annotated[Sequence[str], Field(default_factory=list)]
config: Annotated[Config | None, Field(default=None)]
```

**Critical:** `| None` goes INSIDE `Annotated[T | None, Field()]`, NOT outside as `Annotated[T, Field()] | None` (different Pydantic semantics).

### Pattern 3: ABC -> Protocol Conversion (ARCH-04/05)

**Pure ABC (6 total) -- full conversion:**
```python
# BEFORE
class MyABC(ABC):
    @abstractmethod
    def do_thing(self) -> str: ...

# AFTER
@runtime_checkable
class MyProtocol(Protocol):
    def do_thing(self) -> str: ...
```

**Template ABC (8 total) -- extract + retain:**
```python
# Extract interface to protocols.py
@runtime_checkable
class MyProtocol(Protocol):
    def do_thing(self) -> str: ...

# Keep concrete base with implementation
class MyBase:  # no longer ABC
    def do_thing(self) -> str:
        return self._implementation()
    def _implementation(self) -> str:
        raise NotImplementedError
```

### Pattern 4: TypeAdapter Caching (ARCH-06)

```python
# BEFORE (inline, hot-path)
def validate(self, data: Mapping[str, str]) -> bool:
    adapter = TypeAdapter(dict[str, str])
    return adapter.validate_python(data) is not None

# AFTER (cached as ClassVar)
class MyClass:
    _str_dict_adapter: ClassVar[TypeAdapter[dict[str, str]]] = TypeAdapter(dict[str, str])

    def validate(self, data: Mapping[str, str]) -> bool:
        return self._str_dict_adapter.validate_python(data) is not None
```

### Pattern 5: PEP 695 Type Alias (ARCH-08)

```python
# BEFORE
from typing import TypeAlias
MyType: TypeAlias = str | int

# AFTER
type MyType = str | int
```

### Anti-Patterns to Avoid
- **Annotated[T, Field()] | None:** Wrong Pydantic semantics. Always `Annotated[T | None, Field()]`.
- **isinstance on TypeAliasType:** PEP 695 `type X = ...` creates TypeAliasType -- CRASHES at runtime with isinstance. Use tuple constants or TypeGuard.
- **Modifying FROZEN protocols:** `p.Base`, `p.HasModelDump`, `p.Handler` are FROZEN per D-08.
- **Hand-editing __init__.py:** Always use `make codegen`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Field migration regex | Custom regex/sed | ast-grep pattern matching | ast-grep understands AST structure, regex breaks on multiline Field() |
| Protocol import fixup | Manual per-file edits | ast-grep + grep verification | 33 projects, hundreds of files |
| __init__.py exports | Manual export lists | `make codegen` | Autogenerated, hand-edits get overwritten |
| Type alias migration | Manual find-replace | ast-grep `type $NAME: TypeAlias = $EXPR` -> `type $NAME = $EXPR` | Structural replacement avoids false positives |

## Common Pitfalls

### Pitfall 1: Annotated Semantics for Optional Fields
**What goes wrong:** Using `Annotated[T, Field()] | None` instead of `Annotated[T | None, Field()]`
**Why it happens:** Intuitive but wrong -- Pydantic treats these differently
**How to avoid:** ast-grep rule must capture the full type including `| None` and place it inside Annotated
**Warning signs:** Pydantic validation errors on None values after migration

### Pitfall 2: issubclass() on Protocols
**What goes wrong:** `issubclass(SomeClass, MyProtocol)` fails at runtime unless Protocol is `@runtime_checkable`
**Why it happens:** ABCs support issubclass natively; Protocols require `@runtime_checkable`
**How to avoid:** Wave 0 refactors all 16 issubclass() sites in flext-core BEFORE ABC conversion
**Warning signs:** `TypeError: Protocols with non-method members don't support issubclass()`

### Pitfall 3: Missing `make codegen` After Protocol Changes
**What goes wrong:** `__init__.py` exports stale, imports fail
**Why it happens:** Protocols added/removed but exports not regenerated
**How to avoid:** Run `make codegen` after EVERY change to protocols.py, models.py, constants.py, typings.py
**Warning signs:** ImportError on newly added protocols

### Pitfall 4: Field() in Multiline Declarations
**What goes wrong:** ast-grep pattern fails on multiline Field() with keyword args
**Why it happens:** Simple pattern `$NAME: $TYPE = Field($$$)` may not match multiline
**How to avoid:** Test ast-grep patterns with dryRun=true first. Use multiline-aware patterns.
**Warning signs:** grep shows remaining non-Annotated Field() after migration

### Pitfall 5: TypeAdapter Cache on Wrong Scope
**What goes wrong:** Caching a TypeAdapter that uses a forward reference not yet resolved
**Why it happens:** ClassVar evaluated at class definition time, before all types available
**How to avoid:** For the 5 identified dynamic instances, accept they cannot be cached. Only cache adapters with fully-resolved types.
**Warning signs:** `PydanticUserError` at import time

### Pitfall 6: TypeAlias in Infrastructure Tooling
**What goes wrong:** Migrating TypeAlias in flext-infra code that manipulates TypeAlias strings
**Why it happens:** flext-infra tools (typing_unifier, namespace_validator) inspect `TypeAlias` as AST patterns
**How to avoid:** Distinguish between TypeAlias used AS type annotations (migrate) vs TypeAlias referenced as strings in tooling logic (keep or update detection patterns)
**Warning signs:** flext-infra validation tools break after migration

## Code Examples

### ast-grep: Field() -> Annotated Migration

```yaml
# sg rule for simple Field migration
id: field-to-annotated
language: python
rule:
  pattern: "$NAME: $TYPE = Field($$$ARGS)"
fix: "$NAME: Annotated[$TYPE, Field($$$ARGS)]"
```

Note: This simple rule handles single-line cases. Multiline and `| None` cases need separate patterns or post-processing.

### ast-grep: Concrete -> Protocol Type Substitution

```bash
# Replace FlextContext -> p.Context in type annotations
sg --pattern '$NAME: FlextContext' --rewrite '$NAME: p.Context' --lang python

# Replace in isinstance checks
sg --pattern 'isinstance($VAR, FlextContext)' --rewrite 'isinstance($VAR, p.Context)' --lang python
```

### Grep: Verify Import Normalization (ARCH-02)

```bash
# Find violations: c,m,t,u,p imported from flext_core in tests
sg --pattern 'from flext_core import $$$' --lang python */tests/
```

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.4+ |
| Config file | `pyproject.toml` [tool.pytest.ini_options] |
| Quick run command | `make test PROJECT=<name>` |
| Full suite command | `make validate VALIDATE_SCOPE=workspace` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ARCH-01 | Zero concrete types in public APIs | grep audit | `grep -rn ": FlextContext\|: FlextContainer\|: FlextSettings\|: FlextLogger" */src/ \| grep -v __init__` -> 0 | N/A (grep) |
| ARCH-02 | Local namespace imports in tests | grep audit | `grep -rn "from flext_core import [cmtup]" */tests/` -> 0 | N/A (grep) |
| ARCH-03 | Field() in Annotated form | grep audit | `grep -rn "Field(" --include="*.py" */src/ \| grep -v "Annotated\[" \| grep -v PrivateAttr` -> 0 | N/A (grep) |
| ARCH-04 | 6 ABCs converted to Protocol | grep audit | Count `@runtime_checkable` increased by 6 | N/A (grep) |
| ARCH-05 | 8 template ABCs have Protocol extracted | manual review | Protocol exists in protocols.py for each | N/A |
| ARCH-06 | TypeAdapter cached | grep audit | `grep -rn "TypeAdapter(" --include="*.py" */src/ \| grep -v ClassVar \| grep -v "^#"` -> ~5 dynamic only | N/A (grep) |
| ARCH-07 | Zero mutable defaults | grep audit | `grep -rn "default=\[\]\|default={}" --include="*.py" */src/` -> 0 | N/A (grep) |
| ARCH-08 | PEP 695 type aliases | grep audit | `grep -rn "TypeAlias" --include="*.py" */src/ \| grep -v ".venv"` -> 0 in production src | N/A (grep) |

### Sampling Rate
- **Per task commit:** `make check PROJECT=<affected_project>`
- **Per wave merge:** `make check PROJECT=<affected_projects>` + `make test PROJECT=<core_projects>`
- **Phase gate:** `make validate VALIDATE_SCOPE=workspace` + all grep audits pass

### Wave 0 Gaps
None -- existing test infrastructure covers all phase requirements. All validation is grep-based auditing + existing linter/test gates.

## Current State Baseline

Measured via grep (research time):

| Metric | Count | Notes |
|--------|-------|-------|
| issubclass() in flext-core/src | 16 across 8 files | 6 relevant per sisyphus plan |
| TypeAlias remaining | 113 across 30 files | Many in flext-infra tooling (may be intentional) |
| Field(default=[]) | 2 in flext-dbt-oracle | Others may have been fixed; verify at execution |
| Protocols already defined | 334 across 25 files | Extensive existing infrastructure |
| PEP 695 aliases already | 1,271 | Stragglers only for ARCH-08 |

## Sources

### Primary (HIGH confidence)
- `.sisyphus/plans/protocol-solid-standardization.md` -- DIP enforcement audit, protocol mapping, ast-grep patterns
- `.sisyphus/plans/pydantic-v2-advanced-modernization.md` -- Field() counts, ABC audit, TypeAdapter audit, mutable defaults
- `.sisyphus/plans/flext-core-typing-simplification.md` -- Type alias cleanup, protocol simplification
- `.claude/skills/lib-pydantic-v2/SKILL.md` -- Pydantic v2 patterns and rules
- `.claude/skills/flext-strict-typing/SKILL.md` -- Type system rules, PEP 695 patterns
- `.claude/skills/python-313-typing/SKILL.md` -- PEP 695/742 reference

### Secondary (MEDIUM confidence)
- Grep-based current state measurements (point-in-time, may shift before execution)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - all tooling already in project, proven in Phase 1
- Architecture: HIGH - patterns documented in sisyphus plans and skills, 334 protocols already exist
- Pitfalls: HIGH - derived from actual project experience (Phase 1) and sisyphus plan guardrails

**Research date:** 2026-03-24
**Valid until:** 2026-04-24 (stable domain, no external dependency changes expected)
