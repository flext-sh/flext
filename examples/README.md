# FLEXT Examples

This directory contains comprehensive examples demonstrating advanced FLEXT capabilities for enterprise data integration.

## Examples Overview

### 1. ACL Processing Example (`acl_processing_example.py`)

**Advanced ACL Processing with Railway Pattern**

Demonstrates comprehensive Access Control List (ACL) processing capabilities:

- **Batch processing paralelo**: Using `ThreadPoolExecutor` for concurrent ACL operations
- **Intelligent server auto-detection**: Automatic detection of LDAP server types (OpenLDAP, Oracle OID, Oracle Unified Directory, Active Directory, Apache DS)
- **Integrated ACL validation**: Complex context-based validation with custom rules per server type
- **Railway pattern**: Failure-resistant pipeline that stops on first error
- **Performance analytics**: Comprehensive metrics and throughput analysis

**Key Features:**

- Server-specific ACL attribute detection
- Parallel batch processing with configurable worker threads
- Complex validation rules with forbidden permission combinations
- Railway pattern for robust error handling
- Performance monitoring and analytics

### 2. Advanced Processing Example (`advanced_processing_example.py`)

**Advanced Processing with Current APIs**

Demonstrates modern processing capabilities with corrected APIs:

- **Parallel processing**: Using `ThreadPoolExecutor` for concurrent operations
- **Batch processing**: Sequential processing for heavy operations
- **Integrated pipeline**: Combined processing, validation, and analysis stages
- **Railway pattern**: Error handling with early termination on failures
- **Performance analytics**: Comprehensive metrics across all processing stages

**Key Features:**

- Advanced processor with configurable parallel execution
- Validation processor with parallel item checking
- Analysis processor for data insights and aggregation
- Batch heavy operations processor for memory-intensive tasks
- End-to-end pipeline integration

### 3. Complete Workflow Example (`complete_workflow_example.py`)

**Complete Workflow Integration**

Demonstrates the complete FLEXT enterprise workflow with all capabilities integrated:

- **Railway pattern abrangente**: Comprehensive error handling across all stages
- **Processamento paralelo**: Parallel execution in all workflow stages
- **Auto-detecção inteligente**: Automatic data source and pipeline configuration
- **Builders inteligentes**: Dynamic workflow construction based on requirements
- **Validação end-to-end**: Complete workflow validation with multiple aspects

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

- Operations return `FlextResult[T]` for type-safe error handling
- Pipeline stops on first failure (no exception propagation)
- Comprehensive error reporting and context tracking

### Parallel Processing

Extensive use of parallel processing throughout:

- `ThreadPoolExecutor` for concurrent operations
- Configurable worker thread pools
- Batch processing for memory efficiency
- Parallel validation and analysis stages

### Type Safety

Full type safety with modern Python features:

- `from __future__ import annotations` for forward references
- Comprehensive type hints throughout
- Generic types with proper variance
- Protocol-based design where appropriate

### Enterprise Features

Production-ready enterprise capabilities:

- Comprehensive logging and metrics
- Configurable processing parameters
- Performance analytics and monitoring
- Correlation ID tracking for distributed operations
- Context management across pipeline stages

## Usage Examples

### Basic ACL Processing

```python
from examples.acl_processing_example import AclProcessingPipeline

# Create pipeline with 8 worker threads
pipeline = AclProcessingPipeline(max_workers=8)

# Process ACL entries
result = pipeline.process_acls_with_pipeline(
    raw_entries=ldap_entries,
    server_context={"strict_mode": True},
    parallel=True
)

if result.is_success:
    summary = result.unwrap()
    # Access comprehensive processing results
    print(f"Processed {summary['acls_extracted']} ACLs")
```

### Advanced Processing Pipeline

```python
from examples.advanced_processing_example import IntegratedProcessingPipeline

# Create integrated pipeline
pipeline = IntegratedProcessingPipeline(max_workers=8, batch_size=200)

# Execute complete pipeline
result = pipeline.execute_integrated_pipeline(
    items=data_items,
    processing_func=process_function,
    validation_func=validate_function,
    analysis_func=analyze_function,
    use_parallel=True
)
```

### Complete Workflow

```python
from examples.complete_workflow_example import (
    ComprehensiveRailwayPattern,
    CompleteWorkflowBuilder
)

# Build workflow configuration
config = CompleteWorkflowBuilder.build_comprehensive_workflow(
    workflow_type="ldap_processing",
    requirements={"max_workers": 8, "parallel": True}
)

# Execute complete workflow
railway = ComprehensiveRailwayPattern(max_workers=8)
result = railway.execute_workflow_railway(
    workflow_id="enterprise_workflow",
    input_data=input_data,
    stage_definitions=config["stage_definitions"],
    workflow_requirements=config
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

## Quality Assurance

All examples follow FLEXT quality standards:

- **Linting**: Pass Ruff checks with zero errors
- **Type checking**: Full mypy compliance
- **Testing**: Designed for comprehensive test coverage
- **Documentation**: Extensive docstrings and examples
- **Performance**: Optimized for enterprise workloads

## Dependencies

Examples use only FLEXT core dependencies:

- `flext-core`: Core FLEXT functionality
- Standard library modules (concurrent.futures, dataclasses, typing)

No external dependencies required for basic functionality.

## Integration with FLEXT Ecosystem

These examples demonstrate integration with the complete FLEXT ecosystem:

- **FLEXT-LDIF**: LDAP-specific processing capabilities
- **FLEXT-Core**: Foundation patterns and utilities
- **FLEXT-Result**: Railway pattern implementation
- **FLEXT-Services**: Service-oriented architecture patterns

## Enterprise Readiness

All examples are production-ready with:

- Comprehensive error handling
- Performance monitoring and analytics
- Configurable execution parameters
- Correlation tracking for distributed operations
- Type-safe APIs throughout
- Extensive documentation and examples
