# Utility & Helper Patterns

**Version**: 0.9.0 | **Status**: Active | **Python**: 3.13+

## Overview

Standardized approach to organizing utility functions across the FLEXT ecosystem. Emphasizes domain-specific organization, consistent naming conventions, and proper separation between generic and specialized utilities.

## Core Principles

### Domain-Specific Organization

Utilities grouped by their semantic domain:

```python
flext_data_*()      # Data processing utilities
flext_auth_*()      # Authentication utilities
flext_text_*()      # Text processing utilities
flext_time_*()      # Time/date utilities
flext_crypto_*()    # Cryptographic utilities
flext_net_*()       # Network utilities
```

### Naming Convention

Clear, descriptive function names:

```python
# Pattern: flext_[domain]_[action]_[object]
flext_data_safe_int_conversion()
flext_auth_hash_password()
flext_text_normalize_whitespace()
flext_time_format_iso8601()
```

### Result-Based Error Handling

All operations that can fail return FlextResult.

### Generic Core, Specific Extensions

- **flext-core**: Generic utilities only
- **Projects**: Domain-specific utilities
- **No cross-dependencies**: Projects don't share utilities

## Core Generic Utilities

### System Utilities

```python
from typing import Dict

from datetime import datetime, timezone
import uuid

def flext_core_generate_id() -> str:
    """Generate unique identifier."""
    return str(uuid.uuid4())

def flext_core_generate_correlation_id() -> str:
    """Generate correlation ID for distributed tracing."""
    return f"flext-{uuid.uuid4().hex[:16]}-{int(datetime.now().timestamp())}"

def flext_core_get_timestamp() -> datetime:
    """Get current UTC timestamp."""
    return datetime.now(timezone.utc)

def flext_core_safe_get(
    dictionary: FlextTypes.Dict,
    key: str,
    default: object = None
) -> object:
    """Safely get value from dictionary with default."""
    return dictionary.get(key, default)
```

### Data Conversion Utilities

```python
from flext_core.result import FlextResult

def flext_data_safe_int_conversion(
    value: object,
    default: int = 0
) -> FlextResult[int]:
    """Safely convert value to integer."""
    if value is None:
        return FlextResult[None].ok(default)

    try:
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return FlextResult[None].ok(default)

        return FlextResult[None].ok(int(value))
    except (ValueError, TypeError) as e:
        return FlextResult[None].fail(f"Cannot convert '{value}' to integer: {e}")

def flext_data_safe_bool_conversion(
    value: object,
    default: bool = False
) -> bool:
    """Safely convert value to boolean."""
    if value is None:
        return default

    if isinstance(value, str):
        return value.lower() in ('true', 'yes', '1', 'on', 't', 'y')

    if isinstance(value, (int, float)):
        return value != 0

    return bool(value)
```

### Text Processing Utilities

```python
import re

def flext_text_normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text."""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def flext_text_truncate(
    text: str,
    max_length: int,
    suffix: str = "..."
) -> str:
    """Truncate text to maximum length with suffix."""
    if len(text) <= max_length:
        return text

    if max_length <= len(suffix):
        return text[:max_length]

    return text[:max_length - len(suffix)] + suffix

def flext_text_slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower()
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'[^a-z0-9-]', '', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

def flext_text_mask_sensitive(
    text: str,
    visible_start: int = 4,
    visible_end: int = 4,
    mask_char: str = "*"
) -> str:
    """Mask sensitive information in text."""
    if len(text) <= visible_start + visible_end:
        return mask_char * len(text)

    masked_length = len(text) - visible_start - visible_end
    return text[:visible_start] + (mask_char * masked_length) + text[-visible_end:]
```

### Time and Date Utilities

```python
def flext_time_format_iso8601(dt: datetime) -> str:
    """Format datetime as ISO8601 string."""
    return dt.isoformat()

def flext_time_parse_iso8601(date_string: str) -> FlextResult[datetime]:
    """Parse ISO8601 string to datetime."""
    try:
        if date_string.endswith('Z'):
            date_string = date_string[:-1] + '+00:00'

        return FlextResult[None].ok(datetime.fromisoformat(date_string))
    except ValueError as e:
        return FlextResult[None].fail(f"Invalid ISO8601 date format: {e}")

def flext_time_format_duration(seconds: float) -> str:
    """Format duration in human-readable form."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f}h"
    else:
        days = seconds / 86400
        return f"{days:.1f}d"
```

### Collection Utilities

```python
from typing import List, Callable
from flext_core import T

def flext_collection_chunk(
    items: List[T],
    chunk_size: int
) -> List[List[T]]:
    """Split list into chunks of specified size."""
    if chunk_size <= 0:
        return []

    return [
        items[i:i + chunk_size]
        for i in range(0, len(items), chunk_size)
    ]

def flext_collection_unique(items: List[T]) -> List[T]:
    """Return unique items preserving order."""
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

def flext_collection_group_by(
    items: List[T],
    key_func: Callable[[T], object]
) -> Dict[object, List[T]]:
    """Group items by key function."""
from collections import defaultdict
    groups = defaultdict(list)
    for item in items:
        key = key_func(item)
        groups[key].append(item)
    return dict(groups)
```

## Domain-Specific Utilities

### Authentication Utilities (flext-auth)

```python
# flext-auth/src/flext_auth/utils.py
import bcrypt
import jwt
from datetime import datetime, timedelta

def flext_auth_hash_password(password: str) -> FlextResult[str]:
    """Hash password using bcrypt."""
    try:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return FlextResult[None].ok(hashed.decode('utf-8'))
    except Exception as e:
        return FlextResult[None].fail(f"Password hashing failed: {e}")

def flext_auth_verify_password(
    password: str,
    hashed_password: str
) -> FlextResult[bool]:
    """Verify password against hash."""
    try:
        result = bcrypt.checkpw(
            password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
        return FlextResult[None].ok(result)
    except Exception as e:
        return FlextResult[None].fail(f"Password verification failed: {e}")

def flext_auth_generate_jwt(
    payload: dict,
    secret_key: str,
    expires_in: int = 3600
) -> FlextResult[str]:
    """Generate JWT token."""
    try:
        payload = payload.copy()
        payload['exp'] = datetime.utcnow() + timedelta(seconds=expires_in)
        payload['iat'] = datetime.utcnow()

        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return FlextResult[None].ok(token)
    except Exception as e:
        return FlextResult[None].fail(f"JWT generation failed: {e}")

def flext_auth_generate_api_key(prefix: str = "flext") -> str:
    """Generate API key with prefix."""
from flext_core.utils import flext_crypto_generate_token
    token = flext_crypto_generate_token(32)
    return f"{prefix}_{token}"
```

### Data Processing Utilities (flext-meltano)

```python
# flext-meltano/src/flext_meltano/utils.py
from typing import Iterator, Dict, List
import json

def flext_data_parse_json_stream(
    stream: Iterator[str]
) -> Iterator[FlextResult[dict]]:
    """Parse JSON objects from line stream."""
    for line in stream:
        line = line.strip()
        if not line:
            continue

        try:
            obj = json.loads(line)
            yield FlextResult[None].ok(obj)
        except json.JSONDecodeError as e:
            yield FlextResult[None].fail(f"Invalid JSON on line: {e}")

def flext_data_flatten_record(
    record: dict,
    separator: str = ".",
    prefix: str = ""
) -> dict:
    """Flatten nested dictionary with separator."""
    flattened = {}

    for key, value in record.items():
        new_key = f"{prefix}{separator}{key}" if prefix else key

        if isinstance(value, dict):
            flattened.update(
                flext_data_flatten_record(value, separator, new_key)
            )
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    flattened.update(
                        flext_data_flatten_record(
                            item, separator, f"{new_key}[{i}]"
                        )
                    )
                else:
                    flattened[f"{new_key}[{i}]"] = item
        else:
            flattened[new_key] = value

    return flattened

def flext_data_batch_records(
    records: Iterator[dict],
    batch_size: int = 1000
) -> Iterator[List[dict]]:
    """Batch records into chunks."""
    batch = []

    for record in records:
        batch.append(record)

        if len(batch) >= batch_size:
            yield batch
            batch = []

    if batch:
        yield batch
```

### LDAP Utilities (flext-ldap)

```python
# flext-ldap/src/flext_ldap/utils.py
def flext_ldap_escape_filter_chars(value: str) -> str:
    """Escape special characters for LDAP filter."""
    escape_chars = {
        '\\': r'\5c',
        '*': r'\2a',
        '(': r'\28',
        ')': r'\29',
        '\0': r'\00',
        '/': r'\2f'
    }

    for char, escaped in escape_chars.items():
        value = value.replace(char, escaped)

    return value

def flext_ldap_parse_dn(dn: str) -> FlextResult[List[Dict[str, str]]]:
    """Parse LDAP DN into components."""
    try:
        components = []
        parts = re.split(r'(?<!\\),', dn)

        for part in parts:
            part = part.strip()
            if '=' not in part:
                return FlextResult[None].fail(f"Invalid DN component: {part}")

            key, value = part.split('=', 1)
            components.append({
                'type': key.strip(),
                'value': value.strip()
            })

        return FlextResult[None].ok(components)
    except Exception as e:
        return FlextResult[None].fail(f"DN parse error: {e}")
```

## Usage Examples

### Basic Utility Usage

```python
from flext_core.utils import (
    flext_data_safe_int_conversion,
    flext_text_slugify,
    flext_time_format_duration,
    flext_collection_chunk
)

# Safe conversions
result = flext_data_safe_int_conversion("123")
if result.success:
    print(f"Converted: {result.data}")  # 123

# Text processing
slug = flext_text_slugify("Hello World! 123")
print(slug)  # "hello-world-123"

# Time formatting
duration = flext_time_format_duration(3665)
print(duration)  # "1.0h"

# Collection utilities
items = list(range(10))
chunks = flext_collection_chunk(items, 3)
# [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
```

### Data Processing Pipeline

```python
from flext_meltano.utils import (
    flext_data_parse_json_stream,
    flext_data_flatten_record,
    flext_data_batch_records
)

def process_json_stream(lines: List[str]) -> FlextResult[List[dict]]:
    """Process JSON lines with transformation."""
    processed_records = []
    errors = []

    # Parse JSON stream
    for result in flext_data_parse_json_stream(iter(lines)):
        if result.is_failure:
            errors.append(result.error)
            continue

        record = result.data

        # Flatten nested structure
        flattened = flext_data_flatten_record(record)
        processed_records.append(flattened)

    if errors:
        return FlextResult[None].fail(
            f"Processing completed with {len(errors)} errors",
            errors=errors,
            partial_result=processed_records
        )

    return FlextResult[None].ok(processed_records)

# Batch processing
def process_in_batches(records: List[dict]) -> None:
    for batch in flext_data_batch_records(iter(records), batch_size=100):
        print(f"Processing batch of {len(batch)} records")
        # Process batch...
```

### Authentication Workflow

```python
from flext_auth.utils import (
    flext_auth_hash_password,
    flext_auth_verify_password,
    flext_auth_generate_jwt
)

class AuthService:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def register_user(self, username: str, password: str) -> FlextResult[User]:
        # Hash password
        hash_result = flext_auth_hash_password(password)
        if hash_result.is_failure:
            return FlextResult[None].fail(f"Password hashing failed: {hash_result.error}")

        # Create user
        user = User(username=username, password_hash=hash_result.data)
        return FlextResult[None].ok(user)

    def login(self, username: str, password: str) -> FlextResult[dict]:
        # Get user
        user = self.get_user_by_username(username)
        if not user:
            return FlextResult[None].fail("Invalid credentials")

        # Verify password
        verify_result = flext_auth_verify_password(password, user.password_hash)
        if verify_result.is_failure or not verify_result.data:
            return FlextResult[None].fail("Invalid credentials")

        # Generate token
        token_result = flext_auth_generate_jwt(
            {"user_id": user.id, "username": user.username},
            self.secret_key,
            expires_in=3600
        )

        if token_result.is_failure:
            return FlextResult[None].fail("Token generation failed")

        return FlextResult[None].ok({
            "access_token": token_result.data,
            "token_type": "Bearer"
        })
```

## Quality Standards

- **Single Responsibility**: Each function does one thing well
- **Pure Functions**: No side effects when possible
- **Error Handling**: Return FlextResult for fallible operations
- **Type Safety**: Complete type annotations
- **Documentation**: Clear docstrings with examples

## Related Patterns

- [Foundation](./foundation.md) - FlextResult usage
- [Type System](./types.md) - Type definitions
- [Error](./error-observability.md) - Error handling in utilities

---

**Utility & Helper Patterns** - Domain-specific utility organization that ensures consistency and maintainability across the entire FLEXT ecosystem.
