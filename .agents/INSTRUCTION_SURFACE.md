# Instruction Surface Manifest

**Reviewed**: 2026-04-27 | **Scope**: Complete audit of all agent/skill/MCP/instruction surfaces

Canonical governance: [`AGENTS.md`](../AGENTS.md)

## Hard Start Card

This file is inventory and routing only. Policy lives in [`AGENTS.md`](../AGENTS.md).

1. Read `AGENTS.md` §0 first.
2. Run `qlty smells --all --sarif --include-tests > /tmp/qlty_smells-tests.json` before the next refactor cycle.
3. If the selected smell is stale or already gone, rerun `qlty` immediately.
4. Pick one offender only.
5. Search owner/origin before writing.
6. Single-caller private helper = inline delete. No new carrier model or wrapper.
7. Reuse `c/m/p/t/u` or parent method before adding anything.
8. New helper/proxy/wrapper before proof of no origin is invalid.
9. Manual kwargs key/type normalization is invalid when one Pydantic validation call can own payload.
10. True option bags: `model_validate(kwargs)` once; fixed-shape APIs: explicit params + one packed `model_validate({...})`.
11. Parameter-count smell does not justify widened kwargs or a new carrier model; reuse the owner model, enum, or `match/case` first.
12. First edit is followed immediately by `ruff` then `pyrefly` on the touched file.
13. Before first patch, write the 4-item brutal self-critique (risk, stop-rule, primitive, propagate+gate command).
14. Pointer/meta docs reinforce routing and tool choice only; normative rules are updated in `AGENTS.md`.

---

## §1 Surface Hierarchy

This section is load-order only. Startup law stays in the Hard Start Card above and canonically in `AGENTS.md` §0.

```
LOAD ORDER (highest authority first):
1. AGENTS.md              — FLEXT canonical governance (SSOT)
2. .agents/skills/        — FLEXT path-scoped skills (52 skills)
3. .github/prompts/       — workspace prompts for high-intensity task modes
4. .github/copilot-instructions.md — pointer only → AGENTS.md
5. ~/.claude/CLAUDE.md    — universal user profile + GSD
6. ~/.claude/rules/       — language-level rules (python, rust, ts, k8s)
7. ~/.copilot/agents/     — user-level agents (CLEAN — see §4)
8. ~/.copilot/skills/     — user-level skills (manifest only)
9. ~/.agents/skills/      — user-level unique skills (4 skills)
10. ~/.vscode/agent-plugins/ — installed plugin repos (see §3)
```

---

## §2 Workspace Surfaces (canonical)

| Surface | Path | Count | Status |
|---------|------|-------|--------|
| FLEXT Skills | `.agents/skills/` | 52 skills | ✅ Canonical |
| GitHub Prompts | `.github/prompts/` | 1 prompt | ✅ Default refactor directive |
| Copilot Instructions | `.github/copilot-instructions.md` | pointer | ✅ OK |
| Serena Project Config | `.serena/project.yml` | 1 config | ✅ Present |
| Cline Rules | `.clinerules` | pointer | ✅ OK |
| Windsurf Rules | `.windsurfrules` | pointer | ✅ OK |
| Codex | `codex.md` | pointer | ✅ OK |
| Child AGENTS | `<repo>/AGENTS.md` × 30 | pointer | ✅ OK |
| MCP Config | `.vscode/mcp.json` | empty | ⚠️ See §5 |

---

## §3 Installed Plugin Repos (`~/.vscode/agent-plugins/`)

Plugins are loaded automatically by VS Code Copilot. Do NOT copy their
skills/agents into `.agents/` — they are already surfaced by the plugin system.

| Plugin Repo | Size | Skills | Agents | Relevance |
|-------------|------|--------|--------|-----------|
| `github/awesome-copilot` | 139MB | 296 | 203 | HIGH — generic engineering toolkit |
| `davepoon/buildwithclaude` | 37MB | 6 | 6 | MEDIUM — multi-agent builders (ag2, triforce) |
| `obra/episodic-memory` | 5.7MB | 1 | 1 | LOW — semantic convo search (claude-mem overlap) |
| `obra/double-shot-latte` | 9MB | 0 | 0 | MEDIUM — auto-continue decision |
| `obra/superpowers` | 1MB | 0 | 1 | MEDIUM — brainstorm/execute-plan/write-plan cmds |
| `mhattingpete/claude-skills-marketplace` | 3.1MB | 14 | 0 | HIGH — code-auditor, test-fixing, git-pushing |
| `github/copilot-plugins` | varied | 3 | 0 | MEDIUM — secret-scanning (useful) |
| `Piebald-AI/claude-code-lsps` | 548KB | 0 | 0 | MEDIUM — basedpyright LSP config |

### Removed plugins (2026-04-19)

| Removed | Reason |
|---------|--------|
| `microsoft/What-I-Did-Copilot` | Daily work tracker — not FLEXT relevant |
| `scaryrawr/scarypilot` | Azure DevOps focused — not FLEXT relevant |
| `daothihuong2111/*` | Empty repository |
| `obra/episodic-memory/node_modules` | 439MB node_modules removed (reinstallable) |

---

## §4 User-Level Agent/Skill Surfaces

### `~/.copilot/agents/` — CLEANED (2026-04-19)

All 40 agents that were here were exact duplicates of `github/awesome-copilot/agents/`.
Since `awesome-copilot` is loaded as a plugin, these were loaded twice.
**All 40 removed.** Backup at `/tmp/copilot-agents-backup-20260419/`.

### `~/.copilot/installed-plugins/thedotmack/claude-mem/`

Memory management plugin with 7 skills: `do`, `knowledge-agent`, `make-plan`,
`mem-search`, `smart-explore`, `timeline-report`, `version-bump`.
**KEEP** — provides cross-session memory for Claude Code. No overlap with workspace.

### `~/.agents/skills/` (user-level, 4 unique skills)

| Skill | Purpose | Overlap |
|-------|---------|---------|
| `microsoft-foundry` | Foundry deploy/eval | None in workspace |
| `ask` | Code archaeology | None in workspace |
| `git-ai-search` | Search git for AI conversations | None in workspace |
| `prompt-analysis` | Analyze prompting patterns | None in workspace |

### `~/.claude/agents/` (user-level, 8 GSD agents)

GSD workflow agents: `gsd-advisor-researcher`, `gsd-assumptions-analyzer`,
`gsd-codebase-mapper`, `gsd-debugger`, `gsd-executor`, `gsd-integration-checker`,
`gsd-nyquist-auditor`, `gsd-phase-researcher`.
**KEEP** — GSD workflow, no overlap with workspace skills.

### `~/.claude/rules/` (language rules, 4 files)

python.md, rust.md, typescript.md, kubernetes.md — always-apply language rules.
These supplement AGENTS.md with language-specific defaults.
**KEEP, NO OVERLAP** with workspace (AGENTS.md delegates to these).

---

## §5 MCP Server Gap

`.vscode/mcp.json` has `servers: {}` — no MCP servers configured.

Recommended MCP servers for FLEXT workflows:

```json
{
  "servers": {
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${env:GITHUB_TOKEN}" }
    },
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/marlonsc/flext"]
    }
  }
}
```

> Note: Apply only when GitHub token is available and MCP use is intentional.

### Serena Status

- `.vscode/mcp.json` registers the workspace Serena MCP server through `serena start-mcp-server --context=vscode --project-from-cwd`.
- `.serena/project.yml` is present and configured for project `flext` with Python language support.
- When Serena-backed tooling is available, agents must use the installed `serena` CLI, validate the local project with `serena project health-check`, and activate/setup the `flext` project correctly before relying on Serena navigation or rename flows.
- Serena setup is not optional for Serena-dependent tasks; half-configured usage is treated as a tooling failure that must be surfaced explicitly.

---

## §6 Deduplication Findings: Sub-Repo Docs

Each of 30 sub-repos has `docs/guides/skill-automation-pattern.md`.
These are project-specific evolved copies of the skill pattern guide,
NOT governance duplicates. They are developer reference docs and intentionally
project-scoped. No action required — do not delete.

---

## §7 What Belongs in `.agents/skills/` (FLEXT canonical)

All FLEXT-specific domain skills live here. Do NOT copy generic skills
from installed plugins into `.agents/skills/`. Plugin skills are loaded
automatically by the VS Code Copilot plugin system.

Add to `.agents/skills/` ONLY when:

1. The skill is FLEXT-domain-specific (MRO, pydantic governance, etc.)
2. The skill needs to be available to Claude Code (not just VS Code Copilot)
3. The skill cannot be sourced from any installed plugin

---

## §8 Prompt Routing

Use workspace prompts only for task-mode amplification, never as an alternate policy source.

- `flext-aggressive-scale-refactor.prompt.md` is the default high-intensity mode for requests about simplification, deduplication, pyrefly/ruff reduction, contract centralization, facade migration, MRO cleanup, or aggressive Pydantic v2 standardization.
- Prompts do not override `AGENTS.md`; they operationalize it for a specific execution mode.
- When that prompt is selected, agents still load `AGENTS.md` first, then path-scoped skills, then the prompt.

---

*Last audit: 2026-04-19 | Auditor: agent | Evidence: removed 40 duplicate agents,
439MB node_modules, 2 irrelevant plugins, 1 empty org dir.*
