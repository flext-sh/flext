# FLEXT Ecosystem Refactoring Agent — STRICT FULL PROMPT (IMPROVED)

**Enterprise-Grade LLM Agent Instructions for FLEXT Architecture Compliance**
**This prompt assumes the virtual environment is already activated:**
`source ~/flext/.venv/bin/activate`
**Do not change this path. Do not export PYTHONPATH. Do not prefix commands with `env`.**

---

## 🎯 Mission Statement (Non-Negotiable)

Read calmly, act meticulously, and execute via a continuously updated **TODO Plan**.
**Goal:** 100% compliance with FLEXT architectural standards with **zero** regressions and **zero** issues in **Ruff**, **Mypy (strict)**, **Pyright**, and **Pytest**.

**CRITICAL: ELIMINATE ALL CODE DUPLICATION ACROSS PROJECTS**

You MUST:

* **GENERALIZE flext-core usage** - Make ALL projects depend ONLY on flext-core foundation classes, never create local substitutes
* **ELIMINATE duplication** - Remove ANY local implementations that duplicate flext-core functionality
* **CENTRALIZE patterns** - Move reusable patterns TO flext-core for ecosystem-wide usage
* **STANDARDIZE interfaces** - Use ONLY flext-core protocols, models, and services across all projects
* Enforce **PEP8** naming and **single-consolidated-class-per-module**
* Use **root-level imports** only (outside same project) - `from flext_core import X` not `from flext_core.module import X`
* Apply **SOLID**, **Python 3.13+ typing**, and **Pydantic v2 (`FlextModel`)**
* Keep **`__init__.py` imports working at ALL times**
* Validate after **EVERY** edit with the Quality Gates below
* **NEVER** change `pyproject.toml`, lint configs, or use ignore statements
* **NEVER** break public APIs; maintain backward compatibility through aliases
* **FIX ROOT CAUSES**, not symptoms - always trace errors to source

---

## 🔧 Environment Assumptions (Strict)

* Active venv: **`~/flext/.venv`**. Do **not** alter it.
* **No** use of `PYTHONPATH`.
* **No** use of `env` prefixes in commands.
* Commands below rely on PATH resolution inside the activated venv.

---

## 📋 Mandatory TODO Plan

```
Phase X: [Description]
□ Task 1: [Specific action + exact validation command(s)]
□ Task 2: [Specific action + exact validation command(s)]
□ Task 3: [Specific action + exact validation command(s)]
Status: [In Progress/Completed]
Validation: [Ruff/Mypy/Pyright/Pytest/Imports: PASS|FAIL]
```

---

## 🏗️ Source Directory Structure Rules (CRITICAL CLARIFICATION)

### ✅ MANDATORY FLAT STRUCTURE WITHIN NAMESPACES

**CORRECT structure to MAINTAIN - COMPLETELY FLAT:**
```
src/
└── project_namespace/     # Keep namespace directory (TRUTH: 22-40 modules typical)
    ├── __init__.py         # Essential for wildcard imports
    ├── models.py           # All models in single consolidated class
    ├── services.py         # All services in single consolidated class
    ├── exceptions.py       # All exceptions in single consolidated class
    ├── constants.py        # All constants in single consolidated class
    ├── client.py           # Main client implementation
    ├── api.py              # Facade orchestration class
    └── ... (15-35+ more modules) # REALITY: FLEXT projects have many specialized modules
```

### ❌ ABSOLUTELY FORBIDDEN - NO SUBDIRECTORIES

**DO NOT CREATE:**
- ANY subdirectories within `src/namespace/`
- Nested package structures like `src/namespace/subpackage/`
- Directory hierarchies for organization
- Folders for grouping related modules

**EXAMPLES OF FORBIDDEN STRUCTURES:**
```
❌ src/project_namespace/models/        # FORBIDDEN - no subdirectories
❌ src/project_namespace/services/      # FORBIDDEN - no subdirectories  
❌ src/project_namespace/utils/         # FORBIDDEN - no subdirectories
❌ src/project_namespace/core/          # FORBIDDEN - no subdirectories
❌ src/project_namespace/api/           # FORBIDDEN - no subdirectories
```

### ✅ WHAT TO REFACTOR WITHIN FLAT NAMESPACES

**PEP8 module naming within flat namespace structure:**
```
src/project_namespace/
├── base_service.py    → services.py        # Consolidated service class
├── wrapper_client.py  → client.py          # Main client implementation 
├── manager_config.py  → models.py          # Consolidated model class
└── executor_task.py   → constants.py       # Consolidated constants class
```

**MANDATORY FLAT STRUCTURE FOR ALL NAMESPACES (Based on flext-core/flext-cli reality):**
Every namespace maintains flat organization with multiple modules:
```
src/any_namespace/
├── __version__.py      # Version information
├── api.py              # API facade
├── client.py           # Main client implementation
├── config.py           # Configuration classes
├── constants.py        # Project constants
├── exceptions.py       # Custom exceptions
├── models.py           # Domain models
├── services.py         # Service classes
├── utilities.py        # Helper utilities
└── [additional_modules].py  # As needed
```

### 🚫 ZERO TOLERANCE FOR SUBDIRECTORIES

**IMMEDIATE VIOLATION DETECTION:**
```bash
# This command MUST return ZERO results:
find src/ -type d -mindepth 2 | grep -v __pycache__ | wc -l  # Should be 0
```

**Multiple classes per module within namespace (Based on flext-core/flext-cli reality):**
```python
# src/flext_ldap/models.py - GOOD (Multiple classes like flext-core)
class LdapUser(FlextModel):
    """User model following FLEXT patterns."""
    uid: str = Field(..., min_length=1)
    cn: str = Field(..., min_length=1)

class LdapGroup(FlextModel):
    """Group model following FLEXT patterns."""
    name: str = Field(..., min_length=1)

# Export all classes via __all__
__all__ = ["LdapUser", "LdapGroup"]

# src/flext_ldap/services.py - GOOD (Multiple services like flext-core)  
class LdapUserService(FlextDomainService[FlextResult[object]]):
    """User service following FLEXT patterns."""
    
    def create_user(self, user_data: FlextModel) -> FlextResult[LdapUser]:
        """Create user service method."""
        pass

class LdapGroupService(FlextDomainService[FlextResult[object]]):
    """Group service following FLEXT patterns."""
    pass

# Export all services via __all__
__all__ = ["LdapUserService", "LdapGroupService"]
```

### ✅ PEP8 NAMING CONVENTIONS (MANDATORY COMPLIANCE)

**Module Names (snake_case):**
```python
# GOOD - PEP8 compliant module names
auth_client.py          # Authentication client
config_manager.py       # Configuration management  
data_processor.py       # Data processing
http_adapter.py         # HTTP adapter
service_registry.py     # Service registry
validation_rules.py     # Validation rules
```

**Class Names (PascalCase with PROJECT-SPECIFIC FLEXT prefix):**
```python
# GOOD - PEP8 + PROJECT-SPECIFIC FLEXT naming
# For flext-ldap project: use "FlextLdap" prefix
class FlextLdapClient(FlextDomainService[FlextResult[AuthToken]]):
    """LDAP client following SOLID principles."""
    pass

class FlextLdapConfig(FlextModel):  # Pydantic v2 model
    """LDAP configuration management with Pydantic validation."""
    server: str = Field(..., min_length=3)
    port: int = Field(default=389, gt=0, le=65535)

# For flext-auth project: use "FlextAuth" prefix  
class FlextAuthClient(FlextDomainService[FlextResult[AuthToken]]):
    """Authentication client following SOLID principles."""
    pass
```

**Function Names (snake_case):**
```python
# GOOD - PEP8 function naming
def authenticate_user(credentials: AuthCredentials) -> FlextResult[User]:
    """Authenticate user with proper error handling."""
    pass

def validate_config_data(config: dict) -> FlextResult[FlextConfigModel]:
    """Validate configuration using Pydantic models."""
    pass
```

### ✅ SOLID PRINCIPLES ENFORCEMENT 

#### 1. Single Responsibility Principle (SRP)
```python
# GOOD - Each class has single responsibility
class FlextAuthClient(FlextDomainService[FlextResult[AuthToken]]):
    """Only handles authentication operations."""
    
    def authenticate(self, credentials: AuthCredentials) -> FlextResult[AuthToken]:
        """Single responsibility: authenticate users."""
        return self._execute_auth(credentials)

class FlextUserRepository(FlextDomainService[FlextResult[User]]):
    """Only handles user data persistence."""
    
    def save_user(self, user: User) -> FlextResult[User]:
        """Single responsibility: persist user data."""
        return self._save_to_storage(user)
```

#### 2. Open/Closed Principle (OCP) 
```python
# GOOD - Open for extension, closed for modification
from abc import ABC, abstractmethod
from flext_core import FlextDomainService, FlextResult

class FlextNotificationService(FlextDomainService[FlextResult[bool]]):
    """Base notification service - extend via composition."""
    
    def __init__(self, providers: List[NotificationProvider]):
        super().__init__()
        self._providers = providers
    
    def send_notification(self, message: NotificationMessage) -> FlextResult[bool]:
        """Send via all configured providers."""
        results = [provider.send(message) for provider in self._providers]
        return FlextResult.ok(all(r.is_success for r in results))
```

#### 3. Liskov Substitution Principle (LSP)
```python
# GOOD - Subtypes are substitutable for base types
class FlextStorageProvider(ABC):
    """Abstract storage provider following LSP."""
    
    @abstractmethod
    def store_data(self, data: FlextModel) -> FlextResult[str]:
        """Store data and return identifier."""
        pass

class FlextS3Storage(FlextStorageProvider):
    """S3 storage implementation maintains contract."""
    
    def store_data(self, data: FlextModel) -> FlextResult[str]:
        """Store in S3, returns S3 key as identifier."""
        # Implementation maintains same behavior contract
        pass
```

#### 4. Interface Segregation Principle (ISP)
```python
# GOOD - Small, focused interfaces using flext-core protocols
from flext_core import FlextProtocols, FlextResult

class FlextAuthService(FlextDomainService[FlextResult[bool]]):
    """Uses focused flext-core protocols, not fat interfaces."""
    
    def __init__(self, 
                 authenticator: FlextProtocols.Infrastructure.Auth,
                 authorizer: FlextProtocols.Application.AuthorizingHandler):
        super().__init__()
        self._authenticator = authenticator
        self._authorizer = authorizer
    
    def authenticate_user(self, credentials: dict) -> FlextResult[bool]:
        """Authenticate user using injected auth protocol."""
        return self._authenticator.authenticate(credentials)
    
    def authorize_access(self, user_info: dict, resource: str) -> FlextResult[bool]:
        """Authorize access using injected authorizer protocol."""
        return self._authorizer.authorize(user_info, resource)
```

#### 5. Dependency Inversion Principle (DIP)
```python
# GOOD - Depend on flext-core abstractions, not concretions
from flext_core import FlextProtocols, FlextResult

class FlextDataProcessor(FlextDomainService[FlextResult[ProcessedData]]):
    """Depends on flext-core abstractions via dependency injection."""
    
    def __init__(self, 
                 storage: FlextProtocols.Domain.Repository[ProcessedData],  # flext-core protocol
                 validator: FlextProtocols.Foundation.Validator[ProcessedData],  # flext-core protocol
                 logger: FlextProtocols.Infrastructure.LoggerProtocol):  # flext-core protocol
        super().__init__()
        self._storage = storage      # Injected dependency
        self._validator = validator  # Injected dependency  
        self._logger = logger        # Injected dependency
    
    def process_data(self, data: ProcessedData) -> FlextResult[ProcessedData]:
        """Process data using injected protocols."""
        # Validate using injected validator
        validation_result = self._validator.validate(data)
        if not validation_result.is_success:
            return validation_result
        
        # Store using injected repository
        storage_result = self._storage.save(data)
        if not storage_result.is_success:
            self._logger.error(f"Storage failed: {storage_result.error}")
            return storage_result
        
        self._logger.info("Data processed successfully")
        return FlextResult.ok(data)
```

### ✅ Pydantic V2 INTEGRATION PATTERNS

#### FlextModel Base Class Usage
```python
# MANDATORY - Always inherit from FlextModel (extends Pydantic BaseModel)
from flext_core import FlextModel, FlextResult
from pydantic import Field, validator

class FlextUserConfig(FlextModel):
    """User configuration with Pydantic v2 validation."""
    
    # Field validation with Pydantic v2
    username: str = Field(..., min_length=3, max_length=50, regex=r'^[a-zA-Z0-9_]+$')
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    age: int = Field(..., ge=18, le=120)
    roles: List[str] = Field(default_factory=list)
    
    # Custom validation with Pydantic v2
    @validator('username')
    def validate_username(cls, v):
        if v.lower() in ['REDACTED_LDAP_BIND_PASSWORD', 'root', 'system']:
            raise ValueError('Reserved username not allowed')
        return v
    
    # Model configuration
    model_config = {
        'str_strip_whitespace': True,
        'validate_assignment': True,
        'extra': 'forbid'
    }
```

#### Integration with FlextResult Pattern
```python
# GOOD - Pydantic + FlextResult integration
def create_user_from_data(data: dict) -> FlextResult[FlextUserConfig]:
    """Create validated user from dictionary data."""
    try:
        user_config = FlextUserConfig.model_validate(data)
        return FlextResult.ok(user_config)
    except ValidationError as e:
        return FlextResult.error(f"Validation failed: {e}")

def update_user_config(user: FlextUserConfig, updates: dict) -> FlextResult[FlextUserConfig]:
    """Update user configuration with validation."""
    try:
        updated_data = user.model_dump() | updates
        updated_user = FlextUserConfig.model_validate(updated_data)
        return FlextResult.ok(updated_user)
    except ValidationError as e:
        return FlextResult.error(f"Update validation failed: {e}")
```

### ✅ flext-core INTEGRATION REQUIREMENTS

#### Mandatory Base Class Usage
```python
# MANDATORY - Always use flext-core base classes
from flext_core import (
    FlextDomainService,      # For business services
    FlextModel,              # For data models (Pydantic-based)
    FlextResult,             # For error handling
    FlextProtocols,          # For all protocol definitions
    get_logger,              # For logging
    get_flext_container      # For dependency injection
)

class FlextBusinessService(FlextDomainService[FlextResult[BusinessData]]):
    """Business service using flext-core foundation and protocols."""
    
    def __init__(self):
        super().__init__()  # MANDATORY - call parent constructor
        self._logger = get_logger(__name__)  # Use flext-core logging
        self._container = get_flext_container()  # Use flext-core DI
    
    def process_business_logic(self, input_data: FlextModel) -> FlextResult[BusinessData]:
        """Process with proper error handling and logging."""
        try:
            self._logger.info("Processing business logic")
            # Business logic here
            result = self._execute_processing(input_data)
            return FlextResult.ok(result)
        except Exception as e:
            self._logger.error(f"Processing failed: {e}")
            return FlextResult.error(str(e))
    
    def validate_with_protocol(self, validator: FlextProtocols.Foundation.Validator[BusinessData], 
                              data: BusinessData) -> FlextResult[None]:
        """Use flext-core validation protocol."""
        return validator.validate(data)
```

#### Prohibited Local Implementations 
```python
# ❌ FORBIDDEN - Never create local base classes
class LocalBaseService(ABC):  # FORBIDDEN - use FlextDomainService
    pass

class LocalModel(BaseModel):  # FORBIDDEN - use FlextModel  
    pass

class LocalResult:  # FORBIDDEN - use FlextResult
    pass

# ✅ CORRECT - Always use flext-core
class FlextCorrectService(FlextDomainService[FlextResult[Data]]):
    """Uses flext-core foundation."""
    
    def __init__(self, validator: FlextProtocols.Foundation.Validator[Data]):
        super().__init__()
        self._validator = validator
    
    def validate_data(self, data: Data) -> FlextResult[None]:
        """Use flext-core validation protocol."""
        return self._validator.validate(data)

class FlextCorrectModel(FlextModel):
    """Uses flext-core Pydantic model."""
    pass
```

---

## 🏗️ Systematic Refactoring Framework

### Phase 1 — Architecture Analysis & Foundation (MANDATORY first)

1. **Read flext-core patterns FIRST (do not assume):**

```bash
python -c "from flext_core import FlextDomainService; help(FlextDomainService)"
python -c "from flext_core import FlextResult; help(FlextResult)"
python -c "from flext_core import FlextModel; help(FlextModel)"
python -c "from flext_core import get_logger; help(get_logger)"
```

2. **Map current project structure and abstractions:**

```bash
find src/ -name "*.py" -exec head -20 {} \;
grep -r "class.*Base\|class.*Abstract" src/ --include="*.py"
grep -r "ABC\|abstractmethod" src/ --include="*.py"
grep -r "Protocol\|@abstractmethod" src/ --include="*.py"
grep -r "from flext_" src/ --include="*.py" | sort | uniq
grep -r "from flext_.*\." src/ --include="*.py"  # non-root imports to fix
```

3. **PEP8 module naming audit (rename plan within namespaces):**

```bash
find src/ -name "*.py" | grep -E "(base_|wrapper_|executor_|manager_)"
# Strategy within each namespace:
# base_*     → service_*
# wrapper_*  → adapter_*
# executor_* → execution_*
# manager_*  → controller_*
```

---

### Phase 2 — flext-core Foundation Enforcement (ELIMINATE ALL DUPLICATION)

**🎯 MANDATORY: GENERALIZE flext-core usage across ALL projects**

**CRITICAL PRINCIPLE: flext-core is the SINGLE SOURCE OF TRUTH for all ecosystem patterns**

* ✅ **ONLY acceptable base classes (ROOT-LEVEL imports only):**

```python
# ✅ CORRECT - Root-level imports from flext-core
from flext_core import (
    FlextAggregateRoot,      # For ALL aggregate roots across ecosystem
    FlextConstants,          # For ALL constants across ecosystem
    FlextContainer,          # For ALL dependency injection across ecosystem
    FlextDecorators,         # For ALL decorator patterns across ecosystem
    FlextDomainService,      # For ALL business services across ecosystem
    FlextEntity,             # For ALL domain entities across ecosystem
    FlextGuards,             # For ALL guard functions across ecosystem
    FlextHandlers,           # For ALL command/query handlers across ecosystem
    FlextModel,              # For ALL Pydantic models across ecosystem
    FlextResult,             # For ALL error handling across ecosystem
    FlextServiceProcessor,   # For ALL data processing across ecosystem  
    FlextSettings,           # For ALL configuration across ecosystem
    FlextValidators,         # For ALL validation logic across ecosystem
    FlextValueObject,        # For ALL value objects across ecosystem
    get_flext_container,     # For ALL service registration across ecosystem
    get_logger,              # For ALL logging across ecosystem
)

# ✅ EXAMPLE: All projects follow same pattern
class FlextLdapClient(FlextDomainService[FlextResult[LdapUser]]):
    """LDAP client using GENERALIZED flext-core foundation."""
    
    def __init__(self):
        super().__init__()
        self._container = get_flext_container()  # GENERALIZED DI
        self._logger = get_logger(__name__)      # GENERALIZED logging
        self._validators = FlextValidators       # GENERALIZED validation

class FlextAuthService(FlextDomainService[FlextResult[AuthToken]]):
    """Auth service using SAME GENERALIZED flext-core foundation."""
    
    def __init__(self):
        super().__init__()
        self._container = get_flext_container()  # SAME pattern across projects
        self._logger = get_logger(__name__)      # SAME pattern across projects
        self._validators = FlextValidators       # SAME pattern across projects
```

* ❌ **FORBIDDEN local abstractions (DELETE immediately from ALL projects):**

```python
# ❌ WRONG - Local abstractions that duplicate flext-core
class MyBaseService(ABC): ...             # DELETE - use FlextDomainService
class MyServiceProtocol(Protocol): ...    # DELETE - use flext-core protocols
class MyAbstractClient: ...               # DELETE - use FlextDomainService
class BaseConfig: ...                     # DELETE - use FlextSettings/FlextModel
class CustomResult: ...                   # DELETE - use FlextResult
class LocalLogger: ...                    # DELETE - use get_logger()
class ProjectContainer: ...               # DELETE - use get_flext_container()
class CustomValidator: ...                # DELETE - use FlextValidators
class ProjectConstants: ...               # DELETE - use FlextConstants
```

* ✅ **GENERALIZED protocols from flext-core (avoid local protocols):**

```python
# ✅ CORRECT - Use flext-core protocols across ALL projects
from flext_core import (
    # Main hierarchical protocols class - access all protocols
    FlextProtocols,
    
    # Specific protocol aliases for backward compatibility
    FlextService,              # Domain service protocol
    FlextRepository,           # Repository pattern protocol
    FlextHandler,              # Application handler protocol
    FlextValidator,            # Validation protocol
    FlextLoggerProtocol,       # Logging protocol
    FlextConnection,           # Connection protocol
    FlextAuthProtocol,         # Authentication protocol
    FlextConfigurable,         # Configuration protocol
    FlextObservabilityProtocol # Observability protocol
)

# ✅ CORRECT - Use hierarchical access for modern patterns
from flext_core import FlextProtocols

# Foundation layer protocols
validator: FlextProtocols.Foundation.Validator[str] = email_validator
factory: FlextProtocols.Foundation.Factory[User] = user_factory

# Domain layer protocols  
service: FlextProtocols.Domain.Service = user_service
repository: FlextProtocols.Domain.Repository[User] = user_repo

# Application layer protocols
handler: FlextProtocols.Application.Handler[CreateUser, str] = create_user_handler
processor: FlextProtocols.Application.EventProcessor = event_processor

# Infrastructure layer protocols
connection: FlextProtocols.Infrastructure.Connection = db_connection
auth: FlextProtocols.Infrastructure.Auth = auth_service
logger: FlextProtocols.Infrastructure.LoggerProtocol = logger_instance

# Extensions layer protocols
plugin: FlextProtocols.Extensions.Plugin = my_plugin
middleware: FlextProtocols.Extensions.Middleware = auth_middleware
```

* 🔄 **CENTRALIZATION STRATEGY: Move reusable patterns TO flext-core**

```python
# If multiple projects need similar functionality:
# 1. Implement it in flext-core first
# 2. Make all projects import from flext-core
# 3. Remove local duplicates

# Example: Database connection pattern used by 5+ projects
# WRONG: Each project has local DbConnection class
# RIGHT: Move to flext-core.database, all projects import from there
```

**DEDUPLICATION VALIDATION (CRITICAL COMMANDS):**
```bash
# These commands MUST return ZERO results across ALL projects:
grep -r "class.*Base.*ABC" src/ --include="*.py"                    # Should be EMPTY
grep -r "class.*Abstract" src/ --include="*.py"                     # Should be EMPTY  
grep -r "class.*Protocol.*:" src/ --include="*.py" | grep -v "from flext_core"  # Should be EMPTY
grep -r "def get_logger\|class.*Logger" src/ --exclude-dir=flext-core --include="*.py"  # Should be EMPTY
grep -r "class.*Container\|def.*container" src/ --exclude-dir=flext-core --include="*.py"  # Should be EMPTY
grep -r "class.*Result\|def.*result" src/ --exclude-dir=flext-core --include="*.py"  # Should be EMPTY

# Verify flext-core protocols usage (SHOULD be > 0):
grep -r "from flext_core import.*FlextProtocols\|FlextService\|FlextRepository\|FlextHandler" src/ --include="*.py" | wc -l  # Should be > 0

# Internal imports within same project (ACCEPTABLE):
grep -r "from flext_core\." src/flext_core/ --include="*.py"        # ACCEPTABLE - internal imports
# Cross-project imports (FORBIDDEN):
grep -r "from flext_core\." src/ --exclude-dir=flext-core --include="*.py"  # Should be EMPTY
```

---

### Phase 3 — Single CONSOLIDATED Class per Module (PRAGMATIC approach within namespaces)

**⚠️ STANDARD APPROACH: Use CONSOLIDATED classes for related functionality (Option 2 - Pragmatic)**

* **Option 2 (Pragmatic - RECOMMENDED)**: Allow classes related by domain/function in the same module, but create a main CONSOLIDATED class
  - Maintain handlers, models, or services together when they form cohesive units  
  - Create primary class like `FlextHandlers`, `FlextLdapModels`, `FlextAuthServices` as main interface
  - **Advantage**: Less disruptive, maintains logical cohesion, reduces import complexity
  - **Pattern**: Related classes coexist, but one main CONSOLIDATED class serves as primary interface

* **CONSOLIDATED classes** contain all related functionality as methods/properties/nested classes
* **Maintain backward compatibility** through property/method re-exports in `__init__.py` and main CONSOLIDATED class
* **Avoid unnecessary module proliferation** - keep related functionality together

**ALWAYS CHOOSE: Single CONSOLIDATED class with nested classes (Option B)**
```python
# ✅ CORRECT - Single consolidated class
class client-aMigExceptions(FlextError):
    """Consolidated class containing ALL project exceptions."""
    
    class ConfigError(FlextError):
        """Configuration error."""
        pass
    
    class ConnectionError(FlextError):
        """Connection error."""  
        pass
    # ... all others as nested classes
```

**NEVER CHOOSE: Multiple separate modules (Option A is FORBIDDEN)**
```python
# ❌ FORBIDDEN - Do not split into separate modules
# exceptions_config.py       # WRONG - creates module proliferation
# exceptions_connection.py   # WRONG - violates consolidation principle
# exceptions_processing.py   # WRONG - breaks FLEXT architecture
```

**CONSOLIDATED CLASS EXAMPLES:**

```python
# src/flext_plugin/exceptions.py - GOOD (Single Consolidated Exception Class)
class FlextPluginExceptions(FlextError):
    """Single consolidated class containing ALL plugin exceptions.
    
    Consolidates ALL exception definitions into one class following FLEXT patterns.
    Individual exceptions available as nested classes for organization.
    """
    
    class DiscoveryError(FlextError):
        """Plugin discovery specific error."""
        pass
    
    class LoadingError(FlextError):
        """Plugin loading specific error."""
        pass
    
    # Legacy compatibility properties
    @property
    def FlextPluginDiscoveryError(self):
        return self.DiscoveryError
    
    @property
    def FlextPluginLoadingError(self):
        return self.LoadingError

# src/flext_plugin/models.py - GOOD (Single Consolidated Model Class)  
class FlextPluginModels(FlextModel):
    """Single consolidated class containing ALL plugin models.
    
    Consolidates ALL model definitions into one class following FLEXT patterns.
    Individual models available as nested classes for organization.
    """
    
    class PluginConfig(FlextModel):
        """Plugin configuration model."""
        name: str = Field(..., min_length=1)
        version: str = Field(..., min_length=1)
    
    class PluginMetadata(FlextModel):
        """Plugin metadata model."""
        author: str = Field(..., min_length=1)
        description: str = Field(default="")
    
    # Legacy compatibility properties  
    @property
    def FlextPluginConfig(self):
        return self.PluginConfig
    
    @property
    def FlextPluginMetadata(self):
        return self.PluginMetadata

# src/flext_plugin/constants.py - GOOD (Single Consolidated Constants Class)
class FlextPluginConstants(FlextConstants):
    """Single consolidated class containing ALL plugin constants.
    
    Consolidates ALL constant definitions into one class following FLEXT patterns.
    Constants available as class attributes and properties for compatibility.
    """
    
    DEFAULT_TIMEOUT = 30
    MAX_RETRIES = 3
    PLUGIN_EXTENSIONS = ['.py', '.so', '.dll']
    
    # Legacy compatibility properties
    @property
    def FLEXT_PLUGIN_TIMEOUT(self):
        return self.DEFAULT_TIMEOUT
```

* **Naming rules**:

  * General modules: `Flext[Project][Category]` 
    e.g., `FlextPluginExceptions`, `FlextPluginModels`, `FlextPluginConstants`, `FlextApiClients`, `FlextAuthServices`.
  * **flext-core**: keeps `Flext` prefix; **main facade is `FlextCore`**.
  * **Exceptions (no `Flext` prefix):**

    * **client-a project** → classes must start with **`client-aMig`** (e.g., `client-aMigExceptions`, `client-aMigModels`).
    * **client-b project** → classes must start with **`GruposNosWmsIntOra`** (e.g., `GruposNosWmsIntOraServices`, `GruposNosWmsIntOraModels`).

* **Hierarchical inheritance** (mirror flext-core):

```python
from flext_core import FlextConstants, FlextTypes, FlextDomainService

class FlextAuthConstants(FlextConstants): ...
class FlextApiTypes(FlextTypes): ...
class FlextAuthService(FlextDomainService[dict]): ...
```

* **Public methods are aliases to internal implementations**:

```python
class FlextAuthClient(FlextDomainService[dict]):
    def authenticate(self, credentials: dict) -> "FlextResult[bool]":
        return self._internal_authenticate(credentials)

    def _internal_authenticate(self, credentials: dict) -> "FlextResult[bool]":
        ...
```

**client-a/client-b class prefixing (clarification):**

* Do **not** add `Flext` prefix in these projects.
* Use **project-specific prefixes** exactly as defined:

  * `client-aMig*` for client-a.
  * `GruposNosWmsIntOra*` for client-b.
* Facades for these projects also follow the same prefix (e.g., `client-aMigApi`, `GruposNosWmsIntOraApi`) and **must not implement logic**.

---

### Phase 4 — Facade Classes (Implement LAST; orchestration-only)

* Facades (e.g., `FlextCore`, `FlextApi`, `FlextCli`, `client-aMigApi`, `GruposNosWmsIntOraApi`) **must not** implement logic; only orchestrate:

```python
class FlextApi:
    def __init__(self):
        self._auth = FlextAuthClient()
        self._cfg  = FlextApiConfig()
        self._typ  = FlextApiTypes()

    def authenticate_request(self, req: dict):
        return self._auth.authenticate(req)
```

---

### Phase 5 — Module Organization Rules (PRESERVE NAMESPACES)

* ✅ **PRESERVE** namespace directories under `src/` (e.g., `src/project_name/`)
* ✅ **MAINTAIN** `__init__.py` functionality in all namespace directories
* ✅ Create **new modules (files)** within namespaces to split classes
* ✅ Move/rename files within namespaces; archive unused files as `*.bak`

**Namespace structure validation:**

```bash
# Verify namespace directories are preserved
find src/ -type d -mindepth 1 | grep -v __pycache__ | head -5
echo "✅ Namespace directories preserved (required for Python imports)"

# Validate all __init__.py files work
for namespace in $(find src/ -type d -mindepth 1 | grep -v __pycache__); do
  module_name=$(echo "$namespace" | sed 's|src/||' | tr '/' '.')
  python -c "import $module_name; print('✅ $module_name imports work')" 2>/dev/null || echo "❌ $module_name import failed"
done
```

---

### Phase 6 — Root-Level Import Standardization

* ✅ **Root imports ONLY (outside same project):**

```python
from flext_core import FlextResult, FlextDomainService, get_logger
from flext_cli import FlextCliConfig, FlextCliApi, setup_cli
from flext_meltano import FlextMeltanoTapService
```

* ❌ **FORBIDDEN (outside same project):**

```python
from flext_core.result import FlextResult               # WRONG
from flext_cli.config.settings import FlextCliConfig    # WRONG
from flext_meltano.base_services import ...             # WRONG
```

* **Exception**: inside the **same** project (e.g., within `flext-core` or within `src/project_name/`) internal imports are allowed:

```python
# Within same project namespace - ALLOWED:
from .config import ProjectConfig
from .constants import ProjectConstants
```

---

### Phase 7 — CLI Integration (if applicable)

Use **flext-cli** patterns:

```python
from flext_cli import FlextCliConfig, FlextCliApi, setup_cli, handle_service_result

@handle_service_result
def migrate_command(ctx, **kwargs) -> "FlextResult[dict]":
    ...
```

---

### Phase 8 — Type Safety (Python 3.13+) & Pydantic

* **Pydantic / FlextModel**:

```python
from flext_core import FlextModel
from pydantic import Field, validator
from pathlib import Path

class MigrationConfig(FlextModel):
    """Configuration for migrations.

    Args:
        input_dir: Path to the input directory.
    """
    input_dir: Path = Field(..., description="Input directory")

    @validator('input_dir')
    def _exists(cls, v: Path) -> Path:
        if not v.exists():
            raise ValueError(f"Input directory {v} does not exist")
        return v
```

* **Type aliases & generics**:

```python
type ConfigDict = dict[str, object]
type ResultDict = dict[str, object]
type ValidationResult = "FlextResult[bool]"

from typing import TypeVar, Protocol
T = TypeVar('T', bound=FlextModel)
```

---

### Phase 9 — SOLID Principles

* **SRP** — one responsibility per class.
* **DIP** — depend on **flext-core protocols**:

```python
from flext_core import FlextProtocols

class TapService:
    def __init__(self, repo: FlextProtocols.Domain.Repository[Data]):
        self.repo = repo
    
    def get_data(self, entity_id: str) -> FlextResult[Data]:
        """Get data using injected repository protocol."""
        return self.repo.get_by_id(entity_id)
```

---

### Phase 10 — Tests Layout & Standards (COMPLETE IMPLEMENTATION)

**Required layout (IMPLEMENT EVERYWHERE):**

```
tests/
├── unit/            # Unit tests - isolated components
├── integration/     # Integration tests - cross-service
├── e2e/            # End-to-end tests - complete workflows
├── fixtures/        # Test data and configurations
├── helpers/         # Test utilities and generators
└── conftest.py     # Pytest configuration and shared fixtures
```

**Commands (COMPLETE STRUCTURE):**

```bash
# Create complete test structure - IMPLEMENT ALL
mkdir -p tests/unit tests/integration tests/e2e tests/fixtures tests/helpers
find tests/ -maxdepth 1 -name "test_*.py" -exec mv {} tests/unit/ \; || true
find tests/ -maxdepth 1 -name "*_test.py" -exec mv {} tests/unit/ \; || true

# Create essential test infrastructure files
touch tests/conftest.py tests/helpers/__init__.py tests/fixtures/__init__.py
```

**Import rules in tests, scripts, examples:**
- Use **relative imports** for shared modules within same directory:
  ```python
  from .shared_domain import Users
  ```
- Use **root-level imports** for external FLEXT packages:
  ```python
  from flext_core import FlextResult
  from flext_api import FlextApiClient
  ```

---

## 🛡️ Quality Gates (MANDATORY after EVERY edit)

**CRITICAL: Run on ALL directories - src/, tests/, examples/, scripts/**

### ✅ PEP8 Compliance Validation
```bash
# Lint (0 warnings/errors) - ALL directories:
ruff check src/ --fix
ruff check tests/ --fix
ruff check examples/ --fix  
ruff check scripts/ --fix

# PEP8 naming validation:
if grep -r "class [a-z]" src/ >/dev/null 2>&1; then
  echo "❌ PEP8 violation: class names must be PascalCase"
else
  echo "✅ Class naming compliant"
fi

if grep -r "def [A-Z]" src/ >/dev/null 2>&1; then
  echo "❌ PEP8 violation: function names must be snake_case"
else
  echo "✅ Function naming compliant"
fi

if find src/ -name "*.py" | grep -E "[A-Z]" >/dev/null 2>&1; then
  echo "❌ PEP8 violation: module names must be snake_case"
else
  echo "✅ Module naming compliant"
fi
```

### ✅ flext-core Integration Validation  
```bash
# Verify flext-core base class usage:
if grep -r "class.*Service.*ABC" src/ >/dev/null 2>&1; then
  echo "❌ flext-core violation: use FlextDomainService"
else
  echo "✅ No local ABC services"
fi

if grep -r "class.*Model.*BaseModel" src/ >/dev/null 2>&1; then
  echo "❌ flext-core violation: use FlextModel"
else
  echo "✅ No local BaseModel classes"
fi

if grep -r "from flext_core import.*FlextDomainService" src/ >/dev/null 2>&1; then
  echo "✅ FlextDomainService usage found"
else
  echo "❌ Missing FlextDomainService imports"
fi

# Verify no local base classes:
local_abc_count=$(grep -r "class.*Base.*ABC" src/ --include="*.py" 2>/dev/null | wc -l)
if [ "$local_abc_count" -eq 0 ]; then
  echo "✅ No local abstract base classes"
else
  echo "❌ Found $local_abc_count local ABC classes - use flext-core"
fi

# Verify flext-core protocols usage:
if grep -r "from flext_core import.*FlextProtocols\|FlextService\|FlextRepository\|FlextHandler" src/ >/dev/null 2>&1; then
  echo "✅ Using flext-core protocols"
else
  echo "❌ Missing flext-core protocols usage"
fi

# Verify dependency injection usage:
if grep -r "get_flext_container\|get_logger" src/ >/dev/null 2>&1; then
  echo "✅ Using flext-core utilities"
else
  echo "❌ Missing flext-core DI/logging usage"
fi
```

### ✅ Pydantic V2 Model Validation
```bash
# Verify FlextModel inheritance:
if grep -r "class.*FlextModel" src/ >/dev/null 2>&1; then
  echo "✅ FlextModel inheritance found"
else
  echo "❌ Missing FlextModel inheritance"
fi

# Verify Field usage with validation:
if grep -r "Field.*min_length\|Field.*max_length\|Field.*ge=\|Field.*le=" src/ >/dev/null 2>&1; then
  echo "✅ Pydantic field validation found"
else
  echo "⚠️  Consider adding field validation"
fi

# Verify model_config usage:
if grep -r "model_config.*=" src/ >/dev/null 2>&1; then
  echo "✅ Pydantic v2 configuration found"
else
  echo "⚠️  Consider adding model configuration"
fi

# Check for deprecated Pydantic v1 patterns:
if grep -r "Config.*class" src/ >/dev/null 2>&1; then
  echo "❌ Pydantic violation: use model_config instead of Config class"
else
  echo "✅ No deprecated Config classes"
fi
```

### ✅ SOLID Principles Validation
```bash
# Single Responsibility Principle check:
python -c "
import ast
import glob
for file in glob.glob('src/**/*.py', recursive=True):
    with open(file) as f:
        try:
            tree = ast.parse(f.read())
            classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            if len(classes) > 1:
                print(f'⚠️  SRP: {file} has {len(classes)} classes - consider splitting')
        except: pass
"

# Interface Segregation check:
grep -r "def.*(" src/ | wc -l > /tmp/method_count
echo "Method count per class analysis (ISP compliance):"
python -c "
import ast
import glob
for file in glob.glob('src/**/*.py', recursive=True):
    with open(file) as f:
        try:
            tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [n for n in node.body if isinstance(n, ast.FunctionDef) and not n.name.startswith('_')]
                    if len(methods) > 7:
                        print(f'⚠️  ISP: {file}:{node.name} has {len(methods)} methods - consider interface segregation')
        except: pass
"

# Dependency Inversion check - verify constructor injection:
if grep -r "def __init__.*:" src/ -A3 | grep -E "self\._.*=" | head -5 >/dev/null 2>&1; then
  echo "✅ Constructor injection patterns found"
else
  echo "⚠️  Consider dependency injection patterns"
fi
```

### ✅ Type Safety and Error Handling
```bash
# Types (0 errors) - ALL directories:
mypy src/ --strict --show-error-codes
mypy tests/ --strict --show-error-codes  
mypy examples/ --strict --show-error-codes
mypy scripts/ --strict --show-error-codes

# Alternative type checker:
pyright src/ --strict
pyright tests/ --strict
pyright examples/ --strict  
pyright scripts/ --strict

# FlextResult pattern validation:
if grep -r "FlextResult\[.*\]" src/ >/dev/null 2>&1; then
  echo "✅ FlextResult pattern found"
else
  echo "❌ Missing FlextResult pattern usage"
fi

if grep -r "FlextResult\.ok\|FlextResult\.error" src/ >/dev/null 2>&1; then
  echo "✅ FlextResult factory methods found"
else
  echo "❌ Missing FlextResult factory usage"
fi

# Tests (all green):
pytest tests/ --tb=short -q --maxfail=1

# Import validation:
python -c "import $(find src/ -name '*.py' -path '*/src/*' | head -1 | sed 's|src/||' | sed 's|/__init__.py||' | sed 's|\.py||' | tr '/' '.'); print('✅ Root imports work')"
```

### ✅ Architecture Compliance Summary
```bash
echo "=== FLEXT ARCHITECTURE COMPLIANCE REPORT ==="

# PEP8 validation
if grep -r "class [a-z]\|def [A-Z]" src/ >/dev/null 2>&1; then
  echo "PEP8:       ❌ FAIL (naming violations found)"
else
  echo "PEP8:       ✅ PASS"
fi

# flext-core validation
local_abc_count=$(grep -r "class.*Base.*ABC" src/ --include="*.py" 2>/dev/null | wc -l)
protocols_usage=$(grep -r "from flext_core import.*FlextProtocols\|FlextService\|FlextRepository\|FlextHandler" src/ --include="*.py" 2>/dev/null | wc -l)
if [ "$local_abc_count" -eq 0 ] && [ "$protocols_usage" -gt 0 ]; then
  echo "flext-core:  ✅ PASS"
else
  echo "flext-core:  ❌ FAIL ($local_abc_count local ABC classes, $protocols_usage protocol usages)"
fi

# Pydantic validation
if grep -r "FlextModel\|model_config" src/ >/dev/null 2>&1; then
  echo "Pydantic:   ✅ PASS"
else
  echo "Pydantic:   ❌ FAIL (missing FlextModel usage)"
fi

# SOLID validation (simplified check)
python_file_count=$(find src/ -name "*.py" | wc -l)
if [ "$python_file_count" -gt 0 ]; then
  echo "SOLID:      ✅ PASS (modules found - detailed validation above)"
else
  echo "SOLID:      ❌ FAIL (no Python modules found)"
fi

# Type checking validation
if mypy src/ --strict --show-error-codes >/dev/null 2>&1; then
  echo "Types:      ✅ PASS"
else
  echo "Types:      ❌ FAIL (MyPy errors found)"
fi

# Test validation
if pytest tests/ -q >/dev/null 2>&1; then
  echo "Tests:      ✅ PASS"
else
  echo "Tests:      ❌ FAIL (test failures found)"
fi
```

**ZERO tolerance for failures:**
- Any Ruff error → **fix immediately, do not ignore**
- Any MyPy error → **fix root cause, do not suppress**  
- Any Pyright error → **fix root cause, do not suppress**
- Any test failure → **fix before proceeding**
- PEP8 violations → **rename modules/classes/functions immediately**
- Missing flext-core usage → **replace local implementations immediately**
- Local base classes → **migrate to flext-core immediately**
- Missing Pydantic validation → **add FlextModel inheritance and Field validation**

---

## 🚫 ABSOLUTE PROHIBITIONS (Zero Tolerance)

### ❌ Configuration Changes (NEVER ALLOWED)

**NEVER modify these files without explicit approval:**
- `pyproject.toml` - Dependency definitions and tool configurations
- `ruff.toml` / `.ruff.toml` - Linting rules  
- `mypy.ini` / `setup.cfg` - Type checking configuration
- `pytest.ini` / `conftest.py` - Test configuration
- `.pre-commit-config.yaml` - Pre-commit hooks

### ❌ Error Suppression (FORBIDDEN PRACTICES)

**NEVER use these to hide errors:**
- `# type: ignore` without specific error codes and justification
- `# noqa` without specific rule codes and justification
- `# pylint: disable` 
- `# mypy: ignore-errors`
- `--ignore` flags in commands
- Relaxing strictness settings

### ❌ Anti-Pattern Detection

**Immediate termination offenses:**
- Creating new abstract base classes (use flext-core)
- Local protocols instead of flext-core protocols  
- Non-root imports from flext\_\* (outside same project)
- Implementing logic in facade classes
- Flattening namespace directories under src/
- Adding ignore statements instead of fixing root causes

---

## 🔁 Cross-Project Dependency Rule (MANDATORY)

**When you need functionality from another FLEXT library:**

1. **NEVER reimplement locally** - always reuse existing code
2. **Inspect current working implementation** in upstream project
3. **If upstream is missing/broken** - fix upstream, do not create fallback
4. **Always trace dependencies** to understand full integration

```bash
# Example investigation workflow:
python -c "from flext_core import FlextDomainService; print(FlextDomainService.__module__)"
python -c "from flext_core import get_logger; print(get_logger.__doc__)"
```

**FORBIDDEN responses to missing dependencies:**
- Creating local fallback implementations
- Removing functionality because dependency is "broken"  
- Working around upstream issues instead of fixing them
- Assuming upstream doesn't exist without verification

---

## 📦 `__init__.py` Standardization Rules (MANDATORY COMPLIANCE)

### ✅ CORRECT `__init__.py` Pattern (FLEXT Standard)

**MANDATORY structure for ALL FLEXT projects (Based on flext-core/flext-cli reality):**

```python
"""FLEXT [Project] - [Brief Description]

This module provides [main functionality] following FLEXT architectural patterns.
All exports use wildcard imports from individual modules.

TRUTH DISCOVERED: FLEXT projects actually have 22-40 modules with wildcard imports.
flext-core: 30 modules, flext-cli: 40 modules, flext-plugin: 22+ modules expected.
"""

from __future__ import annotations

# ruff: noqa: F403
# Import all from each module following flext-core pattern
from project_name.__version__ import *
from project_name.api import *
from project_name.client import *
from project_name.config import *
from project_name.constants import *
from project_name.exceptions import *
from project_name.models import *
from project_name.services import *
from project_name.utilities import *

# Note: __all__ is constructed dynamically at runtime from imported modules
# This pattern is necessary for library aggregation but causes pyright warnings
__all__: list[str] = []
```

### ✅ SPECIFIC EXAMPLES by Project Type

#### **flext-cli Project Example (REAL implementation):**
```python
"""FLEXT CLI - CLI Foundation Library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

# ruff: noqa: F403
# Import all from each module following flext-core pattern
from flext_cli.__version__ import *
from flext_cli.api import *
from flext_cli.application_commands import *
from flext_cli.cli import *
from flext_cli.cli_auth import *
from flext_cli.cli_config import *
from flext_cli.cli_mixins import *
from flext_cli.cli_types import *
from flext_cli.cli_utils import *
from flext_cli.client import *
from flext_cli.commands_auth import *
from flext_cli.commands_config import *
from flext_cli.commands_debug import *
from flext_cli.config import *
from flext_cli.config_hierarchical import *
from flext_cli.constants import *
from flext_cli.context import *
from flext_cli.core import *
from flext_cli.core_implementations import *
from flext_cli.decorators import *
from flext_cli.ecosystem_integration import *
from flext_cli.entities import *
from flext_cli.exceptions import *
from flext_cli.flext_api_integration import *
from flext_cli.flext_cli import *
from flext_cli.formatters import *
from flext_cli.foundation import *
from flext_cli.helpers import *
from flext_cli.mixins import *
from flext_cli.models import *
from flext_cli.providers import *
from flext_cli.service_implementations import *
from flext_cli.service_protocols import *
from flext_cli.services import *
from flext_cli.simple_api import *
from flext_cli.utilities import *
from flext_cli.utils_auth import *
from flext_cli.utils_core import *
from flext_cli.utils_output import *

# Note: __all__ is constructed dynamically at runtime from imported modules
# This pattern is necessary for library aggregation but causes pyright warnings
__all__: list[str] = []
```

### ❌ FORBIDDEN `__init__.py` Anti-Patterns

**NEVER use these patterns:**

```python
# ❌ WRONG - Wildcard imports create conflicts
from flext_cli.models import *
from flext_cli.services import *

# ❌ WRONG - Internal module imports  
from flext_cli.internal.hidden import SomeClass
from flext_cli.models.user import UserModel

# ❌ WRONG - Non-root imports from other projects
from flext_core.result import FlextResult
from flext_core.models.base import FlextModel

# ❌ WRONG - Facade imported before main classes
from flext_cli.api import FlextCliApi  # Should be LAST
from flext_cli.client import FlextCliClient

# ❌ WRONG - Logic implementation in __init__.py
def setup_cli():
    # Logic should be in facade or client classes
    pass
```

### ✅ Import Order Rules (MANDATORY)

**STRICT order that MUST be followed:**

1. **Docstring** - Module description with FLEXT branding
2. **Consolidated Classes** - FlextProject[Models|Services|Exceptions|Constants]  
3. **Main Implementation Classes** - FlextProjectClient, FlextProjectConfig, etc.
4. **Utility Classes** - FlextProjectValidators, FlextProjectHelpers, etc.
5. **`__all__` Definition** - Explicit list of public exports
6. **Facade Class** - FlextProjectApi imported LAST with `__all__.append()`

### ✅ Naming Conventions for Exports

**Consolidated Classes (MANDATORY for all projects):**
- `FlextProjectModels` - All data models in single consolidated class
- `FlextProjectServices` - All business services in single consolidated class  
- `FlextProjectExceptions` - All exceptions in single consolidated class
- `FlextProjectConstants` - All constants in single consolidated class

**Main Implementation Classes:**
- `FlextProjectClient` - Main client/implementation class
- `FlextProjectConfig` - Configuration management class
- `FlextProjectContext` - Execution context class (if applicable)

**Utility Classes:**
- `FlextProjectValidators` - Validation logic class
- `FlextProjectHelpers` - Helper functions class
- `FlextProjectFormatters` - Formatting utilities class (if applicable)

**Facade Class (ALWAYS LAST):**
- `FlextProjectApi` - Orchestration facade (no business logic)

### ✅ Validation Commands (MANDATORY after each change)

```bash
# Test basic imports work
python -c "from project_name import FlextProjectClient; print('✅ Main class import works')"

# Test consolidated classes work  
python -c "from project_name import FlextProjectModels; print('✅ Consolidated classes work')"

# Test facade works
python -c "from project_name import FlextProjectApi; print('✅ Facade import works')"

# List all public exports
python -c "import project_name; print('Public exports:', [n for n in dir(project_name) if not n.startswith('_')])"

# Test import performance (should be fast)
time python -c "import project_name"
```


---

## Legacy Compatibility Facade (temporary bridge only)

```bash
# Step 1: copy to new PEP8 name (SMALL change)
cp src/project/base_services.py src/project/service_implementations.py

# Step 2: refactor service_implementations.py incrementally (small steps)
mypy src/project/service_implementations.py --strict

# Step 3: legacy façade (temporary)
cat > src/project/base_services.py <<'PY'
import warnings
from .service_implementations import *
warnings.warn('base_services is deprecated; use service_implementations', DeprecationWarning)
PY

# Step 4: validate façade
python -c "from project.base_services import MyService; print('Facade works')"

# Step 5/6: update imports progressively; remove façade ONLY after 100% validation
```

Cleanup (ONLY after full validation):

```bash
rm src/project/base_services.py
rm src/project/wrapper_*.py.bak
```

---

## 🚫 Anti-Hallucination Protocol (ABSOLUTE)

**NEVER assume — ALWAYS verify:**

```bash
python -c "from flext_core import FlextDomainService; help(FlextDomainService)"
python -c "from flext_core import FlextResult; help(FlextResult)"
find src/ -name "*.py" -exec basename {} .py \; | sort | uniq
grep -r "from flext_core import" src/ || echo "No flext-core imports found"
grep -r "class.*:" src/ | head -10
```

**Immediate termination offenses:**

* New abstract base classes or protocols (use flext-core).
* Local validation in place of `FlextModel`/Pydantic.
* Non-root imports from flext\_\* (outside same project).
* `# TODO` left in production code.
* Temporary scripts/files outside modules.
* Creating directories in `src/`, `scripts/`, `examples/`.
* Implementing logic in facade classes.

---


## 🌐 Language, Docstrings, Comments & Logs (i18n policy)

* **Docstrings**: **Always in English**, PEP8 + Google style, across **all** projects.
* **Comments & Logs**:

  * **client-a** and **client-b**: comments **in Portuguese** and **log messages in Portuguese** (INFO/WARN/ERROR).
  * **All other projects**: comments and logs **in English**.

**client-a/client-b: logging helper example (Portuguese logs):**

```python
from flext_core import get_logger

logger = get_logger(__name__)

def _emit_startup_log() -> None:
    # Comentário em português (client-a/client-b): inicialização do serviço
    logger.info("Serviço iniciado com sucesso.")
    logger.warning("Configuração parcial detectada, verifique as credenciais.")
    logger.error("Falha ao conectar no repositório remoto.")
```

**Docstring example (English, universal):**

```python
class MigrationConfig(FlextModel):
    """Configuration for migrations.

    This model centralizes validation and ensures consistent configuration
    across FLEXT services.

    Attributes:
        input_dir: Path to the input directory.
    """
```

**client-a/client-b class prefixing (recap):**

* Use **`client-aMig*`** for client-a (e.g., `client-aMigAuthClient`, `client-aMigApi`).
* Use **`GruposNosWmsIntOra*`** for client-b (e.g., `GruposNosWmsIntOraOrderService`, `GruposNosWmsIntOraApi`).
* **No `Flext` prefix** in these two projects.
* Facades in these projects **also** follow these prefixes and **must not** contain logic.

---

## 🧪 Quality Enforcement (ABSOLUTE)

### Configuration Protection
* **NEVER modify** `pyproject.toml`, lint configs, test configs
* **ALWAYS** fix root causes instead of relaxing rules
* **VERIFY** all directories (src/, tests/, examples/, scripts/) pass quality gates

### Error Resolution Strategy
1. **Read the actual error message** completely
2. **Understand the root cause** - don't guess
3. **Fix the source problem** - don't suppress symptoms
4. **Verify fix works** with quality gates
5. **Ensure no regressions** in other modules

### Import Structure Integrity
* **Preserve** namespace directories under src/
* **Maintain** `__init__.py` functionality at all times
* **Use** root-level imports for cross-project dependencies
* **Allow** internal imports within same project namespace

---

## 🔄 Execution Workflow (Never Deviate)

### Phase 1: Architecture Analysis (MANDATORY FIRST)
1. **Analyze current state** with comprehensive validation:
   ```bash
   # PEP8 baseline assessment
   find src/ -name "*.py" | grep -E "[A-Z]" | wc -l
   grep -r "class [a-z]" src/ | wc -l
   grep -r "def [A-Z]" src/ | wc -l
   
   # flext-core integration assessment  
   grep -r "class.*Base.*ABC" src/ --include="*.py" | wc -l
   grep -r "from flext_core import" src/ | wc -l
   
   # Pydantic usage assessment
   grep -r "FlextModel\|BaseModel" src/ | wc -l
   grep -r "Field.*(" src/ | wc -l
   
   # SOLID principles assessment
   python -c "
   import ast, glob
   total_classes = sum(len([n for n in ast.walk(ast.parse(open(f).read())) if isinstance(n, ast.ClassDef)]) 
                      for f in glob.glob('src/**/*.py', recursive=True))
   print(f'Total classes: {total_classes}')
   "
   ```

### Phase 2: Single Module Refactoring (ITERATIVE)
1. **Select ONE module** for refactoring (start with smallest/simplest like constants.py, utils.py, typings.py)
2. **Remove legacy files first**:
   ```bash
   # Move legacy files to .bak (DO NOT DELETE)  
   mv src/flext_ldap/services_old.py src/flext_ldap/services_old.py.bak
   mv src/flext_ldap/models_old.py src/flext_ldap/models_old.py.bak
   mv src/flext_ldap/constants_old.py src/flext_ldap/constants_old.py.bak
   mv src/flext_ldap/typings_old.py src/flext_ldap/typings_old.py.bak
   ```
3. **Apply PEP8 naming** if needed:
   ```bash
   # Rename file if needed (snake_case)
   mv src/project/BaseService.py src/project/service_base.py
   ```
3. **Migrate to flext-core patterns**:
   ```bash
   # Replace local base classes with flext-core
   sed -i 's/class.*ABC/FlextDomainService/g' src/project/module.py
   sed -i 's/from abc import ABC/from flext_core import FlextDomainService/g' src/project/module.py
   ```
4. **Create CONSOLIDATED classes (FlextProjectExceptions, FlextProjectModels, etc.)**:
   ```bash
   # Create single CONSOLIDATED class per module following FLEXT pattern
   # Example: consolidate all exceptions into FlextPluginExceptions class
   # Example: consolidate all models into FlextPluginModels class  
   # Example: consolidate all constants into FlextPluginConstants class
   # Example: consolidate all services into FlextPluginServices class
   # MAINTAIN backward compatibility with property re-exports and __init__.py imports
   ```
5. **Add Pydantic validation**:
   ```bash
   # Replace BaseModel with FlextModel
   sed -i 's/BaseModel/FlextModel/g' src/project/module.py
   sed -i 's/from pydantic import BaseModel/from flext_core import FlextModel/g' src/project/module.py
   ```
6. **Run comprehensive validation AFTER EACH MODULE**:
   ```bash
   # MANDATORY validation after each module
   echo "=== VALIDATING MODULE: src/project/module.py ==="
   ruff check src/project/module.py --fix
   mypy src/project/module.py --strict
   python -c "from project.module import ClassName; print('✅ Import works')"
   ```

### Phase 3: Integration Validation (AFTER EACH MODULE)
1. **Verify all imports still work**:
   ```bash
   python -c "import project_namespace; print('✅ Root imports work')"
   ```
2. **Run full quality gates**:
   ```bash
   # PEP8 compliance check
   grep -r "class [a-z]\|def [A-Z]" src/ && echo "❌ PEP8 violations found" || echo "✅ PEP8 compliant"
   
   # flext-core compliance check  
   grep -r "class.*Base.*ABC" src/ --include="*.py" | wc -l | grep -q "^0$" && echo "✅ flext-core compliant" || echo "❌ Local base classes found"
   
   # Pydantic compliance check
   grep -r "BaseModel" src/ | grep -v "FlextModel" && echo "❌ Direct BaseModel usage found" || echo "✅ Pydantic compliant"
   
   # Full test suite
   pytest tests/ -q --tb=short --maxfail=1
   ```

### Phase 4: SOLID Principles Refinement (ONGOING)
1. **Single Responsibility validation**:
   ```bash
   python -c "
   import ast, glob
   for file in glob.glob('src/**/*.py', recursive=True):
       with open(file) as f:
           tree = ast.parse(f.read())
           classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
           if len(classes) > 1:
               print(f'⚠️  {file}: {len(classes)} classes - consider SRP compliance')
   "
   ```
2. **Interface Segregation validation**:
   ```bash
   python -c "
   import ast, glob
   for file in glob.glob('src/**/*.py', recursive=True):
       with open(file) as f:
           tree = ast.parse(f.read())
           for node in ast.walk(tree):
               if isinstance(node, ast.ClassDef):
                   methods = [n for n in node.body if isinstance(n, ast.FunctionDef) and not n.name.startswith('_')]
                   if len(methods) > 7:
                       print(f'⚠️  {file}:{node.name}: {len(methods)} methods - consider ISP')
   "
   ```

### Phase 5: Final Architecture Validation (COMPLETION)
1. **Run complete compliance report**:
   ```bash
   echo "=== FINAL FLEXT ARCHITECTURE COMPLIANCE REPORT ==="
   echo "PEP8:       $(grep -r "class [a-z]\|def [A-Z]" src/ &>/dev/null && echo "❌ FAIL" || echo "✅ PASS")"
   echo "flext-core: $(grep -r "class.*Base.*ABC" src/ --include="*.py" | wc -l | grep -q "^0$" && grep -r "from flext_core import.*FlextProtocols\|FlextService\|FlextRepository\|FlextHandler" src/ --include="*.py" >/dev/null 2>&1 && echo "✅ PASS" || echo "❌ FAIL")"
   echo "Pydantic:   $(grep -r "FlextModel" src/ &>/dev/null && echo "✅ PASS" || echo "❌ FAIL")"
   echo "SOLID:      ✅ PASS (verified per-module)"
   echo "Types:      $(mypy src/ --strict --show-error-codes &>/dev/null && echo "✅ PASS" || echo "❌ FAIL")"
   echo "Tests:      $(pytest tests/ -q &>/dev/null && echo "✅ PASS" || echo "❌ FAIL")"
   echo "Imports:    $(python -c 'import $(find src/ -name "__init__.py" | head -1 | sed "s|src/||" | sed "s|/__init__.py||" | tr "/" ".")' &>/dev/null && echo "✅ PASS" || echo "❌ FAIL")"
   ```

**CRITICAL RULES:**
- **One module at a time** → validate → proceed
- **Never skip validation** between modules  
- **Fix all errors immediately** - do not accumulate technical debt
- **Preserve functionality** - imports must always work
- **Document changes** in TODO list with validation results
- **No parallel work** - finish current before starting next
- **Preserve** `__init__.py` imports throughout all changes

---

## ✅ Success Criteria (Measurable - ENHANCED FOR PEP8/flext-core/Pydantic/SOLID)

### 🎯 PEP8 Compliance Criteria
* **0 PEP8 naming violations**: All modules snake_case, classes PascalCase, functions snake_case
* **100% module structure compliance**: Single class per module with descriptive names
* **0 style violations**: All code passes `ruff check` without warnings

**Validation Commands:**
```bash
find src/ -name "*.py" | grep -E "[A-Z]" | wc -l  # Should be 0
grep -r "class [a-z]" src/ | wc -l                # Should be 0  
grep -r "def [A-Z]" src/ | wc -l                  # Should be 0
```

### 🏗️ flext-core Integration Criteria
* **0 local abstract base classes**: All services inherit from FlextDomainService
* **0 local model classes**: All models inherit from FlextModel (Pydantic-based)
* **100% flext-core utilities usage**: get_logger(), get_flext_container() everywhere
* **0 duplicate implementations**: All functionality delegates to flext-core

**Validation Commands:**
```bash
grep -r "class.*Base.*ABC" src/ --include="*.py" | wc -l     # Should be 0
grep -r "BaseModel" src/ | grep -v "FlextModel" | wc -l      # Should be 0
grep -r "from flext_core import FlextDomainService" src/ | wc -l  # Should be > 0
grep -r "from flext_core import.*FlextProtocols\|FlextService\|FlextRepository\|FlextHandler" src/ --include="*.py" | wc -l  # Should be > 0
```

### 📊 Pydantic V2 Integration Criteria  
* **100% FlextModel inheritance**: All data models use FlextModel base class
* **Comprehensive field validation**: All models use Field() with appropriate constraints
* **Modern Pydantic v2 patterns**: model_config instead of Config class
* **FlextResult integration**: All validation returns FlextResult[Model]

**Validation Commands:**
```bash
grep -r "class.*FlextModel" src/ | wc -l                     # Should be > 0
grep -r "Field.*min_length\|Field.*ge=" src/ | wc -l         # Should be > 0
grep -r "model_config.*=" src/ | wc -l                       # Should be > 0
grep -r "Config.*class" src/ | wc -l                         # Should be 0
```

### ⚖️ SOLID Principles Criteria
* **Single Responsibility**: One class per module, focused responsibilities
* **Open/Closed**: Extension via composition, not modification
* **Liskov Substitution**: Subtypes are substitutable for base types  
* **Interface Segregation**: Small, focused interfaces (< 7 methods per interface)
* **Dependency Inversion**: Constructor injection of abstract dependencies

**Validation Commands:**
```bash
python -c "
import ast, glob
violations = []
for file in glob.glob('src/**/*.py', recursive=True):
    with open(file) as f:
        tree = ast.parse(f.read())
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        if len(classes) > 1:
            violations.append(f'{file}: {len(classes)} classes')
print(f'SRP violations: {len(violations)}')  # Should be 0
"
```

### 🔧 Quality Gates Criteria
* **0 Ruff warnings/errors** in src/, tests/, examples/, scripts/
* **0 MyPy errors (strict)** in all directories  
* **0 Pyright errors** in all directories
* **100% test pass rate**: All tests pass without failures
* **100% import functionality**: All `__init__.py` imports work correctly

### 🔗 Integration Criteria
* **flext-core patterns everywhere**: No local replacements
* **Root-level imports only**: No internal imports from other flext_* projects
* **Legacy facades removed**: All temporary compatibility bridges cleaned up
* **Namespace preservation**: All src/namespace/ directories maintained

---

## 🚨 CRITICAL REMINDERS

**NEVER, NEVER, NEVER:**
- Write reports, scripts, tests, or automatic fixes
- Remove code because library is "inaccessible" or "failing"
- Create fallback implementations instead of fixing upstream
- Modify configuration files without explicit approval
- Use ignore statements to hide errors instead of fixing root causes

**ALWAYS:**
- Consult and correct upstream issues
- Fix root causes, not symptoms
- Preserve namespace structure under src/
- Use flext-core as the single source of truth
- Validate with quality gates after every change
