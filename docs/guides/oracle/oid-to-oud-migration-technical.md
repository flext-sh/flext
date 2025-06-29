# OID to OUD Migration Guide

This document provides instructions for migrating LDAP data from Oracle Internet Directory (OID) to Oracle Unified Directory (OUD).

## Overview

The migration process involves several steps to handle schema differences between OID and OUD:

1. Extend OUD schema with OID-specific object classes and attributes
2. Create missing parent entries required by OID hierarchy
3. Transform and fix LDIF files to be compatible with OUD
4. Import the fixed LDIF data into OUD

## Prerequisites

- OUD server installed and running
- LDIF files exported from OID
- Python 3.6+ with necessary dependencies
- Access to both OID and OUD environments

## Schema Differences

OID and OUD have several schema differences that need to be addressed:

1. **Missing object classes**: OID uses some object classes not defined in OUD (e.g., `orclcontainerOC`)
2. **Hierarchy differences**: OID has configuration entries under `cn=subconfigsubentry` that don't exist in OUD
3. **Missing intermediate entries**: Some entries in OID reference parent entries that don't exist in OUD
4. **Attribute differences**: Some attributes used in OID are not defined in OUD

## Migration Tools

The following tools are provided to assist with migration:

- `schema_migration_helper.py`: Analyzes OID schema and generates extensions for OUD
- `flext_ldif_for_oud.py`: Processes LDIF files to make them compatible with OUD
- `ldif_tools.py`: Provides utilities for LDIF analysis and reporting

## Migration Process

### 1. Analyze LDIF Files

```bash
# Generate statistics about LDIF files
make ldif-stats LDIF_FILE=path/to/oid_export.ldif

# Generate comprehensive report
make ldif-report
```

### 2. Extend OUD Schema

```bash
# Apply schema extensions to OUD
make ldif-apply-schema-extensions
```

This uses the `oid_schema_extensions.ldif` file to add missing object classes to the OUD schema.

### 3. Migrate and Fix LDIF Data (with automatic parent creation)

```bash
# Fix LDIF data and import to OUD in one step (with automatic parent creation)
make ldif-migrate-oid-to-oud INPUT_LDIF=path/to/oid_export.ldif OUTPUT_LDIF=path/to/fixed_export.ldif
```

The migration process now:

1. Extends the OUD schema
2. During LDIF processing, automatically creates missing parent entries
3. Fixes and transforms LDIF entries for OUD compatibility

### Advanced Options

For specific cases, you can run the script directly with advanced parameters:

```bash
# Run flext_ldif_for_oud.py script with custom parameters
python scripts/flext_ldif_for_oud.py --input input.ldif --output output.ldif \
    --ldap-host localhost --ldap-port 3389 --ldap-bind-dn "cn=Directory Manager" --ldap-password "password"
```

## Troubleshooting

### Common Issues

1. **Object class violations**:

   - Symptom: Error messages like "unknown objectclass orclcontainerOC"
   - Solution: Ensure schema extensions are applied first using `ldif-apply-schema-extensions`

2. **Missing parent entries**:

   - Symptom: Error messages like "parent entry does not exist"
   - Solution: The script now automatically creates parent entries during LDIF processing

3. **Special characters in DNs**:
   - Symptom: Error parsing LDIF entries
   - Solution: The `flext_ldif_for_oud.py` script handles special character escaping

### Logs

All migration tools produce detailed logs to help troubleshoot issues:

- Schema extension logs are in the standard OUD logs
- LDIF processing logs are displayed on console and can be redirected to a file
- The `ldif-report` command generates a detailed LDIF processing report

## Example Workflow

```bash
# Step 1: Analyze LDIF data
make ldif-stats LDIF_FILE=ldifs/oid_export.ldif
make ldif-report

# Step 2: Apply schema extensions
make ldif-apply-schema-extensions

# Step 3: Fix and import LDIF data (with automatic parent creation)
make ldif-migrate-oid-to-oud INPUT_LDIF=ldifs/oid_export.ldif OUTPUT_LDIF=ldifs/oud_import.ldif
```

## Advanced Configuration

For advanced configurations, you can modify the following files:

- `ldifs/oid_schema_extensions.ldif`: Add additional object class or attribute definitions
- `scripts/flext_ldif_for_oud.py`: Customize transformation rules for specific OID attributes or object classes

## Security Considerations

- Ensure LDIF files are handled securely and contain no sensitive data in plain text
- Use secure connections when connecting to LDAP servers
- Validate schema extensions before applying to production environments
- Test migration process in development environment first

## Performance Optimization

- Process large LDIF files in batches
- Monitor OUD server resources during import
- Consider disabling indexes temporarily during large imports
- Use appropriate batch sizes for optimal performance
