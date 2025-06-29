# FLX Plugin - Enterprise Plugin System

**Status**: 🟡 Development (40% Complete)
**Based on**: Real implementation from `flx-meltano-enterprise/src/flx_core/plugins/`

## Overview

FLX Plugin provides a sophisticated plugin architecture for extending the FLX platform. Currently embedded within flx-core, this module enables dynamic loading, lifecycle management, and hot reload capabilities for plugins.

## Real Implementation Status

| Component         | Status      | Details                           |
| ----------------- | ----------- | --------------------------------- |
| **discovery.py**  | ✅ Complete | Plugin discovery via entry points |
| **loader.py**     | ✅ Complete | Dynamic plugin loading            |
| **manager.py**    | 🟡 Partial  | Basic management, no hot reload   |
| **types.py**      | ✅ Complete | Plugin interfaces and types       |
| **validators.py** | ✅ Complete | Plugin validation logic           |
| **hot_reload.py** | ❌ Missing  | Main gap to implement             |

**Current**: 40% complete with foundational components working
**Gap**: Hot reload system for zero-downtime updates

## Architecture

```
flx-plugin/
├── src/
│   └── flx_plugin/
│       ├── __init__.py
│       ├── core/
│       │   ├── discovery.py        # Plugin discovery
│       │   ├── loader.py          # Dynamic loading
│       │   ├── manager.py         # Lifecycle management
│       │   ├── types.py           # Plugin interfaces
│       │   └── validators.py      # Validation logic
│       ├── hot_reload/
│       │   ├── __init__.py
│       │   ├── watcher.py         # File system monitoring
│       │   ├── reloader.py        # Hot reload logic
│       │   └── state_manager.py   # State preservation
│       ├── registry/
│       │   ├── __init__.py
│       │   ├── local.py           # Local plugin registry
│       │   ├── remote.py          # Remote marketplace
│       │   └── catalog.py         # Plugin catalog
│       └── examples/
│           ├── basic_plugin.py
│           ├── stateful_plugin.py
│           └── async_plugin.py
```

## Plugin Types

### 1. **Extractor Plugins** (Singer Taps)

```python
class ExtractorPlugin(Plugin):
    """Extract data from sources."""

    async def discover(self) -> Catalog:
        """Discover available streams."""

    async def extract(self, state: State) -> AsyncIterator[Record]:
        """Extract records with state management."""
```

### 2. **Loader Plugins** (Singer Targets)

```python
class LoaderPlugin(Plugin):
    """Load data to destinations."""

    async def load(self, records: AsyncIterator[Record]) -> State:
        """Load records and return state."""
```

### 3. **Transformer Plugins**

```python
class TransformerPlugin(Plugin):
    """Transform data between extraction and loading."""

    async def transform(self, record: Record) -> Record:
        """Transform individual records."""
```

### 4. **Orchestrator Plugins**

```python
class OrchestratorPlugin(Plugin):
    """Orchestrate complex workflows."""

    async def orchestrate(self, pipeline: Pipeline) -> ExecutionResult:
        """Orchestrate pipeline execution."""
```

## Features

### Currently Implemented

- **Entry Point Discovery**: Automatic plugin discovery via setuptools
- **Dynamic Loading**: Import and instantiate plugins at runtime
- **Validation Framework**: Schema and interface validation
- **Basic Lifecycle**: Initialize, start, stop, cleanup
- **Plugin Metadata**: Name, version, author, capabilities

### To Be Implemented (Hot Reload)

- **File System Watching**: Monitor plugin directories
- **State Preservation**: Save/restore plugin state
- **Zero-Downtime Reload**: Replace plugins without stopping
- **Version Management**: Handle plugin upgrades
- **Rollback Capability**: Revert to previous version on failure

## Quick Start

```bash
# Install plugin system
cd /home/marlonsc/pyauto/flx-plugin
poetry install

# Create a basic plugin
poetry run flx-plugin create my-plugin --type extractor

# Install a plugin
poetry run flx-plugin install tap-github

# List installed plugins
poetry run flx-plugin list

# Enable hot reload (when implemented)
poetry run flx-plugin watch --enable-hot-reload
```

## Creating Plugins

### Basic Plugin Structure

```python
# my_plugin.py
from flx_plugin import Plugin, PluginMetadata, hook

class MyPlugin(Plugin):
    """Example plugin implementation."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my-plugin",
            version="1.0.0",
            author="Your Name",
            description="My awesome plugin",
            capabilities=["extract", "state"]
        )

    @hook("before_pipeline_run")
    async def setup(self, context):
        """Called before pipeline execution."""
        self.logger.info("Setting up plugin")

    @hook("extract_records")
    async def extract(self, context):
        """Extract records from source."""
        async for record in self.source.read():
            yield self.transform_record(record)
```

### Plugin Configuration

```yaml
# plugin.yaml
name: my-plugin
version: 1.0.0
type: extractor
entry_point: my_plugin:MyPlugin

configuration:
  api_key:
    type: string
    required: true
    secret: true
  base_url:
    type: string
    default: https://api.example.com

dependencies:
  - requests>=2.28.0
  - pydantic>=2.0.0
```

## Hot Reload Implementation (Proposed)

### State-Preserving Reload

```python
# Proposed implementation for hot reload
class HotReloadManager:
    """Manage plugin hot reloading."""

    async def reload_plugin(self, plugin_id: str):
        """Reload plugin preserving state."""
        # 1. Save current state
        state = await self.save_plugin_state(plugin_id)

        # 2. Stop plugin gracefully
        await self.stop_plugin(plugin_id)

        # 3. Reload plugin code
        new_plugin = await self.load_plugin_code(plugin_id)

        # 4. Restore state
        await self.restore_plugin_state(new_plugin, state)

        # 5. Start new plugin
        await self.start_plugin(new_plugin)
```

### File System Monitoring

```python
# Watch for plugin changes
class PluginWatcher:
    """Monitor plugin files for changes."""

    def __init__(self, plugin_dirs: List[Path]):
        self.watcher = watchfiles.awatch(plugin_dirs)

    async def watch(self):
        """Watch for plugin changes."""
        async for changes in self.watcher:
            for change_type, path in changes:
                plugin_id = self.get_plugin_id(path)

                if change_type in ('added', 'modified'):
                    await self.reload_plugin(plugin_id)
```

## Plugin Registry

### Local Registry

```python
# Local plugin management
class LocalRegistry:
    """Manage locally installed plugins."""

    def list_plugins(self) -> List[PluginInfo]:
        """List all installed plugins."""

    def install_plugin(self, path: Path) -> PluginInfo:
        """Install plugin from path."""

    def uninstall_plugin(self, plugin_id: str) -> None:
        """Uninstall plugin."""
```

### Remote Marketplace (Future)

```python
# Plugin marketplace integration
class RemoteRegistry:
    """Connect to plugin marketplace."""

    async def search(self, query: str) -> List[PluginInfo]:
        """Search marketplace for plugins."""

    async def download(self, plugin_id: str) -> Path:
        """Download plugin from marketplace."""
```

## Security

- **Sandboxing**: Plugins run in isolated environments
- **Permission System**: Fine-grained capability model
- **Code Signing**: Verify plugin authenticity
- **Resource Limits**: CPU/memory constraints
- **Audit Logging**: Track all plugin operations

## Testing Plugins

```bash
# Unit test plugin
poetry run pytest tests/test_my_plugin.py

# Integration test with pipeline
poetry run flx-plugin test my-plugin --pipeline test-pipeline

# Performance test
poetry run flx-plugin benchmark my-plugin
```

## Performance Considerations

- Plugin discovery cached at startup
- Lazy loading for unused plugins
- Async/await throughout for non-blocking
- State checkpointing for recovery
- Resource pooling for efficiency

## Integration with Other Modules

- **flx-core**: Plugin infrastructure foundation
- **flx-meltano**: Singer protocol plugins
- **flx-cli**: Plugin management commands
- **flx-api**: Plugin configuration endpoints
- **flx-web**: Plugin management UI

## Next Steps

1. **Implement Hot Reload** (Primary Gap)

   - File system watcher
   - State preservation
   - Graceful transitions

2. **Plugin Marketplace**

   - Registry API
   - Version management
   - Dependency resolution

3. **Enhanced Security**
   - Sandboxing
   - Code signing
   - Resource limits

## License

Part of the FLX Platform - Enterprise License
