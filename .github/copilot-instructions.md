# FLEXT Ecosystem Copilot Instructions

## Project Overview

FLEXT is an enterprise-grade distributed data integration platform implementing Clean Architecture, Domain-Driven Design (DDD), and CQRS patterns. It consists of **32+ Python projects** in a monorepo workspace with dual-service architecture: **FLEXT Control Panel** (port 8081) and **FlexCore Runtime** (port 8080).

## Architecture Foundation

### Railway-Oriented Programming (Critical Pattern)
All FLEXT components use `FlextResult[T]` for type-safe error handling instead of exceptions:

```python
from flext_core import FlextResult

def process_data(data: dict) -> FlextResult[ProcessingResult]:
    if not data:
        return FlextResult[ProcessingResult].fail("Empty data")
    return FlextResult[ProcessingResult].ok(process(data))

# Chain operations with automatic error propagation
result = (process_data(input_data)
    .map(lambda x: transform(x))
    .flat_map(lambda x: save_to_database(x)))
```

**Critical**: Always return `FlextResult[T]` instead of raising exceptions. Use `.success`, `.value`, `.error` properties for result handling.

### Project Structure Patterns
- **flext-core**: Foundation library (FlextResult, FlextContainer, FlextConfig)
- **flext-api**: HTTP foundation with FastAPI integration
- **flext-meltano**: Singer/Meltano/DBT integration hub
- **flext-db-***: Database abstraction layers
- **flext-tap-***: Singer extractors (data sources)
- **flext-target-***: Singer loaders (data destinations)
- **flext-dbt-***: DBT transformation projects

## Essential Development Workflows

### Quality Gates (Strict Enforcement)
```bash
# Run comprehensive checks before committing
make check                    # All quality checks
make test-all                # All test suites (90% minimum coverage)
make lint                     # mypy strict mode + ruff
```

**Type Safety**: Python 3.13+ with strict mypy/pyright compliance. All code must have explicit type annotations.

### Workspace Commands
```bash
# Development setup
make install                  # Install all 32+ projects in dev mode
make dev                      # Start development environment
make services                 # Start FLEXT Control Panel + FlexCore

# Testing patterns
make test-unit               # Unit tests only
make test-integration        # Integration tests
make ecosystem               # Full ecosystem test
```

### Docker Orchestration
```bash
# Start complete platform
docker compose up -d         # PostgreSQL, Redis, FLEXT services

# Individual service testing
cd flext-meltano && docker compose up -d    # Meltano environment
cd flexcore && docker compose up -d         # FlexCore runtime
```

## Singer/Meltano Integration Patterns

### Meltano Configuration (meltano.yml)
FLEXT uses Meltano for orchestrating Singer taps/targets with enterprise patterns:

```yaml
plugins:
  extractors:
    - name: tap-oracle
      pip_url: flext-tap-oracle
      settings:
        - name: host
          kind: string
        - name: service_name
          kind: string
  loaders:
    - name: target-oracle
      pip_url: flext-target-oracle
```

### Singer Development Pattern
All Singer components follow FLEXT foundation patterns:

```python
from flext_core import FlextResult, FlextConfig
from flext_db_oracle import FlextDbOracleManager

class FlextTapOracle(Tap):
    def discover_catalog(self) -> FlextResult[Catalog]:
        # Always return FlextResult, never raise exceptions
        db_result = self.db_manager.get_schema_metadata()
        if not db_result.success:
            return FlextResult[Catalog].fail(f"Schema discovery failed: {db_result.error}")
        
        return FlextResult[Catalog].ok(self._build_catalog(db_result.value))
```

## Code Quality Standards

### Type Annotations (Required)
- Use explicit types for all function signatures
- Avoid `Any` type - use specific types or Union
- Add type comments for complex generic patterns:

```python
# Good
def process_records(records: list[dict[str, str | int]]) -> FlextResult[ProcessingResult]:
    
# Avoid
def process_records(records):  # Missing types
def process_records(records: Any) -> Any:  # Too generic
```

### Testing Patterns
- Use `pytest` with factory-boy for test data
- Mock external dependencies with `pytest-mock`
- Test both success and failure paths with FlextResult
- Achieve 90%+ test coverage

### Configuration Management
All projects use `FlextConfig` with Pydantic for configuration:

```python
from flext_core import FlextConfig

class MyProjectSettings(FlextConfig):
    database_url: str
    api_timeout: int = 30
    
    class Config:
        env_prefix = "MY_PROJECT_"
```

## Common Gotchas

1. **FlextResult Chains**: Always handle both success/failure cases
2. **Import Paths**: Use `from flext_core import` not `from flext_core.result import`
3. **Database Connections**: Use connection pooling patterns from flext-db-* libraries
4. **Singer Messages**: Follow Singer SDK patterns exactly for tap/target compatibility
5. **Go Integration**: FlexCore (Go) communicates with FLEXT Service via REST APIs on ports 8080/8081

## Key Files to Reference

- `/docs/patterns/` - FLEXT architectural patterns
- `flext-core/examples/` - Foundation pattern examples
- `Makefile` - Workspace development commands
- `docker-compose.yml` - Service orchestration
- `pyproject.toml` - Python 3.13+ dependency management

## Error Handling Philosophy

FLEXT embraces explicit error handling through railway-oriented programming. Never use try/catch blocks - always return FlextResult and chain operations functionally. This ensures error paths are visible, testable, and composable across the entire 32-project ecosystem.
