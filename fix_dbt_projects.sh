#!/bin/bash
# Systematic DBT project fix script based on discovered patterns
# Fixes: flext-dbt-oracle, flext-dbt-oracle-wms

set -e

echo "=== SYSTEMATIC DBT PROJECT FIXES ==="
echo "Patterns discovered:"
echo "1. SettingsConfigDict must come from pydantic_settings"
echo "2. Core.Headers → Core.Dict"
echo "3. Core.StringList → Core.List"
echo "4. version.py needs simplified implementation"
echo ""

# Function to fix a single DBT project
fix_dbt_project() {
    local project_name=$1
    local project_dir="/home/marlonsc/flext/$project_name"

    if [ ! -d "$project_dir" ]; then
        echo "❌ $project_name: Directory not found"
        return 1
    fi

    cd "$project_dir"
    echo "📁 Processing $project_name..."

    # Fix 1: SettingsConfigDict import
    if [ -f "src/${project_name//-/_}/config.py" ]; then
        echo "  🔧 Fixing SettingsConfigDict import..."
        sed -i 's/from pydantic import \(.*\)SettingsConfigDict/from pydantic import \1\nfrom pydantic_settings import SettingsConfigDict/' "src/${project_name//-/_}/config.py" 2>/dev/null || true
        sed -i 's/^from pydantic import Field, SettingsConfigDict/from pydantic import Field\nfrom pydantic_settings import SettingsConfigDict/' "src/${project_name//-/_}/config.py" 2>/dev/null || true
    fi

    # Fix 2 & 3: Type annotations
    if [ -f "src/${project_name//-/_}/config.py" ]; then
        echo "  🔧 Fixing type annotations..."
        sed -i 's/\.Core\.Headers/.Core.Dict/g' "src/${project_name//-/_}/config.py"
        sed -i 's/\.Core\.StringList/.Core.List/g' "src/${project_name//-/_}/config.py"
    fi

    # Fix 4: version.py
    if [ -f "src/${project_name//-/_}/version.py" ]; then
        echo "  🔧 Fixing version.py..."
        version_class="${project_name//-/}"
        version_class="${version_class//dbt/Dbt}"
        version_class="Flext${version_class^}Version"

        cat > "src/${project_name//-/_}/version.py" <<EOF
"""Version information for $project_name."""

from __future__ import annotations

from typing import Final

# Version components
MAJOR: Final[int] = 0
MINOR: Final[int] = 9
PATCH: Final[int] = 0

# Version string
__version__: Final[str] = f"{MAJOR}.{MINOR}.{PATCH}"
__version_info__: Final[tuple[int, int, int]] = (MAJOR, MINOR, PATCH)


class $version_class:
    """Version information container for $project_name."""

    def __init__(self) -> None:
        self.major = MAJOR
        self.minor = MINOR
        self.patch = PATCH
        self.version = __version__
        self.version_info = __version_info__

    @classmethod
    def current(cls) -> $version_class:
        """Return current version information."""
        return cls()


VERSION: Final[$version_class] = $version_class.current()

__all__ = ["VERSION", "$version_class", "__version__", "__version_info__"]
EOF
    fi

    # Test import
    echo "  🧪 Testing import..."
    if python3 -c "import sys; sys.path.insert(0, 'src'); import ${project_name//-/_}" 2>/dev/null; then
        echo "  ✅ $project_name: Import successful"
        return 0
    else
        echo "  ❌ $project_name: Import failed - manual intervention needed"
        python3 -c "import sys; sys.path.insert(0, 'src'); import ${project_name//-/_}" 2>&1 | tail -10
        return 1
    fi
}

# Fix each remaining DBT project
echo ""
echo "=== FIXING REMAINING DBT PROJECTS ==="
echo ""

fix_dbt_project "flext-dbt-oracle"
echo ""

fix_dbt_project "flext-dbt-oracle-wms"
echo ""

echo "=== DBT PROJECT FIXES COMPLETE ==="
echo "Status:"
echo "✅ flext-dbt-ldap (manually fixed)"
echo "✅ flext-dbt-ldif (manually fixed)"
cd /home/marlonsc/flext
python3 -c "import sys; sys.path.insert(0, 'flext-dbt-oracle/src'); import flext_dbt_oracle" 2>/dev/null && echo "✅ flext-dbt-oracle" || echo "❌ flext-dbt-oracle"
python3 -c "import sys; sys.path.insert(0, 'flext-dbt-oracle-wms/src'); import flext_dbt_oracle_wms" 2>/dev/null && echo "✅ flext-dbt-oracle-wms" || echo "❌ flext-dbt-oracle-wms"
