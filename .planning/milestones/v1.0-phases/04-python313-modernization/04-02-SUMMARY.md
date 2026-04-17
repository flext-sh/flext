---
phase: 04-python313-modernization
plan: 02
subsystem: typing
tags: [strenum, unique, literal, enum, pep695]

requires:
  - phase: 04-01
    provides: "PEP 695 type aliases established"
provides:
  - "@unique on all 297 StrEnum classes in src/"
  - "Redundant Literal[str,...] type aliases removed across 17 projects"
  - "New StrEnum classes: Operation, ErrorMode (flext-tests), OICApiVersion (flext-oracle-oic)"
affects: [04-03, typing, models, constants]

tech-stack:
  added: []
  patterns: ["@unique decorator mandatory on all StrEnum", "Use StrEnum type directly instead of Literal alias"]

key-files:
  created: []
  modified:
    - "flext-core/src/flext_core/_constants/cqrs.py"
    - "flext-core/src/flext_core/errors.py"
    - "flext-tests/src/flext_tests/constants.py"
    - "flext-tests/src/flext_tests/files.py"
    - "flext-tests/src/flext_tests/models.py"
    - "flext-observability/src/flext_observability/constants.py"
    - "flext-observability/src/flext_observability/_core.py"
    - "flext-grpc/src/flext_grpc/constants.py"
    - "flext-grpc/src/flext_grpc/models.py"
    - "flext-grpc/src/flext_grpc/services.py"
    - "flext-grpc/src/flext_grpc/protocols.py"
    - "flext-grpc/src/flext_grpc/utilities.py"
    - "flext-grpc/src/flext_grpc/typings.py"
    - "flext-web/src/flext_web/constants.py"
    - "flext-web/src/flext_web/typings.py"
    - "flext-web/src/flext_web/models.py"
    - "flext-api/src/flext_api/constants.py"
    - "flext-cli/src/flext_cli/constants.py"
    - "flext-cli/src/flext_cli/api.py"
    - "flext-quality/src/flext_quality/constants.py"
    - "flext-ldif/src/flext_ldif/constants.py"
    - "flext-ldif/src/flext_ldif/_models/*.py"
    - "flext-ldif/src/flext_ldif/protocols.py"
    - "flext-ldif/src/flext_ldif/servers/*.py"
    - "flext-plugin/src/flext_plugin/typings.py"
    - "flext-db-oracle/src/flext_db_oracle/typings.py"
    - "flext-oracle-oic/src/flext_oracle_oic/settings.py"
    - "flext-oracle-wms/src/flext_oracle_wms/constants.py"
    - "flext-tap-ldap/src/flext_tap_ldap/constants.py"
    - "flext-tap-oracle-wms/src/flext_tap_oracle_wms/constants.py"
    - "flext-dbt-ldap/src/flext_dbt_ldap/constants.py"
    - "flext-meltano/src/flext_meltano/typings.py"
    - "flext-ldap/src/flext_ldap/constants.py"

key-decisions:
  - "Redundant Literal aliases pointing to StrEnum members removed rather than converted"
  - "Frozen _utilities/ files left untouched; 2 Literal aliases kept as type aliases to StrEnum for backward compat"
  - "New StrEnums (Operation, ErrorMode) created in flext-tests constants for values that only had Literals"
  - "OICApiVersion StrEnum created in settings.py replacing inline Literal"
  - "Used StrEnum types directly in Pydantic model fields (StrEnum inherits from str)"

patterns-established:
  - "All StrEnum must have @unique decorator"
  - "Use StrEnum type in annotations instead of Literal[str,...] aliases"
  - "Remove Literals class containers when all aliases are unused"

requirements-completed: [MOD-03, MOD-04]

duration: 22min
completed: 2026-03-24
---

# Phase 04 Plan 02: StrEnum @unique + Literal-to-StrEnum Summary

**@unique enforced on all 297 StrEnum classes; 65+ redundant Literal[str,...] aliases removed/converted across 17 projects**

## Performance

- **Duration:** 22 min
- **Started:** 2026-03-24T18:17:22Z
- **Completed:** 2026-03-24T18:39:44Z
- **Tasks:** 2
- **Files modified:** 35+

## Accomplishments

- All 297 StrEnum classes in src/ now have @unique (5 were missing)
- 65+ Literal[str,...] type aliases removed or replaced with StrEnum references across 17 projects
- 3 new StrEnum classes created (Operation, ErrorMode, OICApiVersion)
- All references to removed Literal aliases updated to use StrEnum types directly

## Task Commits

1. **Task 1: Add @unique to all StrEnum classes** - `make save` (feat)
   - 5 StrEnums fixed: MetricType, FlextErrorDomain, Format, CompareMode, Severity
2. **Task 2: Convert Literal unions to StrEnum** - `make save` (feat)
   - 17 submodules committed + root

## Decisions Made

- Redundant Literal aliases that duplicated StrEnum values were removed entirely (not converted to StrEnum references) since they were mostly unused
- For Literal aliases used in code: replaced with the corresponding StrEnum type directly in annotations
- Frozen `_utilities/*` files untouched; kept 2 Literal aliases as backward-compat type aliases (`AclSubjectTypeLiteral = AclSubjectType`, `AttributeMarkerStatusLiteral = AttributeMarkerStatus`)
- `PluginVariant` and `SingerVersion` in flext-meltano left as str (not enough values or too version-specific to warrant StrEnum)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Created Operation and ErrorMode StrEnums in flext-tests**

- **Found during:** Task 2
- **Issue:** `_OperationLiteral` and `_ErrorModeLiteral` in files.py had no corresponding StrEnum
- **Fix:** Created `@unique class Operation(StrEnum)` and `@unique class ErrorMode(StrEnum)` in flext-tests constants
- **Files modified:** flext-tests/src/flext_tests/constants.py
- **Verification:** ruff check passes

**2. [Rule 2 - Missing Critical] Created OICApiVersion StrEnum in flext-oracle-oic**

- **Found during:** Task 2
- **Issue:** `OICApiVersionLiteral = Literal["v1", "v2"]` used in settings but no StrEnum
- **Fix:** Created `@unique class OICApiVersion(StrEnum)` in settings.py
- **Files modified:** flext-oracle-oic/src/flext_oracle_oic/settings.py

**3. [Rule 2] Converted flext-api ActiveMethods/SafeMethods Literals to frozenset constants**

- **Found during:** Task 2
- **Issue:** `type ActiveMethods = Literal[...]` and `type SafeMethods = Literal[...]` were unused type aliases
- **Fix:** Converted to `ACTIVE_METHODS: Final[frozenset[str]]` and `SAFE_METHODS: Final[frozenset[str]]` for runtime validation
- **Files modified:** flext-api/src/flext_api/constants.py

---

**Total deviations:** 3 auto-fixed (3 missing critical)
**Impact on plan:** All auto-fixes necessary for correctness. No scope creep.

## Issues Encountered

- Pre-existing RUF065 errors in frozen `flext-ldif/src/flext_ldif/_utilities/schema.py` (4 errors) — out of scope, not caused by changes

## Known Stubs

None.

## Next Phase Readiness

- All StrEnum classes have @unique enforcement
- No remaining `type X = Literal[...]` PEP 695 aliases in constants/typings files
- Ready for Phase 04-03 or further typing improvements

---
*Phase: 04-python313-modernization*
*Completed: 2026-03-24*
