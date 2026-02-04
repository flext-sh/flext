# Pydantic 2 Migration Plan

## Objective
Migrate the entire Flext monorepo from `TypedDict` and `cast()` usage to **Pydantic 2 BaseModels** and **TypeGuard/isinstance** checks, enforcing the `c, t, p, m, u` architecture.

## Strategy
1.  **Centralize Models**: Move data structures from `typings.py` (`t`) to `models.py` (`m`).
2.  **Convert TypedDict → BaseModel**:
    *   Inherit from `FlextModels.BaseModel` or `FlextModels.BaseConfig`.
    *   Use `ConfigDict` for configuration.
    *   Use `Field` for validation/metadata.
    *   Replace `total=False` with explicit `Optional` / `| None = None`.
3.  **Eliminate `cast()`**:
    *   Use `isinstance()` checks.
    *   Use Pydantic's `model_validate`.
    *   Refactor code to avoid type narrowing via force.
4.  **Verification**:
    *   Run `make check` (includes `ruff` and `basedpyright`).
    *   Run tests.

## Phase 1: flext-auth (Current)
*   [ ] Analyze `flext_auth/typings.py` (24+ TypedDicts).
*   [ ] Move `UserDict`, `SessionDict`, `AuthenticationResponseDict` to `models.py` as Pydantic models.
*   [ ] Move `ProviderConfig`, `OAuth2TokenResponse`, `KerberosTicketData` to `models.py`.
*   [ ] Move `Credentials` nested classes to `models.py`.
*   [ ] Move `Tokens` nested classes to `models.py`.
*   [ ] Update imports across `flext-auth`.
*   [ ] Verify with `make check`.

## Phase 2: Remaining Projects (Prioritized)
1.  **flext-plugin**: 3 `cast()` usages.
2.  **flext-tap-ldap**: 8 `cast()` usages, multiple TypedDicts in `typings.py`?
3.  **flext-target-oracle**: 10 `cast()` usages.

## Execution Log
*   `flext-api`: Verified `Plugin` refactor.
*   `flext-auth`: Started migration of `typings.py`.
