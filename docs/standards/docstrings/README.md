# FLEXT Python Docstring Standards

**Approach**: Document based on **why code was built this way**, not generic templates.

This directory contains standards and guidance for writing Python docstrings across the FLEXT monorepo using Google-style PEP 257 conventions, validated against Ruff strict mode (select=["ALL"], preview=true).

## Primary Reference

- **[PEP257-GOOGLE-RUFF.md](./PEP257-GOOGLE-RUFF.md)** — **Main reference** for standards
  - PEP 257 + Google Style + Ruff compliance
  - Copyright placeholder and placement
  - Real examples from FLEXT code
  - Ruff checklist and validation commands

## Supporting Documents

- **[Guidelines](./guidelines.md)** — Comprehensive style reference and patterns
- **[Patterns](./patterns.md)** — Real patterns from codebase analysis
- **[Examples](./examples.md)** — Before/after with actual code from FLEXT
- **[Quick Reference](./quick-ref.md)** — Pre-commit checklist

## Key Principle

**Good docstrings answer:**

1. **Why does this class/method exist?** (domain/responsibility)
2. **How does it differ from similar methods?** (contrast)
3. **What are the constraints or edge cases?** (boundaries)
4. **When will this function fail?** (error conditions)

**Skip docstrings that:**
- Repeat the method name
- Describe implementation details
- Document type hints already clear from signature

## Quick Start

### For Code Review

```bash
# Check which files need docstrings
python3 scripts/validate-docstrings.py <path/to/files>
```

### For Implementation

1. Read the code to understand **WHY** it was built that way
2. Check if similar methods exist—document what makes this one different
3. Add 1-3 sentence docstring explaining the non-obvious part
4. Skip generic documentation on obvious methods

## Tools

**Validation** (identify gaps):
```bash
python3 scripts/validate-docstrings.py flext-core/src
```

**Audit workflow** (guided manual improvement):
```bash
bash scripts/audit-docstrings.sh flext-core/src
```

## Philosophy

Rather than auto-generating docstrings across 2,500+ files:

1. Identify truly confusing code
2. Read it to understand business intent
3. Add minimal, useful documentation
4. Use as template for similar patterns

This maintains docstring **quality and usefulness** instead of quantity.

---

**Table of Contents**

- Guidelines — Full reference
- Patterns — Structural analysis
- Examples — Real before/after
- Quick Reference — Pre-commit checklist
