---
name: flext-cli-ssot-enforcement
description: 'Mandatory guidance for when working in any flext workspace project to ensure flext-cli SSOT for CLI domain (typer/click/rich/tabulate/process-exec/json/yaml/csv/toml/prompts/output) is not violated. Auto-fail violations.'
license: MIT
metadata:
  version: 1.0.0
---
# flext-cli SSOT enforcement

## Workflow

1. Classify the CLI concern: routing, rendering, prompting, serialization, or process execution.
2. Locate the corresponding public `flext-cli` model, protocol, or service.
3. Keep the consumer command declarative and move reusable behavior to the owner.
4. Exercise the command through the canonical CLI runner and verify help, output, and exit status.

## Contracts

- Route Typer/Click, Rich, prompts, process execution, and structured output through `flext-cli`.
- Keep package CLIs as thin model-driven routers; business behavior belongs in services.
- Test public commands through the canonical CLI runner and real exit codes.
