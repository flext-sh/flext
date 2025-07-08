# FLEXT Development Standards - Template Usage Guide

## 📋 Overview

This directory contains standardized templates for all FLEXT projects to ensure:

- **100% PEP compliance** with maximum strictness
- **Latest tool versions** with bleeding-edge options
- **Quality gateways** that prevent any warnings
- **Unified development experience** across all projects
- **Zero tolerance** for quality issues

## 📁 Available Templates

### Core Configuration Files

| Template | Purpose | Features |
|----------|---------|----------|
| `pyproject.toml.template` | Poetry + tools config | Latest versions, Git deps option, strict quality rules |
| `Makefile.template` | Development automation | Quality gateways, zero tolerance mode, color output |
| `.pre-commit-config.yaml.template` | Pre-commit hooks | Latest tools, security scanning, strict validation |
| `.github_workflows_ci.yml.template` | CI/CD pipeline | Multi-platform testing, security scans, quality gates |
| `.vscode_settings.json.template` | VS Code/Cursor config | Aligned with all tools, strict analysis, auto-formatting |

### Template Variables

All templates use `{{VARIABLE}}` placeholders:

- `{{PROJECT_NAME}}` - Project name (e.g., "flext-quality")
- `{{PACKAGE_NAME}}` - Python package name (e.g., "flext_quality")
- `{{PROJECT_CLI_NAME}}` - CLI command name (e.g., "flext-quality")
- `{{VERSION}}` - Current version (e.g., "0.1.0")
- `{{DESCRIPTION}}` - Project description
- `{{KEYWORDS}}` - Additional keywords
- `{{ADDITIONAL_DEPENDENCIES}}` - Project-specific deps
- `{{SONAR_CONNECTION_ID}}` - SonarLint connection (optional)
- `{{SONAR_PROJECT_KEY}}` - SonarLint project key (optional)

## 🔧 Usage Instructions

### 1. Manual Template Application (Recommended)

**DO NOT use automated scripts.** Apply templates manually with careful review:

```bash
# 1. Copy template to project
cp FLEXT_STANDARDS/pyproject.toml.template flext-project/pyproject.toml

# 2. Replace template variables manually
# Edit the file and replace {{PROJECT_NAME}} etc.

# 3. Test immediately
cd flext-project
make quality-gate
```

### 2. Template Customization Process

For each project:

1. **Start with base template**
2. **Replace ALL template variables**
3. **Add project-specific dependencies**
4. **Test quality gateway immediately**
5. **Fix any issues before proceeding**
6. **Never skip quality validation**

### 3. Progressive Quality Implementation

Templates include progressive strictness levels:

#### Level 1: Basic (All projects must achieve)

- ✅ Poetry configuration
- ✅ Basic linting (Ruff)
- ✅ Code formatting (Black)
- ✅ Import sorting (isort)
- ✅ Basic type checking

#### Level 2: Standard (Production projects)

- ✅ Strict type checking (MyPy)
- ✅ Security scanning (Bandit, Safety)
- ✅ Test coverage > 80%
- ✅ Pre-commit hooks
- ✅ CI/CD pipeline

#### Level 3: Excellence (Critical projects)

- ✅ 100% type coverage
- ✅ 90%+ test coverage
- ✅ Documentation coverage
- ✅ Performance testing
- ✅ Zero warnings/errors

## 🚨 Quality Gateway Rules

### Zero Tolerance Policy

The Makefile template implements **zero tolerance** quality gates:

```bash
make quality-gate  # Must pass 100% - no exceptions
```

### Quality Gate Components

1. **Poetry Lock Check** - Dependencies must be locked
2. **Ruff Linting** - Zero linting errors allowed
3. **Format Check** - Code must be perfectly formatted
4. **Type Check** - Strict MyPy validation
5. **Security Check** - No security vulnerabilities
6. **Test Validation** - All tests must pass

### Failure Handling

❌ **If ANY quality gate fails:**

- ❌ **DO NOT** commit code
- ❌ **DO NOT** create pull requests
- ❌ **DO NOT** merge changes
- ✅ **FIX** all issues first
- ✅ **RE-RUN** quality gate
- ✅ **ONLY** proceed when 100% clean

## 🛠️ Tool Configuration Hierarchy

### Tool Selection Priority

1. **Ruff** (primary linter + formatter)
2. **Black** (code formatting)
3. **MyPy** (type checking)
4. **isort** (import sorting)
5. **Bandit** (security)
6. **Safety** (dependency security)
7. **Pytest** (testing)

### Configuration Sources

Tools read configuration in this order:

1. `pyproject.toml` (primary)
2. Project-specific overrides
3. Global defaults

## 📦 Git Dependencies Option

Templates include commented sections for bleeding-edge versions:

```toml
# Uncomment for latest Git versions
# ruff = {git = "https://github.com/astral-sh/ruff.git", branch = "main"}
# mypy = {git = "https://github.com/python/mypy.git", branch = "master"}
```

**Use Git dependencies when:**

- ✅ You need latest features
- ✅ You can handle potential instability
- ✅ You're contributing to tool development

**Avoid Git dependencies when:**

- ❌ Project requires stability
- ❌ CI/CD must be reliable
- ❌ Team prefers stable releases

## 🔄 Template Maintenance

### Update Frequency

Templates are updated when:

- 🔄 **Weekly**: Tool version updates
- 🔄 **Monthly**: Configuration improvements
- 🔄 **As needed**: Critical security updates

### Validation Process

Before updating templates:

1. ✅ Test on reference project (`flext-quality`)
2. ✅ Validate all quality gates pass
3. ✅ Check compatibility across projects
4. ✅ Document any breaking changes

## 🎯 Project Implementation Strategy

### Phase 1: Template Validation

1. Test templates on `flext-quality` (reference project)
2. Verify all quality gates pass
3. Document any required adjustments

### Phase 2: Incremental Rollout

1. Apply to 2-3 projects manually
2. Identify common issues
3. Refine templates based on findings

### Phase 3: Full Standardization

1. Apply to remaining projects
2. Establish maintenance schedule
3. Create update procedures

## ⚠️ Important Warnings

### DO NOT Use Automation

- ❌ **NEVER** apply templates automatically via scripts
- ❌ **NEVER** bulk-update without individual validation
- ❌ **NEVER** skip quality gate validation

### Manual Review Required

- ✅ **ALWAYS** review each change manually
- ✅ **ALWAYS** test quality gates immediately
- ✅ **ALWAYS** fix issues before proceeding

### Breaking Changes

- ⚠️ **EXPECT** some projects may need adjustments
- ⚠️ **PLAN** for configuration conflicts
- ⚠️ **TEST** thoroughly before committing

## 🤝 Support & Issues

### Getting Help

When facing issues:

1. 📖 Check this documentation first
2. 🔍 Review reference implementation (`flext-quality`)
3. 🧪 Test on minimal reproduction case
4. 💬 Discuss complex decisions with team

### Common Issues

- **Tool version conflicts**: Use template versions
- **Configuration conflicts**: Follow template hierarchy
- **Quality gate failures**: Fix ALL issues before proceeding
- **Performance concerns**: Optimize incrementally

---

**Remember**: These templates implement **maximum strictness** for **production-quality** code. Every project using these templates will maintain the highest standards of code quality, security, and reliability.
