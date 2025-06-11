# OUD Automation - Simplified CLI

A simplified CLI for Oracle Unified Directory automation with standardized table output and automatic configuration loading from `.env` file.

## Features

- ✅ **Standardized table output** (default format)
- ✅ **Automatic .env loading**
- ✅ **Standardized logging with logger.info**
- ✅ **Support for multiple output formats** (table, json, csv, yaml)
- ✅ **Simplified design** without FLX CLI dependencies

## Installation

```bash
# Clone the repository
cd oud-automation

# Copy the example configuration file
cp .env.example .env

# Edit .env with your settings
vim .env

# Make the CLI executable
chmod +x oud-cli
```

## Usage

### Basic Commands

```bash
# Process LDIF file
./oud-cli ldif-process input.ldif
./oud-cli ldif-process input.ldif --output-file processed.ldif

# Migrate schema
./oud-cli schema-migrate --from-oid
./oud-cli schema-migrate --schema-file custom.schema --dry-run

# LDAP search
./oud-cli ldap-search --filter "(uid=john*)" --limit 20
./oud-cli ldap-search --base-dn "ou=people,dc=example,dc=com"

# List configured LDAP servers
./oud-cli ldap-servers

# Test connection
./oud-cli test-connection

# Check system health
./oud-cli health

# Show version
./oud-cli version
```

### Output Format Options

```bash
# Table format (default)
./oud-cli ldap-search

# JSON format
./oud-cli --json ldap-search
./oud-cli --format json ldap-search

# CSV format
./oud-cli --csv ldap-search
./oud-cli --format csv ldap-search

# YAML format
./oud-cli --yaml ldap-search
./oud-cli --format yaml ldap-search
```

### Debug and Logging

```bash
# Enable debug
./oud-cli --debug ldap-search

# Logs are automatically written as configured in .env
# LOG_FILE=./logs/oud_automation.log
```

## Configuration via .env

The CLI automatically loads configuration from the `.env` file. Example:

```env
# Main LDAP configuration
LDAP_HOST=ldap.example.com
LDAP_PORT=389
LDAP_BIND_DN=cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com
LDAP_BIND_PASSWORD=secretpassword
LDAP_BASE_DN=dc=example,dc=com
LDAP_USE_SSL=false
LDAP_TIMEOUT=30.0

# Additional servers (optional)
LDAP_HOST_1=ldap-backup.example.com
LDAP_PORT_1=389

# OUD configuration
OUD_INSTANCE_DIR=/opt/oracle/oud/instances/oud1
OUD_ADMIN_PORT=4444
OUD_BACKEND_ID=userRoot

# Processing configuration
BATCH_SIZE=1000
MAX_WORKERS=4
LOG_LEVEL=INFO
```

## Output Examples

### Table Output (default)

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃          LDAP Search Results (limit: 10)         ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ DN                                   │ Uid       │
├──────────────────────────────────────┼───────────┤
│ uid=user1,ou=people,dc=example,dc=com│ user1     │
│ uid=user2,ou=people,dc=example,dc=com│ user2     │
└──────────────────────────────────────┴───────────┘
```

### JSON Output

```json
[
  {
    "dn": "uid=user1,ou=people,dc=example,dc=com",
    "uid": "user1",
    "cn": "User 1",
    "mail": "user1@example.com"
  }
]
```

### CSV Output

```csv
DN,Uid,Cn,Mail
uid=user1,ou=people,dc=example,dc=com,user1,User 1,user1@example.com
uid=user2,ou=people,dc=example,dc=com,user2,User 2,user2@example.com
```

## Project Structure

```
oud-automation/
├── oud-cli                          # Main CLI script
├── .env.example                     # Configuration example
├── src/oud_automation/
│   ├── cli/
│   │   └── simple_cli.py           # Simplified CLI implementation
│   ├── config.py                   # Configuration management
│   ├── ldap_connection.py          # LDAP connection
│   ├── ldif_processor_simple.py    # LDIF processor
│   └── schema_manager.py           # Schema manager
└── logs/                           # Logs directory
```

## Logging

The system uses `logger.info` for accessory data and debug information:

```python
logger.info(f"Processing LDIF file: {input_file}")
logger.info(f"Found {len(results)} entries")
logger.info("Configuration loaded from environment")
```

## Development

To add new commands:

1. Add the method to the `OudCliApplication` class
2. Register the command with the `@cli.command()` decorator
3. Use `self.output.print_data()` for standardized output
4. Use `logger.info()` for debug information

Example:

```python
@cli.command()
@click.pass_obj
def my_command(app):
    """Command description."""
    # Command logic
    results = {"key": "value"}
    app.output.print_data([results], "Table Title")
    logger.info("Command executed successfully")
```
