---
name: flext-context-routing
description: 'Use this skill to use when selecting tools, prompts, MCP servers, and
  skills automatically by project/session context. Triggers on requests about automation,
  tool choice, simplification, deduplication, safe execution, context detection, and
  cross-project routing. DO NOT USE FOR: questions unrelated to flext-context-routing
  creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# FLEXT Context Routing

**UTILITY SKILL**

## USE FOR

- Requests about flext context routing.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to flext-context-routing.
- creating projects or architecture from scratch.

## Workflow

1. Identify touched paths and task intent.
2. Detect project governance and stack markers.
3. Check tool readiness: correct Scope root, `scope status`, Serena project/config availability, and configured MCP relevance.

## Critical rules

- Prefer canonical sources.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
