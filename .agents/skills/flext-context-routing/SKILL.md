---
name: flext-context-routing
description: Use when selecting tools, prompts, MCP servers, and skills automatically by project/session context. Triggers on requests about automation, tool choice, simplification, deduplication, safe execution, context detection, and cross-project routing.
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
- `.agents/skills/flext-scope-bootstrap/SKILL.md`
- `.serena/project.yml`
- `.vscode/mcp.json`

## Rules

- Detect project context before choosing tools.
- Load governance first, then only path-relevant skills.
- Detect task intent as well as touched paths; route high-intensity refactor intents to the workspace prompt after loading governance and skills.
- Prefer structural navigation before raw text scans when available.
- When `scope` is available, treat it as mandatory for cross-file discovery, blast-radius checks, and caller/reference analysis.
- When Scope config is missing, stale, or invalid, bootstrap it from the correct root with the official CLI (`scope init` or `scope workspace init`) instead of hand-authoring config files.
- When Serena is available, treat correct Serena project activation/setup as mandatory before Serena-backed symbol or refactor operations.
- Use the installed `serena` CLI from the official quick-start flow for durable setup. Do not route workspace MCP through ad-hoc `uvx` wrappers or repo-local shell scripts.
- When a change is structural or repeated, route to `ast-grep` rather than manual grep-only propagation.
- Use project-native validation commands for changed scope.
- Enforce context guardrails: no destructive git/filesystem operations unless explicitly requested.
- Use MCP when task needs remote metadata/integration and server is configured; do not skip configured MCP context for tasks that depend on it.
- Avoid editing generated/vendor/cache trees unless explicitly requested.

## Instructions

- Context detection order:
  1. `AGENTS.md` / `CLAUDE.md`
  2. `.agents/skills/`
  3. `.github/prompts/` when the request is a task-mode match
  4. Stack markers (`pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`)
  5. MCP marker (`.vscode/mcp.json`)
- Tool routing by task class:
  - Discover/search: `scope` first when available; if Scope is missing or invalid, load `flext-scope-bootstrap`, repair from the correct root, and then continue.
  - Single-file edit: patch/edit tools.
  - Multi-file refactor: `scope` for blast radius, Serena where project-aware symbol tooling applies, `ast-grep` for structural propagation, then scoped verification.
  - Validation: project-native lint/type/test gates.
- Serena readiness baseline for FLEXT:
  - Confirm install surface: `command -v serena`
  - Confirm CLI surface: `serena --help` and `serena start-mcp-server --help`
  - Confirm repo-local project health: `serena project health-check`
  - If `.serena/project.yml` is missing, create it with `serena project create . --name flext --language python --index`
  - Keep workspace MCP config in `.vscode/mcp.json` on `serena start-mcp-server --context=vscode --project-from-cwd`
- Intent routing:
  - Simplify/deduplicate/refactor/pyrefly-reduction/contract-centralization requests: load `.github/prompts/flext-aggressive-scale-refactor.prompt.md` after `AGENTS.md` and the path-scoped skills.
  - Documentation pointer cleanup: load `flext-docs-pointer-policy` and keep prompts pointer-only.
- Session routing:
  - Preserve active objective from current session.
  - Continue from latest verified state unless user redirects.

## Workflow

1. Identify touched paths and task intent.
2. Detect project governance and stack markers.
3. Check tool readiness: correct Scope root, `scope status`, Serena project/config availability, and configured MCP relevance.
4. Load minimal relevant skills.
5. If Scope is missing or stale, load `flext-scope-bootstrap` and repair the setup before using structural queries.
6. If the intent is broad simplification/refactor, load the workspace prompt for that task mode.
7. Route tools/MCP according to task class.
8. Execute scoped changes.
9. Run scoped validation.
10. Report results and assumptions.

## Examples

Good:

- Request: "fix pyright errors in flext-core models"
- Route: load `AGENTS.md` + `rules-flext-core` + typing skills; use scoped edits; run project type/lint checks.

- Request: "deduplicate conversions across flext-ldif and reduce pyrefly errors"
- Route: load `AGENTS.md` + path skills + `.github/prompts/flext-aggressive-scale-refactor.prompt.md`; prioritize canonical Pydantic models, constants, and same-cycle propagation.

Bad:

- Request: "fix one test"
- Route: runs broad workspace rewrite and edits vendor folders.
- Why bad: ignores scope and context guardrails.

## Verification

- `test -f AGENTS.md && test -d .agents/skills`
- `rg -n "^name:|^description:" .agents/skills/flext-context-routing/SKILL.md`
- `rg -n "Use when selecting tools, MCP servers, and skills automatically" .agents/skills/flext-context-routing/SKILL.md`
- `command -v serena && serena --help >/dev/null && serena start-mcp-server --help >/dev/null`
- `serena project health-check`
