#!/usr/bin/env python3
import os
import re


def remove_version_limits(content):
    """Remove upper version limits but keep lower limits."""
    patterns = [
        # Remove ,<version from >=version,<version
        (r"(\w+>=[\d\.]+),<[\d\.<]+", r"\1"),
        # Change ^version to >=version
        (r"(\w+)\^([\d\.]+)", r"\1>=\2"),
        # Remove standalone <version constraints
        (r",\s*<[\d\.<]+", ""),
    ]

    result = content
    for pattern, replacement in patterns:
        result = re.sub(pattern, replacement, result)
    return result


def process_pyproject_toml(filepath) -> bool | None:
    """Process a single pyproject.toml file."""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        new_content = remove_version_limits(content)

        if new_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Updated: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False


def main() -> None:
    # Process main pyproject.toml
    main_file = "./pyproject.toml"
    if os.path.exists(main_file):
        process_pyproject_toml(main_file)
        print("Main pyproject.toml updated")

    # Process submodule pyproject.toml files
    submodules = [
        "flext-api",
        "flext-auth",
        "flext-cli",
        "flext-core",
        "flext-db-oracle",
        "flext-dbt-ldap",
        "flext-grpc",
        "flext-ldap",
        "flext-meltano",
        "flext-observability",
        "flext-oracle-oic-ext",
        "flext-plugin",
        "flext-quality",
        "flext-tap-ldap",
        "flext-tap-oracle-oic",
        "flext-tap-oracle-wms",
        "flext-target-ldap",
        "flext-target-oracle",
        "flext-target-oracle-oic",
        "flext-web",
        "flext-meltano-bridge",
        "algar-oud-mig",
        "gruponos-poc-oic-wms",
        "gruponos-meltano-native",
    ]

    updated_count = 0
    for submodule in submodules:
        pyproject_path = f"{submodule}/pyproject.toml"
        if os.path.exists(pyproject_path):
            if process_pyproject_toml(pyproject_path):
                updated_count += 1

    print(f"Updated {updated_count} submodule pyproject.toml files")


if __name__ == "__main__":
    main()
