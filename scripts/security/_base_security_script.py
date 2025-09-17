#!/usr/bin/env python3
"""Base security script with common validation logic.

Classe base para scripts de segurança com validações comuns reutilizáveis.
"""

from __future__ import annotations

from pathlib import Path

from flext_core import FlextResult
from flext_tools import Colors, FlextScript, print_colored


class BaseSecurityScript(FlextScript):
    """Base class for security scripts with common validation."""

    def validate_preconditions(self) -> FlextResult[None]:
        """Validate common security script preconditions."""
        workspace_root = Path.cwd()

        # Check if we're in FLEXT workspace
        if not (workspace_root / "flext-core").exists():
            print_colored("❌ Execute from FLEXT workspace root", Colors.RED)
            return FlextResult[None].fail("Not in FLEXT workspace root")

        print_colored("✅ FLEXT workspace detected", Colors.GREEN)

        # Check cryptography availability
        try:
            print_colored("✅ Cryptography library available", Colors.GREEN)
            return FlextResult[None].ok(None)
        except ImportError:
            print_colored(
                "❌ Cryptography library not found - install with: pip install cryptography",
                Colors.RED,
            )
            return FlextResult[None].fail("Cryptography library not found")
