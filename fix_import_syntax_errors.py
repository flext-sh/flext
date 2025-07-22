#!/usr/bin/env python3
"""Fix specific import syntax errors introduced by ServiceResult standardization."""

import os
import re
import sys
from pathlib import Path


def fix_import_syntax_errors(file_path: Path) -> tuple[bool, str]:
    """Fix malformed import statements."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Fix the specific malformed imports we found
        fixes = [
            # Fix "import ServiceResult" -> "ServiceResult"
            (r"from flext_core\.domain\.shared_types import import ServiceResult",
             "from flext_core.domain.shared_types import ServiceResult"),
            (r"from flext_core\.domain\.shared_types import import Environment",
             "from flext_core.domain.shared_types import Environment"),
            (r"from flext_core\.domain\.shared_types import import ResultStatus",
             "from flext_core.domain.shared_types import ResultStatus"),
            # Fix any other "import import" patterns
            (r"import import (\w+)", r"import \1"),
        ]

        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            return True, f"Fixed import syntax errors in {file_path}"

        return False, f"No import syntax errors found in {file_path}"

    except Exception as e:
        return False, f"Error processing {file_path}: {e}"


def main() -> None:
    """Fix import syntax errors across workspace."""
    workspace_root = Path("/home/marlonsc/flext")

    # Files we know have issues from the error output
    files_with_issues = [
        # flext-db-oracle files
        "flext-db-oracle/src/flext_db_oracle/application/services.py",
        "flext-db-oracle/src/flext_db_oracle/patterns/oracle_patterns.py",
        "flext-db-oracle/src/flext_db_oracle/schema/analyzer.py",
        "flext-db-oracle/src/flext_db_oracle/schema/ddl.py",
        "flext-db-oracle/src/flext_db_oracle/simple_api.py",
        "flext-db-oracle/src/flext_db_oracle/utils/database_utils.py",
        "flext-db-oracle/tests/integration/test_oracle_integration.py",
        "flext-db-oracle/tests/unit/test_application_services.py",
        # flext-meltano files
        "flext-meltano/src/flext_meltano/extensions.py",
        # algar-oud-mig files
        "algar-oud-mig/tests/unit/test_domain_types.py",
        "algar-oud-mig/tests/unit/test_handlers.py",
        "algar-oud-mig/tests/unit/test_idempotent_migration_service.py",
        "algar-oud-mig/tests/unit/test_oud_connection_service.py",
        "algar-oud-mig/tests/unit/test_schema_service.py",
        "algar-oud-mig/tests/unit/test_services.py",
        # gruponos-meltano-native files
        "gruponos-meltano-native/src/gruponos_meltano_native/orchestrator.py",
        "gruponos-meltano-native/tests/unit/test_basic_integration.py",
    ]

    fixed_count = 0
    failed_count = 0


    for file_path in files_with_issues:
        full_path = workspace_root / file_path
        if full_path.exists():
            success, message = fix_import_syntax_errors(full_path)
            if success:
                fixed_count += 1
            else:
                failed_count += 1
        else:
            failed_count += 1

    if failed_count > 0:
        sys.exit(1)



if __name__ == "__main__":
    main()
