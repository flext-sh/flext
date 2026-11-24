# ADR-036: Flext Carries No AI Hub Configuration

## Status

Accepted (2026-11-24). Supersedes ADR-033, ADR-034 and ADR-035.

## Context

Earlier ADRs wired AI Hub into this workspace from the flext side: a shell wrapper
(`scripts/ai-hub-mcp/ai-hub-mcp-wrapper.sh`, ADR-033), a duplicated LSP block in the
operator's kilo configuration (ADR-034) and an AI Hub/OpenMoat provider and MCP
alignment in that same global configuration (ADR-035). Their own consequence sections
record the defects of that shape: "hardcoded paths to ai-hub runtime" and
"configuration must be maintained in two places".

The resulting state was measured on 2026-11-24:

- `.vscode/mcp.json` carried an `ai-hub` client bridge with AI Hub environment
  variables (`AI_HUB_MCP_SOCKET`, `AIHUB_PROJECT_ROOT`) and `--agent kilo`.
- A workspace-owned shell wrapper re-implemented the AI Hub client launch.
- Three accepted ADRs documented AI Hub integration owned by this workspace.
- The live kilo configuration had no `mcp` root, so the gateway was not projected by
  its actual owner even though the declarations exist in AI Hub's agent registry.

AI Hub already owns this projection: its agent registry declares the kilo
`mcp_generation` (MCP root key, client bridge, live configuration path) and its hook
and stdio-MCP policy is owned by OpenMoat under AI Hub's own ADRs. Project MCP files
are explicitly not written by AI Hub (operator ruling 2026-10-09), and its artifact
catalog classifies `.vscode/mcp.json` as machine-local runtime wiring, not a projection
it authors.

## Decision

1. This workspace carries **no AI Hub-specific configuration**: no gateway client
   bridge, no AI Hub environment variables, no AI Hub launch wrapper, no AI Hub runtime
   or tool paths, and no duplicated global agent configuration.
2. AI Hub is the **sole owner** of projecting its MCP gateway and hooks into agent
   homes, including kilo, from its own typed configuration and through its own deploy
   and hook-policy path. That activation is performed by AI Hub, never from this
   workspace.
3. This workspace keeps only the independent tools it consumes directly. The
   `code-review-graph` MCP server stays because it is a standalone graph tool launched
   directly, not the AI Hub gateway.
4. Authored IDE configuration uses the current schema of its native owner and contains
   no machine-specific AI Hub wiring.

## Consequences

### Positive

- One owner per projection: AI Hub projects its own MCP and hooks; this workspace
  contains none of it.
- No hardcoded AI Hub runtime paths and no duplicated configuration maintained in two
  places.
- The workspace remains usable standalone, independent of the AI Hub installation.
- Superseded wrappers, docs and ADRs are removed rather than kept as a compatibility
  path.

### Negative

- Availability of AI Hub MCP tools in the kilo editor surface depends on AI Hub
  projecting its own configuration; this is an external owner dependency and does not
  block this workspace's completion.
- A hand-written AI Hub entry can no longer be used as a local shortcut here.

## Implementation

- `.vscode/mcp.json` keeps only the independent `code-review-graph` server; the
  `ai-hub` and stale `serena` entries are removed.
- `scripts/ai-hub-mcp/ai-hub-mcp-wrapper.sh` and `docs/ai-hub-mcp-wrapper.md` are
  deleted.
- ADR-033, ADR-034 and ADR-035 are marked superseded by this record.

## Related

- ADR-005: Config, settings, constants, templates and schemas SSOT.
- ADR-033, ADR-034, ADR-035: superseded integration records.
