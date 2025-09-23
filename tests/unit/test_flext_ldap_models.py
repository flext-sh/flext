"""Comprehensive tests for FlextLdapModels - targeting 100% coverage.

This test module provides comprehensive coverage for all LDAP model
implementations, focusing on validation, edge cases, and business logic.
"""

import pytest
from flext_ldap.models import FlextLdapModels
from pydantic import SecretStr, ValidationError


class TestDistinguishedName:
    """Test DistinguishedName model."""

    def test_create_valid_dn(self) -> None:
        """Test creating valid DN."""
        dn = FlextLdapModels.DistinguishedName("uid=test,ou=users,dc=example,dc=com")
        assert dn.value == "uid=test,ou=users,dc=example,dc=com"

    def test_create_factory_method(self) -> None:
        """Test DN factory method."""
        dn = FlextLdapModels.DistinguishedName.create(
            "uid=test,ou=users,dc=example,dc=com"
        )
        assert dn.value == "uid=test,ou=users,dc=example,dc=com"

    def test_rdn_property(self) -> None:
        """Test RDN extraction."""
        dn = FlextLdapModels.DistinguishedName("uid=test,ou=users,dc=example,dc=com")
        assert dn.rdn == "uid=test"

    def test_empty_dn_validation(self) -> None:
        """Test empty DN validation."""
        with pytest.raises(ValidationError):
            FlextLdapModels.DistinguishedName("")

    def test_whitespace_dn_validation(self) -> None:
        """Test whitespace DN validation."""
        with pytest.raises(ValidationError):
            FlextLdapModels.DistinguishedName("   ")

    def test_none_dn_validation(self) -> None:
        """Test None DN validation."""
        with pytest.raises(ValidationError):
            FlextLdapModels.DistinguishedName(None)

    def test_post_init_normalization(self) -> None:
        """Test post_init normalization."""
        dn = FlextLdapModels.DistinguishedName(
            "  uid=test,ou=users,dc=example,dc=com  "
        )
        assert dn.value == "uid=test,ou=users,dc=example,dc=com"


class TestFilter:
    """Test Filter model."""

    def test_create_valid_filter(self) -> None:
        """Test creating valid filter."""
        filter_obj = FlextLdapModels.Filter("(objectClass=person)")
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
        """Test invalid filter validation."""
        with pytest.raises(ValidationError):
            FlextLdapModels.Filter("invalid_filter")

    def test_empty_filter_validation(self) -> None:
        """Test empty filter validation."""
        with pytest.raises(ValidationError):
            FlextLdapModels.Filter("")

    def test_filter_normalization(self) -> None:
        """Test filter normalization."""
        filter_obj = FlextLdapModels.Filter("  (uid=test)  ")
        assert filter_obj.expression == "(uid=test)"


class TestScope:
    """Test Scope model."""

    def test_valid_scope_values(self) -> None:
        """Test valid scope values."""
        scopes = ["base", "onelevel", "subtree"]
        for scope_val in scopes:
            scope = FlextLdapModels.Scope(scope_val)
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
        with pytest.raises(ValidationError):
            FlextLdapModels.Scope("invalid")

    def test_empty_scope_validation(self) -> None:
        """Test empty scope validation."""
        with pytest.raises(ValidationError):
            FlextLdapModels.Scope("")


class TestLdapUser:
    """Test LdapUser model."""

    @pytest.fixture
    def valid_user_data(self):
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

    def test_create_valid_user(self, valid_user_data) -> None:
        """Test creating valid user."""
        user = FlextLdapModels.LdapUser(**valid_user_data)
        assert user.dn == valid_user_data["dn"]
        assert user.cn == valid_user_data["cn"]
        assert user.uid == valid_user_data["uid"]

    def test_user_with_all_fields(self, valid_user_data) -> None:
        """Test user with all optional fields."""
        full_data = {
            **valid_user_data,
            "telephone_number": "123-456-7890",
            "mobile": "987-654-3210",
            "department": "IT",
            "title": "Developer",
            "organization": "Example Corp",
            "organizational_unit": "Engineering",
        }
        user = FlextLdapModels.LdapUser(**full_data)
        assert user.telephone_number == "123-456-7890"
        assert user.department == "IT"

    def test_dn_validation(self, valid_user_data) -> None:
        """Test DN validation."""
        # Test empty DN
        with pytest.raises(ValidationError):
            invalid_data = {**valid_user_data, "dn": ""}
            FlextLdapModels.LdapUser(**invalid_data)

        # Test whitespace DN
        with pytest.raises(ValidationError):
            invalid_data = {**valid_user_data, "dn": "   "}
            FlextLdapModels.LdapUser(**invalid_data)

    def test_email_validation(self, valid_user_data) -> None:
        """Test email validation."""
        # Test invalid email
        with pytest.raises(ValidationError):
            invalid_data = {**valid_user_data, "mail": "invalid_email"}
            FlextLdapModels.LdapUser(**invalid_data)

        # Test valid email variations
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "test+tag@example.org",
        ]
        for email in valid_emails:
            data = {**valid_user_data, "mail": email}
            user = FlextLdapModels.LdapUser(**data)
            assert user.mail == email

    def test_cn_validation(self, valid_user_data) -> None:
        """Test CN validation."""
        with pytest.raises(ValidationError):
            invalid_data = {**valid_user_data, "cn": ""}
            FlextLdapModels.LdapUser(**invalid_data)

    def test_object_classes_validation(self, valid_user_data) -> None:
        """Test object classes validation."""
        # Test with custom object classes
        data = {**valid_user_data, "object_classes": ["person", "organizationalPerson"]}
        user = FlextLdapModels.LdapUser(**data)
        assert "person" in user.object_classes

        # Test empty object classes should use defaults
        user = FlextLdapModels.LdapUser(**valid_user_data)
        assert len(user.object_classes) > 0

    def test_business_rules_validation(self, valid_user_data) -> None:
        """Test business rules validation."""
        user = FlextLdapModels.LdapUser(**valid_user_data)
        # This should not raise an exception
        assert user.uid == "testuser"

    def test_get_attribute(self, valid_user_data) -> None:
        """Test get_attribute method."""
        user = FlextLdapModels.LdapUser(**valid_user_data)
        assert user.get_attribute("cn") == "Test User"
        assert user.get_attribute("nonexistent") is None

    def test_set_attribute(self, valid_user_data) -> None:
        """Test set_attribute method."""
        user = FlextLdapModels.LdapUser(**valid_user_data)
        user.set_attribute("title", "Senior Developer")
        assert user.additional_attributes["title"] == "Senior Developer"

    def test_get_rdn(self, valid_user_data) -> None:
        """Test get_rdn method."""
        user = FlextLdapModels.LdapUser(**valid_user_data)
        rdn = user.get_rdn()
        assert rdn == "uid=test"

    def test_get_parent_dn(self, valid_user_data) -> None:
        """Test get_parent_dn method."""
        user = FlextLdapModels.LdapUser(**valid_user_data)
        parent_dn = user.get_parent_dn()
        assert parent_dn == "ou=users,dc=example,dc=com"


class TestGroup:
    """Test Group model."""

    @pytest.fixture
    def valid_group_data(self):
        """Valid group data for testing."""
        return {
            "dn": "cn=testgroup,ou=groups,dc=example,dc=com",
            "cn": "testgroup",
            "gid_number": 1000,
            "description": "Test Group",
        }

    def test_create_valid_group(self, valid_group_data) -> None:
        """Test creating valid group."""
        group = FlextLdapModels.Group(**valid_group_data)
        assert group.dn == valid_group_data["dn"]
        assert group.cn == valid_group_data["cn"]
        assert group.gid_number == valid_group_data["gid_number"]

    def test_group_with_members(self, valid_group_data) -> None:
        """Test group with members."""
        data = {
            **valid_group_data,
            "member_dns": ["uid=user1,ou=users,dc=example,dc=com"],
            "unique_member_dns": ["uid=user2,ou=users,dc=example,dc=com"],
        }
        group = FlextLdapModels.Group(**data)
        assert len(group.member_dns) == 1
        assert len(group.unique_member_dns) == 1

    def test_dn_validation(self, valid_group_data) -> None:
        """Test DN validation."""
        with pytest.raises(ValidationError):
            invalid_data = {**valid_group_data, "dn": ""}
            FlextLdapModels.Group(**invalid_data)

    def test_business_rules_validation(self, valid_group_data) -> None:
        """Test business rules validation."""
        group = FlextLdapModels.Group(**valid_group_data)
        # This should not raise an exception
        assert group.cn == "testgroup"

    def test_has_member(self, valid_group_data) -> None:
        """Test has_member method."""
        member_dn = "uid=test,ou=users,dc=example,dc=com"
        data = {**valid_group_data, "member_dns": [member_dn]}
        group = FlextLdapModels.Group(**data)

        assert group.has_member(member_dn)
        assert not group.has_member("uid=other,ou=users,dc=example,dc=com")

    def test_add_member(self, valid_group_data) -> None:
        """Test add_member method."""
        group = FlextLdapModels.Group(**valid_group_data)
        member_dn = "uid=test,ou=users,dc=example,dc=com"

        group.add_member(member_dn)
        assert member_dn in group.member_dns

        # Test adding duplicate member
        group.add_member(member_dn)
        assert group.member_dns.count(member_dn) == 1

    def test_remove_member(self, valid_group_data) -> None:
        """Test remove_member method."""
        member_dn = "uid=test,ou=users,dc=example,dc=com"
        data = {**valid_group_data, "member_dns": [member_dn]}
        group = FlextLdapModels.Group(**data)

        group.remove_member(member_dn)
        assert member_dn not in group.member_dns

        # Test removing non-existent member
        group.remove_member("uid=nonexistent,ou=users,dc=example,dc=com")


class TestEntry:
    """Test Entry model."""

    @pytest.fixture
    def valid_entry_data(self):
        """Valid entry data for testing."""
        return {
            "dn": "uid=test,ou=entries,dc=example,dc=com",
            "attributes": {"uid": "test", "cn": "Test Entry"},
            "object_classes": ["top", "person"],
        }

    def test_create_valid_entry(self, valid_entry_data) -> None:
        """Test creating valid entry."""
        entry = FlextLdapModels.Entry(**valid_entry_data)
        assert entry.dn == valid_entry_data["dn"]
        assert entry.attributes == valid_entry_data["attributes"]

    def test_dn_validation(self, valid_entry_data) -> None:
        """Test DN validation."""
        with pytest.raises(ValidationError):
            invalid_data = {**valid_entry_data, "dn": ""}
            FlextLdapModels.Entry(**invalid_data)

    def test_get_attribute(self, valid_entry_data) -> None:
        """Test get_attribute method."""
        entry = FlextLdapModels.Entry(**valid_entry_data)
        assert entry.get_attribute("uid") == "test"
        assert entry.get_attribute("nonexistent") is None

    def test_get_attribute_with_default(self, valid_entry_data) -> None:
        """Test get_attribute with default value."""
        entry = FlextLdapModels.Entry(**valid_entry_data)
        assert entry.get_attribute("nonexistent", "default") == "default"

    def test_set_attribute(self, valid_entry_data) -> None:
        """Test set_attribute method."""
        entry = FlextLdapModels.Entry(**valid_entry_data)
        entry.set_attribute("mail", "test@example.com")
        assert entry.attributes["mail"] == "test@example.com"

    def test_has_attribute(self, valid_entry_data) -> None:
        """Test has_attribute method."""
        entry = FlextLdapModels.Entry(**valid_entry_data)
        assert entry.has_attribute("uid")
        assert not entry.has_attribute("nonexistent")

    def test_get_rdn(self, valid_entry_data) -> None:
        """Test get_rdn method."""
        entry = FlextLdapModels.Entry(**valid_entry_data)
        rdn = entry.get_rdn()
        assert rdn == "uid=test"


class TestSearchRequest:
    """Test SearchRequest model."""

    def test_create_valid_search_request(self) -> None:
        """Test creating valid search request."""
        request = FlextLdapModels.SearchRequest(
            base_dn="ou=users,dc=example,dc=com",
            filter="(objectClass=person)",
            scope="subtree",
        )
        assert request.base_dn == "ou=users,dc=example,dc=com"
        assert request.filter_str == "(objectClass=person)"
        assert request.scope == "subtree"

    def test_base_dn_validation(self) -> None:
        """Test base DN validation."""
        with pytest.raises(ValidationError):
            FlextLdapModels.SearchRequest(base_dn="", filter="(objectClass=person)")

    def test_filter_validation(self) -> None:
        """Test filter validation."""
        with pytest.raises(ValidationError):
            FlextLdapModels.SearchRequest(
                base_dn="ou=users,dc=example,dc=com", filter="invalid_filter"
            )

    def test_filter_parentheses_validation(self) -> None:
        """Test filter parentheses validation."""
        with pytest.raises(ValidationError):
            FlextLdapModels.SearchRequest(
                base_dn="ou=users,dc=example,dc=com",
                filter="objectClass=person",  # Missing parentheses
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
        response = FlextLdapModels.SearchResponse(
            entries=entries,
            total_count=1,
            result_code=0,
            result_description="Success",
            matched_dn="",
            next_cookie=None,
            entries_returned=1,
            time_elapsed=0.5,
        )
        assert len(response.entries) == 1
        assert response.total_count == 1
        assert response.result_code == 0

    def test_entries_returned_validator(self) -> None:
        """Test entries_returned field validator."""
        entries = [{"dn": "uid=test,ou=users,dc=example,dc=com"}]
        response = FlextLdapModels.SearchResponse(
            entries=entries,
            total_count=1,
            result_code=0,
            result_description="Success",
            matched_dn="",
            next_cookie=None,
            entries_returned=0,  # This should be auto-calculated
            time_elapsed=0.5,
        )
        # The validator should auto-calculate from entries list
        assert response.entries_returned == len(entries)


class TestCreateUserRequest:
    """Test CreateUserRequest model."""

    @pytest.fixture
    def valid_create_user_data(self):
        """Valid create user data."""
        return {
            "uid": "newuser",
            "cn": "New User",
            "sn": "User",
            "given_name": "New",
            "mail": "newuser@example.com",
            "user_password": SecretStr("password123"),
        }

    def test_create_valid_request(self, valid_create_user_data) -> None:
        """Test creating valid create user request."""
        request = FlextLdapModels.CreateUserRequest(**valid_create_user_data)
        assert request.uid == "newuser"
        assert request.cn == "New User"

    def test_dn_validation(self, valid_create_user_data) -> None:
        """Test DN validation."""
        data = {**valid_create_user_data, "dn": "invalid_dn"}
        with pytest.raises(ValidationError):
            FlextLdapModels.CreateUserRequest(**data)

    def test_email_validation(self, valid_create_user_data) -> None:
        """Test email validation."""
        data = {**valid_create_user_data, "mail": "invalid_email"}
        with pytest.raises(ValidationError):
            FlextLdapModels.CreateUserRequest(**data)

    def test_password_validation(self, valid_create_user_data) -> None:
        """Test password validation."""
        # Test with weak password
        data = {**valid_create_user_data, "user_password": SecretStr("123")}
        with pytest.raises(ValidationError):
            FlextLdapModels.CreateUserRequest(**data)

    def test_required_string_validation(self, valid_create_user_data) -> None:
        """Test required string validation."""
        data = {**valid_create_user_data, "cn": ""}
        with pytest.raises(ValidationError):
            FlextLdapModels.CreateUserRequest(**data)

    def test_business_rules_validation(self, valid_create_user_data) -> None:
        """Test business rules validation."""
        request = FlextLdapModels.CreateUserRequest(**valid_create_user_data)
        # This should not raise an exception
        assert request.uid == "newuser"

    def test_to_user_entity(self, valid_create_user_data) -> None:
        """Test to_user_entity method."""
        request = FlextLdapModels.CreateUserRequest(**valid_create_user_data)
        user = request.to_user_entity()
        assert isinstance(user, FlextLdapModels.LdapUser)
        assert user.uid == request.uid
        assert user.cn == request.cn


class TestCreateGroupRequest:
    """Test CreateGroupRequest model."""

    @pytest.fixture
    def valid_create_group_data(self):
        """Valid create group data."""
        return {"cn": "newgroup", "gid_number": 2000, "description": "New Group"}

    def test_create_valid_request(self, valid_create_group_data) -> None:
        """Test creating valid create group request."""
        request = FlextLdapModels.CreateGroupRequest(**valid_create_group_data)
        assert request.cn == "newgroup"
        assert request.gid_number == 2000

    def test_dn_validation(self, valid_create_group_data) -> None:
        """Test DN validation."""
        data = {**valid_create_group_data, "dn": "invalid_dn"}
        with pytest.raises(ValidationError):
            FlextLdapModels.CreateGroupRequest(**data)

    def test_cn_validation(self, valid_create_group_data) -> None:
        """Test CN validation."""
        data = {**valid_create_group_data, "cn": ""}
        with pytest.raises(ValidationError):
            FlextLdapModels.CreateGroupRequest(**data)


class TestConnectionInfo:
    """Test ConnectionInfo model."""

    def test_create_connection_info(self) -> None:
        """Test creating connection info."""
        conn_info = FlextLdapModels.ConnectionInfo(
            server="ldap.example.com",
            port=389,
            bind_dn="cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com",
            bind_password=SecretStr("password"),
        )
        assert conn_info.server == "ldap.example.com"
        assert conn_info.port == 389

    def test_server_validation(self) -> None:
        """Test server validation."""
        with pytest.raises(ValidationError):
            FlextLdapModels.ConnectionInfo(
                server="",
                port=389,
                bind_dn="cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com",
                bind_password=SecretStr("password"),
            )

    def test_port_validation(self) -> None:
        """Test port validation."""
        with pytest.raises(ValidationError):
            FlextLdapModels.ConnectionInfo(
                server="ldap.example.com",
                port=0,  # Invalid port
                bind_dn="cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com",
                bind_password=SecretStr("password"),
            )


class TestLdapError:
    """Test LdapError model."""

    def test_create_ldap_error(self) -> None:
        """Test creating LDAP error."""
        error = FlextLdapModels.LdapError(
            error_code=49, error_message="Invalid credentials", operation="bind"
        )
        assert error.error_code == 49
        assert error.error_message == "Invalid credentials"

    def test_error_code_validation(self) -> None:
        """Test error code validation."""
        with pytest.raises(ValidationError):
            FlextLdapModels.LdapError(
                error_code=-1,  # Invalid error code
                error_message="Error",
                operation="bind",
            )


class TestOperationResult:
    """Test OperationResult model."""

    def test_create_operation_result(self) -> None:
        """Test creating operation result."""
        result = FlextLdapModels.OperationResult(
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
        config = FlextLdapModels.ConnectionConfig(
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
            assert config.validate_assignment is True
