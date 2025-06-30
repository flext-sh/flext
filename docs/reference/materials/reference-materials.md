# FLEXT Framework Reference Materials Guide - Reference

> **Function**: Comprehensive reference materials for FLEXT Framework development and Oracle integrations | **Audience**: Developers, architects, technical writers | **Status**: ✅ VALIDATED

[![Reference](https://img.shields.io/badge/reference-materials-blue.svg)](./index.md)
[![Oracle](https://img.shields.io/badge/oracle-integrations-red.svg)](../../guides/oracle/index.md)
[![Framework](https://img.shields.io/badge/framework-FLEXT%200.4.0-orange.svg)](../../index.md)

**Centralized reference materials, examples, SDKs, and integration resources supporting FLEXT Framework implementation following hexagonal architecture patterns**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Reference](../index.md) → **📂 Materials**: [Materials Hub](./index.md) → **📄 Current**: Reference Materials Guide

### **📍 Learning Path Position**

```
[Reference Hub](../index.md) → [Materials Hub](./index.md) → **[REFERENCE MATERIALS]** → [Oracle Implementation](../../guides/oracle/index.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Reference Materials Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔗 Source Materials**: [Oracle Documentation](../../guides/oracle/index.md)
- **🔗 Related**: [Architecture Guide](../../architecture/index.md), [Development Standards](../../development/index.md)

---

## 📋 **Overview**

This guide centralizes reference materials, examples, SDKs, and legacy integrations to support the FLEXT Framework implementation following hexagonal architecture patterns.

### **Prerequisites**

- [Architecture Hub](../../architecture/index.md) - Understanding hexagonal architecture principles
- [Getting Started](../../getting-started/index.md) - Framework setup and installation
- [Oracle Integration Guides](../../guides/oracle/index.md) - Oracle implementation context

### **What You'll Find**

- Oracle platform reference documentation and resources
- Integration examples and implementation patterns
- Development tools and testing resources
- Legacy integration references and best practices

## Index

- [PyAuto Reference Materials](#pyauto-reference-materials)
  - [Index](#index)
  - [Overview](#overview)
  - [Structure](#structure)
  - [How to Use](#how-to-use)
  - [Oracle Documentation](#oracle-documentation)
  - [Integration Examples](#integration-examples)
  - [Governance](#governance)

## Overview

The `reference/` folder is a collection of support and reference materials, serving both as technical reference and repository of best practices. **It does not contain active project source code**, but rather resources that help understand platforms and integration patterns aligned with our Hexagonal Architecture approach.

## Structure

### `/oracle/` — Oracle Platform Resources

- `documentation/` — Official Oracle documentation in various formats
  - REST API guides (WMS, OIC)
  - Implementation and configuration guides
  - Security and SSO documentation
- `api-specs/` — API specifications and OpenAPI definitions
- `integration-guides/` — Specific integration documentation and guides

### `/examples/` — Integration Examples and Patterns

- `legacy-integrations/` — Previous integrations and historical examples
  - Legacy Oracle-WMS projects
  - Reference configurations and artifacts
- `oracle-official/` — Official examples provided by Oracle
  - OIC integration patterns
  - Cloud-native examples
  - Utilities and tools

### `/tools/` — Development and Integration Tools

- `postman/` — Postman collections and API testing tools
- `schemas/` — Data schemas and format definitions
- `mappings/` — WMS-specific solutions and data transformations

## How to Use

Materials in this directory should be used as:

1. **Technical reference** to understand APIs, formats, and patterns
2. **Source of best practices** for developing new integrations following Hexagonal Architecture
3. **Knowledge base** for troubleshooting and debugging
4. **Adaptation source** for implementing adapters and ports in the FLEXT framework

**Important:** When using code examples or configurations:

- Always verify the version/date of material and current compatibility
- Adapt to follow project patterns and libraries (FLEXT framework, hexagonal architecture)
- Document any reuse or adaptation
- Consider how examples fit into inbound/outbound port patterns

## Oracle Documentation

The directory includes official documentation in various formats (PDF, Markdown) for offline access and quick reference:

- `wms-rest-api-guide.{md,pdf}` — Complete WMS Cloud REST API guide
- `integration-api-guide.{md,pdf}` — OIC API documentation
- `security-guide.{md,pdf}` — Security guide and best practices
- `sso-and-alternate-authentication-setup.{md,pdf}` — Authentication setup
- `implementation-and-configuration-guide.{md,pdf}` — Implementation guide

**For current documentation**, always consult official sites:

- [Oracle WMS Cloud Documentation](https://docs.oracle.com/en/cloud/saas/warehouse-management/index.html)
- [Oracle Integration Cloud Documentation](https://docs.oracle.com/en/cloud/paas/integration-cloud/index.html)
- [Oracle Autonomous Database Documentation](https://docs.oracle.com/en/cloud/paas/autonomous-database/index.html)

## Integration Examples

Examples include:

1. **Postman Collections** — In `tools/postman/`
2. **OIC Projects** — In `examples/oracle-official/` and `examples/legacy-integrations/`
3. **Schemas and Definitions** — In `tools/schemas/` and `tools/mappings/`
4. **Integration Patterns** — Examples showing adapter implementation patterns

For each example subdirectory, consult the specific README for usage details and relevance to the current hexagonal architecture.

## Governance

This directory follows governance guidelines to maintain its usefulness:

- All materials must have clear metadata (version, date, origin)
- Subdirectories must include README explaining their content
- Outdated materials must be marked as such
- Examples should indicate their relevance to current architecture patterns

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Architecture Hub](../../architecture/index.md) - Essential understanding of hexagonal architecture patterns for proper reference material usage
- [Getting Started](../../getting-started/index.md) - Framework fundamentals and installation required before utilizing reference materials
- [Oracle Integration Overview](../../guides/oracle/index.md) - Oracle integration context for understanding platform-specific references

### **Next Steps**

- [Oracle WMS Integration Guide](../../guides/oracle/oracle-wms-comprehensive-integration-guide.md) - Practical implementation using reference materials
- [Oracle OIC Integration Guide](../../guides/oracle/oracle-oic-complete-guide.md) - OIC integration patterns utilizing reference documentation
- [Development Standards](../../development/index.md) - Development practices implementing reference patterns

### **Related Topics**

- [Examples Hub](../../examples/index.md) - Working code examples demonstrating reference implementations
- [API Reference](../../api-reference/index.md) - Complete API documentation complementing reference materials
- [Infrastructure Documentation](../../infrastructure/index.md) - Infrastructure patterns referenced in integration examples
- [Testing Documentation](../../development/testing/index.md) - Testing strategies for reference implementations
- [Deployment Hub](../../deployment/index.md) - Production deployment utilizing reference configurations

---

## 🆘 **Support and Updates**

For questions about reference materials:

1. Check the specific Oracle documentation links for current versions
2. Verify compatibility with current FLEXT Framework version
3. Consult [Development Standards](../../development/index.md) for adaptation guidelines
4. Review [Examples](../../examples/index.md) for practical implementation patterns

### **Maintenance Guidelines**

- All materials include metadata (version, date, origin)
- Outdated materials are clearly marked
- Examples indicate relevance to current architecture patterns
- Regular updates follow framework evolution

---

**📂 Hub**: [Reference Materials Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLEXT 0.4.0+ | **Updated**: 2025-06-11
