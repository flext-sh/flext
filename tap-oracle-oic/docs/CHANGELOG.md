# Changelog

All notable changes to tap-oic will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-06-15

### Added

- **Integration Generation**: Create integrations programmatically via OIC REST API
- **Connection Management**: Create and manage connections via API
- **Project Management**: Create and organize projects programmatically
- **Singer Integration Generator**: Automatically create OIC integrations from Singer tap/target configurations
- **Workflow Templates**: Pre-built templates for common integration patterns
- **Deployment Strategies**: Blue-green, canary, and multi-environment deployment support
- **Enhanced Monitoring**: Real-time monitoring and alerting capabilities
- **Self-Healing Integrations**: Automatic error recovery patterns

### Changed

- **Major Documentation Overhaul**: Reorganized from 36+ files to 11 essential documents
- **Corrected Capabilities**: Updated all documentation to reflect OIC Gen3's true ability to create integrations via API
- **Improved API Client**: Enhanced with connection pooling and better error handling
- **Performance Optimizations**: Batch processing and caching improvements

### Fixed

- Removed all false claims about OIC being "read-only"
- Corrected API endpoint documentation
- Fixed authentication issues with OAuth2
- Improved state management reliability

### Migration Notes

- This is a major version upgrade with new capabilities
- Review the new INTEGRATION_GENERATION.md for programmatic integration creation
- Update configuration to leverage new features
- Check API_REFERENCE.md for updated endpoints

## [1.0.0] - 2025-01-15

### Added

- Initial release of tap-oic
- Full support for Oracle Integration Cloud Generation 3
- OAuth2 authentication (mandatory for Gen3)
- Core streams:
  - integrations
  - connections
  - packages
  - projects (Gen3 feature)
- Monitoring streams:
  - monitoring_instances
  - monitoring_errors
  - monitoring_messages
- Extended streams:
  - lookups
  - libraries
  - certificates
  - schedules
- Analytics streams (Gen3):
  - usage_analytics
  - intelligence_predictions
- State management for incremental replication
- Comprehensive documentation
- Meltano integration support
- Docker container support

### Security

- OAuth2 authentication support
- Secure credential management
- TLS 1.2+ enforcement

### Performance

- Connection pooling
- Pagination support
- Streaming mode for large datasets
- Configurable batch sizes

[2.0.0]: https://github.com/your-org/tap-oic/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/your-org/tap-oic/releases/tag/v1.0.0
