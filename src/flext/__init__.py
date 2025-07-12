"""FLEXT - Multi-Project Workspace Coordinator for Enterprise Data Integration."""

from flext_core.domain.constants import FlextFramework

__version__ = FlextFramework.VERSION
__author__ = "FLEXT Team"
__email__ = "team@flext.sh"
__license__ = "MIT"
__homepage__ = "https://github.com/flext-sh/flext"

# Re-export commonly used components
from flext.cli import main as cli_main
from flext.dev import DevToolsManager

# Workspace management
from flext.workspace import WorkspaceManager
from flext_core import *

__all__ = [
    "DevToolsManager",
    "WorkspaceManager",
    "cli_main",
]
