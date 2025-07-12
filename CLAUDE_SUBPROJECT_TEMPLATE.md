# CLAUDE.md - [PROJECT_NAME] PROJECT STANDARDS

**Hierarchy**: PROJECT-SPECIFIC
**Reference**: `/home/marlonsc/flext/CLAUDE.md` → Workspace standards & ANTI-CHAOS rules
**Last Updated**: [DATE]

---

## 📋 PROJECT OVERVIEW

**Name**: [PROJECT_NAME]
**Purpose**: [Brief description of project purpose]
**Status**: [OPERATIONAL/IN DEVELOPMENT/MAINTENANCE]

---

## 🛑 ANTI-CHAOS PROTOCOL REMINDER

### **THIS PROJECT FOLLOWS WORKSPACE ANTI-CHAOS RULES**

**ABSOLUTELY FORBIDDEN**:

- ❌ Modifying pyproject.toml, .gitignore, Makefile without permission
- ❌ Creating loose scripts (fix_*.py, temp_*.py, migrate_*.py)
- ❌ Making changes without --debug and --trace diagnosis
- ❌ Duplicating existing code or functionality
- ❌ Creating unverified documentation or reports

**REFER TO**: `/home/marlonsc/flext/CLAUDE.md` → Section "ANTI-CHAOS PROTOCOL"

---

## 🏗️ PROJECT STRUCTURE

```
[PROJECT_NAME]/
├── src/               # Source code
├── tests/             # Test files
├── scripts/           # ONLY approved automation scripts
├── docs/              # Project documentation
├── .env.example       # Environment template
└── pyproject.toml     # DO NOT MODIFY without permission
```

---

## 🔧 PROJECT-SPECIFIC PATTERNS

### Dependencies

- [List key dependencies and their purposes]
- [DO NOT add new dependencies without checking existing functionality]

### Environment Variables

- [List required environment variables with PREFIX]
- [Use project-specific prefix: PROJECT_NAME_*]

### Debug Commands

```bash
# Standard debug execution
python -m [module_name] --debug --trace

# With full logging
LOG_LEVEL=DEBUG python -m [module_name]
```

---

## 🎯 QUALITY GATES (MANDATORY)

Run these at the END of EVERY work cycle:

```bash
# 1. Lint check
make lint

# 2. Type check  
make typecheck

# 3. Run tests
make test

# 4. Verify no loose scripts
find . -name "fix_*.py" -o -name "temp_*.py" | grep -v tests

# 5. Check project still works
python -m [main_module] --help
```

---

## 📊 KNOWN ISSUES

### Active Issues

- [Issue description] - [Workaround if any]

### Resolved Issues

- [Issue description] - [Resolution applied]

---

## 🚀 DEVELOPMENT WORKFLOW

1. **BEFORE starting work**: Read this file AND workspace CLAUDE.md
2. **BEFORE modifying**: Check if functionality exists with Grep/Read
3. **DURING development**: Use --debug and --trace for all executions
4. **AFTER changes**: Run quality gates checklist
5. **IF errors occur**: Debug first, don't create fix scripts

---

## ⚠️ CRITICAL REMINDERS

- **NEVER** assume - always verify with tools
- **NEVER** create scripts outside project structure  
- **NEVER** modify infrastructure files without permission
- **ALWAYS** use debug mode for diagnosis
- **ALWAYS** check for existing implementations first

---

**REMEMBER**: Stability over activity. When in doubt, investigate more.
