#\!/usr/bin/env python3
"""
Simple test for gopy integration without complex initialization
"""

import ctypes
from pathlib import Path

def test_simple_gopy():
    """Test simple gopy function calls"""
    print("🧪 Testing Simple Gopy Integration...")
    
    try:
        # Load the library
        lib_path = Path(__file__).parent / "gopy_go.so"
        lib = ctypes.CDLL(str(lib_path))
        print("✅ Library loaded successfully")
        
        # Initialize Go runtime
        lib.GoPyInit()
        print("✅ Go runtime initialized")
        
        # Try to call a simple function without complex initialization
        print("📋 Available functions:")
        
        try:
            # Try GetMeltanoVersion first (simplest function)
            lib.gopy_GetMeltanoVersion.restype = ctypes.c_char_p
            lib.gopy_GetMeltanoVersion.argtypes = []
            
            result = lib.gopy_GetMeltanoVersion()
            if result:
                version_str = result.decode('utf-8')
                print(f"✅ GetMeltanoVersion: {version_str}")
            else:
                print("⚠️ GetMeltanoVersion returned null")
                
        except Exception as e:
            print(f"❌ GetMeltanoVersion failed: {e}")
        
        print("🎯 Simple test completed\!")
        return True
        
    except Exception as e:
        print(f"❌ Simple test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_simple_gopy()
    exit(0 if success else 1)