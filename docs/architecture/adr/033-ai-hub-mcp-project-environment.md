# ADR-033: AI Hub MCP Project Environment Activation

## Status

Superseded by [ADR-036](036-flext-consumes-no-ai-hub-configuration.md) (2026-11-24).

## Context

The AI Hub MCP client was running without the correct project environment
context, causing validation failures. The MCP client needs to:

1. Run from the correct project root directory
2. Have direnv activated to load project environment variables
3. Use the correct Python virtual environment
4. Have access to all project-specific tools and paths

## Decision

Create a wrapper script (`scripts/ai-hub-mcp/ai-hub-mcp-wrapper.sh`)
that:

1. Derives the project root from the script location
2. Changes to the project root
3. Sources direnv to activate the project environment
4. Finds and executes ai-hub with the activated environment

Update kilo configuration to use this wrapper script.

## Consequences

### Positive

- MCP client always runs with correct project context
- No manual environment variable passing needed
- Portable across different user accounts
- Works in both workspace and standalone checkout modes

### Negative

- Additional script file to maintain
- Dependency on direnv being installed and configured

## Implementation

- Wrapper script: `scripts/ai-hub-mcp/ai-hub-mcp-wrapper.sh`
- Kilo config: `~/.config/kilo/kilo.json` and `~/.config/kilo/kilo.jsonc`
- Documentation: `docs/ai-hub-mcp-wrapper.md`

## Related

- ADR-032: Host-wide heavy-gate admission
- ADR-005: Config/settings SSOT
