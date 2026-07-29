# api-cases-auth

## Overview

Community of 308 nodes

- **Size**: 308 nodes
- **Cohesion**: 0.2687
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
| ------ | ------ | ------ | ------- |
| _emit | Function | flext-observability/examples/01_functional.py | 24-26 |
| _emit | Function | flext-observability/examples/02_solid_observability_demo.py | 30-32 |
| formatters_print | Function | flext-cli/src/flext_cli/_utilities/formatters.py | 33-35 |
| FlextAuthAdvancedFeaturesExample | Class | flext-auth/examples/advanced_features_02.py | 20-162 |
| example_advanced_configuration | Function | flext-auth/examples/advanced_features_02.py | 26-30 |
| example_jwt_operations | Function | flext-auth/examples/advanced_features_02.py | 33-50 |
| example_role_based_access | Function | flext-auth/examples/advanced_features_02.py | 53-75 |
| example_session_management | Function | flext-auth/examples/advanced_features_02.py | 78-92 |
| example_password_security | Function | flext-auth/examples/advanced_features_02.py | 95-114 |
| example_token_validation | Function | flext-auth/examples/advanced_features_02.py | 117-141 |
| basic_example_runner | Function | flext-auth/examples/advanced_features_02.py | 150-151 |
| main | Function | flext-auth/examples/advanced_features_02.py | 154-162 |
| _emit | Function | flext-auth/examples/basic_auth_05.py | 12-14 |
| FlextAuthBasicAuthExample | Class | flext-auth/examples/basic_auth_05.py | 17-44 |
| main | Function | flext-auth/examples/basic_auth_05.py | 21-44 |
| _emit | Function | flext-auth/examples/basic_refactored_usage_06.py | 21-23 |
| FlextAuthDemo | Class | flext-auth/examples/basic_refactored_usage_06.py | 26-150 |
| **init** | Function | flext-auth/examples/basic_refactored_usage_06.py | 29-32 |
| demo_user_authentication | Function | flext-auth/examples/basic_refactored_usage_06.py | 34-45 |
| demo_user_registration | Function | flext-auth/examples/basic_refactored_usage_06.py | 47-59 |
| _print_token_info | Function | flext-auth/examples/basic_refactored_usage_06.py | 61-64 |
| demo_password_utilities | Function | flext-auth/examples/basic_refactored_usage_06.py | 66-79 |
| demo_secure_password_generation | Function | flext-auth/examples/basic_refactored_usage_06.py | 82-98 |
| demo_email_validation | Function | flext-auth/examples/basic_refactored_usage_06.py | 101-117 |
| validate_email_manual | Function | flext-auth/examples/basic_refactored_usage_06.py | 105-114 |
| demo_jwt_operations | Function | flext-auth/examples/basic_refactored_usage_06.py | 119-132 |
| main | Function | flext-auth/examples/basic_refactored_usage_06.py | 135-150 |
| FlextAuthBasicUsageExample | Class | flext-auth/examples/basic_usage_01.py | 10-43 |
| _run_examples | Function | flext-auth/examples/basic_usage_01.py | 19-30 |
| main | Function | flext-auth/examples/basic_usage_01.py | 33-43 |
| FlextAuthBasicUsagePortugueseExample | Class | flext-auth/examples/basic_usage_07.py | 12-32 |
| exemplo_flext_auth | Function | flext-auth/examples/basic_usage_07.py | 16-32 |
| FlextAuthBasicUsageFlows | Class | flext-auth/examples/basic_usage_flows.py | 10-154 |
| example_basic_authentication | Function | flext-auth/examples/basic_usage_flows.py | 16-27 |
| example_password_operations | Function | flext-auth/examples/basic_usage_flows.py | 30-34 |
| example_user_lifecycle | Function | flext-auth/examples/basic_usage_flows.py | 75-129 |
| example_direct_auth | Function | flext-auth/examples/basic_usage_flows.py | 132-154 |
| FlextAuthBasicUsageWorkflow | Class | flext-auth/examples/basic_usage_workflow.py | 12-109 |
| example_advanced_registration | Function | flext-auth/examples/basic_usage_workflow.py | 18-61 |
| example_complete_workflow | Function | flext-auth/examples/basic_usage_workflow.py | 64-101 |
| FlextAuthComprehensiveDemo | Class | flext-auth/examples/comprehensive_demo_03.py | 25-148 |
| demo_complete_auth_workflow | Function | flext-auth/examples/comprehensive_demo_03.py | 29-52 |
| demo_password_operations | Function | flext-auth/examples/comprehensive_demo_03.py | 55-69 |
| demo_jwt_operations | Function | flext-auth/examples/comprehensive_demo_03.py | 72-86 |
| demo_user_management | Function | flext-auth/examples/comprehensive_demo_03.py | 89-108 |
| demo_security_features | Function | flext-auth/examples/comprehensive_demo_03.py | 111-117 |
| demo_error_handling | Function | flext-auth/examples/comprehensive_demo_03.py | 120-126 |
| basic_example_runner | Function | flext-auth/examples/comprehensive_demo_03.py | 135-136 |
| main | Function | flext-auth/examples/comprehensive_demo_03.py | 139-148 |
| FlextAuthDebugIssuesExample | Class | flext-auth/examples/debug_auth_issues_09.py | 15-74 |

*... and 258 more members.*

## Execution Flows

- **main** (criticality: 0.90, depth: 4)
- **main** (criticality: 0.85, depth: 9)
- **main** (criticality: 0.85, depth: 12)
- **main** (criticality: 0.84, depth: 12)
- **main** (criticality: 0.83, depth: 14)
- **main** (criticality: 0.83, depth: 12)
- **main** (criticality: 0.82, depth: 11)
- **authenticate_user** (criticality: 0.81, depth: 9)
- **main** (criticality: 0.80, depth: 5)
- **authenticate** (criticality: 0.78, depth: 9)
- *... and 21 more flows.*

## Dependencies

### Outgoing

- `that` (270 edge(s))
- `register_user` (99 edge(s))
- `str` (57 edge(s))
- `authenticate_user` (45 edge(s))
- `info` (37 edge(s))
- `ok` (32 edge(s))
- `fail` (31 edge(s))
- `validate_token` (24 edge(s))
- `get` (20 edge(s))
- `isinstance` (19 edge(s))
- `getenv` (17 edge(s))
- `lower` (15 edge(s))
- `len` (11 edge(s))
- `error` (11 edge(s))
- `fetch_logger` (11 edge(s))

### Incoming

- `that` (270 edge(s))
- `register_user` (72 edge(s))
- `FlextAuth` (63 edge(s))
- `str` (43 edge(s))
- `quick_start` (38 edge(s))
- `authenticate_user` (30 edge(s))
- `create_token` (23 edge(s))
- `lower` (14 edge(s))
- `get_user_by_username` (12 edge(s))
- `ok` (12 edge(s))
- `validate_token` (11 edge(s))
- `isinstance` (11 edge(s))
- `get_active_sessions` (10 edge(s))
- `end_session_by_id` (7 edge(s))
- `create_test_auth_data` (7 edge(s))
