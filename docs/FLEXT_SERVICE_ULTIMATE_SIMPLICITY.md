# FlextService - Ultimate Simplicity (Python 3.13)

**Philosophy:** "Serviços são apenas funções com validação Pydantic"  
**Goal:** ZERO boilerplate, ZERO ceremony, ZERO code duplication

---

## 🎯 The Problem with Current Approach

```python
# ❌ TOO MUCH CODE for simple operations:

# 1. Service class
class ParseLdif(FlextService[list[Entry]]):
    source: str
    def execute(self) -> FlextResult[list[Entry]]:
        return FlextResult.ok(parse(self.source))

# 2. Factory function (DUPLICAÇÃO!)
def parse_ldif(source: str) -> list[Entry]:
    return ParseLdif(source=source).value
    
# 3. Usage (ainda tem .value!)
entries = parse_ldif("file.ldif")  # Ou
entries = ParseLdif(source="file.ldif").value

# Problemas:
# - Factory é duplicação do service
# - Ainda precisa .value ou .result
# - Precisa implementar execute()
# - Muito código para algo simples
```

---

## 💡 The Solution: Auto-Executing Services

### Use `__call__` for Direct Execution

```python
# flext-core/src/flext_core/service.py

from typing import ParamSpec, Concatenate
from pydantic import BaseModel

P = ParamSpec('P')

class FlextService[TResult](BaseModel):
    """Service that executes automatically when called.
    
    NO .execute() needed!
    NO .value needed!
    NO .result needed!
    NO factory functions needed!
    
    Just implement compute() and call the instance!
    
    Example:
        class ParseLdif(FlextService[list[Entry]]):
            source: str
            
            def compute(self) -> list[Entry]:
                return parse(self.source)
        
        # Direct usage - ZERO ceremony!
        entries = ParseLdif(source="file.ldif")()
        
        # Or even simpler with __new__:
        entries = ParseLdif("file.ldif")  # Auto-executes!
    """
    
    def __call__(self) -> TResult:
        """Execute service when called - ZERO ceremony!
        
        This allows:
            service = MyService(param="value")
            result = service()  # Execute!
        
        Or even:
            result = MyService(param="value")()
        """
        return self.compute()
    
    def compute(self) -> TResult:
        """Override this - return value directly, NOT FlextResult!
        
        Example:
            def compute(self) -> list[Entry]:
                return parse(self.source)
        
        Raise exceptions on error (we'll catch them).
        """
        raise NotImplementedError(f"{self.__class__.__name__}.compute() not implemented")


# Even better - auto-execute on creation!
class AutoFlextService[TResult](BaseModel):
    """Service that executes AUTOMATICALLY on instantiation.
    
    ULTIMATE simplicity - just instantiate and get the result!
    
    Example:
        class ParseLdif(AutoFlextService[list[Entry]]):
            source: str
            
            def compute(self) -> list[Entry]:
                return parse(self.source)
        
        # ZERO ceremony - auto-executes!
        entries = ParseLdif(source="file.ldif")
        # That's it! entries is list[Entry], not a service instance!
    """
    
    def __new__(cls, **kwargs):
        """Intercept creation to auto-execute.
        
        Instead of returning instance, execute and return result!
        """
        # Create instance for validation
        instance = super().__new__(cls)
        instance.__init__(**kwargs)  # Pydantic validation
        
        # Execute and return result directly!
        return instance.compute()
    
    def compute(self) -> TResult:
        """Override this - return value directly."""
        raise NotImplementedError
```

---

## 🚀 Real Example: Ultimate Simplicity

### Pattern 1: Callable Service (Explicit Call)

```python
# flext-ldif/src/flext_ldif/services/parser.py

from pathlib import Path
from typing import Annotated
from pydantic import Field
from flext_core.service import FlextService

class ParseLdif(FlextService[list[Entry]]):
    """Parse LDIF - callable service.
    
    Usage:
        entries = ParseLdif(source="file.ldif")()
    """
    
    source: Annotated[str | Path, Field(description="LDIF source")]
    encoding: str = "utf-8"
    
    def compute(self) -> list[Entry]:
        """Return entries directly (NOT FlextResult)."""
        # Load
        match self.source:
            case Path() as path:
                content = path.read_text(encoding=self.encoding)
            case str() as content:
                pass
        
        # Parse
        return parse_ldif_content(content)


# Usage - explicit call
service = ParseLdif(source="file.ldif")
entries = service()  # Call it!

# Or one-liner
entries = ParseLdif(source="file.ldif")()
```

### Pattern 2: Auto-Executing Service (ULTIMATE)

```python
# flext-ldif/src/flext_ldif/services/parser.py

from flext_core.service import AutoFlextService

class ParseLdif(AutoFlextService[list[Entry]]):
    """Parse LDIF - auto-executing service.
    
    Usage:
        entries = ParseLdif(source="file.ldif")
        # That's it! Returns list[Entry] directly!
    """
    
    source: Annotated[str | Path, Field(description="LDIF source")]
    encoding: str = "utf-8"
    
    def compute(self) -> list[Entry]:
        """Compute result."""
        match self.source:
            case Path() as path:
                content = path.read_text(encoding=self.encoding)
            case str() as content:
                pass
        
        return parse_ldif_content(content)


# Usage - ZERO ceremony!
entries = ParseLdif(source="file.ldif")  # Auto-executes!
# entries is list[Entry], NOT a service instance!

# Pydantic validation still works!
try:
    entries = ParseLdif(source=123)  # ValidationError!
except ValidationError as e:
    print(f"Invalid input: {e}")
```

### Comparison: Before vs After

```python
# ════════════════════════════════════════════════════════════════
# OLD WAY (Too much code)
# ════════════════════════════════════════════════════════════════

# 1. Service with execute()
class ParseLdif(FlextService[list[Entry]]):
    source: str
    
    def execute(self) -> FlextResult[list[Entry]]:
        try:
            return FlextResult.ok(parse(self.source))
        except Exception as e:
            return FlextResult.fail(str(e))

# 2. Factory function (DUPLICAÇÃO!)
def parse_ldif(source: str) -> list[Entry]:
    return ParseLdif(source=source).value

# 3. Usage
entries = parse_ldif("file.ldif")
# Or
entries = ParseLdif(source="file.ldif").value


# ════════════════════════════════════════════════════════════════
# NEW WAY (Minimal code)
# ════════════════════════════════════════════════════════════════

# 1. Service with compute()
class ParseLdif(AutoFlextService[list[Entry]]):
    source: str
    
    def compute(self) -> list[Entry]:
        return parse(self.source)

# 2. NO factory needed!

# 3. Usage - DIRECT!
entries = ParseLdif(source="file.ldif")


# ════════════════════════════════════════════════════════════════
# CODE REDUCTION
# ════════════════════════════════════════════════════════════════
# Lines of code: 20 → 8 (60% reduction)
# Concepts: 5 → 2 (FlextResult, factory, .value, execute eliminated)
# Boilerplate: HIGH → ZERO
```

---

## 🎨 Complete Real-World Example

```python
# flext-ldif/src/flext_ldif/services/parser.py

from pathlib import Path
from typing import Annotated
from pydantic import Field, field_validator
from flext_core.service import AutoFlextService
from flext_ldif.models import Entry

class ParseLdif(AutoFlextService[list[Entry]]):
    """Parse LDIF file.
    
    Auto-executing service - just instantiate to get results!
    
    Example:
        >>> entries = ParseLdif(source="users.ldif")
        >>> for entry in entries:
        ...     print(entry.dn)
    """
    
    # Pydantic validation
    source: Annotated[
        str | Path,
        Field(description="LDIF file path or content")
    ]
    
    encoding: Annotated[
        str,
        Field(default="utf-8")
    ] = "utf-8"
    
    strict: bool = True
    
    # Field validators
    @field_validator('source')
    @classmethod
    def validate_source(cls, v: str | Path) -> str | Path:
        if isinstance(v, Path) and not v.exists():
            raise ValueError(f"File not found: {v}")
        return v
    
    # Implementation
    def compute(self) -> list[Entry]:
        """Parse LDIF and return entries."""
        # Load content (Python 3.13 match)
        match self.source:
            case Path() as path:
                content = path.read_text(encoding=self.encoding)
            case str() as content:
                pass
        
        # Parse
        entries = parse_ldif_content(content, strict=self.strict)
        
        # Return directly (no FlextResult!)
        return entries


# Usage examples
# ════════════════════════════════════════════════════════════════

# Simple usage - ZERO ceremony!
entries = ParseLdif(source="users.ldif")
print(f"Got {len(entries)} entries")

# With options
entries = ParseLdif(
    source=Path("users.ldif"),
    encoding="iso-8859-1",
    strict=False
)

# Validation automatic
try:
    entries = ParseLdif(source=Path("nonexistent.ldif"))
except ValueError as e:
    print(f"Error: {e}")  # "File not found: nonexistent.ldif"

# Pattern matching for flexibility
match ParseLdif(source="users.ldif"):
    case [] as empty:
        print("No entries")
    case [entry] as single:
        print(f"One entry: {entry.dn}")
    case entries:
        print(f"Multiple entries: {len(entries)}")
```

---

## 🔄 Error Handling

### Option 1: Exceptions (Simple)

```python
class ParseLdif(AutoFlextService[list[Entry]]):
    source: str
    
    def compute(self) -> list[Entry]:
        """Raise exceptions on error (simple)."""
        if not self.source:
            raise ValueError("Source cannot be empty")
        
        return parse(self.source)


# Usage with try/except
try:
    entries = ParseLdif(source="file.ldif")
except ValueError as e:
    print(f"Error: {e}")
```

### Option 2: Optional Return (Safe)

```python
class ParseLdifSafe(AutoFlextService[list[Entry] | None]):
    """Safe version - returns None on error."""
    source: str
    
    def compute(self) -> list[Entry] | None:
        """Return None on error (never raises)."""
        try:
            return parse(self.source)
        except Exception:
            return None


# Usage - no exception handling needed
entries = ParseLdifSafe(source="might_fail.ldif")
if entries:
    print(f"Success: {len(entries)} entries")
else:
    print("Parsing failed")
```

### Option 3: Result Type (Advanced)

```python
from typing import Annotated

type Success[T] = Annotated[T, "success"]
type Failure = Annotated[str, "error"]
type Result[T] = Success[T] | Failure

class ParseLdifResult(AutoFlextService[Result[list[Entry]]]):
    """Returns Result type."""
    source: str
    
    def compute(self) -> Result[list[Entry]]:
        """Return Success or Failure."""
        try:
            entries = parse(self.source)
            return Success(entries)
        except Exception as e:
            return Failure(str(e))


# Usage with pattern matching
match ParseLdifResult(source="file.ldif"):
    case Success(entries):
        print(f"Got {len(entries)} entries")
    case Failure(error):
        print(f"Error: {error}")
```

---

## 📊 Benefits Summary

### Code Reduction

| Aspect | Old | New | Reduction |
|--------|-----|-----|-----------|
| Service code | 15 lines | 8 lines | 47% |
| Factory function | 3 lines | 0 lines | 100% |
| Usage | 1 line + .value | 1 line | .value eliminated |
| execute() | Required | NO (use compute()) | Simpler |
| FlextResult | Required | NO (return direct) | Simpler |

### Concepts Eliminated

- ❌ `.execute()` - not needed
- ❌ `.value` - not needed
- ❌ `.result` - not needed
- ❌ `FlextResult` - not needed (for simple cases)
- ❌ Factory functions - not needed
- ❌ `.unwrap()` - not needed

### What Remains

- ✅ Pydantic validation (field validators, model validators)
- ✅ Type safety (generics, type hints)
- ✅ Infrastructure (logger, config via mixins - optional)
- ✅ `compute()` method (simple, direct)

---

## 🎯 Implementation in flext-core

```python
# flext-core/src/flext_core/service.py

"""Ultra-simple service base classes.

Zero ceremony, zero boilerplate, maximum simplicity.
"""

from pydantic import BaseModel
from abc import ABC, abstractmethod

# ═══════════════════════════════════════════════════════════════════════
# OPTION 1: Callable Service (explicit call)
# ═══════════════════════════════════════════════════════════════════════

class FlextService[TResult](BaseModel, ABC):
    """Service that executes when called.
    
    Usage:
        result = MyService(params)()  # Call to execute
    """
    
    def __call__(self) -> TResult:
        """Execute service."""
        return self.compute()
    
    @abstractmethod
    def compute(self) -> TResult:
        """Override this to implement service logic."""
        ...


# ═══════════════════════════════════════════════════════════════════════
# OPTION 2: Auto-Executing Service (ULTIMATE SIMPLICITY)
# ═══════════════════════════════════════════════════════════════════════

class AutoFlextService[TResult](BaseModel, ABC):
    """Service that auto-executes on instantiation.
    
    ULTIMATE simplicity - instantiate and get result!
    
    Usage:
        result = MyService(params)  # Auto-executes!
    """
    
    def __new__(cls, **kwargs):
        """Auto-execute on creation."""
        # Validate with Pydantic
        instance = super().__new__(cls)
        instance.__init__(**kwargs)
        
        # Execute and return result (not instance!)
        return instance.compute()
    
    @abstractmethod
    def compute(self) -> TResult:
        """Override this to implement service logic."""
        ...


# ═══════════════════════════════════════════════════════════════════════
# OPTION 3: Hybrid (best of both worlds)
# ═══════════════════════════════════════════════════════════════════════

class FlextServiceMixin:
    """Mixin for infrastructure access (optional)."""
    
    @property
    def logger(self):
        """Get logger."""
        from flext_core.loggings import FlextLogger
        return FlextLogger(self.__class__.__name__)
    
    @property
    def config(self):
        """Get config."""
        from flext_core.config import FlextConfig
        return FlextConfig.get_global_instance()


# Full-featured auto-executing service
class FlextAutoService[TResult](AutoFlextService[TResult], FlextServiceMixin):
    """Auto-executing service with infrastructure.
    
    Combines:
    - Auto-execution (from AutoFlextService)
    - Infrastructure access (from FlextServiceMixin)
    - Pydantic validation (from BaseModel)
    
    Usage:
        class MyService(FlextAutoService[Result]):
            param: str
            
            def compute(self) -> Result:
                self.logger.info(f"Processing {self.param}")
                return process(self.param)
        
        # Zero ceremony!
        result = MyService(param="value")
    """
    pass


# Exports
__all__ = [
    "FlextService",        # Callable (explicit)
    "AutoFlextService",    # Auto-executing
    "FlextAutoService",    # Auto-executing + infrastructure
]
```

---

## ✅ Final Recommendation

### Use AutoFlextService

```python
from flext_core.service import AutoFlextService

class ParseLdif(AutoFlextService[list[Entry]]):
    """Parse LDIF - ultra-simple!"""
    source: str
    
    def compute(self) -> list[Entry]:
        return parse(self.source)

# Usage - ZERO ceremony!
entries = ParseLdif(source="file.ldif")
```

**Benefits:**
- ✅ NO factory functions (eliminated)
- ✅ NO .value (eliminated)
- ✅ NO .result (eliminated)
- ✅ NO .execute() (eliminated)
- ✅ Direct instantiation = result
- ✅ Pydantic validation preserved
- ✅ Type-safe
- ✅ Minimal code

**Trade-off:**
- Instance is consumed on creation (can't reuse)
- For reusable instances, use `FlextService` (callable)

---

**This is ULTIMATE simplicity!** 🎯

