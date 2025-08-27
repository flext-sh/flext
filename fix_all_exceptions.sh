#!/bin/bash
# Fix all exception usage patterns across all FLEXT projects

# Function to fix a single file
fix_file() {
    local file="$1"
    echo "Fixing: $file"
    
    # Fix incorrect imports like "from flext_core import FlextExceptions.ValidationError"
    sed -i 's/from flext_core import FlextExceptions\.\([A-Za-z]*\)/from flext_core import FlextExceptions/g' "$file"
    
    # Fix double FlextExceptions references
    sed -i 's/FlextExceptions\.FlextExceptions\./FlextExceptions\./g' "$file"
    
    # Update all FlextExceptions.FlextXxx to FlextExceptions.Xxx
    sed -i 's/FlextExceptions\.FlextValidationError/FlextExceptions.ValidationError/g' "$file"
    sed -i 's/FlextExceptions\.FlextConfigurationError/FlextExceptions.ConfigurationError/g' "$file"
    sed -i 's/FlextExceptions\.FlextTimeoutError/FlextExceptions.TimeoutError/g' "$file"
    sed -i 's/FlextExceptions\.FlextConnectionError/FlextExceptions.ConnectionError/g' "$file"
    sed -i 's/FlextExceptions\.FlextOperationError/FlextExceptions.OperationError/g' "$file"
    sed -i 's/FlextExceptions\.FlextProcessingError/FlextExceptions.ProcessingError/g' "$file"
    sed -i 's/FlextExceptions\.FlextPermissionError/FlextExceptions.PermissionError/g' "$file"
    sed -i 's/FlextExceptions\.FlextAuthenticationError/FlextExceptions.AuthenticationError/g' "$file"
    sed -i 's/FlextExceptions\.FlextTypeError/FlextExceptions.TypeError/g' "$file"
    sed -i 's/FlextExceptions\.FlextAttributeError/FlextExceptions.AttributeError/g' "$file"
    sed -i 's/FlextExceptions\.FlextNotFoundError/FlextExceptions.NotFoundError/g' "$file"
    sed -i 's/FlextExceptions\.FlextAlreadyExistsError/FlextExceptions.AlreadyExistsError/g' "$file"
    sed -i 's/FlextExceptions\.FlextCriticalError/FlextExceptions.CriticalError/g' "$file"
    sed -i 's/FlextExceptions\.FlextUserError/FlextExceptions.UserError/g' "$file"
    sed -i 's/FlextExceptions\.FlextError/FlextExceptions.Error/g' "$file"
    
    # Fix imports that directly import legacy exception classes from root
    sed -i 's/from flext_core import FlextValidationError/from flext_core import FlextExceptions/g' "$file"
    sed -i 's/from flext_core import FlextConfigurationError/from flext_core import FlextExceptions/g' "$file"
    sed -i 's/from flext_core import FlextTimeoutError/from flext_core import FlextExceptions/g' "$file"
    sed -i 's/from flext_core import FlextConnectionError/from flext_core import FlextExceptions/g' "$file"
    sed -i 's/from flext_core import FlextOperationError/from flext_core import FlextExceptions/g' "$file"
    sed -i 's/from flext_core import FlextProcessingError/from flext_core import FlextExceptions/g' "$file"
    sed -i 's/from flext_core import FlextPermissionError/from flext_core import FlextExceptions/g' "$file"
    sed -i 's/from flext_core import FlextAuthenticationError/from flext_core import FlextExceptions/g' "$file"
    sed -i 's/from flext_core import FlextTypeError/from flext_core import FlextExceptions/g' "$file"
    sed -i 's/from flext_core import FlextAttributeError/from flext_core import FlextExceptions/g' "$file"
    sed -i 's/from flext_core import FlextNotFoundError/from flext_core import FlextExceptions/g' "$file"
    sed -i 's/from flext_core import FlextAlreadyExistsError/from flext_core import FlextExceptions/g' "$file"
    sed -i 's/from flext_core import FlextCriticalError/from flext_core import FlextExceptions/g' "$file"
    sed -i 's/from flext_core import FlextUserError/from flext_core import FlextExceptions/g' "$file"
    sed -i 's/from flext_core import FlextError/from flext_core import FlextExceptions/g' "$file"
}

# Process all Python files in all FLEXT projects
for project_dir in /home/marlonsc/flext/flext-*/; do
    echo "=== Processing $(basename $project_dir) ==="
    find "$project_dir" -name "*.py" -type f | while read -r file; do
        # Check if file contains any legacy patterns
        if grep -q "FlextExceptions\.Flext\|from flext_core import.*Flext.*Error\|FlextExceptions\.Error\|FlextExceptions\.ValidationError" "$file" 2>/dev/null; then
            fix_file "$file"
        fi
    done
done

echo "All files updated!"