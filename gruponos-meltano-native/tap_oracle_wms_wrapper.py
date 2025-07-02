#!/usr/bin/env python3
"""Wrapper for tap-oracle-wms that applies jsonschema compatibility patch."""

# Apply the patch first
import sys
import os

# Suppress the patch output when in discovery mode
if "--discover" in sys.argv:
    sys.stdout = open(os.devnull, 'w')
    import fix_jsonschema
    sys.stdout = sys.__stdout__
else:
    import fix_jsonschema

# Now import and run the tap
sys.path.insert(0, '/home/marlonsc/flext/flext-tap-oracle-wms/src')

from tap_oracle_wms.tap import TapOracleWMS

if __name__ == "__main__":
    TapOracleWMS.cli()