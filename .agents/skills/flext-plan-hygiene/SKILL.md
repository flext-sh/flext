---
name: flext-plan-hygiene
description: Use when managing implementation plans across sessions to prevent plan proliferation. Covers consolidation, deduplication, and archival protocols for maintaining single-source-of-truth task tracking in Beads. Load before spawning new tasks or resuming multi-session work.

---

# Flext Plan Hygiene

**Reviewed**: 2026-06-07 | **Scope**: Beads consolidation rules, overlap detection, cross-session deduplication, and archival protocol

## Scope

- Beads (`bd`) as the only pending-work, ownership, lease, and dependency SSOT
- Legacy markdown/task-board files as read-only migration sources only
- `git log` (cross-session task history)

## References

- `AGENTS.md` §10.0 Beads Pending-Work SSOT
- `AGENTS.md` §11 Beads-First Multi-Agent Coordination
- `bd --help`

## Rules

- **One Bead Hierarchy Per Scope**: Never create a new plan file if an existing Bead or Bead parent covers the same scope.
- **Overlap Detection**: Before creating a Bead, check existing Beads for overlapping task ranges.
- **Cross-Session Deduplication**: Check `git log` for completed tasks before starting new work.
- **Legacy Plan Archival**: After importing actionable content into Beads, remove tracked legacy plans with `git rm` or archive ignored files as `.bak`.
- **Consolidation First**: Merge small task threads into larger scoped Beads rather than proliferating plan files.
- **Local CLI Reality**: In this repository, use local `bd 1.0.5` with Dolt. Do not write plans that require legacy SQLite/no-db/daemon sync or unsupported commands unless `bd --help` and `bd context --json` prove they apply to this workspace.
- **Tooling and Gate Reality**: Plans for refactors or workspace maintenance must explicitly account for Scope/Serena/`ast-grep`/MCP applicability and the requirement to return all affected projects to zero `ruff`, `pyrefly`, enforcement, and `pytest` debt.

## Instructions

### Beads Consolidation Rules

1. **Check Existing Beads**: Before creating a new pending-work item, search existing Beads:

   ```bash
   bd search "<scope keyword>"
   bd list --status open
   bd list --status in_progress
   ```

2. **Identify Overlapping Scope**: Inspect matching Beads and their dependencies:

   ```bash
   bd show <id>
   bd dep tree <id>
   ```

3. **Merge Instead of Proliferate**: If new work overlaps with an existing Bead:
   - Add detail to the existing Bead with `bd update` or `bd comments add`
   - Add child Beads only for real execution units
   - Document the merge in the Bead notes/comments

### Overlap Detection Checklist

Before creating a new Bead, verify:

- [ ] No existing Bead covers the same project(s)
- [ ] No existing Bead has overlapping task ranges (e.g., T1-T10 vs T5-T15)
- [ ] No existing Bead targets the same architectural layer
- [ ] No existing Bead addresses the same quality gate or validation scope
- [ ] Scope is genuinely new or a natural extension of an existing Bead

### Cross-Session Deduplication Protocol

1. **Check Git Log for Completed Tasks**:

   ```bash
   git log --oneline --all -20
   ```

2. **Verify Task Completion Status**:

   ```bash
   bd list --status closed
   bd list --status open
   ```

3. **If Task Already Done**:
   - Do NOT recreate the task in a new plan file
   - Relate the new Bead to the completed Bead if context is still useful
   - Link to the commit or Bead close reason that completed the work

### Multi-Session And Multi-Project Protocol

1. **One Active Tracker**:
   - Use Beads for current ownership, status, dependencies, and handoff notes.
   - Do not create or update `.agents/coordination/tasks.md` for active leases.
   - If a legacy task board exists, import actionable rows into Beads first, then remove or archive the board.

2. **One Repository Boundary**:
   - Each independent repository owns one `.beads/` directory at its repo root.
   - In this workspace, use `project:<member>` labels for member projects unless that member is an independent repo with its own Beads store.
   - Use `bd repo add/list/sync`, `bd ship`, and supported `external:<project>:<capability>` dependencies for cross-project visibility.
   - Use Dolt shared-server mode for concurrent writers; embedded mode is only for solo work.

3. **Agent Ownership**:
   - Claim executable work with `bd update <id> --claim --json`.
   - Long-lived agents use agent beads plus `bd agent state`, `bd agent heartbeat`, and `bd slot set <agent-bead> hook <work-bead>` when an agent bead exists.
   - Worker subagents get their own child Bead and disjoint write scope before they start.

4. **Recovery Order**:
   - Freeze Beads writers before recovery and capture `bd context --json`, `bd dolt show`, `bd status --json`, `bd dep cycles --json`, and `bd backup status --json`.
   - Run `bd backup sync` before any destructive or migration repair.
   - Treat JSONL as import/export material only; run `bd import --dry-run` before any JSONL import.
   - Rebuild with documented `bd bootstrap`, `bd import`, or `bd backup restore` paths, then validate with `bd status`, `bd dolt show`, `bd backup status`, `bd dep cycles`, and `bd graph`.
   - Do not use `bd --no-db`, SQLite sync, or daemon kill/restart loops for normal Dolt-backed work.

### Legacy Plan Archival Protocol

1. **Archive Completed Legacy Plans**:

   ```bash
   bd comments add <id> "Legacy source imported: <path>"
   git rm <tracked legacy plan>
   ```

2. **Archive Ignored Markdown Only When Needed**:

   ```bash
   mv <ignored legacy plan>.md <ignored legacy plan>.md.bak
   ```

3. **Preserve Learnings In Beads**:
   - Add durable decisions to the owning Bead comment
   - Add broad governance changes to `AGENTS.md` or the relevant skill
   - Do not keep legacy markdown as active task tracking

## Workflow

1. **Before Creating a Plan**:
   - Run overlap detection checklist
   - Check git log for related completed work
   - Review existing Bead scopes and dependency trees
   - Verify the plan includes impact analysis, tool usage, propagation, and zero-debt closure when the task is cross-file or cross-project

2. **When Consolidating Work**:
   - Merge task lists into the larger Bead hierarchy
   - Update the Bead description or add a comment
   - Use `bd dep relate` or parent-child dependencies for hierarchy

3. **When Archiving Legacy Plans**:
   - Verify all tasks are completed
   - Ensure pending items were imported into Beads
   - Remove tracked markdown with `git rm`
   - Rename ignored markdown to `.bak` only after import

## Examples

Good:

```markdown
## Scope

- Wave 0: Skills fixes (4 contradictions + new skill)
- Wave 1: Type reference fixes (3 P0 broken refs)
- Wave 2: Import rule enforcement (2 projects)
- Wave 3: Architecture validation (workspace-wide)

**Consolidation**: All waves in single plan to maintain unified task tracking.
```

Why good: Single plan covers related work across multiple waves, preventing plan proliferation.

Bad:

```markdown
## Scope

- Fix flext-architecture-layers skill

---

## Scope (NEW PLAN)

- Fix flext-patterns skill

---

## Scope (ANOTHER NEW PLAN)

- Fix flext-import-rules skill
```

Why bad: Three separate plans for related skill fixes; should be consolidated into one plan.

## Verification

Make gates:

- `make val VALIDATE_SCOPE=workspace` — workspace validation ensures plan consistency

Pattern checks:

- `bd search "<scope keyword>"` — detect overlapping Beads
- `bd dep cycles` — dependency graph must be acyclic
- `bd graph --all --compact` — inspect active hierarchy
- `rg -n "legacy pending-work source|legacy plan" AGENTS.md .agents docs` — detect stale legacy-plan references without reviving retired path names
