# FLEXT Documentation Maintenance & Quality Assurance Guide

> **Important**
>
> The bespoke maintenance scripts under `scripts/docs_*` have been removed.
> Refer to the unified `flext-quality` CLI (`python -m
> flext_quality.docs_maintenance.cli` / `flext-docs`) for all automation tasks.
> Content below that references the legacy helpers is retained for archival
> context only.

**Version:** 1.0.0
**Last Updated:** 2025-10-09
**Status:** Production Ready

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Automated Tools](#automated-tools)
- [Quality Gates](#quality-gates)
- [CI/CD Integration](#cicd-integration)
- [Maintenance Workflows](#maintenance-workflows)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Overview

The FLEXT Documentation Maintenance System provides comprehensive automated quality assurance, validation,
     and maintenance for the monorepo's **659 markdown files** across **36 documentation directories**.

### Key Features

- **Automated Quality Audits**: Weekly scheduled audits of all documentation
- **Link Validation**: Internal and external link checking with automatic fixes
- **Style Consistency**: Markdown formatting and accessibility compliance
- **Content Freshness**: Tracking and alerting for stale documentation
- **CI/CD Integration**: GitHub Actions workflows for continuous validation
- **Automated Reporting**: Detailed audit reports with severity classifications

### Documentation Statistics

``` yaml
Total Markdown Files: 659
Documentation Directories: 36
Projects: 33
```

---

## System Architecture

### Components

```
┌─────────────────────────────────────────────────────┐
│          Documentation Maintenance System           │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────┐  ┌──────────────────┐        │
│  │  Audit Engine   │  │  Link Validator  │        │
│  │  - Metrics      │  │  - Internal      │        │
│  │  - Quality      │  │  - External      │        │
│  │  - Freshness    │  │  - Images        │        │
│  └─────────────────┘  └──────────────────┘        │
│                                                     │
│  ┌─────────────────┐  ┌──────────────────┐        │
│  │ Style Checker   │  │  Auto Fixer      │        │
│  │  - Markdown     │  │  - Links         │        │
│  │  - Formatting   │  │  - Alt Text      │        │
│  │  - Accessibility│  │  - TOCs          │        │
│  └─────────────────┘  └──────────────────┘        │
│                                                     │
│  ┌─────────────────────────────────────────┐      │
│  │         Reporting & Dashboard           │      │
│  │  - Markdown Reports                     │      │
│  │  - JSON Metrics                         │      │
│  │  - HTML Dashboard                       │      │
│  │  - GitHub Issues                        │      │
│  └─────────────────────────────────────────┘      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Data Flow

1. **Discovery**: Find all markdown files in workspace
2. **Analysis**: Extract metrics and validate content
3. **Validation**: Check links, images, style, accessibility
4. **Reporting**: Generate multi-format reports
5. **Automation**: Auto-fix common issues
6. **Integration**: Commit changes and create issues

---

## Automated Tools

### 1. Documentation Audit Tool

**Location:** `scripts/docs_maintenance_audit.py`

Comprehensive quality analysis and validation.

#### Usage

```bash
# Basic audit
python scripts/docs_maintenance_audit.py --root . --output audit.md

# Full audit with external link checking
python scripts/docs_maintenance_audit.py \
    --root . \
    --output audit.md \
    --format markdown \
    --check-external-links

# JSON output for metrics
python scripts/docs_maintenance_audit.py \
    --root . \
    --output audit.json \
    --format json

# HTML dashboard
python scripts/docs_maintenance_audit.py \
    --root . \
    --output audit.html \
    --format html
```

#### Validation Categories

- **Content Quality**
  - Document age and freshness
  - Word count and completeness
  - TODO/FIXME markers
  - Heading structure

- **Link Validation**
  - Internal broken links
  - External link health
  - Anchor references
  - Image paths

- **Style Compliance**
  - Line length limits
  - Heading hierarchy
  - Code block language tags
  - List formatting

- **Accessibility**
  - Alt text for images
  - Descriptive link text
  - Proper heading structure

#### Issue Severity Levels

- **Critical**: Broken links, missing images, security issues
- **High**: Accessibility violations, major structure issues
- **Medium**: Stale content (>90 days), minor link issues
- **Low**: Style violations, formatting inconsistencies
- **Info**: Suggestions, optimization opportunities

---

### 2. Link Fixer Tool

**Location:** `scripts/docs_link_fixer.py`

Automatically fixes common link issues.

#### Usage

```bash
# Dry-run (preview changes)
python scripts/docs_link_fixer.py --root .

# Apply fixes
python scripts/docs_link_fixer.py --root . --apply
```

#### Automatic Fixes

- Convert absolute paths to relative paths
- Fix broken internal links using similarity matching
- Add placeholder alt text to images
- Update outdated file references

---

### 3. Table of Contents Generator

**Location:** `scripts/docs_toc_generator.py`

Generates and updates TOCs based on heading structure.

#### Usage

```bash
# Dry-run
python scripts/docs_toc_generator.py --root .

# Apply to all files
python scripts/docs_toc_generator.py --root . --apply

# Custom configuration
python scripts/docs_toc_generator.py \
    --root . \
    --min-headings 5 \
    --max-level 4 \
    --apply
```

#### Configuration

- `--min-headings`: Minimum headings required (default: 3)
- `--max-level`: Maximum heading depth (default: 3)
- `--pattern`: File pattern to match (default: `**/*.md`)

---

### 4. Synchronization Automation

**Location:** `scripts/docs_sync_automation.sh`

Comprehensive maintenance workflow automation.

#### Usage

```bash
# Preview all changes
./scripts/docs_sync_automation.sh

# Apply all fixes
./scripts/docs_sync_automation.sh --apply

# Apply and commit
./scripts/docs_sync_automation.sh --apply --commit

# Full audit with external links
./scripts/docs_sync_automation.sh --apply --external-links
```

#### Workflow Steps

1. Run quality audit
2. Fix broken links
3. Generate/update TOCs
4. Validate all links
5. Format markdown (if prettier available)
6. Commit changes (if `--commit`)

---

## Quality Gates

### Pre-Commit Checks

Documentation changes should pass these checks before commit:

```bash
# 1. Lint markdown files
markdownlint **/*.md

# 2. Validate links
python scripts/docs_maintenance_audit.py --root . --output /tmp/audit.md
grep -q "broken_link" /tmp/audit.md && exit 1 || exit 0

# 3. Check style
python scripts/docs_maintenance_audit.py --root . --output /tmp/audit.md
grep -q "severity-critical" /tmp/audit.md && exit 1 || exit 0
```

### Pull Request Validation

Automated checks run on every PR touching markdown files:

- Markdown syntax validation
- Internal link checking
- Style consistency enforcement
- Accessibility compliance

See `.github/workflows/docs_maintenance.yml` for details.

---

## CI/CD Integration

### GitHub Actions Workflows

#### Weekly Audit

**Trigger:** Every Sunday at 00:00 UTC

**Actions:**

1. Run comprehensive audit
2. Generate reports (Markdown, JSON, HTML)
3. Create/update GitHub issue with findings
4. Upload reports as artifacts

**Configuration:** `.github/workflows/docs_maintenance.yml`

#### PR Validation

**Trigger:** Pull requests modifying `*.md` files

**Actions:**

1. Quick audit of changed files
2. Validate internal links
3. Check style compliance
4. Comment on PR with summary

#### Manual Execution

Workflows can be triggered manually via GitHub Actions UI with options for external link checking.

---

## Maintenance Workflows

### Weekly Maintenance Routine

```bash
# 1. Run automated sync (preview)
./scripts/docs_sync_automation.sh

# 2. Review proposed changes
git diff

# 3. Apply fixes
./scripts/docs_sync_automation.sh --apply

# 4. Review and commit
git add -A
git commit -m "docs: weekly maintenance - fix links and update TOCs"
git push
```

### Quarterly Deep Clean

```bash
# 1. Full audit with external link checking
python scripts/docs_maintenance_audit.py \
    --root . \
    --output quarterly_audit.md \
    --check-external-links

# 2. Review audit report
cat quarterly_audit.md

# 3. Address high-priority issues manually

# 4. Run automated fixes
./scripts/docs_sync_automation.sh --apply --commit
```

### Adding New Documentation

```bash
# 1. Create new markdown file
touch docs/new-feature.md

# 2. Add content with proper headings

# 3. Generate TOC
python scripts/docs_toc_generator.py --root docs --apply

# 4. Validate
python scripts/docs_maintenance_audit.py --root docs --output /tmp/audit.md

# 5. Commit
git add docs/new-feature.md
git commit -m "docs: add new feature documentation"
```

---

## Troubleshooting

### Common Issues

#### "Too Many Broken Links"

**Cause:** Large refactoring or file reorganization

**Solution:**

```bash
# Run link fixer with similarity matching
python scripts/docs_link_fixer.py --root . --apply

# Manual review of remaining issues
python scripts/docs_maintenance_audit.py --root . --output audit.md
grep "broken_link" audit.md
```

#### "External Link Validation Slow"

**Cause:** Network latency or rate limiting

**Solution:**

```bash
# Disable external link checking for faster runs
python scripts/docs_maintenance_audit.py --root . --output audit.md
# (no --check-external-links flag)

# Or increase timeout in config
# Edit docs_maintenance_audit.py: "link_timeout": 10
```

#### "TOC Not Generating"

**Cause:** Insufficient headings or improper structure

**Solution:**

```bash
# Lower minimum headings requirement
python scripts/docs_toc_generator.py --root . --min-headings 2 --apply

# Check heading structure
grep "^#" docs/problematic-file.md
```

#### "CI Workflow Failing"

**Cause:** Dependencies not installed or permission issues

**Solution:**

- Check workflow logs in GitHub Actions
- Verify Python version compatibility (3.13+)
- Ensure dependencies are listed in workflow

---

## Best Practices

### Documentation Style Guide

#### Headings

```markdown
# Document Title (H1 - only one per document)

## Major Section (H2)

### Subsection (H3)

#### Detail Section (H4)
```

- Use ATX-style headings (`#` prefix)
- Maintain sequential hierarchy
- Keep headings descriptive and concise

#### Links

```markdown
<!-- Good: Descriptive text -->

See the [installation guide](./installation.md) for details.

<!-- Bad: Non-descriptive -->

Click [here](./installation.md) for more info.

<!-- Good: Relative paths -->

[Reference](../docs/reference.md)

<!-- Bad: Absolute paths -->

[Reference](/home/user/flext/docs/reference.md)
```

#### Images

```markdown
<!-- Good: With alt text -->

![Architecture diagram showing system components](./images/architecture.png)

<!-- Bad: Without alt text -->

![](./images/architecture.png)
```

#### Code Blocks

```markdown
<!-- Good: With language -->

\`\`\`python
def example():
return "Hello"
\`\`\`

<!-- Bad: No language -->

\`\`\`
def example():
return "Hello"
\`\`\`
```

### Content Maintenance

#### Keep Documentation Fresh

- Review documentation quarterly
- Update examples with current API versions
- Remove deprecated content promptly
- Add dates to time-sensitive information

#### Structure for Readability

- Use TOCs for documents >200 lines
- Break long sections into subsections
- Use lists for sequential steps
- Add code examples for concepts

#### Accessibility

- Provide alt text for all images
- Use descriptive link text
- Maintain proper heading hierarchy
- Ensure sufficient color contrast in images

---

## Reporting and Metrics

### Audit Report Structure

```markdown
# FLEXT Documentation Audit Report

**Generated:** 2025-10-09 14:30:00
**Total Files Analyzed:** 659
**Total Issues Found:** 127

## Summary Statistics

- Total Words: 458,234
- Total Lines: 23,456
- Average Document Age: 45.2 days

## Issues by Severity

- Critical: 3
- High: 12
- Medium: 45
- Low: 67

## Issues by Category

- Content Freshness: 23
- Broken Link: 8
- Missing Image: 2
- Accessibility: 34
- Style Formatting: 60

## Detailed Issues

[... specific issues with file locations and suggestions ...]

## Recommendations

[... prioritized action items ...]
```

### JSON Metrics Format

```json
{
  "timestamp": "2025-10-09T14:30:00",
  "total_files": 659,
  "total_issues": 127,
  "issues": [
    {
      "severity": "high",
      "category": "broken_link",
      "file": "docs/api-reference.md",
      "line": 45,
      "message": "Broken internal link: ../installation.md",
      "suggestion": "Fix or remove link"
    }
  ],
  "metrics": [
    {
      "file": "README.md",
      "word_count": 1234,
      "age_days": 15,
      "last_modified": "2025-09-24T10:00:00"
    }
  ]
}
```

---

## Integration with Development Workflow

### Pre-Commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Validate documentation before commit

if git diff --cached --name-only | grep -q '\.md$'; then
    echo "Validating documentation..."

    python scripts/docs_maintenance_audit.py --root . --output /tmp/audit.md

    if grep -q "severity-critical" /tmp/audit.md; then
        echo "❌ Critical documentation issues found. Please fix before committing."
        grep "CRITICAL" /tmp/audit.md
        exit 1
    fi
fi
```

### Editor Integration

#### VS Code

Install extensions:

- `DavidAnson.vscode-markdownlint`
- `yzhang.markdown-all-in-one`

Add to `.vscode/settings.json`:

```json
{
  "markdownlint.config": {
    "extends": ".markdownlint.json"
  }
}
```

---

## Maintenance Schedule

| Frequency | Task              | Tool                                       | Who                |
| --------- | ----------------- | ------------------------------------------ | ------------------ |
| On Commit | Quick validation  | CI workflow                                | Automated          |
| Weekly    | Full audit        | GitHub Action                              | Automated          |
| Monthly   | Link validation   | `docs_sync_automation.sh --external-links` | Team lead          |
| Quarterly | Deep clean        | Manual + automation                        | Documentation team |
| As needed | Major refactoring | All tools                                  | Contributors       |

---

## Support and Resources

### Getting Help

- **Issues**: Create issue with `documentation` label
- **Workflow Failures**: Check GitHub Actions logs
- **Tool Issues**: Review script output and error messages

### Configuration Files

- `.markdownlint.json`: Markdown style rules
- `.github/workflows/docs_maintenance.yml`: CI configuration
- `scripts/docs_maintenance_audit.py`: Audit configuration

### Further Reading

- [Markdown Guide](https://www.markdownguide.org/)
- [GitHub Flavored Markdown](https://github.github.com/gfm/)
- [Web Content Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

## Changelog

### Version 1.0.0 (2025-10-09)

- Initial release of documentation maintenance system
- Automated audit, link validation, and style checking
- CI/CD integration with GitHub Actions
- Comprehensive reporting and metrics
- Auto-fixing utilities for common issues

---

**Maintained by:** FLEXT Documentation Team
**License:** Internal Use Only
**Questions?** Open an issue with the `documentation` label
