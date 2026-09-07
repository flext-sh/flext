# utilities-oracle-engine


<!-- TOC START -->
- [Overview](#overview)
- [Members](#members)
- [Execution Flows](#execution-flows)
- [Dependencies](#dependencies)
  - [Outgoing](#outgoing)
  - [Incoming](#incoming)
<!-- TOC END -->

## Overview

Community of 60 nodes

- **Size**: 60 nodes
- **Cohesion**: 0.0405
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| FlextDbOracleUtilitiesDbOracle | Class | flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py | 30-225 |
| coerced_enum | Function | flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py | 54-64 |
| dispatcher_enabled | Function | flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py | 67-69 |
| validate_identifier | Function | flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py | 72-80 |
| escape_oracle_identifier | Function | flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py | 83-90 |
| format_query_result | Function | flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py | 93-100 |
| format_sql_for_oracle | Function | flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py | 103-106 |
| generate_query_hash | Function | flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py | 109-116 |
| validate_config_map | Function | flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py | 119-126 |
| normalize_params | Function | flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py | 129-133 |
| _parse_rowcount | Function | flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py | 136-145 |
| _parse_count_value | Function | flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py | 148-165 |
| _normalize_singer_type | Function | flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py | 168-174 |
| _sqlalchemy_create_engine | Function | flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py | 177-190 |
| _engine_connect | Function | flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py | 193-195 |
| _engine_begin | Function | flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py | 198-202 |
| _context_exit | Function | flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py | 205-209 |
| _engine_dispose | Function | flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py | 212-214 |
| _connection_execute | Function | flext-db-oracle/src/flext_db_oracle/_utilities/db_oracle.py | 217-225 |
| test_format_query_result_produces_non_empty_string | Test | flext-db-oracle/tests/unit/test_cli.py | 283-293 |
| test_escape_identifier_accepts_valid_names | Test | flext-db-oracle/tests/unit/test_client.py | 59-65 |
| test_escape_identifier_rejects_bad_names | Test | flext-db-oracle/tests/unit/test_client.py | 77-83 |
| test_escape_identifier_truncates_to_max_length | Test | flext-db-oracle/tests/unit/test_client.py | 85-90 |
| test_validate_identifier_accepts_normal_names | Test | flext-db-oracle/tests/unit/test_client.py | 95-99 |
| test_validate_identifier_rejects_empty_and_reserved | Test | flext-db-oracle/tests/unit/test_client.py | 109-115 |
| test_validate_identifier_rejects_too_long | Test | flext-db-oracle/tests/unit/test_client.py | 117-122 |
| test_format_sql_collapses_whitespace | Test | flext-db-oracle/tests/unit/test_client.py | 134-138 |
| test_query_hash_is_short_hex_digest | Test | flext-db-oracle/tests/unit/test_client.py | 142-148 |
| test_query_hash_is_deterministic | Test | flext-db-oracle/tests/unit/test_client.py | 150-154 |
| test_query_hash_varies_with_query | Test | flext-db-oracle/tests/unit/test_client.py | 156-160 |
| test_query_hash_is_order_independent_for_params | Test | flext-db-oracle/tests/unit/test_client.py | 162-166 |
| test_format_result_json_emits_json_text | Test | flext-db-oracle/tests/unit/test_client.py | 170-174 |
| test_format_result_table_emits_string_repr | Test | flext-db-oracle/tests/unit/test_client.py | 176-181 |
| test_normalize_params_returns_empty_map_for_none | Test | flext-db-oracle/tests/unit/test_client.py | 185-188 |
| test_oracle_validation_constants_real_usage | Test | flext-db-oracle/tests/unit/test_constants.py | 443-454 |
| test_oracle_reserved_words_real_validation | Test | flext-db-oracle/tests/unit/test_constants.py | 472-482 |
| test_generate_query_hash_is_deterministic | Test | flext-db-oracle/tests/unit/test_services.py | 395-406 |
| test_generate_query_hash_returns_16_char_alphanumeric | Test | flext-db-oracle/tests/unit/test_utilities.py | 44-52 |
| test_generate_query_hash_is_deterministic_for_same_inputs | Test | flext-db-oracle/tests/unit/test_utilities.py | 54-60 |
| test_generate_query_hash_differs_by_params | Test | flext-db-oracle/tests/unit/test_utilities.py | 62-66 |
| test_generate_query_hash_is_case_sensitive_on_query | Test | flext-db-oracle/tests/unit/test_utilities.py | 68-76 |
| test_generate_query_hash_is_parameter_order_independent | Test | flext-db-oracle/tests/unit/test_utilities.py | 78-88 |
| test_generate_query_hash_accepts_none_params | Test | flext-db-oracle/tests/unit/test_utilities.py | 90-99 |
| test_generate_query_hash_handles_complex_multiline_query | Test | flext-db-oracle/tests/unit/test_utilities.py | 101-113 |
| test_format_sql_collapses_internal_whitespace | Test | flext-db-oracle/tests/unit/test_utilities.py | 119-124 |
| test_format_sql_removes_newlines_and_double_spaces | Test | flext-db-oracle/tests/unit/test_utilities.py | 126-131 |
| test_format_sql_preserves_all_clause_keywords | Test | flext-db-oracle/tests/unit/test_utilities.py | 133-156 |
| test_format_sql_empty_or_blank_yields_empty_string | Test | flext-db-oracle/tests/unit/test_utilities.py | 163-167 |
| test_escape_identifier_returns_valid_identifier_unchanged | Test | flext-db-oracle/tests/unit/test_utilities.py | 177-181 |
| test_escape_identifier_rejects_invalid_input | Test | flext-db-oracle/tests/unit/test_utilities.py | 195-199 |

*... and 10 more members.*

## Execution Flows

No execution flows pass through this community.

## Dependencies

### Outgoing

- `that` (63 edge(s))
- `ok` (37 edge(s))
- `generate_query_hash` (24 edge(s))
- `unwrap` (11 edge(s))
- `escape_oracle_identifier` (9 edge(s))
- `fail` (8 edge(s))
- `len` (8 edge(s))
- `format_query_result` (6 edge(s))
- `format_sql_for_oracle` (6 edge(s))
- `validate_identifier` (6 edge(s))
- `str` (5 edge(s))
- `isinstance` (4 edge(s))
- `int` (3 edge(s))
- `model_validate` (3 edge(s))
- `isalnum` (2 edge(s))

### Incoming

- `that` (63 edge(s))
- `ok` (31 edge(s))
- `generate_query_hash` (24 edge(s))
- `flext-db-oracle/tests/unit/test_utilities.py::TestsFlextDbOracleUtilitiesUnit` (23 edge(s))
- `flext-db-oracle/tests/unit/test_client.py::TestsFlextDbOracleClient` (14 edge(s))
- `unwrap` (11 edge(s))
- `escape_oracle_identifier` (9 edge(s))
- `len` (7 edge(s))
- `format_query_result` (6 edge(s))
- `format_sql_for_oracle` (6 edge(s))
- `validate_identifier` (6 edge(s))
- `str` (3 edge(s))
- `fail` (3 edge(s))
- `bool` (2 edge(s))
- `flext-db-oracle/tests/unit/test_constants.py::TestsFlextDbOracleConstants` (2 edge(s))
