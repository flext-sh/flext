# Schemas Directory

This directory is used to cache schema definitions extracted from the API. Schema files are used to generate models and validate data.

## Schema Files

Schema files are stored in JSON format with the following naming convention:

- `{entity_name}.schema.json` - Schema definition for an entity

## Extracting Schemas

You can extract schemas using the CLI tool:

```bash
# Extract all schemas
cli-tool schema extract --all --output-dir ./schemas

# Extract schema for a specific entity
cli-tool schema extract --entity users --output-dir ./schemas
```

Or using the Makefile:

```bash
# Extract all schemas
make extract-schemas

# Extract schema for a specific entity
make extract-schema ENTITY=users
```

## Schema Format

Schemas are stored in JSON Schema format. Here's an example:

```json
{
  "type": "object",
  "title": "user",
  "description": "User entity",
  "properties": {
    "id": {
      "type": "string",
      "description": "Unique identifier"
    },
    "name": {
      "type": "string",
      "description": "User's full name"
    },
    "email": {
      "type": "string",
      "format": "email",
      "description": "User's email address"
    }
  },
  "required": ["id", "name", "email"]
}
```

## Configuration

You can configure schema settings in the `.env` file:

```bash
API_SCHEMA_PATH=api/schemas
API_SCHEMA_CACHE_DIR=./schemas
```
