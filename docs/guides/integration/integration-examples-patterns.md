# 🔌 Integration Examples & Patterns

> **Function**: Comprehensive integration patterns for external systems | **Audience**: Integration engineers, developers | **Status**: ✅ Production Ready

[![Integration](https://img.shields.io/badge/integration-patterns-blue.svg)](./index.md)
[![Patterns](https://img.shields.io/badge/patterns-enterprise-green.svg)](../../architecture/patterns/index.md)
[![Examples](https://img.shields.io/badge/examples-validated-orange.svg)](../../examples/index.md)

**Complete guide to enterprise integration patterns with FLX Framework - validated against production implementations**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Guides](../index.md) → **📂 Section**: [Integration](./index.md) → **📄 Current**: Integration Patterns

---

## 🔗 **Cross-Section Navigation**

### **⬅️ Prerequisites**

- [Architecture Hub](../../architecture/index.md) - Essential understanding of hexagonal architecture and integration patterns
- [Getting Started Hub](../../getting-started/index.md) - FLX Framework installation and basic concepts required
- [API Reference Hub](../../api-reference/index.md) - Understanding adapter APIs and integration interfaces

### **➡️ Next Steps**

- [Oracle Integration Hub](../oracle/index.md) - Oracle-specific integration patterns and implementations
- [Examples Hub](../../examples/index.md) - Working code examples demonstrating integration patterns
- [Infrastructure Hub](../../infrastructure/index.md) - Production infrastructure for integration services

### **🔗 Related Topics**

- [Authentication Hub](../authentication/index.md) - Authentication patterns for external system integrations
- [Development Hub](../../development/index.md) - Testing strategies for integration code
- [Security Hub](../../security/index.md) - Security patterns for external integrations
- [Deployment Hub](../../deployment/index.md) - Production deployment patterns for integrated systems
- [Optimization Hub](../../optimization/index.md) - Performance optimization for high-volume integrations

## 🔌 Overview

FLX provides robust integration capabilities using proven enterprise integration patterns to connect with various external systems while maintaining loose coupling and high reliability.

### **Supported Integration Patterns**

- **🌐 API Integration**: REST, GraphQL, gRPC, and WebSocket APIs
- **📬 Message Queues**: Asynchronous messaging with various brokers
- **💾 Database Integration**: Multi-database support with connection pooling
- **📁 File Processing**: Batch file processing and ETL pipelines
- **☁️ Cloud Services**: Native cloud provider integrations
- **🔄 Real-time Streaming**: Event streams and real-time data processing

## 🌐 API Integration Patterns

### **REST API Client**

```python
# flext/integrations/rest_client.py
from flext.adapters.outbound.http_client import HTTPClientAdapter
from flext.core.integration import APIClient, RateLimiter, CircuitBreaker

class RestAPIClient(APIClient):
    """Enterprise REST API client with resilience patterns."""

    def __init__(self, base_url: str, api_key: str = None, **config):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key

        # Initialize resilience components
        self.rate_limiter = RateLimiter(
            max_requests=config.get('rate_limit', 100),
            time_window=config.get('rate_window', 60)
        )

        self.circuit_breaker = CircuitBreaker(
            failure_threshold=config.get('failure_threshold', 5),
            recovery_timeout=config.get('recovery_timeout', 60)
        )

        # HTTP client configuration
        self.http_client = HTTPClientAdapter(
            timeout=config.get('timeout', 30),
            retries=config.get('retries', 3),
            backoff_factor=config.get('backoff_factor', 0.3)
        )

        # Authentication configuration
        self.auth_config = config.get('auth', {})

    async def authenticate(self) -> dict[str, str]:
        """Authenticate and return headers."""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'

        # OAuth 2.0 authentication
        if self.auth_config.get('type') == 'oauth2':
            access_token = await self._get_oauth_token()
            headers['Authorization'] = f'Bearer {access_token}'

        # Custom authentication
        elif self.auth_config.get('type') == 'custom':
            custom_headers = await self._get_custom_auth_headers()
            headers.update(custom_headers)

        return headers

    async def get(self, endpoint: str, params: dict = None, **kwargs) -> dict:
        """GET request with resilience patterns."""
        return await self._request('GET', endpoint, params=params, **kwargs)

    async def post(self, endpoint: str, data: dict = None, **kwargs) -> dict:
        """POST request with resilience patterns."""
        return await self._request('POST', endpoint, json=data, **kwargs)

    async def put(self, endpoint: str, data: dict = None, **kwargs) -> dict:
        """PUT request with resilience patterns."""
        return await self._request('PUT', endpoint, json=data, **kwargs)

    async def delete(self, endpoint: str, **kwargs) -> dict:
        """DELETE request with resilience patterns."""
        return await self._request('DELETE', endpoint, **kwargs)

    async def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Execute HTTP request with resilience patterns."""
        # Apply rate limiting
        await self.rate_limiter.acquire()

        # Check circuit breaker
        if not self.circuit_breaker.can_execute():
            raise CircuitBreakerOpenError("Circuit breaker is open")

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            # Get authentication headers
            headers = await self.authenticate()
            if 'headers' in kwargs:
                headers.update(kwargs['headers'])
            kwargs['headers'] = headers

            # Execute request
            response = await self.http_client.request(method, url, **kwargs)

            # Record success
            self.circuit_breaker.record_success()

            return response

        except Exception as e:
            # Record failure
            self.circuit_breaker.record_failure()
            raise APIIntegrationError(f"API request failed: {str(e)}") from e

    async def _get_oauth_token(self) -> str:
        """Get OAuth 2.0 access token."""
        token_url = self.auth_config['token_url']
        client_id = self.auth_config['client_id']
        client_secret = self.auth_config['client_secret']

        # Check cache for existing token
        cache_key = f"oauth_token:{client_id}"
        cached_token = await self.cache.get(cache_key)
        if cached_token:
            return cached_token

        # Request new token
        auth_data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        }

        if 'scope' in self.auth_config:
            auth_data['scope'] = self.auth_config['scope']

        response = await self.http_client.post(
            token_url,
            data=auth_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

        access_token = response['access_token']
        expires_in = response.get('expires_in', 3600)

        # Cache token with 10% buffer before expiration
        cache_ttl = int(expires_in * 0.9)
        await self.cache.set(cache_key, access_token, ttl=cache_ttl)

        return access_token

# Specific API Integration Examples
class CRMIntegration(RestAPIClient):
    """CRM system integration."""

    def __init__(self, config: dict):
        super().__init__(**config)
        self.organization_id = config.get('organization_id')

    async def create_customer(self, customer_data: dict) -> dict:
        """Create customer in CRM."""
        payload = {
            'organization_id': self.organization_id,
            'customer': {
                'first_name': customer_data['first_name'],
                'last_name': customer_data['last_name'],
                'email': customer_data['email'],
                'phone': customer_data.get('phone'),
                'company': customer_data.get('company'),
                'custom_fields': customer_data.get('custom_fields', {})
            }
        }

        response = await self.post('/customers', payload)
        return {
            'external_id': response['id'],
            'crm_url': response['url'],
            'created_at': response['created_at']
        }

    async def update_customer(self, external_id: str, updates: dict) -> dict:
        """Update customer in CRM."""
        response = await self.put(f'/customers/{external_id}', updates)
        return {
            'external_id': response['id'],
            'updated_at': response['updated_at']
        }

    async def get_customer_activities(self, external_id: str) -> list[dict]:
        """Get customer activities from CRM."""
        response = await self.get(f'/customers/{external_id}/activities')
        return response.get('activities', [])

class PaymentGatewayIntegration(RestAPIClient):
    """Payment gateway integration."""

    async def process_payment(self, payment_data: dict) -> dict:
        """Process payment through gateway."""
        payload = {
            'amount': payment_data['amount'],
            'currency': payment_data['currency'],
            'payment_method': payment_data['payment_method'],
            'customer_id': payment_data['customer_id'],
            'description': payment_data.get('description'),
            'metadata': payment_data.get('metadata', {})
        }

        response = await self.post('/payments', payload)

        return {
            'transaction_id': response['id'],
            'status': response['status'],
            'amount_captured': response.get('amount_captured'),
            'fees': response.get('fees'),
            'created_at': response['created_at']
        }

    async def refund_payment(self, transaction_id: str, amount: float = None) -> dict:
        """Refund payment."""
        payload = {'amount': amount} if amount else {}

        response = await self.post(f'/payments/{transaction_id}/refunds', payload)

        return {
            'refund_id': response['id'],
            'amount_refunded': response['amount'],
            'status': response['status'],
            'created_at': response['created_at']
        }
```

### **GraphQL Client**

```python
# flext/integrations/graphql_client.py
from flext.core.integration import GraphQLClient

class FLXGraphQLClient(GraphQLClient):
    """GraphQL client with advanced features."""

    def __init__(self, endpoint: str, **config):
        super().__init__(endpoint, **config)
        self.query_cache = {}
        self.subscription_handlers = {}

    async def query(self, query: str, variables: dict = None,
                   use_cache: bool = True) -> dict:
        """Execute GraphQL query with caching."""
        # Generate cache key
        cache_key = self._generate_cache_key(query, variables)

        # Check cache
        if use_cache and cache_key in self.query_cache:
            return self.query_cache[cache_key]

        # Execute query
        response = await self._execute_request({
            'query': query,
            'variables': variables or {}
        })

        # Cache successful responses
        if use_cache and 'errors' not in response:
            self.query_cache[cache_key] = response

        return response

    async def mutation(self, mutation: str, variables: dict = None) -> dict:
        """Execute GraphQL mutation."""
        return await self._execute_request({
            'query': mutation,
            'variables': variables or {}
        })

    async def subscribe(self, subscription: str, variables: dict = None,
                       handler: callable = None) -> str:
        """Subscribe to GraphQL subscription."""
        subscription_id = self._generate_subscription_id()

        # Store handler
        if handler:
            self.subscription_handlers[subscription_id] = handler

        # Start subscription (WebSocket connection)
        await self._start_subscription(subscription_id, subscription, variables)

        return subscription_id

    async def unsubscribe(self, subscription_id: str) -> None:
        """Unsubscribe from GraphQL subscription."""
        await self._stop_subscription(subscription_id)
        self.subscription_handlers.pop(subscription_id, None)

    def build_query(self, operation_name: str, fields: list[str],
                   arguments: dict = None) -> str:
        """Build GraphQL query dynamically."""
        args_str = ""
        if arguments:
            args_list = [f"{k}: {self._format_argument(v)}"
                        for k, v in arguments.items()]
            args_str = f"({', '.join(args_list)})"

        fields_str = ", ".join(fields)

        return f"""
        query {{
            {operation_name}{args_str} {{
                {fields_str}
            }}
        }}
        """

    def build_mutation(self, operation_name: str, input_data: dict,
                      return_fields: list[str]) -> str:
        """Build GraphQL mutation dynamically."""
        input_str = self._format_input_object(input_data)
        fields_str = ", ".join(return_fields)

        return f"""
        mutation {{
            {operation_name}(input: {input_str}) {{
                {fields_str}
            }}
        }}
        """

# GraphQL Integration Example
class ContentManagementIntegration(FLXGraphQLClient):
    """Content management system GraphQL integration."""

    async def get_articles(self, category: str = None, limit: int = 10) -> list[dict]:
        """Get articles from CMS."""
        query = self.build_query(
            operation_name="articles",
            fields=[
                "id", "title", "slug", "content", "author { name, email }",
                "category { name, slug }", "publishedAt", "tags"
            ],
            arguments={
                "category": category,
                "limit": limit,
                "status": "PUBLISHED"
            }
        )

        response = await self.query(query)
        return response['data']['articles']

    async def create_article(self, article_data: dict) -> dict:
        """Create article in CMS."""
        mutation = self.build_mutation(
            operation_name="createArticle",
            input_data=article_data,
            return_fields=["id", "title", "slug", "status", "publishedAt"]
        )

        response = await self.mutation(mutation)
        return response['data']['createArticle']

    async def subscribe_to_article_updates(self, handler: callable) -> str:
        """Subscribe to real-time article updates."""
        subscription = """
        subscription {
            articleUpdated {
                id
                title
                status
                updatedAt
                author { name }
            }
        }
        """

        return await self.subscribe(subscription, handler=handler)
```

## 📬 Message Queue Integration

### **Message Broker Adapter**

```python
# flext/integrations/message_brokers.py
from flext.adapters.outbound.message_queue import MessageQueueAdapter
from flext.core.events import EventBus, DomainEvent

class RabbitMQAdapter(MessageQueueAdapter):
    """RabbitMQ message broker adapter."""

    def __init__(self, connection_url: str, **config):
        super().__init__(name="rabbitmq")
        self.connection_url = connection_url
        self.exchange_config = config.get('exchanges', {})
        self.queue_config = config.get('queues', {})
        self.connection = None
        self.channel = None

    async def _connect(self) -> None:
        """Connect to RabbitMQ."""
        import aio_pika

        self.connection = await aio_pika.connect_robust(self.connection_url)
        self.channel = await self.connection.channel()

        # Setup exchanges and queues
        await self._setup_topology()

    async def _disconnect(self) -> None:
        """Disconnect from RabbitMQ."""
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()

    async def _setup_topology(self) -> None:
        """Setup exchanges, queues, and bindings."""
        # Create exchanges
        for exchange_name, config in self.exchange_config.items():
            await self.channel.declare_exchange(
                exchange_name,
                type=config.get('type', 'topic'),
                durable=config.get('durable', True),
                auto_delete=config.get('auto_delete', False)
            )

        # Create queues
        for queue_name, config in self.queue_config.items():
            queue = await self.channel.declare_queue(
                queue_name,
                durable=config.get('durable', True),
                exclusive=config.get('exclusive', False),
                auto_delete=config.get('auto_delete', False),
                arguments=config.get('arguments', {})
            )

            # Bind queue to exchanges
            for binding in config.get('bindings', []):
                await queue.bind(
                    exchange=binding['exchange'],
                    routing_key=binding.get('routing_key', '#')
                )

    async def publish_message(self, exchange: str, routing_key: str,
                            message: dict, **options) -> None:
        """Publish message to exchange."""
        import aio_pika

        message_body = json.dumps(message).encode()

        # Create message with properties
        amqp_message = aio_pika.Message(
            message_body,
            delivery_mode=options.get('delivery_mode', 2),  # Persistent
            priority=options.get('priority', 0),
            expiration=options.get('expiration'),
            message_id=options.get('message_id'),
            correlation_id=options.get('correlation_id'),
            headers=options.get('headers', {})
        )

        # Get exchange
        exchange_obj = await self.channel.get_exchange(exchange)

        # Publish message
        await exchange_obj.publish(amqp_message, routing_key=routing_key)

    async def consume_messages(self, queue_name: str, handler: callable,
                             **options) -> None:
        """Consume messages from queue."""
        queue = await self.channel.get_queue(queue_name)

        async def message_handler(message):
            async with message.process():
                try:
                    # Decode message
                    message_data = json.loads(message.body.decode())

                    # Call handler
                    await handler(message_data, message)

                except Exception as e:
                    # Handle processing error
                    await self._handle_message_error(message, e)
                    raise

        # Start consuming
        await queue.consume(
            message_handler,
            consumer_tag=options.get('consumer_tag'),
            no_ack=options.get('no_ack', False),
            exclusive=options.get('exclusive', False)
        )

# Event Bus Integration
class EventDrivenIntegration:
    """Event-driven integration with external systems."""

    def __init__(self, event_bus: EventBus, message_broker: MessageQueueAdapter):
        self.event_bus = event_bus
        self.message_broker = message_broker
        self.event_mappings = {}

    async def setup_event_publishing(self) -> None:
        """Setup automatic event publishing to message broker."""

        # Subscribe to all domain events
        @self.event_bus.subscribe("*")
        async def publish_to_broker(event: DomainEvent) -> None:
            """Publish domain event to message broker."""
            event_type = event.__class__.__name__

            # Check if event should be published externally
            if event_type in self.event_mappings:
                mapping = self.event_mappings[event_type]

                # Transform event data
                message_data = await self._transform_event(event, mapping)

                # Publish to broker
                await self.message_broker.publish_message(
                    exchange=mapping['exchange'],
                    routing_key=mapping['routing_key'],
                    message=message_data,
                    headers={
                        'event_type': event_type,
                        'source_service': 'flext-application',
                        'correlation_id': str(event.event_id)
                    }
                )

    async def setup_event_consumption(self) -> None:
        """Setup consumption of external events."""

        # Consume customer events from CRM
        await self.message_broker.consume_messages(
            queue_name="crm_customer_events",
            handler=self._handle_crm_customer_event
        )

        # Consume payment events from payment service
        await self.message_broker.consume_messages(
            queue_name="payment_events",
            handler=self._handle_payment_event
        )

    async def _handle_crm_customer_event(self, message_data: dict, message) -> None:
        """Handle customer event from CRM."""
        event_type = message_data.get('event_type')

        if event_type == 'customer.profile_updated':
            # Create internal domain event
            customer_updated_event = ExternalCustomerUpdated(
                external_customer_id=message_data['customer_id'],
                updated_fields=message_data['updated_fields'],
                source_system='crm',
                occurred_at=datetime.fromisoformat(message_data['occurred_at'])
            )

            # Publish to internal event bus
            await self.event_bus.publish(customer_updated_event)

    async def _handle_payment_event(self, message_data: dict, message) -> None:
        """Handle payment event from payment service."""
        event_type = message_data.get('event_type')

        if event_type == 'payment.completed':
            # Create internal domain event
            payment_completed_event = ExternalPaymentCompleted(
                payment_id=message_data['payment_id'],
                customer_id=message_data['customer_id'],
                amount=message_data['amount'],
                currency=message_data['currency'],
                occurred_at=datetime.fromisoformat(message_data['occurred_at'])
            )

            # Publish to internal event bus
            await self.event_bus.publish(payment_completed_event)

    def register_event_mapping(self, event_type: str, exchange: str,
                              routing_key: str, transformer: callable = None) -> None:
        """Register event mapping for external publishing."""
        self.event_mappings[event_type] = {
            'exchange': exchange,
            'routing_key': routing_key,
            'transformer': transformer
        }

    async def _transform_event(self, event: DomainEvent, mapping: dict) -> dict:
        """Transform domain event for external consumption."""
        if mapping.get('transformer'):
            return await mapping['transformer'](event)

        # Default transformation
        return {
            'event_id': str(event.event_id),
            'event_type': event.__class__.__name__,
            'occurred_at': event.occurred_at.isoformat(),
            'data': event.dict()
        }
```

## 💾 Database Integration Patterns

### **Multi-Database Support**

```python
# flext/integrations/multi_database.py
from flext.adapters.outbound.database import DatabaseAdapter

class MultiDatabaseManager:
    """Manager for multiple database connections."""

    def __init__(self):
        self.databases: dict[str, DatabaseAdapter] = {}
        self.read_replicas: dict[str, list[DatabaseAdapter]] = {}
        self.write_databases: dict[str, DatabaseAdapter] = {}

    async def register_database(self, name: str, database: DatabaseAdapter,
                              role: str = 'readwrite') -> None:
        """Register database with specific role."""
        await database.connect()

        self.databases[name] = database

        if role in ['readwrite', 'write']:
            self.write_databases[name] = database

        if role in ['readwrite', 'read']:
            if name not in self.read_replicas:
                self.read_replicas[name] = []
            self.read_replicas[name].append(database)

    async def get_read_database(self, name: str) -> DatabaseAdapter:
        """Get read database (with load balancing for replicas)."""
        if name not in self.read_replicas:
            raise DatabaseNotFoundError(f"No read database found for {name}")

        replicas = self.read_replicas[name]

        # Simple round-robin load balancing
        import random
        return random.choice(replicas)

    async def get_write_database(self, name: str) -> DatabaseAdapter:
        """Get write database."""
        if name not in self.write_databases:
            raise DatabaseNotFoundError(f"No write database found for {name}")

        return self.write_databases[name]

    async def execute_read_query(self, database_name: str, query: str,
                               parameters: list = None) -> list[dict]:
        """Execute read query with replica routing."""
        db = await self.get_read_database(database_name)
        return await db.fetch_all(query, parameters)

    async def execute_write_query(self, database_name: str, query: str,
                                parameters: list = None) -> dict:
        """Execute write query on primary database."""
        db = await self.get_write_database(database_name)
        return await db.execute(query, parameters)

    async def execute_distributed_transaction(self, operations: list[dict]) -> None:
        """Execute distributed transaction across multiple databases."""
        # Implement two-phase commit protocol
        transactions = {}

        try:
            # Phase 1: Prepare all transactions
            for operation in operations:
                db_name = operation['database']
                db = await self.get_write_database(db_name)

                transaction = await db.begin_transaction()
                transactions[db_name] = transaction

                # Execute operation in transaction
                await transaction.execute(
                    operation['query'],
                    operation.get('parameters')
                )

            # Phase 2: Commit all transactions
            for transaction in transactions.values():
                await transaction.commit()

        except Exception as e:
            # Rollback all transactions
            for transaction in transactions.values():
                try:
                    await transaction.rollback()
                except Exception:
                    pass  # Log rollback failures

            raise DistributedTransactionError(f"Transaction failed: {str(e)}")

# Database-specific integrations
class LegacyDatabaseIntegration:
    """Integration with legacy database systems."""

    def __init__(self, legacy_db: DatabaseAdapter):
        self.legacy_db = legacy_db
        self.field_mappings = {}
        self.table_mappings = {}

    async def sync_customer_data(self, customer: Customer) -> None:
        """Sync customer data with legacy system."""
        # Map modern customer to legacy format
        legacy_customer = await self._map_customer_to_legacy(customer)

        # Check if customer exists in legacy system
        existing = await self.legacy_db.fetch_one(
            "SELECT customer_id FROM legacy_customers WHERE external_id = ?",
            [str(customer.id)]
        )

        if existing:
            # Update existing customer
            await self._update_legacy_customer(
                existing['customer_id'],
                legacy_customer
            )
        else:
            # Create new customer in legacy system
            await self._create_legacy_customer(legacy_customer)

    async def _map_customer_to_legacy(self, customer: Customer) -> dict:
        """Map modern customer to legacy format."""
        return {
            'external_id': str(customer.id),
            'first_name': customer.personal_info.first_name,
            'last_name': customer.personal_info.last_name,
            'email_address': customer.contact_info.email if customer.contact_info else None,
            'phone_number': customer.contact_info.phone if customer.contact_info else None,
            'status_code': 'A' if customer.status == CustomerStatus.ACTIVE else 'I',
            'created_date': customer.registration_date,
            'last_modified': datetime.utcnow()
        }

    async def _create_legacy_customer(self, customer_data: dict) -> None:
        """Create customer in legacy system."""
        query = """
        INSERT INTO legacy_customers (
            external_id, first_name, last_name, email_address,
            phone_number, status_code, created_date, last_modified
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        await self.legacy_db.execute(query, [
            customer_data['external_id'],
            customer_data['first_name'],
            customer_data['last_name'],
            customer_data['email_address'],
            customer_data['phone_number'],
            customer_data['status_code'],
            customer_data['created_date'],
            customer_data['last_modified']
        ])

    async def _update_legacy_customer(self, customer_id: int, customer_data: dict) -> None:
        """Update customer in legacy system."""
        query = """
        UPDATE legacy_customers
        SET first_name = ?, last_name = ?, email_address = ?,
            phone_number = ?, status_code = ?, last_modified = ?
        WHERE customer_id = ?
        """

        await self.legacy_db.execute(query, [
            customer_data['first_name'],
            customer_data['last_name'],
            customer_data['email_address'],
            customer_data['phone_number'],
            customer_data['status_code'],
            customer_data['last_modified'],
            customer_id
        ])
```

## 📁 File Processing Integration

### **ETL Pipeline**

```python
# flext/integrations/etl_pipeline.py
from flext.core.processing import ETLPipeline, Extractor, Transformer, Loader

class CustomerDataETL(ETLPipeline):
    """ETL pipeline for customer data processing."""

    def __init__(self, source_config: dict, target_config: dict):
        self.extractor = self._create_extractor(source_config)
        self.transformer = CustomerDataTransformer()
        self.loader = self._create_loader(target_config)

    def _create_extractor(self, config: dict) -> Extractor:
        """Create data extractor based on source type."""
        source_type = config['type']

        if source_type == 'csv':
            return CSVExtractor(
                file_path=config['file_path'],
                delimiter=config.get('delimiter', ','),
                encoding=config.get('encoding', 'utf-8')
            )
        elif source_type == 'json':
            return JSONExtractor(file_path=config['file_path'])
        elif source_type == 'database':
            return DatabaseExtractor(
                database=config['database'],
                query=config['query']
            )
        elif source_type == 'api':
            return APIExtractor(
                endpoint=config['endpoint'],
                auth_config=config.get('auth', {})
            )
        else:
            raise ValueError(f"Unsupported source type: {source_type}")

    def _create_loader(self, config: dict) -> Loader:
        """Create data loader based on target type."""
        target_type = config['type']

        if target_type == 'database':
            return DatabaseLoader(
                database=config['database'],
                table=config['table']
            )
        elif target_type == 'file':
            return FileLoader(
                file_path=config['file_path'],
                format=config.get('format', 'json')
            )
        elif target_type == 'api':
            return APILoader(
                endpoint=config['endpoint'],
                auth_config=config.get('auth', {})
            )
        else:
            raise ValueError(f"Unsupported target type: {target_type}")

    async def process(self) -> ETLResult:
        """Execute ETL pipeline."""
        result = ETLResult()

        try:
            # Extract data
            raw_data = await self.extractor.extract()
            result.extracted_count = len(raw_data)

            # Transform data
            transformed_data = []
            errors = []

            for record in raw_data:
                try:
                    transformed_record = await self.transformer.transform(record)
                    transformed_data.append(transformed_record)
                except TransformationError as e:
                    errors.append({
                        'record': record,
                        'error': str(e)
                    })

            result.transformed_count = len(transformed_data)
            result.transformation_errors = errors

            # Load data
            load_result = await self.loader.load(transformed_data)
            result.loaded_count = load_result.success_count
            result.load_errors = load_result.errors

            result.status = 'completed' if not errors and not load_result.errors else 'completed_with_errors'

        except Exception as e:
            result.status = 'failed'
            result.error = str(e)

        return result

class CustomerDataTransformer(Transformer):
    """Transformer for customer data."""

    async def transform(self, record: dict) -> dict:
        """Transform raw customer record."""
        try:
            # Validate required fields
            self._validate_required_fields(record)

            # Normalize data
            transformed = {
                'customer_id': self._generate_customer_id(),
                'personal_info': {
                    'first_name': self._normalize_name(record.get('first_name')),
                    'last_name': self._normalize_name(record.get('last_name')),
                    'date_of_birth': self._parse_date(record.get('date_of_birth'))
                },
                'contact_info': {
                    'email': self._normalize_email(record.get('email')),
                    'phone': self._normalize_phone(record.get('phone'))
                },
                'addresses': self._transform_addresses(record.get('addresses', [])),
                'metadata': {
                    'source': record.get('source', 'import'),
                    'imported_at': datetime.utcnow().isoformat()
                }
            }

            # Apply business rules
            transformed = await self._apply_business_rules(transformed)

            return transformed

        except Exception as e:
            raise TransformationError(f"Failed to transform record: {str(e)}")

    def _validate_required_fields(self, record: dict) -> None:
        """Validate required fields are present."""
        required_fields = ['first_name', 'last_name', 'email']

        for field in required_fields:
            if not record.get(field):
                raise ValidationError(f"Missing required field: {field}")

    def _normalize_name(self, name: str) -> str:
        """Normalize name field."""
        if not name:
            return ""

        return name.strip().title()

    def _normalize_email(self, email: str) -> str:
        """Normalize email field."""
        if not email:
            raise ValidationError("Email is required")

        email = email.strip().lower()

        # Validate email format
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError(f"Invalid email format: {email}")

        return email

    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number."""
        if not phone:
            return ""

        # Remove all non-digit characters
        import re
        digits_only = re.sub(r'[^\d]', '', phone)

        # Format based on length (assuming US format)
        if len(digits_only) == 10:
            return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
        elif len(digits_only) == 11 and digits_only[0] == '1':
            return f"1-({digits_only[1:4]}) {digits_only[4:7]}-{digits_only[7:]}"
        else:
            return phone  # Return original if can't format

    async def _apply_business_rules(self, record: dict) -> dict:
        """Apply business rules to transformed record."""
        # Example: Set customer status based on email domain
        email = record['contact_info']['email']
        domain = email.split('@')[1] if '@' in email else ''

        # Company domains get VIP status
        vip_domains = ['company.com', 'enterprise.com']
        if domain in vip_domains:
            record['status'] = 'vip'
        else:
            record['status'] = 'regular'

        # Add customer segment based on data
        record['segment'] = await self._determine_customer_segment(record)

        return record

    async def _determine_customer_segment(self, record: dict) -> str:
        """Determine customer segment based on data."""
        # Simple segmentation logic
        email_domain = record['contact_info']['email'].split('@')[1]

        if email_domain.endswith('.edu'):
            return 'education'
        elif email_domain.endswith('.gov'):
            return 'government'
        elif email_domain.endswith('.org'):
            return 'nonprofit'
        else:
            return 'commercial'

# File Processing Adapters
class CSVExtractor(Extractor):
    """Extract data from CSV files."""

    def __init__(self, file_path: str, delimiter: str = ',', encoding: str = 'utf-8'):
        self.file_path = file_path
        self.delimiter = delimiter
        self.encoding = encoding

    async def extract(self) -> list[dict]:
        """Extract data from CSV file."""
        import csv
        import aiofiles

        records = []

        async with aiofiles.open(self.file_path, 'r', encoding=self.encoding) as file:
            content = await file.read()

            # Process CSV in memory (for large files, consider streaming)
            csv_reader = csv.DictReader(
                content.splitlines(),
                delimiter=self.delimiter
            )

            for row in csv_reader:
                records.append(dict(row))

        return records

class DatabaseLoader(Loader):
    """Load data into database."""

    def __init__(self, database: DatabaseAdapter, table: str):
        self.database = database
        self.table = table

    async def load(self, records: list[dict]) -> LoadResult:
        """Load records into database."""
        result = LoadResult()

        async with self.database.transaction() as tx:
            for record in records:
                try:
                    # Generate insert query
                    columns = list(record.keys())
                    placeholders = ', '.join(['?' for _ in columns])
                    values = [record[col] for col in columns]

                    query = f"""
                    INSERT INTO {self.table} ({', '.join(columns)})
                    VALUES ({placeholders})
                    """

                    await tx.execute(query, values)
                    result.success_count += 1

                except Exception as e:
                    result.errors.append({
                        'record': record,
                        'error': str(e)
                    })

        return result
```

---

**🔌 Your FLX application now supports comprehensive integration patterns for connecting with external systems, APIs, databases, and message brokers!**

---

**📄 Content Document** | **🏠 Parent**: [Integration Hub](./index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
