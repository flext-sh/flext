# MyPy and Type Safety - Development Standards

> **Function**: Complete guide for type checking best practices and systematic error resolution | **Audience**: Developers, QA engineers | **Status**: ✅ VALIDATED

[![Standards](https://img.shields.io/badge/standards-type--safety-blue.svg)](./index.md)
[![MyPy](https://img.shields.io/badge/mypy-validation-orange.svg)](../testing/validation-testing.md)
[![Framework](https://img.shields.io/badge/framework-FLEXT%200.4.0-green.svg)](../../index.md)

**Complete guide for type checking best practices and systematic error resolution using MyPy**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Development](../index.md) → **📂 Standards**: [Development Standards](./index.md) → **📄 Current**: Type Safety

### **📍 Learning Path Position**

```
[Coding Standards](./coding-standards.md) → **[Type Safety]** → [Code Quality](./code-quality.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Development Standards](./index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔗 Source Code**: [FLEXT Type Safety](../../../flext/src/flext/core/types/)
- **🔗 Related**: [Testing Standards](../testing/index.md), [Code Quality](./code-quality.md)

---

## 📋 **Overview**

Complete guide for type checking best practices and systematic error resolution.

## 🎯 CRITICAL: Complete Analysis Before Action

**NEVER start fixing errors without understanding the full picture:**

```bash
# ❌ WRONG: Jump into fixes
mypy --ignore-missing-imports src/ | head -20
# Start fixing random errors...

# ✅ CORRECT: Full analysis first
# 1. Get complete error count and categories
mypy --ignore-missing-imports src/ 2>&1 > mypy_full_report.txt
echo "Total mypy errors: $(grep "error:" mypy_full_report.txt | wc -l)"
grep -o "\[.*\]" mypy_full_report.txt | sort | uniq -c | sort -nr

# 2. Analyze linting issues separately
ruff check src/ --statistics
ruff check src/ --select=C901 | grep "^src/" | wc -l  # Complexity count

# 3. Create action plan BEFORE coding
echo "ANALYSIS COMPLETE: X mypy errors, Y linting issues" >> .token
echo "STRATEGY: Fix import errors first, then type annotations" >> .token
```

## 📊 MYPY ERROR CATEGORIES AND SOLUTIONS

### 1. Unfollowed Import Errors

```python
# These indicate architectural issues, not quick fixes
# "Argument becomes Any due to an unfollowed import"

# ❌ WRONG: Create types.py with aliases
# ❌ WRONG: Use TYPE_CHECKING everywhere
# ❌ WRONG: Suppress with type: ignore

# ✅ CORRECT: Understand WHY imports are unfollowed
# - Circular dependencies?
# - Missing type stubs?
# - Conditional imports?
```

### 2. Missing Type Annotations

```python
# ❌ WRONG: Add Any everywhere
def process(data) -> Any:  # Lazy!

# ✅ CORRECT: Add proper types
def process(data: dict[str, str]) -> list[ProcessResult]:
```

### 3. Incompatible Types

```python
# ❌ WRONG: Cast to silence error
result = cast(str, some_function())  # Hiding the problem

# ✅ CORRECT: Fix the actual type mismatch
# Understand what type is expected and why
```

## 🏗️ IMPORT ARCHITECTURE BEST PRACTICES

**Avoiding Unfollowed Import Hell:**

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

## 📈 TYPE CHECKING STRATEGY ORDER

1. **Fix syntax errors first** (undefined names, imports)
2. **Add missing annotations** (parameters, return types)
3. **Fix type incompatibilities** (wrong types being passed)
4. **Handle complex inference** (nested dicts, generics)
5. **Address architectural issues** (unfollowed imports) - LAST

## ⚠️ COMPLEXITY WARNINGS (C901) - ARCHITECTURAL DEBT

**REALITY CHECK**: C901 warnings indicate functions doing too much

```python
# These require REFACTORING, not quick fixes:
# - Split into smaller functions
# - Extract complex logic to separate methods
# - Use strategy pattern for multiple conditions

# Document for future work:
echo "TECH DEBT: 14 C901 complexity warnings require refactoring" >> .token
echo "ESTIMATE: 2-4 hours per function to properly refactor" >> .token
```

## 🔍 COMMON PITFALLS TO AVOID

### 1. Creating "helper" files without checking patterns

- Check if similar solutions exist first
- Follow project conventions

### 2. Partial type annotations

```python
# ❌ WRONG: Annotate some but not all
def process(data) -> str:  # Missing param type

# ✅ CORRECT: Complete annotations
def process(data: dict[str, Any]) -> str:
```

### 3. Ignoring root causes

- Unfollowed imports = architectural issue
- Multiple similar errors = pattern to fix systematically
- Complexity warnings = technical debt, not quick fixes

## 📋 VALIDATION AFTER TYPE FIXES

```bash
# MANDATORY validation sequence:
# 1. Check reduction in errors
mypy --ignore-missing-imports src/ 2>&1 | grep "error:" | wc -l

# 2. Verify no new issues introduced
ruff check src/ --select=F,E9  # Critical errors only

# 3. Document exactly what was fixed
echo "FIXED: 132 mypy errors -> 96 (27% reduction)" >> .token
echo "METHOD: Added type annotations, fixed inference issues" >> .token
echo "REMAINING: Unfollowed imports need architectural review" >> .token
```

## 🎯 HONEST PROGRESS REPORTING

**MANDATORY: Report exact numbers, not approximations**

```bash
# After each significant change:
echo "PROGRESS: Reduced mypy errors from 228 to 96 (58% reduction)" >> .token
echo "REMAINING: 96 errors - mostly unfollowed imports from ldap3" >> .token
echo "COMPLEXITY: 14 C901 warnings (not 7 as initially reported)" >> .token
```

## 🚨 SYSTEMATIC MYPY ERROR REDUCTION PROTOCOL

### Phase 1: Error Analysis and Categorization

```bash
# Get complete error count
mypy --strict src/ 2>&1 | grep "error:" | wc -l

# Categorize errors by type
mypy --strict src/ 2>&1 | grep -o "\[.*\]" | sort | uniq -c | sort -nr

# Common categories:
# [attr-defined] - Missing attributes/methods
# [call-arg] - Function call argument issues
# [return-value] - Return type mismatches
# [no-untyped-def] - Missing function annotations
# [no-any-return] - Functions returning Any
```

### Phase 2: Systematic Fixes by Category

**Priority Order (highest impact first):**

1. **[attr-defined]** - Missing methods/attributes
2. **[call-arg]** - Function argument mismatches
3. **[return-value]** - Return type issues
4. **[no-untyped-def]** - Missing annotations

### Phase 3: Architectural Issues

Handle unfollowed imports and complex inference last, as these often require larger changes.

## 🔧 PYDANTIC 2.11+ COMPATIBILITY

**Common Issues and Solutions:**

```python
# FORBIDDEN:
@dataclass
class SampleCommand(Command):
    name: str
    value: int

# REQUIRED:
class SampleCommand(Command):
    name: str = Field(...)
    value: int = Field(...)
```

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Development Standards](./index.md) - Understanding development standards and patterns
- [Coding Standards](./coding-standards.md) - Code style and quality guidelines
- [Getting Started](../../getting-started/index.md) - FLEXT Framework installation and setup

### **Next Steps**

- [Code Quality](./code-quality.md) - Code quality assessment and improvement
- [Testing Standards](../testing/index.md) - Testing strategies and type safety
- [API Reference](../../api-reference/index.md) - Type-safe API documentation

### **Related Topics**

- [Validation Testing](../testing/validation-testing.md) - Type validation in testing
- [Architecture Patterns](../../architecture/patterns/index.md) - Type-safe architecture patterns
- [Performance Standards](./performance-standards.md) - Type safety impact on performance

---

## 🆘 **Troubleshooting**

### **Common Issues**

For type safety issues:

1. Start with complete analysis before fixing individual errors
2. Focus on import and annotation errors first
3. Use proper Pydantic 2.11+ patterns for models
4. Avoid type: ignore unless absolutely necessary

### **Additional Resources**

- [MyPy Documentation](https://mypy.readthedocs.io/) - Official MyPy documentation
- [Type Safety Examples](../../examples/type-safety/index.md) - Working type safety examples
- [Development Hub](../index.md) - Complete development tools documentation

---

**📂 Hub**: [Development Standards](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLEXT 0.4.0+ | **Updated**: 2025-06-19

## 📊 REAL-WORLD SYSTEMATIC RESULTS

**Example of proper systematic approach:**

- **Initial**: 3704 MyPy errors
- **Phase 1** (attr-defined): 3704 → 3365 (-339 errors, 9.2%)
- **Phase 2** (call-arg): 3365 → 3214 (-151 errors, 4.4%)
- **Total**: 490 errors fixed (13.2% reduction)

**Key Success Factors:**

1. Complete enumeration before starting
2. Category-based systematic approach
3. Fix highest-impact categories first
4. Validate after each phase
5. Document exact progress

## ⚡ REMEMBER

- **Complete analysis before action** - No random fixes
- **Systematic approach** - Fix by category, not randomly
- **Architectural awareness** - Some errors indicate deeper issues
- **Honest reporting** - Exact numbers, realistic timelines
- **Validation always** - Test after each significant change

---

_Type safety is fundamental to PyAuto's enterprise-grade reliability. Follow these protocols systematically for consistent results._
