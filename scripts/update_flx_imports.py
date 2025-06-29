#!/usr/bin/env python3
"""Update import paths in extracted FLX modules.

This script updates all imports from the monolithic flx_core structure
to the new modular structure based on the extracted modules.
"""

import re
from pathlib import Path

# Import mapping from old to new structure
IMPORT_MAPPINGS = {
    # Core remains as flx_core
    "from flx_core.domain": "from flx_core.domain",
    "from flx_core.application": "from flx_core.application",
    "from flx_core.infrastructure": "from flx_core.infrastructure",
    "from flx_core.config": "from flx_core.config",
    "from flx_core.events": "from flx_core.events",
    "from flx_core.plugins": "from flx_core.plugins",

    # Auth module (special case - auth is extracted to flx-auth)
    "from flx_core.auth.interfaces": "from flx_auth.interfaces",
    "from flx_core.auth.models": "from flx_auth.models",
    "from flx_core.auth.user_service": "from flx_auth.user_service",
    "from flx_core.auth.jwt_service": "from flx_auth.jwt_service",
    "from flx_core.auth.tokens": "from flx_auth.tokens",
    "from flx_core.auth.types": "from flx_auth.types",
    "from flx_core.auth.security": "from flx_auth.security",
    "from flx_core.auth.repositories": "from flx_auth.repositories",
    "from flx_core.auth.authorization_service": "from flx_auth.authorization_service",
    "from flx_core.auth.authentication_implementation": "from flx_auth.authentication_implementation",
    "from flx_core.auth": "from flx_auth",

    # gRPC module
    "from flx_core.grpc.converters": "from flx_grpc.converters",
    "from flx_core.grpc.interceptors": "from flx_grpc.interceptors",
    "from flx_core.grpc.server": "from flx_grpc.server",
    "from flx_core.grpc.server_implementation": "from flx_grpc.server_implementation",
    "from flx_core.grpc.client": "from flx_grpc.client",
    "from flx_core.grpc.proto": "from flx_grpc.proto",
    "from flx_core.grpc": "from flx_grpc",

    # Meltano module
    "from flx_core.meltano.runner": "from flx_meltano.runner",
    "from flx_core.meltano.meltano_orchestrator": "from flx_meltano.meltano_orchestrator",
    "from flx_core.meltano.state_manager": "from flx_meltano.state_manager",
    "from flx_core.meltano.adapters": "from flx_meltano.adapters",
    "from flx_core.meltano.config": "from flx_meltano.config",
    "from flx_core.meltano.models": "from flx_meltano.models",
    "from flx_core.meltano": "from flx_meltano",

    # Observability module
    "from flx_core.observability.structured_logging": "from flx_observability.structured_logging",
    "from flx_core.observability.metrics_collector": "from flx_observability.metrics_collector",
    "from flx_core.observability.tracing": "from flx_observability.tracing",
    "from flx_core.observability": "from flx_observability",
    "from flx_core.monitoring.health": "from flx_observability.health",
    "from flx_core.monitoring.metrics": "from flx_observability.metrics",
    "from flx_core.monitoring.tracing": "from flx_observability.tracing",
    "from flx_core.monitoring": "from flx_observability.monitoring",

    # API module (imports FROM core, doesn't export TO other modules)
    # Web module (imports FROM core, doesn't export TO other modules)
}

# Cross-module dependencies (module -> module)
CROSS_MODULE_DEPS = {
    "flx_api": ["flx_core", "flx_auth"],
    "flx_web": ["flx_core", "flx_auth", "flx_grpc"],
    "flx_grpc": ["flx_core"],
    "flx_meltano": ["flx_core"],
    "flx_observability": ["flx_core"],
    "flx_auth": ["flx_core"],  # Auth depends on core for domain models
}


def update_imports_in_file(file_path: Path) -> tuple[int, list[str]]:
    """Update imports in a single Python file.

    Returns:
        Tuple of (number of changes, list of changes made)
    """
    try:
        content = file_path.read_text()
        original_content = content
        changes = []

        # Apply each import mapping
        for old_import, new_import in IMPORT_MAPPINGS.items():
            if old_import in content:
                # Count occurrences before replacement
                count = content.count(old_import)
                content = content.replace(old_import, new_import)
                if count > 0:
                    changes.append(f"{old_import} -> {new_import} ({count} occurrences)")

        # Handle relative imports within modules
        module_name = get_module_name(file_path)
        if module_name:
            # Update relative imports to use the module name
            content = update_relative_imports(content, module_name)

        # Write back if changed
        if content != original_content:
            file_path.write_text(content)
            return len(changes), changes

        return 0, []

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0, []


def update_relative_imports(content: str, module_name: str) -> str:
    """Update relative imports within a module to use absolute imports."""
    # This is a simplified version - in practice you'd want more sophisticated parsing
    lines = content.split('\n')
    updated_lines = []

    for line in lines:
        # Handle "from . import X" -> "from module_name import X"
        if line.strip().startswith("from . import"):
            updated_line = line.replace("from . import", f"from {module_name} import")
            updated_lines.append(updated_line)
        # Handle "from .submodule import X" -> "from module_name.submodule import X"
        elif line.strip().startswith("from ."):
            updated_line = re.sub(r"from \.([\w.]+) import", f"from {module_name}.\\1 import", line)
            updated_lines.append(updated_line)
        else:
            updated_lines.append(line)

    return '\n'.join(updated_lines)


def get_module_name(file_path: Path) -> str:
    """Get the module name from the file path."""
    # Extract module name from path structure
    parts = file_path.parts
    if "flx-" in str(file_path):
        for i, part in enumerate(parts):
            if part.startswith("flx-") and i + 2 < len(parts) and parts[i + 1] == "src":
                return parts[i + 2].replace("-", "_")
    return ""


def update_module(module_path: Path) -> dict[str, any]:
    """Update all Python files in a module."""
    print(f"\nProcessing module: {module_path}")

    total_files = 0
    total_changes = 0
    all_changes = []

    # Find all Python files
    src_path = module_path / "src"
    if not src_path.exists():
        print("  No src directory found")
        return {"files": 0, "changes": 0}

    python_files = list(src_path.rglob("*.py"))

    for py_file in python_files:
        changes_count, changes = update_imports_in_file(py_file)
        if changes_count > 0:
            total_files += 1
            total_changes += changes_count
            all_changes.extend(changes)
            print(f"  Updated {py_file.relative_to(module_path)}: {changes_count} changes")
            for change in changes:
                print(f"    - {change}")

    return {
        "files": total_files,
        "changes": total_changes,
        "details": all_changes
    }


def main():
    """Main entry point."""
    print("FLX Import Path Updater")
    print("=" * 50)

    # Base directory
    base_dir = Path("/home/marlonsc/pyauto")

    # Modules to update
    modules = [
        "flx-core",
        "flx-auth",
        "flx-api",
        "flx-web",
        "flx-grpc",
        "flx-meltano",
        "flx-observability"
    ]

    results = {}

    for module in modules:
        module_path = base_dir / module
        if module_path.exists():
            results[module] = update_module(module_path)
        else:
            print(f"\nModule {module} not found at {module_path}")
            results[module] = {"files": 0, "changes": 0, "error": "Module not found"}

    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)

    total_files = sum(r.get("files", 0) for r in results.values())
    total_changes = sum(r.get("changes", 0) for r in results.values())

    for module, result in results.items():
        if "error" in result:
            print(f"{module}: {result['error']}")
        else:
            print(f"{module}: {result['files']} files updated, {result['changes']} import changes")

    print(f"\nTotal: {total_files} files updated, {total_changes} import changes")

    # Write detailed report
    report_path = base_dir / "FLX_IMPORT_UPDATE_REPORT.md"
    with open(report_path, "w") as f:
        f.write("# FLX Import Update Report\n\n")
        f.write(f"**Date**: {Path(__file__).stat().st_mtime}\n")
        f.write(f"**Total Files Updated**: {total_files}\n")
        f.write(f"**Total Import Changes**: {total_changes}\n\n")

        for module, result in results.items():
            f.write(f"## {module}\n\n")
            if "error" in result:
                f.write(f"Error: {result['error']}\n\n")
            else:
                f.write(f"- Files updated: {result['files']}\n")
                f.write(f"- Import changes: {result['changes']}\n\n")

                if result.get("details"):
                    f.write("### Changes:\n\n")
                    for change in result["details"]:
                        f.write(f"- {change}\n")
                    f.write("\n")

    print(f"\nDetailed report written to: {report_path}")


if __name__ == "__main__":
    main()
