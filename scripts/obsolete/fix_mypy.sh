#!/bin/bash
# Script to run the mypy error fixers

set -e # Exit on any error

# Check if directory was provided
if [ "$#" -ne 1 ]; then
	echo "Usage: $0 <directory>"
	echo "Example: $0 ./dc-api-x"
	exit 1
fi

DIRECTORY="$1"

# Make sure the directory exists
if [ -z "$(test -d "$DIRECTORY" && echo exists)" ]; then
	echo "Error: Directory '$DIRECTORY' does not exist."
	exit 1
fi

# Check if mypy is installed
if [ -z "$(command -v mypy)" ]; then
	echo "Error: mypy is not installed or not in PATH."
	echo "Please install mypy first: pip install mypy"
	exit 1
fi

# Check if all the necessary Python scripts exist
SCRIPTS=("fix_test_return_types.py" "fix_mypy_errors.py" "fix_generic_type_params.py" "fix_advanced_mypy_errors.py" "fix_all_mypy_errors.py" "fix_deprecated_typing.py")
MISSING_SCRIPTS=()

for SCRIPT in "${SCRIPTS[@]}"; do
	if [ -z "$(test -f "$SCRIPT" && echo exists)" ]; then
		MISSING_SCRIPTS+=("$SCRIPT")
	fi
done

if [ ${#MISSING_SCRIPTS[@]} -gt 0 ]; then
	echo "Error: The following required scripts are missing:"
	for SCRIPT in "${MISSING_SCRIPTS[@]}"; do
		echo "  - $SCRIPT"
	done
	echo "Please make sure all the fixer scripts are in the current directory."
	exit 1
fi

# Make scripts executable
chmod +x fix_*.py

# First, fix deprecated typing imports
echo "Step 0: Fixing deprecated typing imports (List, Dict, etc.)..."
python fix_deprecated_typing.py "$DIRECTORY"
echo

# Run the main fixer script
echo "Starting mypy error fixing process for $DIRECTORY..."
echo "This may take a while depending on the size of the codebase."
echo

python fix_all_mypy_errors.py "$DIRECTORY"

echo
echo "Process completed."
echo "You can run 'mypy $DIRECTORY' to check the remaining errors."
echo "For any remaining errors, you may need to fix them manually following the guidance provided."
