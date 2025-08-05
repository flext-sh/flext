# FLEXT Quick Reference

**Version**: 1.0.0 | **Last Updated**: 2025-01-08

## 🚀 Quick Navigation

### Documentation Structure

```
docs/
├── README.md              # Main index
├── quick-reference.md     # This file
├── architecture/          # System design
├── patterns/              # Coding patterns
├── api/                   # API documentation
├── guides/                # User guides
├── standards/             # Coding standards
└── development/           # Dev planning
```

## 📝 Common Patterns

### Creating Models

```python
from flext_core.foundation import FlextEntity, FlextValue

class User(FlextEntity):
    username: str
    email: Email

class Email(FlextValue):
    address: str
    verified: bool = False
```

### Handling Errors

```python
from flext_core.errors import FlextBusinessError, FlextResult

def process() -> FlextResult[str]:
    try:
        # operation
        return FlextResult.ok("success")
    except Exception as e:
        return FlextResult.fail(str(e))
```

### Configuration

```python
from flext_core.config import FlextConfigHierarchical

config = FlextConfigHierarchical()
value = config.get_config("key").unwrap_or("default")
```

### Using Types

```python
from flext_core.types import FlextTypes

connection: FlextTypes.Data.Connection
query: FlextTypes.Data.Query
result: FlextTypes.Core.Result
```

## 🎯 Common Tasks

| Task | Documentation |
|------|---------------|
| Setup development | [Getting Started](./guides/getting-started/README.md) |
| Deploy application | [Deployment Guide](./guides/deployment/README.md) |
| Configure service | [Configuration](./guides/configuration/README.md) |
| Debug issues | [Troubleshooting](./guides/troubleshooting/README.md) |
| Understand architecture | [Architecture](./architecture/overview.md) |
| Use patterns | [Patterns](./patterns/README.md) |
| API reference | [API Docs](./api/README.md) |

## 📚 Pattern References

| Pattern | File | Purpose |
|---------|------|---------|
| Foundation | [patterns/foundation.md](./patterns/foundation.md) | Base models & results |
| Types | [patterns/types.md](./patterns/types.md) | Type system |
| Config/CLI | [patterns/config-cli.md](./patterns/config-cli.md) | Configuration |
| Errors | [patterns/error-observability.md](./patterns/error-observability.md) | Error handling |
| Constants | [patterns/constants.md](./patterns/constants.md) | Semantic constants |
| Utilities | [patterns/utilities.md](./patterns/utilities.md) | Helper functions |

## 🔧 CLI Commands

```bash
# Development
make install          # Install dependencies
make test            # Run tests
make lint            # Run linters
make format          # Format code

# Docker
docker-compose up    # Start services
docker-compose down  # Stop services

# FLEXT CLI
flext pipeline list  # List pipelines
flext tap list       # List data sources
flext target list    # List destinations
```

## 📦 Project Structure

```
flext/                    # Control Panel (Go)
├── cmd/                  # CLI applications
├── pkg/                  # Public packages
├── internal/             # Private code
└── docs/                 # Documentation

flext-*/                  # Library projects (Python)
├── src/                  # Source code
├── tests/                # Test files
├── docs/                 # Project docs
└── pyproject.toml        # Project config
```

## 🔗 Key Links

- **GitHub**: [github.com/flext-sh/flext](https://github.com/flext-sh/flext)
- **Issues**: [GitHub Issues](https://github.com/flext-sh/flext/issues)
- **Discussions**: [GitHub Discussions](https://github.com/flext-sh/flext/discussions)

---

For detailed information, see the [main documentation index](./README.md).
