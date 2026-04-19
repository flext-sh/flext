---
name: flext-context-routing
description: Use when selecting tools, MCP servers, and skills automatically by project/session context. Triggers on requests about automation, tool choice, safe execution, context detection, and cross-project routing.
---

# FLEXT Context Routing

## Scope

- `.agents/skills/`
- Repository-level task routing and tool selection

## References

- `AGENTS.md`
- `CLAUDE.md`
- `.github/copilot-instructions.md`
- `.agents/skills/flext-agent-integration/SKILL.md`

## Rules

- Detect project context before choosing tools.
- Load governance first, then only path-relevant skills.
- Prefer structural navigation before raw text scans when available.
- Use project-native validation commands for changed scope.
- Enforce context guardrails: no destructive git/filesystem operations unless explicitly requested.
- Use MCP only when task needs remote metadata/integration and server is configured.
- Avoid editing generated/vendor/cache trees unless explicitly requested.

## Instructions

- Context detection order:
  1. `AGENTS.md` / `CLAUDE.md`
  2. `.agents/skills/`
  3. Stack markers (`pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`)
  4. MCP marker (`.vscode/mcp.json`)
- Tool routing by task class:
  - Discover/search: structural tools, then fast text search.
  - Single-file edit: patch/edit tools.
  - Multi-file refactor: structural changes with scoped verification.
  - Validation: project-native lint/type/test gates.
- Session routing:
  - Preserve active objective from current session.
  - Continue from latest verified state unless user redirects.

## Workflow

1. Identify touched paths and task intent.
2. Detect project governance and stack markers.
3. Load minimal relevant skills.
4. Route tools/MCP according to task class.
5. Execute scoped changes.
6. Run scoped validation.
7. Report results and assumptions.

## Examples

Good:

- Request: "fix pyright errors in flext-core models"
- Route: load `AGENTS.md` + `rules-flext-core` + typing skills; use scoped edits; run project type/lint checks.

Bad:

- Request: "fix one test"
- Route: runs broad workspace rewrite and edits vendor folders.
- Why bad: ignores scope and context guardrails.

## Verification

- `test -f AGENTS.md && test -d .agents/skills`
- `rg -n "^name:|^description:" .agents/skills/flext-context-routing/SKILL.md`
- `rg -n "Use when selecting tools, MCP servers, and skills automatically" .agents/skills/flext-context-routing/SKILL.md`
