# ADR-035: Kilo Code OpenMoat/OpenCode Configuration Alignment

## Status

Superseded by [ADR-036](036-flext-consumes-no-ai-hub-configuration.md) (2026-11-24).

## Context

Kilo Code and OpenCode (which uses OpenMoat) had divergent configurations.
OpenCode had advanced features like cliproxy provider, browse MCP, and
canonical ai-hub MCP transport that kilo lacked.

## Decision

Align kilo-code configuration to match opencode's advanced config:

1. MCP ai-hub command uses canonical native form (openmoat mcp proxy)
2. Added browse MCP server
3. Added cliproxy provider with ai-hub-balanced/fast/frontier/most-capable models
4. Set model=cliproxy/ai-hub-balanced, small_model=cliproxy/ai-hub-fast
5. Fixed JSONC validity (missing comma before formatter)

Both `~/.config/kilo/kilo.json` and `~/.config/kilo/kilo.jsonc` are updated.

## Consequences

### Positive

- Consistent configuration across kilo and opencode
- Same model provider (cliproxy) available in both tools
- Browse MCP available in kilo
- Canonical ai-hub MCP transport in both

### Negative

- Configuration must be maintained in two places
- Hardcoded paths to ai-hub runtime

## Implementation

- `~/.config/kilo/kilo.json` - Full config update
- `~/.config/kilo/kilo.jsonc` - Full config update
- Bead: flext-qd9e4 (closed)

## Related

- ADR-033: AI Hub MCP Project Environment Activation
- ADR-034: Kilo LSP Configuration Parity with OpenCode
