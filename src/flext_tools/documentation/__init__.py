"""FLEXT Documentation Generation Module.

Provides comprehensive documentation generation capabilities for the FLEXT ecosystem
using Jinja2 templates, MkDocs integration, and automated content generation.
"""

from __future__ import annotations

from flext_tools.documentation.generator import DocumentationGenerator
from flext_tools.documentation.templates import TemplateManager

__all__ = ["DocumentationGenerator", "TemplateManager"]
