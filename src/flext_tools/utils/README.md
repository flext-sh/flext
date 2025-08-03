# FLEXT Tools Utils - Essential Utility Framework

**Version 2.0.0** | **Type: Utility Framework** | **Integration: FLEXT Core Utilities**

Comprehensive utility framework for the FLEXT ecosystem with essential helper functions, path management, logging infrastructure, and standard library extensions across all 33 FLEXT projects.

## 📋 Module Overview

### **Purpose**

Provides enterprise-grade utility functions and helper libraries for common operations across the FLEXT ecosystem with standardized logging, path management, color output, and standard library extensions for enhanced development productivity.

### **Architecture Position**

- **Layer**: Infrastructure Tools (Core Utilities)
- **Dependencies**: flext-core, standard library, colorama
- **Consumers**: All FLEXT projects requiring utility functions and helpers
- **Ecosystem Role**: Foundation utility layer for common operations and patterns

## 🎯 Key Components

### **Utility Tools**

#### **colors.py** - Enhanced Terminal Output

- **Purpose**: Color-enhanced terminal output and formatting utilities
- **Features**: ANSI color support, formatting helpers, theme management
- **Integration**: Console output enhancement for CLI tools and logging
- **Usage**: `from flext_tools.utils.colors import ColorFormatter, Colors`

#### **logging.py** - Enterprise Logging Infrastructure

- **Purpose**: Comprehensive logging configuration and management
- **Features**: Structured logging, multi-handler support, correlation IDs
- **Integration**: Centralized logging across all FLEXT ecosystem projects
- **Usage**: `from flext_tools.utils.logging import get_logger, setup_logging`

#### **paths.py** - Path Management and Utilities

- **Purpose**: Advanced path manipulation and workspace management
- **Features**: Cross-platform paths, workspace discovery, validation
- **Integration**: Standardized path handling across FLEXT projects
- **Usage**: `from flext_tools.utils.paths import WorkspacePath, resolve_path`

#### **stdlib.py** - Standard Library Extensions

- **Purpose**: Extended standard library functionality and patterns
- **Features**: Enhanced data structures, utility functions, performance helpers
- **Integration**: Common utility patterns for FLEXT development
- **Usage**: `from flext_tools.utils.stdlib import enhanced_dict, timing_context`

## 🚀 Quick Start

### **Enhanced Terminal Output**

```python
from flext_tools.utils.colors import Colors, ColorFormatter
from flext_tools.utils.colors import success, warning, error, info

# Basic color output
print(Colors.GREEN + "Success message" + Colors.RESET)
print(Colors.YELLOW + "Warning message" + Colors.RESET)
print(Colors.RED + "Error message" + Colors.RESET)

# Enhanced color helpers
success("Operation completed successfully!")
warning("Configuration file not found, using defaults")
error("Failed to connect to database")
info("Processing 1,000 records...")

# Advanced formatting
formatter = ColorFormatter(
    theme="professional",
    enable_icons=True,
    enable_timestamps=True
)

# Format messages with context
formatted_success = formatter.format_success(
    message="Deployment completed",
    context={"environment": "production", "duration": "45s"}
)

formatted_error = formatter.format_error(
    message="Validation failed",
    context={"errors": 3, "warnings": 7},
    details="See log file for complete error details"
)

print(formatted_success)
print(formatted_error)

# Progress indicators
from flext_tools.utils.colors import ProgressIndicator

progress = ProgressIndicator(
    total=100,
    description="Processing data",
    show_percentage=True,
    show_eta=True,
    color_scheme="gradient"
)

for i in range(100):
    # Simulate work
    time.sleep(0.1)
    progress.update(i + 1)

progress.finish("Data processing completed!")
```

### **Enterprise Logging Setup**

```python
from flext_tools.utils.logging import setup_logging, get_logger
from flext_tools.utils.logging import LogConfig, LogLevel

# Configure enterprise logging
log_config = LogConfig(
    level=LogLevel.INFO,
    format="structured",  # structured, simple, detailed
    output="both",        # console, file, both
    log_file="/var/log/flext/application.log",
    rotation_size="10MB",
    rotation_count=5,
    correlation_id=True,
    performance_logging=True,
    security_logging=True
)

# Initialize logging system
setup_logging(log_config)

# Get configured logger
logger = get_logger(__name__)

# Structured logging with context
logger.info(
    "User authentication successful",
    extra={
        "user_id": "user123",
        "session_id": "sess_abc123",
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0...",
        "authentication_method": "oauth2"
    }
)

# Performance logging
with logger.performance_context("database_query"):
    # Database operation
    result = execute_complex_query()
    logger.info(f"Query returned {len(result)} records")

# Error logging with context
try:
    risky_operation()
except Exception as e:
    logger.error(
        "Operation failed",
        extra={
            "operation": "data_processing",
            "input_size": 1000,
            "error_type": type(e).__name__,
            "stack_trace": traceback.format_exc()
        },
        exc_info=True
    )

# Security logging
logger.security(
    "Potential security violation detected",
    extra={
        "violation_type": "unusual_access_pattern",
        "user_id": "user123",
        "resource": "/admin/sensitive_data",
        "risk_level": "medium"
    }
)
```

### **Advanced Path Management**

```python
from flext_tools.utils.paths import WorkspacePath, resolve_path
from flext_tools.utils.paths import find_project_root, validate_path
from pathlib import Path

# Initialize workspace path management
workspace = WorkspacePath("/workspace/flext")

# Intelligent path resolution
config_path = workspace.resolve("config/production.yaml")
data_path = workspace.resolve("data/processed/")
temp_path = workspace.resolve("temp/", create_if_missing=True)

print(f"Config: {config_path}")
print(f"Data: {data_path}")
print(f"Temp: {temp_path}")

# Project discovery and validation
project_root = find_project_root(
    start_path=Path.cwd(),
    markers=["pyproject.toml", ".git", "CLAUDE.md"]
)

if project_root:
    print(f"Project root found: {project_root}")

    # Validate project structure
    validation_result = validate_path(
        project_root,
        required_structure=[
            "src/",
            "tests/",
            "pyproject.toml",
            "README.md"
        ]
    )

    if validation_result.valid:
        print("✅ Project structure is valid")
    else:
        print("❌ Project structure issues:")
        for issue in validation_result.issues:
            print(f"  - {issue}")

# Cross-platform path handling
safe_path = resolve_path(
    base_path="/workspace/flext",
    relative_path="../../../etc/passwd",  # Potential security risk
    security_check=True,
    normalize=True
)

print(f"Resolved path: {safe_path}")  # Will be contained within workspace

# Path utilities for FLEXT projects
flext_paths = workspace.get_project_paths("flext-core")
print(f"Source: {flext_paths.source}")
print(f"Tests: {flext_paths.tests}")
print(f"Docs: {flext_paths.docs}")
print(f"Config: {flext_paths.config}")
```

### **Standard Library Extensions**

```python
from flext_tools.utils.stdlib import enhanced_dict, timing_context
from flext_tools.utils.stdlib import retry_with_backoff, memoize
from flext_tools.utils.stdlib import chunked, flatten

# Enhanced dictionary with dot notation
config = enhanced_dict({
    "database": {
        "host": "localhost",
        "port": 5432,
        "credentials": {
            "username": "flext_user",
            "password": "secure_password"
        }
    },
    "api": {
        "host": "0.0.0.0",
        "port": 8080,
        "timeout": 30
    }
})

# Dot notation access
db_host = config.database.host
db_user = config.database.credentials.username
api_timeout = config.api.timeout

print(f"Database: {db_host}:{config.database.port}")
print(f"API timeout: {api_timeout}s")

# Performance timing context
with timing_context("data_processing") as timer:
    # Simulate data processing
    processed_data = process_large_dataset(data)

print(f"Processing completed in {timer.elapsed:.2f}s")

# Retry with intelligent backoff
@retry_with_backoff(
    max_attempts=3,
    backoff_strategy="exponential",
    initial_delay=1.0,
    max_delay=60.0,
    exceptions=(ConnectionError, TimeoutError)
)
async def unreliable_api_call(endpoint: str) -> dict:
    """API call with automatic retry on failures."""
    response = await http_client.get(endpoint)
    return response.json()

# Memoization for expensive operations
@memoize(ttl=3600, max_size=100)
def expensive_calculation(data: list) -> float:
    """Expensive calculation with caching."""
    return sum(x ** 2 for x in data) / len(data)

# Data processing utilities
large_list = list(range(10000))

# Process data in chunks
for chunk in chunked(large_list, chunk_size=100):
    process_chunk(chunk)

# Flatten nested structures
nested_data = [[1, 2], [3, 4], [5, [6, 7]]]
flat_data = list(flatten(nested_data))
print(f"Flattened: {flat_data}")  # [1, 2, 3, 4, 5, 6, 7]
```

## 📊 Utility Patterns

### **Logging Strategies**

- **Structured Logging**: JSON-formatted logs for machine processing
- **Contextual Logging**: Rich context information for debugging
- **Performance Logging**: Execution time and resource usage tracking
- **Security Logging**: Security events and audit trail logging

### **Path Management**

- **Workspace-Aware Paths**: Intelligent workspace-relative path resolution
- **Security-Conscious**: Path traversal attack prevention
- **Cross-Platform**: Consistent path handling across operating systems
- **Project Discovery**: Automatic project structure detection and validation

## 🔧 Configuration

### **Logging Configuration**

```python
# Comprehensive logging configuration
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "structured": {
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(correlation_id)s | %(message)s",
            "class": "flext_tools.utils.logging.StructuredFormatter"
        },
        "detailed": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)-20s | %(filename)s:%(lineno)d | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "structured",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": "/var/log/flext/application.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        },
        "security": {
            "class": "logging.handlers.SysLogHandler",
            "level": "WARNING",
            "formatter": "structured",
            "address": "/dev/log",
            "facility": "auth"
        }
    },
    "loggers": {
        "flext": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False
        },
        "flext.security": {
            "level": "INFO",
            "handlers": ["console", "file", "security"],
            "propagate": False
        }
    },
    "root": {
        "level": "WARNING",
        "handlers": ["console"]
    }
}
```

### **Color Theme Configuration**

```python
# Color theme configuration
color_themes = {
    "professional": {
        "success": Colors.GREEN,
        "warning": Colors.YELLOW,
        "error": Colors.RED,
        "info": Colors.BLUE,
        "debug": Colors.CYAN,
        "highlight": Colors.MAGENTA,
        "reset": Colors.RESET
    },
    "accessibility": {
        "success": Colors.BOLD + Colors.GREEN,
        "warning": Colors.BOLD + Colors.YELLOW,
        "error": Colors.BOLD + Colors.RED,
        "info": Colors.BOLD + Colors.BLUE,
        "debug": Colors.DIM + Colors.CYAN,
        "highlight": Colors.BOLD + Colors.WHITE,
        "reset": Colors.RESET
    },
    "minimal": {
        "success": "",
        "warning": Colors.DIM,
        "error": Colors.BOLD,
        "info": "",
        "debug": Colors.DIM,
        "highlight": Colors.BOLD,
        "reset": Colors.RESET
    }
}
```

## 📈 Performance Optimization

### **Utility Performance**

- **Lazy Loading**: Lazy initialization of expensive utilities
- **Caching**: Intelligent caching of frequently used operations
- **Memory Efficiency**: Memory-efficient data structures and algorithms
- **CPU Optimization**: CPU-optimized algorithms for common operations

### **Logging Performance**

- **Async Logging**: Asynchronous logging for high-throughput applications
- **Log Level Filtering**: Efficient log level filtering at source
- **Structured Data**: Efficient serialization of structured log data
- **Buffer Management**: Intelligent log buffer management and flushing

## 🔗 Integration Points

### **Development Tools Integration**

- **IDE Integration**: Enhanced IDE support with intelligent utilities
- **Debugging**: Debugging-friendly utilities with clear error messages
- **Testing**: Testing utilities for mock data and test helpers
- **Documentation**: Automatic documentation generation from utility functions

### **Ecosystem Integration**

- **Core Integration**: Deep integration with flext-core patterns
- **Quality Gates**: Utility validation in quality assurance processes
- **Monitoring**: Integration with monitoring and observability systems
- **Security**: Security-conscious utility design and implementation

### **External Tool Integration**

- **CLI Tools**: Enhanced CLI experience with color and formatting
- **Log Aggregation**: Integration with log aggregation systems
- **Monitoring**: Integration with application performance monitoring
- **Documentation**: Integration with documentation generation tools

## 📚 Best Practices

### **Utility Design**

- **Single Responsibility**: Each utility has a clear, single purpose
- **Error Handling**: Comprehensive error handling with meaningful messages
- **Documentation**: Clear documentation with usage examples
- **Testing**: Comprehensive testing of utility functions

### **Performance Considerations**

- **Efficiency**: Optimized algorithms and data structures
- **Memory Management**: Careful memory usage and cleanup
- **Caching**: Intelligent caching where appropriate
- **Profiling**: Regular performance profiling and optimization

### **Security Considerations**

- **Input Validation**: Comprehensive input validation and sanitization
- **Path Security**: Secure path handling and traversal prevention
- **Logging Security**: Secure logging without sensitive data exposure
- **Access Control**: Appropriate access control for utility functions

## 📚 Documentation

- **[Utilities Guide](../../../docs/utilities-guide.md)** - Comprehensive utility usage patterns
- **[Logging Guide](../../../docs/logging-guide.md)** - Enterprise logging strategies
- **[Development Guide](../../../docs/development-guide.md)** - Development utility patterns

---

**Navigation**: [FLEXT Hub](../../../docs/NAVIGATION.md) > Tools > Utils
**Parent Module**: [flext_tools](../README.md)
**Related**: [Core Tools](../core/README.md) | [Quality Tools](../quality/README.md)
