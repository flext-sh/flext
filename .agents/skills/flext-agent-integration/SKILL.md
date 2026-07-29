---
name: flext-agent-integration
description: 'Guidance for setting up agent tooling, configuring MCP tools, or enabling automatic project-context routing across FLEXT and non-FLEXT repositories. Covers skill discovery, tool priority ordering, session start protocols, safe tool guardrails, and agent configuration.'
license: MIT
metadata:
  version: 1.0.0
---
# FLEXT Agent Integration

## Workflow

1. Detect the Git root, scoped `AGENTS.md`, provider manifest, stack markers, and
   paths implicated by the request.
2. Route repository knowledge to local resources and skills before external tools.
3. Check tool readiness before selection: Scope index/root, configured MCP servers,
   and the canonical Make/CLI surface.
4. Choose the least powerful tool that returns decisive evidence; do not start an
   MCP server or broad index when local structural search already answers the task.
5. Preserve the operator's intent, writable paths, validation commands, and stop
   condition across any handoff.

## Tool order

1. Repository docs, configuration, code, and generated-owner metadata.
2. Scope for symbols and relationships; `rg` for exact text and non-code assets.
3. Path-specific validators and canonical Make verbs.
4. Configured MCP resources for external systems they own.
5. Official upstream documentation when the contract is external or time-sensitive.

## Guardrails

- Never treat an unavailable optional tool as permission to bypass a canonical gate.
- Do not send repository secrets, credentials, or unnecessary source to external tools.
- Keep tool output bounded to the decision; store long evidence in the task ledger.
- Distributed agent configuration is owned by its provider source, not a generated
  workspace projection.
