#!/usr/bin/env python3
"""
Basic test to verify installation and imports.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("🚀 FLX-Meltano Enterprise Basic Test")
print("=" * 40)

# Test 1: Import core modules
print("\n1️⃣ Testing core imports...")
try:
    import flx

    print("✅ flx imported successfully")
    print(f"   Version: {flx.__version__}")
except ImportError as e:
    print(f"❌ Failed to import flx: {e}")

# Test 2: Import config
print("\n2️⃣ Testing configuration...")
try:
    from flx.config import settings

    print("✅ Settings imported successfully")
    print(f"   Environment: {settings.environment}")
    print(f"   gRPC Port: {settings.grpc_port}")
    print(f"   Database URL: {settings.database_url[:30]}...")
except Exception as e:
    print(f"❌ Failed to load config: {e}")

# Test 3: Import API modules
print("\n3️⃣ Testing API imports...")
try:
    import flx_api

    print("✅ flx_api imported successfully")
except ImportError as e:
    print(f"❌ Failed to import flx_api: {e}")

# Test 4: Import CLI modules
print("\n4️⃣ Testing CLI imports...")
try:
    import flx_cli

    print("✅ flx_cli imported successfully")
except ImportError as e:
    print(f"❌ Failed to import flx_cli: {e}")

# Test 5: Import Web modules
print("\n5️⃣ Testing Web imports...")
try:
    import flx_web

    print("✅ flx_web imported successfully")
except ImportError as e:
    print(f"❌ Failed to import flx_web: {e}")

# Test 6: Test FastAPI
print("\n6️⃣ Testing FastAPI...")
try:
    from fastapi import FastAPI

    app = FastAPI()
    print("✅ FastAPI working")
except Exception as e:
    print(f"❌ FastAPI error: {e}")

# Test 7: Test Django
print("\n7️⃣ Testing Django...")
try:
    import django

    print(f"✅ Django {django.__version__} imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Django: {e}")

print("\n" + "=" * 40)
print("✨ Test completed!")
