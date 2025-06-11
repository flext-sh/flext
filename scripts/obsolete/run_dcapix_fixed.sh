#!/bin/bash

# Run the fix script on the dc-api-x flx_project
python fix_dcapix.py dc-api-x

echo "Fix script completed. You can verify the changes by running mypy on the dc-api-x flx_project."
