# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Scripts package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import scripts.ai_docstring_generator as _scripts_ai_docstring_generator

    ai_docstring_generator = _scripts_ai_docstring_generator
    from flext_core.constants import FlextConstants as c
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.models import FlextModels as m
    from flext_core.protocols import FlextProtocols as p
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from flext_core.typings import FlextTypes as t
    from flext_core.utilities import FlextUtilities as u
    from scripts.ai_docstring_generator import (
        CONTEXT_LINES,
        OLLAMA_BASE_URL,
        OLLAMA_MODEL,
        DocstringGenerator,
        DocstringInserter,
        MethodInfo,
        OllamaClient,
        PythonCodeAnalyzer,
        Validator,
    )
_LAZY_IMPORTS = {
    "CONTEXT_LINES": ("scripts.ai_docstring_generator", "CONTEXT_LINES"),
    "DocstringGenerator": ("scripts.ai_docstring_generator", "DocstringGenerator"),
    "DocstringInserter": ("scripts.ai_docstring_generator", "DocstringInserter"),
    "MethodInfo": ("scripts.ai_docstring_generator", "MethodInfo"),
    "OLLAMA_BASE_URL": ("scripts.ai_docstring_generator", "OLLAMA_BASE_URL"),
    "OLLAMA_MODEL": ("scripts.ai_docstring_generator", "OLLAMA_MODEL"),
    "OllamaClient": ("scripts.ai_docstring_generator", "OllamaClient"),
    "PythonCodeAnalyzer": ("scripts.ai_docstring_generator", "PythonCodeAnalyzer"),
    "Validator": ("scripts.ai_docstring_generator", "Validator"),
    "ai_docstring_generator": "scripts.ai_docstring_generator",
    "c": ("flext_core.constants", "FlextConstants"),
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": ("flext_core.models", "FlextModels"),
    "p": ("flext_core.protocols", "FlextProtocols"),
    "r": ("flext_core.result", "FlextResult"),
    "s": ("flext_core.service", "FlextService"),
    "t": ("flext_core.typings", "FlextTypes"),
    "u": ("flext_core.utilities", "FlextUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}

__all__ = [
    "CONTEXT_LINES",
    "OLLAMA_BASE_URL",
    "OLLAMA_MODEL",
    "DocstringGenerator",
    "DocstringInserter",
    "MethodInfo",
    "OllamaClient",
    "PythonCodeAnalyzer",
    "Validator",
    "ai_docstring_generator",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "u",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
