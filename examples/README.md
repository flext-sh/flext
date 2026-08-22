# FLEXT Examples

<!-- TOC START -->

- [Key Features](#key-features)
  - [Examples Overview](#examples-overview)
  - [1. ACL Processing Example (`acl_processing_example.py`)](#1-acl-processing-example-aclprocessingexamplepy)
  - [2. Advanced Processing Example (`advanced_processing_example.py`)](#2-advanced-processing-example-advancedprocessingexamplepy)
  - [3. Complete Workflow Example (`complete_workflow_example.py`)](#3-complete-workflow-example-completeworkflowexamplepy)
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

Comprehensive examples demonstrating advanced FLEXT capabilities for enterprise data integration.

**Reviewed**: 2026-02-17 | **Version**: 0.10.0-dev

Part of the [FLEXT](https://github.com/flext-sh/flext) ecosystem.

## Key Features

### Examples Overview

### 1. ACL Processing Example (`acl_processing_example.py`)

**Advanced ACL Processing with Railway Pattern**

Demonstrates comprehensive Access Control List (ACL) processing capabilities:

- **Parallel Batch Processing**: Using `ThreadPoolExecutor` for concurrent ACL operations.
- **Intelligent Server Auto-detection**: Automatic detection of LDAP server types (OpenLDAP, Oracle OID, Oracle Unified Directory, Active Directory, Apache DS).
- **Integrated ACL Validation**: Complex context-based validation with custom rules per server type.
- **Railway Pattern**: Failure-resistant pipeline that follows functional error handling principles.
- **Performance Analytics**: Comprehensive metrics and throughput analysis.

**Key Features:**

- Server-specific ACL attribute detection
- Parallel batch processing with settingsurable worker threads
- Complex validation rules with forbidden permission combinations
- Railway pattern for robust error handling
- Performance monitoring and analytics

### 2. Advanced Processing Example (`advanced_processing_example.py`)

**Advanced Processing with Current APIs**

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

**Complete Workflow Integration**

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

- `from __future__ import annotations

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
from examples import AclProcessingPipeline

# Create pipeline with 8 worker threads
pipeline = AclProcessingPipeline(max_workers=8)

# Process ACL entries
result = pipeline.process_acls_with_pipeline(
    raw_entries=ldap_entries, server_context={"strict_mode": True}, parallel=True
)

if result.is_success:
    summary = result.unwrap()
    # Access comprehensive processing results
    u.Cli.print(f"Processed {summary['acls_extracted']} ACLs")
```

### Advanced Processing Pipeline

```python
from examples import IntegratedProcessingPipeline

# Create integrated pipeline
pipeline = IntegratedProcessingPipeline(max_workers=8, batch_size=200)

# Execute complete pipeline
result = pipeline.execute_integrated_pipeline(
    items=data_items,
    processing_func=process_function,
    validation_func=validate_function,
    analysis_func=analyze_function,
    use_parallel=True,
)
```

### Complete Workflow

```python
from examples import ComprehensiveRailwayPattern, CompleteWorkflowBuilder

# Build workflow configuration
settings = CompleteWorkflowBuilder.build_comprehensive_workflow(
    workflow_type="ldap_processing", requirements={"max_workers": 8, "parallel": True}
)

# Execute complete workflow
railway = ComprehensiveRailwayPattern(max_workers=8)
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

We welcome contributions! Please see our [Contributing Guide](../docs/CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
