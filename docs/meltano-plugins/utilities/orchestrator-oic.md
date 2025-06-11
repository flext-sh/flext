# Orchestrator OIC

This plugin is responsible for configuration, management and monitoring of flows between Oracle WMS Cloud, Oracle Integration Cloud (OIC) and Oracle Autonomous Database.

## Features

- Integration Configuration in OIC for connection with WMS Cloud
- Webhook Configuration for real-time events
- Configuration and management of scheduled jobs for FTP file verification
- Autonomous Database table creation and maintenance
- Data flow monitoring and error logging
- Job status control and execution retry

## Dependencies

```yaml
# Main dependencies
- oracle-cloud-sdk
- requests
- sqlalchemy
- cx_Oracle
- schedule
- pydantic

# Development dependencies  
- pytest
- pytest-mock
- pytest-cov
```

## Usage

```bash
# Install the plugin
meltano install utility orchestrator-oic

# Run the orchestrator
meltano run orchestrator-oic
```

## Available Commands

### `setup`

Initial OIC environment setup

```bash
meltano run orchestrator-oic:setup
```

### `monitor`

Monitor active integrations

```bash
meltano run orchestrator-oic:monitor
```

### `sync`

Synchronize data between systems

```bash
meltano run orchestrator-oic:sync
```

### `status`

Check system status

```bash
meltano run orchestrator-oic:status
```

## Configuration

```yaml
utilities:
  - name: orchestrator-oic
    namespace: orchestrator_oic
    pip_url: .
    executable: orchestrator-oic
    settings:
      # OIC Configuration
      - name: oic_url
        label: OIC Instance URL
        kind: string
        required: true
        description: Oracle Integration Cloud instance URL
      - name: oic_username
        label: OIC Username  
        kind: string
        required: true
        description: Username for OIC authentication
      - name: oic_password
        label: OIC Password
        kind: password
        required: true
        description: Password for OIC authentication
        
      # WMS Configuration
      - name: wms_url
        label: WMS Cloud URL
        kind: string
        required: true
        description: Oracle WMS Cloud instance URL
      - name: wms_username
        label: WMS Username
        kind: string
        required: true
        description: Username for WMS authentication
      - name: wms_password
        label: WMS Password
        kind: password
        required: true
        description: Password for WMS authentication
        
      # Autonomous Database Configuration
      - name: adb_wallet_path
        label: ADB Wallet Path
        kind: string
        required: true
        description: Path to Oracle Autonomous Database wallet
      - name: adb_connection_string
        label: ADB Connection String
        kind: string
        required: true
        description: Connection string for Autonomous Database
      - name: adb_username
        label: ADB Username
        kind: string
        required: true
        description: Username for Autonomous Database
      - name: adb_password
        label: ADB Password
        kind: password
        required: true
        description: Password for Autonomous Database
        
      # Scheduling Configuration
      - name: schedule_interval
        label: Schedule Interval
        kind: integer
        default: 300
        description: Job execution interval in seconds
      - name: retry_attempts
        label: Retry Attempts
        kind: integer
        default: 3
        description: Number of retry attempts for failed jobs
        
      # Monitoring Configuration
      - name: log_level
        label: Log Level
        kind: options
        options:
          - DEBUG
          - INFO
          - WARNING
          - ERROR
        default: INFO
        description: Application log level

# This configuration makes the job periodically check the SFTP directory
# and process new files when they are available
```

## FTP File Processing

The orchestrator monitors the configured SFTP directory and processes new files:

```yaml
# FTP Configuration
- name: ftp_host
  label: FTP Host
  kind: string
  required: true
  description: FTP server hostname or IP
- name: ftp_port
  label: FTP Port
  kind: integer
  default: 22
  description: FTP server port
- name: ftp_username
  label: FTP Username
  kind: string
  required: true
  description: Username for FTP authentication
- name: ftp_password
  label: FTP Password
  kind: password
  required: true
  description: Password for FTP authentication
- name: ftp_directory
  label: FTP Directory
  kind: string
  default: "/incoming"
  description: Directory path to monitor for files
```

## Project Structure

```
src/orchestrator_oic/
├── __init__.py
├── main.py                   # Main entry point
├── orchestrator.py           # Orchestration logic
├── config/
│   ├── __init__.py
│   ├── settings.py           # Configuration management
│   └── logging.py            # Logging configuration
├── services/
│   ├── __init__.py
│   ├── oic_service.py        # OIC integration service
│   ├── wms_service.py        # WMS integration service
│   ├── adb_service.py        # Autonomous Database service
│   └── scheduler_service.py  # Scheduling service
├── models/
│   ├── __init__.py
│   ├── job.py                # Job data models
│   └── integration.py        # Integration data models
└── utils/
    ├── __init__.py
    ├── logger.py             # Logging utilities
    └── exceptions.py         # Custom exceptions
```

## Data Flow

```
WMS Cloud → OIC → Orchestrator → Autonomous Database
     ↑                              ↓
     └─────── Status/Errors ←────────┘
```

## Error Handling

The orchestrator implements comprehensive error handling:

- Connection failures with automatic retry
- Data validation errors
- Integration flow monitoring
- Status notification and alerting

## Development

```bash
# Install development dependencies
poetry install --dev

# Run tests
poetry run pytest

# Run with debug logging
LOG_LEVEL=DEBUG poetry run orchestrator-oic
```

## Examples

### Complete Pipeline Configuration

```yaml
schedules:
  - name: wms-to-adb-sync
    interval: "@hourly"
    job: orchestrator-oic monitor && orchestrator-oic sync
```

### Custom Schedule Configuration

```yaml
environments:
  - name: prod
    config:
      plugins:
        utilities:
          - name: orchestrator-oic
            config:
              schedule_interval: 1800  # 30 minutes
              retry_attempts: 5
              log_level: INFO
```
