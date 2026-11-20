# AI Hub MCP Wrapper Script

## Overview

The AI Hub MCP wrapper script (`scripts/ai-hub-mcp/ai-hub-mcp-wrapper.sh`)
ensures that the AI Hub MCP client runs with the correct project environment
context. This is critical for validation and command execution to work correctly.

## Problem Solved

Previously, the AI Hub MCP client would run without the correct project
environment, causing:

- Validation failures due to incorrect working directory
- Missing environment variables (PATH, VENV_DIR, etc.)
- Commands not finding the correct Python environment
- direnv not being activated

## Solution

The wrapper script:

1. Changes to the project root directory (derived from script location)
2. Sources direnv to load the project environment
3. Finds and executes ai-hub with the activated environment

## Configuration

The kilo configuration (`~/.config/kilo/kilo.json` and
`~/.config/kilo/kilo.jsonc`) uses the wrapper script instead of calling
ai-hub directly.

## Usage

The wrapper script is automatically invoked by the kilo MCP configuration.
No manual intervention is needed.

## Environment Variables

The wrapper script relies on direnv to set up:

- `PROJECT_ROOT`: Project root directory
- `RUNTIME_ROOT`: Runtime root (may differ in workspaces)
- `VENV_DIR`: Virtual environment directory
- `PATH`: Includes the virtual environment bin directory
- `PYTHONPATH`: Python module search path
- Other project-specific variables

## Future Considerations

- The wrapper script should be portable across different user accounts
- The script should work in both workspace and standalone checkout modes
- direnv must be installed and configured for the project

## LSP Configuration (Ported from OpenCode)

The kilo LSP configuration has been updated to match the opencode configuration,
which uses openmoat. The LSP servers include:

- Python (pyright-langserver)
- Python Pyrefly (pyrefly lsp)
- TypeScript (typescript-language-server)
- Rust (rust-analyzer)
- Go (gopls)

This ensures consistent language server support across both tools.

## OpenMoat/OpenCode Configuration Alignment

The kilo configuration has been aligned with opencode's advanced config:

- MCP ai-hub uses canonical native form (openmoat mcp proxy)
- Browse MCP server added
- Cliproxy provider with ai-hub models added
- Model set to cliproxy/ai-hub-balanced
- Small model set to cliproxy/ai-hub-fast

See ADR-035 for details.
