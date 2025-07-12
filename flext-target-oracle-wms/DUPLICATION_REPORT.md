# ConfigMapper Code Duplication Report

## Executive Summary

After searching across all FLEXT projects, I found that **ConfigMapper is NOT duplicated** across the codebase. There is only one implementation of the `ConfigMapper` class, which exists in:

- `/home/marlonsc/flext/flext-tap-oracle-wms/src/flext_tap_oracle_wms/config_mapper.py`

## Search Results

### ConfigMapper Class Occurrences

- **Found in 1 file only**: `flext-tap-oracle-wms/src/flext_tap_oracle_wms/config_mapper.py`
- **Mentioned in 1 documentation**: `flext-tap-oracle-wms/FLEXT_CORE_MIGRATION_APPLIED.md`

### Similar Configuration Patterns

Other FLEXT projects use different configuration approaches:

1. **flext-core** provides:

   - `BaseConfig` and `BaseSettings` classes for configuration management
   - Dependency injection container
   - Environment variable handling with prefixes
   - Does NOT have a ConfigMapper pattern

2. **Other tap/target projects** use:
   - Direct Pydantic models (e.g., `flext-tap-oracle-oic` uses `SingerTapConfig`)
   - Simple configuration classes without the mapper pattern
   - Environment variable handling through Pydantic's built-in features

## Analysis

### ConfigMapper Unique Features

The `ConfigMapper` in `flext-tap-oracle-wms` provides unique functionality:

1. **Multi-source configuration precedence**: cache > env > profile > default
2. **Profile-based configuration with dot notation paths**
3. **Dynamic configuration mapping for hardcoded values**
4. **Singleton pattern for global instance management**
5. **Type-safe conversions with fallbacks**

### Why It's Not in flext-core

The ConfigMapper appears to be specific to the Oracle WMS tap because:

1. **Domain-specific mappings**: Contains WMS-specific configurations like:

   - WMS API endpoints and versions
   - Oracle WMS field type patterns
   - Allocation and order status mappings
   - Company/facility codes

2. **Profile-based configuration**: This pattern is unique to the WMS tap's need to handle multiple configuration profiles

3. **Hardcoded value externalization**: Specifically designed to make previously hardcoded WMS values configurable

## Recommendation

### DO NOT Centralize ConfigMapper to flext-core

**Reasons:**

1. **Domain-specific logic**: The ConfigMapper contains WMS-specific business logic that doesn't belong in a core library
2. **Not a common pattern**: Only one project uses this pattern; other projects use simpler Pydantic-based configs
3. **flext-core already provides**: Base configuration classes and environment handling that projects can extend
4. **Separation of concerns**: Each tap/target should manage its own configuration mapping logic

### Alternative Approach

If configuration mapping becomes a common need:

1. Create a generic `ConfigMapperMixin` in flext-core with just the core mapping logic
2. Let each project extend it with domain-specific mappings
3. Keep business logic (status mappings, field patterns) in the specific projects

## Conclusion

**No duplication found**. The ConfigMapper is unique to `flext-tap-oracle-wms` and should remain there as it contains WMS-specific business logic and configuration mappings.
