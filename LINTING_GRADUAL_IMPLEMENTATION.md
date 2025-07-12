# FLEXT WORKSPACE - GRADUAL LINTING IMPLEMENTATION GUIDE

**Status**: Strategy Defined & Tools Created
**Date**: 2025-07-12

## ✅ COMPLETED

1. **Linting Analysis Report**
   - Total issues: 4,990 across 23 projects
   - Created automated reporting script: `scripts/linting_report.py`
   - Identified issue categories and priorities

2. **Gradual Fix Strategy**
   - Created `LINTING_STRATEGY.md` with 4-phase approach
   - Developed automated fix script: `scripts/gradual_lint_fix.sh`
   - Tested on `flext-target-oracle` (no safe fixes available)

3. **Key Findings**
   - `flext-core` has 0 issues - proof that clean code is achievable
   - Most common issues:
     - BLE001: Blind exception handling (231 instances)
     - S106: Hardcoded passwords (205 instances - mostly in tests)
     - G004: f-string in logging (153 instances)
   - Safe auto-fixable categories are minimal in current codebase

## 🎯 RECOMMENDED APPROACH

### Phase 1: New Code Standards (Immediate)
```bash
# Add to all projects' pyproject.toml
[tool.ruff]
select = ["F", "E", "W", "I", "N", "UP", "S", "BLE", "FBT", "A", "C4", "DTZ", "T10", "EM", "EXE", "ISC", "ICN", "G", "INP", "PIE", "T20", "PT", "RET", "SIM", "TID", "TCH", "ARG", "PTH", "ERA", "PD", "PGH", "PL", "TRY", "NPY", "RUF"]
ignore = ["S106"]  # Allow hardcoded passwords in tests

# Add pre-commit hook (warning mode)
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.8.0
  hooks:
    - id: ruff
      args: [--exit-zero]  # Warning only, don't block commits
```

### Phase 2: Project-by-Project Fixes

**Low-Risk Projects First:**
1. `flext-cli` - 223 issues
2. `flext-plugin` - 228 issues  
3. `flext-target-oracle` - 2 issues

**Then Medium-Risk:**
4. `flext-observability` - 159 issues
5. `flext-meltano` - 133 issues
6. `flext-ldap` - 80 issues

**High-Risk Last:**
7. `flext-auth` - 680 issues (security critical)
8. `flext-api` - 252 issues
9. `flext-grpc` - 306 issues

### Phase 3: Manual Review Categories

These require human judgment:
- **BLE001**: Blind exception handling → Add specific exception types
- **G004**: f-strings in logging → Use lazy % formatting
- **ANN001/ANN201**: Missing type annotations → Add types carefully
- **ARG001/ARG002**: Unused arguments → May be required by interfaces

## 📝 EXAMPLE FIXES

### BLE001: Blind Exception
```python
# Bad
try:
    risky_operation()
except:  # BLE001
    pass

# Good
try:
    risky_operation()
except SpecificException:
    logger.exception("Operation failed")
```

### G004: Logging f-strings
```python
# Bad
logger.info(f"Processing {item}")  # G004

# Good
logger.info("Processing %s", item)
```

### S106: Hardcoded Password (in tests)
```python
# Acceptable in tests - add to ignore list
def test_connection():
    config = Config(password="test123")  # noqa: S106
```

## 🚀 NEXT STEPS

1. **Update pre-commit hooks** across all projects (warning mode)
2. **Start with flext-cli** as pilot project
3. **Document each fix** in commit messages
4. **Monitor test coverage** - ensure no functionality loss
5. **Gradual rollout** - one project per week

## 📊 SUCCESS METRICS

- Week 1-2: Pre-commit hooks active (warning mode)
- Month 1: 3-5 projects cleaned
- Month 2: 50% reduction in issues
- Month 3: All projects under 50 issues each
- End state: Pre-commit enforcing (blocking mode)

## 💡 LESSONS LEARNED

1. **Auto-fixable issues are rare** - Most require human judgment
2. **Test files have many "issues"** - Need separate standards
3. **Gradual is key** - Don't break working code for style
4. **flext-core proves it's possible** - 0 issues achieved

---

**Remember**: The goal is sustainable code quality, not perfection overnight.