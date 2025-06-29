"""Stateful counter plugin example.

Demonstrates state preservation and hot reload capabilities.
"""

from typing import Any, Dict

from flx_plugin import Plugin, PluginMetadata, PluginType


class CounterPlugin(Plugin):
    """Stateful counter plugin with hot reload support."""

    @classmethod
    def get_metadata(cls) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            id="counter-plugin",
            name="Counter Plugin",
            version="1.0.0",
            description="A stateful counter plugin that preserves state across reloads",
            plugin_type=PluginType.PROCESSOR,
            author="FLX Team",
            license="MIT",
            capabilities=["counting", "state_preservation"],
            dependencies=[],
            configuration_schema={
                "type": "object",
                "properties": {
                    "initial_value": {
                        "type": "integer",
                        "default": 0,
                        "description": "Initial counter value",
                    },
                    "increment": {
                        "type": "integer",
                        "default": 1,
                        "description": "Increment value",
                    },
                    "max_value": {
                        "type": "integer",
                        "default": 1000000,
                        "description": "Maximum counter value",
                    },
                },
                "required": [],
            },
        )

    async def initialize(self) -> None:
        """Initialize the plugin."""
        self.logger.info("Counter plugin initializing")

        # Get configuration
        self.increment = self.config.get("increment", 1)
        self.max_value = self.config.get("max_value", 1000000)

        # Initialize state
        self.counter = self.config.get("initial_value", 0)
        self.total_operations = 0
        self.last_reset_at = None

        self.logger.info(f"Counter initialized at {self.counter}")

    async def execute(self, input_data: Any, context: Dict[str, Any]) -> Any:
        """Execute counter operation.

        Args:
        ----
            input_data: Operation command (increment, decrement, reset, get)
            context: Execution context

        Returns:
        -------
            Counter state and operation result

        """
        operation = "increment"  # default

        if isinstance(input_data, str):
            operation = input_data.lower()
        elif isinstance(input_data, dict):
            operation = input_data.get("operation", "increment")

        self.total_operations += 1

        result = {
            "operation": operation,
            "previous_value": self.counter,
        }

        if operation == "increment":
            new_value = min(self.counter + self.increment, self.max_value)
            self.counter = new_value
            result["new_value"] = new_value
            result["changed"] = new_value != result["previous_value"]

        elif operation == "decrement":
            new_value = max(self.counter - self.increment, 0)
            self.counter = new_value
            result["new_value"] = new_value
            result["changed"] = new_value != result["previous_value"]

        elif operation == "reset":
            self.counter = self.config.get("initial_value", 0)
            self.last_reset_at = context.get("execution_time")
            result["new_value"] = self.counter
            result["reset"] = True

        elif operation == "get":
            result["value"] = self.counter

        else:
            result["error"] = f"Unknown operation: {operation}"
            result["value"] = self.counter

        result["total_operations"] = self.total_operations

        self.logger.debug(f"Counter operation: {operation}, value: {self.counter}")

        return result

    async def get_state(self) -> Dict[str, Any]:
        """Get plugin state for preservation.

        Returns
        -------
            Current plugin state

        """
        return {
            "counter": self.counter,
            "total_operations": self.total_operations,
            "last_reset_at": self.last_reset_at,
        }

    async def set_state(self, state: Dict[str, Any]) -> None:
        """Restore plugin state.

        Args:
        ----
            state: State to restore

        """
        self.counter = state.get("counter", 0)
        self.total_operations = state.get("total_operations", 0)
        self.last_reset_at = state.get("last_reset_at")

        self.logger.info(
            f"State restored: counter={self.counter}, "
            f"operations={self.total_operations}"
        )

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        return {
            "status": "healthy",
            "counter_value": self.counter,
            "total_operations": self.total_operations,
            "config": {
                "increment": self.increment,
                "max_value": self.max_value,
            },
            "state_preservation": True,
        }

    async def cleanup(self) -> None:
        """Clean up plugin resources."""
        self.logger.info(
            f"Counter plugin cleanup - final value: {self.counter}, "
            f"total operations: {self.total_operations}"
        )


# Entry point for plugin discovery
plugin_class = CounterPlugin
