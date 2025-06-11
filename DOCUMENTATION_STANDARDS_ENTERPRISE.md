# 🏗️ PyAuto Enterprise Documentation Standards
## Arquitetura Hexagonal + DDD + Clean Code + Python 3.11+

**Version**: 3.0 - Enterprise Grade  
**Created**: 2025-01-06  
**Standards**: Python 3.11+ | PEPs | SOLID | KISS | DRY | PYDANTIC | HEXAGONAL | DDD  
**GitHub Org**: https://github.com/datacosmos-br/

---

## 🚨 CRITICAL ANALYSIS OF CURRENT STATE

### **Major Issues Identified**

1. **Inconsistent Naming Conventions**
   - Mixed usage of `flx-database-oracle` vs `flx_database_oracle`
   - Inconsistent capitalization in documentation headers
   - No clear naming hierarchy (core → plugins → implementations)

2. **Structural Problems**
   - Documentation scattered across `/docs/` instead of integrated with code
   - No clear separation between API docs, guides, and examples
   - Missing standardized module structure

3. **Pattern Violations**
   - Not following Python package naming conventions (PEP 8)
   - Inconsistent use of type hints and Pydantic models
   - Mixed architectural patterns without clear boundaries

4. **Quality Issues**
   - Excessive use of emojis and decorative elements
   - Inconsistent formatting and structure
   - Missing critical technical depth in some areas

---

## 📐 ENTERPRISE STANDARDS

### **1. NAMING CONVENTIONS (STRICT COMPLIANCE)**

#### **Project Naming**
```
✅ CORRECT:
flx                     # Core framework (lowercase, short)
flx_database_oracle     # Plugin (underscore separator)
flx_http_oracle_oic     # Multi-word plugin
gruponos_oic_wms        # Implementation project
algar_oud_migration     # Migration project

❌ INCORRECT:
flx-database-oracle     # Hyphen in Python packages
FLX_Core               # Mixed case
flxDatabaseOracle      # CamelCase packages
```

#### **Module & Package Naming**
```python
✅ CORRECT:
src/flx/core/entities.py
src/flx/adapters/outbound/database.py
src/flx_database_oracle/adapter.py
tests/unit/test_entities.py
tests/integration/test_database_adapter.py

❌ INCORRECT:
src/flx/Core/Entities.py          # Capitalized modules
src/flx/adapters/DatabaseAdapter.py  # CamelCase files
tests/test-entities.py            # Hyphens in filenames
```

#### **Class Naming (PEP 8)**
```python
✅ CORRECT:
class DatabaseAdapter:
class OrderAggregate:
class ValueObject:
class HTTPClientPort:

❌ INCORRECT:
class database_adapter:    # snake_case classes
class DB_Adapter:         # Underscore in class names
class databaseAdapter:    # camelCase classes
```

#### **Function & Method Naming**
```python
✅ CORRECT:
def execute_query(self, query: str) -> QueryResult:
def calculate_order_total(self) -> Money:
async def connect_to_database(self) -> None:

❌ INCORRECT:
def ExecuteQuery():       # PascalCase
def execute_Query():      # Mixed case
def executequery():       # No separation
```

### **2. DOCUMENTATION STRUCTURE (CODE-FIRST)**

#### **Project Structure**
```
{project}/
├── README.md                    # Project overview + navigation
├── src/
│   └── {package}/
│       ├── __init__.py         # Package exports + docstring
│       ├── README.md           # Module documentation
│       ├── core/               # Domain layer
│       │   ├── __init__.py
│       │   ├── README.md       # Domain documentation
│       │   └── entities.py     # With comprehensive docstrings
│       ├── adapters/           # Infrastructure adapters
│       │   ├── README.md
│       │   └── database.py
│       ├── ports/              # Interface definitions
│       │   ├── README.md
│       │   └── repository.py
│       └── examples/           # Working examples
│           ├── README.md
│           └── basic_usage.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── docs/                       # REMOVE - integrate into code
```

### **3. DOCSTRING STANDARDS (GOOGLE STYLE + ENHANCEMENTS)**

#### **Module Docstring Template**
```python
"""Module name and primary purpose.

This module implements {specific functionality} as part of the {layer}
layer in the hexagonal architecture. It provides {key capabilities}.

Architecture:
    Layer: {Domain|Application|Infrastructure|Port|Adapter}
    Pattern: {DDD Entity|Value Object|Repository|Service|etc}
    Dependencies: {Inbound|Outbound|None}

Domain Context:
    {Business domain explanation and rules}

Integration:
    - Inbound: {What calls this module}
    - Outbound: {What this module calls}
    - Events: {Domain events produced/consumed}

Example:
    Basic usage example:
    ```python
    from flx.core import Entity
    
    entity = Entity(id="123")
    entity.process_business_logic()
    ```

Security:
    {Authentication/Authorization requirements}
    {Data validation rules}
    {Access control patterns}

Performance:
    {Caching strategies}
    {Query optimization notes}
    {Scaling considerations}

See Also:
    - :mod:`flx.ports.repository`: Repository interface
    - :mod:`flx.adapters.database`: Database implementation
    - :doc:`/examples/domain_modeling`: Complete examples
"""
```

#### **Class Docstring Template**
```python
class OrderAggregate(AggregateRoot):
    """Order aggregate root managing order lifecycle and invariants.
    
    This aggregate ensures order consistency and enforces business rules
    for order processing within the e-commerce domain.
    
    Business Rules:
        - Orders cannot be modified after confirmation
        - Minimum order value must be respected
        - Inventory must be available for all items
    
    Attributes:
        order_id (OrderId): Unique order identifier
        customer_id (CustomerId): Reference to customer aggregate
        items (List[OrderItem]): Order line items
        status (OrderStatus): Current order state
        total (Money): Calculated order total
    
    Domain Events:
        - OrderCreated: When new order is initialized
        - OrderItemAdded: When item added to order
        - OrderConfirmed: When order is confirmed
        - OrderShipped: When order ships
    
    Invariants:
        - Total must equal sum of item prices
        - Cannot have duplicate items
        - Must have at least one item to confirm
    
    Example:
        Creating and processing an order:
        ```python
        order = OrderAggregate(customer_id=customer_id)
        order.add_item(product_id, quantity=2, price=Money(10.00))
        order.apply_discount(DiscountCode("SAVE10"))
        order.confirm()
        
        events = order.collect_events()
        ```
    
    Raises:
        DomainError: When business rules are violated
        InvalidStateError: When operation invalid for current state
    """
```

#### **Method Docstring Template**
```python
def process_payment(
    self,
    payment_method: PaymentMethod,
    amount: Money,
    *,
    idempotency_key: str,
) -> PaymentResult:
    """Process payment for the order using specified payment method.
    
    This method orchestrates the payment process, ensuring idempotency
    and proper error handling. It integrates with the payment gateway
    through the PaymentPort.
    
    Args:
        payment_method: Payment method containing card/account details
        amount: Amount to charge (must match order total)
        idempotency_key: Unique key for idempotent processing
    
    Returns:
        PaymentResult containing:
            - transaction_id: Payment gateway transaction ID
            - status: Success/Failed/Pending
            - timestamp: Processing timestamp
            - receipt_url: Optional receipt URL
    
    Raises:
        PaymentError: Payment processing failed
        InvalidAmountError: Amount doesn't match order total
        InvalidStateError: Order not in payable state
        
    Side Effects:
        - Updates order payment status
        - Emits PaymentProcessed event
        - May trigger inventory reservation
    
    Example:
        ```python
        result = order.process_payment(
            payment_method=CreditCard(number="****1234"),
            amount=order.total,
            idempotency_key=str(uuid4())
        )
        if result.status == PaymentStatus.SUCCESS:
            await event_bus.publish(order.collect_events())
        ```
    
    Note:
        This method is idempotent when called with same idempotency_key.
        Concurrent calls with same key will return cached result.
    """
```

### **4. HEXAGONAL ARCHITECTURE DOCUMENTATION**

#### **Layer Documentation Requirements**

**Domain Layer** (`/core/`)
- Pure business logic documentation
- No infrastructure references
- Business rules and invariants
- Domain event descriptions

**Application Layer** (`/application/`)
- Use case documentation
- Service orchestration patterns
- Transaction boundaries
- CQRS command/query handlers

**Infrastructure Layer** (`/infra/`)
- Technical implementation details
- Configuration examples
- Performance tuning notes
- Deployment considerations

**Ports** (`/ports/`)
- Interface contracts
- Protocol specifications
- Integration requirements
- Testing strategies

**Adapters** (`/adapters/`)
- Implementation specifics
- Configuration schemas
- Error handling patterns
- Performance characteristics

### **5. TYPE HINTS AND PYDANTIC (STRICT)**

#### **Type Hint Requirements**
```python
from typing import Optional, List, Dict, Union, TypeVar, Generic
from datetime import datetime
from decimal import Decimal
from uuid import UUID

T = TypeVar("T", bound="Entity")

class Entity(Generic[T]):
    """Base entity with proper type hints."""
    
    def __init__(self, entity_id: UUID) -> None:
        self._id: UUID = entity_id
        self._created_at: datetime = datetime.utcnow()
        self._version: int = 0
    
    @property
    def id(self) -> UUID:
        return self._id
    
    def equals(self, other: Optional[T]) -> bool:
        if other is None:
            return False
        return self._id == other._id
```

#### **Pydantic Model Standards**
```python
from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class OrderItemModel(BaseModel):
    """Order item with comprehensive validation."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        validate_default=True,
        extra="forbid",
        frozen=True,  # Immutable by default
    )
    
    product_id: UUID = Field(description="Product reference")
    quantity: int = Field(gt=0, le=1000, description="Order quantity")
    unit_price: Decimal = Field(
        gt=0,
        decimal_places=2,
        description="Price per unit"
    )
    discount_percent: Optional[Decimal] = Field(
        default=None,
        ge=0,
        le=100,
        description="Discount percentage"
    )
    
    @validator("unit_price")
    def validate_price(cls, v: Decimal) -> Decimal:
        """Ensure price has exactly 2 decimal places."""
        return v.quantize(Decimal("0.01"))
    
    @property
    def line_total(self) -> Decimal:
        """Calculate line total with discount."""
        subtotal = self.quantity * self.unit_price
        if self.discount_percent:
            discount = subtotal * (self.discount_percent / 100)
            return subtotal - discount
        return subtotal
```

### **6. README.md TEMPLATE (PROFESSIONAL)**

```markdown
# {Project Name}

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Architecture](https://img.shields.io/badge/architecture-hexagonal-green.svg)
![Status](https://img.shields.io/badge/status-{status}-{color}.svg)

**{One-line description focusing on business value}**

## Overview

{2-3 paragraphs explaining:
- What problem this solves
- Key architectural decisions
- Main components and their relationships}

## Quick Start

```bash
# Installation
pip install {package_name}

# Basic usage
python -m {package_name} --help
```

```python
# Code example
from {package_name} import {MainClass}

instance = {MainClass}(config)
result = instance.execute()
```

## Architecture

{ASCII or mermaid diagram showing hexagonal architecture}

### Components

- **Domain Layer** (`/core/`): {Business logic description}
- **Application Layer** (`/application/`): {Use cases description}
- **Infrastructure** (`/infra/`): {Technical implementations}
- **Ports** (`/ports/`): {Interface definitions}
- **Adapters** (`/adapters/`): {Implementation details}

## Installation

### Requirements

- Python 3.11+
- {Other requirements}

### Development Setup

```bash
# Clone repository
git clone https://github.com/datacosmos-br/pyauto
cd pyauto/{project}

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## Usage

### Configuration

```python
# config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str
    api_key: str
    
    class Config:
        env_file = ".env"
```

### API Examples

{Comprehensive examples for main use cases}

## Testing

```bash
# Unit tests
pytest tests/unit

# Integration tests
pytest tests/integration

# Coverage report
pytest --cov={package_name} --cov-report=html
```

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## License

{License information}
```

### **7. QUALITY GATES AND STANDARDS**

#### **Code Quality Requirements**
- **Type Coverage**: 100% type hints for public APIs
- **Test Coverage**: Minimum 80% with critical paths at 100%
- **Documentation Coverage**: 100% for public modules, classes, methods
- **Complexity**: Cyclomatic complexity < 10
- **Duplication**: < 3% code duplication

#### **Documentation Quality Gates**
- All public APIs have comprehensive docstrings
- Examples are executable and tested
- Type hints match documentation
- Security considerations documented
- Performance implications noted

#### **Architecture Compliance**
- Clear layer separation (no domain → infrastructure imports)
- Dependency injection used consistently
- Ports and adapters properly defined
- Domain events for state changes
- CQRS for complex operations

### **8. ANTI-PATTERNS TO AVOID**

#### **Documentation Anti-Patterns**
```
❌ AVOID:
- Excessive emojis and decorative elements
- Generic descriptions ("This class does X")
- Missing examples
- Outdated information
- TODO comments in production

✅ PREFER:
- Clear, professional language
- Specific, actionable descriptions
- Working, tested examples
- Current, validated information
- Completed documentation
```

#### **Code Anti-Patterns**
```python
❌ AVOID:
# Anemic domain models
class Order:
    def __init__(self):
        self.id = None
        self.items = []
        self.total = 0

# Infrastructure in domain
class Customer(Entity):
    def save(self):
        database.save(self)  # NO!

# Missing type hints
def process(data):
    return data["value"] * 2

✅ PREFER:
# Rich domain models
class Order(AggregateRoot):
    def add_item(self, item: OrderItem) -> None:
        self._enforce_business_rules(item)
        self._items.append(item)
        self._recalculate_total()
        self.emit_event(ItemAdded(self.id, item))

# Clean architecture
class Customer(Entity):
    def change_email(self, email: Email) -> None:
        self._email = email
        self.emit_event(EmailChanged(self.id, email))

# Complete type hints
def process(data: Dict[str, float]) -> float:
    return data["value"] * 2
```

### **9. MIGRATION PATH**

#### **Phase 1: Naming Standardization**
1. Rename all projects to follow Python conventions
2. Update import statements
3. Fix module and file names
4. Update documentation references

#### **Phase 2: Documentation Integration**
1. Move `/docs/` content to code directories
2. Add comprehensive docstrings
3. Create module-level README.md files
4. Add working examples

#### **Phase 3: Architecture Alignment**
1. Enforce layer separation
2. Define clear ports and adapters
3. Implement proper dependency injection
4. Add domain events

#### **Phase 4: Quality Enhancement**
1. Add type hints everywhere
2. Implement Pydantic models
3. Increase test coverage
4. Add security documentation

### **10. TOOLING AND AUTOMATION**

#### **Pre-commit Hooks**
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-docstring-first
      
  - repo: https://github.com/psf/black
    hooks:
      - id: black
        language_version: python3.11
        
  - repo: https://github.com/pycqa/isort
    hooks:
      - id: isort
        
  - repo: https://github.com/pycqa/flake8
    hooks:
      - id: flake8
        additional_dependencies: [
          flake8-docstrings,
          flake8-type-checking,
          flake8-annotations
        ]
        
  - repo: https://github.com/pre-commit/mirrors-mypy
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

#### **Documentation Generation**
```bash
# Generate API documentation
sphinx-apidoc -o docs/api src/

# Check documentation coverage
docstr-coverage src/ --min-coverage=95

# Validate examples
python -m doctest src/**/*.py
```

---

## SUCCESS CRITERIA

1. **Consistent Naming**: All projects, modules, and code follow Python conventions
2. **Integrated Documentation**: All docs live with code, no separate `/docs/`
3. **Type Safety**: 100% type coverage with mypy strict mode
4. **Architecture Purity**: Clean hexagonal architecture with no violations
5. **Quality Standards**: All quality gates passing in CI/CD

---

This enterprise-grade standard ensures professional, maintainable, and scalable Python projects following the best practices of hexagonal architecture, DDD, and clean code principles.