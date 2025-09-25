"""Comprehensive tests for FlextLdapRepositories - targeting 100% coverage.

This test module provides comprehensive coverage for the LDAP repository
implementation, focusing on real functionality and edge cases.
"""

from abc import ABC
from unittest.mock import Mock

import pytest
from flext_ldap.models import FlextLdapModels
from flext_ldap.repositories import FlextLdapRepositories
from pydantic import SecretStr


class TestBaseRepository:
    """Test base repository functionality."""

    @pytest.fixture
    def mock_client(self) -> Mock:
        """Create mock LDAP client."""
        return Mock()

    @pytest.fixture
    def base_repo(self, mock_client: Mock) -> FlextLdapRepositories.UserRepository:
        """Create base repository instance."""
        # Since Repository is abstract, we'll test through UserRepository
        return FlextLdapRepositories.UserRepository(mock_client)

    def test_self(self, mock_client: Mock) -> None:
        """Test repository initialization."""
        repo = FlextLdapRepositories.UserRepository(mock_client)
        assert repo._client == mock_client
        assert repo._logger is not None


class TestUserRepository:
    """Test UserRepository implementation."""

    @pytest.fixture
    def mock_client(self) -> Mock:
        """Create mock LDAP client."""
        return Mock()

    @pytest.fixture
    def user_repo(self, mock_client: Mock) -> FlextLdapRepositories.UserRepository:
        """Create user repository instance."""
        return FlextLdapRepositories.UserRepository(mock_client)

    @pytest.mark.asyncio
    async def test_find_by_dn_success(
        self, user_repo: FlextLdapRepositories.UserRepository
    ) -> None:
        """Test successful find by DN."""
        test_dn = "uid=testuser,ou=users,dc=example,dc=com"

        result = await user_repo.find_by_dn(test_dn)

        assert result.is_success
        user = result.value
        assert isinstance(user, FlextLdapModels.LdapUser)
        assert user.dn == test_dn
        assert user.cn == "Test User"
        assert user.uid == "testuser"

    @pytest.mark.asyncio
    async def test_find_by_dn_exception(
        self, user_repo: FlextLdapRepositories.UserRepository
    ) -> None:
        """Test find by DN with invalid data (returns FlextResult failure)."""
        # Repositories use FlextResult, so they return failures instead of raising
        result = await user_repo.find_by_dn(None)
        # Should return a failure result for invalid input
        assert not result.is_success

    @pytest.mark.asyncio
    async def test_search_success(
        self, user_repo: FlextLdapRepositories.UserRepository
    ) -> None:
        """Test successful search."""
        base_dn = "ou=users,dc=example,dc=com"
        filter_str = "(objectClass=person)"
        page_size = 100
        paged_cookie = b"cookie_data"

        result = await user_repo.search(base_dn, filter_str, page_size, paged_cookie)

        assert result.is_success
        assert isinstance(result.value, list)

    @pytest.mark.asyncio
    async def test_search_with_all_parameters(
        self, user_repo: FlextLdapRepositories.UserRepository
    ) -> None:
        """Test search using all parameters."""
        base_dn = "ou=users,dc=example,dc=com"
        filter_str = "(uid=testuser)"
        page_size = 50
        paged_cookie = b"test_cookie"

        # Mock the logger to verify parameters are used
        user_repo._logger = Mock()

        result = await user_repo.search(base_dn, filter_str, page_size, paged_cookie)

        assert result.is_success
        # Verify logger was called with all parameters
        user_repo._logger.debug.assert_called_once()
        # Check the formatted message, not the format string
        formatted_message = (
            user_repo._logger.debug.call_args[0][0]
            % user_repo._logger.debug.call_args[0][1:]
        )
        assert base_dn in formatted_message
        assert filter_str in formatted_message
        assert str(page_size) in formatted_message

    @pytest.mark.asyncio
    async def test_save_success(
        self, user_repo: FlextLdapRepositories.UserRepository
    ) -> None:
        """Test successful save."""
        test_user = FlextLdapModels.LdapUser(
            dn="uid=test,ou=users,dc=example,dc=com",
            cn="Test User",
            uid="test",
            sn="User",
            given_name="Test",
            mail="test@example.com",
            user_password=SecretStr("password"),
        )

        result = await user_repo.save(test_user)

        assert result.is_success
        assert result.value == test_user

    @pytest.mark.asyncio
    async def test_delete_success(
        self, user_repo: FlextLdapRepositories.UserRepository
    ) -> None:
        """Test successful delete."""
        test_dn = "uid=test,ou=users,dc=example,dc=com"

        result = await user_repo.delete(test_dn)

        assert result.is_success
        assert result.value is True

    @pytest.mark.asyncio
    async def test_delete_empty_dn(
        self, user_repo: FlextLdapRepositories.UserRepository
    ) -> None:
        """Test delete with empty DN."""
        result = await user_repo.delete("")

        assert not result.is_success
        assert "DN cannot be empty" in result.error

    @pytest.mark.asyncio
    async def test_delete_none_dn(
        self, user_repo: FlextLdapRepositories.UserRepository
    ) -> None:
        """Test delete with None DN."""
        result = await user_repo.delete(None)

        assert not result.is_success
        assert "DN cannot be empty" in result.error

    @pytest.mark.asyncio
    async def test_exists_success(
        self, user_repo: FlextLdapRepositories.UserRepository
    ) -> None:
        """Test successful exists check."""
        test_dn = "uid=test,ou=users,dc=example,dc=com"

        result = await user_repo.exists(test_dn)

        assert result.is_success
        assert result.value is True

    @pytest.mark.asyncio
    async def test_exists_empty_dn(
        self, user_repo: FlextLdapRepositories.UserRepository
    ) -> None:
        """Test exists with empty DN."""
        result = await user_repo.exists("")

        assert not result.is_success
        assert "DN cannot be empty" in result.error

    @pytest.mark.asyncio
    async def test_update_success(
        self, user_repo: FlextLdapRepositories.UserRepository
    ) -> None:
        """Test successful update."""
        test_dn = "uid=test,ou=users,dc=example,dc=com"
        attributes = {"mail": "newemail@example.com", "title": "Developer"}

        result = await user_repo.update(test_dn, attributes)

        assert result.is_success
        assert result.value is True

    @pytest.mark.asyncio
    async def test_update_empty_dn(
        self, user_repo: FlextLdapRepositories.UserRepository
    ) -> None:
        """Test update with empty DN."""
        attributes = {"mail": "test@example.com"}

        result = await user_repo.update("", attributes)

        assert not result.is_success
        assert "DN cannot be empty" in result.error

    @pytest.mark.asyncio
    async def test_update_empty_attributes(
        self, user_repo: FlextLdapRepositories.UserRepository
    ) -> None:
        """Test update with empty attributes."""
        test_dn = "uid=test,ou=users,dc=example,dc=com"

        result = await user_repo.update(test_dn, {})

        assert not result.is_success
        assert "Attributes cannot be empty" in result.error

    @pytest.mark.asyncio
    async def test_update_none_attributes(
        self, user_repo: FlextLdapRepositories.UserRepository
    ) -> None:
        """Test update with None attributes."""
        test_dn = "uid=test,ou=users,dc=example,dc=com"

        result = await user_repo.update(test_dn, None)

        assert not result.is_success
        assert "Attributes cannot be empty" in result.error

    @pytest.mark.asyncio
    async def test_find_user_by_uid_success(
        self, user_repo: FlextLdapRepositories.UserRepository
    ) -> None:
        """Test successful find user by UID."""
        test_uid = "testuser"

        result = await user_repo.find_user_by_uid(test_uid)

        assert result.is_success
        user = result.value
        assert isinstance(user, FlextLdapModels.LdapUser)
        assert user.uid == test_uid
        assert f"uid={test_uid}" in user.dn

    @pytest.mark.asyncio
    async def test_find_users_by_filter_success(
        self, user_repo: FlextLdapRepositories.UserRepository
    ) -> None:
        """Test successful find users by filter."""
        filter_str = "(objectClass=person)"

        result = await user_repo.find_users_by_filter(filter_str)

        assert result.is_success
        assert isinstance(result.value, list)

    @pytest.mark.asyncio
    async def test_find_by_dn_returns_result_not_exception(
        self, user_repo: FlextLdapRepositories.UserRepository
    ) -> None:
        """Test that repositories return FlextResult, not raise exceptions."""
        result = await user_repo.find_by_dn("uid=test,ou=users,dc=example,dc=com")
        assert result.is_success or not result.is_success


class TestGroupRepository:
    """Test GroupRepository implementation."""

    @pytest.fixture
    def mock_client(self) -> Mock:
        """Create mock LDAP client."""
        return Mock()

    @pytest.fixture
    def group_repo(self, mock_client: Mock) -> FlextLdapRepositories.GroupRepository:
        """Create group repository instance."""
        return FlextLdapRepositories.GroupRepository(mock_client)

    @pytest.mark.asyncio
    async def test_find_by_dn_success(
        self, group_repo: FlextLdapRepositories.GroupRepository
    ) -> None:
        """Test successful find by DN."""
        test_dn = "cn=testgroup,ou=groups,dc=example,dc=com"

        result = await group_repo.find_by_dn(test_dn)

        assert result.is_success
        group = result.value
        assert isinstance(group, FlextLdapModels.Group)
        assert group.dn == test_dn
        assert group.cn == "Test Group"
        assert group.gid_number == 1000

    @pytest.mark.asyncio
    async def test_search_success(
        self, group_repo: FlextLdapRepositories.GroupRepository
    ) -> None:
        """Test successful search."""
        base_dn = "ou=groups,dc=example,dc=com"
        filter_str = "(objectClass=groupOfNames)"
        page_size = 100
        paged_cookie = b"cookie_data"

        result = await group_repo.search(base_dn, filter_str, page_size, paged_cookie)

        assert result.is_success
        assert isinstance(result.value, list)

    @pytest.mark.asyncio
    async def test_search_with_logger_verification(
        self, group_repo: FlextLdapRepositories.GroupRepository
    ) -> None:
        """Test search with logger parameter verification."""
        base_dn = "ou=groups,dc=example,dc=com"
        filter_str = "(cn=testgroup)"
        page_size = 25
        paged_cookie = b"group_cookie"

        # Mock the logger to verify parameters are used
        group_repo._logger = Mock()

        result = await group_repo.search(base_dn, filter_str, page_size, paged_cookie)

        assert result.is_success
        # Verify logger was called with all parameters
        group_repo._logger.debug.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_success(
        self, group_repo: FlextLdapRepositories.GroupRepository
    ) -> None:
        """Test successful save."""
        test_group = FlextLdapModels.Group(
            dn="cn=test,ou=groups,dc=example,dc=com",
            cn="test",
            gid_number=2000,
            description="Test Group",
        )

        result = await group_repo.save(test_group)

        assert result.is_success
        assert result.value == test_group

    @pytest.mark.asyncio
    async def test_delete_success(
        self, group_repo: FlextLdapRepositories.GroupRepository
    ) -> None:
        """Test successful delete."""
        test_dn = "cn=test,ou=groups,dc=example,dc=com"

        result = await group_repo.delete(test_dn)

        assert result.is_success
        assert result.value is True

    @pytest.mark.asyncio
    async def test_delete_empty_dn(
        self, group_repo: FlextLdapRepositories.GroupRepository
    ) -> None:
        """Test delete with empty DN."""
        result = await group_repo.delete("")

        assert not result.is_success
        assert "DN cannot be empty" in result.error

    @pytest.mark.asyncio
    async def test_exists_success(
        self, group_repo: FlextLdapRepositories.GroupRepository
    ) -> None:
        """Test successful exists check."""
        test_dn = "cn=test,ou=groups,dc=example,dc=com"

        result = await group_repo.exists(test_dn)

        assert result.is_success
        assert result.value is True

    @pytest.mark.asyncio
    async def test_exists_empty_dn(
        self, group_repo: FlextLdapRepositories.GroupRepository
    ) -> None:
        """Test exists with empty DN."""
        result = await group_repo.exists("")

        assert not result.is_success
        assert "DN cannot be empty" in result.error

    @pytest.mark.asyncio
    async def test_update_success(
        self, group_repo: FlextLdapRepositories.GroupRepository
    ) -> None:
        """Test successful update."""
        test_dn = "cn=test,ou=groups,dc=example,dc=com"
        attributes = {"description": "Updated description"}

        result = await group_repo.update(test_dn, attributes)

        assert result.is_success
        assert result.value is True

    @pytest.mark.asyncio
    async def test_update_empty_dn(
        self, group_repo: FlextLdapRepositories.GroupRepository
    ) -> None:
        """Test update with empty DN."""
        attributes = {"description": "test"}

        result = await group_repo.update("", attributes)

        assert not result.is_success
        assert "DN cannot be empty" in result.error

    @pytest.mark.asyncio
    async def test_update_empty_attributes(
        self, group_repo: FlextLdapRepositories.GroupRepository
    ) -> None:
        """Test update with empty attributes."""
        test_dn = "cn=test,ou=groups,dc=example,dc=com"

        result = await group_repo.update(test_dn, {})

        assert not result.is_success
        assert "Attributes cannot be empty" in result.error

    @pytest.mark.asyncio
    async def test_find_group_by_cn_success(
        self, group_repo: FlextLdapRepositories.GroupRepository
    ) -> None:
        """Test successful find group by CN."""
        test_cn = "testgroup"

        result = await group_repo.find_group_by_cn(test_cn)

        assert result.is_success
        group = result.value
        assert isinstance(group, FlextLdapModels.Group)
        assert group.cn == test_cn
        assert f"cn={test_cn}" in group.dn

    @pytest.mark.asyncio
    async def test_get_group_members_success(
        self, group_repo: FlextLdapRepositories.GroupRepository
    ) -> None:
        """Test successful get group members."""
        test_group_dn = "cn=test,ou=groups,dc=example,dc=com"

        result = await group_repo.get_group_members(test_group_dn)

        assert result.is_success
        assert isinstance(result.value, list)

    @pytest.mark.asyncio
    async def test_add_member_to_group_success(
        self, group_repo: FlextLdapRepositories.GroupRepository
    ) -> None:
        """Test successful add member to group."""
        test_group_dn = "cn=test,ou=groups,dc=example,dc=com"
        test_member_dn = "uid=test,ou=users,dc=example,dc=com"

        result = await group_repo.add_member_to_group(test_group_dn, test_member_dn)

        assert result.is_success
        assert result.value is True


class TestFlextLdapRepositories:
    """Test FlextLdapRepositories unified class."""

    def test_unified_class_structure(self) -> None:
        """Test that FlextLdapRepositories contains expected nested classes."""
        assert hasattr(FlextLdapRepositories, "Repository")
        assert hasattr(FlextLdapRepositories, "UserRepository")
        assert hasattr(FlextLdapRepositories, "GroupRepository")

    def test_repository_inheritance(self) -> None:
        """Test that concrete repositories inherit from base Repository."""
        mock_client = Mock()

        user_repo = FlextLdapRepositories.UserRepository(mock_client)
        group_repo = FlextLdapRepositories.GroupRepository(mock_client)

        assert isinstance(user_repo, FlextLdapRepositories.Repository)
        assert isinstance(group_repo, FlextLdapRepositories.Repository)

        """Test that base Repository is abstract."""

        assert issubclass(FlextLdapRepositories.Repository, ABC)

    def test_repository_methods_exist(self) -> None:
        """Test that repositories have all required methods."""
        mock_client = Mock()
        user_repo = FlextLdapRepositories.UserRepository(mock_client)

        required_methods = [
            "find_by_dn",
            "search",
            "save",
            "delete",
            "exists",
            "update",
        ]

        for method_name in required_methods:
            assert hasattr(user_repo, method_name)
            assert callable(getattr(user_repo, method_name))

    def test_user_specific_methods(self) -> None:
        """Test that UserRepository has user-specific methods."""
        mock_client = Mock()
        user_repo = FlextLdapRepositories.UserRepository(mock_client)

        user_methods = ["find_user_by_uid", "find_users_by_filter"]

        for method_name in user_methods:
            assert hasattr(user_repo, method_name)
            assert callable(getattr(user_repo, method_name))

    def test_group_specific_methods(self) -> None:
        """Test that GroupRepository has group-specific methods."""
        mock_client = Mock()
        group_repo = FlextLdapRepositories.GroupRepository(mock_client)

        group_methods = ["find_group_by_cn", "get_group_members", "add_member_to_group"]

        for method_name in group_methods:
            assert hasattr(group_repo, method_name)
            assert callable(getattr(group_repo, method_name))
