<!-- TOC START -->

- [Scope](#scope)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
- [Workflow](#workflow)
- [Examples](#examples)
- [Verification](#verification)

<!-- TOC END -->

---

name: flext-plan-hygiene
description: Plan consolidation, deduplication, and archival protocols to prevent plan proliferation and maintain single-source-of-truth task tracking.

---

# Flext Plan Hygiene

**Reviewed**: 2026-02-28 | **Scope**: Plan consolidation rules, overlap detection, cross-session deduplication, and archival protocol

## Scope

- `.sisyphus/plans/` (plan files)
- `.sisyphus/notepads/` (session learnings)
- `git log` (cross-session task history)

## References

- `AGENTS.md` § Agent Roster (Sisyphus-Junior executor discipline)
- `.sisyphus/plans/workspace-final-standardization.md` (canonical consolidated plan)
- `.sisyphus/notepads/workspace-final-standardization/` (learnings, issues, decisions)

## Rules

- **One Plan Per Scope**: Never create a new plan if an existing plan covers the same scope.
- **Overlap Detection**: Before creating a plan, check existing plans for overlapping task ranges.
- **Cross-Session Deduplication**: Check `git log` for completed tasks before starting new work.
- **Plan Archival**: Archive completed plans to `.sisyphus/archive/` with timestamp.
- **Consolidation First**: Merge small plans into larger scoped plans rather than proliferating.

## Instructions

### Plan Consolidation Rules

1. **Check Existing Plans**: Before creating a new plan, list all plans in `.sisyphus/plans/`:
   ```bash
   ls -1 .sisyphus/plans/*.md | head -20
   ```

2. **Identify Overlapping Scope**: Read the scope section of existing plans to detect overlap:
   ```bash
   grep -h "^## Scope" .sisyphus/plans/*.md -A 5
   ```

3. **Merge Instead of Proliferate**: If a new plan overlaps with an existing plan:
   - Add tasks to the existing plan instead of creating a new one
   - Update the existing plan's scope section to reflect the expanded scope
   - Document the merge in the plan's changelog

### Overlap Detection Checklist

Before creating a new plan, verify:

- [ ] No existing plan covers the same project(s)
- [ ] No existing plan has overlapping task ranges (e.g., T1-T10 vs T5-T15)
- [ ] No existing plan targets the same architectural layer
- [ ] No existing plan addresses the same quality gate or validation scope
- [ ] Scope is genuinely new or a natural extension of an existing plan

### Cross-Session Deduplication Protocol

1. **Check Git Log for Completed Tasks**:
   ```bash
   git log --oneline --all | grep -i "docs(skills)|fix(import)|refactor(architecture)" | head -20
   ```

2. **Verify Task Completion Status**:
   ```bash
   grep -r "status.*completed" .sisyphus/plans/ .sisyphus/notepads/
   ```

3. **If Task Already Done**:
   - Do NOT recreate the task in a new plan
   - Reference the completed task in the new plan's scope
   - Link to the commit that completed the work

### Plan Archival Protocol

1. **Archive Completed Plans**:
   ```bash
   mkdir -p .sisyphus/archive
   mv .sisyphus/plans/completed-plan-name.md .sisyphus/archive/completed-plan-name-YYYYMMDD.md
   ```

2. **Update Archive Index**:
   ```bash
   echo "- completed-plan-name (YYYYMMDD) — [link to commit]" >> .sisyphus/archive/INDEX.md
   ```

3. **Preserve Learnings**:
   - Copy notepad files to archive before deleting plan
   - Keep learnings.md, issues.md, decisions.md for future reference

## Workflow

1. **Before Creating a Plan**:
   - Run overlap detection checklist
   - Check git log for related completed work
   - Review existing plan scopes

2. **When Consolidating Plans**:
   - Merge task lists into the larger plan
   - Update scope section
   - Document merge in changelog

3. **When Archiving Plans**:
   - Verify all tasks are completed
   - Copy notepads to archive
   - Move plan file with timestamp
   - Update archive index

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

- `make validate VALIDATE_SCOPE=workspace` — workspace validation ensures plan consistency

Pattern checks:

- `ls -1 .sisyphus/plans/*.md | wc -l` — count of active plans (should be < 5 for workspace)
- `grep -h "^## Scope" .sisyphus/plans/*.md | sort | uniq -d` — detect overlapping scopes
- `test -d .sisyphus/archive && ls -1 .sisyphus/archive/*.md | wc -l` — count of archived plans
- `grep -c "status.*completed" .sisyphus/plans/*.md` — verify task completion tracking
