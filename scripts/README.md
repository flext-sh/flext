# FLEXT Git History Cleanup Scripts

Quick reference for git history reorganization tools.

## Quick Start

```bash
# 1. Set API key
export ANTHROPIC_API_KEY="your-key-here"

# 2. Test on one submodule first
./git_cleanup_orchestrator.sh --test-run

# 3. Review results
cd flext-grpc && git log --oneline

# 4. If satisfied, run full cleanup
cd ..
./git_cleanup_orchestrator.sh --full-cleanup

# 5. Validate and deploy
git push --force origin main
git submodule foreach 'git push --force origin main'
```

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `git_cleanup_orchestrator.sh` | **Main entry point** | `./git_cleanup_orchestrator.sh --test-run` |
| `git_history_rewriter.py` | AI commit message rewriting | `python git_history_rewriter.py --repo .` |
| `git_cleanup_backup.sh` | Backup repositories | `./git_cleanup_backup.sh --all-submodules` |

## Documentation

See [../docs/GIT_HISTORY_CLEANUP_GUIDE.md](../docs/GIT_HISTORY_CLEANUP_GUIDE.md) for comprehensive guide.

## Current State

- **Total commits**: 357 (main repo)
- **Cruft identified**: 19 commits
- **Version-only**: 105 commits
- **Authors**: 5 unique
- **Submodules**: 32

## Safety

All operations create backups in `~/flext-history-backup-*/` with rollback scripts.

**Rollback**:
```bash
cd ~/flext-history-backup-YYYYMMDD-HHMMSS/
./ROLLBACK.sh
```

## Requirements

```bash
pip install git-filter-repo anthropic
export ANTHROPIC_API_KEY="your-key"
```
