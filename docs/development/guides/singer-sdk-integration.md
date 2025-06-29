# Singer SDK Integration Guide

> **Building custom data extractors and loaders with the Meltano Singer SDK for FLX framework integration**

## Overview

The Meltano Singer SDK is the fastest way to build custom data extractors and loaders that automatically comply with the Singer Specification. When integrated with the FLX framework, it provides a powerful foundation for enterprise data integration pipelines.

## Key Benefits

- **70% less code**: Developers report significant code reduction using the SDK
- **Future-proof**: Automatic access to new features and bug fixes through SDK updates
- **Singer Spec compliant**: Built-in compliance with the de-facto open source standard
- **FLX integration ready**: Seamless integration with hexagonal architecture patterns

## Integration with FLX Framework

The Singer SDK integrates with FLX's hexagonal architecture through adapter patterns:

```python
from flext.adapters.base import BaseAdapter
from singer_sdk import Tap, Target
from typing import Dict, Any

class FLXSingerAdapter(BaseAdapter):
    """Adapter for Singer SDK integration with FLX framework."""

    def __init__(self, tap_class: type[Tap], target_class: type[Target]):
        self.tap_class = tap_class
        self.target_class = target_class

    async def extract_data(self, config: Dict[str, Any]) -> Any:
        """Extract data using Singer tap."""
        tap = self.tap_class(config=config)
        return await tap.sync_all()

    async def load_data(self, data: Any, config: Dict[str, Any]) -> bool:
        """Load data using Singer target."""
        target = self.target_class(config=config)
        return await target.load_data(data)
```

## Building Custom Taps and Targets

### Custom Tap Example

```python
from singer_sdk import Tap
from singer_sdk.streams import RESTStream

class CustomTap(Tap):
    """Custom tap for extracting data from your API."""

    name = "tap-custom-api"
    config_jsonschema = {
        "type": "object",
        "properties": {
            "api_url": {"type": "string"},
            "api_key": {"type": "string"}
        }
    }

    def discover_streams(self):
        return [CustomStream(tap=self)]

class CustomStream(RESTStream):
    """Custom stream for your data source."""

    name = "your_stream"
    path = "/api/data"
    primary_keys = ["id"]
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"}
        }
    }
```

### Custom Target Example

```python
from singer_sdk import Target
from singer_sdk.sinks import SQLSink

class CustomTarget(Target):
    """Custom target for loading data."""

    name = "target-custom-db"
    config_jsonschema = {
        "type": "object",
        "properties": {
            "connection_string": {"type": "string"}
        }
    }

    default_sink_class = CustomSink

class CustomSink(SQLSink):
    """Custom sink for your target database."""

    def process_record(self, record: dict, context: dict) -> None:
        # Custom record processing logic
        super().process_record(record, context)
```

## Development Workflow

### 1. Setup Development Environment

```bash
# Install Singer SDK and cookiecutter
pip install singer-sdk
pip3 install pipx
pipx ensurepath
pipx install cookiecutter
```

### 2. Create Projects from Templates

#### Create New Tap

```bash
# From Git repository
cookiecutter https://github.com/meltano/sdk --directory="cookiecutter/tap-template"

# From local SDK repo
cookiecutter ./singer_sdk/cookiecutter/tap-template
```

#### Create New Target

```bash
# From Git repository
cookiecutter https://github.com/meltano/sdk --directory="cookiecutter/target-template"

# From local SDK repo
cookiecutter ./singer_sdk/cookiecutter/target-template
```

#### Create New Mapper

```bash
# From Git repository
cookiecutter https://github.com/meltano/sdk --directory="cookiecutter/mapper-template"

# From local SDK repo
cookiecutter ./singer_sdk/cookiecutter/mapper-template
```

### 3. Integration with FLX Workspace

```bash
# Add to FLX project dependencies
poetry add singer-sdk

# Link with FLX adapters
poetry add --path ../flext
```

### 4. Testing with FLX Framework

```python
import pytest
from flext.testing.engines import BaseTestEngine
from your_tap import CustomTap

class TestSingerIntegration(BaseTestEngine):
    """Test Singer SDK integration with FLX."""

    async def test_tap_extraction(self):
        tap = CustomTap(config=self.test_config)
        records = []

        for record in tap.sync_all():
            records.append(record)

        assert len(records) > 0
        assert all("id" in record for record in records)
```

## Best Practices

### Configuration Management

- Use FLX configuration patterns for consistent setup
- Leverage environment variables through FLX config adapters
- Implement validation using Pydantic models

### Error Handling

- Integrate with FLX error handling patterns
- Use structured logging for better observability
- Implement retry mechanisms for robust data pipelines

### Performance Optimization

- Utilize FLX async patterns for better throughput
- Implement proper connection pooling
- Use FLX caching mechanisms where appropriate

## Meltano Integration

The Singer SDK works seamlessly with Meltano for complete ELT pipelines:

```yaml
# meltano.yml
plugins:
  extractors:
    - name: tap-custom-api
      pip_url: -e .

  loaders:
    - name: target-custom-db
      pip_url: -e .
```

## Related Documentation

- [Meltano Plugins Integration](meltano-plugins-integration.md)
- [FLX Adapters Guide](../architecture/adapters-implementation-guide.md)
- [Oracle Integration Patterns](../guides/oracle-platform-resources.md)
- [Development Tools](development-tools.md)

## External Resources

- [Singer SDK Documentation](https://sdk.meltano.com)
- [Meltano Documentation](https://docs.meltano.com)
- [Singer Specification](https://hub.meltano.com/singer/spec)
- [Contributing Guide](https://sdk.meltano.com/en/latest/CONTRIBUTING.html)
