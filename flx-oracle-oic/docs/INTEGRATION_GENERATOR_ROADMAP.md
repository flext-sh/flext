# tap-oic Integration Generator and Workflow Creator Roadmap

> **Date**: June 15, 2025
> **Version**: 3.0 Roadmap
> **Status**: PLANNED IMPLEMENTATION

## Executive Summary

This document outlines the roadmap for extending tap-oic beyond its current data extraction capabilities to become a full-featured integration generator and workflow creator for Oracle Integration Cloud (OIC).

## Table of Contents

1. [Vision and Goals](#vision-and-goals)
2. [Technical Architecture](#technical-architecture)
3. [Implementation Phases](#implementation-phases)
4. [Key Features](#key-features)
5. [API Requirements](#api-requirements)
6. [Implementation Details](#implementation-details)
7. [Success Criteria](#success-criteria)

## Vision and Goals

### Vision
Transform tap-oic from a data extraction tool into a comprehensive integration platform that can:
- Generate OIC integrations programmatically
- Create workflows from configuration
- Provide infrastructure-as-code for OIC
- Enable GitOps workflows for integration management

### Goals
1. **Programmatic Integration Creation**: Generate OIC integrations without Visual Designer
2. **Configuration-Driven Workflows**: Define integrations in YAML/JSON
3. **Singer Ecosystem Integration**: Leverage existing taps and targets
4. **Version Control**: Enable Git-based integration management
5. **CI/CD Integration**: Support automated deployment pipelines

## Technical Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         tap-oic v3.0                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │
│  │  Discovery  │  │ Extraction  │  │  Generator  │  │  Workflow │ │
│  │   Engine    │  │   Engine    │  │   Engine    │  │  Creator  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘ │
│         │                │                 │               │        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                Integration Definition Language                │  │
│  │                      (IDL Processor)                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Template Engine                           │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐ │  │
│  │  │ Database │  │   REST   │  │   SOAP   │  │   Custom   │ │  │
│  │  │Templates │  │Templates │  │Templates │  │ Templates  │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────────┘ │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                   OIC API Extensions                         │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐ │  │
│  │  │    IAR   │  │  Config  │  │ Metadata │  │  Deploy    │ │  │
│  │  │ Builder  │  │ Manager  │  │  Manager │  │  Manager   │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────────┘ │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                    Oracle Integration Cloud REST API
```

### Component Details

#### 1. Generator Engine
- Converts configurations to OIC integration definitions
- Supports multiple input formats (YAML, JSON, Python)
- Validates configurations against OIC constraints
- Generates optimized integration flows

#### 2. Workflow Creator
- Orchestrates complex multi-step integrations
- Manages dependencies between integrations
- Handles conditional logic and branching
- Supports parallel and sequential execution

#### 3. Integration Definition Language (IDL)
- Domain-specific language for OIC integrations
- Abstracts OIC complexity
- Provides reusable components
- Enables version control

#### 4. Template Engine
- Pre-built templates for common patterns
- Customizable for specific use cases
- Supports all OIC adapter types
- Includes best practices

## Implementation Phases

### Phase 1: Foundation (Q3 2025)
- [ ] Design Integration Definition Language
- [ ] Implement basic template engine
- [ ] Create IAR file builder
- [ ] Develop configuration validator

### Phase 2: Core Generation (Q4 2025)
- [ ] Implement REST integration generator
- [ ] Add database integration support
- [ ] Create transformation mapping engine
- [ ] Build deployment manager

### Phase 3: Advanced Features (Q1 2026)
- [ ] Add SOAP/XML support
- [ ] Implement custom adapter framework
- [ ] Create visual workflow designer
- [ ] Add GitOps integration

### Phase 4: Enterprise Features (Q2 2026)
- [ ] Multi-tenant support
- [ ] Advanced security features
- [ ] Performance optimization
- [ ] Monitoring integration

## Key Features

### 1. Configuration-Driven Integration Creation

```yaml
# integration.yaml
apiVersion: oic/v1
kind: Integration
metadata:
  name: customer-sync
  description: Sync customers from database to REST API
spec:
  source:
    type: database
    adapter: oracle-db
    connection:
      host: ${DB_HOST}
      port: 1521
      service: ${DB_SERVICE}
    query: |
      SELECT customer_id, name, email, updated_at
      FROM customers
      WHERE updated_at > :last_sync_time

  transformation:
    mapping:
      - source: customer_id
        target: id
      - source: name
        target: full_name
      - source: email
        target: contact_email

  target:
    type: rest
    adapter: rest-adapter
    endpoint: https://api.example.com/customers
    method: POST
    authentication: oauth2

  schedule:
    frequency: hourly
    timezone: UTC
```

### 2. Workflow Definition

```yaml
# workflow.yaml
apiVersion: oic/v1
kind: Workflow
metadata:
  name: order-processing
spec:
  steps:
    - name: validate-order
      integration: order-validation

    - name: check-inventory
      integration: inventory-check
      condition: "steps.validate-order.status == 'valid'"

    - name: process-payment
      integration: payment-processor
      dependsOn: [check-inventory]

    - name: ship-order
      integration: shipping-service
      dependsOn: [process-payment]
      parallel: true

    - name: send-notification
      integration: notification-service
      dependsOn: [process-payment]
      parallel: true
```

### 3. Singer Integration

```python
# Generate OIC integration from Singer tap/target
from tap_oic.generator import IntegrationGenerator

generator = IntegrationGenerator()

# Create integration from Singer components
integration = generator.create_from_singer(
    tap="tap-mysql",
    tap_config={
        "host": "localhost",
        "database": "sales",
        "user": "reader"
    },
    target="target-snowflake",
    target_config={
        "account": "myaccount",
        "database": "analytics",
        "schema": "raw"
    },
    transformations=[
        {"type": "rename", "from": "cust_id", "to": "customer_id"},
        {"type": "filter", "condition": "status = 'active'"}
    ]
)

# Deploy to OIC
integration.deploy()
```

### 4. CLI Commands

```bash
# Generate integration from configuration
tap-oic generate --config integration.yaml --output customer-sync.iar

# Deploy integration
tap-oic deploy --file customer-sync.iar --activate

# Create workflow
tap-oic workflow create --config workflow.yaml

# Validate configuration
tap-oic validate --config integration.yaml

# Generate from Singer tap/target
tap-oic generate-from-singer \
  --tap tap-mysql \
  --target target-postgres \
  --transform transforms.yaml
```

## API Requirements

### Required OIC API Enhancements

To fully implement the generator, these API capabilities are needed:

1. **Integration Creation API**
   ```http
   POST /ic/api/integration/v1/integrations/create
   Content-Type: application/json

   {
     "name": "CUSTOMER_SYNC",
     "description": "Customer synchronization",
     "pattern": "scheduled",
     "source": {...},
     "target": {...},
     "transformations": [...]
   }
   ```

2. **Connection Creation API**
   ```http
   POST /ic/api/integration/v1/connections/create
   Content-Type: application/json

   {
     "name": "DB_CONNECTION",
     "adapter": "oracle-db-adapter",
     "properties": {...}
   }
   ```

3. **Transformation Builder API**
   ```http
   POST /ic/api/integration/v1/transformations/build
   Content-Type: application/json

   {
     "sourceSchema": {...},
     "targetSchema": {...},
     "mappings": [...]
   }
   ```

### Workaround Strategy

Until these APIs are available, we'll:
1. Generate IAR files locally
2. Use existing import API
3. Provide templates for common patterns
4. Enable local testing before deployment

## Implementation Details

### 1. Generator Module Structure

```
tap_oic/
├── generator/
│   ├── __init__.py
│   ├── core.py              # Core generator logic
│   ├── templates/           # Integration templates
│   ├── builders/            # IAR file builders
│   ├── validators/          # Configuration validators
│   └── transformers/        # Transformation engines
├── workflow/
│   ├── __init__.py
│   ├── engine.py           # Workflow execution engine
│   ├── scheduler.py        # Schedule management
│   └── orchestrators/      # External orchestrator adapters
└── idl/
    ├── __init__.py
    ├── parser.py           # IDL parser
    ├── compiler.py         # IDL to OIC compiler
    └── schema.py           # IDL schema definitions
```

### 2. Integration Definition Language (IDL)

```python
# Example IDL syntax
from tap_oic.idl import Integration, Source, Target, Transform

integration = Integration(
    name="customer_sync",
    description="Sync customers to CRM"
)

integration.source = Source.database(
    adapter="oracle",
    query="SELECT * FROM customers WHERE modified > :last_sync"
)

integration.transform = Transform()
    .rename("cust_id", "customer_id")
    .filter("status = 'active'")
    .map({
        "full_name": "first_name + ' ' + last_name",
        "age": "YEAR(CURRENT_DATE) - YEAR(birth_date)"
    })

integration.target = Target.rest(
    url="https://api.crm.com/customers",
    method="POST",
    batch_size=100
)

# Generate IAR file
integration.build("customer_sync.iar")
```

### 3. Template System

```python
# Database to REST template
from tap_oic.generator.templates import DatabaseToRestTemplate

template = DatabaseToRestTemplate()
template.configure(
    source_connection="ORACLE_DB",
    source_query="SELECT * FROM orders",
    target_url="https://api.example.com/orders",
    transformations=[
        {"rename": {"order_id": "id"}},
        {"filter": "status != 'cancelled'"}
    ]
)

iar_file = template.generate()
```

## Success Criteria

### Technical Success Metrics
1. Generate 90% of common integration patterns
2. Reduce integration development time by 70%
3. Enable version control for all integrations
4. Support automated testing of integrations
5. Achieve 99% deployment success rate

### Business Success Metrics
1. Increase integration delivery speed 5x
2. Reduce integration maintenance cost by 60%
3. Enable self-service integration creation
4. Improve integration quality and consistency
5. Support 100+ integration templates

## Next Steps

1. **Validate API Capabilities**: Test if OIC Gen3 supports required APIs
2. **Design IDL Specification**: Create formal language specification
3. **Build Prototype**: Implement basic generator for REST integrations
4. **Create Templates**: Develop templates for common patterns
5. **User Testing**: Validate with real-world use cases

## Conclusion

This roadmap transforms tap-oic into a comprehensive integration platform that brings infrastructure-as-code principles to Oracle Integration Cloud. By implementing these features, organizations can achieve faster, more reliable, and more maintainable integration development.

---

**Note**: This roadmap assumes Oracle will provide or we can work around the current API limitations. The implementation will adapt based on actual OIC capabilities and customer requirements.
