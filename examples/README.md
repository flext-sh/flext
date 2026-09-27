# FLEXT Examples

<!-- TOC START -->

- [Key Features](#key-features)
  - [Examples Overview](#examples-overview)
  - 1. ACL Processing Example (`acl_processing_example.py`)
  - 1. Advanced Processing Example (`advanced_processing_example.py`)
  - 1. Complete Workflow Example (`complete_workflow_example.py`)
- [Architecture Patterns Demonstrated](#architecture-patterns-demonstrated)
  - [Railway Pattern](#railway-pattern)
  - [Parallel Processing](#parallel-processing)
  - [Type Safety](#type-safety)
  - [Enterprise Features](#enterprise-features)
- [Installation](#installation)
- [Usage](#usage)
  - [Usage Examples](#usage-examples)
  - [Basic ACL Processing](#basic-acl-processing)
  - [Advanced Processing Pipeline](#advanced-processing-pipeline)
  - [Complete Workflow](#complete-workflow)
- [Performance Characteristics](#performance-characteristics)
  - [Parallel Processing](#parallel-processing)
  - [Railway Pattern](#railway-pattern)
  - [Type Safety](#type-safety)
- [Integration with FLEXT Ecosystem](#integration-with-flext-ecosystem)
- [Contributing](#contributing)
- [License](#license)

<!-- TOC END -->

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Comprehensive examples demonstrating advanced FLEXT capabilities for enterprise data
integration.

**Reviewed**: 2026-02-17 | **Version**: 0.10.0-dev

Part of the [FLEXT](https://github.com/flext-sh/flext) ecosystem.

## Key Features

### Examples Overview

### 1. ACL Processing Example (`acl_processing_example.py`)

### ACL Processing through flext-ldif

The example injects the public LDIF client and composes its ACL extraction and
permission evaluation operations. `flext-ldif` owns the LDAP entry, ACL,
permission, server and result contracts.

**Key Features:**

- Constructor-injected LDIF client
- Native LDIF entry and ACL models
- Native `Result` failure propagation

### 2. Advanced Processing Example (`advanced_processing_example.py`)

### Advanced Processing with Current APIs

Demonstrates modern processing capabilities with updated APIs:

- **Parallel Processing**: Using `ThreadPoolExecutor` for concurrent operations.
- **Batch Processing**: Sequential processing for heavy operations.
- **Integrated Pipeline**: Combined processing, validation, and analysis stages.
- **Railway Pattern**: Error handling with early termination on failures.
- **Performance Analytics**: Comprehensive metrics across all processing stages.

**Key Features:**

- Advanced processor with settingsurable parallel execution
- Validation processor with parallel item checking
- Analysis processor for data insights and aggregation
- Batch heavy operations processor for memory-intensive tasks
- End-to-end pipeline integration

### 3. Complete Workflow Example (`complete_workflow_example.py`)

### Complete Workflow Integration

Demonstrates the complete FLEXT enterprise workflow with all capabilities integrated:

- **Comprehensive Railway Pattern**: Robust error handling across all stages.
- **Parallel Processing**: Parallel execution in all workflow stages.
- **Intelligent Auto-detection**: Automatic data source and pipeline configuration.
- **Smart Builders**: Dynamic workflow construction based on requirements.
- **End-to-End Validation**: Complete workflow validation with multiple aspects.

**Key Features:**

- Intelligent builder for workflow components
- Parallel stage executor with correlation tracking
- Comprehensive railway pattern for workflow orchestration
- End-to-end validation orchestrator
- Complete workflow builder with auto-configuration
- Performance analytics for entire workflows

## Architecture Patterns Demonstrated

### Railway Pattern

All examples implement the railway pattern for robust error handling:

- Operations return `r[T]` for type-safe error handling
- Pipeline stops on first failure (no exception propagation)
- Comprehensive error reporting and context tracking

### Parallel Processing

Extensive use of parallel processing throughout:

- `ThreadPoolExecutor` for concurrent operations
- Settingsurable worker thread pools
- Batch processing for memory efficiency
- Parallel validation and analysis stages

### Type Safety

Full type safety with modern Python features:

- `from **future** import annotations

from collections.abc import Mapping, Sequence` for forward references

- Comprehensive type hints throughout
- Generic types with proper variance
- Protocol-based design where appropriate

### Enterprise Features

Production-ready enterprise capabilities:

- Comprehensive logging and metrics
- Settingsurable processing parameters
- Performance analytics and monitoring
- Correlation ID tracking for distributed operations
- Context management across pipeline stages

## Installation

Ensure you have the required dependencies for the example scripts:

```bash
pip install flext-core flext-ldif flext-api
```

## Usage

### Usage Examples

### Basic ACL Processing

```python
from examples.acl_processing_example import FlextRootAclProcessingExample
from flext_ldif import c, ldif, m

client = ldif()
content = (
    "dn: cn=test,dc=example,dc=com\n"
    "objectClass: person\n"
    "cn: test\n"
    "sn: Example\n"
    'aci: (target="ldap:///cn=test,dc=example,dc=com")'
    '(targetattr="*")(version 3.0; acl "Allow read"; '
    'allow (read) userdn="ldap:///anyone";)\n'
)
entry = client.parse_ldif(content).unwrap().entries[0]
result = FlextRootAclProcessingExample(service=client).process_acls_with_pipeline(
    entry=entry,
    server_type=c.Ldif.ServerTypes.OUD,
    required_permissions=m.Ldif.AclPermissions(read=True),
)
print(result.unwrap().granted)
```

### Advanced Processing Pipeline

```python
from examples.advanced_processing_example import FlextRootAdvancedProcessingExample

# Build the real validation, processing, and analysis stages
pipeline = FlextRootAdvancedProcessingExample.FlextLdifProcessingPipeline(
    items=[{"id": "item_1", "name": "Sample", "value": "Data"}],
    stages=("validate", "process", "analyze"),
    max_workers=4,
)
result = pipeline.execute()
```

### Complete Workflow

```python
from examples import FlextRootCompleteWorkflow

# Build workflow configuration
settings = FlextRootCompleteWorkflow.build_comprehensive_workflow(
    workflow_type="ldap_processing", requirements={"max_workers": 8, "parallel": True}
)

# Execute complete workflow
railway = FlextRootCompleteWorkflow(max_workers=8)
input_data = {"entries": [{"dn": "cn=test,dc=example,dc=com"}]}
result = railway.execute_workflow_railway(
    workflow_id="enterprise_workflow",
    input_data=input_data,
    stage_definitions=settings["stage_definitions"],
    workflow_requirements=settings,
)
```

## Performance Characteristics

### Parallel Processing

- **Scalability**: Linear scaling with worker threads
- **Memory efficiency**: Batch processing prevents memory exhaustion
- **CPU utilization**: Optimal thread pool sizing based on workload

### Railway Pattern

- **Error resilience**: Fail-fast behavior prevents cascading failures
- **Debugging**: Comprehensive error context and correlation tracking
- **Monitoring**: Detailed performance metrics at each stage

### Type Safety

- **IDE support**: Full autocomplete and type checking
- **Runtime safety**: Pydantic validation where applicable
- **Maintainability**: Self-documenting code with type hints

## Integration with FLEXT Ecosystem

These examples demonstrate integration with the complete FLEXT ecosystem:

- **FLEXT-LDIF**: LDAP-specific processing capabilities
- **FLEXT-Core**: Foundation patterns and utilities
- **FLEXT-Result**: Railway pattern implementation

## Contributing

We welcome contributions! Please see our Contributing Guide for details.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for
details.
