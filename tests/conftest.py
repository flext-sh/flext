"""Centralized pytest configuration for FLEXT workspace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import tempfile
from collections.abc import Generator, Mapping, Sequence
from pathlib import Path
from typing import Union

import pytest
from flext_core import FlextContainer, FlextLogger, FlextResult
from flext_ldif import FlextLdif, FlextLdifModels
from flext_ldif.constants import FlextLdifConstants
from flext_tests import (
    FlextTestsBuilders,
    FlextTestsDomains,
    FlextTestsFactories,
    FlextTestsMatchers,
)

TestDataValue = Union[
    str, int, float, bool, list["TestDataValue"], dict[str, "TestDataValue"]
]
TestDataDict = dict[str, TestDataValue]


def _convert_value_to_test_data(value: object) -> TestDataValue:
    """Convert a single value to TestDataValue through type narrowing."""
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        return [_convert_value_to_test_data(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _convert_value_to_test_data(v) for k, v in value.items()}
    return str(value)


def _convert_to_test_data(data: Mapping[str, object]) -> TestDataDict:
    """Convert Mapping to TestDataDict through type narrowing."""
    result: TestDataDict = {}
    for key, value in data.items():
        result[key] = _convert_value_to_test_data(value)
    return result


class FileManager:
    """Simple file manager for tests."""

    def __init__(self, temp_dir: Path) -> None:
        """Initialize FileManager with temporary directory."""
        super().__init__()
        self.temp_dir = temp_dir

    def create_file(self, filename: str, content: str) -> Path:
        """Create a temporary file with content."""
        file_path = self.temp_dir / filename
        _ = file_path.write_text(content, encoding="utf-8")
        return file_path


# =============================================================================
# CORE FLEXT FIXTURES
# =============================================================================


@pytest.fixture
def flext_container() -> FlextContainer:
    """Provide FlextContainer instance for tests."""
    return FlextContainer()


@pytest.fixture
def flext_logger() -> FlextLogger:
    """Provide FlextLogger instance for tests."""
    return FlextLogger(__name__)


@pytest.fixture
def flext_result_success() -> FlextResult[dict[str, Union[str, int, float, bool]]]:
    """Provide successful FlextResult for tests."""
    return FlextResult.ok({"success": True})


@pytest.fixture
def temp_dir() -> Generator[Path]:
    """Provide temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def test_file_manager(temp_dir: Path) -> FileManager:
    """Provide test file manager for tests."""
    return FileManager(temp_dir)


@pytest.fixture
def flext_result_failure() -> FlextResult[dict[str, Union[str, int, float, bool]]]:
    """Provide failed FlextResult for tests."""
    return FlextResult.fail("Test error")


# =============================================================================
# TEST DATA FACTORIES
# =============================================================================


@pytest.fixture
def flext_builders() -> FlextTestsBuilders:
    """Provide FlextTestsBuilders for test data creation."""
    return FlextTestsBuilders()


@pytest.fixture
def flext_domains() -> FlextTestsDomains:
    """Provide FlextTestsDomains for test data creation."""
    return FlextTestsDomains()


@pytest.fixture
def flext_factories() -> FlextTestsFactories:
    """Provide FlextTestsFactories for test data creation."""
    return FlextTestsFactories()


@pytest.fixture
def flext_matchers() -> FlextTestsMatchers:
    """Provide FlextTestsMatchers for test assertions."""
    return FlextTestsMatchers()


# =============================================================================
# TEST DATA FIXTURES
# =============================================================================


@pytest.fixture
def test_user_data() -> dict[str, Union[str, bool]]:
    """Provide test user data."""
    return FlextTestsDomains.create_user()


@pytest.fixture
def test_config_data() -> TestDataDict:
    """Provide test configuration data."""
    return _convert_to_test_data(FlextTestsDomains.create_configuration())


@pytest.fixture
def test_service_data() -> TestDataDict:
    """Provide test service data."""
    return _convert_to_test_data(FlextTestsDomains.create_service())


@pytest.fixture
def test_payload_data() -> TestDataDict:
    """Provide test payload data."""
    return _convert_to_test_data(FlextTestsDomains.create_payload())


@pytest.fixture
def batch_user_data() -> list[dict[str, Union[str, bool]]]:
    """Provide batch of test user data."""
    return FlextTestsDomains.batch_users(5)


# =============================================================================
# VALIDATION TEST DATA
# =============================================================================


@pytest.fixture
def valid_email_cases() -> list[tuple[str, bool]]:
    """Provide valid email test cases."""
    return FlextTestsDomains.valid_email_cases()


@pytest.fixture
def invalid_email_cases() -> list[tuple[str, bool]]:
    """Provide invalid email test cases."""
    return FlextTestsDomains.invalid_email_cases()


@pytest.fixture
def valid_ages() -> list[int]:
    """Provide valid age test cases."""
    return FlextTestsDomains.valid_ages()


@pytest.fixture
def invalid_ages() -> list[int]:
    """Provide invalid age test cases."""
    return FlextTestsDomains.invalid_ages()


# =============================================================================
# REALISTIC TEST DATA
# =============================================================================


@pytest.fixture
def user_registration_data() -> dict[str, Union[str, bool]]:
    """Provide realistic user registration data."""
    return FlextTestsDomains.create_user()


@pytest.fixture
def order_data() -> TestDataDict:
    """Provide realistic order data."""
    return _convert_to_test_data(FlextTestsDomains.create_payload(data_type="order"))


@pytest.fixture
def api_response_data() -> TestDataDict:
    """Provide realistic API response data."""
    return _convert_to_test_data(FlextTestsDomains.api_response_data())


# =============================================================================
# TEMPORARY RESOURCES
# =============================================================================


@pytest.fixture
def temp_directory() -> Generator[Path]:
    """Provide temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def temp_file(temp_directory: Path) -> Path:
    """Provide temporary file for tests."""
    return temp_directory / "test_file.txt"


@pytest.fixture
def test_file_manager_alternative(temp_directory: Path) -> FileManager:
    """Provide test file manager for tests."""
    return FileManager(temp_directory)


# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "e2e: marks tests as end-to-end tests")
    config.addinivalue_line("markers", "slow: marks tests as slow tests")
    config.addinivalue_line("markers", "docker: marks tests that require Docker")
    config.addinivalue_line("markers", "oracle: marks tests specific to Oracle")
    config.addinivalue_line("markers", "performance: marks tests as performance tests")
    config.addinivalue_line("markers", "stress: marks tests as stress tests")
    config.addinivalue_line("markers", "resilience: marks tests as resilience tests")
    config.addinivalue_line("markers", "integrity: marks tests as integrity tests")
    config.addinivalue_line("markers", "edge_cases: marks tests as edge case tests")
    config.addinivalue_line("markers", "real: marks tests using real functionality")
    config.addinivalue_line("markers", "auth: marks tests as authentication tests")


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add unit marker to tests in unit directories
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)

        # Add integration marker to tests in integration directories
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Add e2e marker to tests in e2e directories
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)

        # Add docker marker to tests that mention docker
        if "docker" in str(item.fspath).lower():
            item.add_marker(pytest.mark.docker)

        # Add oracle marker to tests that mention oracle
        if "oracle" in str(item.fspath).lower():
            item.add_marker(pytest.mark.oracle)


@pytest.fixture
def sample_ldif_entries() -> str:
    """Sample LDIF entries for testing."""
    return """dn: cn=John Doe,ou=people,dc=example,dc=com
objectClass: inetOrgPerson
cn: John Doe
sn: Doe
mail: john.doe@example.com

dn: cn=Jane Smith,ou=people,dc=example,dc=com
objectClass: inetOrgPerson
cn: Jane Smith
sn: Smith
mail: jane.smith@example.com

dn: ou=groups,dc=example,dc=com
objectClass: organizationalUnit
ou: groups
description: Groups organizational unit
"""


# LDIF fixtures with real data (imports moved to top)


@pytest.fixture
def real_ldif_user_entry() -> str:
    """Real LDIF entry for a user with complete attributes."""
    return """dn: cn=John Doe,ou=people,dc=example,dc=com
objectClass: top
objectClass: person
objectClass: inetOrgPerson
objectClass: organizationalPerson
cn: John Doe
sn: Doe
givenName: John
mail: john.doe@example.com
uid: jdoe
userPassword: {SSHA}encryptedpassword
telephoneNumber: +1-555-1234
facsimileTelephoneNumber: +1-555-5678
street: 123 Main St
l: New York
st: NY
postalCode: 10001
c: US
description: Software Engineer
employeeNumber: 12345
employeeType: full-time
"""


@pytest.fixture
def real_ldif_group_entry() -> str:
    """Real LDIF entry for a group with complete attributes."""
    return """dn: cn=developers,ou=groups,dc=example,dc=com
objectClass: top
objectClass: groupOfNames
objectClass: groupOfUniqueNames
cn: developers
description: Development team group
member: cn=John Doe,ou=people,dc=example,dc=com
member: cn=Jane Smith,ou=people,dc=example,dc=com
uniqueMember: cn=John Doe,ou=people,dc=example,dc=com
uniqueMember: cn=Jane Smith,ou=people,dc=example,dc=com
"""


@pytest.fixture
def real_ldif_ou_entry() -> str:
    """Real LDIF entry for an organizational unit."""
    return """dn: ou=people,dc=example,dc=com
objectClass: top
objectClass: organizationalUnit
ou: people
description: People organizational unit
"""


@pytest.fixture
def real_ldif_multiple_entries() -> str:
    """Real LDIF with multiple entries separated by blank lines."""
    return """dn: dc=example,dc=com
objectClass: top
objectClass: domain
dc: example

dn: ou=people,dc=example,dc=com
objectClass: top
objectClass: organizationalUnit
ou: people

dn: cn=John Doe,ou=people,dc=example,dc=com
objectClass: top
objectClass: person
objectClass: inetOrgPerson
cn: John Doe
sn: Doe
mail: john.doe@example.com

dn: cn=Jane Smith,ou=people,dc=example,dc=com
objectClass: top
objectClass: person
objectClass: inetOrgPerson
cn: Jane Smith
sn: Smith
mail: jane.smith@example.com
"""


@pytest.fixture
def real_ldif_entry_with_special_chars() -> str:
    """Real LDIF entry with special characters requiring base64 encoding."""
    return """dn: cn=Test User,ou=people,dc=example,dc=com
objectClass: inetOrgPerson
cn: Test User
sn: User
mail: test@example.com
description:: VGhpcyBpcyBhIHRlc3Qgd2l0aCBzcGVjaWFsIGNoYXJzOiDwn5iA
"""


@pytest.fixture
def real_ldif_entry_with_long_value() -> str:
    """Real LDIF entry with long attribute value requiring folding."""
    return """dn: cn=Long Value Test,ou=people,dc=example,dc=com
objectClass: inetOrgPerson
cn: Long Value Test
sn: Test
description: This is a very long description that should be folded according to RFC 2849 when it exceeds 76 characters in length
"""


@pytest.fixture
def flext_ldif_instance() -> FlextLdif:
    """Provide FlextLdif instance for tests."""
    return FlextLdif.get_instance()


@pytest.fixture
def parsed_user_entry(
    flext_ldif_instance: FlextLdif, real_ldif_user_entry: str
) -> FlextLdifModels.Entry:
    """Parse real LDIF user entry into Entry model."""
    result = flext_ldif_instance.parse(real_ldif_user_entry)
    assert result.is_success, f"Failed to parse user entry: {result.error}"
    entries = result.unwrap()
    assert len(entries) == 1, f"Expected 1 entry, got {len(entries)}"
    return entries[0]


@pytest.fixture
def parsed_multiple_entries(
    flext_ldif_instance: FlextLdif, real_ldif_multiple_entries: str
) -> Sequence[FlextLdifModels.Entry]:
    """Parse real LDIF with multiple entries."""
    result = flext_ldif_instance.parse(real_ldif_multiple_entries)
    assert result.is_success, f"Failed to parse entries: {result.error}"
    return result.unwrap()


@pytest.fixture
def write_format_options_default() -> FlextLdifModels.WriteFormatOptions:
    """Default write format options for LDIF generation."""
    return FlextLdifModels.WriteFormatOptions(
        include_version_header=True,
        include_timestamps=False,
        sort_attributes=False,
        write_empty_values=True,
        line_width=76,
        fold_long_lines=True,
    )


@pytest.fixture
def write_format_options_custom() -> FlextLdifModels.WriteFormatOptions:
    """Custom write format options for LDIF generation."""
    return FlextLdifModels.WriteFormatOptions(
        include_version_header=True,
        include_timestamps=True,
        sort_attributes=True,
        write_empty_values=False,
        line_width=80,
        fold_long_lines=True,
    )


@pytest.fixture
def server_types() -> list[str]:
    """List of supported LDAP server types for testing."""
    return [
        FlextLdifConstants.ServerTypes.OID,
        FlextLdifConstants.ServerTypes.OUD,
        FlextLdifConstants.ServerTypes.OPENLDAP,
        FlextLdifConstants.ServerTypes.AD,
        FlextLdifConstants.ServerTypes.DS_389,
    ]
