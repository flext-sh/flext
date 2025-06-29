# ⚡ FLX Quick Start - Getting Started

> **Function**: First application in 5 minutes | **Audience**: All developers | **Status**: ✅ Active

[![Quick Start](https://img.shields.io/badge/quickstart-5%20minutes-green.svg)](./quickstart.md)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Getting Started](https://img.shields.io/badge/getting--started-active-green.svg)](./index.md)

**Build your first Oracle integration pipeline using FLX Framework in just 5 minutes**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Getting Started](../index.md) → **📂 Section**: [Basics](./index.md) → **📄 Current**: Quickstart

### **📍 Learning Path Position**

```
[Installation Guide](../setup/installation-guide.md) → **[QUICKSTART]** → [Framework Overview](../concepts/flext-framework-overview.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Basics Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔗 Next Step**: [Framework Overview](../concepts/flext-framework-overview.md)

## 🎯 Prerequisites

- **FLX installed**: Follow the [installation guide](../setup/installation-guide.md) if not yet installed
- **Python 3.13+**: Verify with `python --version`
- **Basic Python knowledge**: Understanding of classes and functions

## 🚀 5-Minute Quick Start

### Step 1: Verify Installation

```bash
# Check FLX version
flext --version

# Test CLI help
flext --help
```

### Step 2: Create Your First Pipeline

Create a simple hello world pipeline:

```python
# hello_world.py
from flext.application.pipelines import Pipeline
from flext.domain.entities import DataSource, DataTarget

# Create simple data pipeline
pipeline = Pipeline(
    name="hello_world",
    source=DataSource(
        type="console",
        data=["Hello", "FLX", "World"]
    ),
    target=DataTarget(type="console")
)

# Execute pipeline
result = pipeline.execute()
print(f"✅ Success! Processed {result.records_processed} records")
```

### Step 3: Run Your Pipeline

```bash
# Run the hello world pipeline
python hello_world.py
```

**Expected Output:**

```
Hello
FLX
World
✅ Success! Processed 3 records
```

### Step 4: Add Data Transformation

Enhance your pipeline with data transformation:

```python
# enhanced_pipeline.py
from flext.application.pipelines import Pipeline
from flext.domain.entities import DataSource, DataTarget
from flext.transformers.basic import DataCleaner

# Enhanced pipeline with transformation
pipeline = Pipeline(
    name="enhanced_example",
    source=DataSource(
        type="console",
        data=[
            {"name": "John Doe", "email": "john@example.com"},
            {"name": "Jane Smith", "email": "jane@example.com"}
        ]
    ),
    target=DataTarget(type="console"),
    transformers=[
        DataCleaner(remove_empty=True, trim_whitespace=True)
    ]
)

result = pipeline.execute()
print(f"✅ Processed {result.records_processed} records with transformation")
```

## 🔧 Add Configuration

### Step 5: Create Configuration File

Create a basic configuration file:

```yaml
# config.yaml
flext:
  version: "0.2.0"

  core:
    log_level: "INFO"
    timeout: 30

  pipelines:
    default_timeout: 300
    batch_size: 100
```

### Step 6: Use Configuration in Pipeline

```python
# configured_pipeline.py
from flext.core import ConfigManager
from flext.application.pipelines import Pipeline

# Load configuration
config = ConfigManager.load_config("config.yaml")

# Use configuration in pipeline
pipeline = Pipeline(
    name="configured_example",
    config=config,
    source=your_source,
    target=your_target
)
```

## 🎯 Next Steps

Congratulations! You've created your first FLX pipeline. Now explore more advanced features:

### **Oracle Integration**

Connect to Oracle systems:

```python
from flext.adapters.oracle import OracleAdapter

# Oracle Database connection
oracle_adapter = OracleAdapter(
    dsn="localhost:1521/XE",
    user="hr",
    password="password"
)

# Use in pipeline
pipeline = Pipeline(
    name="oracle_sync",
    source=oracle_adapter.query_source("SELECT * FROM employees"),
    target=your_target
)
```

### **Error Handling**

Add robust error handling:

```python
try:
    result = pipeline.execute()
    print(f"✅ Pipeline completed: {result.records_processed} records")
except ValidationError as e:
    print(f"❌ Validation failed: {e.message}")
except ConnectionError as e:
    print(f"❌ Connection failed: {e.message}")
```

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Installation Guide](../setup/installation-guide.md) - Essential framework installation before building applications
- [Import Guide](../setup/import-guide.md) - Module import patterns used in quickstart examples
- [Python 3.13+ Environment](https://www.python.org/downloads/) - Required runtime environment setup

### **Next Steps**

- [Framework Overview](../concepts/flext-framework-overview.md) - Deep dive into FLX hexagonal architecture patterns
- [First Pipeline Tutorial](./first-pipeline.md) - Build more complex data processing pipelines
- [Basic Examples](../../examples/basic/index.md) - Explore additional working code examples

### **Related Topics**

- [API Reference Hub](../../api-reference/index.md) - Complete framework API documentation for advanced usage
- [Architecture Hub](../../architecture/index.md) - Design patterns and hexagonal architecture principles
- [Oracle Integration Guide](../../guides/oracle/index.md) - Complete Oracle system integration tutorials
- [Development Hub](../../development/index.md) - Development tools and testing frameworks for applications
- [Infrastructure Hub](../../infrastructure/index.md) - Production infrastructure setup for quickstart applications

---

**📂 Hub**: [Basics Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
