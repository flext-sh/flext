#!/usr/bin/env python3
import os
import re


def fix_python_313_only(content):
    """Fix Python version to be exactly 3.13"""
    # Fix requires-python
    content = re.sub(
        r'requires-python = ">=3\.13,<4\.0"',
        r'requires-python = ">=3.13,<3.14"',
        content,
    )
    content = re.sub(
        r'requires-python = ">=3\.13"', r'requires-python = ">=3.13,<3.14"', content
    )
    # Fix poetry python constraint
    content = re.sub(r'python = ">=3\.13,<4\.0"', r'python = ">=3.13,<3.14"', content)
    return re.sub(r'python = ">=3\.13"', r'python = ">=3.13,<3.14"', content)


def fix_pyproject_toml(filepath) -> bool | None:
    """Fix a single pyproject.toml file"""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        new_content = fix_python_313_only(content)

        if new_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Fixed: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False


def main() -> None:
    # Fix main pyproject.toml
    main_file = "./pyproject.toml"
    if os.path.exists(main_file):
        fix_pyproject_toml(main_file)
        print("Fixed main pyproject.toml")

    # Fix all submodule pyproject.toml files
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

    fixed_count = 0
    for submodule in submodules:
        pyproject_path = f"{submodule}/pyproject.toml"
        if os.path.exists(pyproject_path):
            if fix_pyproject_toml(pyproject_path):
                fixed_count += 1

    print(f"Fixed Python version to >=3.13,<3.14 in {fixed_count} files")


if __name__ == "__main__":
    main()
