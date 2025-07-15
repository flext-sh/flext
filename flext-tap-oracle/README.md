# flext-tap-oracle

Modern Oracle Database Tap with Enterprise Features for the FLEXT ecosystem.

## Overview

This tap provides comprehensive Oracle Database extraction capabilities supporting:

- Oracle Database tables and views
- High-performance data extraction
- Enterprise-grade reliability and monitoring

## Features

- High-performance async data extraction
- Enterprise error handling and monitoring
- Circuit breaker patterns for resilience
- Zero-code duplication across sources
- Comprehensive configuration management
- Full observability and metrics

## Installation

```bash
pip install flext-tap-oracle
```

## Usage

Configure the tap using a config.JSON file:

```json
{
  "connection_type": "database",
  "host": "oracle.example.com",
  "port": 1521,
  "service_name": "ORCL",
  "username": "user",
  "password": "password",
  "schema": "HR",
  "tables": ["employees", "departments"]
}
```

Run the tap:

```bash
tap-oracle --config config.json --catalog catalog.json
```

## Configuration

See the configuration documentation for all available options.

## Development

This project uses Poetry for dependency management and follows FLEXT ecosystem standards.
