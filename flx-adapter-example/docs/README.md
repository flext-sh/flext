# 📚 FLX Adapter Example - Documentation

> **Module**: Comprehensive documentation for FLX Adapter Example project with architecture guides and API references | **Audience**: Developers, Solution Architects, Technical Writers | **Status**: Production Ready

## 📋 **Overview**

Complete documentation suite for the FLX Adapter Example project, providing comprehensive guides for architecture patterns, API references, deployment procedures, and development workflows. This documentation demonstrates best practices for documenting enterprise FLX framework applications.

---

## 🧭 **Navigation Context**

**🏠 Root**: [PyAuto Home](../../README.md) → **📂 Component**: [FLX Adapter Example](../README.md) → **📂 Current**: Documentation

---

## 🎯 **Module Purpose**

This documentation module provides comprehensive guides and references for the FLX Adapter Example project, including architectural documentation, API specifications, deployment guides, and development procedures following enterprise documentation standards.

### **Key Documentation Categories**

- **Architecture Documentation** - Hexagonal architecture and design patterns
- **API Documentation** - REST API specifications and endpoint references
- **Development Guides** - Development workflows and coding standards
- **Deployment Documentation** - Deployment procedures and environment setup
- **User Guides** - End-user documentation and tutorials
- **Integration Guides** - External system integration documentation

---

## 📁 **Documentation Structure**

```
docs/
├── architecture/
│   ├── README.md                    # Architecture overview
│   ├── hexagonal-architecture.md   # Hexagonal architecture implementation
│   ├── domain-driven-design.md     # DDD patterns and practices
│   ├── event-sourcing.md           # Event sourcing implementation
│   └── design-decisions.md         # Architectural decision records
├── api/
│   ├── README.md                    # API documentation overview
│   ├── openapi.yaml                # OpenAPI 3.0 specification
│   ├── endpoints-reference.md      # Detailed endpoint documentation
│   ├── authentication.md           # Authentication and authorization
│   └── error-handling.md           # Error response specifications
├── development/
│   ├── README.md                    # Development guide overview
│   ├── getting-started.md          # Quick start guide
│   ├── coding-standards.md         # Coding standards and conventions
│   ├── testing-guide.md            # Testing strategies and patterns
│   └── contributing.md             # Contribution guidelines
├── deployment/
│   ├── README.md                    # Deployment guide overview
│   ├── docker-deployment.md        # Docker containerization guide
│   ├── kubernetes-deployment.md    # Kubernetes deployment patterns
│   ├── production-setup.md         # Production environment setup
│   └── monitoring-setup.md         # Monitoring and observability
├── user-guides/
│   ├── README.md                    # User guides overview
│   ├── quick-start.md              # User quick start tutorial
│   ├── advanced-usage.md           # Advanced features guide
│   ├── troubleshooting.md          # Common issues and solutions
│   └── faq.md                      # Frequently asked questions
├── integration/
│   ├── README.md                    # Integration guides overview
│   ├── database-integration.md     # Database integration patterns
│   ├── external-apis.md            # External API integration
│   ├── event-streaming.md          # Event streaming integration
│   └── monitoring-integration.md   # Monitoring system integration
└── examples/
    ├── README.md                    # Examples overview
    ├── basic-usage.md              # Basic usage examples
    ├── advanced-patterns.md        # Advanced implementation patterns
    └── real-world-scenarios.md     # Real-world use case examples
```

---

## 🏗️ **Architecture Documentation**

### **Hexagonal Architecture Guide (architecture/hexagonal-architecture.md)**

````markdown
# Hexagonal Architecture Implementation

## Overview

The FLX Adapter Example implements hexagonal architecture (Ports and Adapters pattern) to achieve clean separation of concerns and maintainable code structure.

## Architecture Layers

### Domain Layer (Core)

- **Purpose**: Business logic and domain rules
- **Dependencies**: None (dependency-free)
- **Components**:
  - Domain entities
  - Value objects
  - Domain services
  - Business rules

### Application Layer

- **Purpose**: Application services and use cases
- **Dependencies**: Domain layer only
- **Components**:
  - Application services
  - Command handlers
  - Query handlers
  - DTOs

### Infrastructure Layer

- **Purpose**: Technical implementation details
- **Dependencies**: Application and domain layers
- **Components**:
  - Database adapters
  - External API clients
  - Message queue adapters
  - File system adapters

## Port Definitions

### Primary Ports (Inbound)

```python
class CustomerManagementPort(ABC):
    """Primary port for customer management operations."""

    @abstractmethod
    async def create_customer(self, customer_data: CustomerCreationDTO) -> CustomerDTO:
        """Create new customer."""
        pass

    @abstractmethod
    async def get_customer(self, customer_id: str) -> Optional[CustomerDTO]:
        """Get customer by ID."""
        pass
```
````

### Secondary Ports (Outbound)

```python
class CustomerRepositoryPort(ABC):
    """Secondary port for customer persistence."""

    @abstractmethod
    async def save(self, customer: Customer) -> Customer:
        """Save customer entity."""
        pass

    @abstractmethod
    async def find_by_id(self, customer_id: str) -> Optional[Customer]:
        """Find customer by ID."""
        pass
```

## Benefits

1. **Testability**: Easy to mock dependencies for testing
2. **Flexibility**: Easy to swap implementations
3. **Maintainability**: Clear separation of concerns
4. **Independence**: Domain logic independent of infrastructure

````

### **Domain-Driven Design Guide (architecture/domain-driven-design.md)**

```markdown
# Domain-Driven Design Implementation

## Strategic Design

### Bounded Contexts
- **Customer Management**: Customer lifecycle and operations
- **Order Processing**: Order management and fulfillment
- **Inventory Management**: Stock and product management

### Context Mapping
````

Customer Management ---> Order Processing (Customer-Supplier)
Order Processing ---> Inventory Management (Customer-Supplier)

````

## Tactical Design

### Entities
```python
@dataclass
class Customer(Entity):
    """Customer aggregate root."""

    name: str
    email: Email
    status: CustomerStatus

    def change_email(self, new_email: Email) -> None:
        """Change customer email with validation."""
        self._validate_email_change(new_email)
        old_email = self.email
        self.email = new_email

        self.add_domain_event(CustomerEmailChangedEvent(
            customer_id=self.id,
            old_email=old_email.value,
            new_email=new_email.value
        ))
````

### Value Objects

```python
@dataclass(frozen=True)
class Email(ValueObject):
    """Email value object with validation."""

    value: str

    def __post_init__(self):
        if not self._is_valid_email(self.value):
            raise InvalidEmailError(f"Invalid email: {self.value}")

    def _is_valid_email(self, email: str) -> bool:
        return "@" in email and "." in email
```

### Domain Events

```python
@dataclass
class CustomerEmailChangedEvent(DomainEvent):
    """Event raised when customer email changes."""

    customer_id: str
    old_email: str
    new_email: str
    event_type: str = "customer_email_changed"
```

````

---

## 🔌 **API Documentation**

### **OpenAPI Specification (api/openapi.yaml)**

```yaml
openapi: 3.0.3
info:
  title: FLX Adapter Example API
  description: RESTful API for FLX Adapter Example application
  version: 1.0.0
  contact:
    name: Development Team
    email: dev@company.com

servers:
  - url: https://api.example.com/v1
    description: Production server
  - url: https://staging-api.example.com/v1
    description: Staging server
  - url: http://localhost:8000/v1
    description: Development server

paths:
  /customers:
    get:
      summary: List customers
      description: Retrieve a paginated list of customers
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
            minimum: 1
            maximum: 100
        - name: offset
          in: query
          schema:
            type: integer
            default: 0
            minimum: 0
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  customers:
                    type: array
                    items:
                      $ref: '#/components/schemas/Customer'
                  total:
                    type: integer
                  limit:
                    type: integer
                  offset:
                    type: integer

    post:
      summary: Create customer
      description: Create a new customer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CustomerCreationRequest'
      responses:
        '201':
          description: Customer created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Customer'
        '400':
          description: Invalid input
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '409':
          description: Customer already exists
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

  /customers/{customerId}:
    get:
      summary: Get customer
      description: Retrieve customer by ID
      parameters:
        - name: customerId
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Customer found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Customer'
        '404':
          description: Customer not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

components:
  schemas:
    Customer:
      type: object
      properties:
        id:
          type: string
          format: uuid
          description: Unique customer identifier
        name:
          type: string
          description: Customer full name
        email:
          type: string
          format: email
          description: Customer email address
        status:
          type: string
          enum: [active, inactive, suspended]
          description: Customer status
        created_at:
          type: string
          format: date-time
          description: Customer creation timestamp
        updated_at:
          type: string
          format: date-time
          description: Last update timestamp
      required:
        - id
        - name
        - email
        - status
        - created_at
        - updated_at

    CustomerCreationRequest:
      type: object
      properties:
        name:
          type: string
          minLength: 1
          maxLength: 255
          description: Customer full name
        email:
          type: string
          format: email
          description: Customer email address
      required:
        - name
        - email

    Error:
      type: object
      properties:
        error:
          type: string
          description: Error type
        message:
          type: string
          description: Human-readable error message
        details:
          type: object
          description: Additional error details
        timestamp:
          type: string
          format: date-time
          description: Error timestamp
      required:
        - error
        - message
        - timestamp

  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - BearerAuth: []
````

### **Authentication Guide (api/authentication.md)**

````markdown
# Authentication and Authorization

## Overview

The FLX Adapter Example API uses JWT (JSON Web Tokens) for authentication and role-based access control (RBAC) for authorization.

## Authentication Flow

1. **Login**: POST `/auth/login` with credentials
2. **Token Receipt**: Receive JWT access token and refresh token
3. **API Access**: Include token in `Authorization` header
4. **Token Refresh**: Use refresh token to get new access token

## JWT Token Structure

```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "roles": ["user", "admin"],
  "exp": 1640995200,
  "iat": 1640908800
}
```
````

## Authorization Levels

### Roles

- **admin**: Full system access
- **user**: Standard user operations
- **readonly**: Read-only access

### Permissions

- **customers:read**: View customer information
- **customers:write**: Create and modify customers
- **orders:read**: View order information
- **orders:write**: Create and modify orders

## Implementation Example

```python
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
import jwt

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_permission(permission: str):
    async def permission_checker(current_user = Depends(get_current_user)):
        user_permissions = await get_user_permissions(current_user)
        if permission not in user_permissions:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return permission_checker

# Usage in endpoints
@app.get("/customers")
async def list_customers(user = Depends(require_permission("customers:read"))):
    return await customer_service.list_customers()
```

````

---

## 🚀 **Development Documentation**

### **Getting Started Guide (development/getting-started.md)**

```markdown
# Getting Started

## Prerequisites

- Python 3.9+
- Poetry (dependency management)
- Docker and Docker Compose
- PostgreSQL (for development)
- Redis (for caching)

## Quick Setup

1. **Clone Repository**
```bash
git clone <repository-url>
cd flx-adapter-example
````

2. **Install Dependencies**

```bash
poetry install
poetry shell
```

3. **Start Services**

```bash
docker-compose up -d postgres redis
```

4. **Setup Database**

```bash
poetry run alembic upgrade head
```

5. **Run Application**

```bash
poetry run uvicorn flx_adapter_example.main:app --reload
```

6. **Verify Setup**

```bash
curl http://localhost:8000/health
```

## Development Workflow

1. **Create Feature Branch**

```bash
git checkout -b feature/customer-management
```

2. **Implement Changes**

- Follow hexagonal architecture patterns
- Write tests first (TDD)
- Update documentation

3. **Run Tests**

```bash
poetry run pytest
poetry run pytest --cov=flx_adapter_example
```

4. **Quality Checks**

```bash
poetry run black .
poetry run ruff check .
poetry run mypy flx_adapter_example
```

5. **Commit and Push**

```bash
git add .
git commit -m "feat: add customer management endpoint"
git push origin feature/customer-management
```

## Project Structure

```
flx-adapter-example/
├── src/flx_adapter_example/
│   ├── domain/              # Domain layer
│   ├── application/         # Application services
│   ├── infrastructure/      # Infrastructure adapters
│   └── presentation/        # API controllers
├── tests/                   # Test suite
├── docs/                   # Documentation
├── scripts/                # Development scripts
└── docker/                 # Docker configurations
```

````

---

## 🐳 **Deployment Documentation**

### **Docker Deployment Guide (deployment/docker-deployment.md)**

```markdown
# Docker Deployment

## Dockerfile

```dockerfile
FROM python:3.11-slim as builder

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Configure Poetry
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --only=main --no-dev

FROM python:3.11-slim as runtime

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY src/ ./

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "flx_adapter_example.main:app", "--host", "0.0.0.0", "--port", "8000"]
````

## Docker Compose

```yaml
version: "3.8"

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://app:password@postgres:5432/flx_adapter_example
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  postgres:
    image: postgres:14
    environment:
      - POSTGRES_USER=app
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=flx_adapter_example
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

volumes:
  postgres_data:
```

## Multi-stage Production Build

```dockerfile
# Production optimized Dockerfile
FROM python:3.11-slim as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

FROM base as builder

RUN pip install poetry

WORKDIR /app
COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --only=main --no-dev

FROM base as runtime

# Security: Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Copy installed packages
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app
COPY --chown=appuser:appgroup src/ ./

USER appuser

EXPOSE 8000

CMD ["uvicorn", "flx_adapter_example.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

````

---

## 📖 **User Guides**

### **Quick Start Tutorial (user-guides/quick-start.md)**

```markdown
# Quick Start Tutorial

## Introduction

This tutorial will walk you through using the FLX Adapter Example API to manage customers and orders.

## Step 1: Authentication

First, obtain an access token:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password"
  }'
````

Response:

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## Step 2: Create a Customer

```bash
curl -X POST http://localhost:8000/v1/customers \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john.doe@example.com"
  }'
```

Response:

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "John Doe",
  "email": "john.doe@example.com",
  "status": "active",
  "created_at": "2025-06-19T10:00:00Z",
  "updated_at": "2025-06-19T10:00:00Z"
}
```

## Step 3: Retrieve Customer

```bash
curl -X GET http://localhost:8000/v1/customers/123e4567-e89b-12d3-a456-426614174000 \
  -H "Authorization: Bearer <your-token>"
```

## Step 4: List Customers

```bash
curl -X GET "http://localhost:8000/v1/customers?limit=10&offset=0" \
  -H "Authorization: Bearer <your-token>"
```

## Error Handling

The API returns structured error responses:

```json
{
  "error": "ValidationError",
  "message": "Invalid email format",
  "details": {
    "field": "email",
    "value": "invalid-email"
  },
  "timestamp": "2025-06-19T10:00:00Z"
}
```

## Next Steps

- Explore [Advanced Usage](advanced-usage.md)
- Check [API Reference](../api/endpoints-reference.md)
- Review [Integration Guides](../integration/README.md)

```

---

## 🔗 **Cross-References**

### **Component Documentation**

- [Component Overview](../README.md) - Complete FLX Adapter Example documentation
- [Source Implementation](../src/README.md) - Source code structure and patterns
- [Tests](../tests/README.md) - Testing framework and procedures
- [Scripts](../scripts/README.md) - Development and automation scripts

### **Framework Documentation**

- [FLX Framework](../../flx/README.md) - Core framework documentation
- [Architecture Guide](../../docs/architecture/hexagonal-architecture.md) - Hexagonal architecture implementation
- [Development Standards](../../docs/development/standards.md) - Development best practices

### **External References**

- [FastAPI Documentation](https://fastapi.tiangolo.com/) - FastAPI framework reference
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/) - Architectural pattern
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html) - DDD concepts

---

**📂 Module**: Documentation | **🏠 Component**: [FLX Adapter Example](../README.md) | **Framework**: Markdown/OpenAPI | **Updated**: 2025-06-19
```
