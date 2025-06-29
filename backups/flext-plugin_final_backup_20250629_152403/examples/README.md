# FLX Plugin Examples

This directory contains example plugins demonstrating various features of the FLX plugin system.

## Examples Overview

### 1. Basic Plugin (`basic_plugin/`)

A simple "Hello World" plugin that demonstrates:
- Minimal plugin implementation
- Plugin metadata definition
- Configuration schema
- Basic execute method
- Health check implementation

**Run example:**
```python
from flx_plugin.examples.basic_plugin.hello_world_plugin import HelloWorldPlugin

# Create and initialize plugin
plugin = HelloWorldPlugin(config={"greeting": "Hi", "name": "FLX"})
await plugin.initialize()

# Execute plugin
result = await plugin.execute({"name": "Developer"}, {})
print(result)  # {"message": "Hi, Developer!", ...}
```

### 2. Stateful Plugin (`stateful_plugin/`)

A counter plugin that demonstrates:
- State preservation across reloads
- `get_state()` and `set_state()` methods
- Hot reload support
- Stateful operations

**Run example:**
```python
from flx_plugin.examples.stateful_plugin.counter_plugin import CounterPlugin

# Create counter plugin
plugin = CounterPlugin(config={"initial_value": 0, "increment": 5})
await plugin.initialize()

# Perform operations
await plugin.execute("increment", {})  # Counter: 5
await plugin.execute("increment", {})  # Counter: 10

# Save state
state = await plugin.get_state()
print(state)  # {"counter": 10, "total_operations": 2, ...}

# Simulate reload - restore state
new_plugin = CounterPlugin(config={"initial_value": 0, "increment": 5})
await new_plugin.initialize()
await new_plugin.set_state(state)

# Continue from saved state
await new_plugin.execute("increment", {})  # Counter: 15
```

### 3. Singer Plugin (`singer_plugin/`)

A Singer tap plugin that demonstrates:
- Singer protocol integration
- Schema discovery
- Data extraction
- State management for incremental sync
- Stream selection

**Run example:**
```python
from flx_plugin.examples.singer_plugin.tap_example import TapExamplePlugin

# Create tap plugin
plugin = TapExamplePlugin(config={
    "api_url": "https://api.example.com",
    "page_size": 100
})
await plugin.initialize()

# Discover schemas
catalog = await plugin.execute("discover", {})
print(catalog)  # {"streams": [...]}

# Sync data
messages = await plugin.execute({
    "command": "sync",
    "catalog": catalog,
    "state": {}
}, {})

for message in messages:
    print(f"{message['type']}: {message.get('stream', 'N/A')}")
```

## Plugin Development Guide

### 1. Create Your Plugin Class

```python
from flx_plugin import Plugin, PluginMetadata, PluginType

class MyPlugin(Plugin):
    @classmethod
    def get_metadata(cls) -> PluginMetadata:
        return PluginMetadata(
            id="my-plugin",
            name="My Plugin",
            version="1.0.0",
            description="My custom plugin",
            plugin_type=PluginType.PROCESSOR,
            author="Your Name",
            license="MIT",
            capabilities=["custom_processing"],
            dependencies=[],
            configuration_schema={
                "type": "object",
                "properties": {
                    "option": {"type": "string"}
                }
            }
        )
```

### 2. Implement Required Methods

```python
async def initialize(self) -> None:
    """Initialize your plugin."""
    # Setup resources, validate config
    pass

async def execute(self, input_data: Any, context: Dict[str, Any]) -> Any:
    """Execute plugin functionality."""
    # Process input and return result
    pass

async def health_check(self) -> Dict[str, Any]:
    """Check plugin health."""
    return {"status": "healthy"}

async def cleanup(self) -> None:
    """Clean up resources."""
    pass
```

### 3. Add State Support (Optional)

For hot reload support, implement state methods:

```python
async def get_state(self) -> Dict[str, Any]:
    """Return current plugin state."""
    return {"my_data": self.my_data}

async def set_state(self, state: Dict[str, Any]) -> None:
    """Restore plugin state."""
    self.my_data = state.get("my_data")
```

### 4. Register Your Plugin

For entry point discovery, add to your `setup.py`:

```python
entry_points={
    'flx.plugins': [
        'my-plugin = my_package.my_plugin:MyPlugin',
    ],
}
```

## Testing Plugins

```python
import pytest
from flx_plugin.core.validators import PluginValidator

async def test_my_plugin():
    # Validate plugin
    validator = PluginValidator()
    result = validator.validate_plugin_class(MyPlugin)
    assert result.is_valid

    # Test execution
    plugin = MyPlugin(config={})
    await plugin.initialize()
    result = await plugin.execute("test", {})
    assert result is not None
    await plugin.cleanup()
```

## Hot Reload Development

Enable hot reload for development:

```python
from flx_plugin.hot_reload import HotReloadManager

# Setup hot reload
manager = HotReloadManager(
    plugin_manager=plugin_manager,
    watch_directories=[Path("./my_plugins")],
    strategy=ReloadStrategy(
        preserve_state=True,
        create_rollback=True
    )
)

# Start watching
await manager.start()

# Your plugin will automatically reload when you save changes!
```

## Best Practices

1. **Always validate input** in your execute method
2. **Handle errors gracefully** and provide meaningful error messages
3. **Implement proper cleanup** to avoid resource leaks
4. **Use logging** for debugging and monitoring
5. **Follow semantic versioning** for your plugin versions
6. **Document configuration schema** thoroughly
7. **Test state preservation** if implementing hot reload
8. **Consider security** when processing external data

## More Information

See the [FLX Plugin documentation](../README.md) for complete API reference and advanced features.
