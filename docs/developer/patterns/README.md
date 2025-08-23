# FLEXT Patterns

**Version**: 0.9.0 | **Status**: Active Standard

## Overview

Unified semantic patterns that ensure consistency, type safety, and maintainability across the FLEXT ecosystem. These patterns eliminate duplication and provide clear architectural guidelines.

## Pattern Categories

### [Foundation Patterns](./foundation.md)

Core architectural patterns including FlextModel, FlextResult, FlextEntity, and FlextValue.

### [Type System Patterns](./types.md)

Hierarchical type system with FlextTypes namespace organization.

### [Configuration & CLI Patterns](./config-cli.md)

Hierarchical configuration management and command-line interface patterns.

### [Error & Observability Patterns](./error-observability.md)

Comprehensive error handling and observability architecture.

### [Constants & Semantics Patterns](./constants.md)

Hierarchical constant organization and semantic structures.

### [Utility & Helper Patterns](./utilities.md)

Domain-specific utility organization with consistent naming conventions.

## Quick Usage

```python
# Foundation
from flext_core.foundation import FlextModel, FlextResult

# Types
from flext_core.types import FlextTypes

# Configuration
from flext_core.config import FlextConfigHierarchical

# Errors
from flext_core.errors import FlextBusinessError, FlextTechnicalError

# Constants
from flext_core.constants import FlextConstants

# Utilities
from flext_auth.utils import flext_auth_hash_password
```

## Pattern Hierarchy

```
Foundation Patterns (base layer)
    ↑
Type System & Constants
    ↑
Configuration & Error Handling
    ↑
Utility Patterns (application layer)
```

---

See [Quick Reference](../quick-reference.md) for rapid pattern lookup.
