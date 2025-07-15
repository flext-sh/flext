# FLEXT DBT Oracle WMS

Oracle WMS (Warehouse Management System) data transformation package using DBT and FLEXT framework.

## Description

This package provides comprehensive DBT integration for Oracle WMS data transformation using flext-core standards and modern Python 3.13 type system.

**IMPORTANT**: This package is for Oracle WMS API integration, NOT Oracle Database.

## Features

- DBT models for Oracle WMS entities (allocation, orders, inventory, etc.)
- Staging, marts, and metrics layers
- Enterprise-grade data quality tests
- Oracle-specific macros and utilities
- Comprehensive documentation

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Run DBT transformations
dbt run

# Run tests
dbt test

# Generate documentation
dbt docs generate
```

## Configuration

Configure your `profiles.yml` to connect to your Oracle WMS data source.

## DBT Models

- **Staging**: Raw data transformations (`stg_wms__*`)
- **Marts**: Business-ready models (`opr_wms__*`, `ana_wms__*`)
- **Metrics**: KPIs and dashboard models (`met_wms__*`)

## License

MIT License
