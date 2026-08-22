# ADR-011: Runtime-Forward Annotation Law

- **Status:** Accepted
- **Date:** 2026-07-17
- **Tracking:** `mro-wkii`, ADR-011 rollout epic
- **Implementation status:** flext-core first (warn → fix → strict), then all member projects one bead each. Pending the flext-core clean-baseline gate in this ADR.
- **Amends:** ADR-005 §2 (facade and layer direction). **Related:** ADR-002, ADR-006, ADR-010.

<!-- ADR-011 (agent) — ratify the operator-approved, oracle-verified runtime-forward annotation law; supersede the "reverse-via-TYPE_CHECKING" rule with runtime-forward imports; no model_rebuild; no ad-hoc lazy; data=m.*, collaborators=p.*. -->

## Context

FLEXT composes every package from the canonical MRO facades `c → t → p → m → u`
(constants, typings, protocols, models, utilities) plus the operational facades
`r/e/x/h/d/s`. Models are Pydantic v2-way and interfaces are protocol-typed for
SOLID/DIP. The platform also self-instruments with `beartype.claw`
(`BEARTYPE_MODE`-gated) as a runtime type tripwire.

Prior law (ADR-005 §2; AGENTS.md §19/U5/U6/U20; arc42) allowed **reverse imports
under `if TYPE_CHECKING:`** and required `p → m`, `t → p`, `t → m`, and `m → c`
to be lazy or type-checking-only. That design is **incompatible** with the two
runtime engines the platform actually depends on, proven empirically on
beartype 0.22.9 + pydantic 2.13:

- **Pydantic v2 builds the core schema eagerly at class definition.** A field
  annotation whose name is only importable under `TYPE_CHECKING` raises
  `PydanticUserError: ... is not fully defined; ... call model_rebuild()`. The
  only escapes are a runtime import or `model_rebuild()`.
- **beartype claw evaluates PEP 526 annotated assignments and decorated
  signatures at runtime.** A `TYPE_CHECKING`-only name in a runtime-evaluated
  annotation raises `NameError` at import.

A mass ruff `flake8-type-checking` (`TC001/TC002/TC003`) autofix moved runtime
facade/stdlib imports into `TYPE_CHECKING` and broke beartype self-instrumentation
of `flext-core` (the pre-refactor tree passed the same claw import; the
post-refactor tree fails with `NameError`). Because `select = ["ALL"]` keeps TC
active, the autofix re-injects the defect on every run.

This ADR replaces the "reverse-via-`TYPE_CHECKING`" rule with a single
runtime-forward invariant that satisfies Pydantic v2, beartype, and SOLID/DIP
simultaneously, with **zero exceptions**, **no `model_rebuild()`**, and **no
ad-hoc lazy imports**.

## Decision

### 1. Facade direction is index-ordered; reverse edges are forbidden

Assign layer indices `c = 0 < t = 1 < p = 2 < m = 3 < u = 4`.

- An import is **FORWARD** iff `importer_index > importee_index`. Forward imports
  are **runtime-legal** and are the default: `u → m,p,t,c`; `m → p,t,c`;
  `p → t,c`; `t → c`.
- An import is **REVERSE** iff `importer_index < importee_index`. Reverse imports
  are **FORBIDDEN entirely** — not at runtime and not under `if TYPE_CHECKING:`.
  A reverse edge is always a symptom of a mis-placed artifact (see §3d).
- "Layer X is below layer Y" grants Y the right to import X; it never grants X
  the right to import Y.

The runtime import graph is a proven DAG (`t→c`; `p→t,c`; `m→t,p,c`;
`u→m,p,t,c`; topological order `c < t < p < m < u`), so §2 can never force a cycle.

### 2. The single invariant — runtime-forward annotations

Every name that appears in a **runtime-evaluated annotation** MUST be a top-level
**runtime** import. This covers:

- a Pydantic model field annotation,
- a PEP 526 annotated assignment (`NAME: T = value`) at module, class, or
  function scope,
- a beartype-decorated function signature (parameter and return),
- a PEP 695 `type` alias right-hand side.

Consequences that are now law:

- **No `TYPE_CHECKING` gating of an annotation name.** `if TYPE_CHECKING:` is
  reserved for symbols used *solely* in static-only positions that no runtime
  engine evaluates — and never to hide a reverse edge (which §1 forbids outright).
- **No `from __future__ import annotations` used to evade runtime resolution.**
  Pydantic still evaluates annotation strings against module globals at schema
  build, so stringizing hides the failure instead of preventing it. Prefer real,
  non-stringized annotations so a missing runtime import fails at module load.

### 3. Placement and typing

**(a) Collaborator / dependency-injection / behavior fields → `p.*` protocols.**
Injected collaborators (container, settings, dispatcher, registry, a service
dependency) are typed by their `p.*` protocol (DIP). The `FlextService` /
`FlextModels` base sets `model_config = ConfigDict(arbitrary_types_allowed=True)`;
this is the **only** sanctioned use of `arbitrary_types_allowed`. Such fields
are validated by structural `isinstance` and are not serialized — correct,
because they are injected objects, not payloads.

**(b) Data / payload fields → concrete `m.*` (or `t` scalars).** Any field
constructed from a dict or emitted by `model_dump()` — including **nested and
composed** data (`address: Address`, `contacts: list[Contact]`,
`aliases: dict[str, Address]`) — is a concrete `m.*` model or a `t` scalar,
**never a bare protocol**. Pydantic performs full recursive validation and
serialization only through concrete types; a protocol-typed data field cannot
deserialize a dict. Models holding models is an intra-layer `m → m` runtime edge
(legal, no cycle, no `model_rebuild`).

**(c) `p` never references `m`.** Protocols bound generics and members with
`p.BaseModel` (and other `p.*`), never a concrete `m.*` model. `p → p` is legal;
`p → m` is a forbidden reverse edge.

**(d) `t` is pure vocabulary.** `t` imports only `c`, the standard library, and
`t` itself. A composite alias whose right-hand side names a `p.*` lives in `p`;
one that names an `m.*` lives in `m`. An artifact lives at the layer of its
highest-index referent; a reverse edge means the artifact is in the wrong module.

**(e) `u` / `services` / `api` signatures type models by `p.*`.** Utility and
service parameters and return values that carry a model are annotated with the
owning `p.*` protocol, imported at runtime (`u → p` forward). The concrete `m.*`
instance is passed and returned unchanged (object identity preserved; no
dump/revalidate roundtrip). Annotating a `u`/`services` signature with a concrete
`m.*` couples the utility to an implementation and is forbidden.

### 4. No `model_rebuild()`, no ad-hoc lazy imports, bounded recursion

- **`model_rebuild()` is prohibited** anywhere in production source. It only ever
  defers annotation resolution that §2 already guarantees at class-build time.
- **Ad-hoc lazy imports are prohibited**: function-local `from flext_* import …`,
  `@cached_property` deferral of type/config resolution, and internal package
  `__getattr__`. The **only** sanctioned lazy mechanism is the generated PEP 562
  facade map at the **production package root** `__init__.py` (U20); every other
  package initializer is an eager static re-export (U22).
- **Recursion is bounded to what resolves without a rebuild**: a direct
  self-referential model (`class Node(m.BaseModel): children: list[Node] = []`)
  or a single-module `RootModel` union. **Cross-module mutually-recursive Pydantic
  models are forbidden** (they cannot resolve without `model_rebuild()`).
- **JSON / recursive contracts are Pydantic-instrumented at contracts.** Any
  Pydantic field, public parameter/return, or persisted shape that carries JSON
  or a recursive structure is a concrete `m.*` (`BaseModel` / `RootModel`), never
  raw `dict` / `TypedDict` / `t.JsonValue` as a contract. Raw `dict` is permitted
  only as a transient local at a true external I/O membrane
  (`json.loads` input, `model_dump` output), never stored or exposed.

### 5. beartype is the runtime tripwire; enforcement is staged

- `BeartypeConf(claw_is_pep526=True)`, `BEARTYPE_MODE`-gated (on in dev and CI,
  off in prod). PEP 526 checking stays ON: it is the runtime signal that proves
  §2 holds — a hidden or lazy annotation name fails loud at claw import.
- `flext-core` owns rule identity in its enforcement catalog (`ENFORCE-*`,
  warn → strict via `BEARTYPE_MODE` + `promote_to_error_when_strict`).
- `flext-infra` owns the static detectors (rope-semantic) and deterministic
  codemods (ast-grep) that prevent and auto-fix violations, plus the ruff policy
  SSOT (`config/tooling.yaml`) that disables `TC001/TC002/TC003` so autofix never
  re-injects `TYPE_CHECKING` on an annotation name (`TC004` stays: it forbids
  moving a runtime import into `TYPE_CHECKING`).

### 6. Canonical structure is mandatory in every example and validation

Every example, pattern, and validation in this ADR and in every artifact that
applies it MUST use the canonical FLEXT structure:

- **Namespaced MRO aliases**: each facade extends its upstream short alias as the
  MRO base and publishes the local alias exactly once at module bottom
  (`from flext_core import m` → `class FlextXModels(m): …` → `m = FlextXModels`).
- **Single nested class per model module**; one canonical class per
  `_models/_protocols` module; `Tests<Project><Unit>` for tests.
- **Thin MRO facades**: `api.py` (thin MRO facade over the composed runtime),
  `base.py` (publishes local `s`), `cli.py`, and `services/*` composed by MRO for
  everything. No loose helpers, flat aliases, or multiple public classes per
  module in examples.

Canonical example:

```python
from __future__ import annotations

from typing import Annotated

from flext_core import c, m, p, t  # runtime — forward, all resolvable


class FlextExampleModels(m):
    class Address(m.BaseModel):  # single nested class per model module
        street: Annotated[str, m.Field(min_length=1)]
        zip: Annotated[str, m.Field(min_length=1)]

    class Order(m.BaseModel):
        # data / nested / composed → concrete m.*
        address: FlextExampleModels.Address
        lines: tuple[FlextExampleModels.Address, ...]
        # collaborator / DI → p.* protocol
        dispatcher: p.Dispatcher | None = None


m = FlextExampleModels
```

```python
from flext_core import p, r, u  # runtime — u → p forward


class FlextExampleUtilities(u):
    @staticmethod
    def summarize(order: p.Order) -> r[str]:  # signatures type by p.*
        return r[str].ok(f"{order.address.zip}:{len(order.lines)}")


u = FlextExampleUtilities
```

### 7. Unified settings + config data delivery via XDG base directories

Settings and config **data-path delivery** is unified through `settings.py` using
the OS-native XDG base-directory pattern. The directory namespace `<app>` is the
**consuming application** (the project whose entrypoint runs), SHARED by every
library in the process — not the library whose code executes. When
`flext-tap-oracle` runs, a `flext-cli` (or flext-core, flext-meltano) function
that resolves the cache directory resolves `~/.cache/flext-tap-oracle/…`, never
`~/.cache/flext-cli/…`. A library MUST NEVER use its own name for the namespace.

- **Root resolver (layer-0, stdlib-only, no facades):** an XDG root helper per
  base dir returns the OS-native root:
  Linux/BSD `XDG_CACHE_HOME` (`~/.cache`), `XDG_CONFIG_HOME` (`~/.config`),
  `XDG_DATA_HOME` (`~/.local/share`), `XDG_STATE_HOME` (`~/.local/state`),
  `XDG_RUNTIME_DIR`; macOS `~/Library/…`; Windows `%LOCALAPPDATA%` / `%APPDATA%`.
  Mirrors the existing `_platform_cache_root()` family; stays stdlib-only to
  preserve config/settings layer-0 purity (no `c/t/p/m/u` import).
- **Application namespace (process-global, first-wins = outermost app):** base
  `FlextSettings` holds `_app_namespace: ClassVar[str | None]`. The application
  entrypoint (`cli.py` / `api.py` / `__main__`, codegen-added) calls
  `FlextSettings.set_app_namespace("flext-tap-oracle")` exactly once (race-safe
  via the class lock; the first caller — the outermost entrypoint — wins).
  Libraries NEVER call it. Resolution order for `<app>`:
  (1) `FlextSettings._app_namespace`; (2) env `FLEXT_APP_NAMESPACE`;
  (3) `"flext"` (pure-library / flext-core-alone default). `set_app_namespace`
  has a `reset_app_namespace()` companion for tests.
- **Directories are ROOT-ONLY (three access rules):**
  1. **Root namespace = flext-core data.** The flext-core root settings carry the
     standard defaults PLUS the directory group `*_dirs` (`cache_dir`,
     `config_dir`, `data_dir`, `state_dir`, `work_dir`, `runtime_dir`). These are
     the ONLY place directories live, and they resolve to the RUNNING PROJECT's
     namespace (`~/.cache/<app>`, `~/.config/<app>`, …) via `_app_namespace`.
  2. **Library namespaces** are accessed as `settings.<LibNamespace>` /
     `config.<LibNamespace>` (e.g. `settings.Cli`) and expose **NO directory
     fields**.
  3. **Project namespaces** are accessed as `settings.<Namespace>.*` /
     `config.<Namespace>.*` and expose **NO `*_dirs`**.
  A sub-namespace (library or project `FlextXSettings`) MUST NOT define, inherit
  as usable, auto-derive, or auto-configure any directory. It is FORBIDDEN to
  use or configure directories inside a namespace automatically. Every directory
  access goes through the flext-core root, which resolves to the running app.
- **Resolution is access-time, layer-0:** the root directory resolver joins its
  XDG root with the current `<app>` namespace at access time (a stored per-class
  field would bake the wrong namespace, since library singletons build at import
  before the entrypoint sets the namespace). A per-dir env override
  (`FLEXT_<APP>_CONFIG_DIR`, …) always wins. Stdlib + pydantic only; no facades,
  no `@cached_property`/lazy, no `model_rebuild`.
- **Config file location is unified with the root:** `config.py` resolves its
  config-file directory from the flext-core root `config_dir` (single SSOT),
  never from a second CWD/package-relative resolver and never from a
  sub-namespace.
- **Access is the standard SSOT form (U18), root-only for dirs:** directory reads
  go through the flext-core root (`settings.cache_dir` / `config_dir` / … at the
  root), which resolves to the running app. `settings.<LibNamespace>` and
  `settings.<Namespace>.*` never expose directories; facets never re-derive paths.

```python
# settings.py (layer-0: stdlib + pydantic only; no c/t/p/m/u)
import os
import threading
from pathlib import Path
from typing import ClassVar

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class FlextSettings(BaseSettings):
    _app_namespace: ClassVar[str | None] = None
    _app_lock: ClassVar[threading.RLock] = threading.RLock()

    @classmethod
    def set_app_namespace(cls, namespace: str) -> None:
        """Entrypoint-only; first caller (outermost app) wins."""
        with cls._app_lock:
            if FlextSettings._app_namespace is None:
                FlextSettings._app_namespace = namespace

    @classmethod
    def reset_app_namespace(cls) -> None:  # tests only
        with cls._app_lock:
            FlextSettings._app_namespace = None

    @staticmethod
    def _current_app_namespace() -> str:
        return (
            FlextSettings._app_namespace
            or os.environ.get("FLEXT_APP_NAMESPACE")
            or "flext"
        )

    # Directory group lives ONLY on the flext-core root and resolves to the
    # running app namespace at ACCESS time. Sub-namespaces expose NO dirs.
    @computed_field
    @property
    def cache_dir(self) -> Path:
        override = os.environ.get(
            f"FLEXT_{self._current_app_namespace().upper().replace('-', '_')}_CACHE_DIR"
        )
        root = Path(override) if override else _platform_cache_root()
        return root / self._current_app_namespace()

    # config_dir / data_dir / state_dir / work_dir / runtime_dir: same shape,
    # each over its own _platform_*_root(). Defined ONCE here at the root only.


class FlextTapOracleSettings(FlextSettings):
    model_config = SettingsConfigDict(env_prefix="FLEXT_TAP_ORACLE_")
    # Project settings: domain fields ONLY. NO directory fields (rule 3).
    # Directory access is via the flext-core root, resolving to this app once its
    # entrypoint calls FlextSettings.set_app_namespace("flext-tap-oracle").


# flext-tap-oracle entrypoint (cli.py / __main__) — codegen-added:
# FlextSettings.set_app_namespace("flext-tap-oracle")
settings = FlextTapOracleSettings.fetch_global()
```

This section is validated and enforced identically to the rest of ADR-011:
beartype at runtime, rope/ast-grep statically (ban raw-string data paths and
CWD/package-relative config discovery), staged warn → strict per project.

## Consequences

- Pydantic v2 validation and serialization stay intact for all data (nested and
  composed included); DIP is preserved for collaborators via `p.*`.
- beartype self-instrumentation of `flext-core` is green with `claw_is_pep526=True`.
- `model_rebuild()` and ad-hoc lazy imports are removed platform-wide; the only
  lazy surface is the root PEP 562 facade map.
- `TC001/TC002/TC003` are disabled in the ruff SSOT; the runtime-forward rule is
  enforced by beartype (runtime) + rope/ast-grep (static), not by ruff.
- The change is intentionally breaking inside `0.20.0-dev`; every consumer is
  migrated atomically per project and the superseded route is deleted.
- ADR-005 §2 is amended: "reverse references are type-checking-only" is replaced
  by "reverse references are forbidden; forward references are runtime imports".

## Verification

- `flext-core` beartype claw import is green (`BEARTYPE_MODE` on), with zero
  `NameError` / `PydanticUserError` at import, and the full unit suite green.
- A static scan reports zero runtime-evaluated annotation names gated under
  `TYPE_CHECKING`, zero `p → m` / `t → p` / `t → m` edges, zero `model_rebuild(`
  in source, and zero ad-hoc lazy imports outside the root PEP 562 map.
- Data fields validate from dict and round-trip through `model_dump`;
  collaborator fields type-check structurally under beartype.
- `flext-infra` ruff SSOT ignores `TC001/TC002/TC003`; a render of any project
  `pyproject.toml` shows them ignored, and `ruff --fix` no longer moves an
  annotation import into `TYPE_CHECKING`.
- Rollout gate: a project is promoted to `BEARTYPE_MODE=strict` /
  `promote_to_error_when_strict` only after its beartype claw import is green.

## References

- ADR-005 (config/settings/constants/templates/schemas SSOT) — amended §2.
- ADR-002 (platform baseline import-direction checks), ADR-006 (protocol-typed
  driver boundaries), ADR-010 (unified standardization via codegen).
- AGENTS.md §19 (FLEXT Typing & Import Law) and U5/U6/U18/U20 — aligned to this ADR.
- `.agents/skills/`: flext-import-rules, flext-strict-typing, pydantic-v2-governance,
  flext-pydantic-models, flext-agent-strict-rules, flext-mro-namespace-rules.
- Empirical basis: beartype 0.22.9 `claw_is_pep526`; pydantic 2.13 eager core-schema build.
