# unit-wms


<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 98 nodes

- **Size**: 98 nodes
- **Cohesion**: 0.1713
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| _basic_username | Function | flext-oracle-wms/tests/_factories.py | 19-21 |
| _basic_password | Function | flext-oracle-wms/tests/_factories.py | 24-26 |
| _basic_token | Function | flext-oracle-wms/tests/_factories.py | 29-33 |
| _wms_password | Function | flext-oracle-wms/tests/_factories.py | 41-43 |
| _wms_password_underscore | Function | flext-oracle-wms/tests/_factories.py | 46-48 |
| _test_pass | Function | flext-oracle-wms/tests/_factories.py | 51-53 |
| _custom_password | Function | flext-oracle-wms/tests/_factories.py | 56-58 |
| _short_password | Function | flext-oracle-wms/tests/_factories.py | 61-63 |
| _secret | Function | flext-oracle-wms/tests/_factories.py | 66-68 |
| _oauth_secret | Function | flext-oracle-wms/tests/_factories.py | 71-73 |
| _oauth_secret_dashed | Function | flext-oracle-wms/tests/_factories.py | 76-78 |
| _oauth_secret_456 | Function | flext-oracle-wms/tests/_factories.py | 81-83 |
| _basic_auth_settings | Function | flext-oracle-wms/tests/_factories.py | 101-105 |
| TestsFlextOracleWmsApi | Class | flext-oracle-wms/tests/unit/test_api.py | 17-92 |
| api | Function | flext-oracle-wms/tests/unit/test_api.py | 21-31 |
| test_is_flext_service | Test | flext-oracle-wms/tests/unit/test_api.py | 33-35 |
| test_execute_returns_ready_success | Test | flext-oracle-wms/tests/unit/test_api.py | 37-42 |
| test_execute_is_idempotent | Test | flext-oracle-wms/tests/unit/test_api.py | 44-51 |
| test_api_endpoints_keys_match_canonical_constants | Test | flext-oracle-wms/tests/unit/test_api.py | 53-57 |
| test_api_endpoints_returns_validated_models | Test | flext-oracle-wms/tests/unit/test_api.py | 59-67 |
| test_create_oracle_wms_client_succeeds_from_auth_settings | Test | flext-oracle-wms/tests/unit/test_api.py | 85-92 |
| TestsFlextOracleWmsAuthentication | Class | flext-oracle-wms/tests/unit/test_authentication.py | 27-258 |
| test_auth_method_exposes_wire_value | Test | flext-oracle-wms/tests/unit/test_authentication.py | 41-45 |
| test_auth_method_enumeration_is_complete | Test | flext-oracle-wms/tests/unit/test_authentication.py | 47-52 |
| test_defaults_produce_basic_method_and_documented_values | Test | flext-oracle-wms/tests/unit/test_authentication.py | 56-63 |
| test_basic_settings_retain_supplied_credentials | Test | flext-oracle-wms/tests/unit/test_authentication.py | 65-72 |
| test_oauth2_settings_retain_supplied_credentials | Test | flext-oracle-wms/tests/unit/test_authentication.py | 74-83 |
| test_normalized_method_is_canonical_lowercase | Test | flext-oracle-wms/tests/unit/test_authentication.py | 94-99 |
| test_validate_business_rules_accepts_complete_basic | Test | flext-oracle-wms/tests/unit/test_authentication.py | 103-108 |
| test_validate_business_rules_accepts_complete_oauth2 | Test | flext-oracle-wms/tests/unit/test_authentication.py | 110-115 |
| test_authenticator_behavior_reflects_its_settings | Test | flext-oracle-wms/tests/unit/test_authentication.py | 145-154 |
| test_basic_authenticate_returns_deterministic_token | Test | flext-oracle-wms/tests/unit/test_authentication.py | 156-164 |
| test_basic_authenticate_is_idempotent | Test | flext-oracle-wms/tests/unit/test_authentication.py | 166-174 |
| test_authenticate_failure_carries_reason | Test | flext-oracle-wms/tests/unit/test_authentication.py | 197-204 |
| test_authenticate_rejects_unsupported_method | Test | flext-oracle-wms/tests/unit/test_authentication.py | 206-211 |
| test_basic_headers_carry_basic_authorization | Test | flext-oracle-wms/tests/unit/test_authentication.py | 215-223 |
| test_client_builds_from_valid_basic_settings | Test | flext-oracle-wms/tests/unit/test_authentication.py | 235-242 |
| test_client_rejects_non_basic_method | Test | flext-oracle-wms/tests/unit/test_authentication.py | 251-258 |
| TestsFlextOracleWmsAuthenticationCore | Class | flext-oracle-wms/tests/unit/test_authentication_core.py | 23-261 |
| basic_settings | Function | flext-oracle-wms/tests/unit/test_authentication_core.py | 27-31 |
| test_auth_method_serializes_to_stable_wire_value | Test | flext-oracle-wms/tests/unit/test_authentication_core.py | 44-49 |
| test_defaults_expose_documented_public_state | Test | flext-oracle-wms/tests/unit/test_authentication_core.py | 53-63 |
| test_supplied_credentials_are_retained | Test | flext-oracle-wms/tests/unit/test_authentication_core.py | 65-71 |
| test_oauth2_credentials_are_retained | Test | flext-oracle-wms/tests/unit/test_authentication_core.py | 73-82 |
| test_normalized_method_is_case_and_whitespace_insensitive | Test | flext-oracle-wms/tests/unit/test_authentication_core.py | 85-90 |
| test_validate_business_rules_accepts_complete_oauth2 | Test | flext-oracle-wms/tests/unit/test_authentication_core.py | 102-111 |
| test_authenticator_behavior_reflects_its_settings | Test | flext-oracle-wms/tests/unit/test_authentication_core.py | 146-154 |
| test_authenticate_basic_yields_decodable_credentials | Test | flext-oracle-wms/tests/unit/test_authentication_core.py | 156-165 |
| test_authenticate_is_idempotent | Test | flext-oracle-wms/tests/unit/test_authentication_core.py | 167-176 |
| test_authenticate_failure_carries_specific_error | Test | flext-oracle-wms/tests/unit/test_authentication_core.py | 203-210 |

*... and 48 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `that` (105 edge(s))
- `AuthSettings` (31 edge(s))
- `ok` (30 edge(s))
- `unwrap` (29 edge(s))
- `Client` (19 edge(s))
- `authenticate` (11 edge(s))
- `fail` (11 edge(s))
- `from_auth_settings` (11 edge(s))
- `start` (11 edge(s))
- `Authenticator` (10 edge(s))
- `stop` (9 edge(s))
- `model_validate` (7 edge(s))
- `api_endpoints` (6 edge(s))
- `model_dump` (6 edge(s))
- `create_oracle_wms_client` (3 edge(s))

### Incoming

- `that` (105 edge(s))
- `ok` (30 edge(s))
- `AuthSettings` (29 edge(s))
- `unwrap` (29 edge(s))
- `Client` (18 edge(s))
- `flext-oracle-wms/tests/_factories.py` (13 edge(s))
- `authenticate` (11 edge(s))
- `fail` (11 edge(s))
- `from_auth_settings` (11 edge(s))
- `start` (11 edge(s))
- `Authenticator` (10 edge(s))
- `stop` (9 edge(s))
- `api_endpoints` (6 edge(s))
- `model_dump` (6 edge(s))
- `create_oracle_wms_client` (3 edge(s))
