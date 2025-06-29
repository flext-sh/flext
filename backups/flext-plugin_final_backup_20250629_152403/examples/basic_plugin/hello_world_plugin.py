"""Basic hello world plugin example.

Demonstrates the minimal plugin implementation with FLX plugin system.
"""

from typing import Any, Dict

from flx_plugin import Plugin, PluginMetadata, PluginType


class HelloWorldPlugin(Plugin):
    """Simple hello world plugin example."""

    @classmethod
    def get_metadata(cls) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            id="hello-world",
            name="Hello World Plugin",
            version="1.0.0",
            description="A simple hello world plugin example",
            plugin_type=PluginType.UTILITY,
            author="FLX Team",
            license="MIT",
            capabilities=["greeting", "example"],
            dependencies=[],
            configuration_schema={
                "type": "object",
                "properties": {
                    "greeting": {
                        "type": "string",
                        "default": "Hello",
                        "description": "Greeting to use",
                    },
                    "name": {
                        "type": "string",
                        "default": "World",
                        "description": "Name to greet",
                    },
                },
                "required": [],
            },
        )

    async def initialize(self) -> None:
        """Initialize the plugin."""
        self.logger.info("Hello World plugin initialized")

        # Get configuration
        self.greeting = self.config.get("greeting", "Hello")
        self.name = self.config.get("name", "World")

    async def execute(self, input_data: Any, context: Dict[str, Any]) -> Any:
        """Execute the plugin functionality.

        Args:
        ----
            input_data: Input data (unused in this example)
            context: Execution context

        Returns:
        -------
            Greeting message

        """
        # Get name from input if provided
        if isinstance(input_data, dict) and "name" in input_data:
            name = input_data["name"]
        else:
            name = self.name

        message = f"{self.greeting}, {name}!"

        self.logger.info(f"Generated greeting: {message}")

        return {
            "message": message,
            "plugin": self.metadata.name,
            "version": self.metadata.version,
            "timestamp": context.get("execution_time"),
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        return {
            "status": "healthy",
            "message": "Hello World plugin is running",
            "config": {
                "greeting": self.greeting,
                "name": self.name,
            },
        }

    async def cleanup(self) -> None:
        """Clean up plugin resources."""
        self.logger.info("Hello World plugin cleanup completed")


# Entry point for plugin discovery
plugin_class = HelloWorldPlugin
