#!/usr/bin/env python3
"""Fix jsonschema compatibility for singer-sdk."""

# Monkey patch jsonschema to provide Draft7Validator
import jsonschema

# Use Draft4Validator as a fallback for Draft7Validator
if not hasattr(jsonschema, "Draft7Validator"):
    jsonschema.Draft7Validator = jsonschema.Draft4Validator
else:
    pass
