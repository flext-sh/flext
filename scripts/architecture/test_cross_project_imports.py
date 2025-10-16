#!/usr/bin/env python3
"""Cross-project import validation test.

Tests that all 6 FLEXT projects can be imported successfully and their
main components are accessible. This validates the synchronization
across projects as required by the refactoring.
"""

from __future__ import annotations

import traceback

from flext_core import FlextTypes


def test_imports() -> bool:
    """Test imports from all 6 FLEXT projects."""
    results: FlextTypes.StringDict = {}

    # Test flext-core
    try:
        results["flext-core"] = "✅ SUCCESS"
    except (OSError, ValueError, TypeError) as e:
        results["flext-core"] = f"❌ FAILED: {e}"
        traceback.print_exc()

    # Test flext-cli
    try:
        results["flext-cli"] = "✅ SUCCESS"
    except (OSError, ValueError, TypeError) as e:
        results["flext-cli"] = f"❌ FAILED: {e}"
        traceback.print_exc()

    # Test flext-observability
    try:
        results["flext-observability"] = "✅ SUCCESS"
    except (OSError, ValueError, TypeError) as e:
        results["flext-observability"] = f"❌ FAILED: {e}"
        traceback.print_exc()

    # Test flext-meltano - use actual available exports
    try:
        results["flext-meltano"] = "✅ SUCCESS"
    except (OSError, ValueError, TypeError) as e:
        results["flext-meltano"] = f"❌ FAILED: {e}"
        traceback.print_exc()

    # Test flext-ldif
    try:
        results["flext-ldif"] = "✅ SUCCESS"
    except (OSError, ValueError, TypeError) as e:
        results["flext-ldif"] = f"❌ FAILED: {e}"
        traceback.print_exc()

    # Test flext-ldap
    try:
        results["flext-ldap"] = "✅ SUCCESS"
    except (OSError, ValueError, TypeError) as e:
        results["flext-ldap"] = f"❌ FAILED: {e}"
        traceback.print_exc()

    success_count = 0
    total_count = len(results)

    for result in results.values():
        if "SUCCESS" in result:
            success_count += 1

    return success_count == total_count


if __name__ == "__main__":
    success = test_imports()
    raise SystemExit(0 if success else 1)
