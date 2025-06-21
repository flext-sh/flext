#!/usr/bin/env python
"""Fix duplicate TOML configurations in all projects."""

from pathlib import Path

import toml


def fix_pyproject_toml(project_path: Path) -> None:
    """Fix duplicate sections in pyproject.toml."""
    pyproject_path = project_path / "pyproject.toml"

    if not pyproject_path.exists():
        return

    try:
        # Read content
        content = pyproject_path.read_text()

        # Parse TOML safely
        try:
            toml.loads(content)
        except toml.TomlDecodeError:
            # Manual fix for duplicates
            lines = content.split('\n')
            seen_sections: set = set()
            new_lines: list = []
            skip_until_next_section = False

            for line in lines:
                if line.strip().startswith('['):
                    section = line.strip()
                    if section in seen_sections:
                        skip_until_next_section = True
                        continue
                    seen_sections.add(section)
                    skip_until_next_section = False

                if not skip_until_next_section:
                    new_lines.append(line)

            # Write back
            pyproject_path.write_text('\n'.join(new_lines))
    except Exception:
        pass


# Fix all projects
workspace = Path("/home/marlonsc/pyauto")
submodules = [
    "algar-oud-mig", "dbt-ldap", "dc-code-analyzer", "flx",
    "flx-adapter-example", "flx-database-oracle", "flx-http-oracle-oic",
    "flx-http-oracle-wms", "flx-ldap", "flx-meltano-enterprise",
    "flx-oracle-oic", "flx-oracle-wms", "gruponos-poc-oic-wms",
    "ldap-core-shared", "oracle-oic-ext", "tap-ldap", "tap-oracle-oic",
    "tap-oracle-wms", "target-ldap", "target-oracle-oic", "target-oracle-wms"
]

for submodule in submodules:
    project_path = workspace / submodule
    if project_path.exists():
        fix_pyproject_toml(project_path)
