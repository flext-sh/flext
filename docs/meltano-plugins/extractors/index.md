# 🔍 Extractors Hub - Data Source Plugins

> **Function**: Meltano extractor plugins for enterprise data sources | **Audience**: Data engineers, ETL developers | **Status**: ✅ Production Ready

[![Extractors](https://img.shields.io/badge/extractors-3_plugins-blue.svg)](#extractor-categories)
[![Oracle](https://img.shields.io/badge/oracle-ADB%20%7C%20OIC%20%7C%20WMS-red.svg)](./tap-oracle-adb.md)
[![Singer SDK](https://img.shields.io/badge/singer--sdk-0.46.4-green.svg)](../../development/guides/singer_sdk-integration.md)

**Enterprise-grade Meltano extractor plugins for Oracle ADB, OIC, and WMS data extraction with Singer SDK compliance**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Section**: [Meltano Plugins](../index.md) → **📄 Current**: Extractors Hub

### **📍 Learning Path Position**

```
[Meltano Plugins Hub](../index.md) → **[EXTRACTORS HUB]** → [Oracle Integration](../../guides/oracle/index.md)
```

## 🎯 **Quick Links**

- **📂 Parent Hub**: [Meltano Plugins Hub](../index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **📊 Data Pipeline**: [Oracle ADB Extractor](./tap-oracle-adb.md)

---

## 📊 **Overview**

Meltano extractor plugins (taps) provide enterprise-grade data extraction capabilities from Oracle databases, integration platforms, and warehouse management systems. Built on Singer SDK standards with FLEXT Framework integration.

### **Extractor Categories**

| **Plugin**                            | **Data Source**            | **Type**  | **Status**    | **Key Features**                                  |
| ------------------------------------- | -------------------------- | --------- | ------------- | ------------------------------------------------- |
| **[Oracle ADB](./tap-oracle-adb.md)** | Oracle Autonomous Database | Database  | ✅ Production | SQL extraction, table discovery, incremental sync |
| **[Oracle OIC](./tap-oic.md)**        | Oracle Integration Cloud   | API/REST  | ✅ Production | Integration flow extraction, metadata capture     |
| **[OIC WMS](./tap-oic-wms.md)**       | Oracle WMS via OIC         | Warehouse | ✅ Production | WMS data extraction via OIC integration           |

### **🚀 Key Capabilities**

- **Oracle Native**: Full Oracle ecosystem support (ADB, OIC, WMS)
- **Singer Compliance**: Full Singer SDK specification compliance
- **Incremental Sync**: Efficient delta data extraction
- **Schema Discovery**: Automatic table and field discovery
- **Enterprise Features**: Connection pooling, error handling, monitoring

## 🎓 **Learning Paths**

### **🆕 New to Data Extraction**

1. **Foundation**: [Singer SDK Integration](../../development/guides/singer_sdk-integration.md)
2. **First Extractor**: [Oracle ADB Extractor](./tap-oracle-adb.md)
3. **Advanced Features**: [Incremental Sync Patterns](../../guides/integration/index.md)

### **🏗️ Integration Engineers**

1. **API Extraction**: [Oracle OIC Extractor](./tap-oic.md)
2. **Warehouse Data**: [OIC WMS Extractor](./tap-oic-wms.md)
3. **Custom Development**: [Plugin Development Guide](../../guides/development/plugin-development-guide.md)

### **📊 Data Engineers**

1. **Database Extraction**: [Oracle ADB Extractor](./tap-oracle-adb.md)
2. **Pipeline Integration**: [Meltano Contributing Guide](../../development/guides/meltano-contributing-guide.md)
3. **Performance Tuning**: [Optimization Guide](../../optimization/performance/index.md)

## 🔗 **Cross-References**

### **Prerequisites**

- [Meltano Plugins Hub](../index.md) - Understanding Meltano plugin ecosystem
- [Singer SDK Integration](../../development/guides/singer_sdk-integration.md) - Singer SDK framework fundamentals
- [Development Hub](../../development/index.md) - Development environment setup

### **Next Steps**

- [Loaders Hub](../loaders/index.md) - Data destination plugins for extracted data
- [Transformers Hub](../transformers/index.md) - Data transformation after extraction
- [Oracle Integration](../../guides/oracle/index.md) - Complete Oracle integration strategies

### **Related Topics**

- [API Reference](../../api-reference/index.md) - Extractor plugin API documentation
- [Testing Hub](../../development/testing/index.md) - Extractor testing strategies
- [Examples Hub](../../examples/index.md) - Working extractor implementation examples

---

## 📊 **Section Metrics**

- **Available Extractors**: 3 plugins
- **Oracle Coverage**: ADB, OIC, WMS complete
- **Singer SDK Compliance**: 100%
- **Production Readiness**: 100% (3/3 plugins)
- **Documentation Completeness**: 95%

---

**📂 Hub**: [Extractors Hub](#) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLEXT 0.4.0+ | **Updated**: 2025-06-11
