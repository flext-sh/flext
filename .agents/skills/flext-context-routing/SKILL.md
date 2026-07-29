---
name: flext-context-routing
description: 'Guidance for selecting tools, prompts, MCP servers, and skills automatically by project/session context. Triggers on requests about automation, tool choice, simplification, deduplication, safe execution, context detection, and cross-project routing.'
license: MIT
metadata:
  version: 1.0.0
---
# FLEXT Context Routing

## Workflow

1. Identify touched paths and task intent.
2. Detect project governance and stack markers.
3. Check tool readiness: correct Scope root, `scope status`, Serena project/config availability, and configured MCP relevance.

## Contracts

- Resolve authority in this order: operator request, scoped `AGENTS.md`, accepted architecture/docs, then the task-specific skill.
- Load only skills whose trigger matches the touched path or technology.
- Prefer repository resources and structural tools before external search or broad text scans.
