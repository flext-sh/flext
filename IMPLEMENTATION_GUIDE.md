# 🛠️ PyAuto Standards Implementation Guide
## Practical Steps for Enterprise-Grade Python Project

**Version**: 1.0  
**Date**: 2025-01-06  
**Scope**: Complete standardization of PyAuto workspace

---

## 🎯 EXECUTIVE SUMMARY

This guide provides **concrete, actionable steps** to transform PyAuto into an enterprise-grade Python project following:
- **Python 3.11+** best practices
- **PEP 8** naming conventions  
- **Hexagonal Architecture** patterns
- **Domain-Driven Design** principles
- **SOLID, KISS, DRY** principles
- **Type Safety** with Pydantic

---

## 📋 STANDARDIZATION CHECKLIST

### **1. PROJECT STRUCTURE** ✅

```
pyauto/
├── flx/                           # Core framework
│   ├── pyproject.toml            # Poetry/pip configuration
│   ├── README.md                 # Professional documentation
│   ├── src/
│   │   └── flx/                  # Package root
│   │       ├── __init__.py       # Package exports
│   │       ├── core/             # Domain layer
│   │       ├── application/      # Use cases
│   │       ├── ports/            # Interfaces
│   │       ├── adapters/         # Implementations
│   │       └── infra/            # Infrastructure
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   └── examples/                 # Working examples
│
├── flx_database_oracle/          # Plugin (underscore!)
│   ├── pyproject.toml
│   ├── README.md
│   ├── src/
│   │   └── flx_database_oracle/
│   └── tests/
│
└── gruponos_oic_wms/            # Implementation project
    ├── pyproject.toml
    ├── README.md
    └── src/
```

### **2. NAMING CONVENTIONS** ✅

#### **Python Package Names**
```python
✅ CORRECT:
flx
flx_core
flx_database_oracle
flx_http_oracle_oic
gruponos_oic_wms
algar_oud_migration

❌ WRONG:
flx-core            # Hyphens break imports!
flxCore             # CamelCase packages
FLX_CORE           # UPPERCASE packages
```

#### **Module Names**
```python
✅ CORRECT:
entities.py
value_objects.py
database_adapter.py
http_client.py

❌ WRONG:
Entities.py         # Capitalized
valueObjects.py     # camelCase
database-adapter.py # Hyphens
```

#### **Class Names**
```python
✅ CORRECT:
class OrderAggregate:
class DatabaseAdapter:
class HTTPClient:
class OICConnector:

❌ WRONG:
class order_aggregate:    # snake_case
class databaseAdapter:    # camelCase
class Http_Client:        # Mixed
```

### **3. DOCUMENTATION INTEGRATION** ✅

#### **Remove /docs/ Directory**
```bash
# Step 1: Backup existing docs
cp -r docs/ docs_backup_$(date +%Y%m%d)/

# Step 2: Integrate into code
# For each documentation file:
# - API docs → Module docstrings
# - Guides → Module README.md
# - Examples → examples/ directory
```

#### **Module Documentation Structure**
```
src/flx/core/
├── __init__.py          # Module exports + overview docstring
├── README.md            # Detailed documentation
├── entities.py          # With comprehensive docstrings
├── value_objects.py     # With comprehensive docstrings
└── examples/            # Working examples
    ├── __init__.py
    ├── basic_entity.py
    └── complex_aggregate.py
```

### **4. DOCSTRING STANDARDS** ✅

#### **Module Docstring**
```python
"""Core domain entities for FLX framework.

This module implements the domain layer of hexagonal architecture,
providing base classes for entities, aggregates, and value objects
following Domain-Driven Design principles.

Architecture:
    Layer: Domain (innermost)
    Dependencies: None (pure business logic)
    Patterns: Entity, Aggregate Root, Value Object

Example:
    from flx.core import Entity, AggregateRoot
    
    class Order(AggregateRoot):
        def __init__(self, customer_id: str):
            super().__init__()
            self.customer_id = customer_id

Note:
    This module has no external dependencies and contains
    only pure business logic and domain rules.
"""
```

#### **Class Docstring**
```python
class Entity(ABC, Generic[T]):
    """Base class for domain entities with identity.
    
    An entity is defined by its identity rather than its attributes.
    Two entities with the same ID are considered the same entity
    regardless of their other attributes.
    
    Attributes:
        id: Unique identifier for the entity
        version: Optimistic locking version
        created_at: Creation timestamp
        updated_at: Last modification timestamp
    
    Example:
        class Customer(Entity[UUID]):
            def __init__(self, customer_id: UUID, name: str):
                super().__init__(customer_id)
                self.name = name
    
    Note:
        Entities should contain business logic and enforce
        invariants, not just be data containers.
    """
```

#### **Method Docstring**
```python
def add_item(
    self,
    product_id: UUID,
    quantity: int,
    unit_price: Decimal
) -> None:
    """Add an item to the order with validation.
    
    Args:
        product_id: Unique product identifier
        quantity: Number of units (must be positive)
        unit_price: Price per unit (must be positive)
    
    Raises:
        ValueError: If quantity <= 0 or unit_price <= 0
        DomainError: If order is already confirmed
        
    Example:
        order.add_item(
            product_id=UUID("..."),
            quantity=2,
            unit_price=Decimal("9.99")
        )
    """
```

### **5. TYPE HINTS** ✅

#### **Complete Type Annotations**
```python
from typing import Optional, List, Dict, TypeVar, Generic
from datetime import datetime
from decimal import Decimal
from uuid import UUID

T = TypeVar("T")

class Repository(ABC, Generic[T]):
    """Base repository with full type hints."""
    
    @abstractmethod
    async def get(self, entity_id: UUID) -> Optional[T]:
        """Retrieve entity by ID."""
        ...
    
    @abstractmethod
    async def save(self, entity: T) -> T:
        """Persist entity."""
        ...
    
    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        """Remove entity."""
        ...
```

### **6. PYDANTIC MODELS** ✅

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal
from uuid import UUID

class OrderCreateRequest(BaseModel):
    """Order creation request with validation."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )
    
    customer_id: UUID = Field(description="Customer placing order")
    items: List[OrderItemRequest] = Field(
        min_length=1,
        description="Order must have at least one item"
    )
    shipping_address: Address
    billing_address: Optional[Address] = None
    
    @field_validator("items")
    def validate_unique_products(cls, items: List[OrderItemRequest]) -> List[OrderItemRequest]:
        """Ensure no duplicate products."""
        product_ids = [item.product_id for item in items]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError("Duplicate products not allowed")
        return items
```

### **7. TESTING STRUCTURE** ✅

```python
# tests/unit/core/test_entities.py
import pytest
from uuid import uuid4
from flx.core import Entity, DomainError

class TestEntity:
    """Test domain entity behavior."""
    
    def test_entity_equality_based_on_id(self):
        """Entities with same ID are equal."""
        entity_id = uuid4()
        entity1 = TestableEntity(entity_id, "Name 1")
        entity2 = TestableEntity(entity_id, "Name 2")
        
        assert entity1 == entity2
        assert entity1.name != entity2.name
    
    def test_entity_inequality_different_ids(self):
        """Entities with different IDs are not equal."""
        entity1 = TestableEntity(uuid4(), "Name")
        entity2 = TestableEntity(uuid4(), "Name")
        
        assert entity1 != entity2
        assert entity1.name == entity2.name
```

### **8. CONFIGURATION** ✅

```python
# src/flx/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings with validation."""
    
    # Application
    app_name: str = "FLX Framework"
    debug: bool = False
    environment: str = Field(
        default="development",
        pattern="^(development|staging|production)$"
    )
    
    # Database
    database_url: str = Field(
        default="postgresql://localhost/flx",
        description="PostgreSQL connection string"
    )
    database_pool_size: int = Field(default=20, ge=1, le=100)
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = Field(default=8000, ge=1, le=65535)
    api_prefix: str = "/api/v1"
    
    # Security
    secret_key: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 30
    
    class Config:
        env_file = ".env"
        env_prefix = "FLX_"
```

### **9. HEXAGONAL ARCHITECTURE** ✅

#### **Port Definition**
```python
# src/flx/ports/outbound/repository.py
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

class OrderRepository(ABC):
    """Port for order persistence."""
    
    @abstractmethod
    async def get(self, order_id: UUID) -> Optional[Order]:
        """Retrieve order by ID."""
        ...
    
    @abstractmethod
    async def save(self, order: Order) -> Order:
        """Persist order."""
        ...
    
    @abstractmethod
    async def find_by_customer(
        self,
        customer_id: UUID,
        limit: int = 10,
        offset: int = 0
    ) -> List[Order]:
        """Find orders for customer."""
        ...
```

#### **Adapter Implementation**
```python
# src/flx/adapters/outbound/postgres_repository.py
from flx.ports.outbound import OrderRepository
from flx.core import Order
from typing import Optional, List
from uuid import UUID
import asyncpg

class PostgresOrderRepository(OrderRepository):
    """PostgreSQL implementation of order repository."""
    
    def __init__(self, connection_pool: asyncpg.Pool):
        self._pool = connection_pool
    
    async def get(self, order_id: UUID) -> Optional[Order]:
        """Retrieve order from PostgreSQL."""
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM orders WHERE id = $1",
                order_id
            )
            return self._to_domain(row) if row else None
    
    async def save(self, order: Order) -> Order:
        """Persist order to PostgreSQL."""
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO orders (id, customer_id, status, total)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (id) DO UPDATE SET
                    status = EXCLUDED.status,
                    total = EXCLUDED.total,
                    updated_at = NOW()
                """,
                order.id,
                order.customer_id,
                order.status.value,
                str(order.total.amount)
            )
            return order
```

### **10. QUALITY ENFORCEMENT** ✅

#### **pyproject.toml Configuration**
```toml
[tool.poetry]
name = "flx"
version = "0.4.0"
description = "Enterprise Python framework with hexagonal architecture"
authors = ["Your Team <team@example.com>"]
python = "^3.11"

[tool.poetry.dependencies]
python = "^3.11"
pydantic = "^2.0"
fastapi = "^0.104.0"
sqlalchemy = "^2.0"
asyncpg = "^0.29.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4"
pytest-asyncio = "^0.21"
pytest-cov = "^4.1"
mypy = "^1.7"
black = "^23.11"
ruff = "^0.1.6"
pre-commit = "^3.5"

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true

[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'

[tool.ruff]
target-version = "py311"
line-length = 88
select = [
    "E",   # pycodestyle
    "F",   # pyflakes
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "SIM", # flake8-simplify
    "I",   # isort
]

[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers"
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
```

#### **Pre-commit Configuration**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-toml
      - id: check-docstring-first
      
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3.11
        
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
        
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        language_version: python3.11
```

---

## 🚀 IMPLEMENTATION STEPS

### **Week 1: Foundation**
1. Fix all project names (remove hyphens)
2. Set up pyproject.toml for each project
3. Configure pre-commit hooks
4. Add basic type hints

### **Week 2: Documentation**
1. Create README.md for each module
2. Add comprehensive docstrings
3. Move /docs/ content to code
4. Create examples/ directories

### **Week 3: Architecture**
1. Define all ports
2. Implement adapters
3. Fix layer violations
4. Add dependency injection

### **Week 4: Quality**
1. Achieve 100% type coverage
2. Pass all linting checks
3. Set up CI/CD pipeline
4. Document security aspects

---

## 📊 VALIDATION

Run these commands to validate compliance:

```bash
# Check naming conventions
find . -name "*-*" -type d  # Should return nothing

# Check type coverage
mypy src/ --strict

# Check code quality
black --check src/
ruff src/

# Run tests
pytest --cov=src --cov-report=html

# Check documentation
python -m pydoc -b  # Browse documentation
```

---

This guide provides a complete roadmap to transform PyAuto into an enterprise-grade Python project. Follow these standards consistently for maintainable, scalable, and professional code.