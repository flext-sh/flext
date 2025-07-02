#!/usr/bin/env python3
"""
Final FLEXT Meltano Integration Test
"""

import os

# Test 1: Test the gopy-generated library
try:
    old_cwd = os.getcwd()
    os.chdir('/home/marlonsc/flext/python-meltano-gopy')

    # Import the gopy-generated module
    import meltano

    # Check available functions
    available_functions = [attr for attr in dir(meltano) if not attr.startswith('_')]

    # Try to create an adapter
    if hasattr(meltano, 'NewMeltanoAdapter'):
        try:
            adapter = meltano.NewMeltanoAdapter()

            # Test adapter methods
            if hasattr(adapter, 'IsAvailable'):
                available = adapter.IsAvailable()
        except Exception:
            pass

    if hasattr(meltano, 'QuickCheck'):
        available = meltano.QuickCheck()

except Exception:
    pass
finally:
    os.chdir(old_cwd)


# Test 2: Test HTTP API directly
try:
    import requests

    # Test health endpoint
    response = requests.get('http://localhost:8081/health', timeout=5)

    # Test Meltano availability via API
    response = requests.get('http://localhost:8081/api/v1/meltano/health', timeout=10)

    # Test command execution
    command_data = {
        "command": "version",
        "args": []
    }
    response = requests.post('http://localhost:8081/api/v1/meltano/projects/test/command',
                           json=command_data, timeout=10)
    if response.status_code == 200:
        pass

except Exception:
    pass

