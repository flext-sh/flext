# ADR-034: Kilo LSP Configuration Parity with OpenCode

## Status

Superseded by [ADR-036](036-flext-consumes-no-ai-hub-configuration.md) (2026-11-24).

## Context

The kilo-code LSP configuration was empty, while opencode had a full LSP
configuration using openmoat. This inconsistency meant that kilo-code users
did not have access to the same language server support as opencode users.

## Decision

Port the LSP configuration from opencode to kilo-code, including:

- Python (pyright-langserver)
- Python Pyrefly (pyrefly lsp)
- TypeScript (typescript-language-server)
- Rust (rust-analyzer)
- Go (gopls)

Both `~/.config/kilo/kilo.json` and `~/.config/kilo/kilo.jsonc` are updated.

## Consequences

### Positive

- Consistent LSP support across kilo and opencode
- Python development benefits from pyright and pyrefly
- TypeScript, Rust, and Go support available

### Negative

- Configuration must be maintained in two places
- LSP server paths are hardcoded to ai-hub runtime

## Implementation

- `~/.config/kilo/kilo.json` - LSP section added
- `~/.config/kilo/kilo.jsonc` - LSP section added
- `docs/ai-hub-mcp-wrapper.md` - Updated with LSP info
