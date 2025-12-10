#!/usr/bin/env python3
"""FlextMeltano Bridge Script - CLI interface para integração Go ↔ Python.

Este script fornece interface CLI para comunicação entre FlexCore Go service
e flext-meltano Python library, retornando resultados em formato JSON.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from typing import TypeVar, Union

from flext_core import FlextResult
from flext_meltano.bridge import FlextMeltanoBridge

T = TypeVar("T", str, bool, dict[str, object])
CommandResult = dict[str, Union[str, bool, dict[str, object]]]


class FlextMeltanoBridgeScript:
    """CLI interface para integração Go ↔ Python com FlextMeltanoBridge."""

    def __init__(self) -> None:
        """Initialize the bridge script."""
        self.bridge = FlextMeltanoBridge()

    def _handle_result(
        self, result_obj: FlextResult[T], success_key: str
    ) -> CommandResult:
        """Generic handler for bridge results."""
        if result_obj.is_success:
            value = result_obj.value
            return {"status": "success", success_key: value}
        error_msg = result_obj.error or "Unknown error"
        return {"status": "error", "error": str(error_msg)}

    def handle_version(self) -> CommandResult:
        """Handle version command."""
        return self._handle_result(self.bridge.get_version(), "version")

    def handle_validate(self) -> CommandResult:
        """Handle validate command."""
        return self._handle_result(self.bridge.validate_connection(), "valid")

    def handle_discover(self) -> CommandResult:
        """Handle discover command."""
        return self._handle_result(self.bridge.discover_plugins(), "plugins")

    def handle_execute(self, args: list[str]) -> CommandResult:
        """Handle execute command."""
        if len(args) < 1:
            return {"status": "error", "error": "execute requires command argument"}

        exec_command = args[0]
        exec_args = json.loads(args[1]) if len(args) > 1 else None
        return self._handle_result(
            self.bridge.execute_command(exec_command, exec_args), "result"
        )

    def run(self) -> None:
        """Main CLI entry point."""
        if len(sys.argv) < 2:
            sys.exit(1)

        command = sys.argv[1]
        args = sys.argv[2:]

        handlers: dict[str, Callable[[], CommandResult]] = {
            "version": self.handle_version,
            "validate": self.handle_validate,
            "discover": self.handle_discover,
            "execute": lambda: self.handle_execute(args),
        }

        handler = handlers.get(
            command,
            lambda: {
                "status": "error",
                "error": f"Unknown command: {command}",
            },
        )
        output = handler()

        # Output JSON result for Go consumption
        print(json.dumps(output))


def main() -> None:
    """Main entry point."""
    script = FlextMeltanoBridgeScript()
    script.run()


if __name__ == "__main__":
    main()
