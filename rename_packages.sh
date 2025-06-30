#!/bin/bash

# Script to rename all flx_* packages to flext_* for consistency
# This migrates from old FLX naming to new FLEXT naming

set -e

echo "🔄 Renaming flx_* packages to flext_* ..."

# Function to rename directories safely
rename_package() {
    local package_dir="$1"
    local src_dir="$package_dir/src"

    if [ -d "$src_dir" ]; then
        cd "$src_dir"
        for dir in flx_*; do
            if [ -d "$dir" ]; then
                new_name="${dir/flx_/flext_}"
                echo "  📦 $package_dir: $dir → $new_name"
                mv "$dir" "$new_name"
            fi
        done
        cd - >/dev/null
    fi
}

# Rename packages in packages directory
for package_dir in packages/flext-*; do
    if [ -d "$package_dir" ]; then
        rename_package "$package_dir"
    fi
done

echo "✅ Package renaming completed!"

# Now update import statements in Python files
echo "🔄 Updating import statements..."

# Update imports in main src/ directories
find . -name "*.py" -not -path "./legacy/*" -exec sed -i 's/from flx_/from flext_/g' {} \;
find . -name "*.py" -not -path "./legacy/*" -exec sed -i 's/import flx_/import flext_/g' {} \;

# Update imports for flx module references
find . -name "*.py" -not -path "./legacy/*" -exec sed -i 's/flx\./flext./g' {} \;

# Update pyproject.toml files to reflect new package names
find . -name "pyproject.toml" -not -path "./legacy/*" -exec sed -i 's/flx_/flext_/g' {} \;
find . -name "pyproject.toml" -not -path "./legacy/*" -exec sed -i 's/"flx-/"flext-/g' {} \;

echo "✅ Import statements updated!"

# Update package includes in pyproject.toml files
echo "🔄 Updating package includes..."
find . -name "pyproject.toml" -not -path "./legacy/*" -exec sed -i 's/include = "flx_/include = "flext_/g' {} \;

echo "✅ All renaming completed successfully!"
echo "📝 Summary:"
echo "   - Renamed all flx_* directories to flext_*"
echo "   - Updated all import statements from flx_ to flext_"
echo "   - Updated pyproject.toml configurations"
echo ""
echo "🎯 Next: Re-run installation with updated names"
