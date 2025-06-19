# System Assessment Protocols - Development Testing

> **Function**: Complete verification procedures for system state assessment | **Audience**: Developers, QA engineers | **Status**: ✅ VALIDATED

[![Testing](https://img.shields.io/badge/testing-protocols-blue.svg)](./index.md)
[![Assessment](https://img.shields.io/badge/assessment-validation-orange.svg)](./validation-testing.md)
[![Framework](https://img.shields.io/badge/framework-FLX%200.4.0-green.svg)](../../index.md)

**Complete verification procedures for system state assessment and validation**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Development](../index.md) → **📂 Testing**: [Testing Hub](./index.md) → **📄 Current**: Assessment Protocols

### **📍 Learning Path Position**

```
[Testing Overview](./index.md) → **[Assessment Protocols]** → [Validation Testing](./validation-testing.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Testing Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔗 Source Code**: [FLX Testing](../../../flx/src/flx/testing/)
- **🔗 Related**: [Validation Testing](./validation-testing.md), [Emergency Protocols](./emergency-protocols.md)

---

## 📋 **Overview**

Complete verification procedures for system state assessment and validation.

## 🚨 MANDATORY PRE-WORK VALIDATION PROTOCOL

**COPY EXACTLY, NO MODIFICATIONS:**

```bash
# === CATASTROPHIC FAILURE PREVENTION CHECK ===
echo "=== CLAUDE.md v5.0 FAILURE-PREVENTION STARTING ==="
cd /home/marlonsc/pyauto

# STEP 1: READ THE FUCKING TOKEN CONTEXT (Agent keeps ignoring this)
echo "=== CONTEXT ANALYSIS (Agent must actually read this) ==="
echo "Last 20 token entries (AGENT: READ THESE CAREFULLY):"
cat .token | tail -20
echo ""
echo "KEY INDICATORS TO LOOK FOR:"
echo "- 'COMPLETED', 'POST-REFACTOR-COMPLETION' = System working, don't create problems"
echo "- 'BROKEN', 'CRITICAL' = Real issues need attention"
echo "- 'MyPy ZERO ERRORS' = Type system is clean"
echo ""

# STEP 2: UNDERSTAND PROJECT STRUCTURE (Agent keeps fucking this up)
echo "=== PROJECT STRUCTURE VERIFICATION ==="
echo "Available projects:"
ls -1 | grep -E '^flx' | head -10
echo ""
echo "Source code locations:"
find . -name "src" -type d | head -5
echo ""

# STEP 3: TEST IMPORTS WITH CORRECT PATHS (Agent's biggest failure)
echo "=== IMPORT TESTING WITH CORRECT PATHS ==="
echo "Testing FLX Core (src in subdirectory)..."
python -c "import sys; sys.path.insert(0, 'flx/src'); import flx; print('✅ FLX Core OK')" 2>/dev/null || echo "❌ FLX BROKEN"

echo "Testing Oracle adapters (separate projects)..."
python -c "import sys; sys.path.insert(0, 'flx-database-oracle/src'); import flx_database_oracle; print('✅ DB Oracle OK')" 2>/dev/null || echo "❌ DB BROKEN"
python -c "import sys; sys.path.insert(0, 'flx-http-oracle-oic/src'); import flx_http_oracle_oic; print('✅ OIC OK')" 2>/dev/null || echo "❌ OIC BROKEN"
python -c "import sys; sys.path.insert(0, 'flx-http-oracle-wms/src'); import flx_http_oracle_wms; print('✅ WMS OK')" 2>/dev/null || echo "❌ WMS BROKEN"

# STEP 4: REALITY CHECK BEFORE DECLARING FAILURE
echo "=== REALITY CHECK SECTION ==="
echo "If ALL imports failed -> You probably have wrong paths, not broken system"
echo "If token shows 'COMPLETED' -> System is probably working fine"
echo "If token shows 'POST-REFACTOR-COMPLETION' -> Refactor succeeded, don't break it"

# STEP 5: BUILD SYSTEM CHECK
echo "=== BUILD SYSTEM CHECK ==="
ls scripts/common.sh >/dev/null 2>&1 && echo "✅ BUILD SYSTEM OK" || echo "❌ BUILD SYSTEM BROKEN"
make --version >/dev/null 2>&1 && echo "✅ MAKE AVAILABLE" || echo "❌ MAKE MISSING"

echo "=== FAILURE-PREVENTION CHECK COMPLETE ==="
echo "AGENT: Read the output above CAREFULLY before making any conclusions"
```

## 📊 CLASSIFICATION MATRIX

- **✅ All systems OK** = Normal work (proceed with tasks)
- **❌ 1-2 components broken** = Component repair mode (2-4 hours)
- **❌ 3+ broken OR build system down** = **EMERGENCY RESTORATION** (8-20 hours)
- **❌ FLX Core broken** = **CRITICAL SYSTEM FAILURE** (immediate action required)

## 🔧 COMPREHENSIVE SYSTEM ASSESSMENT

**MANDATORY before any technical work:**

```bash
echo "=== SYSTEMATIC ASSESSMENT STARTING ==="

# Test all core imports
python -c "import flx; print('✅ FLX Core')" || echo "❌ FLX BROKEN"
python -c "import flx.application.bootstrap; print('✅ Bootstrap')" || echo "❌ Bootstrap BROKEN"
python -c "import flx.adapters.outbound.cache; print('✅ Cache')" || echo "❌ Cache BROKEN"

# Test build system thoroughly
make lint 2>&1 | grep -E "(error|Error|ERROR)" | wc -l && echo "Lint errors detected"
make test 2>&1 | grep -E "(FAILED|failed)" | wc -l && echo "Test failures detected"

# Test quality gates
ruff check flx/src/ --select=F8 2>/dev/null | wc -l && echo "F8xx errors count"
mypy flx/src/ 2>/dev/null | grep -c "error:" && echo "MyPy errors count"

echo "=== ASSESSMENT COMPLETE ==="
```

## 📋 COMPLETION VALIDATION CHECKLIST

**MANDATORY before claiming ANY task complete:**

```bash
# MANDATORY before claiming ANY task complete
echo "=== COMPLETION VALIDATION ==="

# 1. All imports work
python -c "import flx; import flx_database_oracle; import flx_http_oracle_oic; import flx_http_oracle_wms; print('✅ All imports OK')" || { echo "❌ IMPORTS BROKEN - TASK NOT COMPLETE"; exit 1; }

# 2. Build system works
make lint >/dev/null 2>&1 && echo "✅ Lint OK" || { echo "❌ LINT BROKEN - TASK NOT COMPLETE"; exit 1; }

# 3. No critical errors
[[ $(ruff check flx/src/ --select=F8 2>/dev/null | wc -l) -eq 0 ]] && echo "✅ No F8xx errors" || echo "⚠️ F8xx errors remain"

echo "=== VALIDATION COMPLETE - TASK COMPLETION AUTHORIZED ==="
```

## 🔍 QUALITY GATES VALIDATION

```bash
# Gate 1: All imports work
python -c "
import flx
import flx_database_oracle
import flx_http_oracle_oic
import flx_http_oracle_wms
import flx_adapter_example
print('✅ ALL IMPORTS WORKING')
"

# Gate 2: Build system works
make lint > /dev/null 2>&1 && echo "✅ BUILD SYSTEM OK" || echo "❌ BUILD BROKEN"

# Gate 3: No critical errors in production code
ruff check src/ --select=F,E9 | wc -l | grep -q "^0$" && echo "✅ NO CRITICAL ERRORS" || echo "❌ ERRORS EXIST"

# Gate 4: Core functionality test
python -c "
from flx.adapters.base import BaseAdapter
from flx.core.domain.exceptions import HttpError
print('✅ CORE CLASSES ACCESSIBLE')
"
```

## 🚨 CONTEXT DIRECTORY VERIFICATION MANDATORY

**BEFORE any system functionality claims:**

```bash
# BEFORE any system functionality claims
pwd && echo "Working directory: $(pwd)"
ls -la | head -10 && echo "Directory contents verified"
```

**FORBIDDEN**: Any technical assessment without explicit directory verification

## 📊 COMPLETE ERROR ENUMERATION REQUIRED

**NEVER estimate from samples - get complete counts:**

```bash
# NEVER estimate from samples - get complete counts
python -m mypy --strict src/ 2>&1 | grep "error:" | wc -l
# NOT: First 10 errors → "roughly 6 remaining"
```

## 🔧 INFRASTRUCTURE FUNCTIONAL TESTING PROTOCOL

```bash
# Testing infrastructure verification
python -m pytest tests/ --collect-only | grep "collected"
python -m pytest tests/unit/core/test_base.py -v | head -5

# Build system verification
make -n lint && echo "✅ Lint target exists"
make -n type-check && echo "✅ Type check target exists"
```

## 📋 TOKEN EVIDENCE TRAIL VALIDATION

**BEFORE any "system broken" claims:**

```bash
# BEFORE any "system broken" claims
cat .token | tail -20 | grep -E "(✅|WORKING|SUCCESS|COMPLETED)"
```

**FORBIDDEN**: Failure assessments that contradict existing evidence trail

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Testing Overview](./index.md) - Understanding testing frameworks and strategies
- [Development Environment](../setup/environment.md) - Proper development environment setup
- [Getting Started](../../getting-started/index.md) - FLX Framework installation and configuration

### **Next Steps**

- [Validation Testing](./validation-testing.md) - Comprehensive validation testing strategies
- [Emergency Protocols](./emergency-protocols.md) - Emergency system restoration procedures
- [Integration Testing](./integration-testing.md) - Integration testing methodologies

### **Related Topics**

- [Failure Analysis](./failure-cases.md) - Learning from past failures and prevention
- [Performance Testing](./performance-testing.md) - Performance validation procedures
- [Code Quality](../standards/code-quality.md) - Code quality assessment standards

---

## 🆘 **Troubleshooting**

### **Common Issues**

For assessment protocol issues:

1. Check all import paths are correct before declaring failures
2. Verify environment variables and configuration
3. Review token evidence trail for existing state
4. Validate build system functionality

### **Additional Resources**

- [Testing Examples](../../examples/testing/index.md) - Working testing examples and scripts
- [Development Hub](../index.md) - Complete development tools documentation
- [Architecture Testing](../../architecture/testing/index.md) - Architecture validation testing

---

**📂 Hub**: [Testing Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-19

## 🎯 POST-HEAVY-REFACTOR MANDATORY CHECKLIST

**BEFORE claiming refactor completion:**

- [ ] **Import Test**: All core modules import without errors
- [ ] **Build Test**: `make lint` runs without build system errors
- [ ] **Core Test**: pytest collects 1000+ tests without collection errors
- [ ] **Pass Rate**: >60% of tests passing (not just "some tests work")
- [ ] **Error Count**: <100 error-level test failures
- [ ] **Adapter Test**: All adapters initialize and have required methods
- [ ] **Integration Test**: Bootstrap and DI container function properly
- [ ] **Honest Report**: Actual numbers in .token, not optimistic estimates

**FAILURE OF ANY ITEM = REFACTOR NOT COMPLETE**

## 🔄 EVIDENCE-BASED COMPLETION CLAIMS ONLY

**ALL must pass before completion claims:**

```bash
# ALL must pass before completion claims
make lint               # No linting errors
make type-check         # No type errors
make test              # All tests passing
python -c "import MAIN_MODULE"  # Core functionality verified
```

**FORBIDDEN**: Completion claims based on partial fixes or optimistic estimates
