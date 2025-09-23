"""Comprehensive tests for FlextLdapClient - using ACTUAL API."""

from unittest.mock import Mock, patch

import pytest
from flext_ldap.clients import FlextLdapClient
from flext_ldap.models import FlextLdapModels


class TestFlextLdapClient:
    """Test FlextLdapClient implementation with actual API."""

    @pytest.fixture
    def client(self) -> FlextLdapClient:
        return FlextLdapClient()

    @pytest.fixture
    def mock_connection(self) -> Mock:
        mock_conn = Mock()
        mock_conn.bound = True
        mock_conn.last_error = None
        mock_conn.entries = []
        return mock_conn

    def test_initialization(self) -> None:
        client = FlextLdapClient()
        assert client._connection is None
        assert client._server is None
        assert client._logger is not None

    @pytest.mark.asyncio
    @patch("flext_ldap.clients.Connection")
    @patch("flext_ldap.clients.Server")
    async def test_connect_success(
        self,
        mock_server_class: Mock,
        mock_connection_class: Mock,
        client: FlextLdapClient,
    ) -> None:
        mock_server = Mock()
        mock_conn = Mock()
        mock_conn.bound = True
        mock_server_class.return_value = mock_server
        mock_connection_class.return_value = mock_conn

        result = await client.connect(
            "ldap://localhost:389", "cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com", "password"
        )

        assert result.is_success
        assert result.value is True
        mock_server_class.assert_called_once_with("ldap://localhost:389")
        mock_connection_class.assert_called_once_with(
            mock_server, "cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com", "password", auto_bind=True
        )

    @pytest.mark.asyncio
    @patch("flext_ldap.clients.Connection")
    @patch("flext_ldap.clients.Server")
    async def test_connect_bind_failure(
        self,
        mock_server_class: Mock,
        mock_connection_class: Mock,
        client: FlextLdapClient,
    ) -> None:
        mock_server = Mock()
        mock_conn = Mock()
        mock_conn.bound = False
        mock_server_class.return_value = mock_server
        mock_connection_class.return_value = mock_conn

        result = await client.connect(
            "ldap://localhost:389", "cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com", "wrongpass"
        )

        assert result.is_failure
        assert "Failed to bind" in result.error

    @pytest.mark.asyncio
    @patch("flext_ldap.clients.Server")
    async def test_connect_exception(
        self, mock_server_class: Mock, client: FlextLdapClient
    ) -> None:
        mock_server_class.side_effect = Exception("Connection error")

        result = await client.connect(
            "ldap://localhost:389", "cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com", "password"
        )

        assert result.is_failure
        assert "Connection failed" in result.error

    @pytest.mark.asyncio
    @patch("flext_ldap.clients.Connection")
    async def test_bind_success(
        self,
        mock_connection_class: Mock,
        client: FlextLdapClient,
        mock_connection: Mock,
    ) -> None:
        client._connection = mock_connection
        client._server = Mock()

        mock_new_conn = Mock()
        mock_new_conn.bound = True
        mock_connection_class.return_value = mock_new_conn

        result = await client.bind("cn=test,dc=example,dc=com", "password")

        assert result.is_success
        assert result.value is True

    @pytest.mark.asyncio
    @patch("flext_ldap.clients.Connection")
    async def test_bind_failure(
        self,
        mock_connection_class: Mock,
        client: FlextLdapClient,
        mock_connection: Mock,
    ) -> None:
        client._connection = mock_connection
        client._server = Mock()

        mock_new_conn = Mock()
        mock_new_conn.bound = False
        mock_connection_class.return_value = mock_new_conn

        result = await client.bind("cn=test,dc=example,dc=com", "wrongpass")

        assert result.is_failure
        assert "Bind failed" in result.error

    @pytest.mark.asyncio
    async def test_bind_no_connection(self, client: FlextLdapClient) -> None:
        result = await client.bind("cn=test,dc=example,dc=com", "password")

        assert result.is_failure
        assert "No connection established" in result.error

    @pytest.mark.asyncio
    async def test_unbind_success(
        self, client: FlextLdapClient, mock_connection: Mock
    ) -> None:
        client._connection = mock_connection

        result = await client.unbind()

        assert result.is_success
        mock_connection.unbind.assert_called_once()

    @pytest.mark.asyncio
    async def test_unbind_no_connection(self, client: FlextLdapClient) -> None:
        result = await client.unbind()

        assert result.is_success

    def test_is_connected_true(
        self, client: FlextLdapClient, mock_connection: Mock
    ) -> None:
        client._connection = mock_connection
        mock_connection.bound = True

        assert client.is_connected() is True

    def test_is_connected_false_no_connection(self, client: FlextLdapClient) -> None:
        assert client.is_connected() is False

    def test_is_connected_false_unbound(
        self, client: FlextLdapClient, mock_connection: Mock
    ) -> None:
        client._connection = mock_connection
        mock_connection.bound = False

        assert client.is_connected() is False

    def test_test_connection_connected(
        self, client: FlextLdapClient, mock_connection: Mock
    ) -> None:
        client._connection = mock_connection
        mock_connection.bound = True

        result = client.test_connection()

        assert result.is_success
        assert result.value is True

    def test_test_connection_not_connected(self, client: FlextLdapClient) -> None:
        result = client.test_connection()

        assert result.is_failure
        assert "Not connected" in result.error

    @pytest.mark.asyncio
    @patch("flext_ldap.clients.Connection")
    async def test_authenticate_user_success(
        self,
        mock_connection_class: Mock,
        client: FlextLdapClient,
        mock_connection: Mock,
    ) -> None:
        client._connection = mock_connection
        client._server = Mock()

        mock_entry = Mock()
        mock_entry.entry_dn = "uid=testuser,ou=users,dc=example,dc=com"
        mock_entry.uid = Mock(value="testuser")
        mock_entry.cn = Mock(value="Test User")
        mock_entry.sn = Mock(value="User")
        mock_entry.givenName = Mock(value="Test")
        mock_entry.mail = Mock(value="test@example.com")
        mock_entry.telephoneNumber = Mock(value=None)
        mock_entry.mobile = Mock(value=None)
        mock_entry.departmentNumber = Mock(value=None)
        mock_entry.title = Mock(value=None)
        mock_entry.o = Mock(value=None)
        mock_entry.ou = Mock(value=None)
        mock_entry.userPassword = Mock(value="secret")

        mock_connection.search.return_value = None
        mock_connection.entries = [mock_entry]

        mock_test_conn = Mock()
        mock_test_conn.bind.return_value = True
        mock_test_conn.unbind.return_value = None
        mock_connection_class.return_value = mock_test_conn

        result = await client.authenticate_user("testuser", "password")

        assert result.is_success
        assert isinstance(result.value, FlextLdapModels.LdapUser)

    @pytest.mark.asyncio
    @patch("flext_ldap.clients.Connection")
    async def test_authenticate_user_failure(
        self,
        mock_connection_class: Mock,
        client: FlextLdapClient,
        mock_connection: Mock,
    ) -> None:
        client._connection = mock_connection
        client._server = Mock()

        mock_entry = Mock()
        mock_entry.entry_dn = "uid=testuser,ou=users,dc=example,dc=com"
        mock_connection.search.return_value = None
        mock_connection.entries = [mock_entry]

        mock_test_conn = Mock()
        mock_test_conn.bind.return_value = False
        mock_connection_class.return_value = mock_test_conn

        result = await client.authenticate_user("testuser", "wrongpass")

        assert result.is_failure
        assert "Authentication failed" in result.error

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(
        self, client: FlextLdapClient, mock_connection: Mock
    ) -> None:
        client._connection = mock_connection
        mock_connection.search.return_value = None
        mock_connection.entries = []

        result = await client.authenticate_user("nonexistent", "password")

        assert result.is_failure
        assert "User not found" in result.error

    @pytest.mark.asyncio
    async def test_search_with_request_success(
        self, client: FlextLdapClient, mock_connection: Mock
    ) -> None:
        client._connection = mock_connection

        request = FlextLdapModels.SearchRequest(
            base_dn="ou=users,dc=example,dc=com",
            filter="(uid=test)",
            scope=FlextLdapModels.Scope.SUBTREE,
            attributes=["uid", "cn"],
            page_size=100,
            paged_cookie=b"",
        )

        mock_entry = Mock()
        mock_entry.entry_dn = "uid=test,ou=users,dc=example,dc=com"
        mock_entry.entry_attributes = ["uid", "cn"]
        mock_uid = Mock()
        mock_uid.value = "test"
        mock_cn = Mock()
        mock_cn.value = "Test User"
        mock_entry.__getitem__ = lambda self, key: mock_uid if key == "uid" else mock_cn

        mock_connection.search.return_value = True
        mock_connection.entries = [mock_entry]

        result = await client.search_with_request(request)

        assert result.is_success
        assert isinstance(result.value, FlextLdapModels.SearchResponse)
        assert result.value.total_count == 1

    @pytest.mark.asyncio
    async def test_search_users_success(
        self, client: FlextLdapClient, mock_connection: Mock
    ) -> None:
        client._connection = mock_connection

        mock_entry = Mock()
        mock_entry.entry_dn = "uid=test,ou=users,dc=example,dc=com"
        mock_entry.uid = Mock(value="test")
        mock_entry.cn = Mock(value="Test User")
        mock_entry.sn = Mock(value="User")
        mock_entry.givenName = Mock(value="Test")
        mock_entry.mail = Mock(value="test@example.com")
        mock_entry.telephoneNumber = Mock(value=None)
        mock_entry.mobile = Mock(value=None)
        mock_entry.departmentNumber = Mock(value=None)
        mock_entry.title = Mock(value=None)
        mock_entry.o = Mock(value=None)
        mock_entry.ou = Mock(value=None)
        mock_entry.userPassword = Mock(value="secret")

        mock_connection.search.return_value = True
        mock_connection.entries = [mock_entry]

        result = await client.search_users("ou=users,dc=example,dc=com", "(uid=test)")

        assert result.is_success
        assert len(result.value) > 0

    @pytest.mark.asyncio
    async def test_search_groups_success(
        self, client: FlextLdapClient, mock_connection: Mock
    ) -> None:
        client._connection = mock_connection

        mock_entry = Mock()
        mock_entry.entry_dn = "cn=testgroup,ou=groups,dc=example,dc=com"
        mock_entry.cn = Mock(value="testgroup")
        mock_entry.gidNumber = Mock(value=1000)
        mock_entry.description = Mock(value="Test Group")

        mock_connection.search.return_value = True
        mock_connection.entries = [mock_entry]

        result = await client.search_groups(
            "ou=groups,dc=example,dc=com", "(cn=testgroup)"
        )

        assert result.is_success
        assert len(result.value) > 0

    @pytest.mark.asyncio
    async def test_get_user_success(
        self, client: FlextLdapClient, mock_connection: Mock
    ) -> None:
        client._connection = mock_connection

        mock_entry = Mock()
        mock_entry.entry_dn = "uid=test,ou=users,dc=example,dc=com"
        mock_entry.uid = Mock(value="test")
        mock_entry.cn = Mock(value="Test User")
        mock_entry.sn = Mock(value="User")
        mock_entry.givenName = Mock(value="Test")
        mock_entry.mail = Mock(value="test@example.com")
        mock_entry.telephoneNumber = Mock(value=None)
        mock_entry.mobile = Mock(value=None)
        mock_entry.departmentNumber = Mock(value=None)
        mock_entry.title = Mock(value=None)
        mock_entry.o = Mock(value=None)
        mock_entry.ou = Mock(value=None)
        mock_entry.userPassword = Mock(value="secret")

        mock_connection.search.return_value = True
        mock_connection.entries = [mock_entry]

        result = await client.get_user("uid=test,ou=users,dc=example,dc=com")

        assert result.is_success
        assert result.value.uid == "test"

    @pytest.mark.asyncio
    async def test_get_group_success(
        self, client: FlextLdapClient, mock_connection: Mock
    ) -> None:
        client._connection = mock_connection

        mock_entry = Mock()
        mock_entry.entry_dn = "cn=testgroup,ou=groups,dc=example,dc=com"
        mock_entry.cn = Mock(value="testgroup")
        mock_entry.gidNumber = Mock(value=1000)
        mock_entry.description = Mock(value="Test Group")

        mock_connection.search.return_value = True
        mock_connection.entries = [mock_entry]

        result = await client.get_group("cn=testgroup,ou=groups,dc=example,dc=com")

        assert result.is_success
        assert result.value.cn == "testgroup"

    @pytest.mark.asyncio
    async def test_create_user_success(
        self, client: FlextLdapClient, mock_connection: Mock
    ) -> None:
        client._connection = mock_connection
        mock_connection.add.return_value = True

        request = FlextLdapModels.CreateUserRequest(
            dn="uid=newuser,ou=users,dc=example,dc=com",
            uid="newuser",
            cn="New User",
            sn="User",
            given_name="New",
            mail="newuser@example.com",
            user_password="ValidPass123!",
        )

        mock_entry = Mock()
        mock_entry.entry_dn = "uid=newuser,ou=users,dc=example,dc=com"
        mock_entry.uid = Mock(value="newuser")
        mock_entry.cn = Mock(value="New User")
        mock_entry.sn = Mock(value="User")
        mock_entry.givenName = Mock(value="New")
        mock_entry.mail = Mock(value="newuser@example.com")
        mock_entry.telephoneNumber = Mock(value=None)
        mock_entry.mobile = Mock(value=None)
        mock_entry.departmentNumber = Mock(value=None)
        mock_entry.title = Mock(value=None)
        mock_entry.o = Mock(value=None)
        mock_entry.ou = Mock(value=None)
        mock_entry.userPassword = Mock(value="secret")

        mock_connection.search.return_value = True
        mock_connection.entries = [mock_entry]

        result = await client.create_user(request)

        assert result.is_success
        assert result.value.uid == "newuser"

    @pytest.mark.asyncio
    async def test_create_group_success(
        self, client: FlextLdapClient, mock_connection: Mock
    ) -> None:
        client._connection = mock_connection
        mock_connection.add.return_value = True

        request = FlextLdapModels.CreateGroupRequest(
            dn="cn=newgroup,ou=groups,dc=example,dc=com",
            cn="newgroup",
        )

        mock_entry = Mock()
        mock_entry.entry_dn = "cn=newgroup,ou=groups,dc=example,dc=com"
        mock_entry.cn = Mock(value="newgroup")
        mock_entry.gidNumber = Mock(value=2000)
        mock_entry.description = Mock(value=None)

        mock_connection.search.return_value = True
        mock_connection.entries = [mock_entry]

        result = await client.create_group(request)

        assert result.is_success
        assert result.value.cn == "newgroup"

    @pytest.mark.asyncio
    async def test_update_user_attributes_success(
        self, client: FlextLdapClient, mock_connection: Mock
    ) -> None:
        client._connection = mock_connection
        mock_connection.modify.return_value = True

        result = await client.update_user_attributes(
            "uid=test,ou=users,dc=example,dc=com", {"mail": "new@example.com"}
        )

        assert result.is_success

    @pytest.mark.asyncio
    async def test_update_group_attributes_success(
        self, client: FlextLdapClient, mock_connection: Mock
    ) -> None:
        client._connection = mock_connection
        mock_connection.modify.return_value = True

        result = await client.update_group_attributes(
            "cn=test,ou=groups,dc=example,dc=com", {"description": "Updated"}
        )

        assert result.is_success

    @pytest.mark.asyncio
    async def test_delete_user_success(
        self, client: FlextLdapClient, mock_connection: Mock
    ) -> None:
        client._connection = mock_connection
        mock_connection.delete.return_value = True

        result = await client.delete_user("uid=test,ou=users,dc=example,dc=com")

        assert result.is_success

    @pytest.mark.asyncio
    async def test_delete_group_success(
        self, client: FlextLdapClient, mock_connection: Mock
    ) -> None:
        client._connection = mock_connection
        mock_connection.delete.return_value = True

        result = await client.delete_group("cn=test,ou=groups,dc=example,dc=com")

        assert result.is_success
