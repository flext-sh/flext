# Skill Validation & Harmonization — Design Spec

**Date**: 2026-04-15
**Scope**: 49 SKILL.md files under `.agents/skills/`
**Authority**: AGENTS.md §3 Code Law, §4 Import Law, §7 Skill System

## Context

After the prior refactor pass (removed `Zero Tolerance for Hacks`, `AXIOMATIC`, `TOTALLY FORBIDDEN`, triggers, TOC, frontmatter blank lines), the skills are now structurally clean but their **code examples have drifted from the real `flext-core` API**.

Baseline measurement via `/tmp/validate_skills.py` against the current workspace:

| Metric | Value |
|---|---|
| Total python blocks | 142 |
| Clean (compile + symbols resolve) | 5 |
| Syntax errors | 7 |
| Ruff errors | 128 |
| Pyrefly errors | 95 |

**96.5% of python blocks fail validation**. Primary drift sources confirmed by sampling:

1. **Phantom symbols**: `p.MappingLikePayload`, `p.ResourceFactory`, `p.ResourceCallable`, `p.Container.register*`, `p.Container.get*` — none exist in current `flext_core.protocols`.
2. **API misuse**: `p.Result[str].ok(...)` — `p.Result` is the *protocol*, has no `.ok()` classmethod. The canonical pattern is return type `p.Result[T]`, construction `r[T].ok(...)` (concrete `FlextResult`).
3. **Property drift**: `res.is_success` — actual property is `res.success`.
4. **Placeholder pollution**: `User`, `db`, `fetch_user` used as free variables without definition.
5. **Dead config refs**: `ruff-shared.toml` (config moved to `pyproject.toml [tool.ruff]`).
6. **Cross-project symbol origin ambiguity**: `c.Tests.*`, `t.Tests.*`, `u.Infra.*` — these live in `flext-tests` / `flext-infra`, not `flext-core`.

## Decision: Self-Contained Examples (Caminho Y)

Every python code block in SKILL.md MUST be **self-contained and copy-paste runnable**:

- All types, stub data, and helper functions used in the example are defined in the block itself.
- No free variables like `db`, `User`, `fetch_user` unless defined inside the block.
- Stubs may be minimal (`class User(m.ArbitraryTypesModel): id: str`) but must exist.
- `from __future__ import annotations` + all `from flext_core import ...` declared explicitly at block top.
- Block passes: `ast.parse` → `ruff check --select E,F,W,I,UP,PLC,PLE` → `pyrefly check` with zero errors.

**Rationale**: Forces every example to be a mini-program a developer can paste into a scratch file and run against `flext_core`. Exposes drift immediately. Prevents phantom-API examples from sneaking in.

**Trade-off accepted**: Examples become more verbose (5-15 extra lines for stubs). The doc becomes longer but each example is a trustworthy reference.

## Canonical Patterns (Authority for All Examples)

These patterns were verified against `flext-core/src/flext_core/result.py`, `dispatcher.py`, `loggings.py` on 2026-04-15. They are the non-negotiable conventions for all skill examples.

### r[T] construction vs p.Result[T] return type

```python
from __future__ import annotations

from flext_core import p, r


def parse_semver(value: str) -> p.Result[tuple[int, int, int]]:
    """Return type is the structural protocol p.Result[T]."""
    parts = value.split(".")
    if len(parts) != 3:
        return r[tuple[int, int, int]].fail(f"invalid semver: {value}")
    try:
        major, minor, patch = (int(p) for p in parts)
    except ValueError as exc:
        return r[tuple[int, int, int]].fail_exc(exc)
    return r[tuple[int, int, int]].ok((major, minor, patch))
```

- **Return annotation**: `p.Result[T]` (the structural protocol from `flext_core.protocols`)
- **Construction**: `r[T].ok(value)` or `r[T].fail(msg)` or `r[T].fail_exc(exc)` (the concrete `FlextResult`)
- **Never**: `p.Result[T].ok(...)` — `p.Result` has no `.ok` classmethod, it is a protocol

### Property access on r[T]

```python
result = parse_semver("1.0.0")
if result.success:  # not `.is_success`
    print(result.error)  # property, not method
```

Verified against [result.py:69-79](flext-core/src/flext_core/result.py#L69).

### FlextExceptions DSL (e.fail_*)

For domain-specific failures in runtime paths:

```python
from __future__ import annotations

from flext_core import e, p, r


def load_config(path: str) -> p.Result[dict[str, str]]:
    if not path:
        return e.fail_validation("path is empty", field="path")
    if path.endswith(".toml"):
        return e.fail_operation("toml not supported yet", op="load_config")
    return r[dict[str, str]].ok({})
```

Verified: `e.fail_auth`, `e.fail_authz`, `e.fail_circuit_breaker`, `e.fail_config_error`, `e.fail_conflict`, `e.fail_connection`, `e.fail_not_found`, `e.fail_operation`, `e.fail_rate_limit`, `e.fail_timeout`, `e.fail_type_mismatch`, `e.fail_validation` exist on `flext_core.exceptions.FlextExceptions`.

### m.* flat namespace (flext_core) — verified 2026-04-15

Classes in `m` from `flext_core` are **flat** — no sub-namespaces inside
flext_core. Via MRO, each mixin's inner class is promoted to the facade root.

to every model class in skill examples — the FLEXT enforcer rejects classes
that don't follow the project namespace naming convention (`Flext<Project><Tier>`),
which standalone sandbox files cannot satisfy.

```python
from __future__ import annotations

from typing import Annotated, ClassVar

from pydantic import u.Field

from flext_core import m, p, r, t


class CreateUserCommand(m.Command):
    """CQRS command — inherits from m.Command (flat, no sub-namespace)."""

    name: Annotated[t.NonEmptyStr, u.Field(description="User full name")]
    email: Annotated[str, u.Field(description="User email address")]


class UserSummary(m.Value):
    """Value object — inherits from m.Value (flat, no sub-namespace)."""

    user_id: Annotated[str, u.Field(description="Generated user identifier")]
    display_name: Annotated[str, u.Field(description="Formatted display name")]


def register_user(cmd: CreateUserCommand) -> p.Result[UserSummary]:
    """Uses m.Command and m.Value directly — no m.Domain.Class nesting."""
    if not cmd.name:
        return r[UserSummary].fail("name is required")
    return r[UserSummary].ok(UserSummary(user_id="u1", display_name=cmd.name))
```

**Available flat on `m` (verified from flext_core source):**

- Base models: `m.ArbitraryTypesModel`, `m.StrictModel`, `m.FlexibleInternalModel`,
  `m.ImmutableValueModel`, `m.FrozenModel`, `m.DynamicModel`, `m.EnforcedModel`,
  `m.ManagedModel`, `m.Metadata`
- DDD: `m.Entity`, `m.Value`, `m.AggregateRoot`
- CQRS: `m.Command`, `m.Query`, `m.Event`, `m.Handler`, `m.Pagination`

**Never** `m.Domain.Class` for flext_core types — that sub-namespace pattern
belongs to consumer project facades only (see below).

### Consumer project facade (local sub-namespace) — verified 2026-04-15

Consumer projects create ONE local sub-namespace inside their facade. The nested
class pattern (`m.Domain.Class`) exists ONLY in consumer projects — never in
flext_core:

```python
from __future__ import annotations

from typing import Annotated, ClassVar

from pydantic import u.Field

from flext_core import m, p, r


class FlextTargetOracleModels(m):
    """Consumer project facade — inherits flext_core m via MRO.

    In real project code this class lives in flext_target_oracle/models.py
    and the enforcer validates the Flext<Project><Tier> naming convention.
    """

    class TargetOracle:
        """ONE local namespace — project-specific domain models."""

        class ExecuteResult(m.ArbitraryTypesModel):
            rows_affected: Annotated[int, u.Field(description="Rows modified")]
            table_name: Annotated[str, u.Field(description="Target table name")]


def execute_batch(
    table: str,
) -> p.Result[FlextTargetOracleModels.TargetOracle.ExecuteResult]:
    """Access: FlextTargetOracleModels.TargetOracle.ExecuteResult (one level)."""
    result = FlextTargetOracleModels.TargetOracle.ExecuteResult(
        rows_affected=0,
        table_name=table,
    )
    return r[FlextTargetOracleModels.TargetOracle.ExecuteResult].ok(result)
```

### Pydantic v2 field body

`t.*` aliases ARE the type (first arg of `Annotated`). The base class provides
`model_config` — do not repeat it unless overriding defaults. All fields must
include `description=`:

```python
from __future__ import annotations

from typing import Annotated, ClassVar

from pydantic import u.Field

from flext_core import m, t


class UserProfile(m.ArbitraryTypesModel):
    """Inherits arbitrary_types_allowed from ArbitraryTypesModel.

    t.NonEmptyStr    = Annotated[str, MinLen(1)]    — IS the type
    t.NonNegativeInt = Annotated[int, Ge(0)]        — IS the type
    t.StrSequence    = Sequence[str]                 — covariant param type
    """

    name: Annotated[t.NonEmptyStr, u.Field(description="Display name")]
    age: Annotated[t.NonNegativeInt, u.Field(description="Age in years")]
    tags: Annotated[t.StrSequence, u.Field(description="Labels", default_factory=list)]
```

### Parameter types use t.* composed aliases

```python
from __future__ import annotations

from flext_core import t


def get_first_or_default(items: t.StrSequence, default: str) -> str:
    """Parameters use t.* composed aliases, not inline Sequence[str]."""
    for item in items:
        return item
    return default
```

**Rule**: Parameter types for sequence/mapping/container shapes MUST use `t.*`
composed aliases (`t.StrSequence`, `t.ConfigMap`, `t.IntMapping`, etc.) from
`flext_core.typings`. Do not write `Sequence[str]`, `list[str]`, or
`Mapping[str, int]` inline in parameter positions. Return types inside `r[T]`
remain concrete (`r[list[int]]`) due to invariance — see
[flext-type-system](.agents/skills/flext-type-system/SKILL.md).

## Validator Specification

A single script `/tmp/validate_skills.py` is the source of truth for "block passes/fails". It performs:

1. **Extract**: `re.compile(r"```python\n(.*?)```", re.DOTALL)` over every SKILL.md.
2. **Syntax check**: `ast.parse(block)` — fails → immediate error report.
3. **Sandbox write**: copy block verbatim (NO prelude injection) to `/tmp/skill_sandbox/<skill>/block_NN.py`.
4. **Ruff check**: `ruff check --config /home/marlonsc/flext/pyproject.toml --select E,F,W,I,UP,PLC,PLE --no-fix <path>`.
5. **Pyrefly check**: `pyrefly check <path>` — must report 0 errors.
6. **Report**: `/tmp/skill_validation_report.md` with per-block status and error detail.

The validator does **not** inject imports. Each block must carry its own `from __future__ import annotations` and explicit `from flext_core import ...` lines.

## Taxonomy of Fixes (Execution Order)

Fixes are applied in dependency order so that later categories reuse the vocabulary established in earlier ones.

### Phase 1 — Canonical pattern snippets (reusable)

Create stub skeletons for the most common example shapes (one-time work):

- `result-flow` — return `p.Result[T]`, construct with `r[T].ok/fail/fail_exc`
- `pydantic-v2-class` — `Annotated`, `ConfigDict`, `u.Field`, `u.PrivateAttr`
- `protocol-consumer` — receive `p.HasLogger`, return `p.Result[...]`
- `cross-project-mro` — dual-inheritance facade

These are reference templates I consult while rewriting broken blocks.

### Phase 2 — Drift fixes (per-skill, fail-first)

Walk through the validation report, fix one skill at a time. Priority order:

1. **Skills with 0 clean blocks** (async-python-patterns, flext-5agent-coordination, lib-pydantic-v2, etc.) — these are the most drifted, largest impact
2. **Skills with symbol drift specifically on `p.*`/`t.*`/`r.*`** (confirmed phantom symbols)
3. **Skills with syntax errors** (7 blocks)
4. **Skills with only placeholder-variable issues** (easy batch fix)

For each skill:

- Read the skill
- For each broken block, decide:
  - **Fix**: self-contained stubs + canonical pattern
  - **Replace**: if the block teaches a dead API, rewrite against the real API
  - **Remove**: if the block is redundant with another skill, delete and point to canonical
- Re-run validator on that skill only
- Move to next skill

### Phase 3 — Editorial harmonization (batch)

One final pass with `/tmp/normalize_skills_vocab.py`:

- `ruff-shared.toml` → `pyproject.toml [tool.ruff]`
- `ALWAYS`/`NEVER EVER`/`ABSOLUTELY MUST` → `must`/`never`
- Update stale `**Reviewed**` dates on files that were substantively changed
- Remove duplicate pointers to AGENTS.md where one is enough

### Phase 4 — Verification gate

Re-run these in order and confirm:

1. `python3 /tmp/validate_skills.py` → **137 → 0 broken blocks**
2. `python3 /tmp/verify_skills.py` → all 6 metrics still 0, frontmatter valid
3. Manual read of 5 sample skills from different taxonomy buckets for editorial quality

## Out of Scope

- Fixing the ~1M pyrefly errors in the workspace codebase itself
- Adding new skills or reorganizing skill taxonomy
- Editing `~/.agents/skills/` or `~/.vscode/agent-plugins/` (third-party)
- Touching references/* detail files inside skills (focus on SKILL.md only for this pass)

## Success Criteria

- Every `python` code block in `.agents/skills/*/SKILL.md` passes the validator
- No phantom symbols: every `p.X`, `t.X`, `r.X`, `m.X`, `c.X`, `e.X`, `u.X`, `h.X`, `d.X`, `s.X`, `x.X` reference resolves to a real attribute on the current `flext_core` module
- Canonical `r[T].ok(...)` / `p.Result[T]` return-type pattern is consistent across all examples
- Dead config refs (`ruff-shared.toml`) are gone
- The validation report shows 0 broken blocks

## Risk & Open Questions

- **Risk**: Phase 2 is tedious — each skill needs manual reading. Estimated ~2-3 hours of sequential Edit/Write operations for 25+ broken skills. Mitigation: batch similar fixes; don't over-edit skills that only need 1 block fix.
- **Risk**: Stubs add verbosity. Example skills grow by ~10-30%. Mitigation: keep stubs minimal (1-2 lines per placeholder) and use `m.ArbitraryTypesModel` as a cheap container.
- **Open question**: Should examples that demonstrate deprecated/removed APIs be **deleted** or **updated to current API**? Default: update to current API; delete only if the concept being taught no longer exists in the codebase.
