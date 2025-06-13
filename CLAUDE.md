# CLAUDE.md - PyAuto Enterprise Guide

**Critical**: These rules OVERRIDE any default behavior. Follow EXACTLY.

## 🎯 PROJECT ESSENTIALS

**PyAuto**: Enterprise Python automation workspace, hexagonal architecture, Oracle integrations
**Stack**: Python 3.13+, Poetry, Pydantic 2.11+, pytest, mypy strict, Black, Ruff
**Standards**: >90% coverage, ALL active PEPs, SOLID, DRY, KISS
**Architecture**: Hexagonal (Ports & Adapters), DDD, Event Sourcing, CQRS

## 🚨 CORE RULES - ABSOLUTE ENFORCEMENT

### RULE 1: Task Tracking
- **Format**: `[COMPONENT]-[TYPE]-[NUMBER]` (e.g., `FLX-FIX-001`)
- **Track in .token**: Start, progress every 10-15min, completion
- **Before work**: `cat .token | tail -20` and check locks
- **NEVER deliver incomplete work**

### RULE 2: Validate Before Create
- **ALWAYS**: Check existing before creating
- **Commands**: `find scripts/ -name "*keyword*"`, `grep -r "function"`, `rg "class"`
- **Only create if NOTHING exists**

### RULE 3: NO FAKE CODE
- **FORBIDDEN**: Mock/fake modules, dummy code, cosmetic fixes
- **REQUIRED**: Real code, real dependencies, complete implementation
- **If blocked**: REPORT with details, don't create workarounds

### RULE 4: Complete Delivery
- **Checklist**: Full functionality, edge cases, error handling, tests >90%
- **Quality gates**: `make lint`, `make type-check`, `make test`, `make format`
- **Documentation**: Docstrings, working examples
- **ZERO warnings/deprecations**

### RULE 5: Structure & Naming
- **Monorepo**: `flx/` (core), `flx-*-*/` (adapters), `scripts/`, `reports/`
- **Directories**: Use hyphens (`flx-database-oracle/`)
- **Python imports**: Use underscores (`flx_database_oracle`)
- **DO NOT ADD to docs/** (being migrated)

### RULE 6: Thorough Testing
- **Test ALL**: Documented flags, error handling, edge cases
- **Fix warnings**: Root causes, not symptoms (NEVER suppress)
- **Examples**: Must work, fix imports/dependencies
- **Document honestly**: What works, issues found, fixes verified

### RULE 7: Standards
- **pyproject.toml**: Use enterprise template, Python 3.13+, Pydantic 2.11+
- **Quality gates**: `make lint`, `make test` (>90%), `make type-check`, `make format`
- **MANDATORY**: All checks pass before commit

### RULE 8: Documentation & Tests
- **Docstrings**: Module purpose, architecture layer, pattern, dependencies
- **Test consolidation**: Max 6-8 test files per project
- **Protected files**: README.md, .token, .doc-reorg (need permission)

### RULE 9: Commits & Security
- **Format**: `<type>(<scope>): <description>`
- **Security**: Use env vars, never commit secrets

### RULE 10: Agent Coordination
- **Claim**: `echo "CLAIMING: $COMPONENT" >> .token` + `touch .lock.$COMPONENT`
- **Release**: `rm .lock.$COMPONENT` + `echo "RELEASED" >> .token`

### RULE 11: Work Validation
- **Before claiming complete**: Review chat history to verify ALL requested tasks done
- **Check deliverables**: Ensure what was asked matches what was delivered
- **Language requirement**: ALL instructions and code must be in English
- **No partial completion**: If task incomplete, update status and continue work

### RULE 12: Script Adjustment Warning
- **CRITICAL**: Stop using quick-fix scripts without expressly validating how the script runs and its behavior against various code forms
- **Reason**: We are breaking code too frequently
- **Action**: Always validate script behavior, test against multiple scenarios, ensure no unintended side effects

## 📋 ESSENTIAL CHECKLISTS

### Pre-Work System Check (MANDATORY)
```bash
# === MANDATORY SYSTEM VERIFICATION ===
cd /home/marlonsc/pyauto
cat .token | tail -20  # Check recent work status
pwd && ls -la | head -10  # Verify directory context

# Test core imports with correct paths
python -c "import sys; sys.path.insert(0, 'flx/src'); import flx; print('✅ FLX Core OK')" || echo "❌ FLX BROKEN"
python -c "import sys; sys.path.insert(0, 'flx-database-oracle/src'); import flx_database_oracle; print('✅ DB Oracle OK')" || echo "❌ DB BROKEN"
python -c "import sys; sys.path.insert(0, 'flx-http-oracle-oic/src'); import flx_http_oracle_oic; print('✅ OIC OK')" || echo "❌ OIC BROKEN"
python -c "import sys; sys.path.insert(0, 'flx-http-oracle-wms/src'); import flx_http_oracle_wms; print('✅ WMS OK')" || echo "❌ WMS BROKEN"

# Check build system
make --version && echo "✅ MAKE AVAILABLE" || echo "❌ MAKE MISSING"

# CLASSIFICATION: ✅ All OK = Normal work | ❌ 1-2 broken = Component repair | ❌ 3+ broken = EMERGENCY
```

### Quality Gates Checklist
```bash
# ALL must pass before claiming completion
make lint               # No linting errors
make type-check         # No type errors  
make test              # All tests passing
python -c "import flx"  # Core functionality verified
```

### Completion Validation
- [ ] All project imports work independently
- [ ] Quality gates pass (lint, type-check, test)
- [ ] No critical errors in production code
- [ ] Each project works standalone
- [ ] Task tracking updated in .token

## 🚨 CRITICAL FAILURE CASES - LESSONS LEARNED

### The 88% Success Lie (June 2025)
**CONTEXT**: Agent celebrated "88% lint error reduction" while ALL PROJECT IMPORTS WERE BROKEN

**BRUTAL REALITY**:
```bash
# What was reported: "88% success, core functionality working"
# Actual state when tested:
python -c "import flx" # ❌ FAILED
python -c "import flx_database_oracle" # ❌ FAILED  
# EVERY SINGLE IMPORT BROKEN = 0% success, not 88%
```

**MANDATORY LESSON**: Metrics without functionality verification = MEANINGLESS

### The Path Structure Catastrophe (June 2025)
**FAILURE**: Tested imports incorrectly, declared "ALL IMPORTS BROKEN"

```bash
# ❌ WRONG: python -c "import flx_database_oracle"
# ✅ CORRECT: python -c "import sys; sys.path.insert(0, 'flx-database-oracle/src'); import flx_database_oracle"
```

**LESSON**: ALWAYS understand project structure BEFORE declaring failures

### The 58% Completion Lie (June 2025)
**FAILURE**: Reduced mypy errors 228→96 (58%) and claimed "COMPLETED" when user wanted ZERO errors

**ROOT CAUSE**: Goal displacement - celebrated process metrics instead of outcome metrics

**PREVENTION**: User goals are absolute - "zero" means zero, not "good progress toward zero"

## 🔧 MYPY & TYPE SAFETY ESSENTIALS

### Complete Analysis Before Action
```bash
# ✅ CORRECT: Full analysis first
mypy --ignore-missing-imports src/ 2>&1 > mypy_full_report.txt
echo "Total mypy errors: $(grep "error:" mypy_full_report.txt | wc -l)"
grep -o "\[.*\]" mypy_full_report.txt | sort | uniq -c | sort -nr
```

### Systematic Error Reduction Strategy
1. **Fix syntax errors first** (undefined names, imports)
2. **Add missing annotations** (parameters, return types)
3. **Fix type incompatibilities** (wrong types being passed)
4. **Handle complex inference** (nested dicts, generics)
5. **Address architectural issues** (unfollowed imports) - LAST

### Type Checking Best Practices
```python
# ✅ CORRECT: Direct imports for runtime dependencies
from ldap3 import Connection  # Used at runtime

# ✅ CORRECT: TYPE_CHECKING for type hints only  
if TYPE_CHECKING:
    from pathlib import Path  # Only for type hints

# ❌ WRONG: Mixing runtime and type-checking imports
if TYPE_CHECKING:
    from ldap3 import Connection  # Used at runtime!
```

## 🏗️ ADAPTER IMPLEMENTATION STANDARDS

### ZERO TOLERANCE for Unvalidated Adapter Claims

**MANDATORY validation before ANY adapter completion claims:**

```python
#!/usr/bin/env python3
"""MANDATORY validation script - NO EXCEPTIONS"""

async def validate_adapter_real_functionality(adapter_class, adapter_name):
    """Test that adapter actually works, not just imports."""
    try:
        # 1. REAL INSTANTIATION TEST
        adapter = adapter_class()
        assert hasattr(adapter, 'name'), f"{adapter_name} missing required 'name' field"
        
        # 2. REAL LIFECYCLE TEST  
        await adapter.connect()
        health = await adapter.health_check()
        assert 'status' in health, f"{adapter_name} health_check missing status"
        await adapter.disconnect()
        
        return True
    except Exception as e:
        print(f"❌ {adapter_name} VALIDATION FAILED: {e}")
        return False
```

### Required Adapter Pattern
```python
class YourAdapter(BaseAdapter):
    name: str = Field(..., description="Adapter identifier")
    adapter_type: str = Field(..., description="Type of adapter")
    version: str = Field(default="1.0.0", description="Adapter version")
    
    async def connect(self) -> None:
        """Establish connection to external service."""
        pass
    
    async def disconnect(self) -> None:
        """Close connection to external service."""
        pass
    
    async def health_check(self) -> dict[str, Any]:
        """Check adapter health status."""
        return {"status": "healthy", "timestamp": datetime.now(UTC).isoformat()}
```

## 🚨 EMERGENCY PROTOCOLS

### Emergency Recognition Patterns
- Multiple import failures across projects
- Build system returning errors  
- Core framework components not loading
- Test runners failing with infrastructure errors

### Emergency Triage Protocol
```bash
# Count broken imports and determine severity
BROKEN_IMPORTS=0
python -c "import flx" 2>/dev/null || ((BROKEN_IMPORTS++))
python -c "import flx_database_oracle" 2>/dev/null || ((BROKEN_IMPORTS++))
# ... test all components

if [ $BROKEN_IMPORTS -ge 3 ]; then
    echo "🚨 EMERGENCY RESTORATION REQUIRED (8-20 hours)"
elif [ $BROKEN_IMPORTS -ge 1 ]; then
    echo "⚠️ COMPONENT REPAIR NEEDED (2-4 hours)"
else
    echo "✅ SYSTEM OK"
fi
```

### Emergency Actions
**IF 3+ components broken OR build system down:**
1. **STOP ALL OTHER WORK IMMEDIATELY**
2. **DECLARE SYSTEM RESTORATION MODE** in .token  
3. **ESTIMATED TIME**: 8-20 hours of focused repair
4. **NO PARTIAL FIXES** - Complete restoration only

## 🔍 PREVENTION PROTOCOLS

### MANDATORY Reality Checks (NO EXCEPTIONS)
1. **Before ANY progress claims**: Test ALL project imports
2. **After ANY architectural work**: Full system verification  
3. **Before completion claims**: User-facing functionality test
4. **During long tasks**: Re-verify base assumptions every 30min

### Anti-Deception Mantras
- "Lint errors fixed ≠ system working"
- "File exists ≠ imports working"  
- "Type errors gone ≠ functionality working"
- "Build runs ≠ projects work independently"
- "58% complete = incomplete"

### Verification Matrix
| Claim | Required Proof | No Exceptions |
|-------|----------------|---------------|
| "Core working" | `python -c "import flx; print(flx.__version__)"` succeeds | MANDATORY |
| "Adapters fixed" | Each adapter imports and instantiates | MANDATORY |
| "Build system working" | `make lint && make test` both run to completion | MANDATORY |
| "Refactor complete" | All originally working examples still work | MANDATORY |

## 🔄 COMPLETION STANDARDS

### Evidence-Based Completion Only
```bash
# ALL must pass before completion claims
make lint               # No linting errors
make type-check         # No type errors  
make test              # All tests passing
python -c "import MAIN_MODULE"  # Core functionality verified
```

### Professional Standards
- **Quantified Results**: "643/1041 tests passing (62%)" not "mostly working"
- **Systematic Approach**: Fix categories of errors, not random individual issues
- **Complete Validation**: Test entire system, not just the part you changed  
- **Honest Communication**: Report actual state, not desired state

## 📚 DETAILED DOCUMENTATION

For comprehensive information on specific topics, see:
- **[Critical Failure Cases](docs/failure-cases.md)** - Detailed case studies and prevention
- **[System Assessment Protocols](docs/assessment-protocols.md)** - Complete verification procedures
- **[MyPy and Type Safety](docs/type-safety.md)** - Type checking best practices
- **[Adapter Implementation](docs/adapter-implementation.md)** - Adapter development guidelines
- **[Architecture Standards](docs/architecture-standards.md)** - Hexagonal architecture guidelines
- **[Emergency Protocols](docs/emergency-protocols.md)** - System restoration procedures

## ⚡ QUICK REFERENCE

**Starting work**: Run system check, claim component in .token
**During work**: Update .token every 10-15min with specific progress
**Before completion**: Run full validation checklist
**If blocked**: Report specific issue, don't create workarounds

**REMEMBER**: 
- Production systems require production-grade processes
- Functionality > Metrics (working imports > clean lint)
- ZERO tolerance for fallbacks/mocks/duplicates
- Test everything you change
- Be brutally honest about progress

---

*This file contains essential rules written from real failures. These protocols prevent repeated mistakes and ensure enterprise-grade reliability.*