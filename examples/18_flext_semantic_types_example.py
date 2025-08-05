#!/usr/bin/env python3
"""FLEXT Semantic Types System - Practical Usage Examples.

This example demonstrates the new FLEXT Semantic Types Standard implemented
in semantic_types.py, showing how to use the hierarchical type system across
different domains and scenarios.

Key Features Demonstrated:
    - Hierarchical type organization with FlextTypes namespace
    - Domain-specific type extensions for projects
    - Protocol-based structural typing for flexibility
    - Type-safe functional programming patterns
    - Cross-project type compatibility strategies

Usage:
    python examples/18_flext_semantic_types_example.py

Architecture Integration:
    This example shows how the semantic type system integrates with:
    - FlextResult for railway-oriented programming
    - Domain models and business logic
    - Cross-service communication patterns
    - Plugin and extension development

For complete documentation see:
/home/marlonsc/flext/docs/FLEXT_SEMANTIC_TYPES_STANDARD.md

"""

from __future__ import annotations

from flext_core.semantic_types import (
    FlextTypes, 
    FlextTypeFactory,
    FlextTypeExtension,
    ConnectionProtocol,
    AuthProtocol,
    ObservabilityProtocol,
    FlextConnectionType,
    FlextDataFormat,
    FlextOperationStatus,
)
from flext_core import FlextResult

# =============================================================================
# EXAMPLE 1: Core Functional Types Usage
# =============================================================================

def demonstrate_core_functional_types() -> None:
    """Demonstrate core functional type patterns."""
    print("=== Core Functional Types ===")
    
    # Predicate functions for filtering
    is_active_user: FlextTypes.Core.Predicate[dict[str, object]] = (
        lambda user: user.get("status") == "active"
    )
    
    # Factory functions for object creation
    create_user_factory: FlextTypes.Core.Factory[dict[str, object]] = lambda: {
        "id": "user_123",
        "name": "John Doe", 
        "status": "active",
        "email": "john@example.com"
    }
    
    # Transformer functions for data processing
    format_user_name: FlextTypes.Core.Transformer[dict[str, object], str] = (
        lambda user: f"{user.get('name', 'Unknown')} ({user.get('id', 'no-id')})"
    )
    
    # Validator functions for input validation
    validate_email: FlextTypes.Core.Validator[str] = lambda email: "@" in email
    
    # Demonstrate usage
    user = create_user_factory()
    print(f"Created user: {user}")
    print(f"Is active: {is_active_user(user)}")
    print(f"Formatted name: {format_user_name(user)}")
    print(f"Email valid: {validate_email(user['email'])}")
    print()

# =============================================================================
# EXAMPLE 2: Data Integration Types
# =============================================================================

def demonstrate_data_types() -> None:
    """Demonstrate data integration type patterns."""
    print("=== Data Integration Types ===")
    
    # Connection configuration
    oracle_config: FlextTypes.Data.ConnectionConfig = {
        "host": "localhost",
        "port": 1521,
        "service_name": "XE",
        "username": "system",
        "connection_type": FlextConnectionType.ORACLE
    }
    
    # Data records and processing
    user_record: FlextTypes.Data.Record = {
        "id": "123",
        "name": "Alice Smith",
        "email": "alice@company.com",
        "department": "Engineering"
    }
    
    # Batch processing
    record_batch: FlextTypes.Data.RecordBatch = [user_record, {
        "id": "456", 
        "name": "Bob Wilson",
        "email": "bob@company.com",
        "department": "Sales"
    }]
    
    # Schema definition
    user_schema: FlextTypes.Data.Schema = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "email": {"type": "string", "format": "email"},
            "department": {"type": "string"}
        },
        "required": ["id", "name", "email"]
    }
    
    print(f"Oracle connection: {oracle_config['host']}:{oracle_config['port']}")
    print(f"Processing {len(record_batch)} records")
    print(f"Schema has {len(user_schema.get('properties', {}))} fields")
    print()

# =============================================================================
# EXAMPLE 3: Authentication & Authorization Types  
# =============================================================================

def demonstrate_auth_types() -> None:
    """Demonstrate authentication and authorization type patterns."""
    print("=== Authentication & Authorization Types ===")
    
    # Token management
    access_token: FlextTypes.Auth.AccessToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    refresh_token: FlextTypes.Auth.RefreshToken = "refresh_abc123def456"
    
    # User credentials and context
    login_creds: FlextTypes.Auth.LoginCredentials = {
        "username": "alice.smith",
        "password": "secure_password_123"
    }
    
    auth_context: FlextTypes.Auth.AuthContext = {
        "user_id": "user_123",
        "username": "alice.smith",
        "roles": ["engineer", "team_lead"],
        "permissions": ["read", "write", "REDACTED_LDAP_BIND_PASSWORD"],
        "token_expires_at": "2025-08-06T10:00:00Z"
    }
    
    # Permission and role management
    user_permissions: list[FlextTypes.Auth.Permission] = ["user:read", "user:write", "project:REDACTED_LDAP_BIND_PASSWORD"]
    user_roles: list[FlextTypes.Auth.Role] = ["engineer", "team_lead"]
    
    print(f"Access token length: {len(access_token)}")
    print(f"User: {auth_context['username']}")
    print(f"Roles: {user_roles}")
    print(f"Permissions: {len(user_permissions)}")
    print()

# =============================================================================
# EXAMPLE 4: Observability Types
# =============================================================================

def demonstrate_observability_types() -> None:
    """Demonstrate observability and monitoring type patterns."""
    print("=== Observability & Monitoring Types ===")
    
    # Logging context
    log_context: FlextTypes.Observability.LogContext = {
        "service": "flext-api",
        "version": "1.0.0",
        "correlation_id": "corr_abc123def456",
        "user_id": "user_123",
        "operation": "user_creation"
    }
    
    # Metrics data
    performance_metric: FlextTypes.Observability.Metric = {
        "name": "request_duration", 
        "value": 0.245,
        "unit": "seconds",
        "tags": {"endpoint": "/api/users", "method": "POST"},
        "timestamp": "2025-08-05T15:30:00Z"
    }
    
    # Tracing information
    correlation_id: FlextTypes.Observability.CorrelationId = "corr_abc123def456"
    trace_id: FlextTypes.Observability.TraceId = "trace_def456ghi789"
    
    # Alert data
    alert_data: FlextTypes.Observability.Alert = {
        "level": "WARNING",
        "message": "High CPU usage detected",
        "service": "flext-core",
        "threshold": 85.0,
        "current_value": 92.3,
        "timestamp": "2025-08-05T15:30:00Z"
    }
    
    print(f"Service: {log_context['service']}")
    print(f"Correlation ID: {correlation_id}")
    print(f"Metric: {performance_metric['name']} = {performance_metric['value']}")
    print(f"Alert: {alert_data['level']} - {alert_data['message']}")
    print()

# =============================================================================
# EXAMPLE 5: Singer Protocol Types
# =============================================================================

def demonstrate_singer_types() -> None:
    """Demonstrate Singer protocol type patterns."""
    print("=== Singer Protocol Types ===")
    
    # Singer stream configuration
    singer_stream: FlextTypes.Singer.SingerStream = {
        "tap_stream_id": "users",
        "schema": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "email": {"type": "string"}
            }
        },
        "metadata": [
            {
                "breadcrumb": [],
                "metadata": {
                    "replication-method": "INCREMENTAL",
                    "replication-key": "updated_at",
                    "selected": True
                }
            }
        ]
    }
    
    # Singer record
    singer_record: FlextTypes.Singer.SingerRecord = {
        "type": "RECORD",
        "stream": "users",
        "record": {
            "id": "123",
            "name": "Alice Smith", 
            "email": "alice@company.com",
            "updated_at": "2025-08-05T15:30:00Z"
        },
        "time_extracted": "2025-08-05T15:30:00Z"
    }
    
    # Tap configuration
    tap_config: FlextTypes.Singer.TapConfig = {
        "api_url": "https://api.example.com",
        "api_key": "secret_key_123",
        "start_date": "2025-01-01T00:00:00Z",
        "batch_size": 1000
    }
    
    print(f"Stream: {singer_stream['tap_stream_id']}")
    print(f"Record type: {singer_record['type']}")
    print(f"Tap API: {tap_config['api_url']}")
    print()

# =============================================================================
# EXAMPLE 6: Project-Specific Type Extensions
# =============================================================================

class FlextOracleTypes(FlextTypeExtension):
    """Example of Oracle-specific type extensions."""
    
    class Data(FlextTypes.Data):
        """Oracle data domain extensions."""
        
        # Oracle-specific connection type
        type OracleConnection = dict[str, object]
        type OracleCredentials = dict[str, str]
        type OracleQuery = str
        type OracleResult = list[dict[str, object]]
        
        # WMS-specific types
        type WMSInventoryRecord = dict[str, object]
        type WMSShipmentRecord = dict[str, object]
    
    class Auth(FlextTypes.Auth):
        """Oracle authentication extensions."""
        
        type OracleUser = dict[str, object]
        type OracleRole = dict[str, object]
        type WalletConfig = dict[str, str]

def demonstrate_project_extensions() -> None:
    """Demonstrate project-specific type extensions."""
    print("=== Project-Specific Type Extensions ===")
    
    # Oracle connection with extended types
    oracle_connection: FlextOracleTypes.Data.OracleConnection = {
        "host": "oracle-db.company.com",
        "port": 1521,
        "service_name": "PROD",
        "username": "flext_user",
        "connection_pool_size": 10,
        "wallet_location": "/opt/oracle/wallet"
    }
    
    # Oracle user with extended context 
    oracle_user: FlextOracleTypes.Auth.OracleUser = {
        "username": "FLEXT_USER",
        "roles": ["FLEXT_READ", "FLEXT_WRITE"],
        "tablespace": "FLEXT_DATA",
        "profile": "FLEXT_PROFILE"
    }
    
    # WMS inventory record
    inventory_record: FlextOracleTypes.Data.WMSInventoryRecord = {
        "item_id": "ITEM123",
        "location": "A1-B2-C3",
        "quantity": 150,
        "unit_of_measure": "EA",
        "last_updated": "2025-08-05T15:30:00Z"
    }
    
    print(f"Oracle connection: {oracle_connection['host']}")
    print(f"Oracle user: {oracle_user['username']}")
    print(f"Inventory item: {inventory_record['item_id']} qty={inventory_record['quantity']}")
    print()

# =============================================================================
# EXAMPLE 7: Protocol-Based Integration
# =============================================================================

class MockOracleConnection:
    """Mock Oracle connection implementing ConnectionProtocol."""
    
    def __init__(self, config: FlextTypes.Data.ConnectionConfig) -> None:
        self.config = config
        self._connected = False
    
    def connect(self) -> bool:
        """Establish connection."""
        print(f"Connecting to Oracle at {self.config['host']}:{self.config['port']}")
        self._connected = True
        return True
    
    def disconnect(self) -> None:
        """Close connection."""
        print("Disconnecting from Oracle")
        self._connected = False
    
    def is_connected(self) -> bool:
        """Check connection status."""
        return self._connected

class MockAuthProvider:
    """Mock authentication provider implementing AuthProtocol."""
    
    def authenticate(self, credentials: FlextTypes.Auth.LoginCredentials) -> FlextTypes.Auth.AuthenticatedUser | None:
        """Authenticate user with credentials."""
        if credentials.get("username") == "REDACTED_LDAP_BIND_PASSWORD" and credentials.get("password") == "secret":
            return {
                "id": "user_123",
                "username": credentials["username"],
                "roles": ["REDACTED_LDAP_BIND_PASSWORD"],
                "authenticated_at": "2025-08-05T15:30:00Z"
            }
        return None
    
    def is_authenticated(self, context: FlextTypes.Auth.AuthContext) -> bool:
        """Check if context is authenticated."""
        return context.get("user_id") is not None

def demonstrate_protocol_integration() -> None:
    """Demonstrate protocol-based integration patterns."""
    print("=== Protocol-Based Integration ===")
    
    # Connection protocol usage
    connection_config: FlextTypes.Data.ConnectionConfig = {
        "host": "localhost",
        "port": 1521,
        "service_name": "XE"
    }
    
    connection: ConnectionProtocol = MockOracleConnection(connection_config)
    print(f"Connected: {connection.connect()}")
    print(f"Status: {connection.is_connected()}")
    connection.disconnect()
    
    # Authentication protocol usage
    auth_provider: AuthProtocol = MockAuthProvider()
    
    login_creds: FlextTypes.Auth.LoginCredentials = {
        "username": "REDACTED_LDAP_BIND_PASSWORD",
        "password": "secret"
    }
    
    user = auth_provider.authenticate(login_creds)
    if user:
        print(f"Authenticated user: {user['username']}")
        
        auth_context: FlextTypes.Auth.AuthContext = {
            "user_id": user["id"],
            "username": user["username"]
        }
        print(f"Is authenticated: {auth_provider.is_authenticated(auth_context)}")
    print()

# =============================================================================
# EXAMPLE 8: Type Factory Usage
# =============================================================================

def demonstrate_type_factories() -> None:
    """Demonstrate type factory utility patterns."""
    print("=== Type Factory Utilities ===")
    
    # Create predicate functions
    is_valid_email = FlextTypeFactory.predicate(lambda email: "@" in email and "." in email)
    is_positive_number = FlextTypeFactory.predicate(lambda x: x > 0)
    
    # Create factory functions
    user_factory = FlextTypeFactory.factory(lambda: {
        "id": "user_new",
        "name": "New User",
        "created_at": "2025-08-05T15:30:00Z"
    })
    
    # Create transformer functions
    uppercase_transform = FlextTypeFactory.transformer(lambda s: s.upper())
    length_transform = FlextTypeFactory.transformer(lambda s: len(s))
    
    # Create validator functions  
    email_validator = FlextTypeFactory.validator(
        lambda email: True if "@" in email else "Invalid email format"
    )
    
    # Demonstrate usage
    test_email = "user@example.com"
    print(f"Email '{test_email}' is valid: {is_valid_email(test_email)}")
    print(f"Number 42.5 is positive: {is_positive_number(42.5)}")
    
    new_user = user_factory()
    print(f"Created user: {new_user['name']}")
    
    text = "hello world"
    print(f"'{text}' -> '{uppercase_transform(text)}' (length: {length_transform(text)})")
    
    validation_result = email_validator(test_email)
    print(f"Email validation: {validation_result}")
    print()

# =============================================================================
# EXAMPLE 9: Integration with FlextResult
# =============================================================================

def demonstrate_flext_result_integration() -> None:
    """Demonstrate integration with FlextResult patterns."""
    print("=== FlextResult Type Integration ===")
    
    def validate_user_data(data: dict[str, object]) -> FlextResult[FlextTypes.Data.Record]:
        """Validate user data and return typed record."""
        # Type-safe validation using semantic types
        validator: FlextTypes.Core.Validator[dict[str, object]] = lambda d: (
            isinstance(d.get("id"), str) and 
            isinstance(d.get("name"), str) and
            isinstance(d.get("email"), str)
        )
        
        if not validator(data):
            return FlextResult.fail("Invalid user data structure")
        
        # Transform to typed record
        user_record: FlextTypes.Data.Record = {
            "id": data["id"],
            "name": data["name"], 
            "email": data["email"],
            "validated_at": "2025-08-05T15:30:00Z"
        }
        
        return FlextResult.ok(user_record)
    
    def process_user_record(record: FlextTypes.Data.Record) -> FlextResult[dict[str, object]]:
        """Process validated user record."""
        # Type-safe transformation
        transformer: FlextTypes.Core.Transformer[FlextTypes.Data.Record, dict[str, object]] = (
            lambda r: {
                "user_id": r["id"],
                "display_name": r["name"],
                "contact_email": r["email"],
                "processed_at": "2025-08-05T15:30:00Z",
                "status": FlextOperationStatus.COMPLETED
            }
        )
        
        return FlextResult.ok(transformer(record))
    
    # Railway-oriented programming with semantic types
    input_data = {
        "id": "user_456",
        "name": "Carol Johnson",
        "email": "carol@company.com"
    }
    
    result = (
        validate_user_data(input_data)
        .flat_map(process_user_record)
    )
    
    if result.is_success:
        processed_data = result.data
        print(f"Successfully processed user: {processed_data['display_name']}")
        print(f"Status: {processed_data['status']}")
    else:
        print(f"Processing failed: {result.error}")
    print()

# =============================================================================
# MAIN DEMONSTRATION
# =============================================================================

def main() -> None:
    """Run all semantic types demonstrations."""
    print("FLEXT Semantic Types System - Practical Examples")
    print("=" * 60)
    print()
    
    demonstrate_core_functional_types()
    demonstrate_data_types()
    demonstrate_auth_types()
    demonstrate_observability_types()
    demonstrate_singer_types()
    demonstrate_project_extensions()
    demonstrate_protocol_integration()
    demonstrate_type_factories()
    demonstrate_flext_result_integration()
    
    print("=" * 60)
    print("All examples completed successfully!")
    print()
    print("Next Steps:")
    print("1. Explore the complete type system in semantic_types.py")
    print("2. Read the documentation: docs/FLEXT_SEMANTIC_TYPES_STANDARD.md")
    print("3. Create project-specific extensions following the patterns shown")
    print("4. Migrate existing code to use semantic types for better maintainability")

if __name__ == "__main__":
    main()