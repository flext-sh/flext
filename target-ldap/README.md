# target-ldap

Singer target for LDAP data loading, built with the [Singer SDK](https://sdk.meltano.com).

## Installation

```bash
cd target-ldap
poetry install
```

## Configuration

Create a `config.json` file:

```json
{
  "host": "ldap.example.com",
  "port": 389,
  "bind_dn": "cn=admin,dc=example,dc=com",
  "password": "admin_password",
  "base_dn": "dc=example,dc=com",
  "use_ssl": false,
  "timeout": 30,
  "validate_records": true,
  "user_rdn_attribute": "uid",
  "group_rdn_attribute": "cn"
}
```

### Advanced Configuration

#### DN Templates

You can configure DN templates for each stream:

```json
{
  "dn_templates": {
    "users": "uid={uid},ou=users,dc=example,dc=com",
    "groups": "cn={cn},ou=groups,dc=example,dc=com",
    "service_accounts": "uid={uid},ou=services,dc=example,dc=com"
  }
}
```

#### Default Object Classes

Configure default object classes for streams:

```json
{
  "default_object_classes": {
    "users": ["inetOrgPerson", "organizationalPerson", "person", "top"],
    "groups": ["groupOfNames", "top"],
    "service_accounts": ["account", "top"]
  }
}
```

## Usage

### Basic Usage

```bash
# Read from stdin
cat data.json | poetry run target-ldap --config config.json

# Read from tap-ldap
poetry run tap-ldap --config tap-config.json | poetry run target-ldap --config target-config.json
```

### With State Handling

```bash
poetry run tap-ldap --config tap-config.json --state state.json | \
  poetry run target-ldap --config target-config.json > new-state.json
```

## Data Format

The target expects Singer-formatted messages:

### RECORD Message

```json
{
  "type": "RECORD",
  "stream": "users",
  "record": {
    "dn": "uid=jdoe,ou=users,dc=example,dc=com",
    "uid": "jdoe",
    "cn": "John Doe",
    "sn": "Doe",
    "givenName": "John",
    "mail": "jdoe@example.com",
    "objectClass": ["inetOrgPerson", "person"]
  }
}
```

### Delete Records

To delete an entry, include the `_sdc_deleted_at` field:

```json
{
  "type": "RECORD",
  "stream": "users",
  "record": {
    "dn": "uid=jdoe,ou=users,dc=example,dc=com",
    "_sdc_deleted_at": "2024-01-15T10:30:00Z"
  }
}
```

## Supported Operations

- **Upsert**: Automatically creates new entries or updates existing ones
- **Delete**: Removes entries when `_sdc_deleted_at` is present
- **Schema Validation**: Validates records against LDAP schema
- **Multi-valued Attributes**: Handles attributes like `memberOf`, `mail`

## Development

### Testing

```bash
poetry run pytest
```

### Linting

```bash
poetry run black src/ tests/
poetry run ruff check src/ tests/
poetry run mypy src/
```

## Integration with Meltano

Add to your `meltano.yml`:

```yaml
project_id: your_project_id
environments:
- name: dev
default_environment: dev
plugins:
  loaders:
  - name: target-ldap
    namespace: target_ldap
    pip_url: file:///path/to/target-ldap
    executable: target-ldap
    settings:
    - name: host
      kind: string
      description: LDAP server hostname
    - name: port
      kind: integer
      value: 389
    - name: bind_dn
      kind: string
      description: Bind DN for authentication
    - name: password
      kind: password
      description: Bind password
    - name: base_dn
      kind: string
      description: Base DN for operations
    config:
      host: ${LDAP_HOST}
      bind_dn: ${LDAP_BIND_DN}
      password: ${LDAP_PASSWORD}
      base_dn: ${LDAP_BASE_DN}
```

## Error Handling

The target implements comprehensive error handling:

- Connection failures are logged and retried
- Invalid DNs are detected before operations
- Schema validation prevents invalid attributes
- Detailed error messages for troubleshooting
