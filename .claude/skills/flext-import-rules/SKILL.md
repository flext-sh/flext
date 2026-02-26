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
- [Rule 8: TYPE_CHECKING Is FORBIDDEN](#rule-8-typechecking-is-forbidden)
- [Rule 9: Ruff Configuration (from ruff-shared.toml)](#rule-9-ruff-configuration-from-ruff-sharedtoml)
- [Rule 10: What NOT to Do](#rule-10-what-not-to-do)
- [Rule 11: No Double-Assignment of Facade Aliases](#rule-11-no-double-assignment-of-facade-aliases)
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

from flext_core.constants import c          # 4. FIRST-PARTY (flext_core.*)
from flext_core.typings import t

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
from flext_core.constants import c
from flext_core.typings import t
from flext_core.protocols import p
from flext_core.runtime import FlextRuntime
from flext_core.models import m
from flext_core.result import r
from flext_core.utilities import u
from flext_core.exceptions import e

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
    >>> from flext_core import FlextModels, r
    >>> result = FlextModels.Base.create(...)
    """
```

---

## Rule 4: How to Import from flext-core (From Subprojects)

### Pattern A: Import with alias (most common, used in 90%+ of files)

```python
from flext_core import r, t
from flext_core import FlextModels, u
from flext_core import r, s, t, e  # pre-aliased letters
```

### Pattern B: Import specific class from submodule (used for non-aliased classes)

```python
from flext_core.loggings import FlextLogger
from flext_core.dispatcher import FlextDispatcher
from flext_core.registry import FlextRegistry
from flext_core.context import FlextContext
```

### Pattern C: Import for extension/inheritance

```python
from flext_core import FlextConstants
class FlextAuthConstants(FlextConstants):
    ...

from flext_core import FlextService
class AuthAdminService(FlextService.Admin):
    ...

from flext_core.protocols import FlextProtocols
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

### Rule 4E: Naming Convention for Integration Projects

All `flext-(tap|target|dbt)-*` projects MUST follow this naming pattern for their
facade classes:

```
Flext<Role><Domain>Models     — e.g., FlextTargetLdapModels, FlextTapOracleModels
Flext<Role><Domain>Constants  — e.g., FlextTargetLdapConstants
Flext<Role><Domain>Types      — e.g., FlextTargetLdapTypes
Flext<Role><Domain>Utilities  — e.g., FlextTargetLdapUtilities
Flext<Role><Domain>Protocols  — e.g., FlextTargetLdapProtocols
```

Where `<Role>` is one of: `Target`, `Tap`, `Dbt`, `MeltanoTap`, `MeltanoTarget`.

The `Meltano` prefix in the class name is **optional** — what matters is the
**inheritance** from `FlextMeltanoModels`. Both `FlextTargetLdapModels` and
`FlextMeltanoTapLdapModels` are acceptable as long as they inherit correctly.

```python
# ✅ Both are correct:
class FlextTargetLdapModels(FlextMeltanoModels, FlextLdapModels): ...
class FlextMeltanoTapLdapModels(FlextMeltanoModels, FlextLdapModels): ...
```

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
from flext_core.models import m
from flext_core.result import r
from flext_core.protocols import p

class MyHandler(h.BaseCommandHandler[m.Cqrs.Command, r]):
    ...
```

---

## Rule 8: TYPE_CHECKING Is FORBIDDEN

> **Rule**: See `CLAUDE.md` §3 Code Law for the normative `TYPE_CHECKING` prohibition.

`typing.TYPE_CHECKING` is **prohibited** in the FLEXT ecosystem.
It is a band-aid for circular imports — the real fix is proper module layering.

```python
# ❌ FORBIDDEN — TYPE_CHECKING block
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flext_core.container import FlextContainer

# ✅ CORRECT — move the dependency to the right tier or use protocols
from flext_core.protocols import FlextProtocols
# Use protocol-based decoupling instead of TYPE_CHECKING
```

If a circular import exists, fix the architecture:

1. Move the offending code to a lower tier module.
2. Use protocol-based decoupling (`protocols.py`).
3. Use dependency injection via `FlextContainer`.

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
- `TCH001/TCH002` — Type-checking block for type-only imports
- `UP035/UP038` — Modern import forms (e.g., `collections.abc.Sequence` over `typing.Sequence`)
- `F401` — Unused imports

---

## Rule 10: What NOT to Do

```python
# ❌ Wild imports
from flext_core import *
from flext_core.models import *

# ❌ Relative imports (the codebase uses ZERO relative imports)
from .models import FlextModels
from ..constants import c

# ❌ Importing typing constructs the old way
from typing import List, Dict, Optional, Union  # Use list, dict, X | None, X | Y

# ❌ Importing from collections.abc via typing
from typing import Sequence  # Use: from collections.abc import Sequence

# ❌ Shadowing aliases inconsistently
from flext_core import result  # Use: r (or just r)
```

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

## Verification

Make gates:

- `make check PROJECT=flext-core CHECK_GATES=lint` — ruff import ordering rules
- `make check PROJECT=flext-core CHECK_GATES=type` — type-check verifies import resolution
- `make check PROJECT=flext-core` — all 4 gates including import enforcement

Pattern checks:

- `rg -n "from flext_core\._" --glob "**/*.py" flext-*/src/` — detect private import violations
- `rg -n "from typing import List|from typing import Dict|from typing import Optional" --glob "**/*.py" flext-core/src/` — detect legacy typing imports
- `rg -n "import \*" --glob "**/*.py" flext-core/src/` — detect wildcard imports
