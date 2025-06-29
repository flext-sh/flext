# client-b OIC-WMS Integration Project

A comprehensive integration solution between Oracle Warehouse Management System (WMS) Cloud v25A/25B, Oracle Integration Cloud (OIC), and Oracle Autonomous Database using FLX Framework and Meltano.

## Overview

This flext_project implements a robust integration solution for synchronizing data between Oracle WMS Cloud (v25A/25B) and Oracle Autonomous Database, with OIC handling the orchestration of workflows. The system addresses key business needs through automated data flows:

1. **Direct API Extraction** - Retrieving real-time data from WMS APIs and loading to Autonomous Database
2. **Batch File Processing** - Handling CSV files via SFTP with transformation pipelines for initial loads
3. **Event-Driven Processing** - Capturing WMS events via webhooks for immediate actions
4. **Centralized Data Management** - Consolidating operational data for reporting and analysis

The solution combines batch processing for initial loads with event-driven architecture for real-time updates, providing both reliability and timely information processing.

## Architecture

The integration follows a hybrid architecture pattern with three key components:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Oracle WMS     │     │     Oracle      │     │   Oracle        │
│    Cloud        │◄───►│  Integration    │◄───►│   Autonomous    │
│ (v25A/25B)      │     │  Cloud (OIC)    │     │   Database      │
│                 │     │                 │     │                 │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
    ┌─────────┐            ┌─────────┐             ┌─────────┐
    │ Webhook │            │ REST API│             │ Views & │
    │ Output  │            │ Orchestr│             │ Stored  │
    │Interface│            │ ation   │             │ Procs   │
    └─────────┘            └─────────┘             └─────────┘
         │                       │                       │
         │                       │                       │
         └───────────┬───────────┘                       │
                     │                                   │
                     ▼                                   ▼
              ┌─────────────┐                     ┌─────────────┐
              │ SFTP/CSV    │                     │ Reporting & │
              │ Initial Load│                     │ Downstream  │
              └─────────────┘                     └─────────────┘
```

### Key Components

1. **Oracle WMS Cloud (v25A/25B)** - Source and destination for warehouse operational data

   - Provides events (allocations, order status changes) via webhooks
   - Receives data via REST APIs
   - Supports XML and CSV data formats
   - Configured with Output Interfaces for real-time event propagation

2. **Oracle Integration Cloud (OIC)** - Central integration platform

   - Hosts integration flows for data orchestration
   - Connects via REST, FTP, and DB adapters
   - Handles data transformation and error management
   - Provides monitoring and reprocessing capabilities

3. **Oracle Autonomous Database** - Centralized data repository

   - Stores staging tables with audit capabilities
   - Provides views and procedures for data transformation
   - Serves as historical record and reporting source
   - Implements materialized views for performance optimization

4. **DCauto/Meltano Framework** - Integration technology
   - Manages plugin configuration and connections
   - Provides extraction and loading capabilities
   - Offers scheduling and monitoring features
   - Supports both batch and real-time processing patterns

## Data Flows

The integration implements three primary data flows:

1. **Carga Inicial (Initial Load)**

   - WMS Cloud exports data to CSV files via SFTP
   - Files are processed and loaded to staging tables
   - Provides baseline data for incremental processing
   - Implemented as a scheduled batch process

2. **Pedidos (Orders)**

   - Bidirectional flow supporting both inbound and outbound scenarios:
     - **Inbound**: Orders from external systems loaded to WMS via OIC
     - **Outbound**: Real-time webhook triggers when orders are created/modified in WMS
   - Data is stored in ORDER_HDR_STAGE and ORDER_DTL_STAGE tables
   - Supports UPSERT operations for updates to existing orders

3. **Alocações (Allocations)**
   - Unidirectional flow from WMS to Autonomous Database
   - WMS triggers webhook when inventory is allocated
   - OIC captures the event and stores in ALLOC_STAGE table
   - Enables real-time tracking of order fulfillment

## Prerequisites

Before setup, ensure you have access to:

- Python 3.10
- Oracle WMS Cloud (25A/25B) with API access
- Oracle Integration Cloud (OIC) instance
- Oracle Autonomous Database (ATP or ADW)
- SFTP server for batch file processing

## Setup

Follow these steps to set up the integration environment:

1. Clone this repository:

   ```bash
   git clone <repository-url>
   cd client-b-oic-wms
   ```

2. Install DCauto with Meltano dependencies:

   ```bash
   pip install -e ../../[meltano]
   ```

3. Configure your environment:

   ```bash
   cp .env.example .env
   # Edit .env to add your credentials and connection details
   ```

4. Create required directories:

   ```bash
   mkdir -p logs output/{oic,wms,oic_executions}
   ```

5. Initialize Meltano:

   ```bash
   meltano install
   ```

## Configuration

The flext_project uses a layered configuration approach:

- **meltano.yml** - Main Meltano flext_project configuration defining plugins and pipelines
- **config/config.yml** - Detailed configuration for WMS, OIC, and Autonomous DB
- **dcauto.yml** - DCauto-specific configuration for custom plugins
- **.env** - Environment variables containing credentials and connection details

### Security and Connectivity

- All communications use secure protocols (HTTPS, SFTP with encryption)
- Basic Auth or OAuth2 authentication on all endpoints
- Autonomous DB accessed via secure wallet connection
- IP whitelisting implemented for Autonomous DB access
- Credentials managed via environment variables, never hardcoded

## Usage

### Running Data Pipelines

DCauto provides several commands to manage data pipelines:

```bash
# Extract WMS data and load to Oracle
dcauto meltano run wms target-oracle

# Process FTP files and load to Oracle
dcauto meltano run tap-sftp target-oracle
```

### Working with Scripts

For more custom operations, use the provided scripts:

```bash
# Process batch files from FTP
python scripts/process_wms_batch_files.py

# Trigger and monitor OIC workflows
python scripts/oic_orchestrate_workflows.py

# Extract OIC integration metadata
python scripts/oic_extract_integration_metadata.py
```

### Scheduled Operations

The flext_project includes scheduled tasks:

- `wms_to_oracle_daily` - Daily extraction from WMS
- `ftp_to_oracle_hourly` - Hourly processing of FTP files

Manage schedules using Meltano:

```bash
# List all schedules
meltano schedule list

# Start the scheduler
meltano schedule run
```

## Monitoring and Governance

The integration provides comprehensive monitoring across all components:

### Oracle Integration Cloud

- Dashboard metrics for success/failure rates
- Activity logs for each integration instance
- Error notification and reprocessing capabilities
- Business identifiers for easy instance tracking

### Autonomous Database

- Performance monitoring via Performance Hub
- Storage utilization tracking
- Automated backup verification
- Query performance optimization

### Oracle WMS Cloud

- Interface transmission logs review
- Event queue monitoring
- Output interface status tracking

### Operational Procedures

- Daily monitoring checklist
- Error resolution runbook
- SLA definitions for different severity levels
- Monthly review meetings for continuous improvement

## Error Handling and Recovery

The integration implements robust error handling:

- Transactional consistency between header and detail records
- Retry logic for transient failures
- Compensation logic for partial failures
- Detailed error logging with context information
- Notification system for critical failures
- Manual reprocessing capabilities via OIC console

## Project Structure

```
client-b-oic-wms/
├── config/                  # Configuration files
│   └── config.yml           # Main configuration
├── dcauto.yml               # DCauto configuration
├── docs/                    # Project documentation
│   ├── plan_full.md         # Detailed technical plan
│   └── project_plan.md      # Project overview
├── logs/                    # Log files directory
├── meltano.yml              # Meltano flext_project configuration
├── output/                  # Output data files
│   ├── oic/                 # OIC extraction results
│   ├── wms/                 # WMS extraction results
│   └── oic_executions/      # OIC execution results
├── pipelines/               # Airflow DAG definitions
├── scripts/                 # Utility scripts
│   ├── oic_extract_integration_metadata.py
│   ├── oic_orchestrate_workflows.py
│   └── process_wms_batch_files.py
└── transforms/              # Data transformation definitions
```

## Development

### Adding New Entities

To extend the integration with new data entities:

1. Update entity definitions in `config/config.yml`
2. Create extraction logic in DCauto plugins or scripts
3. Define table structures in the Autonomous Database
4. Configure transformation rules if needed
5. Update schedules in `meltano.yml`

### Custom Transformations

For complex data transformations:

1. Create stored procedures in the Autonomous Database
2. Define views for data representation
3. Configure dbt models if using dbt for transformations

## Support and Operations

### Support Levels

- **Level 1:** Basic monitoring and issue identification
- **Level 2:** Technical troubleshooting and resolution
- **Level 3:** Oracle product support escalation

### Service Level Agreements

- Critical issues (integration stops): 4-hour resolution
- Major issues (partial functionality): 1-day resolution
- Minor issues (cosmetic/non-blocking): Scheduled in backlog

### Cutover Strategy

The transition to production follows these steps:

1. Environment preparation (replica of test config)
2. Pre-production data loading
3. Smoke testing in production environment
4. Controlled cutover during maintenance window
5. Post-cutover verification
6. Hypercare support period (2-4 weeks)

## Documentation

For additional details, refer to:

- `docs/plan_full.md` - Complete technical implementation plan
- `docs/project_plan.md` - High-level flext_project overview
- Oracle Documentation for [WMS Cloud](https://docs.oracle.com/en/cloud/saas/warehouse-management.html), [OIC](https://docs.oracle.com/en/cloud/paas/integration-cloud/), and [Autonomous DB](https://docs.oracle.com/en/cloud/paas/autonomous-database/)
