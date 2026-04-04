# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Infra package."""

from __future__ import annotations

from flext_core.lazy import install_lazy_exports

_LAZY_IMPORTS = {
    "FlextWorkspaceTestConstants": "tests.infra.constants",
    "FlextWorkspaceTestModels": "tests.infra.models",
    "FlextWorkspaceTestProtocols": "tests.infra.protocols",
    "FlextWorkspaceTestTypes": "tests.infra.typings",
    "FlextWorkspaceTestUtilities": "tests.infra.utilities",
    "c": ("tests.infra.constants", "FlextWorkspaceTestConstants"),
    "constants": "tests.infra.constants",
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": ("tests.infra.models", "FlextWorkspaceTestModels"),
    "models": "tests.infra.models",
    "p": ("tests.infra.protocols", "FlextWorkspaceTestProtocols"),
    "protocols": "tests.infra.protocols",
    "r": ("flext_core.result", "FlextResult"),
    "result": "tests.infra.result",
    "s": ("flext_core.service", "FlextService"),
    "t": ("tests.infra.typings", "FlextWorkspaceTestTypes"),
    "typings": "tests.infra.typings",
    "u": ("tests.infra.utilities", "FlextWorkspaceTestUtilities"),
    "utilities": "tests.infra.utilities",
    "x": ("flext_core.mixins", "FlextMixins"),
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
