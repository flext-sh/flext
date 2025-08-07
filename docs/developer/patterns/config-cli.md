# Configuration & CLI Patterns

**Version**: 1.0.0 | **Status**: Active | **Python**: 3.13+

## Overview

Unified, hierarchical configuration management and command-line interface patterns. Ensures consistent precedence, clear separation between interface and implementation, and seamless environment integration.

## Core Principles

### Configuration Hierarchy

Clear precedence order (highest to lowest):

```
1. CLI Arguments      (--timeout 30)
2. Environment Vars   (FLEXT_TIMEOUT=30)
3. .env Files        (TIMEOUT=30 in .env)
4. Config Files      (timeout: 30 in config.yaml)
5. Constants         (DEFAULT_TIMEOUT = 30)
```

### Provider-Based Architecture

Pluggable configuration sources with consistent interface.

### Separation of Concerns

- **flext-core**: Defines interfaces and protocols
- **flext-cli**: Provides concrete CLI implementation
- **Projects**: Extend with domain-specific configuration

## Configuration Foundation

```python
from typing import Any, Protocol, runtime_checkable, Dict, List, Optional
from pathlib import Path

class FlextConfigSemanticConstants:
    """Configuration semantic constants."""

    class Hierarchy:
        """Configuration precedence priorities."""
        CLI_PRIORITY = 1        # Highest precedence
        ENV_PRIORITY = 2        # Environment variables
        DOTENV_PRIORITY = 3     # .env files
        CONFIG_PRIORITY = 4     # Configuration files
        CONSTANTS_PRIORITY = 5  # Default constants (lowest)

    class Sources:
        """Configuration source identifiers."""
        CLI = "cli"
        ENVIRONMENT = "environment"
        DOTENV = "dotenv"
        CONFIG_FILE = "config_file"
        CONSTANTS = "constants"

    class Files:
        """Standard configuration file patterns."""
        DOTENV_FILES = [".env", ".env.local", ".env.development", ".env.production"]
        CONFIG_FILES = ["config.json", "config.yaml", "config.toml", "pyproject.toml"]
```

## Hierarchical Configuration System

```python
class FlextConfigHierarchical:
    """Hierarchical configuration management with provider system."""

    def __init__(self) -> None:
        self._providers: List[FlextConfigProvider] = []
        self._cache: Dict[str, Any] = {}
        self._transformers: Dict[str, Callable] = {}

    def register_provider(self, provider: FlextConfigProvider) -> FlextResult[None]:
        """Register configuration provider with automatic priority sorting."""
        try:
            # Check for duplicate priorities
            existing_priorities = [p.get_priority() for p in self._providers]
            if provider.get_priority() in existing_priorities:
                return FlextResult.fail(f"Provider with priority {provider.get_priority()} already exists")

            self._providers.append(provider)
            self._providers.sort(key=lambda p: p.get_priority())
            self._cache.clear()

            return FlextResult.ok(None)
        except Exception as e:
            return FlextResult.fail(f"Failed to register provider: {e}")

    def get_config(self, key: str, default: Any = None) -> FlextResult[Any]:
        """Get configuration value following hierarchical precedence."""
        if key in self._cache:
            return FlextResult.ok(self._cache[key])

        for provider in self._providers:
            result = provider.get_config(key, None)
            if result.success and result.data is not None:
                value = self._apply_transformers(key, result.data)
                self._cache[key] = value
                return FlextResult.ok(value)

        return FlextResult.ok(default)

    def get_all_configs(self) -> Dict[str, Any]:
        """Get all configuration values merged by precedence."""
        all_configs = {}

        for provider in reversed(self._providers):
            if hasattr(provider, 'get_all'):
                provider_configs = provider.get_all()
                all_configs.update(provider_configs)

        return all_configs
```

## Configuration Providers

### Environment Variable Provider

```python
class FlextEnvironmentProvider:
    """Environment variable configuration provider."""

    def __init__(self, prefix: str = "FLEXT_") -> None:
        self.prefix = prefix

    def get_config(self, key: str, default: Any = None) -> FlextResult[Any]:
        """Get configuration from environment variables."""
        import os

        env_key = f"{self.prefix}{key.upper().replace('.', '_')}"
        value = os.environ.get(env_key, default)
        return FlextResult.ok(value)

    def get_priority(self) -> int:
        return FlextConfigSemanticConstants.Hierarchy.ENV_PRIORITY
```

### Configuration File Provider

```python
class FlextConfigFileProvider:
    """Configuration file provider supporting JSON, YAML, TOML."""

    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration file based on extension."""
        if not self.config_path.exists():
            return

        try:
            content = self.config_path.read_text()

            if self.config_path.suffix == '.json':
                import json
                self._config = json.loads(content)
            elif self.config_path.suffix in ['.yaml', '.yml']:
                import yaml
                self._config = yaml.safe_load(content)
            elif self.config_path.suffix == '.toml':
                import toml
                self._config = toml.loads(content)
        except Exception:
            pass  # Silently fail for optional config files

    def get_config(self, key: str, default: Any = None) -> FlextResult[Any]:
        """Get configuration value using dot notation."""
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return FlextResult.ok(default)

        return FlextResult.ok(value)

    def get_priority(self) -> int:
        return FlextConfigSemanticConstants.Hierarchy.CONFIG_PRIORITY
```

## CLI Interface Protocol

```python
@runtime_checkable
class FlextCliProvider(Protocol):
    """Protocol for CLI argument providers."""

    def parse_args(self, args: Optional[List[str]] = None) -> FlextResult[Dict[str, Any]]: ...
    def get_config(self, key: str, default: Any = None) -> FlextResult[Any]: ...
    def get_priority(self) -> int: ...
```

## Usage Examples

### Basic Configuration Setup

```python
from flext_core.config import FlextConfigHierarchical
from flext_cli import FlextCliImplementation
from pathlib import Path

# Create configuration hierarchy
config = FlextConfigHierarchical()

# Register CLI provider (highest priority)
cli = FlextCliImplementation(prog="myapp", description="My FLEXT Application")
cli.add_argument("host", help="Database host", default="localhost")
cli.add_argument("port", help="Database port", type=int, default=5432)

args_result = cli.parse_args()
if args_result.success:
    config.register_provider(cli)

# Register other providers
config.register_provider(FlextEnvironmentProvider(prefix="MYAPP_"))
config.register_provider(FlextDotenvProvider(Path(".env")))
config.register_provider(FlextConfigFileProvider(Path("config.yaml")))

# Get configuration values
host = config.get_config("host").unwrap_or("localhost")
port = config.get_config("port").unwrap_or(5432)
```

### Pydantic Settings Integration

```python
from pydantic import Field
from flext_core.config import FlextBaseSettings

class DatabaseSettings(FlextBaseSettings):
    """Database configuration with hierarchy support."""

    host: str = Field("localhost", description="Database host")
    port: int = Field(5432, description="Database port")
    database: str = Field(..., description="Database name")
    username: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")

    pool_size: int = Field(10, description="Connection pool size")
    pool_timeout: int = Field(30, description="Pool timeout in seconds")

    class Config:
        env_prefix = "DB_"
        case_sensitive = False

# Create settings with hierarchy
def create_database_config(cli_args: Dict[str, Any]) -> FlextResult[DatabaseSettings]:
    config = FlextConfigHierarchical()

    # Register providers
    cli_provider = FlextCliImplementation()
    cli_provider._parsed_args = cli_args
    config.register_provider(cli_provider)
    config.register_provider(FlextEnvironmentProvider("DB_"))
    config.register_provider(FlextDotenvProvider())

    # Collect configuration
    all_config = {}
    for field_name in DatabaseSettings.__fields__:
        result = config.get_config(field_name)
        if result.success and result.data is not None:
            all_config[field_name] = result.data

    try:
        settings = DatabaseSettings(**all_config)
        return FlextResult.ok(settings)
    except Exception as e:
        return FlextResult.fail(f"Invalid configuration: {e}")
```

### CLI with Subcommands

```python
# Create main CLI
cli = FlextCliImplementation(prog="flext-tool", description="FLEXT Multi-Tool CLI")

# Add global arguments
cli.add_argument("config", short="c", help="Config file path")
cli.add_argument("verbose", short="v", action="count", help="Verbosity")

# Add 'extract' subcommand
extract_cli = cli.add_subcommand("extract", help="Extract data from source")
extract_cli.add_argument("source", help="Data source", required=True)
extract_cli.add_argument("format", help="Output format", choices=["json", "csv"])

# Add 'transform' subcommand
transform_cli = cli.add_subcommand("transform", help="Transform data")
transform_cli.add_argument("input", help="Input file", required=True)
transform_cli.add_argument("rules", help="Transformation rules file")

# Parse and execute
def main():
    args_result = cli.parse_args()

    if args_result.is_failure:
        if args_result.error_code == "CLI_HELP":
            return 0  # Help is not an error
        print(f"Error: {args_result.error}")
        return 1

    args = args_result.data
    command = args.get("command")

    if command == "extract":
        return handle_extract(args)
    elif command == "transform":
        return handle_transform(args)
    else:
        print("Please specify a command")
        return 1
```

## Quality Standards

- **Clear Precedence**: Always respect hierarchy order
- **Type Safety**: Use type hints and validation
- **Error Handling**: Return FlextResult for all operations
- **Documentation**: Document all configuration options
- **Defaults**: Provide sensible defaults

## Related Patterns

- [Foundation](./foundation.md) - FlextConfig base class
- [Constants](./constants.md) - Default values
- [Type System](./types.md) - Configuration types

---

**Configuration & CLI Patterns** - Unified hierarchical configuration management that ensures consistency and flexibility across the FLEXT ecosystem.
