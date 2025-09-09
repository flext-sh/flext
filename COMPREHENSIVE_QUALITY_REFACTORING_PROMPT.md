# COMPREHENSIVE QUALITY REFACTORING PROMPT FOR FLEXT ECOSYSTEM

**Enterprise-Grade Quality Assurance & Refactoring Guidelines**
**Version**: 2.1.0 | **Authority**: WORKSPACE | **Updated**: 2025-01-08
**Environment**: `/home/marlonsc/flext/.venv/bin/python` (No PYTHONPATH required)
**Based on**: flext-core 0.9.0 with 79% test coverage (PROVEN FOUNDATION)

---

## 🎯 MISSION STATEMENT (NON-NEGOTIABLE)

**OBJECTIVE**: Achieve 100% professional quality compliance across the FLEXT ecosystem with zero regressions, following SOLID principles, Python 3.13+ standards, Pydantic best practices, and flext-core foundation patterns.

**CRITICAL REQUIREMENTS**:
- ✅ **95%+ pytest pass rate** with **75%+ coverage** (flext-core proven achievable at 79%)
- ✅ **Zero errors** in ruff, mypy (strict mode), and pyright across ALL source code
- ✅ **Unified classes per module** - single responsibility, no aliases, no wrappers, no helpers
- ✅ **Direct flext-core integration** - eliminate complexity, reduce configuration overhead
- ✅ **MANDATORY flext-cli usage** - ALL CLI projects use flext-cli for CLI AND output, NO direct Click/Rich
- ✅ **ZERO fallback tolerance** - no try/except fallbacks, no workarounds, always correct solutions
- ✅ **SOLID compliance** - proper abstraction, dependency injection, clean architecture
- ✅ **Professional English** - all docstrings, comments, variable names, function names
- ✅ **Incremental refactoring** - never rewrite entire modules, always step-by-step improvements
- ✅ **Real functional tests** - minimal mocks, test actual functionality with real environments
- ✅ **Production-ready code** - no workarounds, fallbacks, try-pass blocks, or incomplete implementations

**CURRENT ECOSYSTEM STATUS** (Evidence-based):
- 🔴 **Ruff Issues**: 1,704 violations (772 import issues, 233 undefined names)
- 🟡 **MyPy Issues**: 0 in main src/ (already compliant)
- 🟡 **Pyright Issues**: 4 errors (mostly minor API mismatches)
- 🔴 **Pytest Status**: 5 errors, 27 passed (test infrastructure needs fixing)
- 🟢 **flext-core Foundation**: 79% coverage, fully functional API

---

## 🚨 ABSOLUTE PROHIBITIONS (ZERO TOLERANCE)

### ❌ FORBIDDEN PRACTICES

1. **CODE QUALITY VIOLATIONS**:
   - Any use of `# type: ignore` without specific error codes
   - Any use of `Any` types instead of proper type annotations
   - Silencing errors with ignore hints instead of fixing root causes
   - Creating wrappers, aliases, or compatibility facades
   - Using sed, awk, or automated scripts for complex refactoring

2. **ARCHITECTURE VIOLATIONS**:
   - Multiple classes per module (use single unified class per module)
   - Helper functions or constants outside of unified classes
   - Local reimplementation of flext-core functionality
   - Creating new modules instead of refactoring existing ones
   - Changing lint, type checker, or test framework behavior

3. **CLI PROJECT VIOLATIONS** (ABSOLUTE ZERO TOLERANCE):
   - **MANDATORY**: ALL CLI projects MUST use `flext-cli` exclusively for CLI functionality AND data output
   - **FORBIDDEN**: Direct `import click` in any project code
   - **FORBIDDEN**: Direct `import rich` in any project code for output/formatting
   - **FORBIDDEN**: Local CLI implementations bypassing flext-cli
   - **FORBIDDEN**: Any CLI functionality not going through flext-cli layer
   - **REQUIRED**: If flext-cli lacks functionality, IMPROVE flext-cli first - NEVER work around
   - **PRINCIPLE**: Fix the foundation, don't work around it
   - **OUTPUT RULE**: ALL data output, formatting, tables, progress bars MUST use flext-cli wrappers
   - **NO EXCEPTIONS**: Even if flext-cli needs improvement, IMPROVE it, don't bypass it

4. **FALLBACK/WORKAROUND VIOLATIONS** (ABSOLUTE PROHIBITION):
   - **FORBIDDEN**: `try/except` blocks as fallback mechanisms
   - **FORBIDDEN**: Palliative solutions that mask root problems
   - **FORBIDDEN**: Temporary workarounds that become permanent
   - **FORBIDDEN**: "Good enough" solutions instead of correct solutions
   - **REQUIRED**: Always implement the correct solution, never approximate

5. **TESTING VIOLATIONS**:
   - Using excessive mocks instead of real functional tests
   - Accepting test failures and continuing development
   - Creating fake or placeholder test implementations
   - Testing code that doesn't actually execute real functionality

6. **DEVELOPMENT VIOLATIONS**:
   - Rewriting entire modules instead of incremental improvements
   - Skipping quality gates (ruff, mypy, pyright, pytest)
   - Modifying behavior of linting tools instead of fixing code
   - Rolling back git versions instead of fixing forward

---

## 🏗️ ARCHITECTURAL FOUNDATION (MANDATORY PATTERNS)

### Core Integration Strategy

**PRIMARY FOUNDATION**: `flext-core` contains ALL base patterns - use exclusively, never reimplement locally

```python
# ✅ CORRECT - Direct usage of flext-core foundation (VERIFIED API)
from flext_core import (
    FlextResult,           # Railway pattern - has .data, .value, .unwrap()
    FlextModels,           # Pydantic models - Entity, Value, AggregateRoot classes
    FlextDomainService,    # Base service - Pydantic-based with Generic[T]
    FlextContainer,        # Dependency injection - use .get_global()
    FlextLogger,           # Structured logging - direct instantiation
    FlextConstants,        # System constants
    FlextExceptions        # Exception hierarchy
)

# ✅ MANDATORY - For ALL CLI projects use flext-cli exclusively
from flext_cli import (
    FlextCliApi,           # High-level CLI API for programmatic access
    FlextCliMain,          # Main CLI entry point and command registration
    FlextCliConfig,        # Configuration management for CLI
    FlextCliConstants,     # CLI-specific constants
    # NEVER import click or rich directly - ALL CLI + OUTPUT through flext-cli
)

# ❌ ABSOLUTELY FORBIDDEN - These imports are ZERO TOLERANCE violations
# import click           # FORBIDDEN - use flext-cli
# import rich            # FORBIDDEN - use flext-cli output wrappers
# from rich.console import Console  # FORBIDDEN - use flext-cli
# from rich.table import Table      # FORBIDDEN - use flext-cli
# from rich.progress import Progress # FORBIDDEN - use flext-cli

# VERIFIED: flext-core API signatures (tested against actual code v0.9.0)
# - FlextResult[T].ok(value) -> creates success result
# - FlextResult[T].fail(error) -> creates failure result  
# - result.is_success -> boolean property
# - result.data -> access value (legacy compatibility)
# - result.value -> access value (preferred)
# - result.unwrap() -> extract value safely
# - FlextContainer.get_global() -> FlextContainer singleton (NO WRAPPER FUNCTIONS)
# - FlextLogger(name) -> direct instantiation (NO get_logger wrapper)

# ✅ CORRECT - Unified class per module pattern (VERIFIED WORKING)
class UnifiedProjectService(FlextDomainService):
    """Single unified service class following flext-core patterns.
    
    This class consolidates all project-related operations,
    following the single responsibility principle while
    maintaining a unified interface.
    
    Note: FlextDomainService is Pydantic-based, inherits from BaseModel
    """
    
    def __init__(self, **data) -> None:
        """Initialize service with proper dependency injection.
        
        Args:
            **data: Pydantic initialization data (FlextDomainService requirement)
        """
        super().__init__(**data)
        # Use direct class access - NO wrapper functions (per updated flext-core)
        self._container = FlextContainer.get_global()
        self._logger = FlextLogger(__name__)
    
    def process_data(self, input_data: dict) -> FlextResult[ProjectData]:
        """Process input data with proper error handling.
        
        Returns:
            FlextResult with .data/.value access and .unwrap() method
        """
        # Input validation - NO fallbacks, fail fast with clear errors
        if not input_data:
            return FlextResult[ProjectData].fail("Input data cannot be empty")
            
        if not isinstance(input_data, dict):
            return FlextResult[ProjectData].fail(f"Expected dict, got {type(input_data)}")
            
        # Transform to domain model - NO try/except fallbacks
        validation_result = ProjectData.model_validate(input_data)
        if isinstance(validation_result, ValidationError):
            return FlextResult[ProjectData].fail(f"Validation failed: {validation_result}")
            
        return FlextResult[ProjectData].ok(validation_result)
    
    def _validate_input(self, data: dict) -> FlextResult[dict]:
        """Validate input data structure."""
        if not data:
            return FlextResult[dict].fail("Empty data not allowed")
        return FlextResult[dict].ok(data)
    
    def _transform_data(self, data: dict) -> FlextResult[ProjectData]:
        """Transform validated data to domain model."""
        try:
            model = ProjectData.model_validate(data)
            return FlextResult[ProjectData].ok(model)
        except ValidationError as e:
            return FlextResult[ProjectData].fail(f"Validation error: {e}")
    
    def _enrich_data(self, data: ProjectData) -> ProjectData:
        """Enrich data with additional context."""
        # Implementation details...
        return data

# ✅ CORRECT - Module exports
__all__ = ["UnifiedProjectService"]
```

### Domain Modeling with VERIFIED flext-core Patterns

```python
# ✅ CORRECT - Using VERIFIED flext-core API patterns
from flext_core import FlextModels, FlextResult

# Domain models - inherit from verified FlextModels classes
class ProjectData(FlextModels.Entity):
    """Project entity with business rules validation."""
    
    name: str
    description: str
    
    def validate_business_rules(self) -> FlextResult[None]:
        """Required abstract method implementation."""
        if not self.name.strip():
            return FlextResult[None].fail("Project name cannot be empty")
        return FlextResult[None].ok(None)

class ProjectEmail(FlextModels.Value):
    """Project email value object."""
    
    address: str
    
    def validate_business_rules(self) -> FlextResult[None]:
        """Required abstract method implementation."""
        if "@" not in self.address:
            return FlextResult[None].fail("Invalid email address")
        return FlextResult[None].ok(None)

# Application services with dependency injection
class ApplicationService:
    """Service using proper dependency injection patterns."""
    
    def __init__(self) -> None:
        # Use direct class access - NO wrapper functions
        self._container = FlextContainer.get_global()
        
    def get_database(self) -> FlextResult[DatabaseService]:
        """Get database service from container.
        
        Returns:
            FlextResult containing service or error message
        """
        # Container.get returns FlextResult automatically
        return self._container.get("database_service")
    
    def register_services(self) -> FlextResult[None]:
        """Register all required services - NO fallbacks, proper error handling."""
        # Get container - if this fails, system is fundamentally broken
        container = FlextContainer.get_global()
        
        # Register services - each registration returns FlextResult
        db_result = container.register("database_service", DatabaseService())
        if db_result.is_failure:
            return FlextResult[None].fail(f"Database service registration failed: {db_result.error}")
            
        cache_result = container.register("cache_service", CacheService())  
        if cache_result.is_failure:
            return FlextResult[None].fail(f"Cache service registration failed: {cache_result.error}")
            
        return FlextResult[None].ok(None)
```

### CLI Development Patterns (MANDATORY FOR ALL CLI PROJECTS)

#### 🔧 UNIVERSAL CLI CONFIGURATION SYSTEM (MANDATORY FOR ALL PROJECTS)

**CRITICAL PRINCIPLE**: ALL projects using CLI MUST implement the universal configuration system through flext-cli + flext-core foundation. NO manual configuration loading allowed - everything is handled automatically by the FLEXT ecosystem.

**MANDATORY DEPENDENCIES** (ZERO TOLERANCE - ALWAYS INSTALLED):
```python
# ✅ MANDATORY - These libraries MUST ALWAYS be installed in supported versions
python-dotenv>=1.0.0    # MANDATORY - NEVER optional, ALWAYS available
pydantic>=2.0.0         # MANDATORY - Configuration validation
click>=8.0.0            # MANDATORY - CLI framework integration
toml>=0.10.0            # MANDATORY - TOML configuration support  
pyyaml>=6.0.0           # MANDATORY - YAML configuration support

# ❌ ABSOLUTELY FORBIDDEN - Optional dependencies or version flexibility
# python-dotenv  # FORBIDDEN - No version range flexibility
# Optional[dotenv]  # FORBIDDEN - Never optional
```

**UNIVERSAL CONFIGURATION PRIORITY ORDER** (ALL PROJECTS):
```
1. ENVIRONMENT VARIABLES  (export DATABASE_HOST=prod - HIGHEST PRIORITY)
2. CONFIGURATION FILE     (customizable: .env, .toml, .json, .yaml)
3. DEFAULT CONSTANTS      (hardcoded in project source)
4. CLI PARAMETERS         (runtime overrides: --host, --port, etc.)
```

**CONFIGURABLE FILE DETECTION SYSTEM**:
```python
# ✅ CORRECT - Projects can specify configuration file format and location
class ProjectCliConfiguration:
    """Universal CLI configuration - customizable per project."""
    
    # Project specifies configuration file preferences
    config_file_options = [
        {"format": "env", "filename": ".env", "priority": 1},           # Default: .env
        {"format": "toml", "filename": "config.toml", "priority": 2},   # Alternative: TOML
        {"format": "yaml", "filename": "config.yaml", "priority": 3},   # Alternative: YAML  
        {"format": "json", "filename": "config.json", "priority": 4},   # Alternative: JSON
    ]
    
    # CLI can override configuration file selection
    def __init__(self):
        self._cli_api = FlextCliApi()
        self._config = FlextCliConfig(
            config_file_options=self.config_file_options,
            auto_detection=True,  # Scan current directory for supported formats
            mandatory_dotenv=True  # python-dotenv ALWAYS available
        )
```

**CLI CONFIGURATION FILE CONTROL** (UNIVERSAL PATTERN):
```bash
# ✅ CORRECT - CLI can specify configuration file and format
python -m project_name --config-file custom.env --config-format env command
python -m project_name --config-file settings.toml --config-format toml command  
python -m project_name --config-file config.yaml --config-format yaml command
python -m project_name --config-file app.json --config-format json command

# ✅ CORRECT - Auto-detection in current directory (priority order)
cd /work/project && python -m project_name command
# Scans: .env (priority 1) → config.toml (priority 2) → config.yaml (priority 3) → config.json (priority 4)

# ✅ CORRECT - Environment variables ALWAYS take precedence
export DATABASE_HOST=production-db
python -m project_name --config-file local.env command  # Uses production-db (ENV var)
```

**MANDATORY LIBRARY COMPLIANCE** (ZERO EXCEPTIONS):
```python
# ✅ MANDATORY - ALL libraries MUST be present in exact supported versions
import os
from pathlib import Path

def validate_mandatory_dependencies() -> FlextResult[None]:
    """Validate ALL mandatory dependencies are installed - NO EXCEPTIONS."""
    
    # MANDATORY: python-dotenv MUST be available
    try:
        import dotenv
        dotenv_version = dotenv.__version__
        if not dotenv_version.startswith(('1.0', '1.1', '1.2')):
            return FlextResult[None].fail(f"python-dotenv version {dotenv_version} not supported")
    except ImportError:
        return FlextResult[None].fail("python-dotenv MANDATORY dependency missing - ZERO TOLERANCE")
    
    # MANDATORY: All configuration format libraries MUST be available
    mandatory_libs = {
        'pydantic': '2.0',
        'click': '8.0', 
        'toml': '0.10',
        'yaml': '6.0'
    }
    
    for lib_name, min_version in mandatory_libs.items():
        try:
            lib = __import__(lib_name)
            if hasattr(lib, '__version__') and lib.__version__ < min_version:
                return FlextResult[None].fail(f"{lib_name} version {lib.__version__} below required {min_version}")
        except ImportError:
            return FlextResult[None].fail(f"{lib_name} MANDATORY dependency missing - ZERO TOLERANCE")
    
    return FlextResult[None].ok(None)

# ❌ ABSOLUTELY FORBIDDEN - Optional dependency patterns
def forbidden_optional_patterns():
    """These patterns are ABSOLUTELY FORBIDDEN."""
    
    # ❌ FORBIDDEN: Optional imports
    # try:
    #     import dotenv
    # except ImportError:
    #     dotenv = None  # FORBIDDEN - dotenv MUST always be available
    
    # ❌ FORBIDDEN: Version flexibility
    # if dotenv and hasattr(dotenv, 'load_dotenv'):  # FORBIDDEN - assume it's there
    
    # ❌ FORBIDDEN: Graceful degradation
    # config = load_env_if_available()  # FORBIDDEN - always load, never optional
```

```python
# ✅ CORRECT - ALL CLI projects MUST use flext-cli exclusively
from flext_cli import FlextCliApi, FlextCliMain, FlextCliConfig
# ❌ FORBIDDEN - NEVER import click directly
# import click  # THIS IS ABSOLUTELY FORBIDDEN

class ProjectCliService:
    """CLI service using flext-cli foundation - NO Click imports allowed.
    
    CONFIGURATION AUTHORITY: 
    - flext-cli automatically loads .env from execution root
    - flext-core provides configuration infrastructure
    - Project ONLY describes configuration schema, never loads manually
    """
    
    def __init__(self) -> None:
        """Initialize CLI service with automatic configuration loading."""
        # ✅ AUTOMATIC: Configuration loaded transparently by flext-cli/flext-core
        self._cli_api = FlextCliApi()
        self._config = FlextCliConfig()  # Automatically includes .env + defaults + CLI params
        
        # ✅ CORRECT: Access configuration through flext-cli API
        # NO manual .env loading, NO custom configuration logic
        
    def define_universal_configuration_schema(self) -> FlextResult[dict]:
        """Define universal configuration schema for ALL projects.
        
        Project ONLY describes configuration needs - flext-cli handles:
        1. Multi-format file detection (.env, .toml, .yaml, .json)
        2. Environment variable precedence 
        3. Default constants fallback
        4. CLI parameter overrides
        5. Automatic validation and type conversion
        """
        # ✅ CORRECT: Universal schema pattern for ALL FLEXT projects
        universal_config_schema = {
            # Database configuration (common to most projects)
            "database": {
                "host": {
                    "default": "localhost",              # Level 3: DEFAULT CONSTANTS  
                    "env_var": "DATABASE_HOST",          # Levels 1&2: ENV VARS → CONFIG FILE
                    "cli_param": "--db-host",            # Level 4: CLI PARAMETERS
                    "config_formats": {                  # Multi-format support
                        "env": "DATABASE_HOST",
                        "toml": "database.host",
                        "yaml": "database.host", 
                        "json": "database.host"
                    },
                    "type": str,
                    "required": True
                },
                "port": {
                    "default": 5432,                     # Level 3: DEFAULT CONSTANTS
                    "env_var": "DATABASE_PORT",          # Levels 1&2: ENV VARS → CONFIG FILE
                    "cli_param": "--db-port",            # Level 4: CLI PARAMETERS
                    "config_formats": {
                        "env": "DATABASE_PORT",
                        "toml": "database.port",
                        "yaml": "database.port",
                        "json": "database.port"
                    },
                    "type": int,
                    "required": False
                },
                "credentials": {
                    "username": {
                        "default": "app_user",           # Level 3: DEFAULT CONSTANTS
                        "env_var": "DATABASE_USERNAME",  # Levels 1&2: ENV VARS → CONFIG FILE
                        "cli_param": "--db-user",        # Level 4: CLI PARAMETERS
                        "config_formats": {
                            "env": "DATABASE_USERNAME",
                            "toml": "database.credentials.username",
                            "yaml": "database.credentials.username",
                            "json": "database.credentials.username"
                        },
                        "type": str,
                        "required": True
                    },
                    "password": {
                        "default": None,                 # Level 3: No default for security
                        "env_var": "DATABASE_PASSWORD",  # Levels 1&2: ENV VARS → CONFIG FILE
                        "cli_param": "--db-password",    # Level 4: CLI PARAMETERS (discouraged)
                        "config_formats": {
                            "env": "DATABASE_PASSWORD",
                            "toml": "database.credentials.password",
                            "yaml": "database.credentials.password",
                            "json": "database.credentials.password"
                        },
                        "type": str,
                        "required": True,
                        "sensitive": True                # Mark as sensitive data
                    }
                }
            },
            # Application configuration (universal patterns)
            "application": {
                "environment": {
                    "default": "development",            # Level 3: DEFAULT CONSTANTS
                    "env_var": "APP_ENVIRONMENT",        # Levels 1&2: ENV VARS → CONFIG FILE
                    "cli_param": "--environment",        # Level 4: CLI PARAMETERS
                    "config_formats": {
                        "env": "APP_ENVIRONMENT",
                        "toml": "application.environment",
                        "yaml": "application.environment",
                        "json": "application.environment"
                    },
                    "type": str,
                    "choices": ["development", "staging", "production"],
                    "required": True
                },
                "debug_mode": {
                    "default": False,                    # Level 3: DEFAULT CONSTANTS
                    "env_var": "APP_DEBUG",              # Levels 1&2: ENV VARS → CONFIG FILE
                    "cli_param": "--debug",              # Level 4: CLI PARAMETERS
                    "config_formats": {
                        "env": "APP_DEBUG",
                        "toml": "application.debug_mode",
                        "yaml": "application.debug_mode",
                        "json": "application.debug_mode"
                    },
                    "type": bool,
                    "required": False
                }
            },
            # Logging configuration (standard pattern)
            "logging": {
                "level": {
                    "default": "INFO",                   # Level 3: DEFAULT CONSTANTS
                    "env_var": "LOG_LEVEL",              # Levels 1&2: ENV VARS → CONFIG FILE
                    "cli_param": "--log-level",          # Level 4: CLI PARAMETERS
                    "config_formats": {
                        "env": "LOG_LEVEL",
                        "toml": "logging.level",
                        "yaml": "logging.level",
                        "json": "logging.level"
                    },
                    "type": str,
                    "choices": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                    "required": False
                },
                "format": {
                    "default": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    "env_var": "LOG_FORMAT",
                    "cli_param": "--log-format",
                    "config_formats": {
                        "env": "LOG_FORMAT",
                        "toml": "logging.format",
                        "yaml": "logging.format", 
                        "json": "logging.format"
                    },
                    "type": str,
                    "required": False
                }
            }
        }
        
        # Register universal schema with flext-cli - handles ALL formats automatically
        schema_result = self._config.register_universal_schema(universal_config_schema)
        if schema_result.is_failure:
            return FlextResult[dict].fail(f"Universal schema registration failed: {schema_result.error}")
            
        return FlextResult[dict].ok(universal_config_schema)
    
    def get_configuration_value(self, key: str) -> FlextResult[str]:
        """Access configuration through automatic hierarchy - NO manual .env logic.
        
        This demonstrates how to access configuration values that are automatically
        resolved through the DEFAULT -> .env -> CLI priority hierarchy.
        """
        # ✅ CORRECT: Get value through flext-cli configuration API
        # This automatically follows the priority hierarchy:
        # 1. ENVIRONMENT VARIABLES -> 2. .env FILE -> 3. DEFAULT CONSTANTS -> 4. CLI PARAMETERS
        value_result = self._config.get_value(key)
        if value_result.is_failure:
            return FlextResult[str].fail(f"Configuration value '{key}' not found: {value_result.error}")
            
        return FlextResult[str].ok(value_result.unwrap())
        
    def demonstrate_automatic_configuration_access(self) -> FlextResult[dict]:
        """Demonstrate accessing configuration values through automatic hierarchy."""
        config_values = {}
        
        # Access database configuration (resolved automatically)
        db_host_result = self.get_configuration_value("database.host")
        if db_host_result.is_success:
            config_values["db_host"] = db_host_result.unwrap()
            
        db_port_result = self.get_configuration_value("database.port") 
        if db_port_result.is_success:
            config_values["db_port"] = db_port_result.unwrap()
            
        # Access logging configuration (resolved automatically)
        log_level_result = self.get_configuration_value("logging.level")
        if log_level_result.is_success:
            config_values["log_level"] = log_level_result.unwrap()
            
        return FlextResult[dict].ok(config_values)
        
    def create_cli_interface(self) -> FlextResult[FlextCliMain]:
        """Create CLI interface using flext-cli patterns.
        
        This method demonstrates proper CLI creation without Click imports.
        If flext-cli lacks functionality, IMPROVE flext-cli, don't work around it.
        """
        # Initialize main CLI handler
        main_cli = FlextCliMain(
            name="project-cli",
            description="Project CLI using flext-cli foundation"
        )
        
        # Register command groups through flext-cli
        auth_result = main_cli.register_command_group("auth", self._create_auth_commands)
        if auth_result.is_failure:
            return FlextResult[FlextCliMain].fail(f"Auth commands registration failed: {auth_result.error}")
            
        config_result = main_cli.register_command_group("config", self._create_config_commands)  
        if config_result.is_failure:
            return FlextResult[FlextCliMain].fail(f"Config commands registration failed: {config_result.error}")
            
        return FlextResult[FlextCliMain].ok(main_cli)
    
    def _create_auth_commands(self) -> FlextResult[dict]:
        """Create authentication commands using flext-cli patterns."""
        # Use flext-cli command builders, NEVER Click decorators OR Rich output
        commands = {
            "login": self._cli_api.create_command(
                name="login",
                description="Authenticate user",
                handler=self._handle_login,
                arguments=["username", "password"],
                output_format="table"  # Use flext-cli output formatting
            ),
            "logout": self._cli_api.create_command(
                name="logout", 
                description="Sign out user",
                handler=self._handle_logout,
                output_format="json"   # Use flext-cli output formatting
            )
        }
        return FlextResult[dict].ok(commands)
    
    def _handle_data_display(self, data: dict) -> FlextResult[str]:
        """Handle data display using flext-cli output wrappers."""
        # ✅ CORRECT - Use flext-cli for ALL output formatting
        output_result = self._cli_api.format_output(
            data=data,
            format_type="table",        # flext-cli handles table formatting
            headers=["Name", "Value"],
            style="default"             # flext-cli handles styling
        )
        
        if output_result.is_failure:
            return FlextResult[str].fail(f"Output formatting failed: {output_result.error}")
            
        # Display using flext-cli display methods
        display_result = self._cli_api.display_output(output_result.unwrap())
        if display_result.is_failure:
            return FlextResult[str].fail(f"Display failed: {display_result.error}")
            
        return FlextResult[str].ok("Data displayed successfully")
    
    def _show_progress_bar(self, task_name: str, total: int) -> FlextResult[None]:
        """Show progress bar using flext-cli progress wrappers."""
        # ✅ CORRECT - Use flext-cli progress bars, NEVER Rich directly
        progress_result = self._cli_api.create_progress_bar(
            task_name=task_name,
            total=total,
            style="default"  # flext-cli handles progress bar styling
        )
        
        if progress_result.is_failure:
            return FlextResult[None].fail(f"Progress bar creation failed: {progress_result.error}")
            
        progress_bar = progress_result.unwrap()
        
        # Update progress through flext-cli
        for i in range(total):
            update_result = progress_bar.update(1)
            if update_result.is_failure:
                return FlextResult[None].fail(f"Progress update failed: {update_result.error}")
                
        return FlextResult[None].ok(None)
    
    def _handle_login(self, args: dict) -> FlextResult[str]:
        """Handle login command - proper error handling, no fallbacks."""
        # Validate required arguments
        if not args.get("username"):
            return FlextResult[str].fail("Username is required")
            
        if not args.get("password"):
            return FlextResult[str].fail("Password is required")
        
        # Perform authentication - NO try/except fallbacks
        auth_result = self._authenticate_user(args["username"], args["password"])
        if auth_result.is_failure:
            return FlextResult[str].fail(f"Authentication failed: {auth_result.error}")
            
        return FlextResult[str].ok(f"Login successful for {args['username']}")
    
    def _authenticate_user(self, username: str, password: str) -> FlextResult[bool]:
        """Authenticate user - implement correct solution, no workarounds."""
        # CORRECT: Use proper authentication service
        # FORBIDDEN: Hardcoded credentials or mock authentication
        
        # Get authentication service from container
        container = FlextContainer.get_global()
        auth_service_result = container.get("auth_service")
        if auth_service_result.is_failure:
            return FlextResult[bool].fail("Authentication service unavailable")
            
        auth_service = auth_service_result.unwrap()
        return auth_service.authenticate(username, password)

# ✅ CORRECT - CLI entry point using flext-cli
def main() -> None:
    """Main CLI entry point - uses flext-cli, never Click directly."""
    cli_service = ProjectCliService()
    cli_result = cli_service.create_cli_interface()
    
    if cli_result.is_failure:
        # Use flext-cli for error output too - NO direct print/rich usage
        cli_api = FlextCliApi()
        error_output = cli_api.format_error_message(
            message=f"CLI initialization failed: {cli_result.error}",
            error_type="initialization",
            suggestions=["Check flext-cli installation", "Verify configuration"]
        )
        cli_api.display_error(error_output.unwrap() if error_output.is_success else cli_result.error)
        exit(1)
        
    cli = cli_result.unwrap()
    cli.run()

# ❌ FORBIDDEN - Examples of what NOT to do in CLI projects
def bad_cli_examples() -> None:
    """THESE ARE ABSOLUTELY FORBIDDEN PATTERNS."""
    
    # ❌ FORBIDDEN: Direct Rich usage for output
    # from rich.console import Console
    # console = Console()
    # console.print("Hello")  # FORBIDDEN
    
    # ❌ FORBIDDEN: Direct Click usage for commands  
    # import click
    # @click.command()  # FORBIDDEN
    # def my_command(): pass
    
    # ❌ FORBIDDEN: Direct Rich table usage
    # from rich.table import Table
    # table = Table()  # FORBIDDEN
    
    # ❌ FORBIDDEN: Direct Rich progress bars
    # from rich.progress import Progress
    # with Progress() as progress:  # FORBIDDEN
    #     task = progress.add_task("Processing...")
    
    # ✅ CORRECT: ALL output through flext-cli
    cli_api = FlextCliApi()
    
    # Table output through flext-cli
    table_result = cli_api.create_table(
        headers=["Name", "Status", "Progress"],
        rows=[["Task 1", "Running", "50%"]],
        style="default"
    )
    
    # Progress bar through flext-cli  
    progress_result = cli_api.create_progress_bar(
        task_name="Processing data",
        total=100,
        style="bar"
    )

# ❌ ABSOLUTELY FORBIDDEN - Manual configuration loading patterns
def forbidden_configuration_patterns() -> None:
    """These patterns are ABSOLUTELY FORBIDDEN in CLI projects."""
    
    # ❌ FORBIDDEN: Manual .env loading
    # import os
    # from dotenv import load_dotenv
    # load_dotenv()  # FORBIDDEN - flext-cli does this automatically
    
    # ❌ FORBIDDEN: Manual environment variable access
    # DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")  # FORBIDDEN
    
    # ❌ FORBIDDEN: Manual configuration file loading
    # import configparser  # FORBIDDEN in CLI projects
    # config = configparser.ConfigParser()  # FORBIDDEN
    
    # ❌ FORBIDDEN: Custom configuration logic
    # def load_config():  # FORBIDDEN - flext-cli handles all configuration
    #     # Custom configuration loading logic
    #     pass
    
    # ✅ CORRECT: Use flext-cli configuration API exclusively
    cli_config = FlextCliConfig()
    value_result = cli_config.get_value("database.host")
    # This automatically handles ENV VARS -> .env -> DEFAULT -> CLI priority

# ✅ CORRECT - Configuration validation through flext-cli
def validate_cli_configuration() -> FlextResult[bool]:
    """Validate CLI configuration through flext-cli validation API."""
    cli_config = FlextCliConfig()
    
    # ✅ CORRECT: Use flext-cli validation (handles all sources automatically)
    validation_result = cli_config.validate_configuration()
    if validation_result.is_failure:
        return FlextResult[bool].fail(f"Configuration validation failed: {validation_result.error}")
        
    return FlextResult[bool].ok(True)

# ✅ CORRECT - Module exports for CLI
__all__ = ["ProjectCliService", "main", "validate_cli_configuration"]
```

#### 🔒 CONFIGURATION PROHIBITIONS (ABSOLUTE ZERO TOLERANCE)

**FORBIDDEN PATTERNS** in ALL CLI projects:

1. **Manual .env Loading**:
   - ❌ `import dotenv` or `load_dotenv()` calls  
   - ❌ Direct `os.getenv()` usage for application configuration
   - ❌ Custom environment variable processing logic

2. **Configuration File Processing**:
   - ❌ `configparser`, `yaml.load()`, `json.load()` for app config
   - ❌ Custom configuration file readers
   - ❌ Manual configuration merging or priority logic

3. **Configuration Infrastructure**:
   - ❌ Creating configuration classes outside flext-cli/flext-core
   - ❌ Custom configuration validation logic  
   - ❌ Manual CLI parameter parsing (argparse, click.option)

**ENFORCEMENT**: Projects violating these patterns MUST be refactored to use flext-cli configuration API exclusively.

```python
# ❌ FORBIDDEN EXAMPLE - Manual configuration (ZERO TOLERANCE VIOLATION)
import os
from dotenv import load_dotenv
import argparse

def forbidden_manual_config():
    """THIS IS ABSOLUTELY FORBIDDEN IN CLI PROJECTS."""
    # Loading .env manually
    load_dotenv()  # FORBIDDEN - flext-cli does this
    
    # Manual environment access
    db_host = os.getenv("DATABASE_HOST", "localhost")  # FORBIDDEN
    
    # Manual CLI parsing
    parser = argparse.ArgumentParser()  # FORBIDDEN
    parser.add_argument("--db-host")    # FORBIDDEN
    args = parser.parse_args()          # FORBIDDEN
    
    # Manual priority resolution
    final_host = args.db_host or db_host  # FORBIDDEN LOGIC

# ✅ CORRECT EXAMPLE - Automatic configuration through flext-cli
def correct_automatic_config() -> FlextResult[dict]:
    """Correct configuration access through flext-cli automatic hierarchy."""
    cli_config = FlextCliConfig()
    
    # Define schema ONLY - flext-cli handles loading
    schema_result = cli_config.register_schema({
        "database": {
            "host": {
                "default": "localhost",
                "env_var": "DATABASE_HOST", 
                "cli_param": "--db-host"
            }
        }
    })
    
    if schema_result.is_failure:
        return FlextResult[dict].fail(f"Schema registration failed: {schema_result.error}")
    
    # Access value - automatically resolved through priority hierarchy
    # 1. ENVIRONMENT VARIABLES -> 2. .env FILE -> 3. DEFAULT CONSTANTS -> 4. CLI PARAMETERS
    host_result = cli_config.get_value("database.host")
    if host_result.is_failure:
        return FlextResult[dict].fail(f"Configuration access failed: {host_result.error}")
        
    return FlextResult[dict].ok({"database_host": host_result.unwrap()})
```

### Testing Strategy (MINIMAL MOCKS, REAL FUNCTIONALITY)

```python
# ✅ CORRECT - Real functional tests using ACTUAL available libraries
import pytest
from flext_core import FlextResult

class TestUnifiedProjectService:
    """Real functional tests for project service.
    
    These tests execute actual functionality against real
    environments, with minimal mocking only where absolutely necessary.
    
    PRIORITY: Test real functionality, not implementation details.
    """
    
    def setup_method(self) -> None:
        """Setup real test environment."""
        # Initialize with empty Pydantic data (FlextDomainService requirement)
        self.service = UnifiedProjectService()
        self.test_data = {"name": "test_project", "description": "test description"}
        
    def test_process_valid_data_success(self) -> None:
        """Test processing valid data returns success result."""
        # Arrange
        valid_data = {"name": "test_project", "type": "data_pipeline"}
        
        # Act
        result = self.service.process_data(valid_data)
        
        # Assert - Test real functionality
        assert result.is_success, f"Processing failed: {result.error}"
        processed_data = result.unwrap()
        assert processed_data.name == "test_project"
        assert processed_data.type == "data_pipeline"
        
    def test_process_empty_data_failure(self) -> None:
        """Test processing empty data returns proper failure."""
        # Act
        result = self.service.process_data({})
        
        # Assert
        assert result.is_failure
        assert "Empty data not allowed" in result.error
        
    def test_database_integration_real_connection(self) -> None:
        """Test real database integration (may require docker)."""
        # This test connects to actual database instance
        db_result = self.service._container.get("database_service")
        assert db_result.is_success
        
        # Test real database operations
        db = db_result.unwrap()
        connection_test = db.test_connection()
        assert connection_test.is_success
```

---

## 📊 QUALITY ASSESSMENT PROTOCOL

### Phase 1: Comprehensive Issue Identification

**MANDATORY FIRST STEP**: Get precise counts of all quality issues:

```bash
# Count exact number of issues across all tools
echo "=== RUFF ISSUES ==="
ruff check . --output-format=github | wc -l

echo "=== MYPY ISSUES ==="  
mypy src/ --show-error-codes --no-error-summary 2>&1 | grep -E "error:|note:" | wc -l

echo "=== PYRIGHT ISSUES ==="
pyright src/ --level error 2>&1 | grep -E "error|warning" | wc -l

echo "=== PYTEST RESULTS ==="
pytest tests/ --tb=no -q 2>&1 | grep -E "failed|passed|error" | tail -1

echo "=== CURRENT COVERAGE ==="
pytest tests/ --cov=src --cov-report=term-missing --tb=no 2>&1 | grep "TOTAL"
```

### Phase 2: Systematic Resolution Workflow

**PRIORITY ORDER** (High impact first):

1. **Fix import and syntax errors** (prevents other tools from running)
2. **Resolve type safety issues** (mypy strict mode + pyright)
3. **Address code quality violations** (ruff with all rules enabled)
4. **Achieve test coverage** (near 100% with real functional tests)
5. **Optimize and consolidate** (remove duplication, improve ergonomics)

### Phase 3: Continuous Validation

**AFTER EVERY CHANGE** (mandatory validation cycle):

```bash
# Quick validation cycle (must pass before proceeding)
ruff check src/ --fix-only  # Auto-fix what can be auto-fixed
ruff check src/             # Verify zero remaining issues
mypy src/ --strict --no-error-summary  # Verify zero type errors
pytest tests/ --tb=short -x # Stop on first test failure
```

---

## 🛠️ INCREMENTAL REFACTORING METHODOLOGY

### Strategy: Progressive Enhancement (NOT Rewriting)

**APPROACH**: Each refactoring cycle improves one specific aspect while maintaining all existing functionality.

#### Cycle 1: Foundation Consolidation

```python
# BEFORE - Multiple scattered implementations
class ServiceA:
    def method1(self): pass

class ServiceB:
    def method2(self): pass
    
# Scattered helper functions
def helper_function(): pass

# AFTER - Single unified class (incremental improvement)
class UnifiedProjectService:
    """Consolidated service following single responsibility principle."""
    
    def method1(self) -> FlextResult[ReturnType]:
        """Former ServiceA.method1 with proper error handling."""
        # Implementation using flext-core patterns
        
    def method2(self) -> FlextResult[ReturnType]:
        """Former ServiceB.method2 with proper error handling."""
        # Implementation using flext-core patterns
        
    def _helper_method(self) -> ReturnType:
        """Former helper_function now as private method."""
        # Implementation as part of unified class
```

#### Cycle 2: Type Safety Enhancement

```python
# BEFORE - Weak typing
def process(data: Any) -> Any:
    return data

# AFTER - Strong typing (incremental improvement)
def process(data: ProcessingInput) -> FlextResult[ProcessingOutput]:
    """Process data with full type safety and error handling."""
    if not isinstance(data, ProcessingInput):
        return FlextResult[ProcessingOutput].fail("Invalid input type")
    
    try:
        result = ProcessingOutput.model_validate(data.model_dump())
        return FlextResult[ProcessingOutput].ok(result)
    except ValidationError as e:
        return FlextResult[ProcessingOutput].fail(f"Processing failed: {e}")
```

#### Cycle 3: Test Coverage Achievement

```python
# NEW - Comprehensive functional tests
class TestUnifiedProjectServiceComplete:
    """Complete test coverage for unified service."""
    
    @pytest.mark.parametrize("input_data,expected_result", [
        ({"valid": "data"}, "success"),
        ({}, "failure"),
        ({"invalid": "structure"}, "failure"),
    ])
    def test_process_data_scenarios(self, input_data, expected_result):
        """Test all processing scenarios comprehensively."""
        service = UnifiedProjectService()
        result = service.process_data(input_data)
        
        if expected_result == "success":
            assert result.is_success
        else:
            assert result.is_failure
    
    def test_error_handling_comprehensive(self):
        """Test all error handling paths."""
        service = UnifiedProjectService()
        
        # Test all failure modes
        error_cases = [
            None,           # None input
            "",             # Empty string
            [],             # Empty list
            {"malformed": "data"},  # Invalid structure
        ]
        
        for case in error_cases:
            result = service.process_data(case)
            assert result.is_failure, f"Should fail for case: {case}"
            assert result.error, "Error message should be present"
    
    def test_integration_with_flext_core(self):
        """Test integration with flext-core components."""
        service = UnifiedProjectService()
        
        # Test container integration
        container_result = service._container.get("test_service")
        # Test based on actual service availability
        
        # Test logging integration
        assert service._logger is not None
        # Verify logger works with real log calls
```

---

## 🔧 TOOL-SPECIFIC RESOLUTION STRATEGIES

### Ruff Issues Resolution

**SYSTEMATIC APPROACH**: Fix by category, not file-by-file

```bash
# Identify high-priority issues first
ruff check . --select F  # Pyflakes errors (critical)
ruff check . --select E9 # Syntax errors (critical) 
ruff check . --select F821 # Undefined name (critical)

# Address import issues
ruff check . --select I    # Import sorting
ruff check . --select F401 # Unused imports

# Apply auto-fixes where safe
ruff check . --fix-only --select I,F401,E,W

# Manual fixes for complex issues
ruff check . --select PLR2004  # Magic values
ruff check . --select C901     # Complex functions
```

**RESOLUTION PATTERNS**:

```python
# ✅ CORRECT - Fix magic values
# BEFORE
if timeout > 30:  # Magic number
    
# AFTER  
class ServiceConstants:
    DEFAULT_TIMEOUT = 30
    
if timeout > ServiceConstants.DEFAULT_TIMEOUT:

# ✅ CORRECT - Fix complex functions
# BEFORE
def complex_function(data):
    # 50+ lines of mixed logic
    
# AFTER
class DataProcessor:
    def process(self, data: InputType) -> FlextResult[OutputType]:
        """Main processing method with clear separation."""
        return (
            self._validate(data)
            .flat_map(self._transform)
            .map(self._enrich)
        )
    
    def _validate(self, data: InputType) -> FlextResult[InputType]:
        """Focused validation logic."""
        
    def _transform(self, data: InputType) -> FlextResult[ProcessedType]:
        """Focused transformation logic."""
        
    def _enrich(self, data: ProcessedType) -> OutputType:
        """Focused enrichment logic."""
```

### MyPy Issues Resolution

**STRICT MODE COMPLIANCE** (zero tolerance for type errors):

```python
# ✅ CORRECT - Proper generic typing
from typing import Generic, TypeVar, Protocol

T = TypeVar('T')
U = TypeVar('U')

class DataProcessor(Generic[T]):
    """Generic data processor with proper type constraints."""
    
    def process(self, data: T) -> FlextResult[T]:
        """Process data maintaining type safety."""
        return FlextResult[T].ok(data)

# ✅ CORRECT - Protocol usage instead of Any
class Processable(Protocol):
    """Protocol defining processable interface."""
    
    def get_data(self) -> dict: ...
    def set_data(self, data: dict) -> None: ...

def process_item(item: Processable) -> FlextResult[dict]:
    """Process any item implementing Processable protocol."""
    try:
        data = item.get_data()
        return FlextResult[dict].ok(data)
    except Exception as e:
        return FlextResult[dict].fail(str(e))

# ✅ CORRECT - Proper error handling without Any
def safe_operation() -> FlextResult[ProcessResult]:
    """Operation with comprehensive error handling."""
    try:
        result = perform_operation()
        return FlextResult[ProcessResult].ok(result)
    except SpecificException as e:
        return FlextResult[ProcessResult].fail(f"Specific error: {e}")
    except Exception as e:
        return FlextResult[ProcessResult].fail(f"Unexpected error: {e}")
```

### Pytest Coverage Enhancement

**EVIDENCE-BASED TESTING** (Follow flext-core 79% success pattern):

```python
# ✅ CORRECT - Comprehensive test coverage (REALISTIC APPROACH)
import pytest
from flext_core import FlextResult

class TestCompleteProjectService:
    """Complete functional test suite following flext-core patterns."""
    
    def test_all_public_methods_coverage(self):
        """Ensure all public methods are tested."""
        service = UnifiedProjectService()
        
        # Test main functionality
        result = service.process_data({"test": "data"})
        assert result is not None
        
        # Test error cases
        error_result = service.process_data(None)
        assert error_result.is_failure
        
        # Test edge cases
        edge_result = service.process_data({})
        assert edge_result is not None
        
    def test_integration_with_dependencies(self):
        """Test integration with actual dependencies."""
        service = UnifiedProjectService()
        
        # Test container integration (real container)
        container = service._container
        assert container is not None
        
        # Test logger integration (real logger)
        logger = service._logger
        assert logger is not None
        
        # Test actual logging (produces real log output)
        logger.info("Test log message")
        
    def test_error_boundary_conditions(self):
        """Test all error boundary conditions."""
        service = UnifiedProjectService()
        
        error_conditions = [
            None,                    # None input
            {},                      # Empty dict
            {"invalid": "format"},   # Wrong format
            {"missing": "required"}, # Missing required fields
        ]
        
        for condition in error_conditions:
            result = service.process_data(condition)
            # Verify error handling works correctly
            assert isinstance(result, FlextResult)
            
    # Use pragma ONLY for truly untestable code
    def test_exception_handling_coverage(self):  # pragma: no cover
        """Test exception scenarios that are hard to trigger in normal flow."""
        # Only use pragma when genuinely impossible to test
        pass
```

---

## 📈 CONTINUOUS IMPROVEMENT CYCLE

### Daily Quality Gates

**MANDATORY EXECUTION**: Every development session must end with full validation

```bash
#!/bin/bash
# quality_gate_check.sh - Run this after every change session

set -e  # Exit on any error

echo "=== QUALITY GATE VALIDATION ==="

echo "1. Ruff Check (Code Quality)..."
ruff check src/ tests/ examples/ scripts/
echo "✅ Ruff passed"

echo "2. MyPy Check (Type Safety)..."  
mypy src/ --strict --no-error-summary
echo "✅ MyPy passed"

echo "3. Pyright Check (Advanced Type Safety)..."
pyright src/ --level error
echo "✅ Pyright passed"

echo "4. Pytest Execution (Functional Tests)..."
pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=95 -x
echo "✅ Pytest passed with 95%+ coverage"

echo "5. Import Validation..."
python -c "import src; print('✅ All imports work')"

echo "=== ALL QUALITY GATES PASSED ==="
```

### Progressive Enhancement Strategy

**WEEKLY CYCLES**: Each week focus on one improvement area

- **Week 1**: Foundation consolidation (eliminate duplication)
- **Week 2**: Type safety enhancement (strict mypy compliance)
- **Week 3**: Test coverage achievement (95%+ real functional tests)
- **Week 4**: Performance optimization (using flext-core patterns)
- **Week 5**: Documentation and API refinement
- **Week 6**: Integration testing and real environment validation

### Success Metrics Tracking

**MEASURABLE TARGETS**:

```bash
# Track progress with concrete numbers
echo "QUALITY METRICS TRACKING" > quality_metrics.log
echo "Date: $(date)" >> quality_metrics.log
echo "Ruff Issues: $(ruff check . --output-format=github | wc -l)" >> quality_metrics.log
echo "MyPy Issues: $(mypy src/ 2>&1 | grep -c error || echo 0)" >> quality_metrics.log
echo "Test Coverage: $(pytest --cov=src --cov-report=term 2>/dev/null | grep TOTAL | awk '{print $4}')" >> quality_metrics.log
echo "Pytest Pass Rate: $(pytest --tb=no -q 2>&1 | grep -E '[0-9]+ passed' | awk '{print $1}')" >> quality_metrics.log
```

**TARGET ACHIEVEMENTS** (Evidence-based, realistic goals):
- 🎯 **Ruff Issues**: From 1,704 to 0 (Systematic reduction by category)
- 🎯 **MyPy Issues**: Maintain 0 in src/ (Already achieved - validate continuously)  
- 🎯 **Pyright Issues**: From 4 to 0 (Minor API signature corrections)
- 🎯 **Test Coverage**: Achieve 75%+ (Match flext-core proven success at 79%)
- 🎯 **Pytest Pass Rate**: From 27 passed/5 errors to 100% pass

---

## 🎖️ PROFESSIONAL EXCELLENCE STANDARDS

### Code Quality Principles

1. **Single Responsibility**: Each class has one clear purpose
2. **Open/Closed**: Extensible through inheritance/composition, not modification
3. **Liskov Substitution**: Derived classes are substitutable for base classes
4. **Interface Segregation**: Clients depend only on methods they use
5. **Dependency Inversion**: Depend on abstractions, not concretions

### Documentation Standards

```python
class ExampleService(FlextDomainService[FlextResult[ProcessedData]]):
    """Professional service class following SOLID principles.
    
    This service handles data processing operations with comprehensive
    error handling, type safety, and integration with the flext-core
    foundation. It demonstrates proper separation of concerns and
    dependency injection patterns.
    
    Attributes:
        _container: Dependency injection container from flext-core
        _logger: Structured logger for operational observability
        
    Example:
        >>> service = ExampleService()
        >>> result = service.process_data({"name": "test"})
        >>> assert result.is_success
        >>> data = result.unwrap()
    """
    
    def __init__(self) -> None:
        """Initialize service with proper dependency injection."""
        super().__init__()
        self._container = get_flext_container()
        self._logger = get_logger(__name__)
        
    def process_data(self, input_data: dict) -> FlextResult[ProcessedData]:
        """Process input data with comprehensive validation and error handling.
        
        This method implements the railway pattern for error handling,
        ensuring that failures are properly captured and propagated
        without raising exceptions.
        
        Args:
            input_data: Dictionary containing data to process
            
        Returns:
            FlextResult containing either successful ProcessedData or error message
            
        Example:
            >>> result = service.process_data({"name": "example"})
            >>> if result.is_success:
            ...     data = result.unwrap()
            ... else:
            ...     logger.error(result.error)
        """
        return (
            self._validate_input(input_data)
            .flat_map(self._transform_to_model)
            .map(self._enrich_with_metadata)
            .map_error(lambda e: f"Data processing failed: {e}")
        )
```

### Error Handling Excellence (ZERO FALLBACK TOLERANCE)

```python
# ✅ PROFESSIONAL - Proper error handling WITHOUT try/except fallbacks
def robust_operation(data: InputType) -> FlextResult[OutputType]:
    """Robust operation with proper error boundary handling - NO FALLBACKS.
    
    This demonstrates the correct approach: validate inputs, handle errors
    explicitly, and return meaningful error messages. NO try/except blocks
    used as fallback mechanisms.
    """
    
    # Step 1: Comprehensive input validation - fail fast and clearly
    if data is None:
        return FlextResult[OutputType].fail("Input data cannot be None")
        
    if not isinstance(data, InputType):
        return FlextResult[OutputType].fail(f"Expected InputType, got {type(data)}")
    
    # Step 2: Business rule validation - explicit error checking
    validation_result = validate_business_rules(data)
    if validation_result.is_failure:
        return FlextResult[OutputType].fail(f"Business rule validation failed: {validation_result.error}")
        
    # Step 3: Data transformation - check result, no exception catching
    transformation_result = transform_data(validation_result.unwrap())
    if transformation_result.is_failure:
        return FlextResult[OutputType].fail(f"Data transformation failed: {transformation_result.error}")
        
    # Step 4: Final processing - explicit success/failure handling
    final_result = finalize_processing(transformation_result.unwrap())
    if final_result.is_failure:
        return FlextResult[OutputType].fail(f"Processing finalization failed: {final_result.error}")
        
    return FlextResult[OutputType].ok(final_result.unwrap())

# ❌ FORBIDDEN - Try/except as fallback mechanism
def bad_operation_with_fallbacks(data: InputType) -> OutputType:
    """THIS IS ABSOLUTELY FORBIDDEN - demonstrates what NOT to do."""
    try:
        # Some operation that might fail
        result = risky_operation(data)
        return result
    except Exception:
        # FORBIDDEN: Silent fallback that masks real problems
        return default_value  # This hides the real issue!
        
    try:
        # FORBIDDEN: Multiple fallback attempts
        return alternative_operation(data)  
    except Exception:
        # FORBIDDEN: Final fallback that gives false success
        return empty_result  # User thinks it worked!

# ✅ CORRECT - Explicit error handling without fallbacks  
def correct_operation(data: InputType) -> FlextResult[OutputType]:
    """Correct approach - explicit error handling, no hidden fallbacks."""
    
    # Attempt primary operation
    primary_result = risky_operation(data)
    if primary_result.is_failure:
        # Log the specific failure, don't hide it
        logger.error(f"Primary operation failed: {primary_result.error}")
        return FlextResult[OutputType].fail(f"Operation failed: {primary_result.error}")
    
    # If primary succeeded, validate the result
    validation_result = validate_result(primary_result.unwrap())
    if validation_result.is_failure:
        return FlextResult[OutputType].fail(f"Result validation failed: {validation_result.error}")
        
    return FlextResult[OutputType].ok(validation_result.unwrap())

# ✅ CORRECT - Service unavailability handling without fallbacks
def database_operation(query: str) -> FlextResult[QueryResult]:
    """Database operation with proper error handling - no silent fallbacks."""
    
    # Get database service from container
    container = FlextContainer.get_global()
    db_service_result = container.get("database_service")
    
    # If service unavailable, FAIL EXPLICITLY - don't hide the problem
    if db_service_result.is_failure:
        return FlextResult[QueryResult].fail("Database service is unavailable - system configuration error")
    
    db_service = db_service_result.unwrap()
    
    # Execute query and handle results explicitly
    query_result = db_service.execute_query(query)
    if query_result.is_failure:
        # Return specific error, don't try alternative approaches silently
        return FlextResult[QueryResult].fail(f"Query execution failed: {query_result.error}")
        
    return FlextResult[QueryResult].ok(query_result.unwrap())
```

---

## ⚡ EXECUTION CHECKLIST

### Before Starting Any Work

- [ ] Read all documentation: `CLAUDE.md`, `FLEXT_REFACTORING_PROMPT.md`, project `README.md`
- [ ] Verify virtual environment: `/home/marlonsc/flext/.venv/bin/python` (VERIFIED WORKING)
- [ ] Run baseline quality assessment using exact commands provided
- [ ] Plan incremental improvements (never wholesale rewrites)
- [ ] Establish measurable success criteria from current baseline

### During Each Development Cycle  

- [ ] Make minimal, focused changes (single aspect per change)
- [ ] Validate after every modification using quality gates
- [ ] Test actual functionality (no mocks, real execution)
- [ ] Document changes with professional English
- [ ] Update tests to maintain coverage near 100%

### After Each Development Session

- [ ] Full quality gate validation (ruff + mypy + pyright + pytest)
- [ ] Coverage measurement and improvement tracking  
- [ ] Integration testing with real dependencies
- [ ] Update documentation reflecting current reality
- [ ] Commit with descriptive messages explaining improvements

### Project Completion Criteria

- [ ] **Code Quality**: Zero ruff violations across all code
- [ ] **Type Safety**: Zero mypy/pyright errors in src/
- [ ] **Test Coverage**: 95%+ with real functional tests
- [ ] **Documentation**: Professional English throughout
- [ ] **Architecture**: Clean SOLID principles implementation
- [ ] **Integration**: Seamless flext-core foundation usage
- [ ] **Maintainability**: Clear, readable, well-structured code

---

## 🏁 FINAL SUCCESS VALIDATION

```bash
#!/bin/bash
# final_validation.sh - Complete ecosystem validation

echo "=== FLEXT ECOSYSTEM FINAL VALIDATION ==="

# Quality Gates
ruff check . --statistics
mypy src/ --strict --show-error-codes  
pyright src/ --stats
pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=95

# Functional Validation  
python -c "
import sys
sys.path.insert(0, 'src')

try:
    # Test all major imports
    from flext_core import FlextResult, get_flext_container, FlextModels
    print('✅ flext-core integration: SUCCESS')
    
    # Test project functionality
    # (Add specific project import tests here)
    
    print('✅ All imports: SUCCESS')
    print('✅ FINAL VALIDATION: PASSED')
    
except Exception as e:
    print(f'❌ VALIDATION FAILED: {e}')
    sys.exit(1)
"

echo "=== ECOSYSTEM READY FOR PRODUCTION ==="
```

---

## 🔬 CLI TESTING AND DEBUGGING METHODOLOGY (MANDATORY FLEXT ECOSYSTEM INTEGRATION)

### Critical Principle: Configuration Hierarchy and .env Detection

**GOLDEN RULE**: Configuration follows strict priority hierarchy with ENVIRONMENT VARIABLES taking precedence over .env files. The .env file is automatically detected from CURRENT execution directory. All CLI testing and debugging MUST use FLEXT ecosystem exclusively - NO external testing tools or custom implementations allowed.

**CORRECT PRIORITY ORDER**:
```
1. ENVIRONMENT VARIABLES  (export DATABASE_HOST=prod-server - HIGHEST PRIORITY)
2. .env FILE             (DATABASE_HOST=localhost from execution directory)
3. DEFAULT CONSTANTS     (DATABASE_HOST="defaulthost" in code)
4. CLI PARAMETERS        (--host override-server for specific overrides)
```

#### 🔧 UNIVERSAL CLI TESTING PATTERN (ALL PROJECTS)

**UNIVERSAL PRINCIPLE**: ALL CLI projects follow identical testing and debugging patterns using FLEXT ecosystem integration, regardless of specific domain (LDAP, API, database, etc.).

```bash
# ✅ CORRECT - Universal CLI testing pattern for ANY project
# Configuration file automatically detected from current directory

# Universal CLI testing commands (work for ALL FLEXT projects):
# Phase 1: CLI Debug Mode Testing (MANDATORY FLEXT-CLI)
python -m project_name --debug primary-command \
  --input-dir data/input \
  --output-dir data/output \
  --config-file custom.env

# Phase 2: CLI Trace Mode Testing (FLEXT-CLI + FLEXT-CORE LOGGING)
export LOG_LEVEL=DEBUG
export ENABLE_TRACE=true
python -m project_name primary-command \
  --input-dir data/input \
  --output-dir data/output \
  --config-format toml

# Phase 3: CLI Configuration Validation (AUTOMATIC MULTI-FORMAT LOADING)
python -m project_name validate-environment --debug --config-format yaml

# Phase 4: CLI Service Connection Testing (FLEXT ECOSYSTEM INTEGRATION)
python -m project_name test-service-connectivity --debug --trace

# Phase 5: CLI Component Testing (FLEXT ECOSYSTEM COMPONENTS)
python -m project_name test-component --component=main-service \
  --debug --trace --config-file production.toml
```

### 🚫 ABSOLUTELY FORBIDDEN - External Testing Patterns

**ZERO TOLERANCE VIOLATIONS** - These patterns are absolutely forbidden:

```bash
# ❌ FORBIDDEN - External LDAP testing tools
# ldapsearch -h localhost -p 3389 -D "cn=orclREDACTED_LDAP_BIND_PASSWORD" -w "password"  # FORBIDDEN
# ldapadd -h localhost -p 3389 -D "cn=orclREDACTED_LDAP_BIND_PASSWORD" -w "password"    # FORBIDDEN
# ldapmodify -h localhost -p 3389 -D "cn=orclREDACTED_LDAP_BIND_PASSWORD"               # FORBIDDEN

# ❌ FORBIDDEN - Custom testing scripts bypassing FLEXT
# python custom_test_ldap.py     # FORBIDDEN
# python manual_ldif_test.py     # FORBIDDEN  
# python direct_connection.py    # FORBIDDEN

# ❌ FORBIDDEN - Manual .env loading
# export $(cat .env | xargs)     # FORBIDDEN - flext-cli does this automatically
# source .env                    # FORBIDDEN - flext-cli handles .env loading

# ❌ FORBIDDEN - Non-FLEXT diagnostic tools
# netcat -zv localhost 3389      # FORBIDDEN - use CLI test commands
# telnet localhost 3389          # FORBIDDEN - use CLI test commands
# dig @localhost dc=ctbc         # FORBIDDEN - use CLI diagnostic commands
```

### ✅ CORRECT - FLEXT CLI Testing and Debugging Methodology

```python
# ✅ CORRECT - CLI testing through FLEXT ecosystem exclusively
from flext_core import FlextResult, get_logger
from flext_cli import FlextCliApi, FlextCliConfig
from flext_ldap import get_flext_ldap_api
from flext_ldif import FlextLDIFAPI

class ProjectCliTestingService:
    """CLI testing service using FLEXT ecosystem - .env automatically loaded."""
    
    def __init__(self) -> None:
        """Initialize CLI testing with automatic .env configuration loading."""
        # ✅ AUTOMATIC: .env loaded transparently by FLEXT ecosystem
        self._logger = get_logger("cli_testing")
        self._cli_api = FlextCliApi()
        self._config = FlextCliConfig()  # Automatically loads .env + defaults + CLI params
        self._ldap_api = get_flext_ldap_api()
        self._ldif_api = FlextLDIFAPI()
        
    def debug_cli_configuration(self) -> FlextResult[dict]:
        """Debug CLI configuration using FLEXT patterns - .env as source of truth."""
        self._logger.debug("Starting CLI configuration debugging")
        
        # ✅ CORRECT: Access configuration through FLEXT API (includes .env automatically)
        config_result = self._config.get_all_configuration()
        if config_result.is_failure:
            return FlextResult[dict].fail(f"Configuration access failed: {config_result.error}")
            
        config_data = config_result.unwrap()
        
        # Debug output through FLEXT CLI API
        debug_display_result = self._cli_api.display_debug_information(
            title="CLI Configuration Debug (ENV → .env → DEFAULT → CLI)",
            data=config_data,
            format_type="tree"  # flext-cli handles formatted output
        )
        
        if debug_display_result.is_failure:
            return FlextResult[dict].fail(f"Debug display failed: {debug_display_result.error}")
            
        return FlextResult[dict].ok(config_data)
    
    def test_ldap_connectivity_debug(self) -> FlextResult[dict]:
        """Test LDAP connectivity with debug logging - FLEXT-LDAP exclusively."""
        self._logger.debug("Starting LDAP connectivity testing")
        
        # ✅ CORRECT: Get LDAP configuration from .env through FLEXT config
        ldap_config_result = self._config.get_ldap_configuration()
        if ldap_config_result.is_failure:
            return FlextResult[dict].fail(f"LDAP config access failed: {ldap_config_result.error}")
            
        ldap_config = ldap_config_result.unwrap()
        
        # ✅ CORRECT: Test connection through FLEXT-LDAP API (NO external tools)
        connection_result = self._ldap_api.test_connection_with_debug(
            host=ldap_config["host"],
            port=ldap_config["port"], 
            bind_dn=ldap_config["bind_dn"],
            bind_password=ldap_config["bind_password"],
            debug_mode=True
        )
        
        if connection_result.is_failure:
            # Display debug information through FLEXT CLI
            self._cli_api.display_error_with_debug(
                error_message=f"LDAP connection failed: {connection_result.error}",
                debug_data=ldap_config,
                suggestions=[
                    "Check .env file configuration",
                    "Verify LDAP server is running", 
                    "Validate network connectivity",
                    "Check LDAP credentials"
                ]
            )
            return FlextResult[dict].fail(connection_result.error)
            
        # Display success with debug information
        connection_info = connection_result.unwrap()
        self._cli_api.display_success_with_debug(
            success_message="LDAP connection successful",
            debug_data=connection_info,
            format_type="table"
        )
        
        return FlextResult[dict].ok(connection_info)
        
    def test_ldif_processing_debug(self, input_directory: str) -> FlextResult[dict]:
        """Test LDIF processing with debug traces - FLEXT-LDIF exclusively."""
        self._logger.debug(f"Starting LDIF processing test for: {input_directory}")
        
        # ✅ CORRECT: Process LDIF through FLEXT-LDIF API with debug mode
        processing_result = self._ldif_api.process_directory_with_debug(
            input_dir=input_directory,
            debug_mode=True,
            trace_mode=True,
            validation_level="strict"
        )
        
        if processing_result.is_failure:
            # Display debug information through FLEXT CLI
            self._cli_api.display_error_with_debug(
                error_message=f"LDIF processing failed: {processing_result.error}",
                debug_data={"input_directory": input_directory},
                suggestions=[
                    "Check LDIF file format and syntax",
                    "Verify file permissions and access",
                    "Validate LDIF structure and schema",
                    "Check for corrupted LDIF entries"
                ]
            )
            return FlextResult[dict].fail(processing_result.error)
            
        # Display processing results with debug information
        processing_info = processing_result.unwrap()
        self._cli_api.display_success_with_debug(
            success_message=f"LDIF processing completed: {len(processing_info['entries'])} entries processed",
            debug_data=processing_info,
            format_type="summary"
        )
        
        return FlextResult[dict].ok(processing_info)
        
    def validate_environment_debug(self) -> FlextResult[dict]:
        """Validate complete environment using FLEXT ecosystem - .env as truth source."""
        validation_results = {}
        
        # Phase 1: Configuration validation (.env + defaults + CLI)
        config_result = self.debug_cli_configuration()
        if config_result.is_success:
            validation_results["configuration"] = "✅ PASSED"
        else:
            validation_results["configuration"] = f"❌ FAILED: {config_result.error}"
            
        # Phase 2: LDAP connectivity validation (flext-ldap)
        ldap_result = self.test_ldap_connectivity_debug()
        if ldap_result.is_success:
            validation_results["ldap_connectivity"] = "✅ PASSED"
        else:
            validation_results["ldap_connectivity"] = f"❌ FAILED: {ldap_result.error}"
            
        # Phase 3: FLEXT ecosystem integration validation
        ecosystem_result = self._validate_flext_ecosystem_integration()
        if ecosystem_result.is_success:
            validation_results["flext_ecosystem"] = "✅ PASSED"
        else:
            validation_results["flext_ecosystem"] = f"❌ FAILED: {ecosystem_result.error}"
            
        # Display complete validation results through FLEXT CLI
        self._cli_api.display_validation_results(
            title="Complete Environment Validation (ENV → .env → DEFAULT → CLI)",
            results=validation_results,
            format_type="detailed_table"
        )
        
        return FlextResult[dict].ok(validation_results)
        
    def _validate_flext_ecosystem_integration(self) -> FlextResult[None]:
        """Validate complete FLEXT ecosystem integration."""
        try:
            # Verify all FLEXT integrations are working
            from flext_core import FlextResult, get_logger, FlextContainer
            from flext_cli import FlextCliApi
            from flext_ldap import get_flext_ldap_api
            from flext_ldif import FlextLDIFAPI
            
            # Test each integration
            logger = get_logger("ecosystem_validation")
            container = FlextContainer.get_global()
            cli_api = FlextCliApi()
            ldap_api = get_flext_ldap_api()
            ldif_api = FlextLDIFAPI()
            
            logger.info("FLEXT ecosystem integration validation completed")
            return FlextResult[None].ok(None)
            
        except Exception as e:
            return FlextResult[None].fail(f"FLEXT ecosystem integration failed: {e}")

# ✅ CORRECT - CLI entry point with debug support
def create_cli_with_debug_support() -> FlextResult[None]:
    """Create CLI with comprehensive debug support using FLEXT patterns."""
    testing_service = ProjectCliTestingService()
    
    # Register CLI commands with debug capabilities
    cli_api = FlextCliApi()
    
    # Debug configuration command
    debug_config_result = cli_api.register_command(
        name="debug-config",
        description="Debug CLI configuration (ENV → .env → DEFAULT → CLI priority)",
        handler=testing_service.debug_cli_configuration,
        supports_debug=True
    )
    
    # Debug LDAP command  
    debug_ldap_result = cli_api.register_command(
        name="debug-ldap",
        description="Debug LDAP connectivity through FLEXT-LDAP",
        handler=testing_service.test_ldap_connectivity_debug,
        supports_debug=True
    )
    
    # Validate environment command
    validate_env_result = cli_api.register_command(
        name="validate-environment",
        description="Complete environment validation using FLEXT ecosystem",
        handler=testing_service.validate_environment_debug,
        supports_debug=True,
        supports_trace=True
    )
    
    if any(result.is_failure for result in [debug_config_result, debug_ldap_result, validate_env_result]):
        return FlextResult[None].fail("CLI debug command registration failed")
        
    return FlextResult[None].ok(None)
```

### 🎯 CLI Testing Best Practices (.env as Source of Truth)

#### 1. Configuration Testing Priority Order

```bash
# ✅ CORRECT - Test configuration hierarchy through CLI
python -m project_name debug-config --debug
# This shows: ENVIRONMENT VARIABLES → .env FILE → DEFAULT CONSTANTS → CLI PARAMETERS resolution

# ✅ CORRECT - Test environment variable precedence over .env
export DATABASE_HOST=env-override-host
python -m project_name debug-config --debug
# This shows environment variable takes precedence over .env file

# ✅ CORRECT - Test CLI parameters for specific overrides  
python -m project_name debug-config --debug --host cli-override-host --port 9999
# This shows CLI parameter overrides for specific execution
```

#### 2. Environment Validation Through CLI

```bash
# ✅ CORRECT - Complete environment validation
python -m project_name validate-environment --debug --trace

# ✅ CORRECT - Specific component testing
python -m project_name debug-ldap --debug      # Test LDAP through flext-ldap
python -m project_name debug-ldif --debug      # Test LDIF through flext-ldif
python -m project_name debug-config --debug    # Test configuration loading
```

#### 3. Problem Diagnosis Through CLI Debug

```bash
# ✅ CORRECT - Progressive diagnosis through FLEXT CLI commands
# Step 1: Verify configuration loading
python -m project_name debug-config --debug

# Step 2: Test connectivity 
python -m project_name debug-ldap --debug --trace

# Step 3: Test data processing
python -m project_name debug-ldif --input-dir data/test --debug

# Step 4: Full environment validation
python -m project_name validate-environment --debug --trace
```

#### 4. Debug Output Analysis (FLEXT CLI Formatting)

```python
# ✅ CORRECT - Debug output through FLEXT CLI API
def display_debug_results(self, debug_data: dict) -> FlextResult[None]:
    """Display debug results using FLEXT CLI formatting."""
    
    # Configuration debug display
    config_display_result = self._cli_api.create_debug_table(
        title="Configuration Resolution (Priority: ENV → .env → DEFAULT → CLI)",
        headers=["Parameter", "Source", "Value", "Priority Level"],
        rows=[
            ["host", "ENV VARIABLE", "prod-server", "🥇 Level 1 (Highest)"],
            ["port", ".env file", "3389", "🥈 Level 2"], 
            ["base_dn", ".env file", "dc=ctbc", "🥈 Level 2"],
            ["timeout", "DEFAULT", "30", "🥉 Level 3"],
            ["debug", "CLI parameter", "true", "🏅 Level 4 (Override)"]
        ],
        highlight_overrides=True
    )
    
    # Connection debug display
    connection_display_result = self._cli_api.create_debug_tree(
        title="LDAP Connection Debug (FLEXT-LDAP)",
        tree_data={
            "connection_status": "✅ SUCCESS",
            "server_info": {
                "host": "localhost (.env)",
                "port": "3389 (.env)",
                "ssl": "false (.env)"
            },
            "authentication": {
                "bind_dn": "cn=orclREDACTED_LDAP_BIND_PASSWORD (.env)",
                "status": "✅ AUTHENTICATED"
            }
        }
    )
    
    return FlextResult[None].ok(None)
```

---

## 📚 SPECIFIC PROJECT EXAMPLES

### 🏭 client-a OUD MIGRATION - PRODUCTION ENTERPRISE EXAMPLE

#### client-a-Specific CLI Implementation (Following Universal Patterns)

**CONTEXT**: The client-a OUD Migration project demonstrates how the universal CLI configuration system works with a real production enterprise project using LDAP/LDIF operations.

```bash
# ✅ client-a CLI Commands (Following Universal Pattern)
# These commands demonstrate the universal CLI patterns applied to client-a project

# client-a Configuration Debug (Universal debug-config pattern)
python -m client-a_oud_mig debug-config --debug --config-format env
# Output: Shows client-a_OUD_HOST=localhost, client-a_OUD_PORT=3389, etc.

# client-a Service Connectivity Testing (Universal test-service-connectivity pattern)
python -m client-a_oud_mig test-service-connectivity --service=ldap --debug --trace
# Tests: LDAP connectivity to localhost:3389, cn=orclREDACTED_LDAP_BIND_PASSWORD, dc=ctbc

# client-a Environment Validation (Universal validate-environment pattern)
python -m client-a_oud_mig validate-environment --debug --config-format env
# Validates: Complete client-a environment using universal validation system

# client-a Primary Operation (Universal primary-command pattern)
python -m client-a_oud_mig migrate --debug --dry-run \
  --input-dir data/input \
  --output-dir data/output \
  --config-file client-a-production.env

# client-a Component Testing (Universal test-component pattern)
python -m client-a_oud_mig test-component --component=ldif-processor --debug \
  --input-dir data/input \
  --config-format env
```

#### client-a Configuration File Examples (Multi-Format Support)

```bash
# ✅ ENHANCED client-a .env (improved nomenclature while preserving fundamentals)

# =============================================================================
# client-a OUD MIGRATION - ENHANCED CONFIGURATION 
# =============================================================================
# Configuration Priority Order (CORRECT):
# 1. ENVIRONMENT VARIABLES (export client-a_OUD_HOST=prod-server - HIGHEST)
# 2. .env FILE (this file - detected from current execution directory)  
# 3. DEFAULT CONSTANTS (hardcoded values in source code)
# 4. CLI PARAMETERS (--host override for specific execution)
# =============================================================================

# OUD SERVER CONNECTION (PRODUCTION client-a VALUES - PRESERVE THESE)
client-a_OUD_HOST=localhost                    # ✅ PRODUCTION VALUE - PRESERVE
client-a_OUD_PORT=3389                         # ✅ PRODUCTION VALUE - PRESERVE  
client-a_OUD_BASE_DN=dc=ctbc                   # ✅ PRODUCTION VALUE - PRESERVE
client-a_OUD_BIND_DN=cn=orclREDACTED_LDAP_BIND_PASSWORD              # ✅ PRODUCTION VALUE - PRESERVE
client-a_OUD_BIND_PASSWORD=iDm55OID            # ✅ PRODUCTION VALUE - PRESERVE

# APPLICATION BIND USER (PRESERVE THESE)
client-a_APP_BIND_DN=cn=client-adeploy,ou=especial,cn=users,dc=network,dc=ctbc  # PRESERVE
client-a_APP_BIND_PASSWORD=L3&E0F2%@           # ✅ PRODUCTION VALUE - PRESERVE

# MIGRATION DIRECTORIES (PRESERVE PATHS)
client-a_INPUT_DIRECTORY=data/input             # ✅ STANDARD PATH - PRESERVE
client-a_OUTPUT_DIRECTORY=data/output           # ✅ STANDARD PATH - PRESERVE
client-a_RULES_FILE=configs/rules.json         # ✅ STANDARD PATH - PRESERVE
client-a_BACKUP_DIRECTORY=data/backup          # ✅ STANDARD PATH - PRESERVE

# ✨ ENHANCED: CLI DEBUGGING AND TRACING
client-a_CLI_DEBUG_MODE=false                  # Enable CLI debug output
client-a_CLI_TRACE_MODE=false                  # Enable detailed trace logging
client-a_CLI_VALIDATION_LEVEL=strict           # Configuration validation level
client-a_CLI_OUTPUT_FORMAT=table               # CLI output format preference

# ✨ ENHANCED: FLEXT ECOSYSTEM INTEGRATION
client-a_FLEXT_LOG_LEVEL=INFO                  # flext-core logging level
client-a_FLEXT_METRICS_ENABLED=true            # flext-core metrics collection
client-a_FLEXT_TRACING_ENABLED=false           # flext-core distributed tracing
client-a_FLEXT_PROFILE_MODE=false              # Performance profiling mode

# ✨ ENHANCED: DEVELOPMENT AND TESTING  
client-a_TEST_MODE=false                       # Enable test-specific behaviors
client-a_MOCK_LDAP_SERVER=false               # Use mock LDAP for testing
client-a_VALIDATION_STRICT_MODE=true          # Strict validation enforcement
client-a_PERFORMANCE_MONITORING=true          # Monitor performance metrics
```

### 🎯 CLI Testing Enforcement (ZERO TOLERANCE)

#### Mandatory CLI Testing Validation

```bash
# ✅ MANDATORY - All projects MUST provide these CLI testing commands

# 1. Configuration debug command
python -m project_name debug-config --debug
# REQUIRED: Shows complete configuration hierarchy resolution

# 2. Environment validation command  
python -m project_name validate-environment --debug --trace
# REQUIRED: Validates complete environment using FLEXT ecosystem

# 3. Connectivity testing command (if applicable)
python -m project_name test-connection --debug
# REQUIRED: Tests external service connectivity through FLEXT APIs

# 4. Component testing commands
python -m project_name test-component --component=ldap --debug
python -m project_name test-component --component=ldif --debug
# REQUIRED: Individual component testing through FLEXT ecosystem
```

#### Forbidden Testing Patterns (ZERO TOLERANCE)

```bash
# ❌ ABSOLUTELY FORBIDDEN - External testing tools
ldapsearch -h localhost -p 3389           # FORBIDDEN - use CLI test commands
netcat -zv localhost 3389                 # FORBIDDEN - use CLI connectivity tests
telnet localhost 3389                     # FORBIDDEN - use CLI diagnostic commands

# ❌ ABSOLUTELY FORBIDDEN - Manual configuration testing
python -c "import os; print(os.getenv('HOST'))"  # FORBIDDEN - use CLI debug-config
export HOST=test && python app.py               # FORBIDDEN - use CLI parameters

# ❌ ABSOLUTELY FORBIDDEN - Custom testing scripts
python test_ldap_manual.py                      # FORBIDDEN - use CLI test commands
python validate_env_custom.py                   # FORBIDDEN - use CLI validate-environment
```

---

**The path to excellence is clear: Follow these standards precisely, validate continuously, never compromise on quality, and ALWAYS use FLEXT ecosystem for CLI testing and debugging with correct configuration priority (ENV → .env → DEFAULT → CLI) and automatic .env detection from current execution directory.**