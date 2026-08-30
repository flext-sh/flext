# FLEXT Python Docstring Standards

<!-- TOC START -->
- [Primary Reference](#primary-reference)
- [Supporting Sections (in the primary reference)](#supporting-sections-in-the-primary-reference)
- [Key Principle](#key-principle)
- [Quick Start](#quick-start)
  - [For Code Review](#for-code-review)
  - [For Implementation](#for-implementation)
- [Tools](#tools)
- [Philosophy](#philosophy)
<!-- TOC END -->

**Approach**: Document based on **why code was built this way**, not generic templates.

This directory contains standards and guidance for writing Python docstrings across
the FLEXT monorepo using Google-style PEP 257 conventions, validated against Ruff
strict mode (select=["ALL"], preview=true).

## Primary Reference

- **[PEP257-GOOGLE-RUFF.md](./PEP257-GOOGLE-RUFF.md)** — **Main reference** for standards
  - PEP 257 + Google Style + Ruff compliance
  - Copyright placeholder and placement
  - Real examples from FLEXT code
  - Ruff checklist and validation commands

## Supporting Sections (in the primary reference)

- **[Guidelines](./PEP257-GOOGLE-RUFF.md#rules)** — Comprehensive style rules per symbol kind
- **[Patterns](./PEP257-GOOGLE-RUFF.md#document-when)** — What to document and what to skip
- **[Examples](./PEP257-GOOGLE-RUFF.md#examples-from-flext-codebase)** — Real before/after from FLEXT code
- **[Quick Reference](./PEP257-GOOGLE-RUFF.md#ruff-compliant-checklist)** — Pre-commit checklist

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
ruff check --select=D,DOC --preview <path/to/files>
```

### For Implementation

1. Read the code to understand **WHY** it was built that way
2. Check if similar methods exist—document what makes this one different
3. Add 1-3 sentence docstring explaining the non-obvious part
4. Skip generic documentation on obvious methods

## Tools

**Validation** (identify gaps):

```bash
ruff check --select=D,DOC --preview flext-core/src
```

**Audit workflow** (guided manual improvement):

```bash
make build WHAT=docs DOCS_PHASE=audit PROJECT=flext-core
```

## Philosophy

Rather than auto-generating docstrings across 2,500+ files:

1. Identify truly confusing code
2. Read it to understand business intent
3. Add minimal, useful documentation
4. Use as template for similar patterns

This maintains docstring **quality and usefulness** instead of quantity.

---

**Table of Contents** (all in [PEP257-GOOGLE-RUFF.md](./PEP257-GOOGLE-RUFF.md))

- Rules — per-symbol style rules (module, class, function, property, exceptions, async)
- Document When — what earns a docstring and what is skipped
- Examples from FLEXT Codebase — real before/after
- Ruff-Compliant Checklist — pre-commit validation
- Ruff Integration — commands and expected ignores
