"""Comprehensive tests for FlextLdapClient - targeting 100% coverage.

This test module provides comprehensive coverage for the LDAP client
implementation, focusing on real functionality and edge cases.
"""

from unittest.mock import Mock, patch

import pytest
from flext_ldap.clients import FlextLdapClient
from flext_ldap.config import FlextLdapConfigs
from flext_ldap.models import FlextLdapModels
from pydantic import SecretStr


class TestFlextLdapClient:
    """Test FlextLdapClient implementation."""

    @pytest.fixture
    def mock_connection(self):
        """Create mock LDAP connection."""
        mock_conn = Mock()
        mock_conn.bound = True
        mock_conn.last_error = None
        mock_conn.entries = []
        return mock_conn

    @pytest.fixture
    def client_config(self):
        """Create test client configuration."""
        return FlextLdapConfigs.LdapConnectionConfig(
            server="ldap://test.example.com",
            port=389,
            bind_dn="cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com",
            bind_password=SecretStr("password123"),
            base_dn="dc=example,dc=com",
            use_ssl=False,
            timeout=30,
        )

    @pytest.fixture
    def client(self, client_config):
        """Create test client."""
        return FlextLdapClient(client_config)

    def test_client_initialization(self, client_config) -> None:
        """Test client initialization."""
        client = FlextLdapClient(client_config)
        assert client._config == client_config
        assert client._connection is None

    @patch("flext_ldap.clients.Connection")
    @patch("flext_ldap.clients.Server")
    def test_connect_success(
        self, mock_server, mock_connection, client, mock_connection_obj
    ) -> None:
        """Test successful connection."""
        mock_server.return_value = Mock()
        mock_connection.return_value = mock_connection_obj
        mock_connection_obj.bind.return_value = True

        result = client.connect()

        assert result.is_success
        assert client._connection is not None
        mock_server.assert_called_once()
        mock_connection.assert_called_once()

    @patch("flext_ldap.clients.Connection")
    @patch("flext_ldap.clients.Server")
    def test_connect_bind_failure(self, mock_server, mock_connection, client) -> None:
        """Test connection with bind failure."""
        mock_server.return_value = Mock()
        mock_conn = Mock()
        mock_conn.bind.return_value = False
        mock_conn.last_error = "Invalid credentials"
        mock_connection.return_value = mock_conn

        result = client.connect()

        assert result.is_failure
        assert "Failed to bind" in result.error

    @patch("flext_ldap.clients.Connection")
    @patch("flext_ldap.clients.Server")
    def test_connect_exception(self, mock_server, mock_connection, client) -> None:
        """Test connection with exception."""
        mock_server.side_effect = Exception("Connection error")

        result = client.connect()

        assert result.is_failure
        assert "Connection error" in result.error

    def test_disconnect_success(self, client, mock_connection) -> None:
        """Test successful disconnection."""
        client._connection = mock_connection

        result = client.disconnect()

        assert result.is_success
        mock_connection.unbind.assert_called_once()
        assert client._connection is None

    def test_disconnect_no_connection(self, client) -> None:
        """Test disconnect when no connection exists."""
        result = client.disconnect()
        assert result.is_success

    def test_disconnect_exception(self, client, mock_connection) -> None:
        """Test disconnect with exception."""
        client._connection = mock_connection
        mock_connection.unbind.side_effect = Exception("Unbind error")

        result = client.disconnect()

        assert result.is_failure
        assert "Unbind error" in result.error

    def test_is_connected_true(self, client, mock_connection) -> None:
        """Test is_connected when connected."""
        client._connection = mock_connection
        assert client.is_connected()

    def test_is_connected_false(self, client) -> None:
        """Test is_connected when not connected."""
        assert not client.is_connected()

    def test_is_connected_unbound(self, client, mock_connection) -> None:
        """Test is_connected when connection is unbound."""
        mock_connection.bound = False
        client._connection = mock_connection
        assert not client.is_connected()

    def test_bind_success(self, client, mock_connection) -> None:
        """Test successful bind."""
        client._connection = mock_connection
        mock_connection.bind.return_value = True

        result = client.bind("cn=test,dc=example,dc=com", "password")

        assert result.is_success
        mock_connection.bind.assert_called_with(
            user="cn=test,dc=example,dc=com", password="password"
        )

    def test_bind_failure(self, client, mock_connection) -> None:
        """Test bind failure."""
        client._connection = mock_connection
        mock_connection.bind.return_value = False
        mock_connection.last_error = "Invalid credentials"

        result = client.bind("cn=test,dc=example,dc=com", "wrongpass")

        assert result.is_failure
        assert "Invalid credentials" in result.error

    def test_bind_no_connection(self, client) -> None:
        """Test bind without connection."""
        result = client.bind("cn=test,dc=example,dc=com", "password")

        assert result.is_failure
        assert "No connection established" in result.error

    def test_search_users_success(self, client, mock_connection) -> None:
        """Test successful user search."""
        # Setup mock entry
        mock_entry = Mock()
        mock_entry.entry_dn = "uid=testuser,ou=users,dc=example,dc=com"
        mock_entry.cn.value = "Test User"
        mock_entry.uid.value = "testuser"
        mock_entry.sn.value = "User"
        mock_entry.givenName.value = "Test"
        mock_entry.mail.value = "test@example.com"
        mock_entry.telephoneNumber.value = "123-456-7890"
        mock_entry.mobile.value = "987-654-3210"
        mock_entry.departmentNumber.value = "IT"
        mock_entry.title.value = "Developer"
        mock_entry.o.value = "Example Corp"
        mock_entry.ou.value = "Engineering"
        mock_entry.userPassword.value = "password123"
        mock_entry.createTimestamp = None
        mock_entry.modifyTimestamp = None

        client._connection = mock_connection
        mock_connection.search.return_value = True
        mock_connection.entries = [mock_entry]

        result = client.search_users("ou=users,dc=example,dc=com", uid="testuser")

        assert result.is_success
        users = result.value
        assert len(users) == 1
        assert users[0].uid == "testuser"
        assert users[0].cn == "Test User"

    def test_search_users_no_connection(self, client) -> None:
        """Test user search without connection."""
        result = client.search_users("ou=users,dc=example,dc=com")

        assert result.is_failure
        assert "No connection established" in result.error

    def test_search_users_search_failure(self, client, mock_connection) -> None:
        """Test user search with search failure."""
        client._connection = mock_connection
        mock_connection.search.return_value = False
        mock_connection.last_error = "Search failed"

        result = client.search_users("ou=users,dc=example,dc=com")

        assert result.is_failure
        assert "Search failed" in result.error

    def test_search_groups_success(self, client, mock_connection) -> None:
        """Test successful group search."""
        # Setup mock entry
        mock_entry = Mock()
        mock_entry.entry_dn = "cn=testgroup,ou=groups,dc=example,dc=com"
        mock_entry.cn.value = "testgroup"
        mock_entry.gidNumber.value = 1000
        mock_entry.description.value = "Test Group"
        mock_entry.createTimestamp = None
        mock_entry.modifyTimestamp = None

        client._connection = mock_connection
        mock_connection.search.return_value = True
        mock_connection.entries = [mock_entry]

        result = client.search_groups("ou=groups,dc=example,dc=com", cn="testgroup")

        assert result.is_success
        groups = result.value
        assert len(groups) == 1
        assert groups[0].cn == "testgroup"
        assert groups[0].gid_number == 1000

    def test_authenticate_user_success(self, client, mock_connection) -> None:
        """Test successful user authentication."""
        # Setup mock for search
        mock_entry = Mock()
        mock_entry.entry_dn = "uid=testuser,ou=users,dc=example,dc=com"

        client._connection = mock_connection
        mock_connection.search.return_value = True
        mock_connection.entries = [mock_entry]

        # Mock test connection for authentication
        with patch("flext_ldap.clients.Connection") as mock_conn_class:
            mock_test_conn = Mock()
            mock_test_conn.bind.return_value = True
            mock_conn_class.return_value = mock_test_conn

            result = client.authenticate_user("testuser", "password")

            assert result.is_success
            assert result.value is True

    def test_authenticate_user_failure(self, client, mock_connection) -> None:
        """Test failed user authentication."""
        # Setup mock for search
        mock_entry = Mock()
        mock_entry.entry_dn = "uid=testuser,ou=users,dc=example,dc=com"

        client._connection = mock_connection
        mock_connection.search.return_value = True
        mock_connection.entries = [mock_entry]

        # Mock test connection for authentication
        with patch("flext_ldap.clients.Connection") as mock_conn_class:
            mock_test_conn = Mock()
            mock_test_conn.bind.return_value = False
            mock_conn_class.return_value = mock_test_conn

            result = client.authenticate_user("testuser", "wrongpass")

            assert result.is_success
            assert result.value is False

    def test_authenticate_user_not_found(self, client, mock_connection) -> None:
        """Test authentication for non-existent user."""
        client._connection = mock_connection
        mock_connection.search.return_value = True
        mock_connection.entries = []

        result = client.authenticate_user("nonexistent", "password")

        assert result.is_failure
        assert "User not found" in result.error

    def test_search_with_request_success(self, client, mock_connection) -> None:
        """Test search with request object."""
        request = FlextLdapModels.SearchRequest(
            base_dn="ou=users,dc=example,dc=com",
            filter="(objectClass=person)",
            scope="subtree",
            attributes=["uid", "cn"],
        )

        # Setup mock entry
        mock_entry = Mock()
        mock_entry.entry_dn = "uid=test,ou=users,dc=example,dc=com"
        mock_entry.entry_attributes = ["uid", "cn"]
        mock_entry.__getitem__ = Mock()
        mock_entry.__getitem__.return_value.value = "test_value"

        client._connection = mock_connection
        mock_connection.search.return_value = True
        mock_connection.entries = [mock_entry]

        result = client.search_with_request(request)

        assert result.is_success
        response = result.value
        assert len(response.entries) == 1

    def test_create_user_success(self, client, mock_connection) -> None:
        """Test successful user creation."""
        request = FlextLdapModels.CreateUserRequest(
            uid="newuser",
            cn="New User",
            sn="User",
            given_name="New",
            mail="newuser@example.com",
            user_password=SecretStr("password123"),
        )

        client._connection = mock_connection
        mock_connection.add.return_value = True

        result = client.create_user(request)

        assert result.is_success
        user = result.value
        assert user.uid == "newuser"
        assert user.cn == "New User"

    def test_create_user_failure(self, client, mock_connection) -> None:
        """Test failed user creation."""
        request = FlextLdapModels.CreateUserRequest(
            uid="newuser",
            cn="New User",
            sn="User",
            given_name="New",
            mail="newuser@example.com",
            user_password=SecretStr("password123"),
        )

        client._connection = mock_connection
        mock_connection.add.return_value = False
        mock_connection.last_error = "User already exists"

        result = client.create_user(request)

        assert result.is_failure
        assert "User already exists" in result.error

    def test_create_group_success(self, client, mock_connection) -> None:
        """Test successful group creation."""
        request = FlextLdapModels.CreateGroupRequest(
            cn="newgroup", gid_number=2000, description="New Group"
        )

        client._connection = mock_connection
        mock_connection.add.return_value = True

        result = client.create_group(request)

        assert result.is_success
        group = result.value
        assert group.cn == "newgroup"
        assert group.gid_number == 2000

    def test_update_user_attributes_success(self, client, mock_connection) -> None:
        """Test successful user attribute update."""
        attributes = {"mail": "updated@example.com", "title": "Senior Developer"}

        client._connection = mock_connection
        mock_connection.modify.return_value = True

        result = client.update_user_attributes(
            "uid=test,ou=users,dc=example,dc=com", attributes
        )

        assert result.is_success
        assert result.value is True

    def test_update_group_attributes_success(self, client, mock_connection) -> None:
        """Test successful group attribute update."""
        attributes = {"description": "Updated description"}

        client._connection = mock_connection
        mock_connection.modify.return_value = True

        result = client.update_group_attributes(
            "cn=test,ou=groups,dc=example,dc=com", attributes
        )

        assert result.is_success
        assert result.value is True

    def test_delete_user_success(self, client, mock_connection) -> None:
        """Test successful user deletion."""
        client._connection = mock_connection
        mock_connection.delete.return_value = True

        result = client.delete_user("uid=test,ou=users,dc=example,dc=com")

        assert result.is_success

    def test_delete_group_success(self, client, mock_connection) -> None:
        """Test successful group deletion."""
        client._connection = mock_connection
        mock_connection.delete.return_value = True

        result = client.delete_group("cn=test,ou=groups,dc=example,dc=com")

        assert result.is_success

    def test_create_user_from_entry_complete(self, client) -> None:
        """Test _create_user_from_entry with complete data."""
        mock_entry = Mock()
        mock_entry.entry_dn = "uid=test,ou=users,dc=example,dc=com"
        mock_entry.cn.value = "Test User"
        mock_entry.uid.value = "testuser"
        mock_entry.sn.value = "User"
        mock_entry.givenName.value = "Test"
        mock_entry.mail.value = "test@example.com"
        mock_entry.telephoneNumber.value = "123-456-7890"
        mock_entry.mobile.value = "987-654-3210"
        mock_entry.departmentNumber.value = "IT"
        mock_entry.title.value = "Developer"
        mock_entry.o.value = "Example Corp"
        mock_entry.ou.value = "Engineering"
        mock_entry.userPassword.value = "password123"
        mock_entry.createTimestamp = None
        mock_entry.modifyTimestamp = None

        user = client._create_user_from_entry(mock_entry)

        assert user.uid == "testuser"
        assert user.cn == "Test User"
        assert user.mail == "test@example.com"

    def test_create_group_from_entry_complete(self, client) -> None:
        """Test _create_group_from_entry with complete data."""
        mock_entry = Mock()
        mock_entry.entry_dn = "cn=test,ou=groups,dc=example,dc=com"
        mock_entry.cn.value = "testgroup"
        mock_entry.gidNumber.value = 1000
        mock_entry.description.value = "Test Group"
        mock_entry.createTimestamp = None
        mock_entry.modifyTimestamp = None

        group = client._create_group_from_entry(mock_entry)

        assert group.cn == "testgroup"
        assert group.gid_number == 1000
        assert group.description == "Test Group"

    def test_no_connection_methods(self, client) -> None:
        """Test methods that require connection when no connection exists."""
        # Test all methods that should fail without connection
        methods_to_test = [
            (client.search_users, ("ou=users,dc=example,dc=com",)),
            (client.search_groups, ("ou=groups,dc=example,dc=com",)),
            (client.authenticate_user, ("user", "pass")),
            (
                client.create_user,
                (
                    FlextLdapModels.CreateUserRequest(
                        uid="test",
                        cn="Test",
                        sn="User",
                        given_name="Test",
                        mail="test@example.com",
                        user_password=SecretStr("pass"),
                    ),
                ),
            ),
            (
                client.create_group,
                (FlextLdapModels.CreateGroupRequest(cn="test", gid_number=1000),),
            ),
            (
                client.update_user_attributes,
                ("uid=test,dc=example,dc=com", {"mail": "new@example.com"}),
            ),
            (
                client.update_group_attributes,
                ("cn=test,dc=example,dc=com", {"description": "new"}),
            ),
            (client.delete_user, ("uid=test,dc=example,dc=com",)),
            (client.delete_group, ("cn=test,dc=example,dc=com",)),
        ]

        for method, args in methods_to_test:
            result = method(*args)
            assert result.is_failure
            assert "No connection established" in result.error


class TestFlextLdapClientClass:
    """Test FlextLdapClient class structure."""

    def test_class_structure(self) -> None:
        """Test that FlextLdapClient has expected methods."""
        assert hasattr(FlextLdapClient, "__init__")
        assert hasattr(FlextLdapClient, "connect")
        assert hasattr(FlextLdapClient, "disconnect")
