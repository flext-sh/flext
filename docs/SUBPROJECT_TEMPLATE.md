# FLEXT Subproject Documentation Template

**Version 0.9.0** | **Template Type**: Enterprise Standard | **Scope**: All 33 FLEXT Projects

This template provides standardized documentation structure for all FLEXT ecosystem projects, ensuring consistent enterprise-grade documentation across the distributed development environment.

## 📋 Required Documentation Files

### **Core Documentation Set**

Every FLEXT subproject must implement this standardized documentation structure:

#### **1. README.md** - Project Overview

```markdown
# [Project Name] - [Brief Description]

**Version X.Y.Z** | **Status: [Status]** | **Type: [Foundation/Service/Infrastructure/Singer]**

[One paragraph description of project purpose and ecosystem positioning]

## 📋 Project Overview

### **Purpose**

[Detailed description of what the project does and why it exists]

### **Architecture Position**

- **Layer**: [Clean Architecture layer]
- **Dependencies**: [List of key dependencies including flext-core]
- **Consumers**: [Projects that depend on this one]
- **Ecosystem Role**: [Position within 33-project ecosystem]

## 🎯 Key Features

[List of main features and capabilities]

## 🚀 Quick Start

[Basic installation and usage instructions]

## 📖 Documentation

- **[Complete Documentation](docs/README.md)** - Full documentation index
- **[Development Guide](CLAUDE.md)** - Claude Code development guidance
- **[API Reference](docs/api-reference.md)** - Complete API documentation
- **[Examples](examples/README.md)** - Practical usage examples

## 🔗 Ecosystem Integration

- **[FLEXT Hub](../docs/NAVIGATION.md)** - Main ecosystem navigation
- **[Architecture Guide](../docs/architecture/)** - System architecture
- **Related Projects**: [List related ecosystem projects]

---

**Navigation**: [FLEXT Hub](../docs/NAVIGATION.md) > [Project Category] > [Project Name]
```

#### **2. CLAUDE.md** - Development Guidance

```markdown
# CLAUDE.md - [Project Name] Development Guidance

**Version X.Y.Z** | **Status: [Status]** | **Integration: FLEXT Ecosystem**

Development guidance for Claude Code when working with [Project Name] within the FLEXT ecosystem, including architectural patterns, integration requirements, and quality standards.

## Project Overview

[Detailed technical description with ecosystem positioning]

## Architecture

[Architecture details with Clean Architecture positioning]

## Integration Patterns

[How this project integrates with flext-core and other ecosystem components]

## Development Commands

[Standard commands for development, testing, and validation]

## Quality Standards

[Quality requirements and validation processes]

## Related Projects

[Integration with other ecosystem components]

---

**Navigation**: [FLEXT Hub](../docs/NAVIGATION.md) > Development > [Project Name]
```

#### **3. docs/README.md** - Documentation Hub

```markdown
# [Project Name] Documentation

**Version X.Y.Z** | **Documentation Status: Complete** | **Coverage: 95%+**

Complete documentation hub for [Project Name] with comprehensive guides, API references, and integration examples.

## 📚 Documentation Structure

[List of all documentation files and their purposes]

## 🎯 Quick Navigation

[Links to most important documentation sections]

## 🔗 Integration Documentation

[Links to ecosystem integration documentation]

---

**Navigation**: [FLEXT Hub](../../docs/NAVIGATION.md) > [Project Category] > [Project Name] > Documentation
```

#### **4. docs/TODO.md** - Project Roadmap

```markdown
# [Project Name] - Development TODO

**Version X.Y.Z** | **Status: [Current Status]** | **Integration: FLEXT Ecosystem**

Development roadmap and pending tasks for [Project Name] with ecosystem integration requirements.

## 🎯 Current Status

[Progress tracking with ecosystem alignment requirements]

## 🔥 Priority Tasks

[High-priority items with ecosystem dependencies]

## 🚀 Roadmap

[Long-term roadmap with ecosystem coordination]

---

**Navigation**: [FLEXT Hub](../../docs/NAVIGATION.md) > Development > [Project Name] > Roadmap
```

### **Source Code Documentation**

#### **5. src/[package]/**init**.py** - Package Documentation

```python
"""
[Project Name] - [Brief Description]

[Comprehensive package description with ecosystem integration notes]

Key Components:
    - [Component 1]: [Description]
    - [Component 2]: [Description]

Architecture:
    [Clean Architecture positioning and integration patterns]

Example:
    [Basic usage example with imports and operations]

Integration:
    - Built on flext-core patterns with FlextResult error handling
    - Integrates with flext-observability for monitoring
    - [Other ecosystem integrations]

Author: FLEXT Development Team
Version: X.Y.Z
License: MIT
"""
```

#### **6. tests/README.md** - Test Documentation

```markdown
# [Project Name] - Test Suite

**Coverage: 90%+** | **Framework: pytest** | **Integration: FLEXT Ecosystem**

Comprehensive test suite with ecosystem integration validation.

## Test Structure

[Description of test organization]

## Running Tests

[Test execution instructions]

---

**Navigation**: [FLEXT Hub](../../docs/NAVIGATION.md) > [Project Name] > Testing
```

#### **7. examples/README.md** - Usage Examples

```markdown
# [Project Name] - Usage Examples

**Version X.Y.Z** | **Examples: Production-Ready** | **Integration: FLEXT Ecosystem**

Practical examples demonstrating [Project Name] functionality with ecosystem integration.

## Example Categories

[Organization of examples]

## Integration Examples

[Examples showing ecosystem integration]

---

**Navigation**: [FLEXT Hub](../../docs/NAVIGATION.md) > [Project Name] > Examples
```

## 🎯 Project-Specific Requirements

### **Foundation Projects (flext-core, flext-observability)**

- Comprehensive architectural documentation
- Reference implementation examples
- Integration patterns for dependent projects
- Performance benchmarking and optimization guides

### **Core Services (FlexCore, FLEXT Service)**

- Go architecture documentation with Clean Architecture patterns
- API contracts and OpenAPI specifications
- Plugin system documentation
- Performance benchmarking and monitoring integration

### **Application Services (5 projects)**

- Service architecture with API references
- Authentication and authorization patterns
- UI/UX documentation for web interfaces
- CLI integration guides and automation examples

### **Infrastructure Projects (6 projects)**

- Connection patterns and configuration management
- Performance optimization guides
- Security implementation with authentication
- Monitoring integration and error handling

### **Singer Ecosystem (15 projects)**

- Singer SDK integration patterns
- Meltano configuration and orchestration
- DBT model documentation with business logic
- Data schema and pipeline integration examples

### **Specialized Projects (2 projects)**

- Client-specific implementation patterns
- Custom business logic documentation
- Integration with standard ecosystem patterns
- Migration and deployment guides

## 🔧 Implementation Checklist

### **Phase 1: Core Documentation**

- [ ] README.md with ecosystem positioning
- [ ] CLAUDE.md with development guidance
- [ ] docs/README.md with navigation
- [ ] docs/TODO.md with roadmap

### **Phase 2: Source Documentation**

- [ ] Package-level docstrings (100% coverage)
- [ ] Module-level documentation
- [ ] Class and method docstrings
- [ ] Type annotations (95%+ coverage)

### **Phase 3: Supporting Documentation**

- [ ] Test suite documentation
- [ ] Usage examples with integration
- [ ] API reference documentation
- [ ] Performance and security guides

### **Phase 4: Ecosystem Integration**

- [ ] Cross-project integration examples
- [ ] Dependency documentation
- [ ] Quality gate integration
- [ ] Monitoring and observability setup

## 📊 Quality Standards

### **Documentation Requirements**

- **Professional English**: Consistent terminology and presentation
- **Technical Accuracy**: All examples must be functional and tested
- **Ecosystem Awareness**: Clear positioning within FLEXT architecture
- **Comprehensive Coverage**: All public APIs documented with examples

### **Integration Standards**

- **flext-core Integration**: Proper use of FlextResult and dependency patterns
- **Cross-Project References**: Clear documentation of project relationships
- **Quality Gates**: Integration with automated validation systems
- **Performance Standards**: Benchmarking and optimization documentation

---

**This template ensures consistent, enterprise-grade documentation across all 33 FLEXT ecosystem projects while maintaining professional standards without marketing content.**
