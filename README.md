# PyAuto - Enterprise Python Automation Workspace

Enterprise-grade Python automation workspace implementing Hexagonal Architecture with Oracle integrations.

## 🎯 Overview

PyAuto is a comprehensive monorepo workspace featuring:

- **Hexagonal Architecture**: Clean separation of concerns using Ports & Adapters pattern
- **Oracle Integrations**: Database, OIC (Oracle Integration Cloud), and WMS (Warehouse Management System)
- **Modern Python**: Built with Python 3.13+, Pydantic 2.11+, and enterprise standards
- **Quality Assurance**: >90% test coverage, strict typing, comprehensive linting

## 🏗️ Architecture

```
pyauto/
├── flx/                    # Core framework (Hexagonal Architecture)
├── flx-database-oracle/    # Oracle Database adapter
├── flx-http-oracle-oic/    # Oracle Integration Cloud adapter  
├── flx-http-oracle-wms/    # Oracle WMS adapter
├── flx-adapter-example/    # Template for new adapters
├── client-a-mig-oud/         # LDAP/OUD migration project
├── client-b-poc-oic-wms/  # POC implementation
└── scripts/               # Automation and maintenance tools
```

## 🚀 Quick Start

```bash
# Install dependencies
poetry install

# Run quality gates
make lint
make type-check  
make test
make format

# Start development
poetry shell
```

## 📦 Core Components

### FLX Framework
Enterprise-grade framework implementing:
- Domain-Driven Design (DDD)
- Command Query Responsibility Segregation (CQRS)
- Event Sourcing patterns
- Circuit breaker and resilience patterns

### Oracle Adapters
- **Database**: SQLAlchemy-based Oracle DB operations
- **OIC**: HTTP client with OAuth2/JWT authentication
- **WMS**: Retail Warehouse Management System integration

## 🔧 Development

All projects follow enterprise standards:
- Python 3.13+ with strict typing
- Pydantic 2.11+ for data validation
- Poetry for dependency management  
- Comprehensive testing with pytest
- Code quality with Black, Ruff, mypy

## 📚 Documentation

See individual project README files for detailed documentation.

## 🤝 Contributing

Follow the established patterns and maintain >90% test coverage.

## 📄 License

MIT License - see individual projects for specific licensing.