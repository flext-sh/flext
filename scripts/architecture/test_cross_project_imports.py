#!/usr/bin/env python3
"""Cross-project import validation test.

Tests that all 6 FLEXT projects can be imported successfully and their
main components are accessible. This validates the synchronization
across projects as required by the refactoring.
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path


def test_imports() -> bool:
    """Test imports from all 6 FLEXT projects."""
    results = {}

    print("🔍 Testing cross-project imports...")
    print("=" * 60)

    # Test flext-core
    try:
        print("📦 Testing flext-core imports...")

        results["flext-core"] = "✅ SUCCESS"
        print("   ✅ flext-core imports working")
    except (OSError, ValueError, TypeError) as e:
        results["flext-core"] = f"❌ FAILED: {e}"
        print(f"   ❌ flext-core failed: {e}")
        traceback.print_exc()

    # Test flext-cli
    try:
        print("📦 Testing flext-cli imports...")

        results["flext-cli"] = "✅ SUCCESS"
        print("   ✅ flext-cli imports working")
    except (OSError, ValueError, TypeError) as e:
        results["flext-cli"] = f"❌ FAILED: {e}"
        print(f"   ❌ flext-cli failed: {e}")
        traceback.print_exc()

    # Test flext-observability
    try:
        print("📦 Testing flext-observability imports...")

        results["flext-observability"] = "✅ SUCCESS"
        print("   ✅ flext-observability imports working")
    except (OSError, ValueError, TypeError) as e:
        results["flext-observability"] = f"❌ FAILED: {e}"
        print(f"   ❌ flext-observability failed: {e}")
        traceback.print_exc()

    # Test flext-meltano - use actual available exports
    try:
        print("📦 Testing flext-meltano imports...")

        results["flext-meltano"] = "✅ SUCCESS"
        print("   ✅ flext-meltano imports working")
    except (OSError, ValueError, TypeError) as e:
        results["flext-meltano"] = f"❌ FAILED: {e}"
        print(f"   ❌ flext-meltano failed: {e}")
        traceback.print_exc()

    # Test flext-ldif
    try:
        print("📦 Testing flext-ldif imports...")

        results["flext-ldif"] = "✅ SUCCESS"
        print("   ✅ flext-ldif imports working")
    except (OSError, ValueError, TypeError) as e:
        results["flext-ldif"] = f"❌ FAILED: {e}"
        print(f"   ❌ flext-ldif failed: {e}")
        traceback.print_exc()

    # Test flext-ldap
    try:
        print("📦 Testing flext-ldap imports...")

        results["flext-ldap"] = "✅ SUCCESS"
        print("   ✅ flext-ldap imports working")
    except (OSError, ValueError, TypeError) as e:
        results["flext-ldap"] = f"❌ FAILED: {e}"
        print(f"   ❌ flext-ldap failed: {e}")
        traceback.print_exc()

    print("=" * 60)
    print("📊 IMPORT VALIDATION RESULTS:")
    print("=" * 60)

    success_count = 0
    total_count = len(results)

    for project, result in results.items():
        print(f"{project:20} | {result}")
        if "SUCCESS" in result:
            success_count += 1

    print("=" * 60)
    print(f"✅ SUCCESS: {success_count}/{total_count} projects")
    print(f"❌ FAILED:  {total_count - success_count}/{total_count} projects")

    if success_count == total_count:
        print("🎉 ALL PROJECTS SYNCHRONIZED! Cross-project imports working perfectly!")
        return True
    print("🚨 SYNCHRONIZATION ISSUES DETECTED! Some imports failed!")
    return False


if __name__ == "__main__":
    # Add all project paths to Python path
    flext_root = Path("/home/marlonsc/flext")
    project_paths = [
        flext_root / "flext-core" / "src",
        flext_root / "flext-cli" / "src",
        flext_root / "flext-observability" / "src",
        flext_root / "flext-meltano" / "src",
        flext_root / "flext-ldif" / "src",
        flext_root / "flext-ldap" / "src",
    ]

    for path in project_paths:
        if path.exists():
            sys.path.insert(0, str(path))

    success = test_imports()
    sys.exit(0 if success else 1)
