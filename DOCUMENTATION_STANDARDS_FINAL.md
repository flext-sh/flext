# PyAuto Documentation Standards - Final
## Code-First Documentation Integration for GitHub Navigation

**Version**: 2.0  
**Created**: 2025-01-06  
**Token**: `.doc-reorg`  
**GitHub Org**: https://github.com/datacosmos-br/

## Overview

This document establishes the final standards for integrating documentation directly into code for seamless GitHub navigation. Documentation lives where developers work, using GitHub's interface as the primary navigation method.

## Repository Structure

```
https://github.com/datacosmos-br/pyauto/ (monorepo workspace)
├── flx/                    # Core framework
├── flx-*/                  # Plugins/adapters  
├── client-b-poc-*/         # Business implementations
├── client-a-oud-mig/          # Oracle directory migration (ex-oud-automation)
├── dc-code-analyzer/       # Independent code analysis utility
└── meltano/, singer-sdk/   # Reference only (don't touch)
```

## Project Categories

### **1. Core Framework** (`flx/`)
- **Purpose**: Base framework with hexagonal architecture
- **Status**: ![Status](https://img.shields.io/badge/status-Beta-blue)
- **Audience**: Framework developers, architects
- **Dependencies**: Standalone (other projects depend on this)

### **2. Plugins/Adapters** (`flx-*/`)
- **Purpose**: Specialized integrations (Oracle DB, OIC, WMS)
- **Status**: ![Status](https://img.shields.io/badge/status-Beta-blue)
- **Audience**: Integration developers
- **Dependencies**: Depends on `flx/` core

### **3. Business Implementations** (`client-b-poc-*/`)
- **Purpose**: Real-world business integrations
- **Status**: ![Status](https://img.shields.io/badge/status-POC-yellow)
- **Audience**: Implementation teams, business users
- **Dependencies**: Depends on multiple `flx-*` plugins

### **4. System Administration** (`client-a-oud-mig/`)
- **Purpose**: Oracle Unified Directory migration tools
- **Status**: ![Status](https://img.shields.io/badge/status-Beta-blue)
- **Audience**: System REDACTED_LDAP_BIND_PASSWORDistrators
- **Dependencies**: Uses `flx/` framework

### **5. Independent Utilities** (`dc-code-analyzer/`)
- **Purpose**: Code quality analysis tools
- **Status**: ![Status](https://img.shields.io/badge/status-Beta-blue)
- **Audience**: DevOps, QA teams
- **Dependencies**: Independent (Django-based)

## Documentation Integration Strategy

### **Hierarchical Documentation Navigation**

```
flx/ (core framework)
├── README.md                     # Framework overview + navigation hub
├── src/flx/
│   ├── README.md                 # API index + architecture overview
│   ├── core/
│   │   ├── README.md + docstrings # Domain layer guide
│   │   └── examples/             # Domain modeling examples
│   ├── adapters/
│   │   ├── README.md + docstrings # Adapter development guide
│   │   └── examples/             # Adapter implementation examples
│   ├── ports/
│   │   ├── README.md + docstrings # Ports interface guide
│   │   └── examples/             # Port definition examples
│   └── testing/
│       ├── README.md + docstrings # Testing framework guide
│       └── examples/             # Testing pattern examples
└── docs/ → MIGRATE to src/       # Legacy docs to be integrated

flx-database-oracle/ (plugin)
├── README.md                     # Plugin overview + links to flx core
├── src/flx_database_oracle/
│   ├── README.md + docstrings    # Oracle DB integration guide
│   └── examples/                 # Database operation examples
└── docs/ → MIGRATE to src/       # Legacy docs to be integrated

client-b-poc-oic-wms/ (implementation)
├── README.md                     # Project overview + links to plugins
├── src/gn_oic_wms_db/
│   ├── README.md + docstrings    # Business implementation guide
│   └── examples/                 # Business process examples
└── scripts/
    └── examples/                 # Deployment and operation examples
```

## Link Strategy

### **GitHub Navigation Links**

**Within Same Repository:**
```markdown
# Relative links for same repo navigation
[Core Framework](../flx/README.md)
[Database Plugin](../flx-database-oracle/README.md)
[Implementation Project](../client-b-poc-oic-wms/README.md)
```

**Cross-Repository/External Links:**
```markdown
# Absolute GitHub links for external navigation
[Main Repository](https://github.com/datacosmos-br/pyauto)
[Organization](https://github.com/datacosmos-br/)
```

**All links point to `main` branch by default**

### **Hierarchical Reference Pattern**

```markdown
# Navigation breadcrumbs for hierarchy awareness
🏠 [DataCosmos](https://github.com/datacosmos-br/) > 📦 [PyAuto](https://github.com/datacosmos-br/pyauto) > 🔧 [FLX Core](../flx/README.md) > 🎯 **Current Module**

# Cross-references showing dependency hierarchy
📋 **Dependencies**: [FLX Core](../flx/README.md) → This Plugin → [Implementation Projects](../client-b-poc-oic-wms/README.md)
```

## Universal Template

### **README.md Structure** (All Projects)

```markdown
# {Project Name}

![Status](https://img.shields.io/badge/status-{Status}-{Color})

{Navigation breadcrumbs}

**{Brief description and purpose}**

## Quick Start

{30-second usage example - executable code}

## Architecture

{High-level design explanation with diagrams}

## Components

{List of main components with links to source}

## Examples

{Links to examples/ subdirectory with real usage}

## API Reference  
{Available for libraries - key classes/functions}

## CLI Reference
{Available for CLI tools - command examples}

## Installation
{Setup and dependency instructions}

## Configuration
{Configuration examples and options}

## Business Process
{Available for implementations - workflow documentation}

## Cross-References

{Links to related projects showing hierarchy}

## Troubleshooting

{Common issues and solutions}

## Navigation

{Links to parent/child documentation}
```

### **Docstring Standards** (All Python Files)

```python
"""Module Description.

Comprehensive module overview explaining purpose and relationship
to other components in the framework hierarchy.

Architecture:
    Description of how this module fits in hexagonal architecture
    and relationships to other layers.

Key Components:
    - Component1: Purpose and usage
    - Component2: Purpose and usage
    
Examples:
    Basic usage example:
    ```python
    from flx.module import Component
    
    component = Component(config)
    result = component.execute()
    ```
    
    Advanced usage with framework integration:
    ```python
    # Show how it integrates with other FLX components
    ```

Cross-References:
    - ../core/README.md: Core domain patterns
    - ../adapters/README.md: Adapter implementations
    - examples/: Complete usage examples

See Also:
    - Parent module documentation for context
    - Related modules for integration patterns
    - Framework overview for architecture understanding
"""
```

### **Examples Structure** (All Projects)

```
{project}/examples/
├── README.md                   # Examples index + navigation
├── basic/
│   ├── README.md              # Basic usage guide
│   ├── quickstart.py          # Minimal working example
│   └── {project}_basic.py     # Project-specific basic example
├── advanced/
│   ├── README.md              # Advanced patterns guide
│   ├── {project}_advanced.py  # Complex usage patterns
│   └── integration.py         # Integration with other components
├── deployment/                 # For implementations only
│   ├── README.md              # Deployment guide
│   └── production_config.py   # Production configuration examples
└── testing/
    ├── README.md              # Testing examples guide
    ├── unit_tests.py          # Unit testing patterns
    └── integration_tests.py   # Integration testing examples
```

## Migration Process

### **Phase 1: Core Framework (`flx/`)**
1. ✅ Update module docstrings with comprehensive documentation
2. ✅ Create/update README.md files in each `src/flx/{module}/`
3. ⏳ Create `examples/` directories with working code
4. ⏳ Migrate content from `/docs/` to appropriate modules
5. ⏳ Add hierarchical navigation links
6. ⏳ Remove legacy `/docs/` files

### **Phase 2: Plugins (`flx-*/`)**
1. Create root README.md with plugin overview + links to core
2. Update module docstrings referencing core concepts
3. Create module README.md files in `src/{plugin}/`
4. Create plugin-specific examples
5. Migrate plugin-specific docs
6. Add navigation showing core → plugin → implementation hierarchy

### **Phase 3: Implementations (`client-b-poc-*/`, `client-a-oud-mig/`)**
1. Create project README.md with business context + plugin links
2. Update module docstrings with business process context
3. Create module README.md with implementation guides
4. Create business process examples in `examples/`
5. Create deployment examples in `scripts/examples/`
6. Add navigation showing full dependency chain

### **Phase 4: Independent Utilities (`dc-code-analyzer/`)**
1. Create tool README.md with utility overview
2. Update Django app documentation
3. Create user guide in appropriate modules
4. Create usage examples
5. Maintain independence from FLX framework references

## Quality Gates

### **Documentation Completeness**
- [ ] All public modules have comprehensive README.md
- [ ] All public APIs have comprehensive docstrings with examples
- [ ] All projects have working examples in `examples/`
- [ ] All cross-references are accurate and functional
- [ ] Navigation hierarchy is clear and complete

### **GitHub Navigation**
- [ ] Links work correctly in GitHub interface
- [ ] Breadcrumb navigation is consistent
- [ ] Hierarchy relationships are clear
- [ ] Examples are discoverable and executable
- [ ] No broken links between projects

### **Content Quality**
- [ ] Examples run without errors
- [ ] Documentation matches actual implementation
- [ ] Cross-references show proper dependency hierarchy
- [ ] Business context is clear for implementation projects
- [ ] Technical depth is appropriate for target audience

## Implementation Priority

1. **🔴 HIGH**: `flx/` core framework (foundation for everything)
2. **🟡 MEDIUM**: `flx-*` plugins (depend on core)
3. **🟢 LOW**: Implementation projects (depend on plugins)
4. **🟢 LOW**: Independent utilities (no dependencies)

## Success Metrics

- **Developer Efficiency**: Developers can navigate from concept to implementation using only GitHub interface
- **Documentation Accuracy**: Documentation is always current with code changes
- **Discoverability**: Related concepts and dependencies are easily found
- **Onboarding Speed**: New developers can understand project relationships and get started quickly
- **Maintenance**: Documentation maintenance is part of normal development workflow

---

This standardization creates a seamless, hierarchical documentation experience optimized for GitHub navigation while maintaining the technical depth needed for each project type.