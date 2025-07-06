#!/usr/bin/env python3
"""Python wrapper for Meltano Go functions via ctypes
This provides a proper Python interface for the gopy-generated Go library.
"""

import ctypes
import ctypes.util
import json
from pathlib import Path


class MeltanoGopyError(Exception):
    """Custom exception for Meltano Gopy errors."""


class MeltanoGopy:
    """Python interface to Go-based Meltano functionality."""

    def __init__(self) -> None:
        """Initialize the Meltano Gopy interface."""
        self._lib = None
        self._load_library()
        self._setup_functions()

    def _load_library(self) -> None:
        """Load the Go shared library."""
        lib_path = Path(__file__).parent / "gopy_go.so"

        if not lib_path.exists():
            msg = f"Go library not found at {lib_path}"
            raise MeltanoGopyError(msg)

        try:
            self._lib = ctypes.CDLL(str(lib_path))
            # Initialize the Go library
            self._lib.GoPyInit()
        except Exception as e:
            msg = f"Failed to load Go library: {e}"
            raise MeltanoGopyError(msg)

    def _setup_functions(self) -> None:
        """Setup function signatures for ctypes."""
        # CheckMeltanoAvailable() bool
        self._lib.gopy_CheckMeltanoAvailable.restype = ctypes.c_bool
        self._lib.gopy_CheckMeltanoAvailable.argtypes = []

        # GetMeltanoVersion() string
        self._lib.gopy_GetMeltanoVersion.restype = ctypes.c_char_p
        self._lib.gopy_GetMeltanoVersion.argtypes = []

        # CreateProject(directory, name string) string
        self._lib.gopy_CreateProject.restype = ctypes.c_char_p
        self._lib.gopy_CreateProject.argtypes = [ctypes.c_char_p, ctypes.c_char_p]

        # AddPluginToProject(pluginType, name, variant string) string
        self._lib.gopy_AddPluginToProject.restype = ctypes.c_char_p
        self._lib.gopy_AddPluginToProject.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]

        # RunMeltanoPipeline(extractor, loader, transformer string) string
        self._lib.gopy_RunMeltanoPipeline.restype = ctypes.c_char_p
        self._lib.gopy_RunMeltanoPipeline.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]

        # GetProjectPlugins() string
        self._lib.gopy_GetProjectPlugins.restype = ctypes.c_char_p
        self._lib.gopy_GetProjectPlugins.argtypes = []

    def _call_string_function(self, func, *args):
        """Helper to call Go functions that return JSON strings."""
        try:
            # Convert string arguments to bytes
            byte_args = [
                arg.encode("utf-8") if isinstance(arg, str) else arg for arg in args
            ]

            # Call the function
            result = func(*byte_args)

            # Convert result to string and parse JSON
            if result:
                json_str = result.decode("utf-8")
                return json.loads(json_str)
            return {"success": False, "error": "No result returned"}

        except Exception as e:
            return {"success": False, "error": f"Function call failed: {e}"}

    def check_meltano_available(self):
        """Check if Meltano CLI is available."""
        try:
            return self._lib.gopy_CheckMeltanoAvailable()
        except Exception as e:
            msg = f"Failed to check Meltano availability: {e}"
            raise MeltanoGopyError(msg)

    def get_meltano_version(self):
        """Get Meltano version information."""
        return self._call_string_function(self._lib.gopy_GetMeltanoVersion)

    def create_project(self, directory, name):
        """Create a new Meltano project."""
        return self._call_string_function(self._lib.gopy_CreateProject, directory, name)

    def add_plugin(self, plugin_type, name, variant=""):
        """Add a plugin to the current project."""
        return self._call_string_function(
            self._lib.gopy_AddPluginToProject, plugin_type, name, variant
        )

    def run_pipeline(self, extractor, loader, transformer=""):
        """Run a Meltano ELT pipeline."""
        return self._call_string_function(
            self._lib.gopy_RunMeltanoPipeline, extractor, loader, transformer
        )

    def get_plugins(self):
        """Get all plugins in the current project."""
        return self._call_string_function(self._lib.gopy_GetProjectPlugins)


# Module-level convenience functions
_meltano_instance = None


def get_meltano_instance():
    """Get or create the global Meltano instance."""
    global _meltano_instance
    if _meltano_instance is None:
        _meltano_instance = MeltanoGopy()
    return _meltano_instance


def CheckMeltanoAvailable():
    """Check if Meltano is available (compatibility function)."""
    return get_meltano_instance().check_meltano_available()


def GetMeltanoVersion():
    """Get Meltano version (compatibility function)."""
    return get_meltano_instance().get_meltano_version()


def CreateProject(directory, name):
    """Create project (compatibility function)."""
    return get_meltano_instance().create_project(directory, name)


if __name__ == "__main__":
    # Test the wrapper

    try:
        meltano = MeltanoGopy()

        # Test availability check
        available = meltano.check_meltano_available()

        # Test version
        version = meltano.get_meltano_version()

    except Exception:
        pass
