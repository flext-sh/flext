"""Comprehensive tests for FlextLdapModels - targeting 100% coverage.

This test module provides comprehensive coverage for all LDAP model
implementations, focusing on validation, edge cases, and business logic.
"""

from datetime import UTC, datetime
from typing import cast

import pytest
from flext_ldap.models import FlextLdapModels
from flext_ldap.typings import FlextLdapTypes
from pydantic import SecretStr, ValidationError


def create_ldap_user_with_defaults(
    dn: str,
    cn: str,
    uid: str,
    sn: str,
    given_name: str,
    mail: str,
    user_password: SecretStr,
    telephone_number: str | None = None,
    mobile: str | None = None,
    department: str | None = None,
    title: str | None = None,
    organization: str | None = None,
    organizational_unit: str | None = None,
    created_timestamp: datetime | None = None,
    modified_timestamp: datetime | None = None,
    additional_attributes: dict[str, list[str]] | None = None,
    object_classes: list[str] | None = None,
) -> FlextLdapModels.LdapUser:
    """Helper function to create LdapUser with default optional parameters."""
    return FlextLdapModels.LdapUser(
        dn=dn,
        cn=cn,
        uid=uid,
        sn=sn,
        given_name=given_name,
        mail=mail,
        user_password=str(user_password),
        telephone_number=telephone_number,
        mobile=mobile,
        department=department,
        title=title,
        organization=organization,
        organizational_unit=organizational_unit,
        object_classes=object_classes or ["person", "organizationalPerson", "inetOrgPerson"],
        additional_attributes=additional_attributes or {},
        created_timestamp=created_timestamp,
        modified_timestamp=modified_timestamp,
    )


def create_group_with_defaults(
    dn: str,
    cn: str,
    gid_number: int | None = None,
    description: str | None = None,
    created_timestamp: datetime | None = None,
    modified_timestamp: datetime | None = None,
    member_dns: list[str] | None = None,
    unique_member_dns: list[str] | None = None,
) -> FlextLdapModels.Group:
    """Helper function to create Group with default optional parameters."""
    return FlextLdapModels.Group(
        dn=dn,
        cn=cn,
        gid_number=gid_number,
        description=description,
        object_classes=["groupOfNames", "top"],
        member_dns=member_dns or [],
        unique_member_dns=unique_member_dns or [],
        additional_attributes={},
        created_timestamp=created_timestamp,
        modified_timestamp=modified_timestamp,
    )


def create_entry_with_defaults(
    dn: str,
    attributes: dict[str, object],
    object_classes: list[str],
    **kwargs: object,
) -> FlextLdapModels.Entry:
    """Helper function to create Entry with default optional parameters."""
    defaults: dict[str, object] = {
        "created_timestamp": None,
        "modified_timestamp": None,
    }
    defaults.update(kwargs)
    return FlextLdapModels.Entry(
        dn=dn,
        attributes=cast("FlextLdapTypes.Entry.AttributeDict", attributes),
        object_classes=list(object_classes),
        created_timestamp=cast("datetime | None", defaults.get("created_timestamp")),
        modified_timestamp=cast("datetime | None", defaults.get("modified_timestamp")),
    )


def create_search_request_with_defaults(
    base_dn: str,
    filter_str: str,
    scope: str,
    page_size: int,
    paged_cookie: bytes | None = None,
    attributes: list[str] | None = None,
    time_limit: int = 60,
    size_limit: int = 1000,
    deref_aliases: str = "never",
    *,
    types_only: bool = False,
) -> FlextLdapModels.SearchRequest:
    """Helper function to create SearchRequest with default optional parameters."""
    return FlextLdapModels.SearchRequest(
        base_dn=base_dn,
        filter=filter_str,
        scope=scope,
        page_size=page_size,
        paged_cookie=paged_cookie,
        attributes=attributes,
        time_limit=time_limit,
        size_limit=size_limit,
        deref_aliases=deref_aliases,
        types_only=types_only,
    )


def create_search_response_with_defaults(
    entries: list[dict[str, object]],
    total_count: int,
    page_size: int,
    paged_cookie: bytes | None = None,
    result_code: int = 0,
    result_message: str = "Success",
    *,
    has_more: bool = False,
) -> FlextLdapModels.SearchResponse:
    """Helper function to create SearchResponse with default optional parameters."""
    _ = page_size
    return FlextLdapModels.SearchResponse(
        entries=entries,
        total_count=total_count,
        result_code=result_code,
        result_description=result_message,
        matched_dn="",
        next_cookie=paged_cookie,
        entries_returned=total_count,
        time_elapsed=0.0,
        has_more=has_more,
    )


def create_user_request_with_defaults(
    dn: str,
    uid: str,
    cn: str,
    sn: str,
    given_name: str,
    mail: str,
    user_password: SecretStr,
    **kwargs: object,
) -> FlextLdapModels.CreateUserRequest:
    """Helper function to create CreateUserRequest with default optional parameters."""
    defaults: dict[str, object] = {
        "telephone_number": None,
        "description": None,
        "department": None,
        "title": None,
        "organization": None,
    }
    defaults.update(kwargs)
    return FlextLdapModels.CreateUserRequest(
        dn=dn,
        uid=uid,
        cn=cn,
        sn=sn,
        given_name=given_name,
        mail=mail,
        user_password=str(user_password),
        telephone_number=cast("str | None", defaults.get("telephone_number")),
        description=cast("str | None", defaults.get("description")),
        department=cast("str | None", defaults.get("department")),
        title=cast("str | None", defaults.get("title")),
        organization=cast("str | None", defaults.get("organization")),
    )


def create_group_request_with_defaults(
    dn: str,
    cn: str,
    description: str | None = None,
    **kwargs: object,
) -> FlextLdapModels.CreateGroupRequest:
    """Helper function to create CreateGroupRequest with default optional parameters."""
    defaults: dict[str, object] = {
        "members": [],
    }
    defaults.update(kwargs)
    return FlextLdapModels.CreateGroupRequest(
        dn=dn,
        cn=cn,
        description=description,
        members=cast("list[str] | None", defaults.get("members")),
    )


def create_connection_info_with_defaults(
    server: str,
    port: int,
    bind_dn: str,
    bind_password: SecretStr,
    timeout: int = 30,
    pool_size: int = 10,
    pool_keepalive: int = 60,
    ca_certs_file: str | None = None,
    **kwargs: object,
) -> FlextLdapModels.ConnectionInfo:
    """Helper function to create ConnectionInfo with default optional parameters."""
    defaults: dict[str, object] = {}
    defaults.update(kwargs)
    return FlextLdapModels.ConnectionInfo(
        server=server,
        port=port,
        bind_dn=bind_dn,
        bind_password=str(bind_password),
        timeout=timeout,
        pool_size=pool_size,
        pool_keepalive=pool_keepalive,
        ca_certs_file=ca_certs_file,
        use_ssl=cast("bool", defaults.get("use_ssl", False)),
    )


def create_ldap_error_with_defaults(
    error_code: int,
    error_message: str,
    operation: str,
    matched_dn: str = "",
    target_dn: str = "",
    **kwargs: object,
) -> FlextLdapModels.LdapError:
    """Helper function to create LdapError with default optional parameters."""
    defaults: dict[str, object] = {}
    defaults.update(kwargs)
    return FlextLdapModels.LdapError(
        error_code=error_code,
        error_message=error_message,
        operation=operation,
        matched_dn=matched_dn,
        target_dn=target_dn,
        server_info=cast("dict[str, object]", defaults.get("server_info", {})),
        timestamp=cast("datetime", defaults.get("timestamp", datetime.now(UTC))),
    )


def create_operation_result_with_defaults(
    success: bool,
    result_code: int,
    result_message: str,
    operation_type: str,
    duration_ms: float,
    **kwargs: object,
) -> FlextLdapModels.OperationResult:
    """Helper function to create OperationResult with default optional parameters."""
    defaults: dict[str, object] = {
        "target_dn": "",
    }
    defaults.update(kwargs)
    return FlextLdapModels.OperationResult(
        success=success,
        result_code=result_code,
        result_message=result_message,
        operation_type=operation_type,
        duration_ms=duration_ms,
        target_dn=cast("str", defaults.get("target_dn", "")),
        data=cast("dict[str, object]", defaults.get("data", {})),
        timestamp=cast("datetime", defaults.get("timestamp", datetime.now(UTC))),
    )


def create_connection_config_with_defaults(
    server: str,
    port: int,
    use_ssl: bool,
    bind_dn: str,
    bind_password: SecretStr,
    timeout: int = 30,
    **kwargs: object,
) -> FlextLdapModels.ConnectionConfig:
    """Helper function to create ConnectionConfig with default optional parameters."""
    defaults: dict[str, object] = {}
    defaults.update(kwargs)
    return FlextLdapModels.ConnectionConfig(
        server=server,
        port=port,
        use_ssl=use_ssl,
        bind_dn=bind_dn,
        bind_password=str(bind_password),
        timeout=timeout,
    )


class TestDistinguishedName:
    """Test DistinguishedName model."""

    def test_create_valid_dn(self) -> None:
        """Test creating valid DN."""
        dn = FlextLdapModels.DistinguishedName(
            value="uid=test,ou=users,dc=example,dc=com"
        )
        assert dn.value == "uid=test,ou=users,dc=example,dc=com"

    def test_create_factory_method(self) -> None:
        """Test DN factory method returns FlextResult."""
        result = FlextLdapModels.DistinguishedName.create(
            "uid=test,ou=users,dc=example,dc=com"
        )
        assert result.is_success
        assert result.value.value == "uid=test,ou=users,dc=example,dc=com"

    def test_rdn_property(self) -> None:
        """Test RDN extraction."""
        dn = FlextLdapModels.DistinguishedName(
            value="uid=test,ou=users,dc=example,dc=com"
        )
        assert dn.rdn == "uid=test"

    def test_empty_dn_validation(self) -> None:
        """Test empty DN validation - ValueError."""
        with pytest.raises(ValueError, match="Distinguished Name cannot be empty"):
            FlextLdapModels.DistinguishedName(value="")

    def test_whitespace_dn_validation(self) -> None:
        """Test whitespace DN validation - raises ValueError in __post_init__."""
        with pytest.raises(ValueError, match="Distinguished Name cannot be empty"):
            FlextLdapModels.DistinguishedName(value="   ")

    def test_none_dn_validation(self) -> None:
        """Test None DN validation - ValueError for None."""
        with pytest.raises(ValueError, match="Distinguished Name cannot be empty"):
            FlextLdapModels.DistinguishedName(value=cast("str", None))

    def test_post_init_no_normalization(self) -> None:
        """Test DN preserves whitespace - no automatic normalization."""
        dn = FlextLdapModels.DistinguishedName(
            value="  uid=test,ou=users,dc=example,dc=com  "
        )
        assert dn.value == "  uid=test,ou=users,dc=example,dc=com  "


class TestFilter:
    """Test Filter model."""

    def test_create_valid_filter(self) -> None:
        """Test creating valid filter."""
        filter_obj = FlextLdapModels.Filter(expression="(objectClass=person)")
        assert filter_obj.expression == "(objectClass=person)"

    def test_equals_factory_method(self) -> None:
        """Test equals factory method."""
        filter_obj = FlextLdapModels.Filter.equals("uid", "testuser")
        assert filter_obj.expression == "(uid=testuser)"

    def test_starts_with_factory_method(self) -> None:
        """Test starts_with factory method."""
        filter_obj = FlextLdapModels.Filter.starts_with("cn", "Test")
        assert filter_obj.expression == "(cn=Test*)"

    def test_object_class_factory_method(self) -> None:
        """Test object_class factory method."""
        filter_obj = FlextLdapModels.Filter.object_class("person")
        assert filter_obj.expression == "(objectClass=person)"

    def test_invalid_filter_validation(self) -> None:
        """Test invalid filter validation - raises ValueError in __post_init__."""
        with pytest.raises(
            ValueError, match="LDAP filter must be enclosed in parentheses"
        ):
            FlextLdapModels.Filter(expression="invalid_filter")

    def test_empty_filter_validation(self) -> None:
        """Test empty filter validation - raises ValueError in __post_init__."""
        with pytest.raises(ValueError, match="LDAP filter cannot be empty"):
            FlextLdapModels.Filter(expression="")

    def test_filter_normalization(self) -> None:
        """Test filter with whitespace - no normalization, strict validation."""
        with pytest.raises(
            ValueError, match="LDAP filter must be enclosed in parentheses"
        ):
            FlextLdapModels.Filter(expression="  (uid=test)  ")


class TestScope:
    """Test Scope model."""

    def test_valid_scope_values(self) -> None:
        """Test valid scope values."""
        scopes = ["base", "onelevel", "subtree"]
        for scope_val in scopes:
            scope = FlextLdapModels.Scope(value=scope_val)
            assert scope.value == scope_val

    def test_scope_constants(self) -> None:
        """Test scope constants."""
        assert FlextLdapModels.Scope.BASE == "base"
        assert FlextLdapModels.Scope.ONELEVEL == "onelevel"
        assert FlextLdapModels.Scope.SUBTREE == "subtree"

    def test_base_factory_method(self) -> None:
        """Test base factory method."""
        scope = FlextLdapModels.Scope.base()
        assert scope.value == "base"

    def test_onelevel_factory_method(self) -> None:
        """Test onelevel factory method."""
        scope = FlextLdapModels.Scope.onelevel()
        assert scope.value == "onelevel"

    def test_subtree_factory_method(self) -> None:
        """Test subtree factory method."""
        scope = FlextLdapModels.Scope.subtree()
        assert scope.value == "subtree"

    def test_invalid_scope_validation(self) -> None:
        """Test invalid scope validation."""
        with pytest.raises(ValueError, match="Invalid scope"):
            FlextLdapModels.Scope(value="invalid")

    def test_empty_scope_validation(self) -> None:
        """Test empty scope validation."""
        with pytest.raises(ValueError):
            FlextLdapModels.Scope(value="")


class TestLdapUser:
    """Test LdapUser model."""

    @pytest.fixture
    def valid_user_data(self) -> dict[str, str | SecretStr]:
        """Valid user data for testing."""
        return {
            "dn": "uid=test,ou=users,dc=example,dc=com",
            "cn": "Test User",
            "uid": "testuser",
            "sn": "User",
            "given_name": "Test",
            "mail": "test@example.com",
            "user_password": SecretStr("password123"),
        }

    def test_create_valid_user(
        self, valid_user_data: dict[str, str | SecretStr]
    ) -> None:
        """Test creating valid user."""
        user = create_ldap_user_with_defaults(
            dn=str(valid_user_data["dn"]),
            cn=str(valid_user_data["cn"]),
            uid=str(valid_user_data["uid"]),
            sn=str(valid_user_data["sn"]),
            given_name=str(valid_user_data["given_name"]),
            mail=str(valid_user_data["mail"]),
            user_password=SecretStr(str(valid_user_data["user_password"])),
        )
        assert user.dn == valid_user_data["dn"]
        assert user.cn == valid_user_data["cn"]
        assert user.uid == valid_user_data["uid"]

    def test_user_with_all_fields(
        self, valid_user_data: dict[str, str | SecretStr]
    ) -> None:
        """Test user with all optional fields."""
        user = create_ldap_user_with_defaults(
            dn=str(valid_user_data["dn"]),
            cn=str(valid_user_data["cn"]),
            uid=str(valid_user_data["uid"]),
            sn=str(valid_user_data["sn"]),
            given_name=str(valid_user_data["given_name"]),
            mail=str(valid_user_data["mail"]),
            user_password=SecretStr(str(valid_user_data["user_password"])),
            telephone_number="123-456-7890",
            mobile="987-654-3210",
            department="IT",
            title="Developer",
            organization="Example Corp",
            organizational_unit="Engineering",
        )
        assert user.telephone_number == "123-456-7890"
        assert user.department == "IT"

    def test_dn_validation(self, valid_user_data: dict[str, str | SecretStr]) -> None:
        """Test DN validation."""
        # Test empty DN
        with pytest.raises(ValidationError):
            create_ldap_user_with_defaults(
                dn="",
                cn=str(valid_user_data["cn"]),
                uid=str(valid_user_data["uid"]),
                sn=str(valid_user_data["sn"]),
                given_name=str(valid_user_data["given_name"]),
                mail=str(valid_user_data["mail"]),
                user_password=SecretStr(str(valid_user_data["user_password"])),
            )

        # Test whitespace DN
        with pytest.raises(ValidationError):
            create_ldap_user_with_defaults(
                dn="   ",
                cn=str(valid_user_data["cn"]),
                uid=str(valid_user_data["uid"]),
                sn=str(valid_user_data["sn"]),
                given_name=str(valid_user_data["given_name"]),
                mail=str(valid_user_data["mail"]),
                user_password=SecretStr(str(valid_user_data["user_password"])),
            )

    def test_email_validation(
        self, valid_user_data: dict[str, str | SecretStr]
    ) -> None:
        """Test email validation."""
        # Test invalid email
        with pytest.raises(ValidationError):
            create_ldap_user_with_defaults(
                dn=str(valid_user_data["dn"]),
                cn=str(valid_user_data["cn"]),
                uid=str(valid_user_data["uid"]),
                sn=str(valid_user_data["sn"]),
                given_name=str(valid_user_data["given_name"]),
                mail="invalid_email",
                user_password=SecretStr(str(valid_user_data["user_password"])),
            )

        # Test valid email variations
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "test+tag@example.org",
        ]
        for email in valid_emails:
            user = create_ldap_user_with_defaults(
                dn=str(valid_user_data["dn"]),
                cn=str(valid_user_data["cn"]),
                uid=str(valid_user_data["uid"]),
                sn=str(valid_user_data["sn"]),
                given_name=str(valid_user_data["given_name"]),
                mail=email,
                user_password=valid_user_data["user_password"],
            )
            assert user.mail == email

    def test_cn_validation(self, valid_user_data: dict[str, str | SecretStr]) -> None:
        """Test CN validation."""
        with pytest.raises(ValidationError):
            create_ldap_user_with_defaults(
                dn=str(valid_user_data["dn"]),
                cn="",
                uid=str(valid_user_data["uid"]),
                sn=str(valid_user_data["sn"]),
                given_name=str(valid_user_data["given_name"]),
                mail=str(valid_user_data["mail"]),
                user_password=valid_user_data["user_password"],
            )

    def test_object_classes_validation(
        self, valid_user_data: dict[str, str | SecretStr]
    ) -> None:
        """Test object classes validation."""
        # Test with custom object classes
        user = create_ldap_user_with_defaults(
            dn=str(valid_user_data["dn"]),
            cn=str(valid_user_data["cn"]),
            uid=str(valid_user_data["uid"]),
            sn=str(valid_user_data["sn"]),
            given_name=str(valid_user_data["given_name"]),
            mail=str(valid_user_data["mail"]),
            user_password=valid_user_data["user_password"],
            object_classes=["person", "organizationalPerson"],
        )
        assert "person" in user.object_classes

        # Test empty object classes should use defaults
        user = create_ldap_user_with_defaults(
            dn=str(valid_user_data["dn"]),
            cn=str(valid_user_data["cn"]),
            uid=str(valid_user_data["uid"]),
            sn=str(valid_user_data["sn"]),
            given_name=str(valid_user_data["given_name"]),
            mail=str(valid_user_data["mail"]),
            user_password=valid_user_data["user_password"],
        )
        assert len(user.object_classes) > 0

    def test_business_rules_validation(
        self, valid_user_data: dict[str, object]
    ) -> None:
        """Test business rules validation."""
        user = create_ldap_user_with_defaults(
            dn=str(valid_user_data["dn"]),
            cn=str(valid_user_data["cn"]),
            uid=str(valid_user_data["uid"]),
            sn=str(valid_user_data["sn"]),
            given_name=str(valid_user_data["given_name"]),
            mail=str(valid_user_data["mail"]),
            user_password=valid_user_data["user_password"],
        )
        # This should not raise an exception
        assert user.uid == "testuser"

    def test_get_attribute(self, valid_user_data: dict[str, str | SecretStr]) -> None:
        """Test get_attribute method - gets from additional_attributes only."""
        user = create_ldap_user_with_defaults(
            dn=str(valid_user_data["dn"]),
            cn=str(valid_user_data["cn"]),
            uid=str(valid_user_data["uid"]),
            sn=str(valid_user_data["sn"]),
            given_name=str(valid_user_data["given_name"]),
            mail=str(valid_user_data["mail"]),
            user_password=valid_user_data["user_password"],
            additional_attributes={"custom_field": "custom_value"},
        )
        assert user.get_attribute("custom_field") == "custom_value"
        assert user.get_attribute("nonexistent") is None

    def test_set_attribute(self, valid_user_data: dict[str, str | SecretStr]) -> None:
        """Test set_attribute method."""
        user = create_ldap_user_with_defaults(
            dn=str(valid_user_data["dn"]),
            cn=str(valid_user_data["cn"]),
            uid=str(valid_user_data["uid"]),
            sn=str(valid_user_data["sn"]),
            given_name=str(valid_user_data["given_name"]),
            mail=str(valid_user_data["mail"]),
            user_password=valid_user_data["user_password"],
        )
        user.set_attribute("title", "Senior Developer")
        assert user.additional_attributes["title"] == "Senior Developer"

    def test_get_rdn(self, valid_user_data: dict[str, str | SecretStr]) -> None:
        """Test get_rdn method."""
        user = create_ldap_user_with_defaults(
            dn=str(valid_user_data["dn"]),
            cn=str(valid_user_data["cn"]),
            uid=str(valid_user_data["uid"]),
            sn=str(valid_user_data["sn"]),
            given_name=str(valid_user_data["given_name"]),
            mail=str(valid_user_data["mail"]),
            user_password=valid_user_data["user_password"],
        )
        rdn = user.get_rdn()
        assert rdn == "uid=test"

    def test_get_parent_dn(self, valid_user_data: dict[str, str | SecretStr]) -> None:
        """Test get_parent_dn method."""
        user = create_ldap_user_with_defaults(
            dn=str(valid_user_data["dn"]),
            cn=str(valid_user_data["cn"]),
            uid=str(valid_user_data["uid"]),
            sn=str(valid_user_data["sn"]),
            given_name=str(valid_user_data["given_name"]),
            mail=str(valid_user_data["mail"]),
            user_password=valid_user_data["user_password"],
        )
        parent_dn = user.get_parent_dn()
        assert parent_dn == "ou=users,dc=example,dc=com"


class TestGroup:
    """Test Group model."""

    @pytest.fixture
    def valid_group_data(self) -> dict[str, str | int]:
        """Valid group data for testing."""
        return {
            "dn": "cn=testgroup,ou=groups,dc=example,dc=com",
            "cn": "testgroup",
            "gid_number": 1000,
            "description": "Test Group",
        }

    def test_create_valid_group(self, valid_group_data: dict[str, str | int]) -> None:
        """Test creating valid group."""
        group = create_group_with_defaults(
            dn=str(valid_group_data["dn"]),
            cn=str(valid_group_data["cn"]),
            gid_number=int(valid_group_data["gid_number"]),
            description=str(valid_group_data["description"]),
        )
        assert group.dn == valid_group_data["dn"]
        assert group.cn == valid_group_data["cn"]
        assert group.gid_number == valid_group_data["gid_number"]

    def test_group_with_members(self, valid_group_data: dict[str, object]) -> None:
        """Test group with members."""
        group = create_group_with_defaults(
            dn=str(valid_group_data["dn"]),
            cn=str(valid_group_data["cn"]),
            gid_number=int(valid_group_data["gid_number"]),
            description=str(valid_group_data["description"]),
            member_dns=["uid=user1,ou=users,dc=example,dc=com"],
            unique_member_dns=["uid=user2,ou=users,dc=example,dc=com"],
        )
        assert len(group.member_dns) == 1
        assert len(group.unique_member_dns) == 1

    def test_dn_validation(self, valid_group_data: dict[str, str | int]) -> None:
        """Test DN validation."""
        with pytest.raises(ValidationError):
            create_group_with_defaults(
                dn="",
                cn=str(valid_group_data["cn"]),
                gid_number=int(valid_group_data["gid_number"]),
                description=str(valid_group_data["description"]),
            )

    def test_business_rules_validation(
        self, valid_group_data: dict[str, str | int]
    ) -> None:
        """Test business rules validation."""
        group = create_group_with_defaults(
            dn=str(valid_group_data["dn"]),
            cn=str(valid_group_data["cn"]),
            gid_number=int(valid_group_data["gid_number"]),
            description=str(valid_group_data["description"]),
        )
        # This should not raise an exception
        assert group.cn == "testgroup"

    def test_has_member(self, valid_group_data: dict[str, str | int]) -> None:
        """Test has_member method."""
        member_dn = "uid=test,ou=users,dc=example,dc=com"
        group = create_group_with_defaults(
            dn=str(valid_group_data["dn"]),
            cn=str(valid_group_data["cn"]),
            gid_number=int(valid_group_data["gid_number"]),
            description=str(valid_group_data["description"]),
            member_dns=[member_dn],
        )

        assert group.has_member(member_dn)
        assert not group.has_member("uid=other,ou=users,dc=example,dc=com")

    def test_add_member(self, valid_group_data: dict[str, object]) -> None:
        """Test add_member method."""
        group = create_group_with_defaults(
            dn=str(valid_group_data["dn"]),
            cn=str(valid_group_data["cn"]),
            gid_number=int(valid_group_data["gid_number"]),
            description=str(valid_group_data["description"]),
        )
        member_dn = "uid=test,ou=users,dc=example,dc=com"

        group.add_member(member_dn)
        assert member_dn in group.member_dns

        # Test adding duplicate member
        group.add_member(member_dn)
        assert group.member_dns.count(member_dn) == 1

    def test_remove_member(self, valid_group_data: dict[str, str | int]) -> None:
        """Test remove_member method."""
        member_dn = "uid=test,ou=users,dc=example,dc=com"
        group = create_group_with_defaults(
            dn=str(valid_group_data["dn"]),
            cn=str(valid_group_data["cn"]),
            gid_number=int(valid_group_data["gid_number"]),
            description=str(valid_group_data["description"]),
            member_dns=[member_dn],
        )

        group.remove_member(member_dn)
        assert member_dn not in group.member_dns

        # Test removing non-existent member
        group.remove_member("uid=nonexistent,ou=users,dc=example,dc=com")


class TestEntry:
    """Test Entry model."""

    @pytest.fixture
    def valid_entry_data(self) -> dict[str, str | dict[str, str] | list[str]]:
        """Valid entry data for testing."""
        return {
            "dn": "uid=test,ou=entries,dc=example,dc=com",
            "attributes": {"uid": "test", "cn": "Test Entry"},
            "object_classes": ["top", "person"],
        }

    def test_create_valid_entry(
        self, valid_entry_data: dict[str, str | dict[str, str] | list[str]]
    ) -> None:
        """Test creating valid entry."""
        entry = create_entry_with_defaults(
            dn=valid_entry_data["dn"],
            attributes=valid_entry_data["attributes"],
            object_classes=valid_entry_data["object_classes"],
        )
        assert entry.dn == valid_entry_data["dn"]
        assert entry.attributes == valid_entry_data["attributes"]

    def test_dn_validation(self, valid_entry_data: dict[str, object]) -> None:
        """Test DN validation."""
        with pytest.raises(ValidationError):
            create_entry_with_defaults(
                dn="",
                attributes=valid_entry_data["attributes"],
                object_classes=valid_entry_data["object_classes"],
            )

    def test_get_attribute(
        self, valid_entry_data: dict[str, str | dict[str, str] | list[str]]
    ) -> None:
        """Test get_attribute method - returns list."""
        entry = create_entry_with_defaults(
            dn=valid_entry_data["dn"],
            attributes=valid_entry_data["attributes"],
            object_classes=valid_entry_data["object_classes"],
        )
        assert entry.get_attribute("uid") == ["test"]
        assert entry.get_attribute("nonexistent") is None

    def test_get_attribute_with_default(
        self, valid_entry_data: dict[str, str | dict[str, str] | list[str]]
    ) -> None:
        """Test get_attribute returns None for non-existent attributes."""
        entry = create_entry_with_defaults(
            dn=valid_entry_data["dn"],
            attributes=valid_entry_data["attributes"],
            object_classes=valid_entry_data["object_classes"],
        )
        assert entry.get_attribute("nonexistent") is None

    def test_set_attribute(
        self, valid_entry_data: dict[str, str | dict[str, str] | list[str]]
    ) -> None:
        """Test set_attribute method."""
        entry = create_entry_with_defaults(
            dn=valid_entry_data["dn"],
            attributes=valid_entry_data["attributes"],
            object_classes=valid_entry_data["object_classes"],
        )
        entry.set_attribute("mail", "test@example.com")
        assert entry.attributes["mail"] == "test@example.com"

    def test_has_attribute(
        self, valid_entry_data: dict[str, str | dict[str, str] | list[str]]
    ) -> None:
        """Test has_attribute method."""
        entry = create_entry_with_defaults(
            dn=valid_entry_data["dn"],
            attributes=valid_entry_data["attributes"],
            object_classes=valid_entry_data["object_classes"],
        )
        assert entry.has_attribute("uid")
        assert not entry.has_attribute("nonexistent")

    def test_get_rdn(
        self, valid_entry_data: dict[str, str | dict[str, str] | list[str]]
    ) -> None:
        """Test get_rdn method."""
        entry = create_entry_with_defaults(
            dn=valid_entry_data["dn"],
            attributes=valid_entry_data["attributes"],
            object_classes=valid_entry_data["object_classes"],
        )
        rdn = entry.get_rdn()
        assert rdn == "uid=test"


class TestSearchRequest:
    """Test SearchRequest model."""

    def test_create_valid_search_request(self) -> None:
        """Test creating valid search request."""
        request = create_search_request_with_defaults(
            base_dn="ou=users,dc=example,dc=com",
            filter_str="(objectClass=person)",
            scope="subtree",
            page_size=100,
            paged_cookie=None,
        )
        assert request.base_dn == "ou=users,dc=example,dc=com"
        assert request.filter_str == "(objectClass=person)"
        assert request.scope == "subtree"

    def test_base_dn_validation(self) -> None:
        """Test base DN validation."""
        with pytest.raises(ValidationError):
            create_search_request_with_defaults(
                base_dn="",
                filter_str="(objectClass=person)",
                scope="subtree",
                page_size=100,
                paged_cookie=None,
            )

    def test_filter_validation(self) -> None:
        """Test filter validation."""
        with pytest.raises(ValidationError):
            create_search_request_with_defaults(
                base_dn="ou=users,dc=example,dc=com",
                filter_str="invalid_filter",
                scope="subtree",
                page_size=100,
                paged_cookie=None,
            )

    def test_filter_parentheses_validation(self) -> None:
        """Test filter parentheses validation."""
        with pytest.raises(ValidationError):
            create_search_request_with_defaults(
                base_dn="ou=users,dc=example,dc=com",
                filter_str="objectClass=person",  # Missing parentheses
                scope="subtree",
                page_size=100,
                paged_cookie=None,
            )

    def test_create_user_search_factory(self) -> None:
        """Test create_user_search factory method."""
        request = FlextLdapModels.SearchRequest.create_user_search(
            uid="testuser", base_dn="ou=users,dc=example,dc=com"
        )
        assert "uid=testuser" in request.filter_str
        assert request.base_dn == "ou=users,dc=example,dc=com"

    def test_create_group_search_factory(self) -> None:
        """Test create_group_search factory method."""
        request = FlextLdapModels.SearchRequest.create_group_search(
            cn="testgroup", base_dn="ou=groups,dc=example,dc=com"
        )
        assert "cn=testgroup" in request.filter_str
        assert request.base_dn == "ou=groups,dc=example,dc=com"

    def test_search_request_with_paging(self) -> None:
        """Test search request with paging parameters."""
        request = FlextLdapModels.SearchRequest(
            base_dn="ou=users,dc=example,dc=com",
            filter="(objectClass=person)",
            page_size=100,
            paged_cookie=b"cookie_data",
        )
        assert request.page_size == 100
        assert request.paged_cookie == b"cookie_data"


class TestSearchResponse:
    """Test SearchResponse model."""

    def test_create_search_response(self) -> None:
        """Test creating search response."""
        entries = [{"dn": "uid=test,ou=users,dc=example,dc=com", "uid": "test"}]
        response = create_search_response_with_defaults(
            entries=entries,
            total_count=1,
            page_size=100,
            paged_cookie=None,
            result_code=0,
            result_message="Success",
            has_more=False,
        )
        assert len(response.entries) == 1
        assert response.total_count == 1
        assert response.result_code == 0

    def test_entries_returned_validator(self) -> None:
        """Test entries_returned field validator."""
        entries = [{"dn": "uid=test,ou=users,dc=example,dc=com"}]
        response = create_search_response_with_defaults(
            entries=entries,
            total_count=1,
            page_size=100,
            paged_cookie=None,
            result_code=0,
            result_message="Success",
            has_more=False,
        )
        # The validator should auto-calculate from entries list
        assert response.entries_returned == len(entries)


class TestCreateUserRequest:
    """Test CreateUserRequest model."""

    @pytest.fixture
    def valid_create_user_data(self) -> dict[str, str]:
        """Valid create user data."""
        return {
            "dn": "uid=newuser,ou=users,dc=example,dc=com",
            "uid": "newuser",
            "cn": "New User",
            "sn": "User",
            "given_name": "New",
            "mail": "newuser@example.com",
            "user_password": "ValidPass123!",
        }

    def test_create_valid_request(self, valid_create_user_data: dict[str, str]) -> None:
        """Test creating valid create user request."""
        request = create_user_request_with_defaults(
            dn=valid_create_user_data["dn"],
            uid=valid_create_user_data["uid"],
            cn=valid_create_user_data["cn"],
            sn=valid_create_user_data["sn"],
            given_name=valid_create_user_data["given_name"],
            mail=valid_create_user_data["mail"],
            user_password=SecretStr(valid_create_user_data["user_password"]),
        )
        assert request.uid == "newuser"
        assert request.cn == "New User"

    def test_dn_validation(self, valid_create_user_data: dict[str, object]) -> None:
        """Test DN validation."""
        with pytest.raises(ValidationError):
            create_user_request_with_defaults(
                dn="invalid_dn",
                uid=valid_create_user_data["uid"],
                cn=valid_create_user_data["cn"],
                sn=valid_create_user_data["sn"],
                given_name=valid_create_user_data["given_name"],
                mail=valid_create_user_data["mail"],
                user_password=SecretStr(valid_create_user_data["user_password"]),
            )

    def test_email_validation(self, valid_create_user_data: dict[str, object]) -> None:
        """Test email validation."""
        with pytest.raises(ValidationError):
            create_user_request_with_defaults(
                dn=valid_create_user_data["dn"],
                uid=valid_create_user_data["uid"],
                cn=valid_create_user_data["cn"],
                sn=valid_create_user_data["sn"],
                given_name=valid_create_user_data["given_name"],
                mail="invalid_email",
                user_password=SecretStr(valid_create_user_data["user_password"]),
            )

    def test_password_validation(
        self, valid_create_user_data: dict[str, object]
    ) -> None:
        """Test password validation."""
        # Test with weak password
        with pytest.raises(ValidationError):
            create_user_request_with_defaults(
                dn=valid_create_user_data["dn"],
                uid=valid_create_user_data["uid"],
                cn=valid_create_user_data["cn"],
                sn=valid_create_user_data["sn"],
                given_name=valid_create_user_data["given_name"],
                mail=valid_create_user_data["mail"],
                user_password="123",
            )

    def test_required_string_validation(
        self, valid_create_user_data: dict[str, object]
    ) -> None:
        """Test required string validation."""
        with pytest.raises(ValidationError):
            create_user_request_with_defaults(
                dn=valid_create_user_data["dn"],
                uid=valid_create_user_data["uid"],
                cn="",
                sn=valid_create_user_data["sn"],
                given_name=valid_create_user_data["given_name"],
                mail=valid_create_user_data["mail"],
                user_password=SecretStr(valid_create_user_data["user_password"]),
            )

    def test_business_rules_validation(
        self, valid_create_user_data: dict[str, object]
    ) -> None:
        """Test business rules validation."""
        request = create_user_request_with_defaults(
            dn=valid_create_user_data["dn"],
            uid=valid_create_user_data["uid"],
            cn=valid_create_user_data["cn"],
            sn=valid_create_user_data["sn"],
            given_name=valid_create_user_data["given_name"],
            mail=valid_create_user_data["mail"],
            user_password=SecretStr(valid_create_user_data["user_password"]),
        )
        # This should not raise an exception
        assert request.uid == "newuser"

    def test_to_user_entity(self, valid_create_user_data: dict[str, object]) -> None:
        """Test to_user_entity method."""
        request = create_user_request_with_defaults(
            dn=valid_create_user_data["dn"],
            uid=valid_create_user_data["uid"],
            cn=valid_create_user_data["cn"],
            sn=valid_create_user_data["sn"],
            given_name=valid_create_user_data["given_name"],
            mail=valid_create_user_data["mail"],
            user_password=SecretStr(valid_create_user_data["user_password"]),
        )
        user = request.to_user_entity()
        assert isinstance(user, FlextLdapModels.LdapUser)
        assert user.uid == request.uid
        assert user.cn == request.cn


class TestCreateGroupRequest:
    """Test CreateGroupRequest model."""

    @pytest.fixture
    def valid_create_group_data(self) -> dict[str, str]:
        """Valid create group data."""
        return {
            "dn": "cn=newgroup,ou=groups,dc=example,dc=com",
            "cn": "newgroup",
            "description": "New Group",
        }

    def test_create_valid_request(
        self, valid_create_group_data: dict[str, str]
    ) -> None:
        """Test creating valid create group request."""
        request = create_group_request_with_defaults(
            dn=valid_create_group_data["dn"],
            cn=valid_create_group_data["cn"],
            description=valid_create_group_data["description"],
        )
        assert request.dn == "cn=newgroup,ou=groups,dc=example,dc=com"
        assert request.cn == "newgroup"
        assert request.description == "New Group"

    def test_dn_validation(self, valid_create_group_data: dict[str, object]) -> None:
        """Test DN validation."""
        with pytest.raises(ValidationError):
            create_group_request_with_defaults(
                dn="invalid_dn",
                cn=valid_create_group_data["cn"],
                description=valid_create_group_data["description"],
            )

    def test_cn_validation(self, valid_create_group_data: dict[str, object]) -> None:
        """Test CN validation."""
        with pytest.raises(ValidationError):
            create_group_request_with_defaults(
                dn=valid_create_group_data["dn"],
                cn="",
                description=valid_create_group_data["description"],
            )


class TestConnectionInfo:
    """Test ConnectionInfo model."""

    def test_create_connection_info(self) -> None:
        """Test creating connection info."""
        conn_info = create_connection_info_with_defaults(
            server="ldap.example.com",
            port=389,
            bind_dn="cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com",
            bind_password=SecretStr("password"),
            timeout=30,
            pool_size=10,
            pool_keepalive=60,
            ca_certs_file=None,
        )
        assert conn_info.server == "ldap.example.com"
        assert conn_info.port == 389

    def test_server_validation(self) -> None:
        """Test server validation."""
        with pytest.raises(ValidationError):
            create_connection_info_with_defaults(
                server="",
                port=389,
                bind_dn="cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com",
                bind_password=SecretStr("password"),
                timeout=30,
                pool_size=10,
                pool_keepalive=60,
                ca_certs_file=None,
            )

    def test_port_validation(self) -> None:
        """Test port validation."""
        with pytest.raises(ValidationError):
            create_connection_info_with_defaults(
                server="ldap.example.com",
                port=0,  # Invalid port
                bind_dn="cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com",
                bind_password=SecretStr("password"),
                timeout=30,
                pool_size=10,
                pool_keepalive=60,
                ca_certs_file=None,
            )


class TestLdapError:
    """Test LdapError model."""

    def test_create_ldap_error(self) -> None:
        """Test creating LDAP error."""
        error = create_ldap_error_with_defaults(
            error_code=49,
            error_message="Invalid credentials",
            operation="bind",
            matched_dn="",
            target_dn="",
        )
        assert error.error_code == 49
        assert error.error_message == "Invalid credentials"

    def test_error_code_validation(self) -> None:
        """Test error code validation."""
        with pytest.raises(ValidationError):
            create_ldap_error_with_defaults(
                error_code=-1,  # Invalid error code
                error_message="Error",
                operation="bind",
                matched_dn="",
                target_dn="",
            )


class TestOperationResult:
    """Test OperationResult model."""

    def test_create_operation_result(self) -> None:
        """Test creating operation result."""
        result = create_operation_result_with_defaults(
            success=True,
            result_code=0,
            result_message="Success",
            operation_type="search",
            duration_ms=100.5,
        )
        assert result.success is True
        assert result.result_code == 0

    def test_success_result_factory(self) -> None:
        """Test success_result factory method."""
        result = FlextLdapModels.OperationResult.success_result(
            operation_type="search",
            target_dn="ou=users,dc=example,dc=com",
            data={"entries": []},
            duration_ms=50.0,
        )
        assert result.success is True
        assert result.result_code == 0

    def test_error_result_factory(self) -> None:
        """Test error_result factory method."""
        result = FlextLdapModels.OperationResult.error_result(
            operation_type="search",
            error_code=32,
            error_message="No such object",
            target_dn="ou=missing,dc=example,dc=com",
            duration_ms=25.0,
        )
        assert result.success is False
        assert result.result_code == 32


class TestConnectionConfig:
    """Test ConnectionConfig model."""

    def test_create_connection_config(self) -> None:
        """Test creating connection config."""
        config = create_connection_config_with_defaults(
            server="ldap.example.com",
            port=389,
            use_ssl=False,
            bind_dn="cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com",
            bind_password=SecretStr("password"),
            timeout=30,
        )
        assert config.server == "ldap.example.com"
        assert config.port == 389
        assert config.use_ssl is False


class TestFlextLdapModels:
    """Test FlextLdapModels unified class."""

    def test_unified_class_structure(self) -> None:
        """Test that FlextLdapModels contains all expected nested classes."""
        expected_classes = [
            "DistinguishedName",
            "Filter",
            "Scope",
            "LdapUser",
            "Group",
            "Entry",
            "SearchRequest",
            "SearchResponse",
            "CreateUserRequest",
            "CreateGroupRequest",
            "ConnectionInfo",
            "LdapError",
            "OperationResult",
            "ConnectionConfig",
        ]

        for class_name in expected_classes:
            assert hasattr(FlextLdapModels, class_name)
            assert callable(getattr(FlextLdapModels, class_name))

    def test_model_inheritance(self) -> None:
        """Test that all models inherit from BaseModel."""
        from pydantic import BaseModel

        models_to_test = [
            FlextLdapModels.LdapUser,
            FlextLdapModels.Group,
            FlextLdapModels.Entry,
            FlextLdapModels.SearchRequest,
            FlextLdapModels.SearchResponse,
        ]

        for model_class in models_to_test:
            instance = model_class.__new__(model_class)
            assert isinstance(instance, BaseModel)

    def test_model_config_validation(self) -> None:
        """Test that models have proper validation configuration."""
        models_to_test = [
            FlextLdapModels.LdapUser,
            FlextLdapModels.Group,
            FlextLdapModels.SearchRequest,
        ]

        for model_class in models_to_test:
            assert hasattr(model_class, "model_config")
            config = model_class.model_config
            # In Pydantic v2, model_config is a dict
            assert config.get("validate_assignment") is True or config.get(
                "validate_assignment", False
            )
