---
name: flext-import-rules
description: Exact import rules and patterns verified from the actual FLEXT codebase
---

# FLEXT Import Rules

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment


> **Verified from**: Static analysis of all `.py` files in `flext-core` and consuming
> projects (`flext-auth`, `flext-cli`, `flext-ldap`) on 2026-02-17.

## Rule 1: Always Use `from __future__ import annotations`

Every single `.py` file in the codebase starts with this. It enables PEP 563
string-based annotations, avoiding circular import issues at type-check time.

```python
# FIRST non-docstring import in EVERY file
from __future__ import annotations
```

---

## Rule 2: Import Order (enforced by ruff `I` rules)

The exact order enforced by `ruff` with `isort` integration:

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
from flext_core import FlextResult as r, FlextTypes as t
from flext_core import FlextModels, FlextUtilities as u
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

### What is NEVER done in subprojects

```python
# ❌ NEVER import from _models/ or _utilities/ in subprojects
from flext_core._models.base import FlextModelsBase  # Private API!
from flext_core._utilities.guards import FlextUtilitiesGuards  # Private API!

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

## Rule 8: TYPE_CHECKING Imports

Use `typing.TYPE_CHECKING` for imports needed ONLY at type-check time,
especially to break circular dependencies:

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flext_core.container import FlextContainer
    from flext_core.context import FlextContext
```

This is particularly important for Tier 5–6 modules that would otherwise
create circular dependencies.

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
from flext_core import FlextResult as result  # Use: FlextResult as r (or just r)
```
