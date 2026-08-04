# result-parts-error

## Overview

Community of 28 nodes

- **Size**: 28 nodes
- **Cohesion**: 0.9143
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
| ------ | ------ | ------ | ------- |
| Result | Class | flext-core/src/flext_core/_protocols/result.py | 32-182 |
| error | Function | flext-core/src/flext_core/_protocols/result.py | 43-43 |
| error_code | Function | flext-core/src/flext_core/_protocols/result.py | 47-47 |
| error_data | Function | flext-core/src/flext_core/_protocols/result.py | 51-51 |
| success | Function | flext-core/src/flext_core/_protocols/result.py | 55-55 |
| exception | Function | flext-core/src/flext_core/_protocols/result.py | 59-59 |
| failure | Function | flext-core/src/flext_core/_protocols/result.py | 63-63 |
| value | Function | flext-core/src/flext_core/_protocols/result.py | 67-67 |
| **enter** | Function | flext-core/src/flext_core/_protocols/result.py | 70-70 |
| **exit** | Function | flext-core/src/flext_core/_protocols/result.py | 73-78 |
| **or** | Function | flext-core/src/flext_core/_protocols/result.py | 87-87 |
| unwrap | Function | flext-core/src/flext_core/_protocols/result.py | 90-90 |
| unwrap_or | Function | flext-core/src/flext_core/_protocols/result.py | 93-93 |
| unwrap_or_else | Function | flext-core/src/flext_core/_protocols/result.py | 96-96 |
| flat_map | Function | flext-core/src/flext_core/_protocols/result.py | 99-102 |
| fold | Function | flext-core/src/flext_core/_protocols/result.py | 105-109 |
| lash | Function | flext-core/src/flext_core/_protocols/result.py | 112-115 |
| map | Function | flext-core/src/flext_core/_protocols/result.py | 118-121 |
| flow_through | Function | flext-core/src/flext_core/_protocols/result.py | 124-127 |
| map_error | Function | flext-core/src/flext_core/_protocols/result.py | 130-133 |
| map_or | Function | flext-core/src/flext_core/_protocols/result.py | 143-147 |
| tap | Function | flext-core/src/flext_core/_protocols/result.py | 150-153 |
| tap_error | Function | flext-core/src/flext_core/_protocols/result.py | 156-156 |
| filter | Function | flext-core/src/flext_core/_protocols/result.py | 159-162 |
| recover | Function | flext-core/src/flext_core/_protocols/result.py | 165-168 |
| to_model | Function | flext-core/src/flext_core/_protocols/result.py | 171-174 |
| **bool** | Function | flext-core/src/flext_core/_protocols/result.py | 177-177 |
| **repr** | Function | flext-core/src/flext_core/_protocols/result.py | 180-182 |

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `ABC` (1 edge(s))
- `type` (1 edge(s))

### Incoming

- `flext-core/src/flext_core/_protocols/result.py` (protocol surface)
- `flext-core/src/flext_core/_result/construction.py` (factories / redaction)
- `flext-core/src/flext_core/_result/transforms.py` (combinators)
