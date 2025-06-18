# tap-ldap

Singer tap for LDAP data extraction, built with the [Singer SDK](https://sdk.meltano.com).

## Installation

```bash
cd tap-ldap
poetry install
```

## Configuration

Create a `config.json` file:

```json
{
  "host": "ldap.example.com",
  "port": 389,
  "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com",
  "password": "REDACTED_LDAP_BIND_PASSWORD_password",
  "base_dn": "dc=example,dc=com",
  "use_ssl": false,
  "timeout": 30,
  "page_size": 1000,
  "user_filter": "(objectClass=inetOrgPerson)",
  "group_filter": "(objectClass=groupOfNames)"
}
```

### Custom Streams

You can define custom streams for specific LDAP queries:

```json
{
  "custom_streams": [
    {
      "name": "service_accounts",
      "search_filter": "(&(objectClass=account)(uid=svc-*))",
      "primary_keys": ["dn"],
      "replication_key": "modifyTimestamp",
      "schema": {
        "properties": {
          "dn": {"type": "string"},
          "uid": {"type": "string"},
          "description": {"type": "string"},
          "modifyTimestamp": {"type": "string", "format": "date-time"}
        }
      }
    }
  ]
}
```

## Usage

### Discover available streams

```bash
poetry run tap-ldap --config config.json --discover > catalog.json
```

### Run the tap

```bash
poetry run tap-ldap --config config.json --catalog catalog.json
```

### Run with state for incremental sync

```bash
poetry run tap-ldap --config config.json --catalog catalog.json --state state.json
```

## Available Streams

- **users**: Extract user entries (inetOrgPerson)
- **groups**: Extract group entries (groupOfNames)
- **organizational_units**: Extract organizational units
- **schema**: Extract LDAP schema information
- **custom streams**: Any custom streams defined in configuration

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
  extractors:
  - name: tap-ldap
    namespace: tap_ldap
    pip_url: file:///path/to/tap-ldap
    executable: tap-ldap
    capabilities:
    - catalog
    - discover
    - state
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
      description: Base DN for searches
    config:
      host: ${LDAP_HOST}
      bind_dn: ${LDAP_BIND_DN}
      password: ${LDAP_PASSWORD}
      base_dn: ${LDAP_BASE_DN}
```
