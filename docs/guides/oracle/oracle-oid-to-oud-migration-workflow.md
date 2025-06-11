# Oracle Directory Migration Workflow

**Date**: January 2025  
**Status**: Complete Migration Guide  
**Version**: Production Ready

## Overview

This document describes the complete workflow for migration between Oracle Internet Directory (OID) and Oracle Unified Directory (OUD) using the automated tools available in this project.

The migration process between OID and OUD is complex and involves several steps, including schema migration, configurations, ACIs, and data. This project provides tools and scripts to automate this process, enabling faster and more reliable migration.

## Prerequisites

- Python 3.10 or higher
- Access to OID and OUD servers
- Administrator credentials for both directories
- Export LDIF (optional, if you already have exported data)

## Workflow Structure

The migration workflow consists of the following main steps:

1. **Initialization** - Preparation of directories and configuration files
2. **Schema Migration** - Difference detection and schema extension generation
3. **LDIF Processing** - LDIF data conversion for OUD compatibility
4. **Data Import** - Loading converted data into OUD

## Migration Commands

### Complete Migration

To run the full migration workflow, use the command:

```bash
make migration-full LDIF=ldifs/your_file.ldif
```

If you don't have an LDIF file and want to migrate directly from OID server to OUD:

```bash
make migration-full
```

### Step-by-Step Migration

If you prefer to run migration in separate steps:

1. **Validation** - Checks configuration without applying changes:

   ```bash
   make migration-validate LDIF=ldifs/your_file.ldif
   ```

2. **Schema Migration** - Migrates schema only:

   ```bash
   make migration-schema
   ```

3. **Data Migration** - Migrates data only (assumes schema has been migrated):

   ```bash
   make migration-data LDIF=ldifs/your_file.ldif
   ```

4. **Status Check** - Checks migration status:

   ```bash
   make migration-status
   ```

## Export Commands

To extract data from directories to LDIF:

```bash
# Export OUD data
make export-oud

# Export OID data
make export-oid
```

## Output Directory Structure

Migration artifacts are stored in the `output/` directory with the following structure:

```
output/
  ├── schema/             # Schema extensions and mapping files
  │    ├── oid_schema_extensions.ldif
  │    └── missing_parents.ldif
  ├── ldif/               # Processed LDIF files
  │    └── fixed_*.ldif
  └── logs/               # Migration logs
       └── migration.log
```

## Configuration

Migration depends on a configuration file that defines how OID-specific schema elements should be handled. The default file is `config/schema_config.json`. You can create this file with:

```bash
make init
```

### Connection Configuration

LDAP connection settings can be defined in two ways:

1. **.env file** (recommended):

   ```bash
   LDAP_HOST=your_server
   LDAP_PORT=3060
   LDAP_BIND_DN="cn=orcladmin"
   LDAP_PASSWORD="your_password"
   LDAP_BASE_DN="dc=example,dc=com"
   ```

2. **Command line options**:
   You can pass credentials directly to CLI commands if you prefer not to use the .env file.

## Schema Operations

For specific schema operations:

```bash
# Detect schema differences
make schema-detect

# Generate schema extensions
make schema-generate

# Apply schema extensions
make schema-apply
```

## LDIF Operations

For specific LDIF operations:

```bash
# Validate LDIF format
make ldif-validate LDIF=ldifs/your_file.ldif

# Generate LDIF statistics
make ldif-stats LDIF=ldifs/your_file.ldif

# Generate detailed report
make ldif-report LDIF=ldifs/your_file.ldif

# Fix LDIF for OUD compatibility
make ldif-fix-for-oud LDIF=ldifs/your_file.ldif
```

## Troubleshooting

If you encounter problems during migration:

1. **Check logs** - Consult logs in `output/logs/migration.log`
2. **Check status** - Use `make migration-status` to see current state
3. **Restart in steps** - Run individual steps instead of complete migration
4. **Verbose mode** - Run CLI commands directly with `--verbose` option

## Migration Validation

Before and after migration, validate your setup:

```bash
# Pre-migration validation
make migration-validate

# Post-migration verification
make migration-verify

# Data integrity check
make data-integrity-check
```

## Performance Considerations

For large migrations:

- Use `--batch-size` parameter for large LDIF files
- Monitor server resources during migration
- Consider migration during off-peak hours
- Use parallel processing for multiple base DNs

## Security Considerations

- Always use encrypted connections (LDAPS)
- Validate all credentials before migration
- Backup all data before starting migration
- Test migration in development environment first

## Integration with FLX Framework

This migration workflow integrates with the FLX framework:

```python
from flx.adapters.oracle.oud import OUDMigrationAdapter

# Initialize migration adapter
adapter = OUDMigrationAdapter(config)

# Run automated migration
result = await adapter.migrate_from_oid(
    source_ldif="data.ldif",
    target_env="production"
)
```

## Related Documentation

- [Oracle OUD Automation Guide](oracle-oud-automation-guide.md)
- [Oracle OID to OUD Migration](oracle-oid-to-oud-migration.md)
- [Oracle Security Guide](oracle-security-guide.md)
- [Oracle SSO Authentication Setup](oracle-sso-authentication-setup.md)

## Advanced Features

### Custom Schema Mapping

Create custom schema mappings for specific organizational units:

```json
{
  "custom_mappings": {
    "organizationalUnit": {
      "oid_attribute": "ou",
      "oud_attribute": "ou",
      "transformation": "lowercase"
    }
  }
}
```

### Automated Rollback

If migration fails, automated rollback is available:

```bash
make migration-rollback
```

## Migration Checklist

- [ ] Backup source directory
- [ ] Verify connectivity to both directories
- [ ] Test migration in development
- [ ] Schedule maintenance window
- [ ] Run pre-migration validation
- [ ] Execute migration
- [ ] Verify data integrity
- [ ] Update application configurations
- [ ] Test applications
- [ ] Document migration results

This workflow provides a comprehensive approach to Oracle directory migration with enterprise-grade reliability and automation.
