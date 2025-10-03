# FLEXT Git History Cleanup Guide

**Version**: 1.0.0
**Last Updated**: 2025-10-03
**Status**: Production Ready

## Overview

Complete workflow for reorganizing git history across the FLEXT workspace (main repository + 32 submodules):

- **Remove cruft**: WIP commits, meaningless merges, version-only commits
- **AI-rewrite messages**: Use Claude API to generate conventional commit messages
- **Normalize authors**: Consolidate author identities via `.mailmap`
- **Scale**: Handle 357 commits in main repo + all submodules

## Analysis Summary

### Current State

```
Total commits (main repo): 357
Cruft commits identified: 19 (WIP, tmp, typo fixes)
Version-only commits: 105 (just "0.9.0" messages)
Merge commits: 2
Authors to normalize: 5 unique identities
Submodules to process: 32
```

### Commit Message Patterns

**Problematic**:

- 83 commits with just "0.9.0" (no context)
- 19 commits with "WIP", "tmp", "typo", "fix lint"
- Inconsistent formatting (no conventional commits)

**Good examples** (will preserve):

- `feat: Complete Phase 1 & 2 - Foundation and model verification`
- `style(flext-ldif): Apply isort formatting after async removal`
- `chore(submodules): update pointers after docs cleanup`

## Prerequisites

### Required Tools

```bash
# 1. git-filter-repo
pip install git-filter-repo
# or on Arch: sudo pacman -S git-filter-repo

# 2. Python 3.13+
python3 --version  # Should be 3.13+

# 3. Anthropic Python SDK (for AI rewriting)
pip install anthropic
```

### Environment Setup

```bash
# Required for AI commit message rewriting
export ANTHROPIC_API_KEY="your-api-key-here"

# Add to ~/.bashrc or ~/.zshrc for persistence
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
```

## Safety Architecture

### Backup Strategy

All operations create comprehensive backups:

1. **Repository clones**: Full mirror clones with all history
2. **Safety tags**: `pre-cleanup-YYYYMMDD-HHMMSS` tags
3. **Metadata exports**: Commit history, branches, tags, HEAD
4. **Rollback script**: Automated restoration if needed

### Rollback Procedure

```bash
# Backups stored in: ~/flext-history-backup-YYYYMMDD-HHMMSS/

# To rollback:
cd ~/flext-history-backup-*/
./ROLLBACK.sh

# This will restore ALL repositories to pre-cleanup state
```

## Workflow

### Phase 1: Test Run (Recommended First Step)

Test the entire workflow on a single small submodule:

```bash
cd /home/marlonsc/flext

# Run test on flext-grpc (small submodule)
./scripts/git_cleanup_orchestrator.sh --test-run
```

**What happens**:

1. Creates backup of test submodule
2. Analyzes commit history
3. Generates AI-rewritten commit messages
4. Applies git-filter-repo with `.mailmap` and message mapping
5. Validates results

**Review results**:

```bash
cd flext-grpc

# Check new commit messages
git log --oneline

# Check author normalization
git log --format='%aN <%aE>' | sort -u

# Compare with original
git log pre-cleanup-YYYYMMDD-HHMMSS..HEAD --oneline
```

**If satisfied**: Proceed to Phase 2
**If not satisfied**: Rollback and adjust

### Phase 2: Full Cleanup

Process all 32 submodules + main repository:

```bash
cd /home/marlonsc/flext

# Full workspace cleanup
./scripts/git_cleanup_orchestrator.sh --full-cleanup
```

**Execution order**:

1. **Backup**: Creates comprehensive backup of all repos
2. **Submodules**: Processes each submodule independently (bottom-up)
3. **Main repo**: Updates submodule references, then cleans main repo
4. **Validation**: Checks commit counts, authors, working directory status

**Duration estimate**: 30-60 minutes (depends on API rate limits)

### Phase 3: Validation

After cleanup completes, validate each repository:

```bash
# Main repository
cd /home/marlonsc/flext
git log --oneline | head -20
git log --format='%aN <%aE>' | sort -u
make test  # Run test suite

# Sample submodule
cd flext-core
git log --oneline | head -20
git log --format='%aN <%aE>' | sort -u
make test
```

**Validation checklist**:

- [ ] Commit messages follow conventional commits
- [ ] Authors normalized to canonical identities
- [ ] No cruft commits (WIP, tmp, etc.)
- [ ] All tests pass
- [ ] Working directory clean
- [ ] Submodule references correct

### Phase 4: Deployment

**⚠️ CRITICAL: Coordinate with team before this step!**

This requires force-pushing to remote repositories. All team members must re-clone.

```bash
# 1. Force push main repository
cd /home/marlonsc/flext
git push --force origin main

# 2. Force push each submodule
git submodule foreach 'git push --force origin main'

# 3. Notify team
# Send email/message with re-clone instructions
```

**Team re-clone instructions**:

```bash
# Delete old clones
rm -rf /path/to/old/flext

# Fresh clone
git clone --recursive https://github.com/your-org/flext.git
cd flext
git submodule update --init --recursive
```

## Scripts Reference

### 1. `git_history_rewriter.py`

AI-powered commit message rewriter using Claude API.

**Usage**:

```bash
# Single repository
python scripts/git_history_rewriter.py \
    --repo /path/to/repo \
    --api-key $ANTHROPIC_API_KEY

# All submodules
python scripts/git_history_rewriter.py \
    --batch-submodules \
    --api-key $ANTHROPIC_API_KEY
```

**Output**:

- `.git/history-cleanup/commit-msg-mapping.txt` - Mapping for git-filter-repo
- `.git/history-cleanup/cleanup-summary.json` - Analysis summary

**Features**:

- Converts to conventional commits: `feat(scope): description`
- Preserves important context (issue numbers, breaking changes)
- Rate-limited to respect Claude API limits (~50 req/min)
- Skips already-conventional messages

### 2. `git_cleanup_backup.sh`

Creates comprehensive backups before destructive operations.

**Usage**:

```bash
# Backup current repository
./scripts/git_cleanup_backup.sh

# Backup all submodules
./scripts/git_cleanup_backup.sh --all-submodules
```

**Backup includes**:

- Mirror clone of repository
- Commit history export
- Branch and tag information
- HEAD reference
- Metadata JSON
- Rollback script

### 3. `git_cleanup_orchestrator.sh`

Main orchestration script - coordinates the full workflow.

**Usage**:

```bash
# Test run (single submodule)
./scripts/git_cleanup_orchestrator.sh --test-run

# Full cleanup (all repos)
./scripts/git_cleanup_orchestrator.sh --full-cleanup
```

**Safety features**:

- Preflight checks (tools, API key)
- Confirmation prompts
- Automatic backups
- Validation after each repo
- Detailed progress reporting

### 4. `.mailmap`

Author normalization mapping (already created).

**Contents**:

```
# Canonical Name <canonical@email.com> <old@email.com>
marlon-costa-dc <128386606+marlon-costa-dc@users.noreply.github.com>
Claude Code <noreply@anthropic.com> Claude <claude@anthropic.com>
Cursor Agent <cursoragent@cursor.com>
```

**To add more mappings**:

```bash
# Find all author variations
git log --all --format='%aN <%aE>' | sort -u

# Add to .mailmap
echo "Canonical Name <email@example.com> Old Name <old@example.com>" >> .mailmap
```

## Advanced Usage

### Manual git-filter-repo

If you need more control:

```bash
cd /path/to/repo

# Backup first!
git tag pre-manual-cleanup

# Apply transformations
git filter-repo \
    --mailmap /home/marlonsc/flext/.mailmap \
    --replace-message .git/history-cleanup/commit-msg-mapping.txt \
    --force

# Validation
git log --oneline
```

### Custom Commit Filtering

Add Python callbacks to `git-filter-repo`:

```python
# remove_cruft.py
def callback(commit, metadata):
    # Remove WIP commits
    if b'WIP' in commit.message or b'wip' in commit.message:
        commit.skip()
```

```bash
git filter-repo \
    --commit-callback 'remove_cruft.py' \
    --force
```

### Submodule-specific Cleanup

Process a single submodule manually:

```bash
cd flext-core

# Analyze
python ../scripts/git_history_rewriter.py --repo .

# Backup
git tag pre-cleanup-manual

# Apply
git filter-repo \
    --mailmap ../.mailmap \
    --replace-message .git/history-cleanup/commit-msg-mapping.txt \
    --force
```

## Troubleshooting

### "externally-managed-environment" error

```bash
# Use pipx instead
pipx install git-filter-repo

# Or create venv
python -m venv ~/venv-git-cleanup
source ~/venv-git-cleanup/bin/activate
pip install git-filter-repo anthropic
```

### "ANTHROPIC_API_KEY not set"

```bash
# Get API key from: https://console.anthropic.com/
export ANTHROPIC_API_KEY="sk-ant-..."

# Or skip AI rewriting (less optimal)
# The scripts will prompt you to continue without AI
```

### Rate limit errors

The script includes automatic rate limiting, but if you hit limits:

```bash
# Process repos in smaller batches
for submodule in flext-core flext-cli flext-api; do
    python scripts/git_history_rewriter.py --repo "$submodule"
    sleep 60  # Wait 1 minute between batches
done
```

### "Submodule reference mismatch"

After cleanup, submodule SHAs change. Update main repo:

```bash
cd /home/marlonsc/flext
git submodule update --remote
git add .gitmodules $(git submodule status | awk '{print $2}')
git commit -m "chore: update submodule references post-cleanup"
```

### Tests fail after cleanup

History changes shouldn't affect tests, but if they do:

```bash
# Check if it's a submodule reference issue
git submodule status

# Re-initialize
git submodule update --init --recursive

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Re-run tests
make test
```

## Best Practices

### Before Starting

1. **Communicate with team**: Schedule maintenance window
2. **Freeze development**: No new commits during cleanup
3. **Export API key**: Ensure ANTHROPIC_API_KEY is set
4. **Disk space**: Ensure ~10GB free (for backups)

### During Execution

1. **Test first**: Always run `--test-run` before `--full-cleanup`
2. **Monitor output**: Watch for errors or warnings
3. **Keep backups**: Don't delete backup directories until validated
4. **Document issues**: Note any problems for troubleshooting

### After Completion

1. **Validate thoroughly**: Check multiple repos, run full test suite
2. **Keep backups**: Retain for at least 1 week post-deployment
3. **Document**: Update this guide with lessons learned
4. **Monitor**: Watch for issues in CI/CD after force push

## Expected Results

### Commit Messages

**Before**:

```
0.9.0
0.9.0
fix typo
WIP async implementation
```

**After**:

```
chore(release): bump version to 0.9.0
docs: correct typos in documentation
feat(core): implement async execution patterns
```

### Author Normalization

**Before**:

```
Claude <claude@anthropic.com>
Claude Code <noreply@anthropic.com>
Cursor Agent <cursoragent@cursor.com>
marlon-costa-dc <128386606+marlon-costa-dc@users.noreply.github.com>
Test User <test@example.com>
```

**After**:

```
Claude Code <noreply@anthropic.com>
Cursor Agent <cursoragent@cursor.com>
marlon-costa-dc <128386606+marlon-costa-dc@users.noreply.github.com>
```

### Repository Size

Minor reduction (removed redundant merge commits), but main benefit is **history quality**, not size.

## Support

For issues or questions:

1. Check [Troubleshooting](#troubleshooting) section
2. Review script output for error messages
3. Check backup integrity: `cd ~/flext-history-backup-*/`
4. If needed, rollback and investigate

## License

Internal FLEXT workspace tooling. See main LICENSE file.

---

**⚠️ REMEMBER**: This is a destructive operation. Always test first, backup everything, and coordinate with your team!
