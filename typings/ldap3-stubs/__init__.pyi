"""Type stubs for ldap3 library."""

from typing import Any, Final

__version__: Final[str]
__author__: Final[str]
__email__: Final[str]
__url__: Final[str]
__description__: Final[str]
__status__: Final[str]
__license__: Final[str]

# Modify operation constants
MODIFY_ADD: Final[int]
MODIFY_DELETE: Final[int]
MODIFY_REPLACE: Final[int]
MODIFY_INCREMENT: Final[int]

# Search scope constants
SUBTREE: Final[int]
LEVEL: Final[int]
BASE: Final[int]

# Authentication constants
SIMPLE: Final[int]
ANONYMOUS: Final[int]
SASL: Final[int]
NTLM: Final[int]

# Connection strategy constants
SYNC: Final[int]
ASYNC: Final[int]
LDIF: Final[int]
RESTARTABLE: Final[int]
REUSABLE: Final[int]


class Server:
    """LDAP Server representation."""

    host: str
    port: int
    use_ssl: bool
    get_info: Any
    mode: Any
    tls: Any

    def __init__(
        self,
        host: str,
        port: int = 389,
        use_ssl: bool = False,
        get_info: Any = None,
        mode: Any = None,
        tls: Any = None,
        connect_timeout: int | None = None,
        **kwargs: Any,
    ) -> None: ...


class Connection:
    """LDAP Connection object."""

    server: Server
    user: str | None
    password: str | None
    auto_bind: bool | int
    client_strategy: Any
    authentication: Any
    read_only: bool
    lazy: bool
    check_names: bool
    raise_exceptions: bool
    result: dict[str, Any]
    entries: list[Any]
    response: list[dict[str, Any]] | None

    def __init__(
        self,
        server: Server | str,
        user: str | None = None,
        password: str | None = None,
        auto_bind: bool | int = False,
        client_strategy: Any = None,
        authentication: Any = None,
        read_only: bool = False,
        lazy: bool = False,
        check_names: bool = True,
        raise_exceptions: bool = False,
        pool_size: int | None = None,
        pool_lifetime: int | None = None,
        **kwargs: Any,
    ) -> None: ...

    def bind(
        self,
        read_server_info: bool = True,
        controls: list[Any] | None = None,
    ) -> bool: ...

    def unbind(self) -> bool: ...

    def search(
        self,
        search_base: str,
        search_filter: str,
        search_scope: int = ...,
        dereference_aliases: int = ...,
        attributes: list[str] | str | None = None,
        size_limit: int = 0,
        time_limit: int = 0,
        types_only: bool = False,
        get_operational_attributes: bool = False,
        controls: list[Any] | None = None,
        paged_size: int | None = None,
        paged_criticality: bool = False,
        paged_cookie: bytes | None = None,
        **kwargs: Any,
    ) -> bool: ...

    def add(
        self,
        dn: str,
        object_class: list[str] | str | None = None,
        attributes: dict[str, Any] | None = None,
        controls: list[Any] | None = None,
    ) -> bool: ...

    def modify(
        self,
        dn: str,
        changes: dict[str, list[tuple[int, Any]]],
        controls: list[Any] | None = None,
    ) -> bool: ...

    def delete(
        self,
        dn: str,
        controls: list[Any] | None = None,
    ) -> bool: ...

    def modify_dn(
        self,
        dn: str,
        relative_dn: str,
        delete_old_dn: bool = True,
        new_superior: str | None = None,
        controls: list[Any] | None = None,
    ) -> bool: ...

    def compare(
        self,
        dn: str,
        attribute: str,
        value: Any,
        controls: list[Any] | None = None,
    ) -> bool: ...

    def extend(self) -> Any: ...


class LDAPException(Exception):
    """Base exception for LDAP operations."""

    ...


class LDAPBindError(LDAPException):
    """Bind operation failed."""

    ...


class LDAPSocketOpenError(LDAPException):
    """Socket open failed."""

    ...


class LDAPSocketCloseError(LDAPException):
    """Socket close failed."""

    ...


class LDAPCommunicationError(LDAPException):
    """Communication error."""

    ...


class LDAPEntryAlreadyExistsResult(LDAPException):
    """Entry already exists."""

    ...


class LDAPNoSuchObjectResult(LDAPException):
    """No such object."""

    ...
