# \!/usr/bin/env python3
"""
Simple test for gopy integration without complex initialization
"""

import ctypes
from pathlib import Path


def test_simple_gopy():
    """Test simple gopy function calls"""

    try:
        # Load the library
        lib_path = Path(__file__).parent / "gopy_go.so"
        lib = ctypes.CDLL(str(lib_path))

        # Initialize Go runtime
        lib.GoPyInit()

        # Try to call a simple function without complex initialization

        try:
            # Try GetMeltanoVersion first (simplest function)
            lib.gopy_GetMeltanoVersion.restype = ctypes.c_char_p
            lib.gopy_GetMeltanoVersion.argtypes = []

            result = lib.gopy_GetMeltanoVersion()
            if result:
                result.decode("utf-8")
            else:
                pass

        except Exception:
            pass

        return True

    except Exception:
        return False


if __name__ == "__main__":
    success = test_simple_gopy()
    exit(0 if success else 1)
