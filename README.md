# 🚀 PyAuto - Enterprise Python Automation Workspace

> **Enterprise-grade Python automation framework implementing Hexagonal Architecture with Oracle integrations and comprehensive data pipeline capabilities**

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Architecture](https://img.shields.io/badge/architecture-hexagonal-green.svg)](./docs/architecture/index.md)
[![Framework](https://img.shields.io/badge/framework-0.4.0-orange.svg)](./flx/README.md)
[![Enterprise](https://img.shields.io/badge/grade-enterprise-red.svg)](./docs/deployment/production-checklist.md)

**Monorepo workspace containing 21+ interconnected projects for enterprise Python automation, Oracle integration, data pipelines, and LDAP management**

---

## 🧭 **Navigation Hub**

### **🎯 Quick Access**
- **📖 [Complete Documentation](./docs/index.md)** - Comprehensive guides and references
- **🏗️ [Architecture Overview](./docs/architecture/index.md)** - Hexagonal architecture patterns
- **🚀 [Getting Started](./docs/getting-started/index.md)** - Setup and first steps
- **🔧 [Development Guide](./docs/development/index.md)** - Development standards and tools

### **🏢 Enterprise Components**
| Component | Purpose | Status | Documentation |
|-----------|---------|--------|---------------|
| **[FLX Core](./flx/)** | Hexagonal architecture framework | ✅ Stable | [FLX Docs](./flx/README.md) |
| **[Meltano Enterprise](./flx-meltano-enterprise/)** | Enterprise data platform | ✅ Production | [Meltano Docs](./flx-meltano-enterprise/README.md) |
| **[Oracle Database](./flx-database-oracle/)** | Oracle DB integration | ✅ Production | [Oracle Docs](./flx-database-oracle/README.md) |
| **[Code Analyzer](./dc-code-analyzer/)** | Django-based code analysis | 🔶 Beta | [Analyzer Docs](./dc-code-analyzer/README.md) |

---

## 🎯 **Core Architecture**

### **🏗️ Hexagonal Architecture Implementation**
```
┌─────────────────────────────────────────────────────────────┐
│                     PyAuto Enterprise                       │
├─────────────────────────────────────────────────────────────┤
│  🎯 Domain Layer (Business Logic)                          │
│  ├─ flx/                    - Core framework               │
│  ├─ ldap-core-shared/       - LDAP domain models          │
│  └─ client-b-poc-oic-wms/   - Business orchestration      │
├─────────────────────────────────────────────────────────────┤
│  🔌 Application Layer (Use Cases)                          │
│  ├─ flx-meltano-enterprise/ - Data platform orchestration │
│  ├─ flx-oracle-wms/         - WMS orchestration           │
│  └─ flx-oracle-oic/         - OIC orchestration           │
├─────────────────────────────────────────────────────────────┤
│  🌐 Infrastructure Layer (Adapters)                        │
│  ├─ Database Adapters                                      │
│  │  └─ flx-database-oracle/ - Oracle DB integration       │
│  ├─ HTTP Adapters                                          │
│  │  ├─ flx-http-oracle-oic/ - OIC API client              │
│  │  └─ flx-http-oracle-wms/ - WMS API client              │
│  ├─ Singer SDK Adapters                                    │
│  │  ├─ tap-oracle-oic/      - OIC data extractor          │
│  │  ├─ tap-oracle-wms/      - WMS data extractor          │
│  │  ├─ tap-ldap/            - LDAP data extractor         │
│  │  ├─ target-oracle-oic/   - OIC data loader             │
│  │  ├─ target-oracle-wms/   - WMS data loader             │
│  │  └─ target-ldap/         - LDAP data loader            │
│  └─ Migration Tools                                        │
│     └─ client-a-oud-mig/       - LDAP migration utility      │
└─────────────────────────────────────────────────────────────┘
```

### **📊 Project Statistics**
- **Total Projects**: 21 independent packages
- **Core Framework**: 1 (FLX)
- **Database Adapters**: 1 (Oracle)
- **HTTP Adapters**: 2 (OIC, WMS)
- **Singer SDK Components**: 6 (3 taps, 3 targets)
- **Enterprise Applications**: 4 (Meltano, Orchestrators, Analyzer)
- **Migration Tools**: 3 (LDAP, dbt, utilities)
- **Development Tools**: 4 (Examples, templates, shared libraries)

---

## 🚀 **Quick Start Guide**

### **📦 Installation Options**

```bash
# 1. Full enterprise installation (all components)
git clone https://github.com/datacosmos-br/pyauto.git
cd pyauto
poetry install --extras "all"

# 2. Core framework only
poetry install --extras "core"

# 3. Oracle ecosystem
poetry install --extras "oracle database"

# 4. LDAP ecosystem
poetry install --extras "ldap"

# 5. Data platform (Meltano + Singer SDK)
poetry install --extras "enterprise singer"
```

### **⚡ First Steps**

```bash
# Verify installation
python -c "import flx; print(f'FLX {flx.__version__} ready!')"

# Run core framework tests
cd flx && make test

# Start enterprise dashboard
cd flx-meltano-enterprise && poetry run meltano ui

# Test Oracle connectivity
cd flx-database-oracle && poetry run flx-oracle-db test-connection
```

### **🎯 Usage Examples**

```python
# Enterprise framework usage
from flx.core import Application, DomainEvent
from flx.infrastructure import OracleAdapter

# Create enterprise application
app = Application(
    name="enterprise-automation",
    adapters=[OracleAdapter()]
)

# Oracle database operations
from flx_database_oracle import OracleClient

client = OracleClient(
    host="oracle-prod.company.com",
    service_name="PROD"
)

# Data pipeline with Singer SDK
from tap_oracle_wms import TapOracleWMS
from target_oracle_oic import TargetOracleOIC

# Extract from WMS, load to OIC
tap = TapOracleWMS(config="wms_config.json")
target = TargetOracleOIC(config="oic_config.json")
```

---

## 📁 **Workspace Structure**

### **🏗️ Core Framework**
```
flx/                           # 🎯 Core hexagonal architecture framework
├── src/flx/
│   ├── core/                  # Domain layer abstractions
│   ├── application/           # Use case implementations
│   ├── infrastructure/        # Infrastructure adapters
│   └── cli/                   # Command-line interface
└── tests/                     # Comprehensive test suite
```

### **🔗 Database & HTTP Adapters**
```
flx-database-oracle/           # 🗄️ Oracle database integration
flx-http-oracle-oic/          # 🌐 Oracle Integration Cloud HTTP client
flx-http-oracle-wms/          # 📦 Oracle WMS HTTP client
```

### **📊 Singer SDK Data Pipeline Components**
```
tap-oracle-oic/               # 📤 OIC data extractor
tap-oracle-wms/               # 📤 WMS data extractor
tap-ldap/                     # 📤 LDAP data extractor
target-oracle-oic/            # 📥 OIC data loader
target-oracle-wms/            # 📥 WMS data loader
target-ldap/                  # 📥 LDAP data loader
```

### **🏢 Enterprise Applications**
```
flx-meltano-enterprise/       # 🎯 Enterprise data platform
client-b-poc-oic-wms/         # 🔄 Business process orchestration
dc-code-analyzer/             # 🔍 Django-based code analysis platform
client-a-oud-mig/               # 🔄 LDAP migration utility
```

### **🛠️ Development & Utilities**
```
examples/                     # 📚 Usage examples and tutorials
docs/                        # 📖 Comprehensive documentation
scripts/                     # 🔧 Development and maintenance scripts
reference/                   # 📋 Official Meltano reference implementations
```

---

## 🎯 **Key Features & Capabilities**

### **🏗️ Enterprise Architecture**
- **Hexagonal Architecture**: Clean separation of domain, application, and infrastructure
- **Domain-Driven Design**: Rich domain models with proper encapsulation
- **CQRS & Event Sourcing**: Command/Query separation and event-driven architecture
- **Dependency Injection**: Pluggable infrastructure through dependency injection
- **Type Safety**: Full Python 3.13+ type checking with mypy strict mode

### **🔗 Oracle Integration**
- **Native Oracle Support**: Direct integration with Oracle Database 23c+
- **Oracle Cloud Integration**: OIC (Oracle Integration Cloud) HTTP client
- **WMS Integration**: Oracle Warehouse Management System integration
- **Connection Pooling**: High-performance connection management
- **Transaction Support**: ACID compliance with distributed transaction support

### **📊 Data Pipeline Capabilities**
- **Singer SDK Compliance**: Full Singer specification implementation
- **Stream Processing**: Real-time data processing with async support
- **Schema Evolution**: Automatic schema detection and evolution
- **Data Quality**: Built-in data validation and quality checks
- **Monitoring**: Comprehensive observability and metrics

### **🏢 Enterprise Features**
- **Multi-tenancy**: Enterprise-grade multi-tenant architecture
- **Security**: OAuth2, JWT, RBAC, and audit logging
- **Scalability**: Horizontal scaling with load balancing
- **Monitoring**: OpenTelemetry, metrics, and distributed tracing
- **Configuration**: Environment-based configuration management

### **🔧 Development Experience**
- **Modern Python**: Python 3.13+ with latest language features
- **Poetry Workspace**: Monorepo management with Poetry
- **Quality Tools**: Black, Ruff, mypy, pytest with 90%+ coverage
- **Documentation**: Comprehensive docs with examples
- **CI/CD Ready**: GitHub Actions workflows and deployment automation

---

## 🛠️ **Development Standards**

### **📋 Quality Requirements**
- **Code Coverage**: Minimum 90% test coverage
- **Type Safety**: 100% mypy strict compliance
- **Code Style**: Black + Ruff formatting
- **Documentation**: Comprehensive docstrings and guides
- **Testing**: Unit, integration, and E2E tests

### **🔧 Development Tools**
```bash
# Quality checks
make lint          # Code formatting and linting
make type-check    # Type checking with mypy
make test          # Full test suite
make coverage      # Coverage reporting

# Development workflow
make dev-install   # Development environment setup
make pre-commit    # Pre-commit hooks setup
make docs          # Documentation generation
```

### **📊 Supported Environments**
- **Python**: 3.9, 3.10, 3.11, 3.12, 3.13
- **Operating Systems**: Linux, macOS, Windows
- **Databases**: Oracle 19c+, PostgreSQL 13+, SQLite 3.8+
- **Cloud Platforms**: AWS, Azure, GCP, Oracle Cloud

---

## 📖 **Documentation Ecosystem**

### **📚 Core Documentation**
- **[Architecture Guide](./docs/architecture/index.md)** - Hexagonal architecture implementation
- **[Development Guide](./docs/development/index.md)** - Development standards and practices
- **[Deployment Guide](./docs/deployment/index.md)** - Production deployment strategies
- **[API Reference](./docs/api-reference/index.md)** - Complete API documentation

### **🎯 Quick Reference Guides**
- **[Getting Started](./docs/getting-started/index.md)** - Setup and first steps
- **[Oracle Integration](./docs/guides/oracle-integration.md)** - Oracle-specific implementations
- **[Data Pipelines](./docs/guides/data-pipelines.md)** - Singer SDK pipeline development
- **[Enterprise Features](./docs/guides/enterprise-features.md)** - Enterprise-grade capabilities

### **🔗 Component Documentation**
Each project maintains its own comprehensive README.md with:
- Purpose and scope
- Installation instructions
- Usage examples
- API documentation
- Configuration options
- Testing guidelines

---

## 🤝 **Contributing & Support**

### **🔧 Development Setup**
```bash
# Setup development environment
git clone https://github.com/datacosmos-br/pyauto.git
cd pyauto
poetry install --extras "dev all"
make pre-commit-install

# Run full validation
make validate-all
```

### **📋 Contribution Guidelines**
- Follow [development standards](./docs/development/index.md)
- Maintain 90%+ test coverage
- Update documentation for all changes
- Follow semantic versioning
- Submit detailed pull requests

### **🆘 Support Channels**
- **Issues**: [GitHub Issues](https://github.com/datacosmos-br/pyauto/issues)
- **Discussions**: [GitHub Discussions](https://github.com/datacosmos-br/pyauto/discussions)
- **Documentation**: [Official Docs](./docs/index.md)
- **Enterprise Support**: Contact maintainers for enterprise support options

---

## 📄 **License & Acknowledgments**

### **📋 License**
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### **🙏 Acknowledgments**
- **Meltano Labs**: Reference implementations and Singer SDK patterns
- **Oracle**: Database and cloud integration technologies
- **Python Community**: Modern Python tooling and best practices
- **FastAPI**: High-performance web framework foundation

---

## 🔗 **Cross-References**

### **🎯 Prerequisites**
- Python 3.9+ with Poetry
- Oracle Database or Oracle Cloud access (for Oracle components)
- LDAP server access (for LDAP components)

### **➡️ Next Steps**
- [Installation Guide](./docs/getting-started/installation.md) - Detailed setup instructions
- [Architecture Deep Dive](./docs/architecture/hexagonal-architecture.md) - Understanding the framework
- [First Project](./docs/getting-started/first-project.md) - Building your first PyAuto application

### **🔗 Related Projects**
- [FLX Framework](./flx/README.md) - Core framework implementation
- [Oracle Database Adapter](./flx-database-oracle/README.md) - Database integration
- [Meltano Enterprise](./flx-meltano-enterprise/README.md) - Data platform implementation

---

**🚀 PyAuto Enterprise Workspace** | **🏠 Root**: PyAuto Home | **Framework**: 0.4.0+ | **Updated**: 2025-06-19
