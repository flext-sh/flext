---
name: flext-mro-namespace-rules
description: 'Use this skill to canonical MRO namespace rules for facade naming, organic
  nested-domain access, and same-project import boundaries. Use when editing `constants.py`,
  `models.py`, `protocols.py`, `typings.py`, `utilities.py`, `tests/`, or any `models/`
  and `_utilities/` mixin tree. DO NOT USE FOR: questions unrelated to flext-mro-namespace-rules
  creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# Flext MRO Namespace Rules

**UTILITY SKILL**

## USE FOR

- Requests about flext mro namespace rules.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to flext-mro-namespace-rules.
- creating projects or architecture from scratch.

## Workflow

1. Identify the public facade and its single local namespace root.
2. Split multi-responsibility implementations into the facade's matching private domain package.
3. Purge flat nested wrapper classes that only restate a private mixin.
4. Rename legacy test facades to `TestsFlext<Project><Tier>` and update consumers.

## Critical rules

- Prefer canonical sources.
- Owner facade modules extend upstream `c`, `t`, `p`, `m`, or `u` using the upstream short alias as the MRO base and then publish the local alias exactly once at module bottom.
- Project `base.py` extends upstream runtime `s` plus private MRO mixins and then publishes local `s`; project `api.py` extends the composed runtime facade and publishes the operational alias.
<!-- mro-wkii.17.26 (agent: codex) — bind MRO composition to one thin domain facade and private focused parts. -->
- A domain's public/composition module is a thin facade only. It composes
  focused mixins from its matching private `_<domain>/` package and owns the
  sole public import path. External imports of private parts, lazy private
  initializers, `__unit__.py`, forwarding aliases, and parallel old/new module
  paths are defects removed atomically with all consumers.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
