# Script Mapping Report - PyAuto Makefile Scripts

## Summary

This report maps the scripts referenced in Makefiles to their actual locations or replacements.

## Missing Scripts and Their Replacements

### 1. **fix_long_lines.py**
- **Referenced in**: `Makefile.lint` (line 204)
- **Current Status**: ❌ MISSING from expected location
- **Found Alternative**: ✅ `scripts/obsolete/fix_long_lines.py`
- **Action Required**: Move from obsolete directory or update Makefile reference

### 2. **generate_full_coverage_report.py**
- **Referenced in**: `Makefile.tests` (line 48)
- **Current Status**: ❌ MISSING from expected location
- **Found Alternative**: ✅ `scripts/analysis/generate_full_coverage_report.py`
- **Action Required**: Update Makefile to use correct path

### 3. **generate_test_templates.py**
- **Referenced in**: `Makefile.tests` (line 94)
- **Current Status**: ❌ MISSING from expected location
- **Found Alternative**: ❌ No direct replacement found
- **Similar Scripts**: 
  - `scripts/utils/temp_script_template.py` (general template, not test-specific)
- **Action Required**: Create new script or remove from Makefile

### 4. **setup_venv.sh**
- **Referenced in**: `Makefile.lint` (line 213, 219, 220)
- **Current Status**: ❌ MISSING from expected location
- **Found Alternative**: ✅ `scripts/utilities/setup_venv.sh`
- **Action Required**: Update references to use utilities subdirectory

### 5. **update_lint_excludes.py**
- **Referenced in**: `Makefile.lint` (line 161)
- **Current Status**: ❌ MISSING from expected location  
- **Found Alternative**: ✅ `scripts/utilities/update_lint_excludes.py`
- **Action Required**: Update Makefile to use correct path

## Existing Scripts (Working Correctly)

### Core Management Scripts
- ✅ `scripts/core/git_manage.py` - Git management operations
- ✅ `scripts/core/project_manage.py` - Project management tasks
- ✅ `scripts/core/scaffold_manage.py` - Scaffold operations

### Utilities
- ✅ `scripts/utilities/sync_dependencies.py` - Dependency synchronization
- ✅ `scripts/utilities/setup_venv.sh` - Virtual environment setup
- ✅ `scripts/utils/script_validation.py` - Script location validation

### Maintenance
- ✅ `scripts/maintenance/cleanup_temp_scripts.py` - Temporary script cleanup

### Runner Scripts
- ✅ `scripts/project_runner.sh` - Project command runner

## Makefile Updates Required

### Makefile.lint
```makefile
# Line 204 - Update path:
@$(PYTHON) $(SCRIPTS_DIR)/obsolete/fix_long_lines.py --exclude=$(EXCLUDE_DIRS) --max-length=$(MAX_LINE_LENGTH); \

# Line 161 - Update path:
@$(PYTHON) $(SCRIPTS_DIR)/utilities/update_lint_excludes.py --input=$(E501_EXCLUDES_FILE) --pyproject=$(WORKSPACE_ROOT)/pyproject.toml

# Lines 213, 219, 220 - Update path:
@bash $(WORKSPACE_ROOT)/scripts/utilities/setup_venv.sh verify || { \
```

### Makefile.tests
```makefile
# Line 48 - Update path:
python scripts/analysis/generate_full_coverage_report.py --workspace . --output reports/coverage

# Line 94 - Either create script or remove:
# Option 1: Remove the target
# Option 2: Create scripts/generate_test_templates.py
```

## Script Organization Issues

1. **Inconsistent Paths**: Some scripts are in root `scripts/`, others in subdirectories
2. **Obsolete Directory**: Contains scripts still referenced by Makefiles
3. **Missing Scripts**: One script (`generate_test_templates.py`) has no replacement

## Recommendations

1. **Move Scripts from Obsolete**:
   ```bash
   mv scripts/obsolete/fix_long_lines.py scripts/maintenance/fixes/
   ```

2. **Create Missing Script**:
   ```bash
   # Create generate_test_templates.py or remove from Makefile
   touch scripts/testing/generate_test_templates.py
   ```

3. **Update All Makefile References**: Use the corrected paths shown above

4. **Standardize Script Organization**:
   - All utility scripts → `scripts/utilities/`
   - All analysis scripts → `scripts/analysis/`
   - All test scripts → `scripts/testing/`
   - All maintenance scripts → `scripts/maintenance/`