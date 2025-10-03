# FLEXT Workspace Standards

**Authority**: Workspace-level configuration and project standards
**Last Update**: 2025-10-03
**Reference**: This is the MANUAL standards document - NO automation allowed

---

## 🛑 ZERO TOLERANCE POLICY

**ABSOLUTELY FORBIDDEN**:
- ❌ Template generators for project configurations
- ❌ Automatic script setup tools
- ❌ Bulk configuration copying
- ❌ One-size-fits-all standardization
- ❌ `fix_*` scripts that modify code automatically
- ❌ `temp_*` scripts in version control
- ❌ `generate_*` configuration scripts

**REQUIRED APPROACH**:
- ✅ Manual verification project-by-project
- ✅ Reality-based standards from working projects
- ✅ Adapt configurations to project maturity
- ✅ Test each change before committing
- ✅ Document deviations with rationale

---

## 📚 Reference Implementation: flext-core

**flext-core** is the reference implementation for all FLEXT projects.

### Standard Files (flext-core proven patterns):

1. **Makefile**
   - Quality targets: `lint`, `type-check`, `test`, `validate`
   - Development: `setup`, `install`, `clean`
   - Single-letter aliases: `l`, `t`, `tc`, `v`

2. **pyproject.toml**
   - `[build-system]` - Poetry Core
   - `[project]` - PEP 621 metadata
   - `[tool.poetry]` - Dependencies
   - `[tool.ruff]` - Extends `../ruff-shared.toml`
   - `[tool.mypy]` or `[tool.pyrefly]` - Type checking

3. **.pre-commit-config.yaml**
   - Uses `poetry run` for all tools
   - Hooks: ruff-format, ruff-lint, mypy/pyrefly
   - Complexity checks: radon-cc, radon-mi

4. **.gitignore**
   - Python artifacts: `__pycache__`, `.pyc`, `.pyo`
   - Caches: `.ruff_cache`, `.mypy_cache`, `.pytest_cache`
   - Build: `dist/`, `build/`, `*.egg-info/`
   - Project-specific patterns as needed

5. **ruff.toml** (or extend shared)
   - Extends: `../ruff-shared.toml`
   - Project-specific overrides only

---

## 🎯 Per-Project Standards (Adapted to Reality)

### Coverage Requirements (Based on Project Maturity):

| Project Type | Min Coverage | Rationale |
|--------------|--------------|-----------|
| **flext-core** | 100% | Foundation library - zero tolerance |
| **Stable Libraries** (api, cli, auth) | 85% | Production-ready domain libraries |
| **Domain Libraries** (ldap, ldif, db-oracle) | 80% | Specialized functionality |
| **Singer Projects** (tap-*, target-*, dbt-*) | 75% | Plugin ecosystem |
| **Enterprise Tools** (client-a-oud-mig) | 70% | Application logic |
| **Experimental** | 60% | Proof of concept phase |

### Type Checking Standards:

| Project Status | MyPy/Pyrefly | Policy |
|----------------|--------------|--------|
| **Production** | Strict mode, ZERO errors in `src/` | Foundation + stable libraries |
| **Stable** | ZERO errors in `src/`, warnings in `tests/` OK | Domain libraries |
| **Active Dev** | ZERO errors in core modules | Singer projects + tools |
| **Experimental** | Type hints required, warnings OK | POC projects |

---

## 📂 Scripts Organization (Reality-Based)

### Directory Structure:
```
scripts/
├── git/                    # Git operations
│   └── git_ultimate_cleanup.py
├── testing/                # Test runners
│   ├── run_tests.py
│   ├── testing_metrics_dashboard.sh
│   └── testing_quality_gates.sh
├── validation/             # Validators
│   ├── ecosystem_quality_validator.sh
│   ├── domain_separation_validator.sh
│   └── validate_equilibrium.py
├── quality/                # Quality analysis
│   ├── quality_dashboard.sh
│   └── [analysis tools]
└── [other categories as needed]
```

### Script Naming Conventions:
- ✅ `[verb]_[noun].py` - Clear action scripts
- ✅ `[category]_[function]_[qualifier].sh` - Descriptive shell scripts
- ❌ `fix_*` - Temporary fixes belong in branches, not main
- ❌ `temp_*` - Temporary files don't belong in version control
- ❌ `generate_*` - No configuration generators allowed

---

## 🔍 Manual Verification Checklist

For EACH project, manually verify:

### 1. Makefile Verification:
```bash
# Check targets exist:
make -n setup          # Should install dependencies + pre-commit
make -n lint           # Should run ruff check
make -n type-check     # Should run mypy or pyrefly
make -n test           # Should run pytest with coverage
make -n validate       # Should run ALL quality gates
```

### 2. pyproject.toml Verification:
- [ ] Uses `[build-system]` with poetry-core
- [ ] Has `[project]` metadata (PEP 621)
- [ ] Lists flext-core as dependency (if applicable)
- [ ] Extends workspace ruff-shared.toml
- [ ] Has appropriate MIN_COVERAGE for project type
- [ ] Dependencies match project reality

### 3. Pre-commit Verification:
- [ ] Uses `poetry run` for all tools
- [ ] Hooks match Makefile quality gates
- [ ] No outdated or unused hooks

### 4. .gitignore Verification:
- [ ] Covers Python standard patterns
- [ ] Includes project-specific patterns
- [ ] NO project configuration files ignored
- [ ] NO workspace-level patterns in subproject .gitignore

### 5. Quality Gates Verification:
```bash
# Test complete pipeline:
make validate          # Should pass with ZERO errors in src/
```

---

## 📋 Project-by-Project Standardization Process

### Step 1: Activate & Analyze
```bash
mcp__serena-flext__activate_project project="flext-[name]"
ls -la  # Check existing files
```

### Step 2: Compare with flext-core
```bash
# Read flext-core reference files:
cat ../flext-core/Makefile
cat ../flext-core/pyproject.toml
cat ../flext-core/.pre-commit-config.yaml
```

### Step 3: Manual Verification
- Use checklist above
- Identify gaps and deviations
- Document WHY deviations exist

### Step 4: Adapt Configuration
- Edit files individually
- Test after EACH change
- Commit when validated

### Step 5: Document Deviations
- Update project CLAUDE.md if needed
- Record rationale for non-standard configurations

---

## 🚫 Common Mistakes to Avoid

1. **Copy-Paste from other projects**
   - ❌ Each project has unique needs
   - ✅ Use flext-core as reference, adapt to reality

2. **Forcing identical configs**
   - ❌ Different project types need different standards
   - ✅ Adapt coverage/type-checking to maturity

3. **Auto-generating configurations**
   - ❌ Templates don't understand project context
   - ✅ Manual configuration ensures correctness

4. **Ignoring project history**
   - ❌ Some deviations have good reasons
   - ✅ Understand WHY before changing

5. **Bulk commits**
   - ❌ Multiple projects changed at once
   - ✅ One project per commit with testing

---

## ✅ Success Criteria

A project is properly standardized when:

1. **Quality Gates Pass**:
   ```bash
   make validate  # Zero errors
   ```

2. **Configurations Match Project Type**:
   - Coverage requirements appropriate
   - Type checking strictness appropriate
   - Dependencies accurate

3. **Documentation Current**:
   - CLAUDE.md reflects reality
   - Deviations documented with rationale

4. **Testing Proves Correctness**:
   - All tests pass
   - Coverage meets standards
   - No regressions introduced

---

## 🔄 Maintenance

**When to Review Standards**:
- New project added to workspace
- Project graduates to higher maturity level
- Market patterns evolve (e.g., new Python version)
- Quality tools updated (e.g., ruff, mypy)

**Who Maintains**:
- Manual review by human developers
- NO automation allowed
- Changes through normal code review process

---

**REMEMBER**: These are STANDARDS, not TEMPLATES. Adapt to project reality, don't force conformity.
