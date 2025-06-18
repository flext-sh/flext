# tap-oracle-wms Documentation

Welcome to the comprehensive documentation for `tap-oracle-wms`, a Singer tap for extracting data from Oracle Warehouse Management System (WMS) Cloud.

## Quick Navigation

**[Documentation Index](documentation-index.md)** - Comprehensive cross-reference guide connecting all tap-oracle-wms documentation with Oracle's official resources.

**[Oracle WMS Official References](oracle-references.md)** - Complete mapping to Oracle's official documentation including Oracle WMS 25B new features and cross-references.

## Documentation Structure

### Core Technical Documentation

1. **[Oracle WMS Architecture](wms-architecture.md)** - Complete overview of Oracle WMS Cloud architecture, components, and design principles
2. **[WMS REST API Reference](wms-api-reference.md)** - Comprehensive API documentation including all endpoints, methods, and response formats
3. **[Authentication Guide](wms-authentication.md)** - Detailed guide on Basic Auth and OAuth2 authentication methods
4. **[Entity Discovery](wms-entity-discovery.md)** - How dynamic entity discovery works, metadata structure, and schema inference
5. **[Data Extraction Patterns](wms-data-extraction.md)** - Pagination strategies, filtering, sorting, and field selection capabilities

### Implementation Guides

6. **[Quick Start Guide](quickstart.md)** - Get up and running with tap-oracle-wms in minutes
7. **[Configuration Reference](configuration.md)** - Complete configuration options and best practices
8. **[Stream Development](stream-development.md)** - How to work with dynamic streams and entity discovery
9. **[Performance Tuning](performance-tuning.md)** - Optimization strategies for large-scale data extraction
10. **[Troubleshooting Guide](troubleshooting.md)** - Common issues and their solutions

### Advanced Topics

11. **[API Evolution & Versioning](wms-api-evolution.md)** - How Oracle WMS API has evolved and version compatibility
12. **[Security Best Practices](security.md)** - Security considerations and recommendations
13. **[Integration Patterns](integration-patterns.md)** - Best practices for integrating with data pipelines
14. **[Migration Guide](migration-guide.md)** - Migrating from other WMS data extraction tools
15. **[Future Capabilities](future-capabilities.md)** - Roadmap and planned features

## Key Features

- **Dynamic Entity Discovery**: Automatically discovers all available entities from the WMS API
- **Dynamic Schema Generation**: Infers schemas from entity metadata and sample data
- **Flexible Authentication**: Supports both Basic Auth and OAuth2
- **Advanced Querying**: Full support for filtering, sorting, field selection, and pagination
- **Performance Optimized**: Cursor-based pagination for large datasets
- **Enterprise Ready**: Production-grade error handling, logging, and monitoring

## Getting Started

1. Start with the [Quick Start Guide](quickstart.md) for basic setup
2. Review the [WMS Architecture](wms-architecture.md) to understand the system
3. Configure authentication using the [Authentication Guide](wms-authentication.md)
4. Explore available entities with [Entity Discovery](wms-entity-discovery.md)
5. Optimize performance with the [Performance Tuning](performance-tuning.md) guide

## Oracle WMS Versions Supported

- Oracle WMS Cloud 25B (Latest)
- Oracle WMS Cloud 24C
- Oracle WMS Cloud 24B
- Oracle WMS Cloud 24A

API Version: `v10` (stable across all supported WMS versions)

## Oracle Official References

**[Oracle WMS Official References](oracle-references.md)** - Complete guide to Oracle's official documentation, API references, and cross-references with this documentation.

Key sections:

- Official Oracle WMS Documentation links
- Cross-reference mapping with tap-oracle-wms docs
- Version compatibility matrix
- Performance guidelines from Oracle
- Integration best practices

## Related Resources

- [Oracle WMS Cloud Documentation](https://docs.oracle.com/en/cloud/saas/warehouse-management/index.html)
- [Oracle WMS REST API Guide](https://docs.oracle.com/en/cloud/saas/warehouse-management/25b/owmre/)
- [WMS Web Service APIs](https://docs.oracle.com/en/cloud/saas/warehouse-management/24a/owmap/)
- [Singer Specification](https://hub.meltano.com/singer/spec)
- [Meltano Integration](https://meltano.com)
