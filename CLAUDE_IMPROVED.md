# CLAUDE.md - PyAuto Enterprise Guide - IMPROVED POST-FAILURE ANALYSIS

**CRITICAL**: These rules OVERRIDE any default behavior. Lessons learned from technical failures.

## 🎯 PROJECT ESSENTIALS

**PyAuto**: Enterprise Python automation workspace, hexagonal architecture, Oracle integrations
**Stack**: Python 3.13+, Poetry, Pydantic 2.11+, pytest, mypy strict, Black, Ruff
**Standards**: >90% coverage, ALL active PEPs, SOLID, DRY, KISS
**Architecture**: Hexagonal (Ports & Adapters), DDD, Event Sourcing, CQRS

## 🚨 CRITICAL RULES - LEARNED FROM FAILURES

### RULE 1: BRUTAL TECHNICAL VALIDATION - NO COSMETIC CHECKS
- **MANDATORY**: Execute actual commands, capture real output
- **FORBIDDEN**: "checking if files exist" without functional validation
- **REQUIRED**: `python -m mypy --strict src/` + capture FULL output
- **REQUIRED**: `python -m pytest tests/` + count ACTUAL collected/passed tests
- **REQUIRED**: `python -m ruff check src/` + report REAL violation count
- **Example**: "✓ imports work" = run actual import test, capture success/failure
- **NO ASSUMPTIONS**: Tool configured ≠ tool functional

### RULE 2: TYPE SAFETY DURING DEVELOPMENT - NEVER DEFER
- **MANDATORY**: Fix type errors IMMEDIATELY when introduced
- **FORBIDDEN**: "will fix types later" - fix NOW
- **REQUIRED**: MyPy strict mode with 0 errors before marking ANY task complete
- **VALIDATION**: `python -m mypy --strict src/ | grep "error:" | wc -l` must equal 0
- **NO EXCEPTIONS**: Type errors = incomplete work, not cosmetic issues

### RULE 3: TESTING INFRASTRUCTURE VALIDATION
- **MANDATORY**: Prove tests execute, don't just check files exist
- **VALIDATION COMMAND**: `python -m pytest tests/ --collect-only | grep "collected"`
- **VALIDATION COMMAND**: `python -m pytest tests/ -v | head -20` for execution proof
- **REQUIRED**: Minimum 10 tests actually collected and executed
- **FORBIDDEN**: Reporting "tests exist" without pytest execution evidence

### RULE 4: QUALITY GATES - REAL EXECUTION REQUIRED
- **BEFORE ANY "COMPLETE"**: Execute and capture output:
  ```bash
  python -m mypy --strict src/ > mypy_output.txt 2>&1
  python -m ruff check src/ > ruff_output.txt 2>&1
  python -m pytest tests/ > pytest_output.txt 2>&1
  ```
- **EVIDENCE REQUIRED**: Include real command outputs in reports
- **ZERO TOLERANCE**: "mostly working" = incomplete

### RULE 5: HONEST TECHNICAL COMMUNICATION
- **FORBIDDEN**: Minimizing serious problems as "minor issues"
- **REQUIRED**: Distinguish "functional" vs "production-ready" vs "prototype"
- **MANDATORY**: "Known Issues" section in every technical report
- **EXAMPLE**: "Framework imports successfully BUT has 15 type errors and 0 working tests"

### RULE 6: POST-REFACTOR COMPLETION PROTOCOL
- **RECOGNITION**: Heavy refactors create systematic gaps, not isolated bugs
- **MANDATORY PHASES**:
  1. **Type Safety Phase**: 0 MyPy strict errors
  2. **Testing Phase**: pytest collection + execution functional
  3. **Quality Phase**: 0 Ruff violations
  4. **Integration Phase**: cross-project functionality verified
- **NO SHORTCUTS**: Complete each phase before next
- **VALIDATION**: Each phase requires command execution proof

### RULE 7: EVIDENCE-BASED REPORTING
- **MANDATORY EVIDENCE**: Every "✓ working" claim must include:
  ```bash
  # Command executed:
  $ python -m mypy --strict src/
  # Output captured:
  Success: no issues found in 42 source files
  
  # Command executed:
  $ python -m pytest tests/
  # Output captured:
  ====================== 47 passed, 0 failed in 12.34s ======================
  ```
- **FORBIDDEN**: Claiming success without evidence
- **REQUIRED**: Include error counts, timing, specific outputs

### RULE 8: FAILURE CASCADE ANALYSIS
- **BEFORE FIXING**: Understand if errors are:
  - **Individual bugs**: Fix one by one
  - **Systematic gaps**: Refactor completion needed
  - **Architectural changes**: Full revalidation required
- **MANDATORY**: Run `python -c "import sys; import [main_module]"` before ANY work
- **IF IMPORTS FAIL**: This is systematic, not individual bugs

### RULE 9: COMPLETION CRITERIA - BRUTAL HONESTY
- **FUNCTIONAL COMPLETE**: All imports work + core functionality tested
- **QUALITY COMPLETE**: 0 MyPy errors + 0 Ruff violations + tests pass
- **PRODUCTION READY**: Quality complete + documentation + integration tested
- **NEVER CONFUSE THESE LEVELS**: Report exactly which level achieved

### RULE 10: REFACTOR AFTERMATH RECOGNITION
- **IMMEDIATE SIGNS**: 
  - Hundreds of test failures
  - Import errors on basic modules
  - Type errors throughout codebase
  - Tools reporting "no tests collected"
- **RESPONSE**: Systematic completion, not piecemeal bug fixing
- **METHODOLOGY**: Map refactor changes, complete implementations, then validate

## TECHNICAL VALIDATION CHECKLISTS

### Phase 1: Basic Functionality
```bash
# MANDATORY BEFORE ANY WORK:
python -c "import flx; print('FLX core imports')"
python -c "from flx.adapters.base import BaseAdapter; print('Adapters import')"
python -c "from flx.core.domain import Entity; print('Domain imports')"
# IF ANY FAIL: Systematic refactor completion needed
```

### Phase 2: Type Safety
```bash
# MANDATORY BEFORE CLAIMING "TYPES FIXED":
python -m mypy --strict src/ | tee mypy_results.txt
# MUST SHOW: Success: no issues found
error_count=$(grep "error:" mypy_results.txt | wc -l)
echo "MyPy errors: $error_count (must be 0)"
```

### Phase 3: Testing Infrastructure
```bash
# MANDATORY BEFORE CLAIMING "TESTS WORK":
python -m pytest tests/ --collect-only | grep "collected"
# MUST SHOW: collected N items (N > 10)
python -m pytest tests/ -v | head -20
# MUST SHOW: actual test execution
```

### Phase 4: Quality Gates
```bash
# MANDATORY BEFORE CLAIMING "QUALITY COMPLETE":
python -m ruff check src/ | tee ruff_results.txt
violation_count=$(grep "src/" ruff_results.txt | wc -l)
echo "Ruff violations: $violation_count (must be 0)"
```

## ERROR PATTERN RECOGNITION

### Pattern: "Cosmetic Success"
- **Symptom**: "Files exist", "imports configured", "tools installed"
- **Reality**: Tools don't work, imports fail, no functional validation
- **Fix**: Execute actual functionality tests

### Pattern: "Optimistic Minimization"
- **Symptom**: "Minor type issues", "small test problems", "few lint errors"
- **Reality**: System fundamentally broken, hundreds of errors
- **Fix**: Honest assessment of actual scope

### Pattern: "Feature Addition During Refactor"
- **Symptom**: Adding new features while basic functionality broken
- **Reality**: Avoiding systematic completion work
- **Fix**: Complete refactor first, then add features

## COMMUNICATION STANDARDS

### Technical Status Reporting Template
```markdown
## Technical Status Report

### Functional Status
- **Core imports**: ✓/❌ (evidence: `python -c "import flx"`)
- **Basic functionality**: ✓/❌ (evidence: actual test)
- **Integration**: ✓/❌ (evidence: cross-module test)

### Quality Status  
- **MyPy strict**: ✓/❌ (X errors - see mypy_output.txt)
- **Ruff compliance**: ✓/❌ (X violations - see ruff_output.txt)
- **Test execution**: ✓/❌ (X tests collected, Y passed)

### Known Issues
1. [Specific issue with impact assessment]
2. [Specific issue with timeline estimate]
3. [Specific issue with workaround status]

### Next Steps (Specific)
1. [Concrete action with validation criteria]
2. [Concrete action with timeline]
3. [Concrete action with success metric]
```

## MANDATORY SESSION PROTOCOL

### Session Start (EVERY TIME)
1. `cat .token | tail -20` - Understand context
2. `python -c "import flx"` - Basic functionality test
3. `python -m pytest tests/ --tb=no -q | tail -1` - Scope assessment
4. Based on results: Bug fix mode vs Refactor completion mode

### Session End (EVERY TIME)
1. Re-run basic functionality tests
2. Capture actual command outputs
3. Report honest progress with evidence
4. Update .token with REAL status

### Before Claiming "Complete"
1. ALL validation commands must pass
2. Evidence captured and included in report
3. Known issues honestly documented
4. Next steps specifically defined

This improved CLAUDE.md incorporates lessons learned from the failure analysis and mandates evidence-based technical validation.