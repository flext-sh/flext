# PROJECT-NAME

**Type**: [Library|Application|Infrastructure|Service] | **Status**: [Development|Production|Active Development] | **Dependencies**: flext-core

**Brief description of what this project does and its role in the FLEXT ecosystem**

> **⚠️ Development Status**: Current realistic status - what works vs what doesn't

## Quick Start

```bash
# Basic setup commands
poetry install

# Test the project works
python -c "from project_name import MainApi; print('✅ Working')"

# Development setup
make setup
```

## Current Reality

**What Actually Works:**

- List specific working features
- No inflated claims or marketing language
- Focus on demonstrable functionality

**What Needs Work:**

- Honest assessment of gaps
- Integration issues
- Performance or completeness concerns

## Architecture Role in FLEXT Ecosystem

### **[Layer] Component**

Brief explanation of where this fits in the FLEXT ecosystem:

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLEXT ECOSYSTEM (32 Projects)                 │
├─────────────────────────────────────────────────────────────────┤
│ Services: FlexCore(Go) | FLEXT Service(Go/Python) | Clients     │
├─────────────────────────────────────────────────────────────────┤
│ Applications: API | Auth | Web | CLI | Quality | Observability  │
├═════════════════════════════════════════════════════════════════┤
│ Infrastructure: [PROJECT HIGHLIGHTED] | Other components        │
├─────────────────────────────────────────────────────────────────┤
│ Singer Ecosystem: Taps(5) | Targets(5) | DBT(4) | Extensions(1) │
├─────────────────────────────────────────────────────────────────┤
│ Foundation: FLEXT-CORE (FlextResult | DI | Domain Patterns)     │
└─────────────────────────────────────────────────────────────────┘
```

### **Core Responsibilities**

1. **Primary Function**: Main responsibility
2. **Integration**: How it connects to other projects
3. **Patterns Used**: flext-core patterns implemented

## Key Features

### **Current Capabilities**

- **Feature 1**: Brief description with realistic scope
- **Feature 2**: What actually works today
- **Feature 3**: Integration status

### **FLEXT Core Integration**

- **FlextResult Pattern**: Type-safe error handling
- **Configuration Management**: Environment-aware settings
- **Structured Logging**: Correlation ID support

## Installation & Usage

### Installation

```bash
# Clone and install
cd /path/to/project
poetry install

# Development setup
make setup
```

### Basic Usage

```python
from project_name import MainApi

# Simple example that actually works
api = MainApi()
result = api.basic_operation()
if result.success:
    print(f"Success: {result.data}")
else:
    print(f"Error: {result.error}")
```

## Development Commands

### Quality Gates (Zero Tolerance)

```bash
# Complete validation pipeline (run before commits)
make validate              # Full validation pipeline
make check                 # Quick lint + type check
make test                  # Run all tests
make lint                  # Code linting
make type-check
make format                # Code formatting
make security              # Security scanning
```

### Project-Specific Commands

```bash
# Commands specific to this project's function
make [project-specific-command]    # Description
```

## Configuration

### Environment Variables

```bash
# Required configuration
export PROJECT_SETTING_1=value
export PROJECT_SETTING_2=value

# Optional settings
export PROJECT_OPTIONAL=value
```

## Quality Standards

### **Zero Tolerance Quality Gates**

- **Coverage**: 90% test coverage enforced
- **Type Safety**: Strict MyPy configuration
- **Linting**: Ruff with rules
- **Security**: Bandit + pip-audit scanning

## Integration with FLEXT Ecosystem

### **FLEXT Core Patterns**

```python
# FlextResult for all operations
def operation(self) -> FlextResult[DataType]:
    try:
        result = self._perform_operation()
        return FlextResult[None].ok(result)
    except Exception as e:
        return FlextResult[None].fail(f"Operation failed: {e}")
```

### **Service Integration**

- **Related projects**: List actual dependencies
- **Integration points**: How this connects to other services
- **Data flow**: Brief description of data movement

## Current Status

**Version**: X.Y.Z (Current)

**Completed**:

- ✅ List actual completed features
- ✅ No inflated claims

**In Progress**:

- 🔄 Current development work
- 🔄 Integration tasks

**Planned**:

- 📋 Future features
- 📋 Integration improvements

## Contributing

### Development Standards

- **FLEXT Core Integration**: Use established patterns
- **Type Safety**: All code must pass MyPy
- **Testing**: Maintain coverage and ensure tests pass
- **Code Quality**: Follow linting rules

### Development Workflow

```bash
# Setup and validate
make setup
make validate
make test
```

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Links

- **[flext-core](../flext-core)**: Foundation library
- **[Documentation](docs/)**: Complete documentation
- **[FLEXT Ecosystem](/)**: Main project

---
