# Python API Client Template Example

> **Related Documentation:**
>
> - [FLEXT Framework Overview](../getting-started/flext-framework-overview.md) - Main framework introduction
> - [Development Standards](../development/standardization-plan.md) - Code quality standards
> - [Testing Comprehensive Guide](../development/testing-comprehensive-guide.md) - Testing strategies
> - [Hexagonal Architecture Guide](../architecture/UNIFIED_ARCHITECTURE_GUIDE.md) - Architecture principles

A comprehensive Python client library and CLI tools template for RESTful APIs, inspired by production-grade implementations and following FLEXT framework patterns.

## Features

- **Robust API Client**: Full-featured client for making HTTP requests with authentication, retries, and error handling
- **Dynamic Entity Support**: Work with API entities in a type-safe way with automatic validation
- **Schema Extraction**: Extract and manage API schemas with support for caching and offline mode
- **Flexible Configuration**: Support for environment variables, configuration profiles, and configuration files
- **Comprehensive Error Handling**: Detailed error classes for different error conditions
- **Advanced Pagination**: Automatic handling of various pagination formats with iterator interface
- **Rich CLI Tools**: Command-line tools for configuration, entity, and schema operations
- **Type Safety**: Full type annotations and validation with Pydantic
- **Hexagonal Architecture**: Follows FLEXT framework architectural patterns

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

The API client can be configured in several ways, following FLEXT configuration patterns:

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

Create a `.env.{profile}` file in your project directory:

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

The API client provides several command-line tools following FLEXT CLI patterns:

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

### Basic Client Usage (Following FLEXT Adapter Patterns)

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

### Entity API (Domain-Driven Design)

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

### Schema API (Type Safety)

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

### Advanced Pagination

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

## Error Handling (Following FLEXT Exception Patterns)

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

## Architecture Pattern (Hexagonal Architecture)

This template follows FLEXT hexagonal architecture principles:

```python
# Domain Layer - Pure business logic
class User:
    """Domain entity representing a user."""
    def __init__(self, id: str, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email

    def is_active(self) -> bool:
        """Business logic for determining if user is active."""
        return self.status == "active"

# Port Interface - Abstract definition
from abc import ABC, abstractmethod

class UserRepositoryPort(ABC):
    """Port interface for user repository."""

    @abstractmethod
    async def get_user(self, user_id: str) -> User:
        """Get user by ID."""
        pass

    @abstractmethod
    async def create_user(self, user: User) -> User:
        """Create a new user."""
        pass

# Adapter Implementation - Concrete API integration
class ApiUserRepository(UserRepositoryPort):
    """Adapter implementing user repository via API."""

    def __init__(self, api_client: ApiClient):
        self._api_client = api_client

    async def get_user(self, user_id: str) -> User:
        """Get user from API."""
        response = await self._api_client.get(f"users/{user_id}")
        if response.success:
            data = response.data
            return User(
                id=data["id"],
                name=data["name"],
                email=data["email"]
            )
        raise UserNotFoundError(f"User {user_id} not found")

    async def create_user(self, user: User) -> User:
        """Create user via API."""
        user_data = {
            "name": user.name,
            "email": user.email
        }
        response = await self._api_client.post("users", data=user_data)
        if response.success:
            data = response.data
            return User(
                id=data["id"],
                name=data["name"],
                email=data["email"]
            )
        raise UserCreationError("Failed to create user")

# Application Service - Coordinates domain and infrastructure
class UserService:
    """Application service for user operations."""

    def __init__(self, user_repository: UserRepositoryPort):
        self._user_repository = user_repository

    async def get_active_user(self, user_id: str) -> User:
        """Get user and validate they are active."""
        user = await self._user_repository.get_user(user_id)
        if not user.is_active():
            raise InactiveUserError(f"User {user_id} is not active")
        return user
```

## Development

### Setup

```bash
# Install development dependencies
poetry install --with dev

# Install pre-commit hooks
pre-commit install
```

### Testing (Following FLEXT Testing Patterns)

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=project_name

# Run specific tests
pytest tests/test_client.py

# Run unit tests only
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run with FLEXT test markers
pytest -m "not slow"
pytest -m "integration"
```

### Testing Examples

```python
import pytest
from unittest.mock import AsyncMock
from project_name import UserService, User

class TestUserService:
    """Test user service following FLEXT testing patterns."""

    @pytest.fixture
    def mock_user_repository(self):
        """Mock user repository for testing."""
        return AsyncMock(spec=UserRepositoryPort)

    @pytest.fixture
    def user_service(self, mock_user_repository):
        """User service with mocked dependencies."""
        return UserService(mock_user_repository)

    @pytest.mark.asyncio
    async def test_get_active_user_success(self, user_service, mock_user_repository):
        """Test getting an active user."""
        # Arrange
        user = User(id="123", name="John Doe", email="john@example.com")
        user.status = "active"
        mock_user_repository.get_user.return_value = user

        # Act
        result = await user_service.get_active_user("123")

        # Assert
        assert result == user
        mock_user_repository.get_user.assert_called_once_with("123")

    @pytest.mark.asyncio
    async def test_get_active_user_inactive_raises_error(self, user_service, mock_user_repository):
        """Test that inactive user raises error."""
        # Arrange
        user = User(id="123", name="John Doe", email="john@example.com")
        user.status = "inactive"
        mock_user_repository.get_user.return_value = user

        # Act & Assert
        with pytest.raises(InactiveUserError):
            await user_service.get_active_user("123")
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

## Project Structure (FLEXT-Aligned)

```
project_name/                 # Main package
├── __init__.py               # Package initialization and exports
├── core/                     # Domain layer (FLEXT pattern)
│   ├── entities.py          # Domain entities
│   ├── value_objects.py     # Value objects
│   ├── events.py            # Domain events
│   └── exceptions.py        # Domain exceptions
├── ports/                    # Port interfaces (FLEXT pattern)
│   ├── inbound/             # Inbound ports
│   └── outbound/            # Outbound ports (repository, etc.)
├── adapters/                 # Adapter implementations (FLEXT pattern)
│   ├── inbound/             # CLI adapters
│   └── outbound/            # API client adapters
├── application/              # Application services (FLEXT pattern)
│   ├── services.py          # Application services
│   └── commands.py          # Command handlers
├── infrastructure/           # Infrastructure layer (FLEXT pattern)
│   ├── config.py            # Configuration management
│   ├── client.py            # HTTP client implementation
│   └── logging.py           # Logging utilities
├── cli/                      # CLI implementation
│   ├── __init__.py
│   ├── commands.py          # CLI commands
│   └── formatters.py        # Output formatters
tests/                        # Test suite (FLEXT pattern)
├── unit/                     # Unit tests
│   ├── core/                # Domain tests
│   ├── application/         # Application service tests
│   └── adapters/            # Adapter tests
├── integration/              # Integration tests
├── e2e/                     # End-to-end tests
├── conftest.py              # Test fixtures
└── __init__.py
docs/                         # Documentation
├── api/                      # API documentation
├── cli/                      # CLI documentation
└── examples/                 # Usage examples
examples/                     # Example code
├── basic_usage.py           # Basic client usage example
└── entity_example.py        # Entity API example
```

## Customization for FLEXT Framework

This template is designed to be customized for your specific API while following FLEXT patterns:

1. **Replace `project_name`** with your actual project name
2. **Update domain entities** to match your API's business domain
3. **Define port interfaces** for your specific operations
4. **Implement adapters** for your API's endpoints
5. **Create application services** for your business workflows
6. **Extend CLI** with commands for your API's operations
7. **Add comprehensive tests** following FLEXT testing patterns

## Best Practices (FLEXT Aligned)

### Domain-Driven Design

- Keep business logic in domain entities
- Use value objects for immutable data
- Implement aggregate roots for complex entities
- Raise domain events for important business occurrences

### Hexagonal Architecture

- Define clear port interfaces
- Implement adapters for external systems
- Keep domain logic independent of infrastructure
- Use dependency injection for loose coupling

### Testing Strategy

- Unit tests for domain logic
- Integration tests for adapter implementations
- End-to-end tests for complete workflows
- Mock external dependencies in unit tests

### Code Quality

- Follow PEP 8 standards
- Use type hints throughout
- Implement comprehensive error handling
- Write clear documentation and docstrings

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Follow FLEXT development standards
4. Write comprehensive tests
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## See Also

- [FLEXT Framework Overview](../getting-started/flext-framework-overview.md) - Framework introduction
- [Hexagonal Architecture Guide](../architecture/UNIFIED_ARCHITECTURE_GUIDE.md) - Architecture principles
- [Testing Patterns](../development/testing-comprehensive-guide.md) - Testing strategies
- [Development Standards](../development/standardization-plan.md) - Code quality guidelines
