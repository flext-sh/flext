# flx-ldap

Unified CLI for LDAP ETL operations, orchestrating tap-ldap, target-ldap, and dbt-ldap.

## Installation

```bash
cd flx-ldap

# Install with all components
poetry install --extras all

# Or install with specific components
poetry install --extras tap      # Only tap-ldap
poetry install --extras target    # Only target-ldap
poetry install --extras dbt       # Only dbt
```

## Configuration

### Configuration File (YAML)

Create `config.yml`:

```yaml
tap:
  host: source.ldap.com
  port: 389
  bind_dn: cn=admin,dc=source,dc=com
  password: source_password
  base_dn: dc=source,dc=com
  user_filter: "(objectClass=inetOrgPerson)"
  group_filter: "(objectClass=groupOfNames)"

target:
  host: target.ldap.com
  port: 389
  bind_dn: cn=admin,dc=target,dc=com
  password: target_password
  base_dn: dc=target,dc=com

dbt:
  project_dir: ../dbt-ldap
  target: dev
  threads: 4
  vars:
    ldap_base_dn: dc=example,dc=com

catalog_path: ./catalog.json
state_path: ./state.json
output_path: ./output
log_level: INFO
```

### Environment Variables

```bash
# Tap configuration
export LDAP_TAP_HOST=source.ldap.com
export LDAP_TAP_BIND_DN=cn=admin,dc=source,dc=com
export LDAP_TAP_PASSWORD=source_password
export LDAP_TAP_BASE_DN=dc=source,dc=com

# Target configuration
export LDAP_TARGET_HOST=target.ldap.com
export LDAP_TARGET_BIND_DN=cn=admin,dc=target,dc=com
export LDAP_TARGET_PASSWORD=target_password
export LDAP_TARGET_BASE_DN=dc=target,dc=com

# DBT configuration
export DBT_PROJECT_DIR=../dbt-ldap
export DBT_TARGET=dev

# General configuration
export FLX_LDAP_OUTPUT_PATH=./output
export FLX_LDAP_LOG_LEVEL=INFO
```

## Usage

### Basic Commands

```bash
# Validate configuration
flx-ldap validate

# Show current configuration
flx-ldap show-config

# Extract data from LDAP
flx-ldap extract --catalog catalog.json --state state.json

# Transform data with dbt
flx-ldap transform run
flx-ldap transform test
flx-ldap transform snapshot

# Load data to LDAP
flx-ldap load --input output/tap-output.jsonl

# Run complete sync pipeline
flx-ldap sync
```

### Advanced Usage

#### Custom Configuration

```bash
# Use specific config file
flx-ldap --config production.yml sync

# Override log level
flx-ldap --log-level DEBUG extract
```

#### Selective Operations

```bash
# Extract with specific output
flx-ldap extract --output custom-output.jsonl

# Transform specific models
flx-ldap transform run --models dim_users,dim_groups

# Full refresh transformation
flx-ldap transform run --full-refresh

# Dry run load
flx-ldap load --dry-run
```

#### Complete Pipeline

```bash
# Full sync with all options
flx-ldap sync \
  --catalog catalog.json \
  --state state.json \
  --dry-run

# Sync without transformation
flx-ldap sync --no-transform
```

### Migration Commands

#### Generate Migration Plan

```bash
flx-ldap migrate plan \
  --source-host old.ldap.com \
  --target-host new.ldap.com \
  --base-dn dc=example,dc=com \
  --output migration-plan.json
```

#### Run Migration

```bash
# With comparison
flx-ldap migrate run \
  --source-catalog source-catalog.json \
  --target-catalog target-catalog.json

# Without comparison
flx-ldap migrate run --no-compare
```

## Integration with algar-oud-mig

The CLI integrates with algar-oud-mig for complex migration scenarios:

1. **Schema Migration**: Extracts and applies custom schema elements
2. **Data Transformation**: Uses algar-oud-mig's transformation logic
3. **Validation**: Leverages existing validation routines

### Migration Configuration

```yaml
migration:
  source_tap_config:
    host: oid.example.com
    port: 389
    base_dn: dc=example,dc=com
  target_config:
    host: oud.example.com
    port: 389
    base_dn: dc=example,dc=com
  comparison_enabled: true
  dry_run: false
  batch_size: 1000
```

## Pipeline Architecture

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│   tap-ldap  │────▶│  dbt-ldap   │────▶│ target-ldap  │
│  (Extract)  │     │ (Transform) │     │   (Load)     │
└─────────────┘     └─────────────┘     └──────────────┘
       │                    │                     │
       └────────────────────┴─────────────────────┘
                            │
                      ┌─────▼──────┐
                      │  flx-ldap  │
                      │(Orchestrate)│
                      └────────────┘
```

## Output Files

The CLI generates several output files:

- `tap-output.jsonl`: Raw extracted data in Singer format
- `flx-ldap.log`: Detailed execution log
- `state.json`: Incremental sync state (if using state)
- `catalog.json`: Discovered catalog (if running discovery)

## Error Handling

The CLI provides comprehensive error handling:

- Configuration validation before execution
- Component availability checks
- Detailed error messages and logs
- Rollback support for migrations

## Performance Considerations

- Use pagination (`page_size`) for large directories
- Enable incremental sync with state management
- Adjust batch size for migrations
- Use multiple threads for dbt transformations

## Troubleshooting

### Common Issues

1. **Component not found**
   ```bash
   # Install missing component
   poetry install --extras tap
   ```

2. **Configuration errors**
   ```bash
   # Validate configuration
   flx-ldap validate
   ```

3. **Connection failures**
   ```bash
   # Test with minimal config
   flx-ldap extract --catalog catalog.json
   ```

### Debug Mode

```bash
# Enable debug logging
flx-ldap --log-level DEBUG sync

# Check generated files
ls -la output/
cat output/flx-ldap.log
```
