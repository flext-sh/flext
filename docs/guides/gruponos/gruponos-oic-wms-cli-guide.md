# GN WMS CLI - Database Administration Tool

A comprehensive command-line interface for managing Oracle WMS database operations, built with Click and Rich for enhanced user experience.

## Installation & Setup

```bash
# Install dependencies
poetry install

# Verify installation
poetry run gn-wms-cli --version
```

## Available Commands

### 🔧 `config` - Configuration Validation

Validate and display environment configuration from `.env` file:

```bash
# Show all configuration parameters (secrets masked)
poetry run gn-wms-cli config

# Show configuration with sensitive values visible
poetry run gn-wms-cli config --show-secrets

# Export configuration as JSON
poetry run gn-wms-cli config --format=json
```

**Features:**

- Validates all environment variables
- Shows configuration status for each parameter
- Masks sensitive values by default
- Supports JSON export for automation
- Identifies missing required parameters

### 🔍 `check` - Table Structure Inspection

Inspect database tables and their structure:

```bash
# Check all WMS tables (default pattern: WMS_%)
poetry run gn-wms-cli check

# Check specific pattern
poetry run gn-wms-cli check --pattern="WMS_ORDER%"

# Include column details
poetry run gn-wms-cli check --columns

# JSON output format
poetry run gn-wms-cli check --format=json
```

**Options:**

- `--pattern TEXT`: Table name pattern (default: WMS_%)
- `--columns`: Show column structure and data types
- `--audit`: Show audit field status
- `--format [table|json]`: Output format

### 📊 `status` - Comprehensive Status Overview

Display system-wide status and health information:

```bash
# Show complete system status
poetry run gn-wms-cli status
```

**Information displayed:**

- Environment configuration validation
- Database connection status with endpoint details
- WMS tables availability and record counts
- Control tables status and error counts
- External services configuration (WMS, OIC)
- Logging configuration

### 🏗️ `setup` - Database Setup

Complete database setup with WMS and control tables:

```bash
# Complete setup
poetry run gn-wms-cli setup

# Force recreation of existing tables
poetry run gn-wms-cli setup --force

# Skip specific components
poetry run gn-wms-cli setup --skip-wms
poetry run gn-wms-cli setup --skip-control

# Dry run (show what would be done)
poetry run gn-wms-cli setup --dry-run
```

### 🧹 `clear` - Data Cleanup

Clear WMS data for fresh testing:

```bash
# Clear all WMS and control tables
poetry run gn-wms-cli clear

# Clear specific tables only
poetry run gn-wms-cli clear --table WMS_ORDER_HDR --table WMS_ORDER_DTL

# Skip control tables
poetry run gn-wms-cli clear --no-control

# Dry run to see impact
poetry run gn-wms-cli clear --dry-run

# Force without confirmation
poetry run gn-wms-cli clear --force
```

### 🔌 `test` - Connection Testing

Test database connectivity and accessibility:

```bash
# Complete connection test
poetry run gn-wms-cli test

# Test specific components
poetry run gn-wms-cli test --no-wms
poetry run gn-wms-cli test --no-control

# Verbose output for debugging
poetry run gn-wms-cli test --verbose
```

### 📊 `analyze` - Update Table Statistics

Update table statistics for better performance and accurate row counts:

```bash
# Analyze all WMS tables
poetry run gn-wms-cli analyze

# Analyze specific pattern
poetry run gn-wms-cli analyze --pattern="WMS_ORDER%"

# Dry run to see what would be analyzed
poetry run gn-wms-cli analyze --dry-run

# Force without confirmation
poetry run gn-wms-cli analyze --force
```

**Options:**

- `--pattern TEXT`: Table name pattern (default: WMS_%)
- `--compute TEXT`: Type of analysis (default: STATISTICS)
- `--dry-run`: Show what would be analyzed without executing
- `--force`: Skip confirmation prompt

**Use case:** When table row counts show as "N/A" or outdated statistics

### 🔍 `validate` - Data Integrity Validation

Comprehensive data integrity and consistency validation:

```bash
# Basic validation (NULL checks)
poetry run gn-wms-cli validate

# Include referential integrity checks
poetry run gn-wms-cli validate --check-references

# Include duplicate record checks
poetry run gn-wms-cli validate --check-duplicates

# Complete validation with all checks
poetry run gn-wms-cli validate --check-references --check-duplicates

# Attempt to fix found issues (future feature)
poetry run gn-wms-cli validate --fix-issues
```

**Validation types:**

- **NULL Values**: Critical fields that should not be NULL
- **Referential Integrity**: Order details without matching headers
- **Duplicates**: Duplicate records in primary key fields
- **Constraints**: Database constraint violations

### 💾 `backup` - Data Backup and Export

Create backup files for WMS tables in multiple formats:

```bash
# Basic backup (SQL format)
poetry run gn-wms-cli backup

# Backup to specific directory
poetry run gn-wms-cli backup --output-dir ./my-backups

# Export as CSV files
poetry run gn-wms-cli backup --format csv

# Export as JSON files
poetry run gn-wms-cli backup --format json

# Schema only (no data)
poetry run gn-wms-cli backup --schema-only

# Data only (no schema)
poetry run gn-wms-cli backup --data-only

# Backup specific tables
poetry run gn-wms-cli backup --pattern="WMS_ORDER%"
```

**Options:**

- `--pattern TEXT`: Table name pattern to backup (default: WMS_%)
- `--output-dir PATH`: Output directory (default: ./backup)
- `--format [sql|csv|json]`: Backup format (default: sql)
- `--compress`: Compress backup files (future feature)
- `--data-only`: Export data only, no schema
- `--schema-only`: Export schema only, no data

**Features:**

- Timestamped backup directories
- Backup manifest with metadata
- Multiple output formats
- Progress tracking
- Error handling and recovery

## Environment Configuration

Ensure your `.env` file contains:

```env
# Oracle Database Configuration (Required)
DB_HOST=your-oracle-host
DB_PORT=1522
DB_SERVICE_NAME=your-service-name
DB_USERNAME=your-username
DB_PASSWORD=your-password

# Database Advanced Settings (Optional)
DB_PROTOCOL=tcps
DB_AUTH_TYPE=basic
DB_SCHEMA=admin
DB_POOL_SIZE=5
DB_MAX_POOL_SIZE=10
DB_TIMEOUT=30
DB_SSL_SERVER_CERT_DN=true

# WMS Integration (Optional)
WMS_URL=https://your-wms-instance.com
WMS_USERNAME=wms-user
WMS_PASSWORD=wms-password
WMS_TIMEOUT=600
WMS_VERIFY_SSL=true
WMS_MAX_RETRIES=1
WMS_RETRY_DELAY=2

# Oracle Integration Cloud (Optional)
IDCS_URL=idcs-instance.identity.oraclecloud.com
IDCS_CLIENT_ID=your-client-id
IDCS_CLIENT_SECRET=your-client-secret
IDCS_CLIENT_AUD=your-audience
OIC_INSTANCE_ID=your-instance-id
OIC_REGION=us-ashburn-1
OIC_ENVIRONMENT=test
OIC_TIMEOUT=60
OIC_MAX_RETRIES=3

# Logging Configuration
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Configuration Validation

The CLI automatically validates your configuration and shows:

- **Required Parameters**: Must be set for basic functionality
- **Optional Parameters**: Enhance functionality when available
- **Invalid Values**: Parameters with incorrect format or values
- **Missing Secrets**: Sensitive parameters that need configuration

Use `poetry run gn-wms-cli config` to validate your setup.

### Log Level Configuration

The CLI respects the `LOG_LEVEL` environment variable with the following behavior:

- **DEBUG**: Shows all log messages including detailed debug information
- **INFO** (default): Shows informational messages about operations
- **WARNING**: Shows only warnings and errors
- **ERROR**: Shows only error messages
- **CRITICAL**: Shows only critical error messages

CLI options override environment settings:

- `--verbose`: Forces DEBUG level (with JSON format for detailed analysis)
- `--quiet`: Forces WARNING level (minimal output)
- No option: Uses `LOG_LEVEL` from `.env` (defaults to INFO)

### Log Formats

- **Normal Mode**: Human-readable format with colors and timestamps
- **Verbose Mode**: JSON format with detailed metadata for debugging and automation

## Global Options

All commands support these global options:

- `--verbose, -v`: Enable detailed debug logging
- `--quiet, -q`: Suppress non-essential output
- `--version`: Show CLI version
- `--help`: Show command help

## Error Handling

The CLI provides comprehensive error handling:

- **Configuration Errors**: Clear messages about missing or invalid parameters
- **Connection Errors**: Detailed database connection diagnostics
- **Validation Errors**: Specific field-level validation messages
- **Operation Errors**: Contextual information about failed operations

## Security Notes

- Passwords and secrets are masked in output by default
- Use `--show-secrets` flag carefully and only when necessary
- Environment files (`.env`) should never be committed to version control
- Use appropriate file permissions for `.env` files (`chmod 600 .env`)

## Examples

```bash
# Complete workflow example
poetry run gn-wms-cli config               # Validate configuration
poetry run gn-wms-cli status               # Check system status
poetry run gn-wms-cli setup --dry-run      # Preview setup
poetry run gn-wms-cli setup               # Perform setup
poetry run gn-wms-cli check               # Verify tables
poetry run gn-wms-cli test                # Test connectivity

# Troubleshooting example
poetry run gn-wms-cli --verbose status     # Detailed diagnostics
poetry run gn-wms-cli config --show-secrets # Check all parameters
poetry run gn-wms-cli test --verbose       # Debug connections
```
