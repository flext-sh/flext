# Critically review architectural lint exceptions

## Authority

Read [the current FLEXT session router](../../../.agents/commands/flext-law.md)
and [this task collection](README.md) before execution. This file supplies only
the task-specific owner, diagnosis and acceptance delta.

## Exclusive ownership

Own the exception decision and, only after coordination, the typed exception policy model/catalog and projection in flext-infra. Do not concurrently edit the generator or consumers owned by other prompts.

## Sources to inspect

flext-infra/src/flext_infra/config/tooling.yaml; _models/deps_tool_config_linters.py; deps/phases/ensure_ruff.py; templates/project/base/pyproject.toml.j2. Historical commit 8021e7ccf3 removed an authorized-exceptions catalog; inspect its parent for provenance only.

## Required correction

Classify each historic rule/scope independently: formatter-owned COM812 and current TC/non-empty-init rulings may already be represented; facade CamelCase-to-letter aliases and exact SDK signature mirrors may have architectural grounds; relative static imports, temporary line-length allowances, private test access and complexity allowances require source repair where possible. Do not copy the old catalog wholesale or revive informative severities. Preserve current authorization data and reject duplicate/overbroad scopes through typed validation if an exception representation is actually needed.

## Acceptance evidence

Prove each retained exception is necessary with a real consumer and exact bounded scope; prove rejected exceptions have a source fix or an explicit unresolved finding. Regenerate and validate the projection through native Make, showing no unrelated rule or coverage change.
