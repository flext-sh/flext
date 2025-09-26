"""Unit tests for FlextLdapClient - Comprehensive test coverage.

Tests the main FlextLdapClient using only the new API methods without compatibility layers.
Following FLEXT standards for test organization and coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from pydantic import SecretStr

from flext_core import FlextResult
from flext_ldap import FlextLdapAPI, FlextLdapConfig, FlextLdapModels


class TestFlextLdapAPI:
    """Test suite for FlextLdapAPI - main domain access point."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.api = FlextLdapAPI()

    def test_api_initialization(self) -> None:
        """Test FlextLdapAPI initialization."""
        api = FlextLdapAPI()
        assert api is not None
        assert api.client is not None
        assert api.config is not None
        assert api.users is not None
        assert api.groups is not None

    def test_api_initialization_with_config(self) -> None:
        """Test FlextLdapAPI initialization with custom config."""
        custom_config = FlextLdapConfig()
        api = FlextLdapAPI(config=custom_config)
        assert api.config is custom_config

    def test_create_factory_method(self) -> None:
        """Test FlextLdapAPI.create factory method."""
        api = FlextLdapAPI.create()
        assert api is not None
        assert isinstance(api, FlextLdapAPI)

    def test_create_factory_method_with_config(self) -> None:
        """Test FlextLdapAPI.create factory method."""
        api = FlextLdapAPI.create()
        assert api is not None
        assert isinstance(api, FlextLdapAPI)

    def test_domain_access_properties(self) -> None:
        """Test domain access properties."""
        api = FlextLdapAPI()

        # Test property access
        assert api.client is not None
        assert api.config is not None
        assert api.users is not None
        assert api.groups is not None
        assert api.models == FlextLdapModels
        assert api.types is not None
        assert api.protocols is not None
        assert api.validations is not None

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self) -> None:
        """Test successful user authentication."""
        with patch("flext_ldap.clients.FlextLdapClient.authenticate_user") as mock_auth:
            # Mock successful authentication
            test_user = FlextLdapModels.LdapUser(
                dn="uid=testuser,ou=users,dc=example,dc=com",
                cn="Test User",
                uid="testuser",
                sn="User",
                given_name="Test",
                mail="test@example.com",
                telephone_number=None,
                mobile=None,
                department=None,
                title=None,
                organization=None,
                organizational_unit=None,
                user_password=None,
                created_timestamp=None,
                modified_timestamp=None,
            )
            mock_auth.return_value = FlextResult[FlextLdapModels.LdapUser].ok(test_user)

            result = await self.api.client.authenticate_user("testuser", "password")

            assert result.is_success
            assert result.value.uid == "testuser"
            assert result.value.cn == "Test User"
            mock_auth.assert_called_once_with("testuser", "password")

    @pytest.mark.asyncio
    async def test_authenticate_user_failure(self) -> None:
        """Test failed user authentication."""
        with patch("flext_ldap.clients.FlextLdapClient.authenticate_user") as mock_auth:
            mock_auth.return_value = FlextResult[FlextLdapModels.LdapUser].fail(
                "Invalid credentials"
            )

            result = await self.api.client.authenticate_user(
                "testuser", "wrongpassword"
            )

            assert not result.is_success
            assert "Invalid credentials" in result.error

    @pytest.mark.asyncio
    async def test_bind_success(self) -> None:
        """Test successful LDAP bind."""
        with patch("flext_ldap.clients.FlextLdapClient.bind") as mock_bind:
            # Create a test config with valid credentials
            test_config = FlextLdapConfig()
            test_config.ldap_bind_dn = "cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com"
            test_config.ldap_bind_password = SecretStr("password")

            # Replace the API's config
            self.api._config = test_config

            mock_bind.return_value = FlextResult[bool].ok(True)

            result = await self.api.client.bind(
                "cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com", "password"
            )

            assert result.is_success
            assert result.value is True
            mock_bind.assert_called_once_with("cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com", "password")

    @pytest.mark.asyncio
    async def test_bind_with_custom_credentials(self) -> None:
        """Test LDAP bind with custom credentials."""
        with patch("flext_ldap.clients.FlextLdapClient.bind") as mock_bind:
            mock_bind.return_value = FlextResult[bool].ok(True)

            result = await self.api.client.bind("cn=user,dc=example,dc=com", "userpass")

            assert result.is_success
            mock_bind.assert_called_once_with("cn=user,dc=example,dc=com", "userpass")

    @pytest.mark.asyncio
    async def test_bind_missing_credentials(self) -> None:
        """Test bind failure when credentials are missing."""
        # Create a test config with missing credentials
        test_config = FlextLdapConfig()
        test_config.ldap_bind_dn = None
        test_config.ldap_bind_password = None

        # Replace the API's config
        self.api._config = test_config

        result = await self.api.client.bind("", "")

        assert not result.is_success
        assert "No connection established" in result.error

    @pytest.mark.asyncio
    async def test_connect_success(self) -> None:
        """Test successful LDAP connection."""
        with patch("flext_ldap.clients.FlextLdapClient.connect") as mock_connect:
            # Create a test config with valid connection details
            test_config = FlextLdapConfig()
            test_config.ldap_bind_dn = "cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com"
            test_config.ldap_bind_password = SecretStr("password")

            # Replace the API's config
            self.api._config = test_config

            mock_connect.return_value = FlextResult[None].ok(None)

            result = await self.api.client.connect()

            assert result.is_success
            assert result.value is None

    @pytest.mark.asyncio
    async def test_disconnect(self) -> None:
        """Test LDAP disconnection."""
        with patch("flext_ldap.clients.FlextLdapClient.unbind") as mock_unbind:
            mock_unbind.return_value = FlextResult[None].ok(None)

            result = await self.api.client.unbind()

            assert result.is_success
            assert result.value is None
            mock_unbind.assert_called_once()

    @pytest.mark.asyncio
    async def test_is_connected(self) -> None:
        """Test connection status check."""
        with patch(
            "flext_ldap.clients.FlextLdapClient.is_connected"
        ) as mock_is_connected:
            mock_is_connected.return_value = True

            result = await self.api.is_connected()

            assert result is True
            mock_is_connected.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_users_default(self) -> None:
        """Test user search with default parameters."""
        with patch(
            "flext_ldap.repositories.FlextLdapRepositories.UserRepository.find_users_by_filter"
        ) as mock_search:
            test_users = [
                FlextLdapModels.LdapUser(
                    dn="uid=user1,ou=users,dc=example,dc=com",
                    cn="User One",
                    uid="user1",
                    sn="One",
                    given_name="User",
                    mail="user1@example.com",
                    telephone_number=None,
                    mobile=None,
                    department=None,
                    title=None,
                    organization=None,
                    organizational_unit=None,
                    user_password=None,
                    created_timestamp=None,
                    modified_timestamp=None,
                )
            ]
            mock_search.return_value = FlextResult[list[FlextLdapModels.LdapUser]].ok(
                test_users
            )

            user_repo = self.api.users.UserRepository(self.api.client)
            result = await user_repo.find_users_by_filter("(objectClass=person)")

            assert result.is_success
            assert len(result.value) == 1
            assert result.value[0].uid == "user1"

    @pytest.mark.asyncio
    async def test_search_users_with_custom_filter(self) -> None:
        """Test user search with custom filter."""
        with patch(
            "flext_ldap.repositories.FlextLdapRepositories.UserRepository.find_users_by_filter"
        ) as mock_search:
            mock_users = [
                FlextLdapModels.LdapUser(
                    dn="uid=REDACTED_LDAP_BIND_PASSWORD,ou=users,dc=example,dc=com",
                    cn="Admin User",
                    uid="REDACTED_LDAP_BIND_PASSWORD",
                    sn="User",
                    given_name="Admin",
                    mail="REDACTED_LDAP_BIND_PASSWORD@example.com",
                )
            ]
            mock_search.return_value = FlextResult[list[FlextLdapModels.LdapUser]].ok(
                mock_users
            )

            user_repo = self.api.users.UserRepository(self.api.client)
            result = await user_repo.find_users_by_filter(
                "(&(objectClass=inetOrgPerson)(uid=REDACTED_LDAP_BIND_PASSWORD))"
            )

            assert result.is_success
            assert len(result.value) == 1
            assert result.value[0].uid == "REDACTED_LDAP_BIND_PASSWORD"
            mock_search.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_groups_default(self) -> None:
        """Test group search with default parameters."""
        with patch(
            "flext_ldap.repositories.FlextLdapRepositories.GroupRepository.search"
        ) as mock_search:
            test_groups = [
                FlextLdapModels.Group(
                    dn="cn=testgroup,ou=groups,dc=example,dc=com",
                    cn="testgroup",
                    gid_number=1000,
                    description="Test group",
                    created_timestamp=None,
                    modified_timestamp=None,
                )
            ]
            mock_search.return_value = FlextResult[list[FlextLdapModels.Group]].ok(
                test_groups
            )

            group_repo = self.api.groups.GroupRepository(self.api.client)
            result = await group_repo.search("(objectClass=group)")

            assert result.is_success
            assert len(result.value) == 1
            assert result.value[0].cn == "testgroup"

    @pytest.mark.asyncio
    async def test_search_groups_with_custom_filter(self) -> None:
        """Test group search with custom filter."""
        with patch("flext_ldap.clients.FlextLdapClient.search_groups") as mock_search:
            mock_groups = [
                FlextLdapModels.Group(
                    dn="cn=REDACTED_LDAP_BIND_PASSWORDs,ou=groups,dc=example,dc=com",
                    cn="REDACTED_LDAP_BIND_PASSWORDs",
                    gid_number=500,
                    description="Administrators group",
                )
            ]
            mock_search.return_value = FlextResult[list[FlextLdapModels.Group]].ok(
                mock_groups
            )

            result = await self.api.client.search_groups(
                base_dn="ou=groups,dc=example,dc=com", cn="REDACTED_LDAP_BIND_PASSWORDs"
            )

            assert result.is_success
            assert len(result.value) == 1
            assert result.value[0].cn == "REDACTED_LDAP_BIND_PASSWORDs"

    @pytest.mark.asyncio
    async def test_search_entries(self) -> None:
        """Test generic LDAP entry search."""
        with patch(
            "flext_ldap.clients.FlextLdapClient.search_with_request"
        ) as mock_search:
            mock_response = FlextLdapModels.SearchResponse(
                entries=[{"dn": "cn=test,dc=example,dc=com", "cn": "test"}]
            )
            mock_search.return_value = FlextResult[FlextLdapModels.SearchResponse].ok(
                mock_response
            )

            result = await self.api.search_entries(
                base_dn="dc=example,dc=com",
                filter_str="(cn=test)",
                scope="subtree",
                attributes=["cn"],
            )

            assert result.is_success
            assert len(result.value.entries) == 1
            mock_search.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user(self) -> None:
        """Test user creation."""
        with patch("flext_ldap.clients.FlextLdapClient.create_user") as mock_create:
            test_user = FlextLdapModels.LdapUser(
                dn="uid=newuser,ou=users,dc=example,dc=com",
                cn="New User",
                uid="newuser",
                sn="User",
                given_name="New",
                mail="newuser@example.com",
                telephone_number=None,
                mobile=None,
                department=None,
                title=None,
                organization=None,
                organizational_unit=None,
                user_password=None,
                created_timestamp=None,
                modified_timestamp=None,
            )
            mock_create.return_value = FlextResult[FlextLdapModels.LdapUser].ok(
                test_user
            )

            create_request = FlextLdapModels.CreateUserRequest(
                dn="uid=newuser,ou=users,dc=example,dc=com",
                cn="New User",
                uid="newuser",
                sn="User",
                given_name="New",
                mail="newuser@example.com",
                user_password="SecurePassword123!",
                telephone_number="+1234567890",
                description="Test user for API testing",
                department="IT Department",
                title="Software Engineer",
                organization="Example Corp",
            )

            result = await self.api.client.create_user(create_request)

            assert result.is_success
            assert result.value.uid == "newuser"
            mock_create.assert_called_once_with(create_request)

    @pytest.mark.asyncio
    async def test_create_group(self) -> None:
        """Test group creation."""
        with patch("flext_ldap.clients.FlextLdapClient.create_group") as mock_create:
            test_group = FlextLdapModels.Group(
                dn="cn=newgroup,ou=groups,dc=example,dc=com",
                cn="newgroup",
                gid_number=2000,
                description="New test group",
                created_timestamp=None,
                modified_timestamp=None,
            )
            mock_create.return_value = FlextResult[FlextLdapModels.Group].ok(test_group)

            create_request = FlextLdapModels.CreateGroupRequest(
                dn="cn=newgroup,ou=groups,dc=example,dc=com",
                cn="newgroup",
                gid_number=2000,
                description="New test group",
            )

            result = await self.api.client.create_group(create_request)

            assert result.is_success
            assert result.value.cn == "newgroup"
            mock_create.assert_called_once_with(create_request)

    @pytest.mark.asyncio
    async def test_get_user(self) -> None:
        """Test get user by Distinguished Name."""
        with patch("flext_ldap.clients.FlextLdapClient.get_user") as mock_get:
            test_user = FlextLdapModels.LdapUser(
                dn="uid=testuser,ou=users,dc=example,dc=com",
                cn="Test User",
                uid="testuser",
                sn="User",
                given_name="Test",
                mail="test@example.com",
                telephone_number=None,
                mobile=None,
                department=None,
                title=None,
                organization=None,
                organizational_unit=None,
                user_password=None,
                created_timestamp=None,
                modified_timestamp=None,
            )
            mock_get.return_value = FlextResult[FlextLdapModels.LdapUser | None].ok(
                test_user
            )

            result = await self.api.client.get_user(
                "uid=testuser,ou=users,dc=example,dc=com"
            )

            assert result.is_success
            assert result.value is not None
            assert result.value.uid == "testuser"

    @pytest.mark.asyncio
    async def test_get_group(self) -> None:
        """Test get group by Distinguished Name."""
        with patch("flext_ldap.clients.FlextLdapClient.get_group") as mock_get:
            test_group = FlextLdapModels.Group(
                dn="cn=testgroup,ou=groups,dc=example,dc=com",
                cn="testgroup",
                gid_number=1000,
                description="Test group",
                created_timestamp=None,
                modified_timestamp=None,
            )
            mock_get.return_value = FlextResult[FlextLdapModels.Group | None].ok(
                test_group
            )

            result = await self.api.get_group(
                "cn=testgroup,ou=groups,dc=example,dc=com"
            )

            assert result.is_success
            assert result.value is not None
            assert result.value.cn == "testgroup"

    @pytest.mark.asyncio
    async def test_update_user_attributes(self) -> None:
        """Test updating user attributes."""
        with patch(
            "flext_ldap.clients.FlextLdapClient.update_user_attributes"
        ) as mock_update:
            mock_update.return_value = FlextResult[bool].ok(True)

            attributes = {"mail": "newemail@example.com", "title": "Senior Developer"}
            result = await self.api.update_user_attributes(
                "uid=testuser,ou=users,dc=example,dc=com", attributes
            )

            assert result.is_success
            assert result.value is True
            mock_update.assert_called_once_with(
                "uid=testuser,ou=users,dc=example,dc=com", attributes
            )

    @pytest.mark.asyncio
    async def test_update_group_attributes(self) -> None:
        """Test updating group attributes."""
        with patch(
            "flext_ldap.clients.FlextLdapClient.update_group_attributes"
        ) as mock_update:
            mock_update.return_value = FlextResult[bool].ok(True)

            attributes = {"description": "Updated group description"}
            result = await self.api.update_group_attributes(
                "cn=testgroup,ou=groups,dc=example,dc=com", attributes
            )

            assert result.is_success
            assert result.value is True
            mock_update.assert_called_once_with(
                "cn=testgroup,ou=groups,dc=example,dc=com", attributes
            )

    @pytest.mark.asyncio
    async def test_delete_user(self) -> None:
        """Test user deletion."""
        with patch("flext_ldap.clients.FlextLdapClient.delete_user") as mock_delete:
            mock_delete.return_value = FlextResult[bool].ok(True)

            result = await self.api.delete_user(
                "uid=testuser,ou=users,dc=example,dc=com"
            )

            assert result.is_success
            assert result.value is True
            mock_delete.assert_called_once_with(
                "uid=testuser,ou=users,dc=example,dc=com"
            )

    @pytest.mark.asyncio
    async def test_delete_group(self) -> None:
        """Test group deletion."""
        with patch("flext_ldap.clients.FlextLdapClient.delete_group") as mock_delete:
            mock_delete.return_value = FlextResult[None].ok(None)

            result = await self.api.client.delete_group(
                "cn=testgroup,ou=groups,dc=example,dc=com"
            )

            assert result.is_success
            assert result.value is None
            mock_delete.assert_called_once_with(
                "cn=testgroup,ou=groups,dc=example,dc=com"
            )

    @pytest.mark.asyncio
    async def test_test_connection(self) -> None:
        """Test LDAP connection testing."""
        with patch("flext_ldap.clients.FlextLdapClient.test_connection") as mock_test:
            mock_test.return_value = FlextResult[bool].ok(True)

            result = await self.api.test_connection()

            assert result.is_success
            assert result.value is True
            mock_test.assert_called_once()

    def test_validate_configuration_consistency(self) -> None:
        """Test configuration validation."""
        with patch(
            "flext_ldap.validations.FlextLdapValidations.validate_dn"
        ) as mock_dn_validate:
            mock_dn_validate.return_value = FlextResult[str].ok(
                "cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com"
            )

            # Create a test config with valid values
            test_config = FlextLdapConfig(
                ldap_bind_dn="cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com",
                ldap_bind_password="REDACTED_LDAP_BIND_PASSWORD_password"
            )

            # Replace the API's config
            self.api._config = test_config

            result = self.api.validate_configuration_consistency()

            # Should succeed with valid configuration
            assert result.is_success

    def test_validate_dn(self) -> None:
        """Test DN validation."""
        with patch(
            "flext_ldap.validations.FlextLdapValidations.validate_dn"
        ) as mock_validate:
            mock_validate.return_value = FlextResult[str].ok(
                "cn=test,dc=example,dc=com"
            )

            result = self.api.validate_dn("cn=test,dc=example,dc=com")

            assert result.is_success
            assert result.value is None  # API returns FlextResult[None]

    def test_validate_filter(self) -> None:
        """Test LDAP filter validation."""
        with patch(
            "flext_ldap.validations.FlextLdapValidations.validate_filter"
        ) as mock_validate:
            mock_validate.return_value = FlextResult[str].ok("(cn=test)")

            result = self.api.validate_filter("(cn=test)")

            assert result.is_success
            assert result.value == "(cn=test)"

    def test_validate_email(self) -> None:
        """Test email validation."""
        with patch(
            "flext_ldap.validations.FlextLdapValidations.validate_email"
        ) as mock_validate:
            mock_validate.return_value = FlextResult[str].ok("test@example.com")

            result = self.api.validations.validate_email("test@example.com")

            assert result.is_success
            assert result.value == "test@example.com"

    def test_validate_email_none(self) -> None:
        """Test email validation with None input."""
        result = self.api.validations.validate_email(None)

        assert result.is_success
        assert result.value is None
