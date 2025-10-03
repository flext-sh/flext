# FLEXT Git History Cleanup Scripts

Quick reference for git history reorganization tools.

## Quick Start (3-Step Safe Process)

```bash
# Step 1: SAFE ANALYSIS (doesn't modify anything)
./git_cleanup_orchestrator.sh --test-run

# Step 2: RECOMMENDED - Test in temporary clone
./git_cleanup_test_safe.sh

# Step 3: ONLY IF SATISFIED - Apply to real repository
./git_cleanup_orchestrator.sh --full-cleanup
```

## Scripts

| Script | Purpose | Safe? |
|--------|---------|-------|
| `git_cleanup_orchestrator.sh --test-run` | **Analysis only** - Preview changes | ✅ SAFE |
| `git_cleanup_test_safe.sh` | **Test in temp clone** | ✅ SAFE |
| `git_cleanup_orchestrator.sh --full-cleanup` | **Apply changes** | ⚠️ DESTRUCTIVE |
| `git_history_rewriter.py` | Heuristic commit rewriting | ✅ SAFE (analysis only) |
| `git_cleanup_backup.sh` | Create backups | ✅ SAFE |
| `git_cleanup_validator.sh` | Validate after cleanup | ✅ SAFE |

## Detailed Workflow

### 1. Analysis Mode (Safe)

```bash
cd /home/marlonsc/flext
./scripts/git_cleanup_orchestrator.sh --test-run
```

**What it does:**
- Analyzes first 100 commits
- Generates improved messages using heuristics
- Creates mapping file for review
- Shows preview

**What it doesn't do:**
- ❌ Modify repository
- ❌ Change commit SHAs
- ❌ Require force push

### 2. Safe Testing (Recommended)

```bash
./scripts/git_cleanup_test_safe.sh
```

**What it does:**
- Creates temporary clone in `/tmp/`
- Applies all changes to the clone
- Shows actual results
- Original repo untouched

**Review results:**
```bash
cd /tmp/flext-cleanup-test-*
git log --oneline | head -50
git log --format='%aN <%aE>' | sort -u
```

### 3. Production Cleanup (Dangerous)

**⚠️ ONLY proceed if satisfied with test results!**

```bash
./scripts/git_cleanup_orchestrator.sh --full-cleanup
```

**This will:**
- Create comprehensive backups
- Process all submodules
- Modify git history
- Require force push

## Documentation

- **Complete Guide**: [../docs/GIT_HISTORY_CLEANUP_GUIDE.md](../docs/GIT_HISTORY_CLEANUP_GUIDE.md)
- **Cursor AI Integration**: [CURSOR_AI_INTEGRATION.md](CURSOR_AI_INTEGRATION.md)

## Current State

- **Total commits**: 357 (main repo)
- **Cruft identified**: 19 commits
- **Version-only**: 105 commits
- **Authors**: 5 unique
- **Submodules**: 32

## Heuristic Rules

Automatic improvements (no API key needed):

| Pattern | Becomes |
|---------|---------|
| `0.9.0` | `chore(release): bump version to 0.9.0` |
| `WIP async` | `feat(core): work in progress on async` |
| `fix typo` | `docs: correct typos in documentation` |
| `fix lint` | `style: apply code formatting and linting` |

## Safety Features

### Automatic Backups

All destructive operations create backups in `~/flext-history-backup-*/` with rollback scripts.

**Rollback:**
```bash
cd ~/flext-history-backup-YYYYMMDD-HHMMSS/
./ROLLBACK.sh
```

### Multiple Safety Layers

1. **Test mode**: Analysis only, no changes
2. **Safe test**: Temporary clone for validation
3. **Backups**: Automatic before any changes
4. **Rollback**: One-command restoration

## Requirements

```bash
# Only git-filter-repo needed - no API keys!
pip install git-filter-repo
```

## Troubleshooting

### "Repository was modified during test"

The old `--test-run` was destructive. Use the new safe workflow:
1. Run `--test-run` (now safe, analysis only)
2. Use `git_cleanup_test_safe.sh` for actual testing
3. Original repo stays untouched

### Want to improve specific messages

1. Run analysis: `./git_cleanup_orchestrator.sh --test-run`
2. Edit mapping: `cursor .git/history-cleanup/commit-msg-mapping.txt`
3. Ask Cursor AI to improve specific lines
4. Test in temp clone: `./git_cleanup_test_safe.sh`

---

**Remember**: Always test in temporary clone before applying to production!
