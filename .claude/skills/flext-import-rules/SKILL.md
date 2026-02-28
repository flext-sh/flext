<!-- TOC START -->

- [Rule 1: Always Use `from __future__ import annotations`](#rule-1-always-use-from-future-import-annotations)
- [Rule 2: Import Order (enforced by ruff `I` rules)](#rule-2-import-order-enforced-by-ruff-i-rules)
- [Rule 3: How to Import from flext-core (Inside flext-core)](#rule-3-how-to-import-from-flext-core-inside-flext-core)
  - [WITHIN flext-core, import via ABSOLUTE paths to submodules](#within-flext-core-import-via-absolute-paths-to-submodules)
  - [Exception: Docstrings use `from flext_core import ...` style for user-facing examples](#exception-docstrings-use-from-flextcore-import-style-for-user-facing-examples)
- [Rule 4: How to Import from flext-core (From Subprojects)](#rule-4-how-to-import-from-flext-core-from-subprojects)
  - [Pattern A: Import with alias (most common, used in 90%+ of files)](#pattern-a-import-with-alias-most-common-used-in-90-of-files)
  - [Pattern B: Import specific class from submodule (used for non-aliased classes)](#pattern-b-import-specific-class-from-submodule-used-for-non-aliased-classes)
  - [Pattern C: Import for extension/inheritance](#pattern-c-import-for-extensioninheritance)
  - [What is NEVER done in subprojects](#what-is-never-done-in-subprojects)
- [Rule 5: Tier Enforcement](#rule-5-tier-enforcement)
  - [Verified violations (these exist but should not be referenced as patterns)](#verified-violations-these-exist-but-should-not-be-referenced-as-patterns)
- [Rule 6: Private Module Convention](#rule-6-private-module-convention)
- [Rule 7: The Facade Alias Pattern](#rule-7-the-facade-alias-pattern)
- [Rule 8: TYPE_CHECKING Policy (Pragmatic Usage)](#rule-8-typechecking-policy-pragmatic-usage)
- [Rule 9: Ruff Configuration (from ruff-shared.toml)](#rule-9-ruff-configuration-from-ruff-sharedtoml)
- [Rule 10: What NOT to Do](#rule-10-what-not-to-do)
- [Rule 11: No Double-Assignment of Facade Aliases](#rule-11-no-double-assignment-of-facade-aliases)
- [Rule 12: Ecosystem MRO & Namespace Composition Architecture](#rule-12-ecosystem-mro--namespace-composition-architecture)
  - [L0 — Foundation](#l0--foundation)
  - [L1 — Domain Libraries](#l1--domain-libraries)
  - [L1 — Platform Libraries](#l1--platform-libraries)
  - [L2 — Integration Projects (Taps/Targets/dbt)](#l2--integration-projects-tapstargetsdbt)
  - [L2 — Custom Composition Projects](#l2--custom-composition-projects)
- [Verification](#verification)
<!-- TOC END -->

---

name: flext-import-rules
description: Exact import rules and patterns verified from the actual FLEXT codebase

---

# FLEXT Import Rules

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment

> **Verified from**: Static analysis of all `.py` files in `flext-core` and consuming
> projects (`flext-auth`, `flext-cli`, `flext-ldap`) on 2026-02-17.
> **Rule**: See `CLAUDE.md` §4 Import Law for canonical aliases, import order, and prohibited import forms.

## Rule 1: Always Use `from __future__ import annotations`

This section provides concrete repository examples for the `from __future__ import annotations` requirement defined in `CLAUDE.md` §3 and §4.

```python
# FIRST non-docstring import in EVERY file
from __future__ import annotations
```

---

## Rule 2: Import Order (enforced by ruff `I` rules)

This section provides the concrete ordering template; canonical policy remains in `CLAUDE.md` §4 Import Law.

```python
from __future__ import annotations          # 1. FUTURE (always first)

import json                                 # 2. STDLIB (bare imports)
import uuid
from collections.abc import Callable        # 2. STDLIB (from imports)
from datetime import UTC, datetime
from typing import Annotated, Final, Self

from pydantic import BaseModel, Field       # 3. THIRD-PARTY
from structlog.typing import BindableLogger

from flext_core import c, t                 # 4. FIRST-PARTY (flext_core.*)

from flext_auth.models import AuthModels    # 5. LOCAL (same project, if applicable)
```

Within each group:

- `import x` before `from x import y`
- Alphabetical by module name
- One import per line (unless same module, then comma-separated)

---

## Rule 3: How to Import from flext-core (Inside flext-core)

### WITHIN flext-core, import via ABSOLUTE paths to submodules

```python
# ✅ CORRECT — Direct absolute import from the specific module
from flext_core import c
from flext_core import t
from flext_core import p
from flext_core import FlextRuntime
from flext_core import m
from flext_core import r
from flext_core import u
from flext_core import e

# ✅ CORRECT — Import from _models/ or _utilities/ (inside their own facades)
from flext_core._models.base import FlextModelsBase
from flext_core._utilities.validation import FlextUtilitiesValidation

# ❌ WRONG — Never import from __init__.py inside the package itself
from flext_core import FlextConstants  # Don't do this within flext-core
```

### Exception: Docstrings use `from flext_core import ...` style for user-facing examples

```python
class FlextModels:
    """Usage:
    >>> from flext_core import m, r
    >>> result = m.Base.create(...)
    """
```

---

## Rule 4: How to Import from flext-core (From Subprojects)

### Pattern A: Import with alias (most common, used in 90%+ of files)

```python
from flext_core import m, r, t
from flext_core import m, u
from flext_core import r, s, t, e  # pre-aliased letters
```

### Pattern B: Import specific class from submodule (used for non-aliased classes)

```python
from flext_core import FlextLogger
from flext_core import FlextDispatcher
from flext_core import FlextRegistry
from flext_core import FlextContext
```

### Pattern C: Import for extension/inheritance

```python
from flext_core import FlextConstants

class FlextAuthConstants(FlextConstants):
    ...

from flext_core import FlextService

class FlextAuthAdminService(FlextService.Admin):
    ...

from flext_core import FlextProtocols

class FlextAuthProtocols(FlextProtocols):
    ...
```

### Pattern D: Cross-project namespace inheritance (CRITICAL for m, c, t, u, p)

When a project depends on another FLEXT project's namespaced types, it MUST inherit the parent project's facade class — NOT `FlextModels`/`FlextProtocols` directly. This gives automatic access to all parent namespaces (e.g., `m.Meltano.*`) via MRO.

```python
# ✅ CORRECT — inherit parent facade, namespaces cascade via MRO
from flext_meltano import FlextMeltanoModels

class FlextTargetOracleModels(FlextMeltanoModels):  # NOT FlextModels!
    class TargetOracle:
        class MyModel(FlextMeltanoModels.ArbitraryTypesModel): ...

m = FlextTargetOracleModels
# m.Meltano.* inherited, m.TargetOracle.* local

# In runtime code — ONLY import m:
from .models import m
schema = m.Meltano.SingerSchemaMessage.model_validate(data)
```

```python
# ❌ WRONG — duplicate alias, extra import surface
from flext_meltano import FlextMeltanoModels as m_meltano  # NEVER

# ❌ WRONG — loses parent namespaces
class FlextTargetOracleModels(FlextModels):  # loses m.Meltano.*

# ❌ WRONG — assignment not valid as type with from __future__ import annotations
class Meltano:
    SingerSchemaMessage = FlextMeltanoModels.Meltano.SingerSchemaMessage
```

This pattern applies identically to `p` (protocols), `c` (constants), `t` (types), `u` (utilities).

### Pattern E: Naming Convention for Integration Projects

All `flext-(tap|target|dbt)-*` projects MUST follow an **EXACT** naming pattern for their facade classes to maintain ecosystem consistency without ambiguity.

**Format**: `Flext<Role><Domain><Facade>`
- **Role**: `Tap`, `Target`, or `Dbt`
- **Domain**: CamelCase version of the domain (e.g., `Ldap`, `DbOracle`, `OracleWms`)
- **Facade**: `Models`, `Constants`, `Types`, `Utilities`, `Protocols`

**Examples**:
- `FlextTargetLdapModels`
- `FlextTapOracleProtocols`
- `FlextDbtOracleWmsUtilities`

> **CRITICAL**: Do NOT include `Meltano` in the class name (e.g., use `FlextTapLdapProtocols`, **not** `FlextMeltanoTapLdapProtocols`). The Meltano integration is represented purely through **inheritance** `(FlextMeltanoProtocols, FlextLdapProtocols)`, not through the name. This strict consistency ensures predictable mapping across all 33 ecosystem projects.

### What is NEVER done in subprojects

```python
# ❌ NEVER import from _models/ or _utilities/ in subprojects
from flext_core._models.base import FlextModelsBase  # Private API!
from flext_core._utilities.guards import FlextUtilitiesGuards  # Private API!
from flext_ldif._models.results import FlextLdifModelsResults  # Private API!

# ✅ CORRECT — use public facade
from flext_ldif import FlextLdifModels
# Then access: FlextLdifModels.Ldif.EntryResult

# Exception: flext_core._models.entity is imported by registry.py (internal to core)
```

---

## Rule 5: Tier Enforcement

A module may ONLY import from modules in **lower** tiers. See `flext-architecture-layers` SKILL for the complete tier map.

```
Tier 0: constants, typings               → No internal imports
Tier 1: runtime                           → constants, typings
Tier 2: protocols                         → typings (NOT constants directly)
Tier 3: models (_models/*)                → constants, typings, protocols
Tier 4: utilities, exceptions, result, settings → Tiers 0-3 + runtime
Tier 5: loggings, context, container, handlers, mixins, decorators → Tiers 0-4
Tier 6: dispatcher, registry, service     → Tiers 0-5
```

### Verified violations (these exist but should not be referenced as patterns)

None found in the current codebase. The tier structure is clean.

---

## Rule 6: Private Module Convention

- Prefixed with `_` (e.g., `_models/`, `_utilities/`, `_decorators/`, `_dispatcher/`)
- These are implementation details, NOT public API
- Only the corresponding facade (e.g., `models.py`, `utilities.py`) may import from them
- Exception: `registry.py` imports from `_models/entity.py` (acceptable as same package)
- Subprojects MUST NOT import from `_` modules

---

## Rule 7: The Facade Alias Pattern

Each facade module creates a lowercase alias:

```python
# constants.py
class FlextConstants: ...
c = FlextConstants

# typings.py
class FlextTypes: ...
t = FlextTypes

# result.py
class FlextResult: ...
r = FlextResult
```

These aliases (`c`, `t`, `p`, `m`, `u`, `r`, `e`, `d`, `h`, `s`, `x`) are
exported in `__init__.py` and used throughout the codebase for concise code:

```python
# REAL code from the codebase:
from flext_core import m
from flext_core import r
from flext_core import h

class MyHandler(h.BaseCommandHandler[m.Cqrs.Command, r]):
    ...
```

---

## Rule 8: TYPE_CHECKING Policy (Pragmatic Usage)

> **Rule**: See `CLAUDE.md` §3 Code Law for the normative `TYPE_CHECKING` policy.

`typing.TYPE_CHECKING` follows a pragmatic policy in the FLEXT ecosystem:

### ALLOWED
- Type-only imports for IDE support and annotations that aren't needed at runtime
- `__init__.py` lazy loading support (see `flext-core/__init__.py:24-59`)
- Forward references in type annotations

```python
# ✅ ALLOWED — type-only import for IDE support
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flext_core.container import FlextContainer

def get_container() -> FlextContainer:  # Annotation works, no runtime import
    ...
```

### FORBIDDEN
- Pydantic model imports (`BaseModel` subclasses need runtime access for validation)
- Band-aid for circular imports (fix architecture instead)
- Any import needed for `isinstance()`, `issubclass()`, or runtime type checks

```python
# ❌ FORBIDDEN — Pydantic models need runtime access
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flext_core.models import FlextModels

class MyModel(FlextModels.Base):  # CRASHES — FlextModels not available at runtime
    name: str

# ❌ FORBIDDEN — hiding circular import instead of fixing architecture
if TYPE_CHECKING:
    from flext_core.utilities import FlextUtilities  # Fix the cycle instead
```

If a circular import exists, fix the architecture:
1. Move the offending code to a lower tier module.
2. Use protocol-based decoupling (`protocols.py`).
3. Use dependency injection via `FlextContainer`.

### Module-Level Lazy Loading (`__init__.py` Optimization)

All package `__init__.py` files **MUST** implement the module-level `__getattr__` lazy loading optimization to avoid circular import storms and optimize startup time. This is the **ONLY** form of lazy loading allowed.

```python
# __init__.py
from typing import TYPE_CHECKING

# 1. Type hinting for IDEs
if TYPE_CHECKING:
    from .models import FlextModels
    from .protocols import FlextProtocols

# 2. Strict mapping
__all__ = ["FlextModels", "FlextProtocols"]

# 3. Native module-level lazy load strategy
def __getattr__(name: str) -> object:
    if name == "FlextModels":
        from .models import FlextModels
        return FlextModels
    if name == "FlextProtocols":
        from .protocols import FlextProtocols
        return FlextProtocols
    
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
```
---

## Rule 9: Ruff Configuration (from ruff-shared.toml)

Key Ruff settings that enforce import discipline:

```toml
target-version = "py313"
line-length = 88
src = ["src"]

[lint.isort]
combine-as-imports = true
force-single-line = false
force-sort-within-sections = true
known-first-party = ["flext_core", "flext_auth", "flext_cli", ...]
known-third-party = ["pydantic", "structlog", "dependency_injector", ...]
lines-after-imports = 2
lines-between-types = 1
order-by-type = true
required-imports = ["from __future__ import annotations"]
section-order = ["future", "standard-library", "third-party", "first-party", "local-folder"]
```

Key enforced rules:

- `I001` — Import sorting
- `I002` — Required `from __future__ import annotations`
- `TCH001/TCH002/TCH003` — Type-checking imports (IGNORED in ruff-shared.toml lines 79-81 for Pydantic compatibility)

---

## Rule 10: What NOT to Do

```python
# ❌ Wild imports
from flext_core import *

# ❌ Relative imports
from .models import FlextModels  # Use: from flext_project.models import m

# ❌ Legacy typing
from typing import List, Dict, Optional, Union  # Use: list, dict, X | None, X | Y

# ❌ Evaluation hacks
eval(user_input)
getattr(obj, "dynamic_attr")  # For architecture logic

# ❌ Shadowing aliases
from flext_core import result  # Use: r
```

> **Note on Relative Imports**: Relative imports exist in some projects (tracked separately). However, **all new code MUST use absolute imports**. Relative imports are not the preferred pattern and should not be used in new development.

## Rule 11: No Double-Assignment of Facade Aliases

In definition files (`constants.py`, `models.py`, `protocols.py`, `utilities.py`),
the facade alias (`c`, `m`, `p`, `u`) MUST be assigned exactly **once** — at the
bottom of the module. Never import the parent alias and then reassign it.

```python
# ❌ ANTI-PATTERN — double-assignment creates confusing scope
from flext_core import c                   # c = FlextConstants at import time

class FlextProjectConstants(c):            # uses c as FlextConstants
    class Foo:
        BAR = c.Something.VALUE            # c is still FlextConstants here

c = FlextProjectConstants                  # REASSIGNS c — scope confusion!

# ✅ CORRECT — import parent class by name, alias only at bottom
from flext_core import FlextConstants

class FlextProjectConstants(FlextConstants):
    class Foo:
        BAR = FlextConstants.Something.VALUE  # explicit parent reference

c = FlextProjectConstants                  # single, clear assignment
```

This applies to ALL facade pairs:

- `from flext_core import FlextConstants` + `c = FlextProjectConstants`
- `from flext_core import FlextModels` + `m = FlextProjectModels`
- `from flext_core import FlextProtocols` + `p = FlextProjectProtocols`
- `from flext_core import FlextUtilities` + `u = FlextProjectUtilities`

**Detection**: `grep -n "^from flext_core.*import.*\b[cmptu]\b" <file>` combined
with `grep -n "^[cmptu] = " <file>` — if both match, it's a double-assignment.

---

## Rule 12: Ecosystem MRO & Namespace Composition Architecture

The FLEXT ecosystem follows a strict, tier-based inheritance model. These are the **TARGET** MRO and Namespace resolution behaviors for all 33 ecosystem projects.

> **CRITICAL - UNIVERSAL APPLICATION**: This architectural rule applies **IDENTICALLY** across all five core components in every project:
> 1. `Protocols` (`p`)
> 2. `Models` (`m`)
> 3. `Types` (`t`)
> 4. `Utilities` (`u`)
> 5. `Constants` (`c`)
>
> If a project's `Protocols` inherit from `FlextCliProtocols`, its `Models` MUST correspondingly inherit from `FlextCliModels`, its `Utilities` from `FlextCliUtilities`, and so on.

**NAMESPACE & MRO MECHANICS**: Each project defines **exactly ONE** inner class representing its own namespace (e.g., `class TapOracle:`). By inheriting parent facade classes, the project automatically gains access to all parent namespaces via Python's Method Resolution Order (MRO).
Example: `AlgarOudMigProtocols(FlextLdapProtocols, FlextCliProtocols)` gives you access to `.AlgarOudMig` (its own), `.Cli` (from CLI), `.Ldap` (from LDAP), and `.Ldif` (because LDAP inherits from LDIF), plus all base methods from `flext-core`.

**TARGET ARCHITECTURE**: The patterns below show what the architecture *should be* natively. Some projects currently inherit `FlextProtocols` directly instead of their intended platform dependency (e.g., `flext-meltano` currently uses `FlextProtocols` but should use `FlextCliProtocols`). When refactoring or building new modules, refer to this target state.

### L0 — Foundation
**`flext-core`** forms the basis of all ecosystem projects.
- **Class**: `FlextProtocols` (same for Models `m`, Constants `c`, Utilities `u`, Types `t`)
- **Inherits**: `(base)`
- **Namespace**: Provides root-level base protocols (`.Result`, `.Service`, `.Config`, etc. without inner namespace class)

---

### L1 — Domain Libraries
Domain libraries encapsulate logic applicable regardless of execution environment.
- **Inheritance Pattern**: Domain libraries generally inherit from `FlextProtocols` (or a lower-tier domain library like Ldif).
- **Namespaces**: Adds one dedicated namespace inner-class (e.g., `.DbOracle`).

| Project | Class Name | TARGET Inherits | Own Namespace | Full Access |
|---|---|---|---|---|
| `flext-ldif` | `FlextLdifProtocols` | `(FlextProtocols)` | `.Ldif` | `.Ldif`, core root |
| `flext-ldap` | `FlextLdapProtocols` | `(FlextLdifProtocols)` | `.Ldap` | `.Ldap`, `.Ldif`, core root |
| `flext-db-oracle` | `FlextDbOracleProtocols` | `(FlextProtocols)` | `.DbOracle` | `.DbOracle`, core root |
| `flext-oracle-wms` | `FlextOracleWmsProtocols` | `(FlextProtocols)` | `.OracleWms` | `.OracleWms`, core root |
| `flext-oracle-oic` | `FlextOracleOicProtocols` | `(FlextProtocols)` | `.OracleOic` | `.OracleOic`, core root |

---

### L1 — Platform Libraries
Base Tools provide infrastructure integrations.
- **Standalone Tools**: Inherit directly from `FlextProtocols`
- **Dependent Tools**: Inherit from other L1 Base Tools (e.g., UI needs Web, Tap needs CLI).

| Project | Class Name | TARGET Inherits | Own Namespace | Full Access |
|---|---|---|---|---|
| *Base Tools* | | | | |
| `flext-cli` | `FlextCliProtocols` | `(FlextProtocols)` | `.Cli` | `.Cli`, core |
| `flext-web` | `FlextWebProtocols` | `(FlextProtocols)` | `.Web` | `.Web`, core |
| `flext-grpc` | `FlextGrpcProtocols` | `(FlextProtocols)` | `.Grpc` | `.Grpc`, core |
| `flext-plugin` | `FlextPluginProtocols` | `(FlextProtocols)` | `.Plugin` | `.Plugin`, core |
| `flext-observability`| `FlextObservabilityProtocols` | `(FlextProtocols)` | `.Observability` | `.Observability`, core |
| *Dependent Tools* | | | | |
| `flext-meltano` | `FlextMeltanoProtocols` | `(FlextCliProtocols)` | `.Meltano` | `.Meltano`, `.Cli`, core |
| `flext-api` | `FlextApiProtocols` | `(FlextWebProtocols)` | `.Api` | `.Api`, `.Web`, core |
| `flext-auth` | `FlextAuthProtocols` | `(FlextWebProtocols)` | `.Auth` | `.Auth`, `.Web`, core |
| `flext-quality` | `FlextQualityProtocols` | `(FlextWebProtocols, FlextCliProtocols)` | `.Quality` | `.Quality`, `.Web`, `.Cli`,  core |

---

### L2 — Integration Projects (Taps/Targets/dbt)
Integrations MUST compose exactly ONE platform and ONE domain. Because `FlextMeltanoProtocols` inherits `FlextCliProtocols` in the target architecture, integrations naturally gain access to `.Cli` tools.

**Pattern Formula**: `Flext<Role><Domain><Facade> (FlextMeltano<Facade>, Flext<Domain><Facade>)`

| Sub-Tier | Project | TARGET Class Name | TARGET Inherits | Own Namespace | Full Access |
|---|---|---|---|---|---|
| **Taps** | `flext-tap-ldap` | `FlextTapLdapProtocols` | `(FlextMeltanoProtocols, FlextLdapProtocols)` | `.TapLdap` | `.TapLdap`, `.Meltano`, `.Cli`, `.Ldap`, `.Ldif`, core root |
| | `flext-tap-ldif` | `FlextTapLdifProtocols` | `(FlextMeltanoProtocols, FlextLdifProtocols)` | `.TapLdif` | `.TapLdif`, `.Meltano`, `.Cli`, `.Ldif`, core root |
| | `flext-tap-oracle` | `FlextTapOracleProtocols` | `(FlextMeltanoProtocols, FlextDbOracleProtocols)` | `.TapOracle` | `.TapOracle`, `.Meltano`, `.Cli`, `.DbOracle`, core root |
| | `flext-tap-oracle-oic` | `FlextTapOracleOicProtocols` | `(FlextMeltanoProtocols, FlextOracleOicProtocols)` | `.TapOracleOic` | `.TapOracleOic`, `.Meltano`, `.Cli`, `.OracleOic`, core root |
| | `flext-tap-oracle-wms` | `FlextTapOracleWmsProtocols` | `(FlextMeltanoProtocols, FlextOracleWmsProtocols)` | `.TapOracleWms` | `.TapOracleWms`, `.Meltano`, `.Cli`, `.OracleWms`, core root |
| **Targets** | `flext-target-ldap` | `FlextTargetLdapProtocols` | `(FlextMeltanoProtocols, FlextLdapProtocols)` | `.TargetLdap` | `.TargetLdap`, `.Meltano`, `.Cli`, `.Ldap`, `.Ldif`, core root |
| | `flext-target-ldif` | `FlextTargetLdifProtocols` | `(FlextMeltanoProtocols, FlextLdifProtocols)` | `.TargetLdif` | `.TargetLdif`, `.Meltano`, `.Cli`, `.Ldif`, core root |
| | `flext-target-oracle` | `FlextTargetOracleProtocols` | `(FlextMeltanoProtocols, FlextDbOracleProtocols)` | `.TargetOracle` | `.TargetOracle`, `.Meltano`, `.Cli`, `.DbOracle`, core root |
| | `flext-target-oracle-oic` | `FlextTargetOracleOicProtocols` | `(FlextMeltanoProtocols, FlextOracleOicProtocols)` | `.TargetOracleOic` | `.TargetOracleOic`, `.Meltano`, `.Cli`, `.OracleOic`, core root |
| | `flext-target-oracle-wms` | `FlextTargetOracleWmsProtocols` | `(FlextMeltanoProtocols, FlextOracleWmsProtocols)` | `.TargetOracleWms` | `.TargetOracleWms`, `.Meltano`, `.Cli`, `.OracleWms`, core root |
| **dbt** | `flext-dbt-ldap` | `FlextDbtLdapProtocols` | `(FlextMeltanoProtocols, FlextLdapProtocols)` | `.DbtLdap` | `.DbtLdap`, `.Meltano`, `.Cli`, `.Ldap`, `.Ldif`, core root |
| | `flext-dbt-ldif` | `FlextDbtLdifProtocols` | `(FlextMeltanoProtocols, FlextLdifProtocols)` | `.DbtLdif` | `.DbtLdif`, `.Meltano`, `.Cli`, `.Ldif`, core root |
| | `flext-dbt-oracle` | `FlextDbtOracleProtocols` | `(FlextMeltanoProtocols, FlextDbOracleProtocols)` | `.DbtOracle` | `.DbtOracle`, `.Meltano`, `.Cli`, `.DbOracle`, core root |
| | `flext-dbt-oracle-wms` | `FlextDbtOracleWmsProtocols` | `(FlextMeltanoProtocols, FlextOracleWmsProtocols)` | `.DbtOracleWms` | `.DbtOracleWms`, `.Meltano`, `.Cli`, `.OracleWms`, core root |

**Example (Tap):**
```python
# flext-tap-oracle/src/flext_tap_oracle/protocols.py
class FlextTapOracleProtocols(FlextMeltanoProtocols, FlextDbOracleProtocols):
    class TapOracle:
        class DataExtractionProtocol(Protocol): ...

p = FlextTapOracleProtocols
# Gives access to: p.TapOracle.*, p.Meltano.*, p.Cli.*, p.DbOracle.*, and core root
```

---

### L2 — Custom Composition Projects
Business-specific projects use structural composition combining Domains and Platforms as needed.

| Project | Class Name | TARGET Inherits | Access Gained via MRO |
|---|---|---|---|
| `algar-oud-mig` | `AlgarOudMigProtocols` | `(FlextLdapProtocols, FlextCliProtocols)` | `.AlgarOudMig`, `.Ldap`, `.Ldif`, `.Cli`, core |
| `gruponos-meltano-native` | `GruponosMeltanoNativeProtocols`| `(FlextTapOracleProtocols, FlextTargetOracleWmsProtocols)`| `.GruponosMeltanoNative`, `.TapOracle`, `.TargetOracleWms`, `.Meltano`, `.Cli`, `.DbOracle`, `.OracleWms`, core |

> **Namespacing Access Rule & Verification**:
>
> Every namespace mapped as "Full Access" is available transparently on the project's alias.
> If `p = AlgarOudMigProtocols`:
> - `p.AlgarOudMig.MutableEntryProtocol` (Own namespace)
> - `p.Ldap.LdapEntryProtocol` (Inherited from `FlextLdapProtocols`)
> - `p.Ldif.EntryProtocol` (Inherited transitively from `FlextLdifProtocols` -> `FlextLdapProtocols`)
> - `p.Cli.Command` (Inherited from `FlextCliProtocols`)
> - `p.Service` (Inherited transitively from `FlextProtocols` -> core root)
>
> **You do NOT need to import the parent aliases** (like `ldif_p` or `cli_p`). Simply import the local alias (`from .protocols import p`) and navigate the namespaces `p.Ldif.*`, `p.Cli.*`.

---

## Verification

Make gates:

- `make check PROJECT=flext-core CHECK_GATES=lint` — ruff import ordering rules
- `make check PROJECT=flext-core CHECK_GATES=type` — type-check verifies import resolution
- `make check PROJECT=flext-core` — all 4 gates including import enforcement

Pattern checks:

- `rg -n "from flext_core\._" --glob "**/*.py" flext-*/src/` — detect private import violations
- `rg -n "from typing import List|from typing import Dict|from typing import Optional" --glob "**/*.py" flext-core/src/` — detect legacy typing imports
- `rg -n "import \*" --glob "**/*.py" flext-core/src/` — detect wildcard imports

