#!/usr/bin/env python3
"""FLEXT Ecosystem Equilibrium Validation Script.

Validates that all domain libraries follow the equilibrium pattern:
- Constants classes extend FlextCore.Constants
- Config classes extend FlextCore.Config
- Models classes extend FlextCore.Models

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

ResultType = Literal["extends", "error", "foundation"]


def validate_equilibrium() -> int:
    """Validate ecosystem equilibrium across all FLEXT libraries.

    Returns:
        Exit code: 0 if 100% equilibrium, 1 otherwise

    """
    print("=" * 80)
    print("FLEXT ECOSYSTEM EQUILIBRIUM VALIDATION")
    print("=" * 80)
    print()

    # Results tracking
    results: dict[str, list[tuple[str, str, str, ResultType | None]]] = {
        "constants": [],
        "config": [],
        "models": [],
    }

    # Domain libraries to validate (order matters - core first)
    domain_libraries = [
        ("flext-core", "core"),
        ("flext-api", "api"),
        ("flext-cli", "cli"),
        ("flext-ldap", "ldap"),
        ("flext-ldif", "ldif"),
        ("flext-db-oracle", "db_oracle"),
        ("flext-auth", "auth"),
        ("flext-web", "web"),
        ("flext-meltano", "meltano"),
        ("flext-grpc", "grpc"),
        ("flext-observability", "observability"),
    ]

    # Get workspace root (script is in scripts/, workspace is parent)
    workspace_root = Path(__file__).parent.parent

    # Add flext-core to path FIRST
    core_path = workspace_root / "flext-core" / "src"
    if core_path.exists():
        sys.path.insert(0, str(core_path))

    # Load foundation
    try:
        from flext_core import FlextCore

        print("✅ Flext foundation loaded\n")
    except Exception as e:
        print(f"❌ Failed to load Flext foundation: {e}\n")
        return 1

    # Validate each library
    for lib_dir, domain in domain_libraries:
        lib_path = workspace_root / lib_dir / "src"
        if not lib_path.exists():
            # Library doesn't exist in workspace - skip
            continue

        # Add to path
        if str(lib_path) not in sys.path:
            sys.path.insert(0, str(lib_path))

        # Test Constants
        try:
            if lib_dir == "flext-core":
                results["constants"].append((
                    lib_dir,
                    "FlextCore.Constants",
                    "✅ FOUNDATION",
                    "foundation",
                ))
            else:
                module_name = f"flext_{domain}.constants"
                class_name = f"Flext{domain.title().replace('_', '')}Constants"

                # Import module using __import__
                module = __import__(module_name, fromlist=[class_name])
                const_cls = getattr(module, class_name)

                # Check inheritance
                extends = issubclass(const_cls, FlextCore.Constants)
                status = (
                    "✅ EXTENDS FlextCore.Constants"
                    if extends
                    else "❌ DOES NOT EXTEND FlextCore.Constants"
                )
                results["constants"].append((
                    lib_dir,
                    class_name,
                    status,
                    "extends" if extends else "error",
                ))

        except Exception as e:
            results["constants"].append((
                lib_dir,
                "Constants",
                f"⚠️  ERROR: {str(e)[:50]}",
                "error",
            ))

        # Test Config
        try:
            if lib_dir == "flext-core":
                results["config"].append((
                    lib_dir,
                    "FlextCore.Config",
                    "✅ FOUNDATION",
                    "foundation",
                ))
            else:
                module_name = f"flext_{domain}.config"
                class_name = f"Flext{domain.title().replace('_', '')}Config"

                # Import module using __import__
                module = __import__(module_name, fromlist=[class_name])
                cfg_cls = getattr(module, class_name)

                extends = issubclass(cfg_cls, FlextCore.Config)
                status = (
                    "✅ EXTENDS FlextCore.Config"
                    if extends
                    else "❌ DOES NOT EXTEND FlextCore.Config"
                )
                results["config"].append((
                    lib_dir,
                    class_name,
                    status,
                    "extends" if extends else "error",
                ))

        except Exception as e:
            results["config"].append((
                lib_dir,
                "Config",
                f"⚠️  ERROR: {str(e)[:50]}",
                "error",
            ))

        # Test Models
        try:
            if lib_dir == "flext-core":
                results["models"].append((
                    lib_dir,
                    "FlextCore.Models",
                    "✅ FOUNDATION",
                    "foundation",
                ))
            else:
                module_name = f"flext_{domain}.models"
                class_name = f"Flext{domain.title().replace('_', '')}Models"

                # Import module using __import__
                module = __import__(module_name, fromlist=[class_name])
                mdl_cls = getattr(module, class_name)

                extends = issubclass(mdl_cls, FlextCore.Models)
                status = (
                    "✅ EXTENDS FlextCore.Models"
                    if extends
                    else "❌ DOES NOT EXTEND FlextCore.Models"
                )
                results["models"].append((
                    lib_dir,
                    class_name,
                    status,
                    "extends" if extends else "error",
                ))

        except Exception as e:
            results["models"].append((
                lib_dir,
                "Models",
                f"⚠️  ERROR: {str(e)[:50]}",
                "error",
            ))

    # Print results
    print("=" * 80)
    print("CONSTANTS INHERITANCE")
    print("=" * 80)
    for lib, cls, status, _ in results["constants"]:
        print(f"{lib:25} {cls:35} {status}")

    print("\n" + "=" * 80)
    print("CONFIG INHERITANCE")
    print("=" * 80)
    for lib, cls, status, _ in results["config"]:
        print(f"{lib:25} {cls:35} {status}")

    print("\n" + "=" * 80)
    print("MODELS INHERITANCE")
    print("=" * 80)
    for lib, cls, status, _ in results["models"]:
        print(f"{lib:25} {cls:35} {status}")

    # Calculate summary
    constants_ok = sum(
        1
        for _, _, _, result_type in results["constants"]
        if result_type in {"extends", "foundation"}
    )
    constants_total = len([r for r in results["constants"] if r[3] != "error"])

    config_ok = sum(
        1
        for _, _, _, result_type in results["config"]
        if result_type in {"extends", "foundation"}
    )
    config_total = len([r for r in results["config"] if r[3] != "error"])

    models_ok = sum(
        1
        for _, _, _, result_type in results["models"]
        if result_type in {"extends", "foundation"}
    )
    models_total = len([r for r in results["models"] if r[3] != "error"])

    total_ok = constants_ok + config_ok + models_ok
    total_checks = constants_total + config_total + models_total

    equilibrium = (total_ok / total_checks * 100) if total_checks > 0 else 0

    print("\n" + "=" * 80)
    print("EQUILIBRIUM SUMMARY")
    print("=" * 80)
    print(f"Constants: {constants_ok}/{constants_total} extend FlextCore.Constants")
    print(f"Config:    {config_ok}/{config_total} extend FlextCore.Config")
    print(f"Models:    {models_ok}/{models_total} extend FlextCore.Models")
    print(f"\nOVERALL:   {total_ok}/{total_checks} ({equilibrium:.1f}%) EQUILIBRIUM")

    if equilibrium == 100:
        print("\n✅ 100% EQUILIBRIUM ACHIEVED - ALL LIBRARIES FOLLOW PATTERN")
        return 0
    print(f"\n⚠️  {100 - equilibrium:.1f}% remaining for full equilibrium")
    return 1


if __name__ == "__main__":
    sys.exit(validate_equilibrium())
