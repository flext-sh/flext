# Implementation Guide

> **tap-oic Version**: 2.0
> **Last Updated**: June 15, 2025

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [Implementation Patterns](#implementation-patterns)
4. [Stream Implementation](#stream-implementation)
5. [State Management](#state-management)
6. [Error Handling](#error-handling)
7. [Performance Optimization](#performance-optimization)
8. [Testing Strategies](#testing-strategies)
9. [Best Practices](#best-practices)

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                            tap-oic v2.0                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐   │
│  │   Discovery    │    │   Extraction   │    │   Management   │   │
│  │    Engine      │    │     Engine     │    │     Client     │   │
│  └────────────────┘    └────────────────┘    └────────────────┘   │
│           │                     │                      │            │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                    Stream Processors                        │   │
│  ├────────────────────────────────────────────────────────────┤   │
│  │ Integrations │ Connections │ Projects │ Metrics │ Lookups  │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                     OIC API Client                          │   │
│  ├────────────────────────────────────────────────────────────┤   │
│  │  OAuth2 │  Retry  │  Rate Limit  │  Pagination  │  Cache   │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                    Oracle Integration Cloud REST API
```

### Component Interactions

```python
# Main entry point flow
tap = TapOIC(config)
    ↓
catalog = tap.discover()  # Discovery Engine
    ↓
tap.sync(catalog)  # Extraction Engine
    ↓
for stream in selected_streams:
    stream_processor.sync()  # Stream Processors
        ↓
    oic_client.get_resources()  # OIC API Client
        ↓
    emit_records()  # Singer Output
```

## Core Components

### 1. OIC API Client

Base client for all OIC API interactions:

```python
from typing import Dict, Any, Optional, List
import requests
from urllib.parse import urljoin
from singer import get_logger

class OICClient:
    """Oracle Integration Cloud API Client"""

    def __init__(self, config: Dict[str, Any]):
        self.base_url = config['base_url']
        self.session = self._create_session(config)
        self.logger = get_logger()

    def _create_session(self, config: Dict[str, Any]) -> requests.Session:
        """Create HTTP session with OAuth2 authentication"""
        session = requests.Session()

        # OAuth2 authentication (OIC's recommended method)
        if config.get('auth_method', 'oauth2') == 'oauth2':
            token = self._get_oauth_token(config)
            session.headers['Authorization'] = f'Bearer {token}'

        # Common headers
        session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': config.get('user_agent', 'tap-oic/2.0')
        })

        # SSL verification
        session.verify = config.get('verify_ssl', True)

        return session

    def request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make API request with retry logic"""
        url = urljoin(self.base_url, endpoint)

        for attempt in range(self.max_retries):
            try:
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise
                self._handle_retry(e, attempt)

    def paginate(
        self,
        endpoint: str,
        params: Optional[Dict] = None
    ) -> Iterator[Dict[str, Any]]:
        """Handle pagination automatically"""
        params = params or {}
        params['limit'] = self.page_size
        params['offset'] = 0

        while True:
            response = self.request('GET', endpoint, params=params)

            for item in response.get('items', []):
                yield item

            if not response.get('hasMore', False):
                break

            params['offset'] += params['limit']
```

### 2. Stream Base Class

All streams inherit from this base class:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Iterator, Optional
from singer import Transformer, metadata

class BaseStream(ABC):
    """Base class for all OIC streams"""

    def __init__(self, client: OICClient, config: Dict[str, Any]):
        self.client = client
        self.config = config
        self.transformer = Transformer()

    @property
    @abstractmethod
    def name(self) -> str:
        """Stream name"""
        pass

    @property
    @abstractmethod
    def endpoint(self) -> str:
        """API endpoint for this stream"""
        pass

    @property
    @abstractmethod
    def key_properties(self) -> List[str]:
        """Primary key fields"""
        pass

    @property
    @abstractmethod
    def replication_key(self) -> Optional[str]:
        """Field used for incremental replication"""
        pass

    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for this stream"""
        schema_path = f"schemas/{self.name}.json"
        with open(schema_path) as f:
            return json.load(f)

    def get_metadata(self) -> List[Dict[str, Any]]:
        """Get stream metadata"""
        mdata = metadata.get_standard_metadata(
            schema=self.get_schema(),
            key_properties=self.key_properties,
            replication_method='INCREMENTAL' if self.replication_key else 'FULL_TABLE'
        )
        return metadata.to_list(mdata)

    def get_records(
        self,
        bookmark: Optional[str] = None
    ) -> Iterator[Dict[str, Any]]:
        """Get records from OIC API"""
        params = {}

        if bookmark and self.replication_key:
            params['modifiedAfter'] = bookmark

        for record in self.client.paginate(self.endpoint, params):
            yield self.transform_record(record)

    def transform_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Transform OIC record to Singer format"""
        # Apply any custom transformations
        return record

    def sync(
        self,
        state: Dict[str, Any],
        catalog_entry: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Sync records for this stream"""
        bookmark = state.get('bookmarks', {}).get(self.name, {})

        with Transformer() as transformer:
            for record in self.get_records(bookmark.get('value')):
                transformed = transformer.transform(
                    record,
                    catalog_entry['schema'],
                    catalog_entry['metadata']
                )

                singer.write_record(self.name, transformed)

                # Update bookmark
                if self.replication_key:
                    new_bookmark = record.get(self.replication_key)
                    if new_bookmark:
                        state = self._update_bookmark(state, new_bookmark)

        return state
```

### 3. Stream Implementations

#### Integrations Stream

```python
class IntegrationsStream(BaseStream):
    """Stream for OIC integrations"""

    name = 'integrations'
    endpoint = '/ic/api/integration/v1/integrations'
    key_properties = ['id']
    replication_key = 'modifiedTime'

    def transform_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Add computed fields"""
        record['_sdc_extracted_at'] = datetime.utcnow().isoformat()

        # Parse version from ID
        if '|' in record.get('id', ''):
            record['identifier'], record['version'] = record['id'].split('|')

        # Normalize status
        record['is_active'] = record.get('status') == 'ACTIVE'

        return record
```

#### Connections Stream

```python
class ConnectionsStream(BaseStream):
    """Stream for OIC connections"""

    name = 'connections'
    endpoint = '/ic/api/integration/v1/connections'
    key_properties = ['id']
    replication_key = 'modifiedTime'

    def get_records(self, bookmark: Optional[str] = None) -> Iterator[Dict[str, Any]]:
        """Override to include connection test status"""
        for record in super().get_records(bookmark):
            # Optionally test connection
            if self.config.get('test_connections', False):
                test_result = self.client.request(
                    'POST',
                    f"{self.endpoint}/{record['id']}/test"
                )
                record['test_status'] = test_result.get('status')

            yield record
```

#### Metrics Stream

```python
class MetricsStream(BaseStream):
    """Stream for integration metrics"""

    name = 'metrics'
    endpoint = '/ic/api/monitoring/v1/integrations/{id}/metrics'
    key_properties = ['integration_id', 'timestamp']
    replication_key = 'timestamp'

    def get_records(self, bookmark: Optional[str] = None) -> Iterator[Dict[str, Any]]:
        """Get metrics for all active integrations"""
        # First get all integrations
        integrations = IntegrationsStream(self.client, self.config)

        for integration in integrations.get_records():
            if integration.get('status') != 'ACTIVE':
                continue

            # Get metrics for this integration
            endpoint = self.endpoint.format(id=integration['id'])
            params = {
                'period': self.config.get('metrics_period', '24h'),
                'interval': self.config.get('metrics_interval', '1h')
            }

            if bookmark:
                params['startTime'] = bookmark

            metrics = self.client.request('GET', endpoint, params=params)

            # Flatten time series data
            for point in metrics.get('timeSeries', []):
                record = {
                    'integration_id': integration['id'],
                    'integration_name': integration['name'],
                    **point
                }
                yield record
```

## Implementation Patterns

### 1. Discovery Pattern

```python
def discover() -> Dict[str, Any]:
    """Discover available streams and their schemas"""
    catalog = {
        'streams': []
    }

    for stream_class in AVAILABLE_STREAMS:
        stream = stream_class(client, config)

        catalog_entry = {
            'stream': stream.name,
            'tap_stream_id': stream.name,
            'schema': stream.get_schema(),
            'metadata': stream.get_metadata(),
            'key_properties': stream.key_properties,
            'replication_key': stream.replication_key,
            'replication_method': 'INCREMENTAL' if stream.replication_key else 'FULL_TABLE'
        }

        catalog['streams'].append(catalog_entry)

    return catalog
```

### 2. Sync Pattern

```python
def sync(config: Dict, state: Dict, catalog: Dict) -> None:
    """Sync data from OIC"""
    client = OICClient(config)

    # Get selected streams
    selected_streams = get_selected_streams(catalog)

    for catalog_entry in selected_streams:
        stream_name = catalog_entry['stream']
        stream_class = STREAM_MAPPING[stream_name]
        stream = stream_class(client, config)

        LOGGER.info(f"Syncing stream: {stream_name}")

        # Write schema
        singer.write_schema(
            stream_name,
            catalog_entry['schema'],
            catalog_entry['key_properties']
        )

        # Sync records
        state = stream.sync(state, catalog_entry)

        # Write state after each stream
        singer.write_state(state)
```

### 3. Rate Limiting Pattern

```python
from functools import wraps
import time

def rate_limit(calls_per_hour: int):
    """Decorator for rate limiting API calls"""
    min_interval = 3600.0 / calls_per_hour
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed

            if left_to_wait > 0:
                time.sleep(left_to_wait)

            ret = func(*args, **kwargs)
            last_called[0] = time.time()

            return ret

        return wrapper
    return decorator

class OICClient:
    @rate_limit(calls_per_hour=1000)
    def request(self, method: str, endpoint: str, **kwargs):
        # Implementation
        pass
```

## State Management

### File-Based State

```python
class FileStateBackend:
    """File-based state storage"""

    def __init__(self, path: str):
        self.path = path

    def get(self) -> Dict[str, Any]:
        """Load state from file"""
        if os.path.exists(self.path):
            with open(self.path) as f:
                return json.load(f)
        return {}

    def set(self, state: Dict[str, Any]) -> None:
        """Save state to file"""
        with open(self.path, 'w') as f:
            json.dump(state, f, indent=2)
```

### Redis State Backend

```python
import redis
import json

class RedisStateBackend:
    """Redis-based state storage"""

    def __init__(self, redis_url: str, key_prefix: str = 'tap_oic'):
        self.client = redis.from_url(redis_url)
        self.key_prefix = key_prefix

    def get(self) -> Dict[str, Any]:
        """Load state from Redis"""
        key = f"{self.key_prefix}:state"
        value = self.client.get(key)

        if value:
            return json.loads(value)
        return {}

    def set(self, state: Dict[str, Any]) -> None:
        """Save state to Redis"""
        key = f"{self.key_prefix}:state"
        value = json.dumps(state)

        self.client.set(key, value)
        # Set expiry to prevent stale state
        self.client.expire(key, 86400)  # 24 hours
```

### State Structure

```json
{
  "bookmarks": {
    "integrations": {
      "value": "2025-06-15T10:00:00Z",
      "version": 1
    },
    "connections": {
      "value": "2025-06-15T09:30:00Z",
      "version": 1
    },
    "metrics": {
      "value": "2025-06-15T09:00:00Z",
      "version": 1,
      "partitions": {
        "CUSTOMER_ORDER_INT": "2025-06-15T09:00:00Z",
        "PRODUCT_SYNC_INT": "2025-06-15T08:45:00Z"
      }
    }
  },
  "currently_syncing": null
}
```

## Error Handling

### Retry Strategy

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_log,
    after_log
)

class OICClient:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type((ConnectionError, Timeout)),
        before=before_log(logger, logging.INFO),
        after=after_log(logger, logging.INFO)
    )
    def request(self, method: str, endpoint: str, **kwargs):
        """Make API request with automatic retry"""
        try:
            response = self.session.request(method, endpoint, **kwargs)
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            if e.response.status_code == 429:
                # Handle rate limiting
                retry_after = int(e.response.headers.get('Retry-After', 60))
                raise RateLimitError(f"Rate limited, retry after {retry_after}s")
            elif e.response.status_code >= 500:
                # Retry server errors
                raise ConnectionError(f"Server error: {e}")
            else:
                # Don't retry client errors
                raise
```

### Error Classification

```python
class ErrorHandler:
    """Classify and handle different error types"""

    @staticmethod
    def handle_error(error: Exception, context: Dict[str, Any]) -> None:
        """Handle errors based on type and context"""

        if isinstance(error, AuthenticationError):
            # Fatal - stop execution
            LOGGER.error(f"Authentication failed: {error}")
            raise

        elif isinstance(error, RateLimitError):
            # Temporary - wait and retry
            wait_time = error.retry_after
            LOGGER.warning(f"Rate limited, waiting {wait_time}s")
            time.sleep(wait_time)

        elif isinstance(error, ValidationError):
            # Skip record and continue
            LOGGER.warning(f"Validation error for record: {error}")
            singer.write_metric('validation_errors', 1)

        elif isinstance(error, ConnectionError):
            # Retry with backoff
            LOGGER.warning(f"Connection error: {error}")
            raise

        else:
            # Unknown error - log and re-raise
            LOGGER.error(f"Unexpected error: {error}")
            raise
```

## Performance Optimization

### 1. Connection Pooling

```python
class OICClient:
    def _create_session(self, config: Dict[str, Any]) -> requests.Session:
        """Create session with connection pooling"""
        session = requests.Session()

        # Configure connection pool
        adapter = HTTPAdapter(
            pool_connections=config.get('pool_connections', 10),
            pool_maxsize=config.get('pool_maxsize', 20),
            max_retries=Retry(
                total=3,
                backoff_factor=0.3,
                status_forcelist=[500, 502, 503, 504]
            )
        )

        session.mount('http://', adapter)
        session.mount('https://', adapter)

        return session
```

### 2. Batch Processing

```python
def sync_with_batching(stream: BaseStream, batch_size: int = 1000) -> None:
    """Process records in batches for better performance"""
    batch = []

    for record in stream.get_records():
        batch.append(record)

        if len(batch) >= batch_size:
            # Process batch
            process_batch(batch)
            batch = []

    # Process remaining records
    if batch:
        process_batch(batch)

def process_batch(records: List[Dict[str, Any]]) -> None:
    """Process a batch of records"""
    # Transform all records
    transformed = [transform_record(r) for r in records]

    # Write records
    for record in transformed:
        singer.write_record(stream.name, record)
```

### 3. Caching

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedOICClient(OICClient):
    """OIC client with caching support"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.cache_ttl = config.get('cache_ttl', 300)  # 5 minutes

    @lru_cache(maxsize=1000)
    def get_cached(self, endpoint: str, ttl_hash: int) -> Dict[str, Any]:
        """Get cached response"""
        return self.request('GET', endpoint)

    def get_with_cache(self, endpoint: str) -> Dict[str, Any]:
        """Get with cache support"""
        # Create TTL hash for cache invalidation
        ttl_hash = int(time.time() // self.cache_ttl)

        return self.get_cached(endpoint, ttl_hash)
```

### 4. Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Callable

def parallel_sync(
    streams: List[BaseStream],
    max_workers: int = 5
) -> None:
    """Sync multiple streams in parallel"""

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all streams
        future_to_stream = {
            executor.submit(stream.sync): stream
            for stream in streams
        }

        # Process completed streams
        for future in as_completed(future_to_stream):
            stream = future_to_stream[future]

            try:
                result = future.result()
                LOGGER.info(f"Stream {stream.name} completed successfully")
            except Exception as e:
                LOGGER.error(f"Stream {stream.name} failed: {e}")
```

## Testing Strategies

### Unit Tests

```python
import unittest
from unittest.mock import Mock, patch
from tap_oic import IntegrationsStream

class TestIntegrationsStream(unittest.TestCase):
    """Test integrations stream"""

    def setUp(self):
        self.client = Mock()
        self.config = {'page_size': 100}
        self.stream = IntegrationsStream(self.client, self.config)

    def test_transform_record(self):
        """Test record transformation"""
        record = {
            'id': 'TEST_INT|01.00.0000',
            'name': 'Test Integration',
            'status': 'ACTIVE'
        }

        transformed = self.stream.transform_record(record)

        self.assertEqual(transformed['identifier'], 'TEST_INT')
        self.assertEqual(transformed['version'], '01.00.0000')
        self.assertTrue(transformed['is_active'])

    @patch('tap_oic.streams.singer.write_record')
    def test_sync(self, mock_write):
        """Test sync process"""
        self.client.paginate.return_value = [
            {'id': 'INT1', 'modifiedTime': '2025-06-15T10:00:00Z'},
            {'id': 'INT2', 'modifiedTime': '2025-06-15T11:00:00Z'}
        ]

        state = {}
        catalog_entry = {
            'schema': {},
            'metadata': []
        }

        new_state = self.stream.sync(state, catalog_entry)

        # Verify records written
        self.assertEqual(mock_write.call_count, 2)

        # Verify bookmark updated
        self.assertEqual(
            new_state['bookmarks']['integrations']['value'],
            '2025-06-15T11:00:00Z'
        )
```

### Integration Tests

```python
class TestOICIntegration(unittest.TestCase):
    """Integration tests with real OIC instance"""

    @classmethod
    def setUpClass(cls):
        cls.config = {
            'instance_url': os.environ['OIC_TEST_URL'],
            'username': os.environ['OIC_TEST_USER'],
            'password': os.environ['OIC_TEST_PASS']
        }
        cls.client = OICClient(cls.config)

    def test_list_integrations(self):
        """Test listing integrations"""
        integrations = list(self.client.paginate(
            '/ic/api/integration/v1/integrations',
            params={'limit': 5}
        ))

        self.assertGreater(len(integrations), 0)
        self.assertIn('id', integrations[0])
        self.assertIn('name', integrations[0])
```

## Best Practices

### 1. Configuration Management

```python
from pydantic import BaseModel, Field, validator
from typing import Optional

class TapConfig(BaseModel):
    """Validated configuration model"""

    instance_url: str = Field(..., description="OIC instance URL")
    username: str = Field(..., description="OIC username")
    password: str = Field(..., description="OIC password")
    start_date: Optional[str] = Field(None, description="Start date for extraction")
    page_size: int = Field(100, ge=1, le=500)
    request_timeout: int = Field(300, ge=1)

    @validator('instance_url')
    def validate_url(cls, v):
        if not v.startswith('https://'):
            raise ValueError('instance_url must use HTTPS')
        return v.rstrip('/')

    @validator('start_date')
    def validate_date(cls, v):
        if v:
            try:
                datetime.fromisoformat(v)
            except ValueError:
                raise ValueError('start_date must be ISO format')
        return v
```

### 2. Logging Best Practices

```python
import logging
from contextvars import ContextVar

# Request ID for tracing
request_id: ContextVar[str] = ContextVar('request_id', default='')

class RequestIdFilter(logging.Filter):
    """Add request ID to log records"""

    def filter(self, record):
        record.request_id = request_id.get()
        return True

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger('tap_oic')
logger.addFilter(RequestIdFilter())
```

### 3. Monitoring and Metrics

```python
from dataclasses import dataclass
from datetime import datetime
import singer

@dataclass
class SyncMetrics:
    """Track sync performance metrics"""

    stream_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    records_synced: int = 0
    errors: int = 0

    def complete(self):
        """Mark sync as complete"""
        self.end_time = datetime.utcnow()
        self.write_metrics()

    def write_metrics(self):
        """Write metrics to Singer"""
        duration = (self.end_time - self.start_time).total_seconds()

        singer.write_metric({
            'type': 'counter',
            'metric': 'records_synced',
            'value': self.records_synced,
            'tags': {'stream': self.stream_name}
        })

        singer.write_metric({
            'type': 'timer',
            'metric': 'sync_duration',
            'value': duration,
            'tags': {'stream': self.stream_name}
        })
```

### 4. Security Best Practices

```python
import os
from cryptography.fernet import Fernet

class SecureConfig:
    """Handle sensitive configuration securely"""

    @staticmethod
    def encrypt_password(password: str, key: bytes) -> str:
        """Encrypt password"""
        f = Fernet(key)
        return f.encrypt(password.encode()).decode()

    @staticmethod
    def decrypt_password(encrypted: str, key: bytes) -> str:
        """Decrypt password"""
        f = Fernet(key)
        return f.decrypt(encrypted.encode()).decode()

    @classmethod
    def load_config(cls, config_path: str) -> Dict[str, Any]:
        """Load config with decryption"""
        with open(config_path) as f:
            config = json.load(f)

        # Get encryption key from environment
        key = os.environ.get('TAP_OIC_ENCRYPTION_KEY')

        if key and config.get('password_encrypted'):
            config['password'] = cls.decrypt_password(
                config['password_encrypted'],
                key.encode()
            )

        return config
```

## Enterprise Security

### Credential Management

#### HashiCorp Vault Integration

```python
import hvac
import json

class VaultCredentialProvider:
    """Retrieve credentials from HashiCorp Vault"""

    def __init__(self, vault_url: str, vault_token: str):
        self.client = hvac.Client(url=vault_url, token=vault_token)

    def get_oic_credentials(self, path: str = 'secret/tap-oic') -> Dict[str, Any]:
        """Get OIC credentials from Vault"""
        response = self.client.secrets.kv.v2.read_secret_version(
            mount_point='secret',
            path='tap-oic'
        )

        return {
            'oauth_client_id': response['data']['data']['client_id'],
            'oauth_client_secret': response['data']['data']['client_secret'],
            'oauth_token_url': response['data']['data']['token_url']
        }

    def rotate_credentials(self) -> None:
        """Rotate OAuth2 credentials"""
        # Generate new client secret in OIC
        new_secret = self._generate_new_secret()

        # Update Vault
        self.client.secrets.kv.v2.create_or_update_secret(
            mount_point='secret',
            path='tap-oic',
            secret={'client_secret': new_secret}
        )
```

#### AWS Secrets Manager Integration

```python
import boto3
import json

class AWSSecretsProvider:
    """Retrieve credentials from AWS Secrets Manager"""

    def __init__(self, region: str = 'us-east-1'):
        self.client = boto3.client('secretsmanager', region_name=region)

    def get_oic_credentials(self, secret_name: str = 'tap-oic-credentials') -> Dict[str, Any]:
        """Get OIC credentials from AWS"""
        response = self.client.get_secret_value(SecretId=secret_name)

        if 'SecretString' in response:
            secret = json.loads(response['SecretString'])
            return {
                'oauth_client_id': secret['client_id'],
                'oauth_client_secret': secret['client_secret'],
                'oauth_token_url': secret['token_url']
            }
```

#### Azure Key Vault Integration

```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

class AzureKeyVaultProvider:
    """Retrieve credentials from Azure Key Vault"""

    def __init__(self, vault_url: str):
        credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=vault_url, credential=credential)

    def get_oic_credentials(self) -> Dict[str, Any]:
        """Get OIC credentials from Azure"""
        return {
            'oauth_client_id': self.client.get_secret('oic-client-id').value,
            'oauth_client_secret': self.client.get_secret('oic-client-secret').value,
            'oauth_token_url': self.client.get_secret('oic-token-url').value
        }
```

### Credential Rotation

```python
import schedule
import time

class CredentialRotator:
    """Automated credential rotation"""

    def __init__(self, provider, oic_REDACTED_LDAP_BIND_PASSWORD_client):
        self.provider = provider
        self.oic_REDACTED_LDAP_BIND_PASSWORD = oic_REDACTED_LDAP_BIND_PASSWORD_client

    def rotate_oauth_secret(self) -> None:
        """Rotate OAuth2 client secret"""
        try:
            # Generate new secret
            new_secret = self.oic_REDACTED_LDAP_BIND_PASSWORD.rotate_client_secret()

            # Update secret store
            self.provider.update_secret('oauth_client_secret', new_secret)

            # Log rotation (no secret values!)
            logger.info("OAuth2 client secret rotated successfully")

            # Notify REDACTED_LDAP_BIND_PASSWORDistrators
            self._send_rotation_notification()

        except Exception as e:
            logger.error(f"Failed to rotate credentials: {str(e)}")
            self._send_rotation_alert(str(e))

    def schedule_rotation(self, days: int = 90) -> None:
        """Schedule automatic rotation"""
        schedule.every(days).days.do(self.rotate_oauth_secret)

        while True:
            schedule.run_pending()
            time.sleep(3600)  # Check every hour
```

### Data Protection

#### Encryption in Transit

```python
import ssl
import requests
from requests.adapters import HTTPAdapter

class TLSAdapter(HTTPAdapter):
    """Force TLS 1.2+ with strong ciphers"""

    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

# Use in tap
session = requests.Session()
session.mount('https://', TLSAdapter())
```

#### Data Masking

```python
import re
import hashlib

class DataMasker:
    """Mask sensitive data in records"""

    def __init__(self, config: Dict[str, Any]):
        self.patterns = {
            'email': (r'[\w\.-]+@[\w\.-]+\.\w+', self._mask_email),
            'ssn': (r'\d{3}-\d{2}-\d{4}', self._mask_ssn),
            'credit_card': (r'\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}', self._mask_cc),
            'phone': (r'\+?\d{1,3}[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}', self._mask_phone)
        }
        self.mask_fields = config.get('mask_fields', [])

    def mask_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive data in record"""
        masked = record.copy()

        # Mask specified fields
        for field in self.mask_fields:
            if field in masked and masked[field]:
                masked[field] = self._hash_value(masked[field])

        # Apply pattern-based masking
        for field, value in masked.items():
            if isinstance(value, str):
                masked[field] = self._apply_patterns(value)

        return masked

    def _mask_email(self, email: str) -> str:
        """Mask email address"""
        parts = email.split('@')
        if len(parts) == 2:
            name = parts[0]
            masked_name = name[0] + '*' * (len(name) - 2) + name[-1] if len(name) > 2 else '***'
            return f"{masked_name}@{parts[1]}"
        return '***@***.***'

    def _hash_value(self, value: str) -> str:
        """One-way hash of sensitive value"""
        return hashlib.sha256(str(value).encode()).hexdigest()[:16]
```

### Compliance

#### GDPR Compliance

```python
class GDPRCompliantTap:
    """GDPR-compliant data extraction"""

    def __init__(self, tap, config: Dict[str, Any]):
        self.tap = tap
        self.pii_fields = config.get('pii_fields', [])
        self.retention_days = config.get('retention_days', 30)

    def extract_with_consent(self, consent_map: Dict[str, bool]) -> Iterator[Dict[str, Any]]:
        """Extract only consented data"""
        for record in self.tap.extract():
            if self._has_consent(record, consent_map):
                yield self._anonymize_if_required(record)

    def _anonymize_if_required(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize PII fields"""
        if self._requires_anonymization(record):
            for field in self.pii_fields:
                if field in record:
                    record[field] = self._anonymize_value(record[field])
        return record

    def export_user_data(self, user_id: str) -> List[Dict[str, Any]]:
        """Export all data for a specific user (GDPR Article 20)"""
        user_data = []
        for stream in self.tap.streams:
            records = stream.get_user_records(user_id)
            user_data.extend(records)
        return user_data

    def delete_user_data(self, user_id: str) -> Dict[str, Any]:
        """Delete user data (GDPR Article 17)"""
        # Mark records for deletion in target system
        deletion_request = {
            'user_id': user_id,
            'requested_at': datetime.utcnow(),
            'streams': list(self.tap.streams.keys())
        }
        return deletion_request
```

#### SOC2 Compliance

```python
class SOC2AuditLogger:
    """SOC2-compliant audit logging"""

    def __init__(self, log_destination):
        self.destination = log_destination

    def log_access(self, user: str, action: str, resource: str, result: bool) -> None:
        """Log all access attempts"""
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user': user,
            'action': action,
            'resource': resource,
            'result': result,
            'ip_address': self._get_ip_address(),
            'session_id': self._get_session_id()
        }

        # Sign log entry
        audit_entry['signature'] = self._sign_entry(audit_entry)

        # Write to tamper-proof log
        self.destination.write(audit_entry)
```

### Security Monitoring

```python
class SecurityMonitor:
    """Monitor for security threats"""

    def __init__(self):
        self.baseline = {}
        self.alerts = []

    def analyze_api_calls(self, api_calls: List[Dict[str, Any]]) -> None:
        """Analyze API calls for anomalies"""
        # Check for unusual patterns
        for call in api_calls:
            if self._is_anomalous(call):
                self.alerts.append({
                    'type': 'anomalous_api_call',
                    'details': call,
                    'timestamp': datetime.utcnow()
                })

        # Check for rate anomalies
        call_rate = len(api_calls) / 300  # per 5 minutes
        if call_rate > self.baseline.get('normal_rate', 100) * 2:
            self.alerts.append({
                'type': 'unusual_api_rate',
                'rate': call_rate,
                'timestamp': datetime.utcnow()
            })

    def _is_anomalous(self, call: Dict[str, Any]) -> bool:
        """Check if API call is anomalous"""
        # Check for suspicious patterns
        suspicious_patterns = [
            'union select',  # SQL injection attempt
            '<script>',      # XSS attempt
            '../',           # Path traversal
            'REDACTED_LDAP_BIND_PASSWORD',         # Privilege escalation
        ]

        call_str = str(call).lower()
        return any(pattern in call_str for pattern in suspicious_patterns)
```

## Summary

This implementation guide provides a comprehensive framework for building a robust tap-oic implementation. Key takeaways:

1. **Modular Architecture**: Separate concerns into distinct components
2. **Error Resilience**: Implement retry logic and error classification
3. **Performance**: Use connection pooling, caching, and parallel processing
4. **Testing**: Comprehensive unit and integration tests
5. **Security**: Protect sensitive data and use secure connections
6. **Monitoring**: Track metrics and performance

For specific implementation examples, see the [Examples](EXAMPLES.md) documentation.
