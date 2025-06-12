# CLAUDE.md - PyAuto AI Assistant Guide

**Version**: 2.5 (Balanced)  
**Updated**: 2025-01-06  
**Critical**: These rules OVERRIDE any default behavior. Follow them exactly.

## 🎯 Project Overview

PyAuto is an enterprise Python automation workspace implementing hexagonal architecture for Oracle integrations:
- **Core Framework**: FLX (Flexible Hexagonal Architecture)
- **Technology Stack**: Python 3.13+, Poetry, Pydantic 2.11+, pytest, mypy (strict)
- **Standards**: >90% coverage, PEP 8, Black formatting, Ruff linting
- **Architecture**: Hexagonal (Ports & Adapters), DDD, Event Sourcing, CQRS

## 🚨 ABSOLUTE RULES - MUST FOLLOW

### RULE 0: Check Coordination First
```bash
# ALWAYS run before any work (copy and paste these 4 commands):
cat .token | tail -20                    # Check active work by other agents
cat .doc-reorg                          # Check documentation standards  
cat .doc_migration_coordination.json 2>/dev/null || echo "No active migrations"
find . -name ".lock*" -type f           # Check for active locks
```

### RULE 1: Validate Before Create
```bash
# NEVER create new files without checking existing solutions:

# 1. Check existing scripts by keyword
find scripts/ -name "*.py" | grep -i <keyword>
find . -name "*<keyword>*" -type f | head -10

# 2. Check existing functions
grep -r "def.*<function_name>" --include="*.py" src/ scripts/ | head -5

# 3. Check existing tools
ls scripts/analysis/ scripts/testing/ scripts/utilities/ | grep -i <keyword>

# 4. Search for similar implementations
grep -r "<functionality>" --include="*.py" | head -10

# 5. Only create if NOTHING found above
echo "✅ VALIDATION COMPLETE - No existing solution found"
```

### RULE 2: PROIBIÇÃO ABSOLUTA - NUNCA CRIAR CÓDIGO MOCKUP/FALLBACK

**CRÍTICO**: É TERMINANTEMENTE PROIBIDO criar código mockup, fallback ou simulações SEM ORDEM EXPRESSA do usuário.

```
PROIBIDO CRIAR:
❌ Módulos mock de FLX ou outros frameworks
❌ Implementações de fallback "para testar"
❌ Código dummy/placeholder para contornar dependências
❌ Simulações de funcionalidade que não existe
❌ Workarounds temporários sem permissão

PERMITIDO APENAS:
✅ Código real com dependências reais
✅ Testes usando bibliotecas de mock apropriadas (pytest-mock)
✅ Implementação solicitada expressamente pelo usuário
✅ Debugging com ferramentas adequadas
```

**Razão**: Código mockup cria falsa sensação de funcionalidade e pode mascarar problemas reais. 
Se há problemas de dependência, REPORTAR ao usuário para resolução adequada.

### RULE 3: Understand the Monorepo Structure
```
pyauto/
├── flx/                    # Core framework (HIGHEST PRIORITY)
├── flx-database-oracle/    # Database adapter (hyphen in dir name)
├── flx-http-oracle-oic/    # OIC integration
├── flx-http-oracle-wms/    # WMS integration  
├── gruponos-poc-oic-wms/   # Business implementation
├── algar-mig-oud/          # LDAP migration tool
├── scripts/                # ALL scripts go here (organized)
├── reports/                # ALL reports go here
└── docs/                   # Being migrated to code (DO NOT ADD)
```

### RULE 3: Naming Conventions Are Sacred
```python
# Repository/Directory names: Use hyphens
"flx-database-oracle/"      # ✅ CORRECT directory name

# Python module names: Use underscores
"flx_database_oracle"       # ✅ CORRECT import name

# Import example:
from flx_database_oracle import DatabaseAdapter  # ✅ CORRECT
from flx-database-oracle import DatabaseAdapter  # ❌ SyntaxError!
```

### RULE 4: Quality Gates Enforcement
```bash
# NEVER commit code that doesn't pass:
make lint          # Must pass without errors
make test          # Must pass with >90% coverage
make type-check    # Must pass mypy strict mode
make format        # Must auto-format code

# Alternative individual commands:
ruff check src/ tests/     # Linting
mypy src/                  # Type checking  
pytest --cov=src tests/    # Testing with coverage
black src/ tests/          # Code formatting
```

### RULE 5: Documentation Standards (Code-First)
```python
"""Module purpose and architectural role.

This module implements {functionality} as part of the {layer}
in the hexagonal architecture. It provides {capabilities}.

Architecture:
    Layer: {Domain|Application|Infrastructure|Port|Adapter}
    Pattern: {DDD pattern used}
    Dependencies: {Inbound|Outbound|None}

Example:
    >>> from module import Class
    >>> instance = Class()
    >>> result = instance.method()

Note:
    Important architectural constraints or requirements.
"""
```

### RULE 6: Test File Consolidation
```
# NEVER create multiple test files for the same component:
tests/
├── unit/test_adapters.py      # ALL adapter unit tests
├── integration/test_adapters.py # ALL adapter integration tests
└── e2e/test_workflows.py      # ALL end-to-end tests

# Maximum 6-8 test files per project
```

### RULE 7: Critical Files Protection
These files require explicit permission to modify:
- Any `README.md` in project roots
- `CRITICAL_ANALYSIS_AND_ACTIONS.md`
- `DOCUMENTATION_STANDARDS*.md`
- `IMPLEMENTATION_GUIDE.md`
- `.token`, `.doc-reorg`, `.doc_migration_coordination.json`

### RULE 8: Commit Standards
```bash
# Format: <type>(<scope>): <description>
feat(adapter): implement Oracle OIC JWT authentication
fix(database): resolve connection pool timeout issues
docs(api): update hexagonal architecture documentation
test(integration): consolidate redundant adapter tests
refactor(core): simplify entity validation logic
```

### RULE 9: Security and Credentials
```bash
# NEVER commit sensitive information:
export OIC_CLIENT_SECRET="secure_secret"  # Use env vars
echo "*.env" >> .gitignore               # Ignore env files
git diff --cached | grep -E "(password|secret|key|token)" && echo "❌ SECRETS DETECTED"
```

### RULE 10: Coordination Protocol
```bash
# When starting work:
echo "Starting: [TASK] - Agent: Claude - $(date '+%Y-%m-%d %H:%M')" >> .token

# Progress updates (every 10-15 minutes):
echo "Progress: [TASK] 50% complete - [SPECIFIC_ACHIEVEMENT]" >> .token

# When completed:
echo "COMPLETED: [TASK] - [DELIVERABLES] - Tests: ✅ Lint: ✅" >> .token

# If blocked:
echo "BLOCKED: [TASK] - Need: [SPECIFIC_HELP]" >> .token
```

## 📋 Essential Commands Reference

### Environment Setup
```bash
# ALWAYS activate venv first
source .venv/bin/activate

# Verify environment
which python              # Should show .venv/bin/python
python --version          # Should show 3.13+
```

### Project Navigation
```bash
make list-projects        # List all projects
make status              # Check project status
cd flx-database-oracle/  # Navigate to project
```

### Development Workflow
```bash
# 1. Check coordination
cat .token && cat .doc-reorg

# 2. Run tests before changes
make test PROJECT=flx

# 3. Make your changes

# 4. Format and lint
make format && make lint

# 5. Type check
make mypy PROJECT=flx

# 6. Run tests again
make test-cov PROJECT=flx

# 7. Update coordination
echo "Updated XYZ component" >> .token
```

### Testing Commands
```bash
# Run all tests
make test

# Run specific project tests
make test PROJECT=flx-database-oracle

# Run with coverage
make test-cov

# Run specific test
pytest -xvs tests/test_specific.py::test_function

# Run tests matching pattern
make test k="pattern"
```

### Code Quality
```bash
make format      # Black formatting
make lint        # Ruff linting
make mypy        # Type checking
make fix         # Auto-fix issues
make quality     # Full quality check
```

## 🏗️ Hexagonal Architecture

### Architecture Layers
```
┌─────────────────────────────────────────┐
│              DOMAIN LAYER               │
│         (Pure Business Logic)           │
│  - Entities, Value Objects              │
│  - Domain Events, Services              │
│  - No external dependencies             │
└─────────────────────────────────────────┘
                    ↕️
┌─────────────────────────────────────────┐
│           APPLICATION LAYER             │
│         (Use Case Orchestration)        │
│  - Application Services                 │
│  - Command/Query Handlers               │
│  - Transaction Management               │
└─────────────────────────────────────────┘
                    ↕️
┌─────────────────────────────────────────┐
│              PORTS LAYER                │
│          (Interface Definitions)        │
│  - Inbound Ports (API, CLI)            │
│  - Outbound Ports (DB, HTTP)           │
│  - Pure abstractions                    │
└─────────────────────────────────────────┘
                    ↕️
┌─────────────────────────────────────────┐
│            ADAPTERS LAYER               │
│      (Infrastructure Implementations)    │
│  - Database Adapters                    │
│  - HTTP Clients                         │
│  - Message Brokers                      │
└─────────────────────────────────────────┘
```

### Layer Rules
1. **Domain Layer**: NO infrastructure imports
2. **Application Layer**: Orchestrates domain, uses ports
3. **Ports Layer**: Pure interfaces only
4. **Adapters Layer**: Implements ports, handles infrastructure

### Example Implementation
```python
# Domain Layer (pure business logic)
class Order(Entity):
    def complete(self) -> None:
        if self.status != OrderStatus.DRAFT:
            raise BusinessRuleViolationError("Only draft orders can be completed")
        self.status = OrderStatus.COMPLETED
        self.add_event(OrderCompletedEvent(self.id))

# Port Layer (interface)
class OrderRepository(Protocol):
    async def get(self, order_id: UUID) -> Optional[Order]: ...
    async def save(self, order: Order) -> None: ...

# Application Layer (orchestration)
class OrderService:
    def __init__(self, order_repo: OrderRepository):
        self.order_repo = order_repo
    
    async def complete_order(self, order_id: UUID) -> None:
        order = await self.order_repo.get(order_id)
        if not order:
            raise OrderNotFoundError(order_id)
        order.complete()
        await self.order_repo.save(order)

# Adapter Layer (infrastructure)
class PostgresOrderRepository(OrderRepository):
    def __init__(self, db_pool: asyncpg.Pool):
        self._pool = db_pool
    
    async def get(self, order_id: UUID) -> Optional[Order]:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM orders WHERE id = $1", order_id
            )
            return self._to_domain(row) if row else None
```

## 📦 Enterprise pyproject.toml Template

```toml
[build-system]
requires = ["poetry-core>=2.1.3"]  # MANDATORY version
build-backend = "poetry.core.masonry.api"

[tool.poetry]
name = "package_name"  # MUST use underscores, NOT hyphens
version = "0.4.0"      # Follow workspace versioning
description = "Clear, professional description"
authors = ["Team Name <team@company.com>"]
license = "MIT"
readme = "README.md"
packages = [{ include = "package_name", from = "src" }]
repository = "https://github.com/datacosmos-br/package-name"
keywords = ["flx", "hexagonal", "domain-keywords"]

[tool.poetry.dependencies]
python = "^3.13,<3.15"  # MANDATORY Python 3.13+
# Core dependencies here

# Local FLX dependency pattern
[tool.poetry.dependencies.flx]
path = "../flx"
develop = true

[tool.poetry.group.dev.dependencies]
# MANDATORY dev dependencies
pytest = "^8.4.0"
pytest-asyncio = "<0.24.0"
pytest-cov = "^6.1.1"
pytest-mock = "^3.14.1"
mypy = "^1.16.0"
ruff = "^0.11.13"
black = "^25.1.0"
isort = "<6"
pre-commit = "^4.2.0"

[tool.poetry.scripts]
your-cli = "package_name.cli:main"

[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_configs = true
show_error_codes = true
pretty = true

[tool.black]
line-length = 88
target-version = ["py313"]

[tool.ruff]
target-version = "py313"
line-length = 88
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "W", "F", "I", "UP", "N", "B", "C4", "DTZ", "T10", "ISC", "PIE", "PT", "RET", "SIM", "ARG", "PL"]
ignore = ["E501", "PLR0913", "PLR2004", "TRY003"]

[tool.pytest.ini_options]
minversion = "8.0"
addopts = [
    "--strict-markers",
    "--strict-config", 
    "--cov-fail-under=90",  # MANDATORY 90% coverage
    "--cov-report=term-missing",
    "--cov-report=html:reports/coverage",
]
testpaths = ["tests"]
```

## 🐍 Python Development Standards

### Type Hints (Python 3.13+)
```python
# Modern syntax - use built-in generics
def process_data(items: list[dict[str, Any]]) -> dict[str, int]:
    return {"count": len(items)}

# Union types
name: str | None = None
items: list[dict[str, Any]] = []

# NOT: Optional[str], List[Dict] - deprecated
```

### Pydantic Models
```python
from pydantic import BaseModel, Field, ConfigDict, field_validator

class ConfiguredModel(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra='forbid',
        validate_assignment=True,
        frozen=True  # For immutable models
    )
    
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=18, le=150)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()
```

### Error Handling
```python
# Domain-specific exceptions
class DomainError(Exception):
    """Base domain exception."""

class BusinessRuleViolationError(DomainError):
    """Raised when business rules are violated."""

# Proper error handling
try:
    result = risky_operation()
except SpecificError as e:
    logger.error("Operation failed", error=str(e), context=context)
    raise BusinessRuleViolationError(f"Cannot process: {e}") from e
```

### Async Patterns
```python
# Connection pooling
import httpx

# Reuse client with connection pool
http_client = httpx.AsyncClient(
    limits=httpx.Limits(max_keepalive_connections=25, max_connections=100),
    timeout=httpx.Timeout(30.0),
    http2=True
)

# Retry logic
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def fetch_data(url: str) -> dict:
    async with http_client as client:
        response = await client.get(url)
        return response.json()

# Concurrent execution
async def process_items(items: list[str]) -> list[dict]:
    tasks = [process_single_item(item) for item in items]
    return await asyncio.gather(*tasks)
```

## 🔌 Oracle Integration Patterns

### Oracle WMS Integration
```python
from flx_http_oracle_wms import WmsClient, WmsConfig

# Configuration
wms_config = WmsConfig(
    base_url="https://your-wms.oracle.com",
    username="wms_user",
    password=os.getenv("WMS_PASSWORD"),
    facility_id="FACILITY_001"
)

# Usage
async with WmsClient(wms_config) as wms:
    # Query items
    items = await wms.query_items({
        "item_code": "PROD-001",
        "facility_id": "FACILITY_001"
    })
    
    # Create shipment
    shipment = await wms.create_shipment({
        "order_id": "ORD-123",
        "items": [{"sku": "PROD-001", "qty": 10}]
    })
```

### Oracle OIC Integration
```python
from flx_http_oracle_oic import OracleOicClient, OicConfig

# OAuth2 configuration
oic_config = OicConfig(
    base_url="https://your-oic.oracle.com",
    client_id=os.getenv("OIC_CLIENT_ID"),
    client_secret=os.getenv("OIC_CLIENT_SECRET"),
    scope="https://your-oic.oracle.com:443/urn:opc:resource:consumer::all"
)

# Usage with automatic token management
async with OracleOicClient(oic_config) as oic:
    result = await oic.execute_integration(
        integration_id="WMS_ORDER_SYNC",
        payload={"order_id": "ORD-123"}
    )
```

### Oracle Database Integration
```python
from flx_database_oracle import FlxOracleDbAdapter, DatabaseConfig

# Database configuration
db_config = DatabaseConfig(
    host="oracle-db.company.com",
    port=1521,
    service_name="ORCL",
    username="app_user",
    password=os.getenv("DB_PASSWORD")
)

# Async operations
async with FlxOracleDbAdapter(db_config) as db:
    # Execute query
    orders = await db.fetch_all(
        "SELECT * FROM orders WHERE status = :status",
        {"status": "PENDING"}
    )
    
    # Transaction support
    async with db.transaction():
        await db.execute(
            "UPDATE inventory SET qty = qty - :qty WHERE sku = :sku",
            {"qty": 10, "sku": "PROD-001"}
        )
```

## 🧪 Testing Strategy

### Test Organization
```
tests/
├── unit/              # Fast, isolated tests
│   ├── test_core.py   # Domain logic tests
│   ├── test_adapters.py # Adapter tests with mocks
│   └── test_models.py # Model validation tests
├── integration/       # Component interaction
│   └── test_integration.py # Real dependencies
├── e2e/              # End-to-end workflows
│   └── test_workflows.py
└── conftest.py       # Shared fixtures
```

### Test Patterns
```python
import pytest
from unittest.mock import AsyncMock

# Fixtures
@pytest.fixture
def mock_repository():
    repo = AsyncMock()
    repo.get.return_value = Order(id=UUID("..."))
    return repo

# Unit test
@pytest.mark.asyncio
async def test_order_completion(mock_repository):
    service = OrderService(mock_repository)
    await service.complete_order(order_id)
    
    mock_repository.get.assert_called_once_with(order_id)
    mock_repository.save.assert_called_once()

# Parametrized test
@pytest.mark.parametrize("status,should_fail", [
    (OrderStatus.DRAFT, False),
    (OrderStatus.COMPLETED, True),
    (OrderStatus.CANCELLED, True),
])
def test_order_completion_rules(status, should_fail):
    order = Order(status=status)
    if should_fail:
        with pytest.raises(BusinessRuleViolationError):
            order.complete()
    else:
        order.complete()
        assert order.status == OrderStatus.COMPLETED
```

## 🔒 Security Best Practices

### Environment Variables
```python
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file

# Use environment variables for secrets
db_password = os.getenv("DB_PASSWORD")  # ✅
api_key = os.getenv("API_KEY")          # ✅

# NEVER hardcode secrets
db_password = "my-password"  # ❌ NEVER DO THIS
```

### Input Validation
```python
from pydantic import BaseModel, EmailStr, validator

class UserInput(BaseModel):
    email: EmailStr
    age: int
    
    @validator('age')
    def validate_age(cls, v):
        if v < 18 or v > 150:
            raise ValueError('Age must be between 18 and 150')
        return v

# SQL injection prevention
async def get_user(user_id: str) -> dict:
    # Parameterized query prevents SQL injection
    query = "SELECT * FROM users WHERE id = $1"  # ✅
    return await db.fetchrow(query, user_id)
    
    # NEVER use string formatting
    # query = f"SELECT * FROM users WHERE id = '{user_id}'"  # ❌
```

## 🚫 Common Mistakes to Avoid

### 1. Creating Duplicate Scripts
```bash
# ❌ WRONG: Creating new analysis script
vim analyze_code.py

# ✅ CORRECT: Check existing first
find scripts/ -name "*analy*" -type f
# Found: scripts/analysis/analyze_flx.py - use this!
```

### 2. Wrong Import Statements
```python
# ❌ WRONG: Using hyphenated name
from flx-database-oracle import adapter

# ✅ CORRECT: Use underscore
from flx_database_oracle import adapter
```

### 3. Ignoring Layer Boundaries
```python
# ❌ WRONG: Domain importing infrastructure
# In flx/core/entities.py
from flx.infra.database import session

# ✅ CORRECT: Use ports
from flx.ports.outbound import RepositoryPort
```

### 4. Poor Test Organization
```bash
# ❌ WRONG: Multiple test files for same component
test_adapter_simple.py
test_adapter_comprehensive.py
test_adapter_final.py

# ✅ CORRECT: Single consolidated file
tests/unit/test_adapter.py
```

## ⚠️ Warning Fix Standards

### CRITICAL: Real Fixes, Not Cosmetic Solutions

**User Feedback**: "warning filter, palhaçada, quero que você arrume de verdade sempre, não fique fazendo maquiagem"

**Translation**: "warning filter, nonsense, I want you to fix things properly always, don't do cosmetic things"

### Pydantic V1 to V2 Migration

The most common warning in FLX framework was Pydantic deprecation warnings from V1 `@validator` decorators:

```python
# ❌ WRONG - Suppress warnings (cosmetic fix)
import warnings
warnings.filterwarnings("ignore", module="pydantic")

# ✅ CORRECT - Fix root cause (real fix)
# 1. Update imports
from pydantic import BaseModel, Field, validator         # Old V1
from pydantic import BaseModel, Field, field_validator   # New V2

# 2. Update validator decorators
@validator('field_name')           # Old V1
def validate_field(cls, v):
    return v

@field_validator('field_name')     # New V2
@classmethod
def validate_field(cls, v):
    return v

# 3. Update class-based config
class Config:                      # Old V1
    frozen = True
    extra = "forbid"

model_config = ConfigDict(         # New V2
    frozen=True,
    extra="forbid"
)
```

### Warning Fix Process

1. **Identify Root Cause**: Never suppress warnings - find what's causing them
2. **System-wide Fix**: Fix all instances, not just one file
3. **Verify Solution**: Test without warning filters to ensure warnings are gone
4. **Document Fix**: Update CLAUDE.md with the proper solution pattern

### Files Fixed in FLX Framework

- `flx/src/flx/testing/engines/base.py` - Updated @validator → @field_validator
- `flx/src/flx/core/meta_factory.py` - Updated @validator → @field_validator
- `flx/src/flx/adapters/mixins/configuration.py` - Updated @validator → @field_validator
- `flx/src/flx/adapters/templates/modern_adapter_template.py` - Updated @validator → @field_validator
- `flx/src/flx/infra/deployment/environments.py` - Updated @validator → @field_validator
- `flx/src/flx/infra/deployment/pipeline.py` - Updated @validator → @field_validator
- `flx/src/flx/infra/deployment/strategies.py` - Updated @validator → @field_validator
- `flx/src/flx/testing/engines/cache_engine.py` - Updated @validator → @field_validator
- `flx/src/flx/testing/engines/database_engine.py` - Updated @validator → @field_validator
- `flx/src/flx/testing/engines/http_engine.py` - Updated @validator → @field_validator
- `flx/src/flx/testing/engines/test_orchestrator.py` - Updated @validator → @field_validator

**Result**: Zero pydantic deprecation warnings in FLX framework

## 🔍 Debugging Tips

### Import Errors
```bash
# Verify module structure
python -c "import flx_database_oracle; print(flx_database_oracle.__file__)"

# Check sys.path
python -c "import sys; print('\n'.join(sys.path))"
```

### Test Failures
```bash
# Run with verbose output
pytest -xvs path/to/test.py

# Run with debugging
pytest --pdb path/to/test.py

# Check coverage gaps
pytest --cov=module --cov-report=term-missing
```

### Type Errors
```bash
# Get detailed mypy output
mypy --show-error-codes --pretty path/to/file.py

# Check specific error
mypy --show-error-context path/to/file.py | grep "error:"
```

## 📊 Quality Standards

- **Code Coverage**: 90% minimum (100% for domain layer)
- **Type Coverage**: 100% for public APIs
- **Documentation**: All public modules, classes, and methods
- **Test Pyramid**: Unit > Integration > E2E
- **Performance**: Connection pooling, async patterns, caching

## 🔄 Continuous Improvement

When you notice patterns repeating:

1. **Document the Pattern**
```markdown
## Repeated Pattern: [Pattern Name]
**Frequency**: Seen in X sessions
**Context**: When this occurs
**Solution**: Standard approach
**Example**: Code or command
```

2. **Add to CLAUDE.md**
   - Commands → Essential Commands
   - Errors → Common Issues
   - Patterns → Best Practices

3. **Share Knowledge**
```bash
echo "PATTERN: Fixed mypy error 3 times - documenting" >> .token
```

## 🚀 Quick Reference

### Checklist Before Starting
- [ ] Activated virtual environment
- [ ] Checked .token for coordination
- [ ] Validated no existing solution exists
- [ ] Understood which layer to modify

### Checklist Before Committing
- [ ] All tests passing (>90% coverage)
- [ ] Type checking passing (mypy strict)
- [ ] Code formatted (black)
- [ ] Linting passing (ruff)
- [ ] Documentation updated
- [ ] Coordination token updated

---

**Remember**: Quality > Speed. Always validate, test, and document.
**Priority**: Security > Correctness > Performance > Features