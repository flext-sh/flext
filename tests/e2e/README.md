# End-to-End Testing Infrastructure for LDAP Components

This directory contains comprehensive end-to-end tests for the LDAP ecosystem components:

- `tap-ldap`: Singer tap for extracting data from LDAP
- `target-ldap`: Singer target for loading data to LDAP
- `dbt-ldap`: DBT package for transforming LDAP data
- `flx-ldap`: Orchestrator for complete LDAP ETL pipelines

## Architecture

The E2E test infrastructure uses Docker containers to provide:

- **Source LDAP**: OpenLDAP server with test data (port 10389)
- **Target LDAP**: Clean OpenLDAP server for migration testing (port 11389)
- **PostgreSQL**: Database for dbt transformations (port 15432)
- **phpLDAPREDACTED_LDAP_BIND_PASSWORD**: Web UI for debugging (port 18080)

## Prerequisites

1. Docker and docker-compose installed
2. Python 3.11+ with required packages:

   ```bash
   pip install pytest docker psycopg2-binary ldap3 faker
   ```

## Quick Start

Run all E2E tests:

```bash
./run_e2e_tests.py
```

Run specific test scenarios:

```bash
./run_e2e_tests.py scenarios/test_full_pipeline.py
```

Keep containers running after tests (for debugging):

```bash
./run_e2e_tests.py --keep-containers
```

## Test Scenarios

### Full Pipeline Tests (`test_full_pipeline.py`)

- **tap_ldap_extraction**: Validates complete data extraction from source LDAP
- **target_ldap_loading**: Tests loading data to target LDAP server
- **dbt_ldap_transformations**: Verifies dbt transformations with PostgreSQL
- **flx_ldap_orchestration**: Tests complete pipeline orchestration
- **incremental_sync**: Validates incremental synchronization capabilities
- **error_handling_and_recovery**: Tests error handling and recovery mechanisms
- **performance_with_large_dataset**: Performance testing with 100+ entries

### Migration Scenarios (`test_migration_scenarios.py`)

- **basic_user_migration**: Simple user migration from source to target
- **group_migration_with_members**: Group migration with member reference updates
- **organizational_structure_migration**: Complete OU structure migration
- **filtered_migration**: Migration with filters (e.g., active users only)
- **attribute_transformation_migration**: Migration with attribute transformations
- **conflict_resolution_migration**: Handling conflicts during migration

### Edge Cases (`test_edge_cases.py`)

- **empty_ldap_source**: Handling empty LDAP directories
- **special_characters_in_dn**: Special characters (UTF-8, quotes, commas)
- **large_attribute_values**: Large text attributes (10KB+)
- **circular_group_membership**: Circular group references
- **binary_attribute_handling**: Binary data (photos, certificates)
- **pagination_edge_cases**: Exact page boundary testing
- **connection_failure_recovery**: Network failure handling
- **schema_validation_edge_cases**: Non-standard object classes
- **multi_valued_attribute_operations**: Multi-valued attribute handling

## Directory Structure

```
tests/e2e/
├── docker-compose.yml       # Container orchestration
├── conftest.py             # Pytest fixtures and configuration
├── run_e2e_tests.py        # Test runner script
├── README.md               # This file
├── configs/                # Test configurations
├── data/                   # Test data and LDIF files
│   ├── source/ldif/        # Source LDAP initialization
│   ├── target/ldif/        # Target LDAP initialization
│   └── postgres/           # PostgreSQL initialization
├── fixtures/               # Additional test fixtures
├── helpers/                # Test utilities
│   ├── ldap_helpers.py     # LDAP operation helpers
│   ├── data_generator.py   # Test data generation
│   └── container_helpers.py # Docker container management
└── scenarios/              # Test scenarios
    ├── test_full_pipeline.py
    ├── test_migration_scenarios.py
    └── test_edge_cases.py
```

## Test Data

### Source LDAP Structure

- Base DN: `dc=source,dc=example,dc=com`
- Admin DN: `cn=REDACTED_LDAP_BIND_PASSWORD,dc=source,dc=example,dc=com`
- Password: `REDACTED_LDAP_BIND_PASSWORD_source_password`

Pre-populated with:

- Organizational Units: People, Groups, Applications, Departments
- Users: Engineering and Sales employees with full attributes
- Groups: Department groups, role-based groups
- Special test entries for edge case testing

### Target LDAP Structure

- Base DN: `dc=target,dc=example,dc=com`
- Admin DN: `cn=REDACTED_LDAP_BIND_PASSWORD,dc=target,dc=example,dc=com`
- Password: `REDACTED_LDAP_BIND_PASSWORD_target_password`

Initially empty except for base OUs.

### PostgreSQL Database

- Database: `dbt_ldap_test`
- User: `dbt_user`
- Password: `dbt_password`
- Schemas: `ldap_raw`, `ldap_staging`, `ldap_analytics`

## Running Tests

### Basic Usage

```bash
# Run all tests
./run_e2e_tests.py

# Run with coverage
./run_e2e_tests.py --coverage

# Run specific test class
./run_e2e_tests.py scenarios/test_full_pipeline.py::TestFullPipeline

# Run specific test method
./run_e2e_tests.py scenarios/test_full_pipeline.py::TestFullPipeline::test_tap_ldap_extraction

# Run tests matching a pattern
./run_e2e_tests.py -k "migration"

# Run with custom pytest args
./run_e2e_tests.py --pytest-args="-x --pdb"
```

### Debugging

Access phpLDAPREDACTED_LDAP_BIND_PASSWORD: <http://localhost:18080>

View container logs:

```bash
./run_e2e_tests.py --logs              # All logs
./run_e2e_tests.py --logs ldap-source  # Specific service
```

Keep containers running:

```bash
./run_e2e_tests.py --keep-containers
```

Manual container management:

```bash
cd tests/e2e
docker-compose up -d     # Start containers
docker-compose logs -f   # View logs
docker-compose down -v   # Stop and clean up
```

### Advanced Options

Skip setup checks:

```bash
./run_e2e_tests.py --skip-setup
```

Skip container rebuild:

```bash
./run_e2e_tests.py --skip-build
```

Run tests with markers:

```bash
# Add @pytest.mark.slow to slow tests
./run_e2e_tests.py -m "not slow"
```

## Writing New Tests

### Using Test Helpers

```python
from ..helpers.ldap_helpers import LDAPTestHelper
from ..helpers.data_generator import LDAPDataGenerator

def test_example(ldap_source_connection):
    helper = LDAPTestHelper(ldap_source_connection)
    generator = LDAPDataGenerator(seed=42)

    # Create test data
    user_data = generator.generate_user(department="ENG")
    helper.create_test_user(
        uid=user_data["uid"],
        base_dn="dc=source,dc=example,dc=com",
        **user_data
    )

    # Verify data
    entry = helper.get_entry_as_dict(
        f"uid={user_data['uid']},ou=People,dc=source,dc=example,dc=com"
    )
    assert entry is not None
```

### Using Fixtures

```python
def test_with_clean_target(clean_target_ldap, ldap_target_connection):
    """Target LDAP is automatically cleaned before test."""
    # Test code here
    pass

def test_with_config(tap_ldap_config, target_ldap_config):
    """Pre-configured tap and target configurations."""
    # Modify configs as needed
    tap_ldap_config["page_size"] = 50
```

### Container Management

```python
from ..helpers.container_helpers import ContainerManager

def test_container_operations(docker_compose_up):
    manager = ContainerManager(E2E_DIR / "docker-compose.yml")

    # Restart a service
    manager.restart_service("ldap-source")

    # Get service logs
    logs = manager.get_service_logs("ldap-source", lines=50)

    # Execute command in container
    result = manager.exec_in_service(
        "postgres",
        ["psql", "-U", "dbt_user", "-c", "SELECT COUNT(*) FROM ldap_raw.users;"]
    )
```

## Troubleshooting

### Container Issues

If containers fail to start:

```bash
# Check for port conflicts
lsof -i :10389 -i :11389 -i :15432 -i :18080

# Clean up everything
docker-compose down -v
docker system prune -f
```

### Test Failures

Enable detailed output:

```bash
./run_e2e_tests.py --pytest-args="-vv -s"
```

Debug with pdb:

```bash
./run_e2e_tests.py --pytest-args="--pdb"
```

### Performance

For faster test runs:

```bash
# Skip slow tests
./run_e2e_tests.py -m "not slow"

# Run in parallel (if tests are independent)
./run_e2e_tests.py --pytest-args="-n 4"
```

## CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: E2E Tests
on: [push, pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install pytest docker psycopg2-binary ldap3 faker
          pip install -e ./tap-ldap
          pip install -e ./target-ldap
          pip install -e ./flx-ldap

      - name: Run E2E tests
        run: ./tests/e2e/run_e2e_tests.py --coverage
```

## Contributing

When adding new E2E tests:

1. Choose the appropriate scenario file or create a new one
2. Use existing helpers and fixtures where possible
3. Clean up test data in teardown
4. Document any new test data or configurations
5. Ensure tests are idempotent and can run repeatedly

## License

This test infrastructure is part of the PyAuto project and follows the same license terms.
