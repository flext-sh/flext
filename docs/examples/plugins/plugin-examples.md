# FLX Plugin Examples

Comprehensive examples demonstrating plugin development patterns and custom protocol implementations for the FLX hexagonal architecture framework.

## Overview

This directory contains practical examples of how to develop plugins for the FLX framework, including custom protocol implementations, bidirectional adapters, and integration patterns. These examples demonstrate the extensibility and flexibility of the FLX plugin system.

## Plugin Architecture

FLX plugins follow the hexagonal architecture pattern, allowing them to act as both inbound and outbound adapters while maintaining clean separation of concerns:

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Application       │◄───┤    Plugin System     ├───►│   External Systems  │
│   Core              │    │   • Registration     │    │   • APIs            │
└─────────────────────┘    │   • Lifecycle Mgmt   │    │   • Databases       │
           │                │   • Event Routing    │    │   • Message Queues  │
           ▼                └──────────────────────┘    └─────────────────────┘
┌─────────────────────┐              │
│   Plugin            │              ▼
│   Interfaces        │    ┌──────────────────────┐
│   • Discovery       │    │   Custom Protocols   │
│   • Configuration   │    │   • HTTP Extensions  │
│   • Health Checks   │    │   • Binary Protocols │
│   • Metrics         │    │   • Streaming APIs   │
└─────────────────────┘    └──────────────────────┘
```

## Available Examples

### Custom Protocol Plugin (`custom_protocol.py`)

**Purpose**: Demonstrates how to implement a custom communication protocol that can be used as both an inbound and outbound adapter.

**Key Features:**

- Binary protocol implementation with custom message framing
- Bidirectional communication support
- Connection pooling and management
- Error handling and reconnection logic
- Protocol versioning and negotiation

**Example Protocol Specification:**

```
Message Format:
┌─────────────┬─────────────┬─────────────┬─────────────┐
│   Header    │   Version   │   Length    │   Payload   │
│  (4 bytes)  │  (2 bytes)  │  (4 bytes)  │ (variable)  │
└─────────────┴─────────────┴─────────────┴─────────────┘

Header: 0x464C5800 (FLX\0)
Version: Protocol version (currently 0x0001)
Length: Payload length in bytes
Payload: JSON or binary data
```

**Usage Example:**

```python
from flext.examples.plugins.custom_protocol import CustomProtocolPlugin

# Initialize plugin
plugin = CustomProtocolPlugin({
    "server_host": "localhost",
    "server_port": 8080,
    "client_pool_size": 10,
    "reconnect_interval": 5.0,
    "message_timeout": 30.0
})

# Register as inbound adapter (server)
app.register_adapter("custom_server", plugin.create_server_adapter())

# Register as outbound adapter (client)
app.register_adapter("custom_client", plugin.create_client_adapter())

# Use in application code
async def handle_custom_request(request):
    # Process incoming request via custom protocol
    response_data = await process_business_logic(request.data)

    # Send response back via custom protocol
    await plugin.send_response(request.connection_id, response_data)
```

**Protocol Implementation Details:**

#### Server Side (Inbound Adapter)

```python
class CustomProtocolServerAdapter(BaseAdapter):
    """Inbound adapter for custom protocol server."""

    async def start(self) -> None:
        """Start the protocol server."""
        self.server = await asyncio.start_server(
            self._handle_connection,
            self.config.host,
            self.config.port
        )
        self.logger.info(f"Custom protocol server listening on {self.config.host}:{self.config.port}")

    async def _handle_connection(self, reader: StreamReader, writer: StreamWriter) -> None:
        """Handle incoming connection."""
        connection_id = self._generate_connection_id()

        try:
            while True:
                # Read message header
                header = await reader.read(10)  # 4 + 2 + 4 bytes
                if not header:
                    break

                # Parse header
                magic, version, length = struct.unpack('!IHI', header)

                if magic != 0x464C5800:
                    raise ProtocolError("Invalid magic number")

                if version != 0x0001:
                    raise ProtocolError(f"Unsupported version: {version}")

                # Read payload
                payload = await reader.read(length)

                # Process message
                message = self._decode_payload(payload)
                response = await self._process_message(message)

                # Send response
                await self._send_response(writer, response)

        except Exception as e:
            self.logger.error(f"Connection {connection_id} error: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
```

#### Client Side (Outbound Adapter)

```python
class CustomProtocolClientAdapter(BaseAdapter):
    """Outbound adapter for custom protocol client."""

    async def connect(self) -> None:
        """Establish connection to server."""
        self.reader, self.writer = await asyncio.open_connection(
            self.config.host,
            self.config.port
        )
        self.logger.info(f"Connected to {self.config.host}:{self.config.port}")

    async def send_message(self, message: dict) -> dict:
        """Send message and wait for response."""
        # Encode message
        payload = self._encode_payload(message)

        # Create header
        header = struct.pack('!IHI', 0x464C5800, 0x0001, len(payload))

        # Send message
        self.writer.write(header + payload)
        await self.writer.drain()

        # Read response
        response_header = await self.reader.read(10)
        magic, version, length = struct.unpack('!IHI', response_header)

        response_payload = await self.reader.read(length)
        return self._decode_payload(response_payload)
```

### Advanced Plugin Patterns

#### Plugin with State Management

```python
class StatefulPlugin(BasePlugin):
    """Plugin that maintains state across requests."""

    def __init__(self, config: dict):
        super().__init__(config)
        self.state_store = {}
        self.locks = {}

    async def process_with_state(self, key: str, operation: callable):
        """Process operation with state isolation."""
        # Acquire per-key lock
        if key not in self.locks:
            self.locks[key] = asyncio.Lock()

        async with self.locks[key]:
            # Get current state
            current_state = self.state_store.get(key, {})

            # Execute operation
            new_state = await operation(current_state)

            # Update state
            self.state_store[key] = new_state

            return new_state
```

#### Plugin with Event Integration

```python
class EventDrivenPlugin(BasePlugin):
    """Plugin that integrates with the FLX event system."""

    async def initialize(self, event_bus: EventBus) -> None:
        """Initialize plugin with event bus integration."""
        self.event_bus = event_bus

        # Subscribe to relevant events
        await self.event_bus.subscribe("user.created", self._handle_user_created)
        await self.event_bus.subscribe("order.placed", self._handle_order_placed)

    async def _handle_user_created(self, event: DomainEvent) -> None:
        """Handle user creation event."""
        user_data = event.data

        # Perform plugin-specific logic
        await self._sync_user_to_external_system(user_data)

        # Emit follow-up event
        await self.event_bus.publish(DomainEvent(
            event_type="user.synced",
            aggregate_id=user_data["id"],
            data={"external_id": external_id}
        ))
```

#### Plugin with Health Monitoring

```python
class MonitorablePlugin(BasePlugin):
    """Plugin with comprehensive health monitoring."""

    def __init__(self, config: dict):
        super().__init__(config)
        self.metrics = {
            "requests_total": 0,
            "requests_failed": 0,
            "connection_pool_size": 0,
            "last_health_check": None
        }

    async def health_check(self) -> HealthStatus:
        """Perform comprehensive health check."""
        checks = []

        # Check external connectivity
        connectivity_check = await self._check_external_connectivity()
        checks.append(connectivity_check)

        # Check resource usage
        resource_check = await self._check_resource_usage()
        checks.append(resource_check)

        # Check error rates
        error_rate_check = await self._check_error_rates()
        checks.append(error_rate_check)

        # Aggregate results
        overall_status = "healthy" if all(c.status == "healthy" for c in checks) else "unhealthy"

        return HealthStatus(
            status=overall_status,
            checks=checks,
            metrics=self.metrics.copy(),
            timestamp=datetime.utcnow()
        )
```

### Plugin Configuration Examples

#### YAML Configuration

```yaml
# plugins.yaml
plugins:
  custom_protocol:
    enabled: true
    config:
      server:
        host: "0.0.0.0"
        port: 8080
        max_connections: 100
        timeout: 30
      client:
        host: "api.example.com"
        port: 8080
        pool_size: 10
        reconnect_interval: 5.0
        request_timeout: 30.0

  external_api:
    enabled: true
    config:
      base_url: "https://api.external.com"
      api_key: "${EXTERNAL_API_KEY}"
      rate_limit: 100
      retry_attempts: 3

  message_queue:
    enabled: false # Can be disabled
    config:
      provider: "redis"
      connection_string: "redis://localhost:6379"
      queue_prefix: "flext"
```

#### Python Configuration

```python
# Dynamic plugin configuration
plugin_configs = {
    "custom_protocol": {
        "enabled": os.getenv("CUSTOM_PROTOCOL_ENABLED", "true").lower() == "true",
        "config": {
            "server": {
                "host": os.getenv("CUSTOM_PROTOCOL_HOST", "0.0.0.0"),
                "port": int(os.getenv("CUSTOM_PROTOCOL_PORT", "8080")),
                "max_connections": int(os.getenv("MAX_CONNECTIONS", "100")),
            }
        }
    }
}

# Register plugins with dynamic configuration
for plugin_name, plugin_config in plugin_configs.items():
    if plugin_config["enabled"]:
        plugin_class = import_plugin(plugin_name)
        plugin_instance = plugin_class(plugin_config["config"])
        app.register_plugin(plugin_name, plugin_instance)
```

### Testing Plugin Examples

#### Unit Testing

```python
import pytest
from flext.examples.plugins.custom_protocol import CustomProtocolPlugin

class TestCustomProtocolPlugin:

    @pytest.fixture
    async def plugin(self):
        config = {
            "server_host": "localhost",
            "server_port": 0,  # Use random port for testing
            "client_pool_size": 1,
        }
        plugin = CustomProtocolPlugin(config)
        await plugin.initialize()
        yield plugin
        await plugin.cleanup()

    async def test_message_encoding_decoding(self, plugin):
        """Test message encoding and decoding."""
        original_message = {"type": "test", "data": {"key": "value"}}

        encoded = plugin._encode_payload(original_message)
        decoded = plugin._decode_payload(encoded)

        assert decoded == original_message

    async def test_connection_handling(self, plugin):
        """Test connection lifecycle."""
        client_adapter = plugin.create_client_adapter()

        # Test connection
        await client_adapter.connect()
        assert client_adapter.is_connected()

        # Test message sending
        response = await client_adapter.send_message({"ping": True})
        assert response["pong"] is True

        # Test disconnection
        await client_adapter.disconnect()
        assert not client_adapter.is_connected()
```

#### Integration Testing

```python
async def test_plugin_integration():
    """Test plugin integration with FLX application."""
    app = create_test_application()

    # Register plugin
    plugin = CustomProtocolPlugin(test_config)
    app.register_plugin("custom_protocol", plugin)

    # Start application
    async with app:
        # Test inbound functionality
        client = create_test_client(app.get_plugin_endpoint("custom_protocol"))
        response = await client.send_message({"action": "test"})
        assert response["status"] == "success"

        # Test outbound functionality
        external_service = app.get_adapter("custom_protocol_client")
        result = await external_service.call_external_api({"data": "test"})
        assert result is not None
```

### Performance Optimization

#### Connection Pooling

```python
class OptimizedProtocolPlugin(BasePlugin):
    """Plugin with optimized connection management."""

    def __init__(self, config: dict):
        super().__init__(config)
        self.connection_pool = asyncio.Queue(maxsize=config["pool_size"])
        self.pool_lock = asyncio.Lock()

    async def get_connection(self) -> Connection:
        """Get connection from pool or create new one."""
        try:
            # Try to get existing connection
            connection = self.connection_pool.get_nowait()
            if connection.is_healthy():
                return connection
        except asyncio.QueueEmpty:
            pass

        # Create new connection
        return await self._create_connection()

    async def return_connection(self, connection: Connection) -> None:
        """Return connection to pool."""
        if connection.is_healthy():
            try:
                self.connection_pool.put_nowait(connection)
            except asyncio.QueueFull:
                await connection.close()
        else:
            await connection.close()
```

#### Caching

```python
class CachingPlugin(BasePlugin):
    """Plugin with intelligent caching."""

    def __init__(self, config: dict):
        super().__init__(config)
        self.cache = {}
        self.cache_ttl = config.get("cache_ttl", 300)  # 5 minutes

    async def cached_operation(self, cache_key: str, operation: callable):
        """Perform operation with caching."""
        # Check cache
        if cache_key in self.cache:
            cached_item = self.cache[cache_key]
            if time.time() - cached_item["timestamp"] < self.cache_ttl:
                return cached_item["data"]

        # Execute operation
        result = await operation()

        # Cache result
        self.cache[cache_key] = {
            "data": result,
            "timestamp": time.time()
        }

        return result
```

## Best Practices

### Plugin Development Guidelines

1. **Follow Hexagonal Architecture**

   - Implement clear port interfaces
   - Separate business logic from infrastructure concerns
   - Use dependency injection for external dependencies

2. **Error Handling**

   - Implement comprehensive error handling
   - Provide meaningful error messages
   - Support graceful degradation

3. **Configuration Management**

   - Use type-safe configuration classes
   - Support environment variable overrides
   - Validate configuration on startup

4. **Monitoring and Observability**

   - Implement health checks
   - Provide metrics and telemetry
   - Support distributed tracing

5. **Testing**
   - Write comprehensive unit tests
   - Include integration tests
   - Test error scenarios and edge cases

### Security Considerations

- **Input Validation**: Always validate and sanitize inputs
- **Authentication**: Implement proper authentication mechanisms
- **Encryption**: Use TLS/SSL for network communication
- **Secrets Management**: Use secure secret storage and rotation
- **Access Control**: Implement proper authorization checks

## TODO Items

- [ ] Add WebSocket protocol plugin example
- [ ] Create gRPC service plugin example
- [ ] Implement GraphQL plugin with federation support
- [ ] Add message queue integration plugin examples
- [ ] Create database migration plugin example
- [ ] Implement OAuth2 authentication plugin
- [ ] Add monitoring and alerting plugin examples
- [ ] Create plugin marketplace and discovery system

## Related Documentation

- [Plugin Architecture](../../infra/plugins/README.md) - Core plugin system
- [Adapter Patterns](../../adapters/README.md) - Adapter implementation patterns
- [Configuration Management](../../infra/config/README.md) - Configuration system
- [Testing Framework](../../testing/README.md) - Testing infrastructure
- [Deployment Guide](../../infra/deployment/README.md) - Plugin deployment strategies
