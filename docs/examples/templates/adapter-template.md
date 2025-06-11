# Python API Client Template

A comprehensive Python client library and CLI tools template for RESTful APIs, inspired by production-grade implementations.

## Features

- **Robust API Client**: Full-featured client for making HTTP requests with authentication, retries, and error handling
- **Dynamic Entity Support**: Work with API entities in a type-safe way with automatic validation
- **Schema Extraction**: Extract and manage API schemas with support for caching and offline mode
- **Flexible Configuration**: Support for environment variables, configuration profiles, and configuration files
- **Comprehensive Error Handling**: Detailed error classes for different error conditions
- **Advanced Pagination**: Automatic handling of various pagination formats with iterator interface
- **Rich CLI Tools**: Command-line tools for configuration, entity, and schema operations
- **Type Safety**: Full type annotations and validation with Pydantic
- **Extensive Documentation**: Comprehensive documentation for all components

## Installation

```bash
# Clone the repository
git clone git@github.com:your-organization/project_name.git
cd project_name

# Install in development mode
pip install -e .

# Or install with Poetry
poetry install
```

## Configuration

The API client can be configured in several ways:

### Environment Variables

```bash
# Basic configuration
export API_URL="https://api.example.com"
export API_USERNAME="your-username"
export API_PASSWORD="your-password"

# Optional settings
export API_TIMEOUT=60
export API_VERIFY_SSL=true
export API_MAX_RETRIES=3
```

### Profile-Based Configuration

Create a `.env.{profile}` file in your flx_project directory:

```bash
# .env.dev
API_DEV_URL="https://api-dev.example.com"
API_DEV_USERNAME="dev-username"
API_DEV_PASSWORD="dev-password"
```

Then use the `--profile` option with CLI commands:

```bash
cli-tool --profile dev ping
```

### Configuration Files

You can also create JSON configuration files:

```json
{
  "url": "https://api.example.com",
  "username": "your-username",
  "password": "your-password",
  "timeout": 60,
  "verify_ssl": true
}
```

## CLI Usage

The API client provides several command-line tools:

### Configuration Management

```bash
# View current configuration
cli-tool config view

# List available profiles
cli-tool config profiles

# Validate configuration and test connection
cli-tool config validate --test-connection

# Create a configuration file
cli-tool config create --url "https://api.example.com" --username "user" --password "pass" --output-file config.json
```

### Entity Operations

```bash
# List available entities
cli-tool entity list
cli-tool entity list --with-fields

# Query an entity
cli-tool entity query users --limit 10 --filter status=active --sort-by created_at
cli-tool entity query users --output-format json --output users.json

# Get a specific entity resource
cli-tool entity get users 123
cli-tool entity get users 123 --output-format table
```

### Schema Operations

```bash
# Extract schemas from API
cli-tool schema extract --all --output-dir schemas
cli-tool schema extract --entity users --entity products --output-dir schemas

# View schema for an entity
cli-tool schema view users --schema-dir schemas
cli-tool schema view users --schema-dir schemas --format json
```

## Python API Usage

### Basic Client Usage

```python
from project_name import ApiClient, ApiResponse

# Create a client with direct configuration
client = ApiClient(
    url="https://api.example.com",
    username="your-username",
    password="your-password"
)

# Or use environment variables
client = ApiClient()

# Or use a configuration profile
client = ApiClient.from_profile("dev")

# Make requests
response = client.get("users")
if response.success:
    users = response.data
    print(f"Found {len(users)} users")
    for user in users:
        print(f"User: {user['name']}")
else:
    print(f"Error: {response.error}")
```

### Entity API

```python
from project_name import ApiClient, EntityManager

# Create client and entity manager
client = ApiClient()
manager = EntityManager(client)

# Discover available entities
entities = manager.discover_entities()
print(f"Available entities: {entities}")

# Get entity instance
users_entity = manager.get_entity("users")

# List users with filtering and pagination
response = users_entity.list(
    filters={"status": "active"},
    sort_by="created_at",
    sort_order="desc",
    limit=10,
    offset=0
)

# Get a specific user
user_response = users_entity.get("123")
user = user_response.data

# Create a new user
new_user = {
    "name": "Jane Smith",
    "email": "jane@example.com"
}
create_response = users_entity.create(new_user)

# Update a user
update_response = users_entity.update("123", {"status": "inactive"})

# Delete a user
delete_response = users_entity.delete("123")
```

### Schema API

```python
from project_name import ApiClient, SchemaManager

# Create client and schema manager
client = ApiClient()
schema_manager = SchemaManager(client)

# Get schema for an entity
user_schema = schema_manager.get_schema("users")
print(f"Fields: {list(user_schema.fields.keys())}")
print(f"Required fields: {user_schema.required_fields}")

# Get model class for an entity
User = schema_manager.get_model("users")

# Create an instance of the model
user = User(id="123", name="John Doe", email="john@example.com")
print(f"User: {user.model_dump()}")

# Extract and cache all schemas
schemas = schema_manager.extract_all_schemas()
```

### Pagination

```python
from project_name import ApiClient, paginate

# Create client
client = ApiClient()

# Create paginated iterator
users_iterator = paginate(
    client=client,
    endpoint="api/users",
    params={"status": "active"},
    page_size=25
)

# Iterate through all pages automatically
for user in users_iterator:
    print(f"User: {user['name']}")

# Can also be used with entity list
from project_name import EntityManager
manager = EntityManager(client)
users_entity = manager.get_entity("users")

# Paginated list
response = users_entity.list(
    filters={"status": "active"},
    limit=10,
    offset=0
)

# Get next page
if response.page_info.has_next:
    next_page_response = users_entity.list(
        filters={"status": "active"},
        limit=10,
        offset=10
    )
```

## Error Handling

```python
from project_name import ApiClient, ApiError, ConnectionError, AuthenticationError

try:
    client = ApiClient()
    response = client.get("users")
    
    if not response.success:
        print(f"API returned an error: {response.error}")
        if response.error_details:
            print(f"Details: {response.error_details}")
    
    # Process successful response
    users = response.data
    
except ConnectionError as e:
    print(f"Connection error: {str(e)}")
except AuthenticationError as e:
    print(f"Authentication failed: {str(e)}")
except ApiError as e:
    print(f"API error: {str(e)}")
```

## Development

### Setup

```bash
# Install development dependencies
poetry install --with dev

# Install pre-commit hooks
pre-commit install
```

### Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=project_name

# Run specific tests
pytest tests/test_client.py
```

### Linting and Formatting

```bash
# Run linters
ruff check .

# Run type checker
mypy .

# Format code
black .
isort .
```

## Project Structure

```asciidoc
project_name/                 # Main package
├── __init__.py               # Package initialization and exports
├── client.py                 # API client implementation
├── config.py                 # Configuration management
├── entity.py                 # Entity operations
├── exceptions.py             # Exception hierarchy
├── models.py                 # Data models
├── schema.py                 # Schema extraction and management
├── pagination.py             # Pagination utilities
├── cli.py                    # Command-line interface
├── utils/                    # Utility functions
│   ├── __init__.py           # Utility package initialization
│   ├── formatting.py         # Formatting utilities
│   ├── logging.py            # Logging utilities
│   └── validation.py         # Validation utilities
tests/                        # Test suite
├── __init__.py
├── conftest.py               # Test fixtures
├── test_client.py            # Client tests
├── test_config.py            # Configuration tests
└── test_cli.py               # CLI tests
docs/                         # Documentation
├── api/                      # API documentation
├── cli/                      # CLI documentation
└── examples/                 # Usage examples
examples/                     # Example code
├── basic_usage.py            # Basic client usage example
└── entity_example.py         # Entity API example
scripts/                      # Utility scripts
schemas/                      # Schema cache directory
```

## Customization

This template is designed to be customized for your specific API:

1. Replace `project_name` with your actual flx_project name
2. Update configuration variables to match your API's requirements
3. Add domain-specific models and entities for your API
4. Extend the CLI with commands for your API's operations
5. Update documentation with your API's details

## License

This flx_project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## PEP 8 Compliance

This flx_project follows strict PEP 8 guidelines using the following tools:

- **Black**: Code formatter with a line length of 88 characters
- **isort**: Import sorting with Black-compatible settings
- **Ruff**: Fast Python linter with rules for PEP 8 enforcement
- **mypy**: Static type checking

To apply or check PEP 8 standards:

```bash
# Apply PEP 8 standards to the codebase
make pep8

# Check PEP 8 compliance without making changes
make pep8-check
```

The apply command will:

1. Format all code with Black
2. Sort imports with isort
3. Apply linting fixes with Ruff

The check command will verify compliance without making changes, useful for CI/CD pipelines

Alternatively, you can run linting and formatting separately:

```bash
# Run linting
make lint

# Format code
make format
```

### Pre-commit Hooks

This flx_project includes a pre-commit configuration to enforce PEP 8 standards before each commit.
To set up pre-commit hooks:

```bash
# Install dev dependencies (includes pre-commit)
make install-dev

# Install git hooks
make setup-hooks
```

Pre-commit will automatically:

- Check for trailing whitespace
- Fix end-of-file issues
- Validate YAML, TOML, and JSON files
- Apply Black and isort formatting
- Run Ruff linting
- Check type hints with mypy

This ensures all committed code follows the flx_project standards.
