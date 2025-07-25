#!/usr/bin/env python3
"""Analyze configuration patterns that need FLEXT consolidation."""

import os
import re


def analyze_config_files() -> None:
    """Analyze configuration patterns in FLEXT ecosystem."""
    print("🔍 Analyzing configuration patterns for FLEXT consolidation...")

    # Find actual config.py files
    config_files: list[str] = []
    for root, dirs, files in os.walk("."):
        # Skip .venv directories
        dirs[:] = [d for d in dirs if not d.startswith(".venv")]

        config_files.extend(os.path.join(root, file) for file in files if file == "config.py" and "/src/" in root)

    print(f"📄 Found {len(config_files)} config.py files")

    # Analyze each config file
    manual_patterns: dict[str, list[str]] = {
        "manual_pydantic": [],
        "manual_env_vars": [],
        "manual_validation": [],
        "custom_classes": [],
    }

    for config_file in config_files:
        try:
            with open(config_file, encoding="utf-8") as f:
                content = f.read()

            # Check for manual Pydantic patterns
            if "BaseSettings" in content or "Settings(" in content:
                manual_patterns["manual_pydantic"].append(config_file)

            # Check for manual env vars
            if "os.getenv(" in content or "os.environ" in content:
                manual_patterns["manual_env_vars"].append(config_file)

            # Check for manual validation
            if "if not" in content and ("config" in content or "settings" in content):
                manual_patterns["manual_validation"].append(config_file)

            # Check for custom config classes
            class_matches = re.findall(r"class\s+([A-Z][a-zA-Z0-9_]*(?:Config|Settings))", content)
            if class_matches:
                manual_patterns["custom_classes"].extend([f"{config_file}:{cls}" for cls in class_matches])

        except Exception as e:
            print(f"❌ Error analyzing {config_file}: {e}")

    # Report findings
    print("\n📊 Configuration Analysis Results:")
    print(f"  Manual Pydantic usage: {len(manual_patterns['manual_pydantic'])} files")
    print(f"  Manual env var access: {len(manual_patterns['manual_env_vars'])} files")
    print(f"  Manual validation: {len(manual_patterns['manual_validation'])} files")
    print(f"  Custom config classes: {len(manual_patterns['custom_classes'])} classes")

    # Show priority files
    print("\n🎯 Priority Files for Consolidation:")

    priority_files = set()
    for file_list in manual_patterns.values():
        if isinstance(file_list[0], str) and ":" not in file_list[0]:
            priority_files.update(file_list)
        else:
            priority_files.update([f.split(":")[0] for f in file_list])

    for i, file_path in enumerate(sorted(priority_files)[:10], 1):
        print(f"  {i}. {file_path}")

    # Analyze specific patterns in priority files
    print("\n🔍 Detailed Analysis of Top Priority Files:")

    for file_path in sorted(priority_files)[:5]:
        print(f"\n📁 {file_path}:")
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Count env var usages
            env_vars = re.findall(r'os\.getenv\(["\']([^"\']+)["\']', content)
            if env_vars:
                print(f"   🌍 Environment variables: {len(env_vars)} ({', '.join(env_vars[:3])}{'...' if len(env_vars) > 3 else ''})")

            # Count config classes
            classes = re.findall(r"class\s+([A-Z][a-zA-Z0-9_]*(?:Config|Settings))", content)
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

        except Exception as e:
            print(f"   ❌ Analysis error: {e}")


def main() -> None:
    """Main analysis function."""
    analyze_config_files()

    print("\n📋 Recommended Actions:")
    print("1. Create standardized FLEXT config base classes")
    print("2. Migrate manual os.getenv() to Pydantic Fields")
    print("3. Replace custom validation with Pydantic validators")
    print("4. Consolidate config classes using flext-core patterns")
    print("5. Update imports to use centralized configuration")


if __name__ == "__main__":
    main()
