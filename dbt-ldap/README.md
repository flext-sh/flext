# dbt-ldap

dbt project for transforming LDAP data extracted by tap-ldap.

## Installation

```bash
cd dbt-ldap
pip install dbt-core dbt-duckdb  # For development
# OR
pip install dbt-core dbt-postgres  # For production
```

## Configuration

### Development (DuckDB)

The default profile uses DuckDB for local development:

```yaml
dbt_ldap:
  outputs:
    dev:
      type: duckdb
      path: ./target/ldap_transform.db
      threads: 4
  target: dev
```

### Production (PostgreSQL)

For production, set environment variables:

```bash
export DBT_POSTGRES_HOST=your-postgres-host
export DBT_POSTGRES_PORT=5432
export DBT_POSTGRES_USER=your-user
export DBT_POSTGRES_PASS=your-password
export DBT_POSTGRES_DB=ldap_warehouse
```

## Project Structure

```
dbt-ldap/
├── models/
│   ├── staging/         # Raw data transformation
│   │   ├── stg_users.sql
│   │   ├── stg_groups.sql
│   │   └── stg_org_units.sql
│   ├── intermediate/    # Business logic
│   │   ├── int_user_groups.sql
│   │   └── int_org_hierarchy.sql
│   └── marts/          # Final analytics tables
│       ├── dim_users.sql
│       ├── dim_groups.sql
│       └── fact_memberships.sql
├── snapshots/          # Historical tracking
│   └── ldap_entries_snapshot.sql
└── macros/            # Reusable SQL functions
    ├── ldap_macros.sql
    └── schema_mapping.sql
```

## Usage

### Run all models

```bash
dbt run
```

### Run specific models

```bash
# Run only staging models
dbt run --select staging.*

# Run a specific model and its dependencies
dbt run --select +dim_users
```

### Test data quality

```bash
dbt test
```

### Generate documentation

```bash
dbt docs generate
dbt docs serve
```

### Create snapshots

```bash
dbt snapshot
```

## Available Models

### Staging Layer

- **stg_users**: Cleans and standardizes user data
- **stg_groups**: Cleans and standardizes group data
- **stg_org_units**: Cleans and standardizes organizational unit data

### Intermediate Layer

- **int_user_groups**: User-group membership relationships
- **int_org_hierarchy**: Organizational unit hierarchy with parent-child relationships

### Marts Layer

- **dim_users**: User dimension with enriched attributes
- **dim_groups**: Group dimension with membership counts
- **fact_memberships**: Fact table for user-group relationships

## Macros

### LDAP-specific functions

- `parse_dn()`: Extract components from Distinguished Names
- `extract_ou_from_dn()`: Get organizational unit from DN
- `normalize_array_field()`: Handle multi-valued LDAP attributes
- `ldap_timestamp_to_timestamp()`: Convert LDAP timestamps
- `count_group_members()`: Calculate group membership counts

### Schema mapping functions

- `map_ldap_user_attributes()`: Standard user attribute mapping
- `map_ldap_group_attributes()`: Standard group attribute mapping
- `map_ldap_ou_attributes()`: Standard OU attribute mapping

## Integration with tap-ldap

1. Extract data using tap-ldap:

```bash
tap-ldap --config tap-config.json | target-jsonl > ldap_data.jsonl
```

2. Load data into your warehouse

3. Run dbt transformations:

```bash
dbt run
```

## Variables

Configure project variables in `dbt_project.yml`:

```yaml
vars:
  ldap_base_dn: "dc=example,dc=com"
  ldap_user_base: "ou=users"
  ldap_group_base: "ou=groups"
  ldap_ou_base: "ou=departments"
```

## Performance Optimization

- Staging models use views for real-time data
- Intermediate models use views for flexibility
- Mart models use tables for query performance
- Indexes are defined on key columns
- Incremental models can be added for large datasets
