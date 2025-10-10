# Documentation Maintenance System - Quick Start

> **Comprehensive automated documentation quality assurance for FLEXT monorepo**

## 🚀 Quick Start

### Run Your First Audit

```bash
# Preview what needs fixing (safe, no changes)
python scripts/docs_maintenance_audit.py --root . --output audit.md

# View the report
cat audit.md
```

### Common Tasks

```bash
# Fix broken links automatically
python scripts/docs_link_fixer.py --root . --apply

# Generate table of contents for all docs
python scripts/docs_toc_generator.py --root . --apply

# Run complete maintenance workflow
./scripts/docs_sync_automation.sh --apply
```

## 📁 Files Created

### Core Tools

| File | Purpose |
|------|---------|
| `scripts/docs_maintenance_audit.py` | Main audit engine - analyzes all 659 markdown files |
| `scripts/docs_link_fixer.py` | Automatically fixes broken links and references |
| `scripts/docs_toc_generator.py` | Generates/updates table of contents |
| `scripts/docs_sync_automation.sh` | Complete maintenance workflow automation |

### Configuration

| File | Purpose |
|------|---------|
| `.markdownlint.json` | Markdown style rules and linting configuration |
| `.github/workflows/docs_maintenance.yml` | GitHub Actions CI/CD workflow |
| `Makefile.docs` | Make commands for easy access to tools |

### Documentation

| File | Purpose |
|------|---------|
| `docs/documentation-maintenance-guide.md` | Complete usage guide (you are here!) |
| `docs/DOCS_MAINTENANCE_README.md` | This quick start guide |

## 🎯 What Gets Checked

### Content Quality ✅

- **Freshness**: Documents >90 days old flagged for review
- **Completeness**: Minimum word count, structure requirements
- **TODO Markers**: Track unfinished documentation
- **Heading Structure**: Proper hierarchy and organization

### Link Validation 🔗

- **Internal Links**: Verify all `../` and `./` references
- **External Links**: Check HTTP status (optional, slower)
- **Images**: Validate image paths and existence
- **Anchors**: Verify heading anchors work

### Style & Formatting 🎨

- **Line Length**: Configurable max characters per line
- **Heading Hierarchy**: Sequential levels (h1→h2→h3, not h1→h3)
- **Code Blocks**: Language specification required
- **List Formatting**: Consistent markers and indentation

### Accessibility ♿

- **Alt Text**: All images must have descriptive alt text
- **Link Text**: Descriptive text (not "click here")
- **Structure**: Proper heading hierarchy for screen readers

## 🛠️ Using Make Commands

Add to your main `Makefile`:

```makefile
include Makefile.docs
```

Then use convenient shortcuts:

```bash
# Show all available commands
make docs-help

# Quick audit
make docs-audit

# Fix everything
make docs-sync-apply

# Run CI checks locally
make docs-ci-check
```

## 📊 Understanding Reports

### Severity Levels

```
🔴 CRITICAL  - Broken links, missing images, security issues
🟠 HIGH      - Accessibility violations, major structure issues
🟡 MEDIUM    - Stale content (>90 days), minor link problems
🔵 LOW       - Style violations, formatting inconsistencies
ℹ️  INFO      - Suggestions, optimization opportunities
```

### Sample Report Structure

```markdown
# FLEXT Documentation Audit Report

**Total Files Analyzed:** 659
**Total Issues Found:** 127

## Issues by Severity
- Critical: 3    ← Fix these immediately!
- High: 12       ← Address soon
- Medium: 45     ← Schedule for review
- Low: 67        ← Nice to have

## Issues by Category
- Broken Link: 8           ← Run link fixer
- Missing Image: 2         ← Add missing assets
- Content Freshness: 23    ← Review/update old docs
- Accessibility: 34        ← Add alt text
- Style Formatting: 60     ← Run auto-formatter
```

## 🔄 Automated Workflows

### Weekly Audit (GitHub Actions)

Runs every Sunday at midnight UTC:

1. Audits all 659 markdown files
2. Generates reports (MD, JSON, HTML)
3. Creates/updates GitHub issue with findings
4. Uploads reports as workflow artifacts

**View:** `.github/workflows/docs_maintenance.yml`

### Pull Request Validation

Runs on every PR touching markdown files:

1. Quick audit of changed files
2. Validates internal links
3. Checks style compliance
4. Comments on PR with summary

## 🎬 Complete Workflow Example

### Scenario: Weekly Maintenance

```bash
# 1. Preview all changes (safe, no writes)
./scripts/docs_sync_automation.sh

# 2. Review what would change
# Read the output carefully

# 3. Apply fixes
./scripts/docs_sync_automation.sh --apply

# 4. Review changes in git
git diff

# 5. Commit if satisfied
git add -A
git commit -m "docs: weekly maintenance - fix links, update TOCs, improve accessibility"
git push
```

### Scenario: Adding New Documentation

```bash
# 1. Create your new doc
vim docs/new-feature-guide.md

# 2. Write content with proper headings

# 3. Generate TOC
python scripts/docs_toc_generator.py --root docs --apply

# 4. Validate before commit
python scripts/docs_maintenance_audit.py --root docs --output /tmp/audit.md

# 5. Check for issues
grep "severity.*critical\|severity.*high" /tmp/audit.md

# 6. Fix any issues, then commit
git add docs/new-feature-guide.md
git commit -m "docs: add new feature guide with TOC"
```

## 🚨 Troubleshooting

### Issue: "Too many broken links after refactoring"

```bash
# Auto-fix with similarity matching
python scripts/docs_link_fixer.py --root . --apply

# Review remaining issues
python scripts/docs_maintenance_audit.py --root . --output audit.md
grep "broken_link" audit.md
```

### Issue: "External link checking is too slow"

```bash
# Disable external checking for faster runs
python scripts/docs_maintenance_audit.py --root . --output audit.md
# (omit --check-external-links flag)

# Or run only internal validation
./scripts/docs_sync_automation.sh --apply
# (no --external-links flag)
```

### Issue: "CI workflow failing"

1. Check GitHub Actions logs
2. Verify Python 3.13+ installed
3. Ensure dependencies available:
   ```bash
   pip install requests beautifulsoup4 markdown
   ```

## 📈 Metrics & Monitoring

### Current Documentation Health

```bash
# Get quick statistics
make docs-stats

# Output:
# Markdown files:    659
# Docs directories:  36
# Total lines:       ~23,456
# Total words:       ~458,234
```

### Track Improvement Over Time

```bash
# Run audit weekly and compare
python scripts/docs_maintenance_audit.py --root . --output audit_$(date +%Y%m%d).md

# Compare with previous week
diff audit_20251002.md audit_20251009.md
```

## 🎓 Best Practices

### Do ✅

- Run audit before committing doc changes
- Fix critical/high issues immediately
- Review medium issues monthly
- Update stale docs (>90 days) quarterly
- Add alt text to all images
- Use descriptive link text
- Keep TOCs updated

### Don't ❌

- Ignore broken links
- Skip external link validation forever
- Commit without running validation
- Use absolute paths in links
- Forget alt text on images
- Use "click here" as link text

## 🔗 Resources

- **Full Guide**: `docs/documentation-maintenance-guide.md`
- **CI Config**: `.github/workflows/docs_maintenance.yml`
- **Style Rules**: `.markdownlint.json`
- **Markdown Guide**: https://www.markdownguide.org/
- **WCAG Guidelines**: https://www.w3.org/WAI/WCAG21/quickref/

## 📞 Getting Help

- **Tool Issues**: Check script output and error messages
- **Workflow Questions**: Review `docs/documentation-maintenance-guide.md`
- **CI/CD Issues**: Check GitHub Actions logs
- **General Help**: Create issue with `documentation` label

---

## Next Steps

1. **Run your first audit**: `python scripts/docs_maintenance_audit.py --root . --output audit.md`
2. **Review the report**: `cat audit.md`
3. **Fix critical issues**: `python scripts/docs_link_fixer.py --root . --apply`
4. **Read full guide**: `docs/documentation-maintenance-guide.md`
5. **Set up Make commands**: Add `include Makefile.docs` to main Makefile

---

**Version:** 1.0.0 | **Last Updated:** 2025-10-09 | **Status:** Production Ready
