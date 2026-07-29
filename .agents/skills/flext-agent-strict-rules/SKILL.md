---
name: flext-agent-strict-rules
description: 'Use when writing or reviewing FLEXT Python code that touches facade aliases, runtime narrowing, dynamic input, or public typed contracts.'
license: MIT
metadata:
  version: 1.0.0
---
# Flext Agent Strict Rules

## Workflow

1. Identify the canonical facade, model, protocol, or type owner for the change.
2. Apply the narrowest typed pattern without adding a second access route.
3. Use structural search to update every affected caller, export, test, and example.
4. Run the Python gates listed in `AGENTS.md` for the touched project.

## Contracts

- Use project facade aliases instead of direct implementation imports.
- Narrow runtime unions with `isinstance` or `TypeGuard`; do not branch on `type(...)`.
- Validate dynamic mappings once with a Pydantic v2 model, then pass typed values.
- Update every caller when a public contract changes; do not add compatibility routes.
