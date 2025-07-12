# FLX CLI Migration Guide: From Cyclopts to Python Fire with Command Bus

## Overview

This guide explains how to migrate from the previous cyclopts-based CLI to the new Python Fire CLI that uses the command bus architecture. The new architecture provides better separation of concerns and allows multiple interfaces (CLI, REST, Web) to share the same business logic.

## Key Changes

### 1. Library Change: Cyclopts → Python Fire

**Before (Cyclopts):**

```python
from cyclopts import App

app = App()

@app.command
def start():
    """Start the application."""
    # Direct implementation
    return application.start()
```

**After (Python Fire):**

```python
import fire

class FlxFireCLI:
    def start(self):
        """Start the application."""
        command = StartApplicationCommand()
        result = self._command_bus.execute_command(command)
        return result.data
```

### 2. Architecture: Direct Implementation → Command Bus

**Before:**

- CLI commands directly called application methods
- Business logic mixed with CLI code
- Difficult to share logic with other interfaces

**After:**

- CLI commands create Command/Query objects
- Commands are executed through the command bus
- Business logic is in handlers, separate from interface
- Same commands can be executed from REST API, WebSocket, etc.

## Migration Steps

### Step 1: Update Dependencies

```toml
# pyproject.toml
[tool.poetry.dependencies]
# Remove
# cyclopts = "^3.17.0"

# Add
fire = "^0.7.0"
```

### Step 2: Create Command Layer

Create commands for your existing CLI operations:

```python
# src/your_project/commands/app_commands.py
from flx.core.commands import Command, Query

class StartApplicationCommand(Command):
    """Command to start the application."""
    pass

class GetApplicationStatusQuery(Query):
    """Query to get application status."""
    include_adapters: bool = True
```

### Step 3: Create Command Handlers

Move business logic from CLI to handlers:

```python
# src/your_project/handlers/app_handlers.py
from flx.core.commands.registry import command_handler, query_handler

@command_handler
class StartApplicationHandler(CommandHandler[StartApplicationCommand, dict]):
    def __init__(self, app: Application):
        self.app = app

    async def handle(self, command: StartApplicationCommand) -> dict:
        await self.app.start()
        return {"status": "started", "timestamp": datetime.utcnow()}

@query_handler
class GetApplicationStatusHandler(QueryHandler[GetApplicationStatusQuery, dict]):
    def __init__(self, app: Application):
        self.app = app

    async def handle(self, query: GetApplicationStatusQuery) -> dict:
        status = self.app.get_status()
        if query.include_adapters:
            status["adapters"] = self.app.list_adapters()
        return status
```

### Step 4: Create Fire CLI Adapter

```python
# src/your_project/cli/fire_cli.py
import fire
import asyncio
from flx.core.commands import CommandBus

class MyProjectCLI:
    def __init__(self, command_bus: CommandBus):
        self._command_bus = command_bus

    def start(self):
        """Start the application."""
        command = StartApplicationCommand()
        result = asyncio.run(self._command_bus.execute_command(command))
        if result.success:
            return result.data.get("message", "Application started")
        return f"Error: {result.error}"

    def status(self, include_adapters: bool = True):
        """Get application status."""
        query = GetApplicationStatusQuery(include_adapters=include_adapters)
        return asyncio.run(self._command_bus.execute_query(query))

def main():
    """Entry point for Fire CLI."""
    command_bus = create_command_bus()  # Your setup
    cli = MyProjectCLI(command_bus)
    fire.Fire(cli)
```

### Step 5: Update Entry Point

```python
# pyproject.toml
[tool.poetry.scripts]
myproject = "myproject.cli.fire_cli:main"
```

## Command Structure Comparison

### Cyclopts Style

```python
# Flat command structure
$ myapp start
$ myapp stop
$ myapp config-get key
$ myapp adapter-list
```

### Fire Style

```python
# Nested command structure (recommended)
$ myapp start              # Direct method
$ myapp config get key     # Nested via class
$ myapp adapter list       # Nested via class

# Or flat if preferred
$ myapp start
$ myapp get_config key
$ myapp list_adapters
```

## Best Practices for Fire CLI

### 1. Use Nested Command Groups

```python
class MyProjectCLI:
    def __init__(self, command_bus: CommandBus):
        self._command_bus = command_bus
        self.config = ConfigCommands(command_bus)
        self.adapter = AdapterCommands(command_bus)

class ConfigCommands:
    def get(self, key: str):
        """Get configuration value."""
        pass

    def set(self, key: str, value: str):
        """Set configuration value."""
        pass
```

### 2. Provide Clear Docstrings

Fire uses docstrings for help text:

```python
def deploy(self, environment: str, version: str, dry_run: bool = False):
    """Deploy application to specified environment.

    Args:
        environment: Target environment (dev, staging, prod)
        version: Version to deploy
        dry_run: If True, only show what would be deployed

    Example:
        myapp deploy prod 1.2.3 --dry-run
    """
```

### 3. Handle Async Operations

```python
def start(self):
    """Start the application."""
    command = StartApplicationCommand()
    # Fire doesn't support async, so use asyncio.run
    result = asyncio.run(self._command_bus.execute_command(command))
    return self._format_result(result)
```

### 4. Return Structured Data

Fire automatically formats output:

```python
def status(self):
    """Get status."""
    return {
        "status": "running",
        "uptime": "2 hours",
        "adapters": ["database", "cache", "queue"]
    }
# Fire will pretty-print this as structured output
```

## Testing Migration

### Before (Cyclopts)

```python
def test_start_command():
    app = create_test_app()
    result = app.start()
    assert result == "Started"
```

### After (Fire with Command Bus)

```python
def test_start_command():
    mock_bus = Mock(spec=CommandBus)
    mock_bus.execute_command.return_value = CommandResult.ok({"status": "started"})

    cli = MyProjectCLI(command_bus=mock_bus)
    result = cli.start()

    assert "started" in result
    mock_bus.execute_command.assert_called_once()
```

## Benefits of the New Architecture

1. **Separation of Concerns**: CLI is just an adapter, business logic is in handlers
2. **Reusability**: Same commands work with REST API, GraphQL, WebSocket, etc.
3. **Testability**: Easy to unit test each layer independently
4. **Flexibility**: Can switch CLI libraries without changing business logic
5. **Type Safety**: Commands and queries are fully typed with Pydantic

## Common Pitfalls and Solutions

### Pitfall 1: Direct Business Logic in CLI

**Don't:**

```python
def start(self):
    # Business logic in CLI
    self.validate_config()
    self.initialize_database()
    self.start_services()
```

**Do:**

```python
def start(self):
    # Delegate to command handler
    command = StartApplicationCommand()
    return self._execute_command(command)
```

### Pitfall 2: Synchronous Fire with Async Handlers

**Problem:** Fire doesn't natively support async
**Solution:** Use `asyncio.run()` in CLI methods

```python
def start(self):
    result = asyncio.run(self._command_bus.execute_command(command))
```

### Pitfall 3: Complex Argument Parsing

**Fire Limitation:** Less control over argument parsing than Cyclopts
**Solution:** Use type hints and docstrings effectively

```python
def deploy(self, environment: str, version: str = "latest",
          force: bool = False, timeout: int = 300):
    """Deploy with proper type hints for Fire to parse."""
```

## Example: Complete Migration

See `/home/marlonsc/pyauto/flx/examples/fire_cli_complete_example.py` for a complete example showing:

- Custom commands and handlers
- Extending the base Fire CLI
- Integration with command bus
- Testing strategies
- Multi-interface support
