# Kilo Code ↔ OpenMoat/OpenCode advanced config alignment

Date: 2026-11-20

## Goal
Apply the advanced OpenMoat/OpenCode configuration to Kilo Code so both clients
share the same canonical ai-hub MCP transport, cliproxy provider, and browse MCP.

## Changes applied
- ~/.config/kilo/kilo.json and kilo.jsonc:
  - mcp.ai-hub.command switched from wrapper script to canonical native form:
    openmoat mcp proxy --server ai-hub --host kilo -- /home/marlonsc/.local/bin/ai-hub mcp --action client --agent kilo
  - Added browse MCP server (mirroring opencode).
  - Added cliproxy provider block (mirroring opencode) with ai-hub-balanced/fast/frontier/most-capable models.
  - Set model=cliproxy/ai-hub-balanced, small_model=cliproxy/ai-hub-fast.
  - Fixed missing comma before "formatter" (jsonc validity).
- Bead: flext-qd9e4 (task, P2) tracks this alignment.
- Learning recorded (kilo memory): use Read/Glob/Grep tools, never bash cat/find/grep.

## Canonical command-form rule (learned)
Prohibited (hook-warned) bash forms: cat, find, grep, head, tail as evidence.
Use the dedicated Read/Glob/Grep tools. Record this in ~/agents general
instructions; never bypass canonical tool surface.

## Open work / next steps
- Validate Kilo starts and ai-hub MCP connects with the new canonical form.
- Update ~/agents/AGENTS.md and ADR index with the canonical-tool rule when the
  agents repo lane is available (currently on fix/storage-fixture-no-venv with
  uncommitted WIP; do not clobber).
- Close bead flext-qd9e4 after runtime proof.
