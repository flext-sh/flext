---
name: flext-agent-integration
description: 'Use this skill to use when setting up agent tooling, configuring MCP
  tools, or enabling automatic project-context routing across FLEXT and non-FLEXT
  repositories. Covers skill discovery, tool priority ordering, session start protocols,
  safe tool guardrails, and agent configuration. DO NOT USE FOR: questions unrelated
  to flext-agent-integration creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# FLEXT Agent Integration

**UTILITY SKILL**

## USE FOR

- Requests about flext agent integration.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to flext-agent-integration.
- creating projects or architecture from scratch.

## Workflow

1. Identify touched paths.
2. Identify whether the request intent matches a workspace prompt.
3. Check whether `scope` is available, whether Serena is configured/usable (`command -v serena`, `serena start-mcp-server --help`, `serena project health-check`), and whether `ast-grep` or MCP is required by the task.

## Critical rules

- Prefer canonical sources.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
