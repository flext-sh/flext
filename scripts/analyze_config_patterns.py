#!/usr/bin/env python3
"""Analyze configuration patterns that need FLEXT consolidation."""

import re
from pathlib import Path


def _find_config_files() -> list[Path]:
    """Find config.py files in the workspace."""
    workspace = Path()
    return [
        config_file
        for config_file in workspace.rglob("config.py")
        if "/src/" in str(config_file) and ".venv" not in str(config_file)
    ]


def _analyze_single_config(config_file: Path, patterns: dict[str, list[str]]) -> None:
    """Analyze a single config file for patterns."""
    try:
        with config_file.open(encoding="utf-8") as f:
            content = f.read()

        # Check for manual Pydantic patterns
        if "BaseSettings" in content or "Settings(" in content:
            patterns["manual_pydantic"].append(str(config_file))

        # Check for manual env vars
        if "os.getenv(" in content or "os.environ" in content:
            patterns["manual_env_vars"].append(str(config_file))

        # Check for manual validation
        if "if not" in content and ("config" in content or "settings" in content):
            patterns["manual_validation"].append(str(config_file))

        # Check for custom config classes
        class_matches = re.findall(
            r"class\s+([A-Z][a-zA-Z0-9_]*(?:Config|Settings))",
            content,
        )
        if class_matches:
            patterns["custom_classes"].extend(
                [f"{config_file}:{cls}" for cls in class_matches],
            )

    except (OSError, UnicodeDecodeError) as e:
        print(f"❌ Error analyzing {config_file}: {e}")


def analyze_config_files() -> None:
    """Analyze configuration patterns in FLEXT ecosystem."""
    print("🔍 Analyzing configuration patterns for FLEXT consolidation...")

    config_files = _find_config_files()
    print(f"📄 Found {len(config_files)} config.py files")

    # Analyze each config file
    manual_patterns: dict[str, list[str]] = {
        "manual_pydantic": [],
        "manual_env_vars": [],
        "manual_validation": [],
        "custom_classes": [],
    }

    for config_file in config_files:
        _analyze_single_config(config_file, manual_patterns)

    # Report findings
    print("\n📊 Configuration Analysis Results:")
    print(f"  Manual Pydantic usage: {len(manual_patterns['manual_pydantic'])} files")
    print(f"  Manual env var access: {len(manual_patterns['manual_env_vars'])} files")
    print(f"  Manual validation: {len(manual_patterns['manual_validation'])} files")
    print(f"  Custom config classes: {len(manual_patterns['custom_classes'])} classes")

    _report_detailed_analysis(manual_patterns)


def _report_detailed_analysis(manual_patterns: dict[str, list[str]]) -> None:
    """Report detailed analysis of priority files."""
    # Show priority files
    print("\n🎯 Priority Files for Consolidation:")

    priority_files = set()
    for file_list in manual_patterns.values():
        if file_list and isinstance(file_list[0], str) and ":" not in file_list[0]:
            priority_files.update(file_list)
        elif file_list:
            priority_files.update([f.split(":")[0] for f in file_list])

    max_display = 10
    for i, file_path in enumerate(sorted(priority_files)[:max_display], 1):
        print(f"  {i}. {file_path}")

    # Analyze specific patterns in priority files
    print("\n🔍 Detailed Analysis of Top Priority Files:")

    max_analysis = 5
    for file_path in sorted(priority_files)[:max_analysis]:
        _analyze_priority_file(file_path)


def _analyze_priority_file(file_path: str) -> None:
    """Analyze a single priority file for detailed patterns."""
    print(f"\n📁 {file_path}:")
    try:
        with Path(file_path).open(encoding="utf-8") as f:
            content = f.read()

        # Count env var usages
        env_vars = re.findall(r'os\.getenv\(["\']([^"\']+)["\']', content)
        if env_vars:
            preview_limit = 3
            preview = ", ".join(env_vars[:preview_limit])
            suffix = "..." if len(env_vars) > preview_limit else ""
            print(f"   🌍 Environment variables: {len(env_vars)} ({preview}{suffix})")

        # Count config classes
        pattern = r"class\s+([A-Z][a-zA-Z0-9_]*(?:Config|Settings))"
        classes = re.findall(pattern, content)
        if classes:
            print(f"   📝 Config classes: {len(classes)} ({', '.join(classes)})")

        # Count BaseSettings usage
        if "BaseSettings" in content:
            print("   ⚙️ Uses Pydantic BaseSettings: Yes")

        # Check for FLEXT imports
        if "flext_core" in content:
            print("   ✅ Already uses flext-core: Yes")
        else:
            print("   ❌ Needs flext-core integration: Yes")

    except (OSError, UnicodeDecodeError) as e:
        print(f"   ❌ Analysis error: {e}")


def main() -> None:
    """Analyze configuration files and provide recommendations."""
    analyze_config_files()

    print("\n📋 Recommended Actions:")
    print("1. Create standardized FLEXT config base classes")
    print("2. Migrate manual os.getenv() to Pydantic Fields")
    print("3. Replace custom validation with Pydantic validators")
    print("4. Consolidate config classes using flext-core patterns")
    print("5. Update imports to use centralized configuration")


if __name__ == "__main__":
    main()
