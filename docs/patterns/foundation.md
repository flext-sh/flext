# Foundation Patterns

**Version**: 1.0.0 | **Status**: Active | **Python**: 3.13+

## Overview

Core architectural patterns that form the base of the FLEXT ecosystem. These patterns provide fundamental building blocks that all other patterns extend.

## Model Patterns

### FlextModel

Universal base model for all FLEXT domain objects.

```python
from pydantic import BaseModel, ConfigDict

class FlextModel(BaseModel):
    """Base model with automatic validation and JSON serialization."""
    
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        use_enum_values=True,
        str_strip_whitespace=True
    )
    
    def validate_business_rules(self) -> 'FlextResult[None]':
        """Override to implement business rule validation."""
        from flext_core.result import FlextResult
        return FlextResult.ok(None)
```

### FlextEntity

Identity-based domain entity with lifecycle tracking.

```python
from datetime import datetime
from typing import Optional
import uuid

class FlextEntity(FlextModel):
    """Domain entity with unique identity and version control."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version: int = Field(default=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
    
    def increment_version(self) -> None:
        self.version += 1
        self.updated_at = datetime.utcnow()
```

### FlextValue

Immutable value object without identity.

```python
class FlextValue(FlextModel):
    """Immutable value object for domain concepts."""
    
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True
    )
    
    def with_updates(self, **kwargs) -> 'FlextValue':
        """Create new instance with updated values."""
        current_data = self.model_dump()
        current_data.update(kwargs)
        return self.__class__(**current_data)
```

### FlextConfig

Environment-aware configuration model.

```python
from pydantic import BaseSettings

class FlextConfig(BaseSettings):
    """Base configuration with environment variable support."""
    
    model_config = ConfigDict(
        env_prefix="FLEXT_",
        case_sensitive=False,
        validate_default=True,
        extra="forbid"
    )
    
    @classmethod
    def create_with_hierarchy(cls, **overrides) -> 'FlextResult[FlextConfig]':
        """Create config with hierarchical precedence."""
        from flext_core.config import FlextConfigHierarchical
        from flext_core.result import FlextResult
        
        try:
            hierarchy = FlextConfigHierarchical()
            config_data = hierarchy.merge_sources(**overrides)
            instance = cls(**config_data)
            return FlextResult.ok(instance)
        except Exception as e:
            return FlextResult.fail(f"Configuration error: {e}")
```

## Result Pattern

Type-safe operation results inspired by Rust's Result type.

```python
from typing import TypeVar, Generic, Optional, Callable
from dataclasses import dataclass

T = TypeVar('T')

@dataclass
class FlextResult(Generic[T]):
    """Type-safe result container for operations that can fail."""
    
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    error_context: Optional[dict] = None
    
    @classmethod
    def ok(cls, data: T) -> 'FlextResult[T]':
        """Create successful result."""
        return cls(success=True, data=data)
    
    @classmethod
    def fail(cls, error: str, error_code: Optional[str] = None, **context) -> 'FlextResult[T]':
        """Create failed result with context."""
        return cls(
            success=False,
            error=error,
            error_code=error_code,
            error_context=context if context else None
        )
    
    def map(self, func: Callable[[T], 'U']) -> 'FlextResult[U]':
        """Transform success value, propagate failure."""
        if self.success:
            try:
                return FlextResult.ok(func(self.data))
            except Exception as e:
                return FlextResult.fail(str(e))
        return FlextResult.fail(self.error, self.error_code, **(self.error_context or {}))
    
    def unwrap_or(self, default: T) -> T:
        """Get value or return default."""
        return self.data if self.success else default
```

## Factory Pattern

Semantic factory for creating domain objects.

```python
from typing import Type, Dict, Any, Callable

class FlextFactory:
    """Factory for creating and validating domain objects."""
    
    _creators: Dict[str, Callable] = {}
    
    @classmethod
    def register_creator(cls, entity_type: str, creator: Callable[..., FlextResult[Any]]) -> None:
        """Register a creator function for entity type."""
        cls._creators[entity_type] = creator
    
    @classmethod
    def create(cls, entity_type: str, **kwargs) -> FlextResult[Any]:
        """Create entity using registered creator."""
        if entity_type not in cls._creators:
            return FlextResult.fail(f"No creator registered for type: {entity_type}")
        
        try:
            return cls._creators[entity_type](**kwargs)
        except Exception as e:
            return FlextResult.fail(f"Creation failed: {str(e)}")
    
    @classmethod
    def create_entity(cls, entity_class: Type[FlextEntity], **kwargs) -> FlextResult[FlextEntity]:
        """Create and validate an entity."""
        try:
            entity = entity_class(**kwargs)
            validation_result = entity.validate_business_rules()
            
            if not validation_result.success:
                return FlextResult.fail(f"Validation failed: {validation_result.error}")
            
            return FlextResult.ok(entity)
        except Exception as e:
            return FlextResult.fail(f"Entity creation failed: {str(e)}")
```

## Protocol Patterns

Base protocol definitions for structural typing.

```python
from typing import Protocol, runtime_checkable, Any, Dict

@runtime_checkable
class FlextSerializable(Protocol):
    """Protocol for serializable objects."""
    
    def to_dict(self) -> Dict[str, Any]: ...
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FlextSerializable': ...

@runtime_checkable
class FlextValidatable(Protocol):
    """Protocol for validatable objects."""
    
    def validate(self) -> FlextResult[None]: ...
    def is_valid(self) -> bool: ...

@runtime_checkable
class FlextIdentifiable(Protocol):
    """Protocol for objects with identity."""
    
    @property
    def id(self) -> str: ...
    
    def equals(self, other: Any) -> bool: ...
```

## Usage Examples

### Creating Domain Models

```python
# Value Object
class Email(FlextValue):
    address: str
    verified: bool = False
    
    def validate_business_rules(self) -> FlextResult[None]:
        if "@" not in self.address:
            return FlextResult.fail("Invalid email format")
        return FlextResult.ok(None)

# Entity
class User(FlextEntity):
    username: str
    email: Email
    full_name: str
    roles: List[str] = Field(default_factory=list)
    
    def grant_role(self, role: str) -> FlextResult[None]:
        if role in self.roles:
            return FlextResult.fail(f"User already has role: {role}")
        
        self.roles.append(role)
        self.increment_version()
        return FlextResult.ok(None)

# Usage
def create_user(username: str, email: str, full_name: str) -> FlextResult[User]:
    email_obj = Email(address=email)
    return FlextFactory.create_entity(
        User,
        username=username,
        email=email_obj,
        full_name=full_name
    )
```

### Chaining Operations

```python
def get_user(user_id: str) -> FlextResult[User]:
    # Database fetch simulation
    ...

def update_email(user: User, new_email: str) -> FlextResult[User]:
    email_obj = Email(address=new_email)
    validation = email_obj.validate_business_rules()
    
    if not validation.success:
        return FlextResult.fail(f"Invalid email: {validation.error}")
    
    user.email = email_obj
    user.increment_version()
    return FlextResult.ok(user)

# Chain operations
result = (
    get_user("user123")
    .map(lambda user: update_email(user, "new@example.com"))
    .map(save_user)
)

if result.success:
    print("Email updated successfully")
else:
    print(f"Operation failed: {result.error}")
```

## Quality Standards

- **Type Safety**: All models must have complete type annotations
- **Validation**: Business rules validated in `validate_business_rules()`
- **Immutability**: Value objects must be frozen
- **Error Handling**: All operations return FlextResult
- **Documentation**: All classes need docstrings with examples

## Related Patterns

- [Type System](./types.md) - Extends foundation with semantic types
- [Error & Observability](./error-observability.md) - Uses FlextResult
- [Configuration](./config-cli.md) - Extends FlextConfig

---

**Foundation Patterns** - The bedrock of the FLEXT ecosystem, providing core architectural patterns that ensure consistency, type safety, and maintainability across all projects.
