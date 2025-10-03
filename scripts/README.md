# FLEXT Git History Cleanup Scripts

Quick reference for git history reorganization tools.

## Quick Start (Safe 3-Step Process)

```bash
# Step 1: TEST FUNCTIONS (doesn't modify anything)
python3 scripts/git_ultimate_cleanup.py --test

# Step 2: DRY RUN (simulates all operations)
python3 scripts/git_ultimate_cleanup.py --dry-run

# Step 3: EXECUTE (with automatic backup)
python3 scripts/git_ultimate_cleanup.py --all --push-all
```

## Scripts

**THE ONLY SCRIPT YOU NEED**: `git_ultimate_cleanup.py`

| Command                                              | Purpose                                                        | Safe?          |
| ---------------------------------------------------- | -------------------------------------------------------------- | -------------- |
| `python3 scripts/git_ultimate_cleanup.py --test`     | **Test all functions** - Validates without changes             | ✅ SAFE        |
| `python3 scripts/git_ultimate_cleanup.py --dry-run`  | **Simulate cleanup** - Shows what would be done                | ✅ SAFE        |
| `python3 scripts/git_ultimate_cleanup.py`            | **Clean main repo** - With external backup                     | ⚠️ DESTRUCTIVE |
| `python3 scripts/git_ultimate_cleanup.py --all`      | **Clean all** - Main + 32 submodules                           | ⚠️ DESTRUCTIVE |
| `python3 scripts/git_ultimate_cleanup.py --push`     | **Clean + push** - Main repo to GitHub                         | ⚠️ DESTRUCTIVE |
| `python3 scripts/git_ultimate_cleanup.py --push-all` | **Clean + push all** - Main + submodules to GitHub             | ⚠️ DESTRUCTIVE |
| `python3 scripts/git_ultimate_cleanup.py --backup-only` | **Backup only** - Creates external backup without cleanup   | ✅ SAFE        |
| `python3 scripts/git_ultimate_cleanup.py --restore-remotes` | **Restore remotes** - Re-add after filter-repo          | ✅ SAFE        |

## Detailed Workflow

### 1. Test Mode (Safe)

```bash
cd /home/marlonsc/flext
python3 scripts/git_ultimate_cleanup.py --test
```

**What it does:**

- ✅ Validates repository structure
- ✅ Tests git directory detection
- ✅ Validates cruft patterns (49 patterns)
- ✅ Validates AI removal patterns (14 patterns)
- ✅ Detects submodules (32 found)
- ✅ Checks remote configuration
- ✅ Verifies backup directory access
- ✅ Tests required commands (git, git-filter-repo, tar)

**What it doesn't do:**

- ❌ Modify repository
- ❌ Change commit SHAs
- ❌ Create backups

### 2. Dry Run (Safe Testing)

```bash
python3 scripts/git_ultimate_cleanup.py --dry-run
```

**What it does:**

- Shows exactly what would be removed
- Simulates all operations
- No actual changes made
- Original repo completely untouched

**Review simulation:**

The script will show:
- Number of cruft patterns to remove
- AI references that would be cleaned
- Author normalization preview

### 3. Production Cleanup (Dangerous)

**⚠️ ONLY proceed if satisfied with test results!**

```bash
python3 scripts/git_ultimate_cleanup.py --all --push-all
```

**This will:**

1. **Create comprehensive backup** (automatic, external to git)
   - tar.gz archive in `~/flext-ultimate-backup-YYYYMMDD-HHMMSS/`
   - Git mirror clone
   - Commit history export
   - Reflog export
   - Branch and tag info
   - Safety tag in repository
   - Recovery script

2. **Clean main repository**
   - Remove 49 cruft patterns from entire history
   - Clean AI references from all commits
   - Normalize author to Marlon Costa <marlonsc@gmail.com>

3. **Clean all 32 submodules**
   - Same cleanup process for each

4. **Restore remotes**
   - Automatically restore GitHub remotes after filter-repo

5. **Push to GitHub**
   - Force push main repository
   - Force push all submodules
   - Push all branches and tags

**Cruft patterns removed (49 total):**

- Build artifacts: `*.pyc`, `__pycache__/`, `dist/`, `build/`, `*.egg-info/`
- Cache directories: `.ruff_cache/`, `.mypy_cache/`, `.pytest_cache/`, `.serena/`
- Coverage reports: `.coverage`, `htmlcov/`, `.tox/`
- Log files: `*.log`, `.meltano/logs/`
- Backup files: `*.backup`, `*.bak`, `*.orig`, `*~`, `.*.swp`
- OS-specific: `.DS_Store`, `Thumbs.db`
- AI/IDE config: `CLAUDE*.md`, `.cursor/`, `.vscode/`, `.idea/`
- AI reports: `*_report.md`, `*_analysis.md`, `*_summary.md`
- Large data: `*.db`, `*.sqlite`, `sync_control.db`
- Archive files: `*.tar`, `*.tar.gz`, `*.zip`

**Recovery (if needed):**

```bash
cd ~/flext-ultimate-backup-YYYYMMDD-HHMMSS/flext/
./RECOVER.sh
```

## Documentation

- **Complete Guide**: [../docs/GIT_HISTORY_CLEANUP_GUIDE.md](../docs/GIT_HISTORY_CLEANUP_GUIDE.md)
- **Cursor AI Integration**: [CURSOR_AI_INTEGRATION.md](CURSOR_AI_INTEGRATION.md)

## Current State

- **Total commits**: 357 (main repo)
- **Cruft patterns**: 49 (build artifacts, cache, logs, AI config, data files)
- **AI patterns**: 14 (removes all Claude/Codex/Cursor references)
- **Authors**: Normalized to Marlon Costa <marlonsc@gmail.com>
- **Submodules**: 32
- **Script**: ONE unified script (git_ultimate_cleanup.py)

## Safety Features

### Multiple Safety Layers

1. **Test mode** (`--test`): Validates all functions without changes
2. **Dry run** (`--dry-run`): Simulates all operations
3. **Automatic backups**: External backup created before any changes
4. **Recovery script**: One-command restoration included
5. **Validation**: Comprehensive pre-flight checks
6. **Force push protection**: Requires explicit confirmation

### Automatic Backups

Every cleanup creates comprehensive backup in `~/flext-ultimate-backup-YYYYMMDD-HHMMSS/`:

- tar.gz archive (survives git history rewrite)
- Git mirror clone
- Commit history export
- Reflog export
- Branch and tag info
- Safety tag in repository
- RECOVER.sh script for easy restoration

**Rollback:**

```bash
cd ~/flext-ultimate-backup-YYYYMMDD-HHMMSS/flext/
./RECOVER.sh
```

## Requirements

```bash
# Only git-filter-repo needed - no API keys!
pip install git-filter-repo
```

## Troubleshooting

### Test before running

**Always run test mode first:**

```bash
# Validate functions
python3 scripts/git_ultimate_cleanup.py --test

# Simulate operations
python3 scripts/git_ultimate_cleanup.py --dry-run
```

### Check repository size

```bash
# Before cleanup
git count-objects -vH

# After cleanup (shows reduction)
git count-objects -vH
```

### Verify changes

```bash
# Check authors are normalized
git log --format='%aN <%aE>' | sort -u

# Check AI references removed
git log --all --grep="Claude\|Codex\|Cursor" --oneline

# Check recent commits
git log --oneline --format='%h %an: %s' | head -20
```

---

**Remember**: Always test in temporary clone before applying to production!
