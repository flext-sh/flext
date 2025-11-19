"""LDIF test fixtures with real data for comprehensive testing.

Provides real LDIF data fixtures for testing LDIF generation, parsing,
and transformation operations without mocks or patches.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Sequence

import pytest
from flext_ldif import FlextLdif, FlextLdifModels
from flext_ldif.constants import FlextLdifConstants


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
        FlextLdifConstants.ServerTypes.DS389,
    ]
