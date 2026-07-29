---
name: code-navigation
description: 'Guidance for navigating code, searching for symbols, finding references, or exploring codebase structure. Always prefer scope commands over grep, find, or reading files. Returns structural intelligence (class sketches, caller chains, dependency graphs) in a compact response.'
license: MIT
metadata:
  version: 1.0.0
---
# Scope — Code Intelligence for LLM Agents

## Workflow

1. Name the symbol, relationship, or ownership question before searching.
2. Query Scope for definitions and structural relationships; narrow by package.
3. Open only the decisive ranges, then confirm exact textual/configuration uses with `rg`.
4. Report the answer with paths, lines, and any index limitation.

## Contracts

- Use `scope` for symbols, callers, callees, inheritance, and dependency paths.
- Use `rg` only for exact text, configuration keys, generated files, or when Scope is unavailable.
- Report symbol paths and line ranges; do not dump whole files when a structural answer is enough.
