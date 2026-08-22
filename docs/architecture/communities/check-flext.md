# check-flext

<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 3 nodes

- **Size**: 3 nodes
- **Cohesion**: 0.1818
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
| ------ | ------ | ------ | ------- |
| TestFlextInfraCheck | Class | flext-infra/tests/unit/check/init_tests.py | 14-26 |
| test_getattr_raises_attribute_error_for_unknown_symbol | Test | flext-infra/tests/unit/check/init_tests.py | 17-20 |
| test_dir_returns_all_exports | Test | flext-infra/tests/unit/check/init_tests.py | 22-26 |

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `dir` (1 edge(s))
- `that` (1 edge(s))
- `raises` (1 edge(s))
- `getattr` (1 edge(s))

### Incoming

- `flext-infra/tests/unit/check/init_tests.py` (1 edge(s))
- `dir` (1 edge(s))
- `that` (1 edge(s))
- `raises` (1 edge(s))
- `getattr` (1 edge(s))
