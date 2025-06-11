#!/bin/bash
# Simple script to run the WMS CLI example

set -e

echo "Running WMS CLI Example"
echo "----------------------"

# Ensure Python environment is activated
if [ -d ".venv" ]; then
  echo "Activating Python virtual environment"
  source .venv/bin/activate
fi

# Run the example script
python wms_cli_example.py

echo "----------------------"
echo "WMS CLI Example completed" 
