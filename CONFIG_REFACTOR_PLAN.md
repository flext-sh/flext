# Configuration Architecture Refactoring Plan

**Date:** 2025-09-23
**Objective:** Implement proper configuration hierarchy with dependency injection across FLEXT ecosystem

---

## 1. Current Architecture Analysis

### Configuration Hierarchy (Current State)

```
BaseSettings (Pydantic v2)
    ├── FlextConfig (flext-core) ✅
    │   ├── env_prefix: "FLEXT_"
    │   └── Uses FlextConstants for defaults
    │
    ├── FlextCliConfig (flext-cli) ❌ BROKEN
    │   ├── Extends BaseSettings directly (WRONG)
    │   ├── env_prefix: "FLEXT_CLI_"
    │   └── Should inherit from FlextConfig
    │
    ├── FlextLdifConfig (flext-ldif) ✅
    │   ├── Extends FlextConfig correctly
    │   └── Uses FlextLdifConstants for defaults
    │
    ├── FlextLdapConfigs (flext-ldap) ✅
    │   ├── Extends FlextConfig correctly
    │   ├── env_prefix: "FLEXT_LDAP_"
    │   └── Uses FlextLdapConstants for defaults
    │
    └── client-aOudMigConfig (client-a-oud-mig) ⚠️ INCOMPLETE
        ├── Extends FlextConfig (correct)
        ├── env_prefix: "client-a_"
        ├── Missing: Config dependency injection
        ├── Issue: Uses os.getenv() instead of Pydantic fields
        └── Issue: No composition with CLI/LDIF/LDAP configs
```

### Issues Identified

1. **FlextCliConfig Inheritance**
   - File: `flext-cli/src/flext_cli/models.py:211`
   - Issue: `class FlextCliConfig(BaseSettings)` should be `class FlextCliConfig(FlextConfig)`
   - Impact: Doesn't inherit core configuration fields

2. **client-aOudMigConfig Composition**
   - File: `client-a-oud-mig/src/client-a_oud_mig/config.py:31`
   - Issue: No dependency injection from domain configs
   - Issue: Direct `os.getenv()` calls bypass Pydantic validation
   - Impact: Configuration priority chain not working properly

3. **Configuration Priority**
   - Required: .env < environment variables < CLI parameters
   - Current: Inconsistent due to os.getenv() usage
   - Solution: Leverage Pydantic BaseSettings built-in priority

---

## 2. Target Architecture

### Desired Configuration Hierarchy

```
BaseSettings (Pydantic v2)
    │
    ├── FlextConfig (Base) ✅
    │   └── Core fields + singleton pattern
    │
    ├── FlextCliConfig (extends FlextConfig) 🔄
    │   └── CLI-specific fields + FlextConfig inheritance
    │
    ├── FlextLdifConfig (extends FlextConfig) ✅
    │   └── LDIF-specific fields
    │
    ├── FlextLdapConfigs (extends FlextConfig) ✅
    │   └── LDAP-specific fields
    │
    └── client-aOudMigConfig (extends FlextConfig + composition) 🔄
        ├── Inherits: FlextConfig base fields
        ├── Composes: FlextCliConfig (injected)
        ├── Composes: FlextLdifConfig (injected)
        ├── Composes: FlextLdapConfigs (injected)
        └── Uses: client-aOudMigConstants for defaults
```

### Configuration Priority Chain

**Pydantic BaseSettings Priority (Automatic):**
```
1. __init__ parameters (highest - CLI arguments)
2. Environment variables (client-a_*, FLEXT_LDAP_*, FLEXT_CLI_*, etc.)
3. .env file values
4. Field defaults from constants (lowest)
```

---

## 3. Implementation Plan

### Phase 1: Fix FlextCliConfig Inheritance

**File:** `flext-cli/src/flext_cli/models.py`

**Changes:**
1. Change base class from `BaseSettings` to `FlextConfig`
2. Remove duplicate fields that exist in FlextConfig
3. Update `model_config` to extend parent config
4. Ensure FlextCliConstants used for CLI-specific defaults
5. Update tests to reflect inheritance

**Before:**
```python
class FlextCliConfig(BaseSettings):
    model_config = ConfigDict(
        env_prefix="FLEXT_CLI_",
        ...
    )
    # Duplicate fields from FlextConfig
    debug: bool = Field(default=False)
    ...
```

**After:**
```python
class FlextCliConfig(FlextConfig):
    model_config = SettingsConfigDict(
        env_prefix="FLEXT_CLI_",
        **FlextConfig.model_config
    )
    # Only CLI-specific fields
    profile: str = Field(default=FlextCliConstants.Defaults.PROFILE)
    ...
```

### Phase 2: Add Config Dependency Injection to client-aOudMigConfig

**File:** `client-a-oud-mig/src/client-a_oud_mig/config.py`

**Changes:**
1. Add optional config injection fields
2. Replace os.getenv() with Pydantic Field defaults
3. Use constants from all domains
4. Add config merging method
5. Update initialization pattern

**Implementation:**
```python
class client-aOudMigConfig(FlextConfig):
    model_config = SettingsConfigDict(
        env_prefix="client-a_",
        **FlextConfig.model_config
    )

    # Injected domain configs (optional, for composition)
    _cli_config: FlextCliConfig | None = None
    _ldif_config: FlextLdifConfig | None = None
    _ldap_config: FlextLdapConfigs | None = None

    # client-a-specific fields using constants
    input_dir: str = Field(
        default=client-aOudMigConstants.Paths.DEFAULT_INPUT_DIR,
        description="Input directory for LDIF files"
    )

    output_dir: str = Field(
        default=client-aOudMigConstants.Paths.DEFAULT_OUTPUT_DIR,
        description="Output directory for processed files"
    )

    batch_size: int = Field(
        default=client-aOudMigConstants.Migration.DEFAULT_BATCH_SIZE,
        ge=1,
        le=client-aOudMigConstants.Migration.MAX_BATCH_SIZE,
        description="Batch size for migration processing"
    )

    # Method to inject configs
    def inject_configs(
        self,
        cli_config: FlextCliConfig | None = None,
        ldif_config: FlextLdifConfig | None = None,
        ldap_config: FlextLdapConfigs | None = None,
    ) -> None:
        self._cli_config = cli_config
        self._ldif_config = ldif_config
        self._ldap_config = ldap_config

    # Access composed values
    def get_effective_log_level(self) -> str:
        # Priority: client-a env > CLI config > FlextConfig
        if self._cli_config:
            return self._cli_config.log_level
        return self.log_level
```

### Phase 3: Remove os.getenv() Calls

**Files to update:**
- `client-a-oud-mig/src/client-a_oud_mig/config.py`

**Changes:**
1. Replace all `os.getenv()` with Pydantic Field declarations
2. Use constants for default values
3. Let Pydantic handle environment variable resolution

**Before:**
```python
def get_client-a_oud_config(self) -> dict[str, str | int | bool]:
    return {
        "host": os.getenv("client-a_OUD_HOST", "localhost"),
        "port": self.oud_port,
        ...
    }
```

**After:**
```python
# Add fields at class level
oud_host: str = Field(
    default=client-aOudMigConstants.OUD.DEFAULT_HOST,
    description="OUD server hostname"
)

def get_client-a_oud_config(self) -> dict[str, str | int | bool]:
    return {
        "host": self.oud_host,  # Pydantic resolves from client-a_OUD_HOST env
        "port": self.oud_port,
        ...
    }
```

### Phase 4: Update Constants

**Files to check:**
- `client-a-oud-mig/src/client-a_oud_mig/constants.py`

**Ensure constants exist for:**
- Paths (DEFAULT_INPUT_DIR, DEFAULT_OUTPUT_DIR)
- Migration (DEFAULT_BATCH_SIZE, MAX_BATCH_SIZE)
- OUD (DEFAULT_HOST, DEFAULT_PORT, DEFAULT_TIMEOUT)

---

## 4. Testing Strategy

### Unit Tests

1. **FlextCliConfig Tests**
   - Test inheritance from FlextConfig
   - Verify CLI-specific fields
   - Test env_prefix resolution

2. **client-aOudMigConfig Tests**
   - Test config injection pattern
   - Verify priority chain: .env < env < init params
   - Test constant defaults
   - Verify composed config access

### Integration Tests

1. **Configuration Priority**
   ```python
   # Test .env file
   # Test environment variables override .env
   # Test CLI params override env vars
   ```

2. **Cross-Domain Configuration**
   ```python
   # Test client-aOudMigConfig with injected CLI config
   # Test client-aOudMigConfig with injected LDIF config
   # Test client-aOudMigConfig with injected LDAP config
   ```

---

## 5. Quality Gates

### Pre-Implementation
- [x] Analyze current architecture
- [x] Identify issues
- [x] Design solution

### During Implementation
- [ ] Fix FlextCliConfig inheritance
- [ ] Add dependency injection to client-aOudMigConfig
- [ ] Remove os.getenv() calls
- [ ] Update constants
- [ ] Run ruff check after each file change

### Post-Implementation
- [ ] Run full quality gate: `ruff check . && mypy . && pyright`
- [ ] Run tests: `pytest -q --cov=src --cov-fail-under=75`
- [ ] Verify configuration priority chain works
- [ ] Update documentation

---

## 6. Migration Guide

### For Users of client-aOudMigConfig

**Before:**
```python
config = client-aOudMigConfig()
# Config values from env only
```

**After:**
```python
# Option 1: Simple usage (same as before)
config = client-aOudMigConfig()

# Option 2: With dependency injection
cli_config = FlextCliConfig()
ldif_config = FlextLdifConfig()
ldap_config = FlextLdapConfigs.get_global_instance()

config = client-aOudMigConfig()
config.inject_configs(
    cli_config=cli_config,
    ldif_config=ldif_config,
    ldap_config=ldap_config
)

# Option 3: With CLI parameter overrides
config = client-aOudMigConfig(
    batch_size=5000,  # Highest priority
    input_dir="/custom/path"
)
```

### Environment Variable Priority

```bash
# .env file (lowest priority)
client-a_BATCH_SIZE=1000

# Environment variable (medium priority)
export client-a_BATCH_SIZE=2000

# CLI parameter (highest priority)
python -m client-a_oud_mig --batch-size 3000
# Result: batch_size = 3000
```

---

## 7. Rollback Plan

If issues arise:
1. Git revert to previous commit
2. Restore FlextCliConfig to BaseSettings inheritance
3. Restore os.getenv() calls in client-aOudMigConfig
4. Run quality gates to ensure stability

---

## 8. Success Criteria

- [ ] FlextCliConfig properly inherits from FlextConfig
- [ ] client-aOudMigConfig has dependency injection for domain configs
- [ ] No direct os.getenv() calls in config classes
- [ ] All configs use constants for defaults
- [ ] Priority chain works: .env < env vars < CLI params
- [ ] All quality gates pass
- [ ] Tests pass with ≥75% coverage
- [ ] Documentation updated

---

## 9. Implementation Checklist

### FlextCliConfig
- [x] Change base class to FlextConfig
- [x] Update model_config
- [x] Remove duplicate fields (kept compatibility fields)
- [x] Verify FlextCliConstants usage
- [x] Run ruff check on flext-cli

### client-aOudMigConfig
- [x] Add config injection fields (implemented via methods)
- [x] Add inject_configs() method
- [x] Replace os.getenv() with Fields
- [x] Use client-aOudMigConstants for defaults
- [x] Update get_*_config() methods
- [x] Run ruff check on client-a-oud-mig

### Constants
- [x] Verify client-aOudMigConstants completeness
- [x] Add missing constants if needed

### Testing
- [x] Update/create config tests
- [x] Test priority chain
- [x] Test dependency injection
- [x] Run full test suite

### Quality Gates
- [x] ruff check .
- [x] mypy .
- [x] pyright
- [ ] pytest with coverage

---

**End of Plan**