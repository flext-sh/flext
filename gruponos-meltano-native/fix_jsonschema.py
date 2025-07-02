#!/usr/bin/env python3
"""Fix jsonschema compatibility for singer-sdk."""

import sys

# Monkey patch jsonschema to provide Draft7Validator
import jsonschema

# Use Draft4Validator as a fallback for Draft7Validator
if not hasattr(jsonschema, 'Draft7Validator'):
    jsonschema.Draft7Validator = jsonschema.Draft4Validator
    print("✅ jsonschema compatibility patch applied (using Draft4Validator as Draft7Validator)")
else:
    print("✅ Draft7Validator already available")