"""Unified script service for FLEXT platform.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import argparse
from abc import abstractmethod
from typing import Self

from flext_core import FlextCore
from pydantic import BaseModel


class FlextScriptService(FlextCore.Service[object]):
    """Unified script service with nested helpers.

    Single responsibility: Script execution and management.
    """

    class ScriptMetadata(BaseModel):
        """Metadata for FLEXT scripts."""

        name: str
        description: str
        category: str
        version: str = "1.0.0"

    class _ParserHelper:
        """Nested helper for argument parsing."""

        @staticmethod
        def create_parser(
            metadata: FlextScriptService.ScriptMetadata,
        ) -> argparse.ArgumentParser:
            """Create argument parser."""
            parser = argparse.ArgumentParser(
                description=metadata.description,
                prog=metadata.name,
            )
            parser.add_argument(
                "--version",
                action="version",
                version=f"{metadata.name} {metadata.version}",
            )
            return parser

    class _ValidationHelper:
        """Nested helper for validation."""

        @staticmethod
        def validate_preconditions() -> FlextCore.Result[None]:
            """Validate script preconditions.

            🚨 AUDIT VIOLATION: Empty validation method instead of proper models validation!
            ❌ CRITICAL ISSUE: This method provides no actual validation
            ❌ MISSING VALIDATION: Should use FlextCore.Models.Validation.validate_script_preconditions()

            🔧 REQUIRED ACTION:
            - Replace with FlextCore.Models.Validation.validate_script_preconditions()
            - Use FlextCore.Models.ScriptMetadata validation for script validation
            - Implement proper precondition validation logic

            📍 SHOULD BE USED INSTEAD: FlextCore.Models.Validation.validate_script_preconditions(metadata)
            """
            # 🚨 AUDIT VIOLATION: Empty validation - should use FlextCore.Models.Validation
            return FlextCore.Result[None].ok(None)

    @property
    @abstractmethod
    def metadata(self: Self) -> ScriptMetadata:
        """Get script metadata."""

    def execute(self: Self) -> FlextCore.Result[object]:
        """Execute script service - FlextCore.Service interface."""
        return self.run({})

    def create_parser(self: Self) -> argparse.ArgumentParser:
        """Create argument parser using nested helper."""
        return self._ParserHelper.create_parser(self.metadata)

    def validate_preconditions(self: Self) -> FlextCore.Result[None]:
        """Validate preconditions using nested helper."""
        return self._ValidationHelper.validate_preconditions()

    def run(self, args: FlextCore.Types.Dict | None = None) -> FlextCore.Result[object]:
        """Run the script."""
        # 🚨 AUDIT VIOLATION: Using empty validation method - should use FlextCore.Models.Validation
        validation_result = self.validate_preconditions()
        if validation_result.is_failure:
            return FlextCore.Result[object].fail(
                validation_result.error or "Precondition validation failed",
            )

        return self.execute_implementation(args or {})

    def main(self: Self) -> int:
        """Main entry point for script."""
        try:
            parser = self.create_parser()
            args = parser.parse_args()
            arg_dict: FlextCore.Types.Dict = vars(args)

            result: FlextCore.Result[object] = self.run(arg_dict)
            if result.is_success:
                return 0
            return 1
        except Exception:
            return 1

    @abstractmethod
    def execute_implementation(
        self, args: FlextCore.Types.Dict
    ) -> FlextCore.Result[object]:
        """Execute script implementation."""


# LEGACY ALIASES ELIMINATED - Use FlextScriptService directly:
# Use: FlextScriptService instead of FlextScript
# Use: FlextScriptService.ScriptMetadata instead of ScriptMetadata

__all__ = ["FlextScriptService"]
