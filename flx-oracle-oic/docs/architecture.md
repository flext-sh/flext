# Architecture Overview

## Component Architecture

The flx-oracle-oic package follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                        flx-oracle-oic                        │
│                      (Unified CLI & FLX)                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────┐│
│  │  tap-oracle-oic │  │target-oracle-oic │  │oracle-oic- ││
│  │                 │  │                  │  │    ext     ││
│  │ Data Extraction │  │  Data Loading    │  │ Lifecycle  ││
│  │  (Singer TAP)   │  │ (Singer Target)  │  │ Monitoring ││
│  └─────────────────┘  └──────────────────┘  └────────────┘│
│                                                             │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
                 ┌──────────────────────────┐
                 │   Oracle Integration     │
                 │      Cloud (OIC)         │
                 └──────────────────────────┘
```

## Design Principles

### 1. Singer Protocol Compliance

- Standard TAP for data extraction
- Standard Target for data loading
- Full catalog and state management
- Stream discovery and selection

### 2. Meltano Extension Architecture

- EDK-based extension for advanced features
- Lifecycle management capabilities
- Monitoring and analytics
- Artifact extraction

### 3. FLX Adapter Pattern

- Hexagonal architecture compliance
- Async operations support
- Dependency injection ready
- Circuit breaker pattern

### 4. Unified CLI

- Single entry point for all operations
- Consistent command structure
- Rich terminal output
- Pipeline orchestration

## Data Flow

### Extraction Flow

```
OIC API → OAuth2 Auth → TAP Streams → Singer Messages → Output
```

### Loading Flow

```
Singer Messages → Target Sinks → OAuth2 Auth → OIC API
```

### Lifecycle Flow

```
CLI Command → Extension → Lifecycle Manager → OIC API
```

## Authentication Architecture

All components share a common OAuth2 authentication pattern:

1. **Client Credentials Flow**: Using IDCS OAuth2
2. **Token Management**: Automatic refresh and caching
3. **Scope Building**: Dynamic scope construction
4. **Error Handling**: Retry with backoff

## Stream Architecture

### Core Streams

- Integrations
- Connections
- Packages
- Lookups
- Libraries
- Certificates

### Infrastructure Streams

- Adapters
- Agent Groups

### Monitoring Streams (via Extension)

- Execution Instances
- Error Logs
- Performance Metrics
- Audit Trail

## Error Handling

1. **Network Errors**: Retry with exponential backoff
2. **Authentication Errors**: Token refresh and retry
3. **API Errors**: Structured error messages
4. **Data Errors**: Validation and logging

## Performance Considerations

1. **Pagination**: Efficient handling of large datasets
2. **Parallelization**: Concurrent stream processing
3. **Caching**: Token and metadata caching
4. **Rate Limiting**: Respect OIC API limits

## Security

1. **Credential Storage**: Environment variables or secure config
2. **Token Handling**: Never log sensitive data
3. **HTTPS Only**: All communications encrypted
4. **Audit Trail**: All operations logged

## Extensibility

The architecture supports:

- Custom stream implementations
- Additional sink types
- New lifecycle operations
- Custom transformations
- Plugin extensions
