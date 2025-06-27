# internal.invalid.md - COMMUNITY-TOOLS PROJECT SPECIFICS

**Hierarchy**: PROJECT-SPECIFIC  
**Project**: Oracle Community Tools Collection - Third-party Oracle tools and integrations  
**Type**: Community Tools & Documentation Collection  
**Status**: MIXED (Multiple community tools)  
**Last Updated**: 2025-06-26

**Reference**: `/home/marlonsc/CLAUDE.md` → Universal Development Principles  
**Reference**: `/home/marlonsc/internal.invalid.md` → Cross-workspace temporary issues  
**Reference**: `../CLAUDE.md` → PyAuto workspace patterns

---

## 🎯 PROJECT-SPECIFIC CONFIGURATION

### Virtual Environment Usage

```bash
# MANDATORY: Use workspace venv
source /home/marlonsc/pyauto/.venv/bin/activate
# Note: This is primarily a documentation collection
```

### Agent Coordination

```bash
# Read workspace coordination first
cat /home/marlonsc/pyauto/.token | tail -5
# Project context
echo "PROJECT_CONTEXT=community-tools" > .token
echo "STATUS=documentation-collection" >> .token
echo "TYPE=oracle-community-tools" >> .token
```

---

## 🚨 PROJECT-SPECIFIC ISSUES

### **1. Community Tools Documentation Maintenance**

**Status**: **ACTIVE COLLECTION** - 15+ community-driven Oracle solutions

**Documentation Challenges**:

- Multiple external dependencies and versions
- Community tools with varying maintenance levels
- Integration examples need regular validation
- Regional community contributions in different languages

### **2. Tool Validation and Testing**

**Challenge**: Ensuring community tools remain functional

**Current Tools Requiring Attention**:

- Prometheus Oracle Exporter configurations
- DBA Tools PowerShell compatibility
- TOAD Scripts validation
- PostgreSQL Oracle Compatibility (Orafce) examples

---

## 🛠️ COMMUNITY TOOLS SPECIFICS

### Tool Categories Managed

1. **Monitoring & Observability** - Prometheus, Grafana integrations
2. **Development Tools** - TOAD Scripts, NetBeans integration
3. **Automation & DevOps** - PowerShell DBA tools, CI/CD examples
4. **Migration & Compatibility** - PostgreSQL Oracle compatibility
5. **Regional Communities** - Oracle Cloud Brasil, localized content

### Maintenance Procedures

```bash
# Validate Prometheus Oracle Exporter examples
cd prometheus-oracle-exporter/
docker run --rm prometheus-oracle-exporter:latest --help

# Test PowerShell DBA tools (Windows only)
powershell -Command "Import-Module dbatools; Get-Command *Oracle*"

# Validate PostgreSQL Orafce examples
# psql -c "CREATE EXTENSION IF NOT EXISTS orafce;"
```

---

## 📋 ENVIRONMENT VARIABLES (PROJECT-SPECIFIC)

### Optional Testing Variables

```bash
# For testing community tool integrations
ORACLE_TEST_HOST=localhost     # Test Oracle instance
ORACLE_TEST_PORT=1521         # Oracle port
PROMETHEUS_URL=http://localhost:9090  # Prometheus instance
GRAFANA_URL=http://localhost:3000     # Grafana dashboard
```

---

## 🔍 MAINTENANCE COMMANDS

### Documentation Validation

```bash
# Validate external links in documentation
grep -r "http" README.md | head -10

# Check for outdated version references
grep -r "version\|v[0-9]" README.md
```

### Community Tool Status Check

```bash
# Check Prometheus Oracle Exporter availability
curl -s https://api.github.com/repos/iamseth/oracledb_exporter/releases/latest

# Validate DBA Tools PowerShell module
# powershell -Command "Find-Module dbatools"
```

---

## 🧪 TESTING NOTES (PROJECT-SPECIFIC)

### Integration Testing Strategy

- **Docker-based testing** for Prometheus exporters
- **PowerShell testing** in Windows environments
- **PostgreSQL testing** for Orafce compatibility
- **Documentation validation** for all examples

### Testing Challenges

- **Multi-platform requirements** (Windows, Linux, Oracle versions)
- **External dependencies** on community repositories
- **Version compatibility** across different Oracle versions
- **Regional tool availability** for international communities

---

## 📈 COMMUNITY INTEGRATION POINTS

### Oracle User Groups

- International Oracle User Group (IOUG)
- Oracle ACE Program
- Regional Oracle communities (Brasil, DOAG, JOUGS)

### Technology Integrations

- **Prometheus/Grafana** monitoring stack
- **PowerShell** automation framework
- **PostgreSQL** migration compatibility
- **Container orchestration** (Docker, Kubernetes)

### Community Contributions

- Tool submissions from community developers
- Regional examples and translations
- Best practices documentation
- Use case scenarios from production environments

---

## 🔄 UPDATE AND MAINTENANCE SCHEDULE

### Regular Maintenance Tasks

- **Monthly**: Update tool version references
- **Quarterly**: Validate all external links and examples
- **Bi-annually**: Review community tool popularity and relevance
- **As needed**: Add new community contributions

### Community Feedback Integration

- Monitor Oracle community forums for new tools
- Track GitHub repositories for popular Oracle integrations
- Integrate feedback from PyAuto workspace users
- Update examples based on real-world usage

---

**Authority**: This file contains project-specific information for community-tools collection  
**Escalation**: Issues affecting multiple community tools should be documented in workspace CLAUDE.md  
**Reference**: For community tool patterns → `../CLAUDE.md`
