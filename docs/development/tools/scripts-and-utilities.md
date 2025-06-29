# FLX Scripts & Utilities

Comprehensive collection of utility scripts for project maintenance, cleanup, code quality enforcement, and development workflow automation in the FLX hexagonal architecture framework.

## 📖 Overview

This directory contains essential scripts for maintaining the FLX codebase, performing automated refactoring, cleanup operations, and supporting development workflows. These scripts follow the UNIX philosophy of doing one thing well and are designed to be composable, reusable, and production-ready.

## 🛠️ Available Scripts

### 1. Ultra Rigorous Cleanup (`ultra_rigorous_cleanup.py`)

**Purpose**: Zero-tolerance comprehensive codebase cleanup and code quality enforcement.

**Philosophy**: Implements ZERO tolerance for code violations following KISS, DRY, and SOLID principles with ruthless efficiency.

**Key Features:**

- **Code Quality Enforcement**: Removes dead code, unused imports, and redundant patterns
- **Architectural Compliance**: Ensures adherence to hexagonal architecture principles
- **Performance Optimization**: Identifies and removes performance bottlenecks
- **Security Hardening**: Removes potential security vulnerabilities and sensitive data
- **Documentation Sync**: Ensures code and documentation remain synchronized

**Zero Tolerance Areas:**

- MyPy errors and warnings (0 tolerance)
- Ruff violations and style issues (0 tolerance)
- Undefined names and missing imports (0 tolerance)
- Code redundancy and legacy compatibility (0 tolerance)
- Mock implementations (replaced with engines)

**Cleanup Operations:**

#### Phase 1: Ruff Auto-Fixes

```bash
# Applies all auto-fixable Ruff violations including unsafe fixes
python -m ruff check src/flext/ --fix --unsafe-fixes
```

- Import sorting and organization
- Code style consistency enforcement
- Unused variable removal
- Dead code elimination
- Security pattern fixes

#### Phase 2: Black Formatting

```bash
# Consistent code formatting with 120-character line length
python -m black src/flext/ --line-length 120
```

- String quote normalization
- Line length enforcement
- Indentation standardization
- Bracket and parentheses formatting

#### Phase 3: Import Sorting

```bash
# Professional import organization with isort
python -m isort src/flext/ --profile black --line-length 120
```

- PEP 8 compliant import ordering
- Black-compatible formatting
- Consistent spacing and grouping

#### Phase 4: Final Validation

```bash
# Zero-tolerance validation of code quality
python -m mypy src/flext/ --no-error-summary
python -m ruff check src/flext/ --statistics
```

- Type checking compliance verification
- Style guide adherence confirmation
- Architecture pattern validation

**Usage:**

```bash
# Run complete zero-tolerance cleanup
python scripts/ultra_rigorous_cleanup.py

# Exit codes:
# 0: Zero violations achieved (success)
# 1: Violations still exist (failure)
```

**Implementation Details:**

- **Error-resistant execution**: Handles subprocess errors gracefully
- **Comprehensive reporting**: Shows MyPy and Ruff violation counts
- **Shell-safe execution**: Uses shell=False for security
- **Progressive phases**: Each phase builds on the previous

**Example Output:**

```
🚨 INITIATING ZERO-TOLERANCE ULTRA-RIGOROUS CLEANUP
============================================================

📋 PHASE 1: RUFF AUTO-FIXES
🔧 Applying all Ruff auto-fixes with unsafe fixes enabled

📋 PHASE 2: BLACK FORMATTING
🔧 Applying Black formatting with 120 character line length

📋 PHASE 3: IMPORT SORTING
🔧 Sorting imports with isort

📋 PHASE 4: VALIDATION
🔧 Running final MyPy validation
   MyPy errors: 0
🔧 Running final Ruff validation
   Ruff violations: 0

📊 FINAL ASSESSMENT: 0 total violations
✅ ZERO-TOLERANCE COMPLIANCE ACHIEVED!
```

**Configuration:**

```yaml
# cleanup_config.yaml
cleanup:
  enabled_operations:
    - dead_code_elimination
    - import_optimization
    - code_pattern_cleanup
    - architecture_validation
    - security_cleanup

  exclusions:
    directories:
      - .git
      - __pycache__
      - .pytest_cache
    files:
      - "*.pyc"
      - "*.pyo"
      - ".DS_Store"

  dead_code:
    remove_unused_functions: true
    remove_unused_classes: true
    remove_unused_variables: true
    exclude_test_files: true

  imports:
    sort_imports: true
    remove_unused: true
    consolidate_duplicates: true
    convert_to_absolute: true

  security:
    scan_for_secrets: true
    remove_debug_code: true
    check_dependencies: true
    clean_test_data: true

  architecture:
    validate_port_boundaries: true
    check_dependency_direction: true
    enforce_naming_conventions: true
    validate_injection_patterns: true
```

**Example Output:**

```
🧹 FLX Ultra Rigorous Cleanup Starting...

📊 Scanning codebase...
   - Files scanned: 247
   - Lines of code: 45,782
   - Estimated cleanup time: 3m 45s

🗑️  Dead Code Elimination:
   ✅ Removed 12 unused functions
   ✅ Removed 3 unused classes
   ✅ Removed 45 unused variables
   ✅ Cleaned up 8 obsolete configurations

📦 Import Optimization:
   ✅ Removed 67 unused imports
   ✅ Consolidated 23 duplicate imports
   ✅ Sorted imports in 156 files
   ✅ Fixed 4 circular import issues

🏗️  Architecture Validation:
   ✅ Validated 45 port-adapter boundaries
   ✅ Fixed 3 dependency direction violations
   ✅ Updated 12 naming convention violations
   ✅ Validated 67 injection patterns

🔒 Security Cleanup:
   ⚠️  Found 2 potential secrets (moved to .env.example)
   ✅ Removed debug code from 8 files
   ✅ Updated 3 vulnerable dependencies
   ✅ Cleaned sensitive data from 5 test files

📋 Summary:
   - Total changes: 234
   - Files modified: 89
   - Lines cleaned: 1,247
   - Security issues fixed: 14
   - Time saved in future maintenance: ~8 hours

✨ Cleanup completed successfully!
```

### 2. Import Consolidation (`../consolidate_imports.py`)

**Purpose**: Advanced import analysis and duplicate pattern detection across adapter files.

**Key Features:**

- **AST-based Analysis**: Uses Abstract Syntax Tree parsing for accurate import detection
- **Duplicate Detection**: Identifies common import patterns across multiple files
- **Import Fingerprinting**: Creates signatures for identical import sets
- **Refactoring Support**: Provides data for import consolidation decisions

**Analysis Capabilities:**

#### Import Pattern Detection

```python
def analyze_imports(file_path: Path) -> set[str]:
    """Analyze imports in a Python file using AST parsing."""
    # Detects both 'import' and 'from...import' statements
    # Returns normalized import strings for comparison
```

#### Duplicate Pattern Identification

```python
def find_duplicate_imports():
    """Find duplicate import patterns across adapter files."""
    # Scans src/flext/adapters and src/flext/infra directories
    # Groups files by import usage patterns
    # Identifies frequently duplicated imports (used in 3+ files)
```

**Usage:**

```bash
# Analyze import patterns across the codebase
python consolidate_imports.py

# The script automatically:
# 1. Scans all adapter and infrastructure Python files
# 2. Analyzes import statements using AST
# 3. Identifies duplicate patterns
# 4. Groups files with identical import signatures
```

**Example Output Analysis:**

```
Import Pattern Analysis:
- Files analyzed: 67
- Unique import patterns: 23
- Duplicate patterns found: 8
- Files with identical imports: 12

Most common duplicated imports:
- "from typing import Protocol": used in 15 files
- "from flext.core.logging import FlxLogger": used in 12 files
- "from abc import ABC, abstractmethod": used in 10 files
```

### 3. Validation & Duplication Detection (`../validate_no_duplications.py`)

**Purpose**: Final validation script ensuring zero tolerance for code duplications and architectural violations.

**Key Features:**

- **Class Duplication Detection**: Identifies duplicate class names and functionality
- **Architectural Compliance**: Validates adapter standardization patterns
- **Dead Code Detection**: Finds obsolete files and patterns
- **Zero-Tolerance Validation**: Comprehensive compliance checking

**Validation Operations:**

#### Class Duplication Analysis

```python
def find_class_duplications():
    """Find any duplicate class names or similar functionality."""
    # Tracks adapter classes across the codebase
    # Identifies base classes and mixins
    # Detects naming conflicts and redundant implementations
```

#### Standardization Compliance

```python
def check_standardization():
    """Check that all adapters follow standardization patterns."""
    # Validates required patterns in adapter implementations:
    # - EnhancedAdapter inheritance
    # - get_default_config method presence
    # - _get_specific_operations implementation
    # - _perform_health_check_operation method
    # - Hierarchical configuration comments
```

#### Dead Code Pattern Detection

```python
dead_code_patterns = [
    "*_production_engine.py",
    "*_standardized.py",
    "*_extended.py",
    "*_legacy.py",
    "*_old.py",
    "*_backup.py",
    "*_template.py"
]
```

**Usage:**

```bash
# Run comprehensive duplication validation
python validate_no_duplications.py

# Exit codes:
# 0: Zero violations found (compliance achieved)
# 1: Violations detected (action required)
```

**Validation Categories:**

1. **Adapter Classes**: No duplicate adapter class names
2. **Base Classes**: No conflicting base class definitions
3. **Dead Files**: No obsolete pattern files remaining
4. **Standardization**: All adapters follow required patterns

### 4. Test Coverage Analysis (`../analyze_test_coverage.py`)

**Purpose**: Automated test coverage analysis and reporting for comprehensive testing validation.

**Status**: Currently empty - TODO implementation needed

**Planned Features:**

- Comprehensive coverage analysis across all test categories
- Gap identification in test coverage
- Coverage trend analysis over time
- Integration with CI/CD pipelines

### 5. Detailed Test Analysis (`../detailed_test_analysis.py`)

**Purpose**: Deep-dive test analysis including performance metrics and quality indicators.

**Status**: Currently empty - TODO implementation needed

**Planned Features:**

- Test execution time analysis
- Test reliability metrics
- Failure pattern analysis
- Test quality scoring

## 🏗️ Script Development Guidelines

### Creating New Scripts

1. **Follow UNIX Philosophy - Single Responsibility**

   ```python
   #!/usr/bin/env python3
   """Single-purpose script following UNIX philosophy."""

   # ✅ Good: Single responsibility
   def cleanup_imports(file_path: Path) -> ImportCleanupResult:
       """Clean up imports in a single file with comprehensive analysis."""
       return ImportCleanupResult(
           removed_imports=analyze_and_remove_unused_imports(file_path),
           sorted_imports=sort_imports_by_pep8(file_path),
           optimization_suggestions=get_import_optimizations(file_path)
       )

   # ❌ Avoid: Multiple responsibilities
   def cleanup_everything(project_path: Path) -> None:
       """Clean imports, remove dead code, and validate architecture."""
       # This violates single responsibility principle
       pass
   ```

2. **Use Comprehensive Type Hints**

   ```python
   from pathlib import Path
   from typing import List, Optional, Dict, Any, Union, Callable
   from dataclasses import dataclass
   from enum import Enum

   class ProcessingResult(Enum):
       SUCCESS = "success"
       PARTIAL = "partial"
       FAILED = "failed"

   @dataclass
   class FileProcessingResult:
       file_path: Path
       status: ProcessingResult
       changes_made: List[str]
       errors: List[str]
       execution_time: float

   def process_files(
       source_dir: Path,
       patterns: List[str],
       config: Optional[Dict[str, Any]] = None,
       progress_callback: Optional[Callable[[str], None]] = None
   ) -> List[FileProcessingResult]:
       """Process files matching patterns in source directory with full typing."""
       results: List[FileProcessingResult] = []
       # Implementation with comprehensive error handling
       return results
   ```

3. **Implement Production-Ready Logging**

   ```python
   import logging
   import sys
   from pathlib import Path
   from typing import Optional
   from flext.core.logging import FlxLogger
   from flext.infra.logging.structured import StructuredLogger

   def setup_script_logging(
       script_name: str,
       log_level: str = "INFO",
       log_file: Optional[Path] = None
   ) -> FlxLogger:
       """Set up comprehensive logging for scripts."""
       logger = FlxLogger(f"flext.scripts.{script_name}")

       # Configure structured logging
       if log_file:
           structured_logger = StructuredLogger(log_file)
           logger.add_handler(structured_logger.get_handler())

       # Set log level
       numeric_level = getattr(logging, log_level.upper(), logging.INFO)
       logger.setLevel(numeric_level)

       return logger

   def main_with_logging():
       """Example main function with comprehensive logging."""
       logger = setup_script_logging("example_script", "DEBUG")

       try:
           logger.info("Script execution started", extra={
               "script_version": "1.0.0",
               "python_version": sys.version,
               "working_directory": str(Path.cwd())
           })

           # Script logic with structured logging
           logger.debug("Processing file", extra={
               "file_path": str(file_path),
               "file_size": file_path.stat().st_size,
               "operation": "analysis"
           })

           logger.info("Script execution completed successfully", extra={
               "files_processed": 42,
               "total_execution_time": 15.7,
               "exit_code": 0
           })

       except Exception as e:
           logger.exception("Script execution failed", extra={
               "error_type": type(e).__name__,
               "error_message": str(e),
               "exit_code": 1
           })
           sys.exit(1)
   ```

4. **Add Professional CLI Interface**

   ```python
   import argparse
   import sys
   from pathlib import Path
   from typing import Optional, List
   from dataclasses import dataclass

   @dataclass
   class ScriptConfig:
       """Configuration container for script execution."""
       target_dir: Path
       dry_run: bool
       verbose: bool
       config_file: Optional[Path]
       operations: List[str]
       parallel_workers: int
       timeout: float

   def create_comprehensive_parser() -> argparse.ArgumentParser:
       """Create comprehensive CLI parser following best practices."""
       parser = argparse.ArgumentParser(
           description="FLX maintenance script with comprehensive options",
           epilog="Examples:\n"
                  "  %(prog)s --target src/flext/core --dry-run\n"
                  "  %(prog)s --operations imports,cleanup --parallel 4\n"
                  "  %(prog)s --config custom_config.yaml --verbose",
           formatter_class=argparse.RawDescriptionHelpFormatter
       )

       # Input/Output options
       parser.add_argument(
           "--target",
           type=Path,
           default=Path("src/"),
           help="Target directory to process (default: src/)"
       )
       parser.add_argument(
           "--config",
           type=Path,
           help="Configuration file path (YAML format)"
       )

       # Operation options
       parser.add_argument(
           "--operations",
           type=str,
           default="all",
           help="Comma-separated list of operations: imports,cleanup,validate,format"
       )
       parser.add_argument(
           "--dry-run",
           action="store_true",
           help="Show changes without applying them"
       )

       # Performance options
       parser.add_argument(
           "--parallel",
           type=int,
           default=1,
           help="Number of parallel workers (default: 1)"
       )
       parser.add_argument(
           "--timeout",
           type=float,
           default=300.0,
           help="Operation timeout in seconds (default: 300)"
       )

       # Logging options
       parser.add_argument(
           "--verbose", "-v",
           action="store_true",
           help="Enable verbose output"
       )
       parser.add_argument(
           "--log-file",
           type=Path,
           help="Log file path for persistent logging"
       )

       # Version information
       parser.add_argument(
           "--version",
           action="version",
           version="%(prog)s 1.0.0"
       )

       return parser

   def validate_arguments(args: argparse.Namespace) -> ScriptConfig:
       """Validate and process command line arguments."""
       # Validate target directory
       if not args.target.exists():
           raise ValueError(f"Target directory does not exist: {args.target}")

       # Validate config file if provided
       if args.config and not args.config.exists():
           raise ValueError(f"Config file does not exist: {args.config}")

       # Parse operations
       if args.operations == "all":
           operations = ["imports", "cleanup", "validate", "format"]
       else:
           operations = [op.strip() for op in args.operations.split(",")]
           valid_operations = {"imports", "cleanup", "validate", "format"}
           invalid_ops = set(operations) - valid_operations
           if invalid_ops:
               raise ValueError(f"Invalid operations: {invalid_ops}")

       return ScriptConfig(
           target_dir=args.target,
           dry_run=args.dry_run,
           verbose=args.verbose,
           config_file=args.config,
           operations=operations,
           parallel_workers=args.parallel,
           timeout=args.timeout
       )

   def main():
       """Main entry point with comprehensive argument handling."""
       parser = create_comprehensive_parser()

       try:
           args = parser.parse_args()
           config = validate_arguments(args)

           # Initialize logging
           log_level = "DEBUG" if config.verbose else "INFO"
           logger = setup_script_logging("maintenance", log_level, args.log_file)

           # Execute script logic
           return execute_script(config, logger)

       except ValueError as e:
           print(f"Error: {e}", file=sys.stderr)
           parser.print_help()
           sys.exit(1)
       except KeyboardInterrupt:
           print("\nOperation cancelled by user", file=sys.stderr)
           sys.exit(130)
       except Exception as e:
           print(f"Unexpected error: {e}", file=sys.stderr)
           sys.exit(1)
   ```

### Script Testing

```python
# tests/scripts/test_ultra_rigorous_cleanup.py
import pytest
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
from scripts.ultra_rigorous_cleanup import run_command, apply_zero_tolerance_fixes

class TestUltraRigorousCleanup:
    """Comprehensive test suite for ultra rigorous cleanup script."""

    @pytest.fixture
    def mock_subprocess_run(self):
        """Mock subprocess.run for testing."""
        with patch('subprocess.run') as mock_run:
            yield mock_run

    def test_run_command_success(self, mock_subprocess_run):
        """Test successful command execution."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success output"
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result

        # Execute
        returncode, stdout, stderr = run_command(
            ["python", "-m", "ruff", "check", "src/"],
            "Testing ruff check"
        )

        # Verify
        assert returncode == 0
        assert stdout == "Success output"
        assert stderr == ""
        mock_subprocess_run.assert_called_once_with(
            ["python", "-m", "ruff", "check", "src/"],
            capture_output=True,
            text=True,
            check=False,
            shell=False
        )

    def test_run_command_failure(self, mock_subprocess_run):
        """Test command execution with errors."""
        # Setup mock
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Found 5 errors"
        mock_subprocess_run.return_value = mock_result

        # Execute
        returncode, stdout, stderr = run_command(
            ["python", "-m", "mypy", "src/"],
            "Testing mypy check"
        )

        # Verify
        assert returncode == 1
        assert stdout == ""
        assert stderr == "Found 5 errors"

    def test_run_command_subprocess_error(self, mock_subprocess_run):
        """Test command execution with subprocess exception."""
        # Setup mock to raise exception
        mock_subprocess_run.side_effect = subprocess.SubprocessError("Command failed")

        # Execute
        returncode, stdout, stderr = run_command(
            ["invalid-command"],
            "Testing invalid command"
        )

        # Verify error handling
        assert returncode == 1
        assert stdout == ""
        assert stderr == "Command failed"

    @patch('scripts.ultra_rigorous_cleanup.run_command')
    def test_apply_zero_tolerance_fixes_success(self, mock_run_command):
        """Test successful zero-tolerance cleanup achieving compliance."""
        # Setup mock responses for each phase
        mock_responses = [
            # Phase 1: Ruff auto-fixes
            (0, "Fixed 10 issues", ""),
            # Phase 2: Black formatting
            (0, "Formatted 25 files", ""),
            # Phase 3: Import sorting
            (0, "Sorted imports in 25 files", ""),
            # Phase 4: MyPy validation
            (0, "", "Success: no issues found"),
            # Phase 4: Ruff validation
            (0, "", "Found 0 errors")
        ]
        mock_run_command.side_effect = mock_responses

        # Execute
        result = apply_zero_tolerance_fixes()

        # Verify success
        assert result is True
        assert mock_run_command.call_count == 5

    @patch('scripts.ultra_rigorous_cleanup.run_command')
    def test_apply_zero_tolerance_fixes_with_violations(self, mock_run_command):
        """Test cleanup with remaining violations."""
        # Setup mock responses with remaining errors
        mock_responses = [
            (0, "Fixed 10 issues", ""),
            (0, "Formatted 25 files", ""),
            (0, "Sorted imports in 25 files", ""),
            (1, "", "src/flext/core/test.py:42: error: Cannot resolve name"),
            (0, "", "Found 3 errors")
        ]
        mock_run_command.side_effect = mock_responses

        # Execute
        result = apply_zero_tolerance_fixes()

        # Verify failure due to violations
        assert result is False

    def test_mypy_error_count_extraction(self, mock_subprocess_run):
        """Test MyPy error count extraction from stderr."""
        # Setup mock with MyPy errors
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = """
src/flext/core/test.py:42: error: Cannot resolve name
src/flext/core/other.py:15: error: Missing type annotation
Found 2 errors in 2 files
"""
        mock_subprocess_run.return_value = mock_result

        # Execute command directly
        returncode, stdout, stderr = run_command(
            ["python", "-m", "mypy", "src/flext/"],
            "Testing MyPy"
        )

        # Verify error extraction logic would work
        error_count = stderr.count("error:")
        assert error_count == 2

    def test_ruff_statistics_parsing(self, mock_subprocess_run):
        """Test Ruff statistics parsing."""
        # Setup mock with Ruff statistics
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = """
3	F401	[*] `flext.core.unused` imported but unused
2	E302	[*] Expected 2 blank lines, found 1
1	W291	[*] Trailing whitespace
"""
        mock_subprocess_run.return_value = mock_result

        # Execute
        returncode, stdout, stderr = run_command(
            ["python", "-m", "ruff", "check", "src/flext/", "--statistics"],
            "Testing Ruff statistics"
        )

        # Verify statistics parsing logic would work
        lines = stderr.strip().split("\n")
        total_violations = sum(
            int(line.split()[0]) for line in lines
            if line and line[0].isdigit()
        )
        assert total_violations == 6  # 3 + 2 + 1

# tests/scripts/test_import_consolidation.py
import pytest
import ast
from pathlib import Path
from unittest.mock import patch, mock_open
from consolidate_imports import analyze_imports, find_duplicate_imports

class TestImportConsolidation:
    """Test suite for import consolidation script."""

    def test_analyze_imports_basic(self):
        """Test basic import analysis."""
        code = """
import os
import sys
from typing import List, Dict
from pathlib import Path
"""

        # Mock file reading
        with patch('builtins.open', mock_open(read_data=code)):
            imports = analyze_imports(Path("test.py"))

        expected_imports = {
            "import os",
            "import sys",
            "from typing import List",
            "from typing import Dict",
            "from pathlib import Path"
        }

        assert imports == expected_imports

    def test_analyze_imports_with_aliases(self):
        """Test import analysis with aliases."""
        code = """
import numpy as np
from typing import List as ListType
"""

        with patch('builtins.open', mock_open(read_data=code)):
            imports = analyze_imports(Path("test.py"))

        expected_imports = {
            "import numpy",  # Alias names are normalized
            "from typing import List"
        }

        assert imports == expected_imports

    def test_analyze_imports_syntax_error(self):
        """Test import analysis with syntax errors."""
        code = "invalid python syntax $$$ import os"

        with patch('builtins.open', mock_open(read_data=code)):
            imports = analyze_imports(Path("test.py"))

        # Should return empty set on syntax error
        assert imports == set()

    @patch('pathlib.Path.rglob')
    @patch('pathlib.Path.exists')
    def test_find_duplicate_imports(self, mock_exists, mock_rglob):
        """Test duplicate import detection."""
        # Setup mock file structure
        mock_exists.return_value = True
        mock_files = [
            Path("src/flext/adapters/http.py"),
            Path("src/flext/adapters/database.py"),
            Path("src/flext/infra/logging.py")
        ]
        mock_rglob.return_value = mock_files

        # Mock file contents
        file_contents = {
            "src/flext/adapters/http.py": """
import asyncio
from typing import Protocol
from flext.core.logging import FlxLogger
""",
            "src/flext/adapters/database.py": """
import asyncio
from typing import Protocol, Dict
from flext.core.base import BaseAdapter
""",
            "src/flext/infra/logging.py": """
import logging
from typing import Protocol
from flext.core.base import BaseClass
"""
        }

        with patch('consolidate_imports.analyze_imports') as mock_analyze:
            # Setup analyze_imports to return different sets for each file
            def side_effect(file_path):
                content = file_contents.get(str(file_path), "")
                if "http.py" in str(file_path):
                    return {"import asyncio", "from typing import Protocol", "from flext.core.logging import FlxLogger"}
                elif "database.py" in str(file_path):
                    return {"import asyncio", "from typing import Protocol", "from flext.core.base import BaseAdapter"}
                elif "logging.py" in str(file_path):
                    return {"import logging", "from typing import Protocol", "from flext.core.base import BaseClass"}
                return set()

            mock_analyze.side_effect = side_effect

            # Execute (function doesn't return, so we test it doesn't crash)
            find_duplicate_imports()

            # Verify analyze_imports was called for each file
            assert mock_analyze.call_count == len(mock_files)

# tests/scripts/test_validation.py
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from validate_no_duplications import find_class_duplications, check_standardization

class TestValidationScript:
    """Test suite for duplication validation script."""

    @patch('pathlib.Path.rglob')
    @patch('pathlib.Path.exists')
    def test_find_class_duplications_no_violations(self, mock_exists, mock_rglob):
        """Test class duplication detection with no violations."""
        mock_exists.return_value = True
        mock_rglob.return_value = [Path("src/flext/adapters/http.py")]

        code = """
class HttpAdapter:
    pass

class HttpClientMixin:
    pass
"""

        with patch('builtins.open', mock_open(read_data=code)):
            result = find_class_duplications()

        # Should return True when no duplications found
        assert result is True

    @patch('pathlib.Path.rglob')
    @patch('pathlib.Path.exists')
    def test_check_standardization_compliance(self, mock_exists, mock_rglob):
        """Test adapter standardization compliance checking."""
        mock_exists.return_value = True
        mock_rglob.return_value = [Path("src/flext/adapters/http.py")]

        # Code with all required patterns
        compliant_code = """
from flext.adapters.base import EnhancedAdapter

class HttpAdapter(EnhancedAdapter):
    # Configuration fields organized hierarchically

    def get_default_config(self):
        pass

    def _get_specific_operations(self):
        pass

    def _perform_health_check_operation(self):
        pass
"""

        with patch('builtins.open', mock_open(read_data=compliant_code)):
            result = check_standardization()

        # Should return True for compliant code
        assert result is True

    @patch('pathlib.Path.rglob')
    @patch('pathlib.Path.exists')
    def test_check_standardization_non_compliance(self, mock_exists, mock_rglob):
        """Test detection of non-compliant adapters."""
        mock_exists.return_value = True
        mock_rglob.return_value = [Path("src/flext/adapters/http.py")]

        # Code missing required patterns
        non_compliant_code = """
class HttpAdapter:
    def basic_method(self):
        pass
"""

        with patch('builtins.open', mock_open(read_data=non_compliant_code)):
            result = check_standardization()

        # Should return False for non-compliant code
        assert result is False
```

## 🔄 Integration with CI/CD

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      # Ultra rigorous cleanup validation
      - id: flext-zero-tolerance-check
        name: FLX Zero Tolerance Validation
        entry: python scripts/ultra_rigorous_cleanup.py
        language: python
        pass_filenames: false
        always_run: true
        description: "Ensures zero MyPy and Ruff violations"

      # Import consolidation check
      - id: flext-import-analysis
        name: FLX Import Pattern Analysis
        entry: python consolidate_imports.py
        language: python
        pass_filenames: false
        always_run: true
        description: "Analyzes import patterns for consolidation opportunities"

      # Duplication validation
      - id: flext-duplication-check
        name: FLX Duplication Validation
        entry: python validate_no_duplications.py
        language: python
        pass_filenames: false
        always_run: true
        description: "Validates zero tolerance for code duplications"

  # Standard code quality tools that complement our scripts
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.13
        args: [--line-length=120]

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.8
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
```

### GitHub Actions - Zero Tolerance Workflow

````yaml
# .github/workflows/zero-tolerance-compliance.yml
name: Zero Tolerance Compliance

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: "0 2 * * 1" # Weekly validation on Monday 2 AM

env:
  PYTHON_VERSION: "3.13"

jobs:
  zero-tolerance-validation:
    name: Zero Tolerance Code Quality
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Python Environment
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: "pip"

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install mypy ruff black isort

      - name: Run Ultra Rigorous Cleanup
        id: cleanup
        run: |
          echo "CLEANUP_RESULT=$(python scripts/ultra_rigorous_cleanup.py && echo 'SUCCESS' || echo 'FAILED')" >> $GITHUB_OUTPUT

      - name: Validate Import Patterns
        run: |
          python consolidate_imports.py
          echo "Import pattern analysis completed"

      - name: Validate Zero Duplications
        run: |
          python validate_no_duplications.py
          echo "Duplication validation completed"

      - name: Generate Compliance Report
        if: always()
        run: |
          echo "# Zero Tolerance Compliance Report" > compliance_report.md
          echo "Generated at: $(date)" >> compliance_report.md
          echo "" >> compliance_report.md
          echo "## Cleanup Result: ${{ steps.cleanup.outputs.CLEANUP_RESULT }}" >> compliance_report.md
          echo "" >> compliance_report.md

          # MyPy validation results
          echo "## MyPy Validation" >> compliance_report.md
          python -m mypy src/flext/ --no-error-summary > mypy_results.txt 2>&1 || true
          echo '```' >> compliance_report.md
          cat mypy_results.txt >> compliance_report.md
          echo '```' >> compliance_report.md
          echo "" >> compliance_report.md

          # Ruff validation results
          echo "## Ruff Validation" >> compliance_report.md
          python -m ruff check src/flext/ --statistics > ruff_results.txt 2>&1 || true
          echo '```' >> compliance_report.md
          cat ruff_results.txt >> compliance_report.md
          echo '```' >> compliance_report.md

      - name: Upload Compliance Report
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: compliance-report-${{ github.sha }}
          path: |
            compliance_report.md
            mypy_results.txt
            ruff_results.txt

      - name: Comment PR with Results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('compliance_report.md', 'utf8');

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: report
            });

      - name: Fail on Compliance Violations
        if: steps.cleanup.outputs.CLEANUP_RESULT == 'FAILED'
        run: |
          echo "❌ Zero tolerance compliance not achieved!"
          echo "Review the compliance report for details."
          exit 1

  dependency-vulnerability-scan:
    name: Dependency Security Scan
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install Dependencies
        run: pip install safety bandit

      - name: Run Safety Check
        run: |
          safety check --json > safety_report.json || true

      - name: Run Bandit Security Check
        run: |
          bandit -r src/flext/ -f json -o bandit_report.json || true

      - name: Upload Security Reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports-${{ github.sha }}
          path: |
            safety_report.json
            bandit_report.json
````

### Makefile Integration

```makefile
# Enhanced Makefile targets for script integration
.PHONY: zero-tolerance cleanup-ultra validate-duplications analyze-imports

# Zero tolerance compliance check
zero-tolerance:
	@echo "🚨 Running zero-tolerance compliance check..."
	@python scripts/ultra_rigorous_cleanup.py
	@if [ $$? -eq 0 ]; then \
		echo "✅ Zero tolerance compliance achieved!"; \
	else \
		echo "❌ Zero tolerance compliance failed!"; \
		exit 1; \
	fi

# Ultra rigorous cleanup
cleanup-ultra:
	@echo "🧹 Running ultra rigorous cleanup..."
	@python scripts/ultra_rigorous_cleanup.py

# Validate no duplications
validate-duplications:
	@echo "🔍 Validating zero duplications..."
	@python validate_no_duplications.py

# Analyze import patterns
analyze-imports:
	@echo "📦 Analyzing import patterns..."
	@python consolidate_imports.py

# Complete compliance suite
compliance-suite: zero-tolerance validate-duplications analyze-imports
	@echo "🏆 Complete compliance validation finished!"

# Development workflow integration
dev-check: compliance-suite test lint
	@echo "🚀 Development checks complete - ready for commit!"

# Pre-commit validation
pre-commit: compliance-suite
	@echo "✨ Pre-commit validation complete!"
```

## ⚙️ Script Configuration

### Environment Variables

```bash
# Script execution environment variables
export FLX_SCRIPTS_LOG_LEVEL="INFO"               # DEBUG, INFO, WARNING, ERROR
export FLX_SCRIPTS_PARALLEL_WORKERS="4"           # Number of parallel workers
export FLX_SCRIPTS_TIMEOUT="300"                  # Operation timeout in seconds
export FLX_SCRIPTS_DRY_RUN="false"               # Enable dry-run mode
export FLX_SCRIPTS_CONFIG_FILE="scripts_config.yaml"  # Custom config file path

# Zero tolerance cleanup configuration
export FLX_CLEANUP_MYPY_CONFIG="pyproject.toml"   # MyPy configuration file
export FLX_CLEANUP_RUFF_CONFIG="pyproject.toml"   # Ruff configuration file
export FLX_CLEANUP_BLACK_LINE_LENGTH="120"        # Black line length
export FLX_CLEANUP_ISORT_PROFILE="black"          # isort profile

# Import analysis configuration
export FLX_IMPORT_ANALYSIS_DIRS="src/flext/adapters,src/flext/infra"  # Directories to analyze
export FLX_IMPORT_MIN_DUPLICATES="3"              # Minimum files for duplicate reporting

# Validation configuration
export FLX_VALIDATION_DEAD_CODE_PATTERNS="*_legacy.py,*_old.py,*_backup.py"
export FLX_VALIDATION_REQUIRED_PATTERNS="EnhancedAdapter,get_default_config"
```

### Comprehensive Configuration Files

```yaml
# scripts_config.yaml - Master configuration for all scripts
scripts:
  # Global settings
  global:
    log_level: "INFO"
    parallel_workers: 4
    timeout: 300
    dry_run: false
    output_dir: "reports/scripts/"
    retention_days: 30

  # Ultra rigorous cleanup configuration
  ultra_cleanup:
    enabled: true
    zero_tolerance: true
    phases:
      ruff_autofix:
        enabled: true
        unsafe_fixes: true
        target_dir: "src/flext/"

      black_formatting:
        enabled: true
        line_length: 120
        target_dir: "src/flext/"

      import_sorting:
        enabled: true
        profile: "black"
        line_length: 120
        target_dir: "src/flext/"

      validation:
        mypy:
          enabled: true
          config_file: "pyproject.toml"
          no_error_summary: true
        ruff:
          enabled: true
          statistics: true
          target_dir: "src/flext/"

  # Import consolidation configuration
  import_analysis:
    enabled: true
    target_directories:
      - "src/flext/adapters"
      - "src/flext/infra"
    min_duplicate_threshold: 3
    exclude_patterns:
      - "__init__.py"
      - "*_test.py"
      - "test_*.py"
    reporting:
      show_file_details: true
      max_files_per_import: 5
      group_by_frequency: true

  # Duplication validation configuration
  duplication_validation:
    enabled: true
    class_analysis:
      track_adapters: true
      track_base_classes: true
      track_mixins: true

    dead_code_patterns:
      - "*_production_engine.py"
      - "*_standardized.py"
      - "*_extended.py"
      - "*_legacy.py"
      - "*_old.py"
      - "*_backup.py"
      - "*_template.py"

    standardization_requirements:
      - "EnhancedAdapter"
      - "get_default_config"
      - "_get_specific_operations"
      - "_perform_health_check_operation"
      - "# Configuration fields organized hierarchically"

  # Performance optimization
  performance:
    use_parallel_processing: true
    max_file_size_mb: 10
    cache_analysis_results: true
    cache_duration_hours: 24

  # Reporting configuration
  reporting:
    formats: ["json", "markdown", "console"]
    include_timestamps: true
    include_file_stats: true
    include_performance_metrics: true
    export_detailed_logs: true

# Tool-specific configurations
tools:
  mypy:
    config_file: "pyproject.toml"
    strict_mode: true
    show_error_codes: true
    warn_redundant_casts: true
    warn_unused_ignores: true

  ruff:
    config_file: "pyproject.toml"
    select: ["ALL"]
    ignore: ["D100", "D101", "D102", "D103", "D104", "D105"]
    line_length: 120
    target_version: "py313"

  black:
    line_length: 120
    target_version: ["py313"]
    skip_string_normalization: false
    experimental_string_processing: true

  isort:
    profile: "black"
    line_length: 120
    multi_line_output: 3
    include_trailing_comma: true
    force_grid_wrap: 0
    use_parentheses: true
```

### Script-Specific Configuration

```yaml
# cleanup_config.yaml - Detailed ultra rigorous cleanup configuration
cleanup:
  zero_tolerance:
    mypy_errors: 0
    ruff_violations: 0
    undefined_names: 0
    dead_code_instances: 0

  execution_phases:
    phase_1_ruff_autofix:
      command:
        ["python", "-m", "ruff", "check", "src/flext/", "--fix", "--unsafe-fixes"]
      description: "Applying all Ruff auto-fixes with unsafe fixes enabled"
      continue_on_error: false

    phase_2_black_formatting:
      command: ["python", "-m", "black", "src/flext/", "--line-length", "120"]
      description: "Applying Black formatting with 120 character line length"
      continue_on_error: false

    phase_3_import_sorting:
      command:
        [
          "python",
          "-m",
          "isort",
          "src/flext/",
          "--profile",
          "black",
          "--line-length",
          "120",
        ]
      description: "Sorting imports with isort"
      continue_on_error: false

    phase_4_mypy_validation:
      command: ["python", "-m", "mypy", "src/flext/", "--no-error-summary"]
      description: "Running final MyPy validation"
      continue_on_error: true
      parse_errors: true

    phase_5_ruff_validation:
      command: ["python", "-m", "ruff", "check", "src/flext/", "--statistics"]
      description: "Running final Ruff validation"
      continue_on_error: true
      parse_statistics: true

  error_parsing:
    mypy:
      error_pattern: "error:"
      extract_count: true

    ruff:
      statistics_format: true
      parse_numeric_counts: true
      line_pattern: "^\\d+\\s+"

  success_criteria:
    total_violations: 0
    mypy_errors: 0
    ruff_violations: 0

  reporting:
    success_message: "✅ ZERO-TOLERANCE COMPLIANCE ACHIEVED!"
    failure_message: "❌ ZERO-TOLERANCE VIOLATION: {violations} issues remain"
    show_phase_progress: true
    show_violation_counts: true
```

## ⚡ Performance Considerations

### Parallel Processing

```python
import asyncio
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Any
import multiprocessing as mp

class ParallelFileProcessor:
    """High-performance parallel file processing for scripts."""

    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or min(mp.cpu_count(), 8)

    async def process_files_async(
        self,
        files: List[Path],
        processor_func: callable
    ) -> List[Dict[str, Any]]:
        """Process files asynchronously with optimal worker count."""
        loop = asyncio.get_event_loop()

        # Use ThreadPoolExecutor for I/O bound operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            tasks = [
                loop.run_in_executor(executor, processor_func, file_path)
                for file_path in files
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter successful results and log errors
            successful_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to process {files[i]}: {result}")
                else:
                    successful_results.append(result)

            return successful_results

    def process_files_parallel(
        self,
        files: List[Path],
        processor_func: callable
    ) -> List[Dict[str, Any]]:
        """Process files in parallel using ProcessPoolExecutor for CPU-bound tasks."""
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(processor_func, file_path) for file_path in files]

            results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result(timeout=30)  # 30 second timeout per file
                    results.append(result)
                except Exception as e:
                    logger.error(f"Processing failed: {e}")

            return results

# Usage example
processor = ParallelFileProcessor(max_workers=4)
results = await processor.process_files_async(python_files, analyze_imports)
```

### Intelligent Caching System

```python
import hashlib
import pickle
import time
from functools import lru_cache, wraps
from pathlib import Path
from typing import Any, Dict, Optional

class FileAnalysisCache:
    """Intelligent caching system for file analysis results."""

    def __init__(self, cache_dir: Path = Path("cache/"), max_age_hours: int = 24):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.max_age = max_age_hours * 3600  # Convert to seconds

    def _get_file_hash(self, file_path: Path) -> str:
        """Generate hash based on file content and modification time."""
        try:
            stat = file_path.stat()
            content = f"{file_path}:{stat.st_mtime}:{stat.st_size}"
            return hashlib.sha256(content.encode()).hexdigest()[:16]
        except OSError:
            return hashlib.sha256(str(file_path).encode()).hexdigest()[:16]

    def get(self, file_path: Path, analysis_type: str) -> Optional[Any]:
        """Retrieve cached analysis result if valid."""
        cache_key = f"{analysis_type}_{self._get_file_hash(file_path)}"
        cache_file = self.cache_dir / f"{cache_key}.pkl"

        if not cache_file.exists():
            return None

        # Check cache age
        if time.time() - cache_file.stat().st_mtime > self.max_age:
            cache_file.unlink()  # Remove stale cache
            return None

        try:
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        except Exception:
            cache_file.unlink()  # Remove corrupted cache
            return None

    def set(self, file_path: Path, analysis_type: str, result: Any) -> None:
        """Cache analysis result."""
        cache_key = f"{analysis_type}_{self._get_file_hash(file_path)}"
        cache_file = self.cache_dir / f"{cache_key}.pkl"

        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(result, f)
        except Exception as e:
            logger.warning(f"Failed to cache result for {file_path}: {e}")

# Decorator for cached file analysis
def cached_analysis(analysis_type: str, cache: FileAnalysisCache):
    """Decorator to add caching to file analysis functions."""
    def decorator(func):
        @wraps(func)
        def wrapper(file_path: Path, *args, **kwargs):
            # Try to get from cache first
            cached_result = cache.get(file_path, analysis_type)
            if cached_result is not None:
                return cached_result

            # Perform analysis and cache result
            result = func(file_path, *args, **kwargs)
            cache.set(file_path, analysis_type, result)
            return result

        return wrapper
    return decorator

# Usage example
cache = FileAnalysisCache()

@cached_analysis("import_analysis", cache)
def analyze_imports_cached(file_path: Path) -> set[str]:
    """Cached version of import analysis."""
    return analyze_imports(file_path)
```

### Progress Tracking & Monitoring

```python
from tqdm import tqdm
from typing import Iterator, List, Callable, Any
import time
import threading
from dataclasses import dataclass, field

@dataclass
class ProcessingStats:
    """Statistics for processing operations."""
    total_files: int = 0
    processed_files: int = 0
    failed_files: int = 0
    start_time: float = field(default_factory=time.time)
    errors: List[str] = field(default_factory=list)

    @property
    def elapsed_time(self) -> float:
        return time.time() - self.start_time

    @property
    def files_per_second(self) -> float:
        if self.elapsed_time == 0:
            return 0
        return self.processed_files / self.elapsed_time

    @property
    def estimated_remaining(self) -> float:
        if self.files_per_second == 0:
            return float('inf')
        remaining_files = self.total_files - self.processed_files
        return remaining_files / self.files_per_second

class AdvancedProgressTracker:
    """Advanced progress tracking with statistics and monitoring."""

    def __init__(self, description: str = "Processing"):
        self.description = description
        self.stats = ProcessingStats()
        self._progress_bar = None
        self._monitor_thread = None
        self._stop_monitoring = threading.Event()

    def start_monitoring(self, total: int) -> None:
        """Start progress monitoring with real-time statistics."""
        self.stats.total_files = total
        self._progress_bar = tqdm(
            total=total,
            desc=self.description,
            unit="files",
            unit_scale=True,
            dynamic_ncols=True,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
        )

        # Start background monitoring thread
        self._monitor_thread = threading.Thread(target=self._monitor_progress)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()

    def update(self, success: bool = True, error_msg: str = None) -> None:
        """Update progress with success/failure information."""
        if success:
            self.stats.processed_files += 1
        else:
            self.stats.failed_files += 1
            if error_msg:
                self.stats.errors.append(error_msg)

        if self._progress_bar:
            self._progress_bar.update(1)
            # Update postfix with current statistics
            self._progress_bar.set_postfix({
                'success': self.stats.processed_files,
                'failed': self.stats.failed_files,
                'rate': f"{self.stats.files_per_second:.1f}/s"
            })

    def finish(self) -> None:
        """Finish progress tracking and display final statistics."""
        self._stop_monitoring.set()

        if self._progress_bar:
            self._progress_bar.close()

        if self._monitor_thread:
            self._monitor_thread.join(timeout=1)

        # Display final statistics
        print(f"\n📊 Processing Complete:")
        print(f"   ✅ Successful: {self.stats.processed_files}")
        print(f"   ❌ Failed: {self.stats.failed_files}")
        print(f"   ⏱️  Total time: {self.stats.elapsed_time:.2f}s")
        print(f"   🚀 Average rate: {self.stats.files_per_second:.1f} files/s")

        if self.stats.errors:
            print(f"   ⚠️  Errors: {len(self.stats.errors)}")

    def _monitor_progress(self) -> None:
        """Background monitoring for memory usage and performance."""
        import psutil
        process = psutil.Process()

        while not self._stop_monitoring.is_set():
            try:
                memory_mb = process.memory_info().rss / 1024 / 1024
                cpu_percent = process.cpu_percent()

                # Update progress bar with system stats
                if self._progress_bar and memory_mb > 100:  # Only show if using significant memory
                    self._progress_bar.set_description(
                        f"{self.description} [RAM: {memory_mb:.0f}MB, CPU: {cpu_percent:.1f}%]"
                    )

                time.sleep(1)  # Update every second
            except Exception:
                break  # Exit monitoring on any error

# Usage example
def process_files_with_tracking(files: List[Path], processor: Callable) -> List[Any]:
    """Process files with advanced progress tracking."""
    tracker = AdvancedProgressTracker("Analyzing files")
    tracker.start_monitoring(len(files))

    results = []
    for file_path in files:
        try:
            result = processor(file_path)
            results.append(result)
            tracker.update(success=True)
        except Exception as e:
            tracker.update(success=False, error_msg=str(e))

    tracker.finish()
    return results
```

## 🛡️ Error Handling & Recovery

### Robust Error Recovery System

```python
import logging
import sys
import traceback
from contextlib import contextmanager
from pathlib import Path
from typing import List, Dict, Any, Optional, Type
from dataclasses import dataclass
from enum import Enum

class ErrorSeverity(Enum):
    """Error severity levels for classification."""
    LOW = "low"           # Non-critical, can continue
    MEDIUM = "medium"     # Important, may affect results
    HIGH = "high"         # Critical, should stop operation
    FATAL = "fatal"       # System-level, requires immediate attention

@dataclass
class ScriptError:
    """Comprehensive error information."""
    severity: ErrorSeverity
    error_type: str
    message: str
    file_path: Optional[Path] = None
    line_number: Optional[int] = None
    traceback_info: Optional[str] = None
    recovery_suggestion: Optional[str] = None

class ScriptErrorHandler:
    """Advanced error handling with recovery strategies."""

    def __init__(self, max_errors: int = 10, stop_on_fatal: bool = True):
        self.max_errors = max_errors
        self.stop_on_fatal = stop_on_fatal
        self.errors: List[ScriptError] = []
        self.logger = logging.getLogger(__name__)

    def handle_error(
        self,
        error: Exception,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        file_path: Optional[Path] = None,
        recovery_suggestion: Optional[str] = None
    ) -> bool:
        """Handle error with appropriate response based on severity."""

        script_error = ScriptError(
            severity=severity,
            error_type=type(error).__name__,
            message=str(error),
            file_path=file_path,
            traceback_info=traceback.format_exc(),
            recovery_suggestion=recovery_suggestion
        )

        self.errors.append(script_error)

        # Log with appropriate level
        log_message = f"{script_error.error_type}: {script_error.message}"
        if file_path:
            log_message += f" (file: {file_path})"

        if severity == ErrorSeverity.LOW:
            self.logger.debug(log_message)
        elif severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        elif severity == ErrorSeverity.HIGH:
            self.logger.error(log_message)
        else:  # FATAL
            self.logger.critical(log_message)

        # Check if we should stop
        if severity == ErrorSeverity.FATAL and self.stop_on_fatal:
            return False

        if len(self.errors) >= self.max_errors:
            self.logger.error(f"Maximum error count ({self.max_errors}) reached")
            return False

        return True  # Continue processing

    @contextmanager
    def error_context(
        self,
        operation: str,
        file_path: Optional[Path] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM
    ):
        """Context manager for error handling during operations."""
        try:
            yield
        except Exception as e:
            recovery_suggestion = self._get_recovery_suggestion(e, operation)
            should_continue = self.handle_error(
                e, severity, file_path, recovery_suggestion
            )
            if not should_continue:
                raise SystemExit(f"Critical error in {operation}: {e}")

    def _get_recovery_suggestion(self, error: Exception, operation: str) -> str:
        """Generate recovery suggestions based on error type and operation."""
        suggestions = {
            "FileNotFoundError": "Verify file path exists and permissions are correct",
            "PermissionError": "Check file permissions and run with appropriate privileges",
            "SyntaxError": "Validate Python syntax in the target file",
            "ImportError": "Ensure all required dependencies are installed",
            "UnicodeDecodeError": "Check file encoding, may need to specify encoding explicitly",
            "subprocess.CalledProcessError": "Verify tool is installed and accessible in PATH",
            "TimeoutError": "Increase timeout or check for hanging processes"
        }

        error_name = type(error).__name__
        base_suggestion = suggestions.get(error_name, "Review error details and retry")

        return f"{base_suggestion}. Operation: {operation}"

    def generate_error_report(self) -> Dict[str, Any]:
        """Generate comprehensive error report."""
        error_counts = {severity.value: 0 for severity in ErrorSeverity}
        for error in self.errors:
            error_counts[error.severity.value] += 1

        return {
            "total_errors": len(self.errors),
            "error_counts": error_counts,
            "errors": [
                {
                    "severity": error.severity.value,
                    "type": error.error_type,
                    "message": error.message,
                    "file": str(error.file_path) if error.file_path else None,
                    "recovery_suggestion": error.recovery_suggestion
                }
                for error in self.errors
            ],
            "recommendations": self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on error patterns."""
        recommendations = []

        # Analyze error patterns
        error_types = [error.error_type for error in self.errors]

        if error_types.count("FileNotFoundError") > 2:
            recommendations.append("Multiple file not found errors - verify target directory structure")

        if error_types.count("PermissionError") > 0:
            recommendations.append("Permission errors detected - consider running with elevated privileges")

        if error_types.count("ImportError") > 0:
            recommendations.append("Import errors found - verify virtual environment and dependencies")

        if len([e for e in self.errors if e.severity == ErrorSeverity.FATAL]) > 0:
            recommendations.append("Fatal errors occurred - manual intervention required")

        return recommendations

# Usage in scripts
def safe_script_execution(files: List[Path], processor_func) -> Dict[str, Any]:
    """Execute script with comprehensive error handling."""
    error_handler = ScriptErrorHandler(max_errors=20)
    results = {"processed": [], "failed": [], "error_report": None}

    for file_path in files:
        with error_handler.error_context("file_processing", file_path):
            try:
                result = processor_func(file_path)
                results["processed"].append({
                    "file": str(file_path),
                    "result": result
                })
            except Exception as e:
                # Error already handled by context manager
                results["failed"].append(str(file_path))

    # Generate final error report
    results["error_report"] = error_handler.generate_error_report()

    return results

# Recovery strategies for specific operations
class RecoveryStrategies:
    """Collection of recovery strategies for common failures."""

    @staticmethod
    def retry_with_backoff(func, max_retries: int = 3, base_delay: float = 1.0):
        """Retry function with exponential backoff."""
        import time

        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise

                delay = base_delay * (2 ** attempt)
                time.sleep(delay)

    @staticmethod
    def fallback_encoding(file_path: Path, encodings: List[str] = None):
        """Try multiple encodings for file reading."""
        if encodings is None:
            encodings = ['utf-8', 'latin-1', 'cp1252', 'ascii']

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read(), encoding
            except UnicodeDecodeError:
                continue

        raise UnicodeDecodeError(f"Could not decode {file_path} with any encoding")

    @staticmethod
    def safe_subprocess_call(cmd: List[str], timeout: int = 30):
        """Safe subprocess execution with timeout and error handling."""
        import subprocess

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return -1, "", str(e)
```

## 📋 TODO Items & Future Enhancements

### High Priority (Immediate Implementation Needed)

- [ ] **Test Coverage Analysis Script** (`analyze_test_coverage.py`)

  - Implement comprehensive coverage analysis across all test categories
  - Gap identification in test coverage with actionable recommendations
  - Coverage trend analysis over time with historical data
  - Integration with CI/CD pipelines for automated reporting

- [ ] **Detailed Test Analysis Script** (`detailed_test_analysis.py`)
  - Deep-dive test analysis including performance metrics
  - Test execution time analysis with bottleneck identification
  - Test reliability metrics and failure pattern analysis
  - Test quality scoring with improvement suggestions

### Medium Priority (Enhanced Functionality)

- [ ] **Dependency Analysis and Update Script**

  - Automated dependency vulnerability scanning
  - Update recommendation system with compatibility checks
  - License compliance validation
  - Dependency tree analysis and optimization

- [ ] **Code Complexity Analysis Script**

  - Cyclomatic complexity measurement and reporting
  - Cognitive complexity analysis for maintainability
  - Technical debt assessment with prioritized recommendations
  - Refactoring opportunity identification

- [ ] **Performance Profiling Automation**
  - Automated performance benchmarking for critical paths
  - Memory usage analysis and optimization suggestions
  - I/O operation profiling and bottleneck detection
  - Performance regression detection between commits

### Low Priority (Nice-to-Have Features)

- [ ] **Documentation Generation Script**

  - Automated API documentation generation from docstrings
  - Architectural documentation extraction from code structure
  - Example code generation from test cases
  - Documentation consistency validation

- [ ] **License Header Management Script**

  - Automated license header insertion and updates
  - Copyright year maintenance across files
  - License compliance verification
  - Multi-license project support

- [ ] **Environment Setup Automation Script**
  - Automated development environment setup
  - Dependency installation verification
  - Configuration template generation
  - Environment consistency validation

### Research & Investigation

- [ ] **AI-Powered Code Analysis**

  - Integration with AI models for advanced code review
  - Automated refactoring suggestions using ML
  - Pattern recognition for architectural improvements
  - Natural language code documentation generation

- [ ] **Advanced Metrics Dashboard**
  - Real-time code quality metrics visualization
  - Technical debt trend analysis
  - Team productivity analytics
  - Code review efficiency metrics

## 📚 Related Documentation

### Core Framework Documentation

- [**Hexagonal Architecture Guide**](../docs/architecture/flext-architecture-standards.md) - Architecture principles and patterns
- [**Testing Framework**](../src/flext/testing/README.md) - Comprehensive testing infrastructure
- [**Development Workflow**](../docs/guides/) - Development process and best practices

### Infrastructure & Deployment

- [**CI/CD Pipeline**](../.github/workflows/) - Continuous integration and deployment setup
- [**Deployment Automation**](../src/flext/infra/deployment/) - Production deployment scripts
- [**Observability**](../src/flext/infra/observability/) - Monitoring and logging infrastructure

### Code Quality & Standards

- [**Code Quality Standards**](../docs/architecture/) - Coding standards and guidelines
- [**Security Guidelines**](../SECURITY.md) - Security best practices and protocols
- [**Troubleshooting Guide**](../docs/TROUBLESHOOTING_GUIDE.md) - Common issues and solutions

### Examples & Tutorials

- [**Basic Examples**](../examples/basic/README.md) - Getting started with FLX
- [**Advanced Examples**](../examples/advanced/README.md) - Enterprise patterns and complex scenarios
- [**Plugin Development**](../examples/plugins/) - Custom adapter and plugin creation

---

## 🎯 Summary

The FLX Scripts & Utilities collection provides a comprehensive suite of tools for maintaining code quality, enforcing architectural standards, and automating development workflows. Built with a zero-tolerance philosophy for code violations, these scripts ensure production-ready code quality through:

- **Zero-tolerance compliance validation** with automated fixes
- **Advanced import analysis and consolidation** for cleaner codebases
- **Comprehensive duplication detection** with architectural compliance
- **High-performance parallel processing** for scalable operations
- **Intelligent caching systems** for optimal performance
- **Robust error handling** with recovery strategies
- **Production-ready CI/CD integration** for automated quality gates

These tools embody the UNIX philosophy of doing one thing well while providing the power and flexibility needed for enterprise-grade Python development in hexagonal architecture environments.
