"""Type stubs for ldap3.core.connection - overrides official stubs with return types."""

from typing import Any, Literal

from ldap3.core.server import Server

class Connection:
    """LDAP Connection object with typed method returns."""
    
    server: Server
    user: str | None
    password: str | None
    auto_bind: bool | int
    result: dict[str, Any]
    entries: list[Any]
    response: list[dict[str, Any]] | None

    def __init__(
        self,
        server: Server | str,
        user: str | None = None,
        password: str | None = None,
        auto_bind: bool | int = False,
        **kwargs: Any,
    ) -> None: ...

    def bind(
        self,
        read_server_info: bool = True,
        controls: Any = None,
    ) -> bool: ...

    def unbind(self, controls: Any = None) -> bool: ...

    def search(
        self,
        search_base: str,
        search_filter: str,
        search_scope: Literal["BASE", "LEVEL", "SUBTREE"] = "SUBTREE",
        dereference_aliases: Literal["NEVER", "SEARCH", "FINDING_BASE", "ALWAYS"] = "ALWAYS",
        attributes: list[str] | str | None = None,
        size_limit: int = 0,
        time_limit: int = 0,
        types_only: bool = False,
        get_operational_attributes: bool = False,
        controls: Any = None,
        paged_size: int | None = None,
        paged_criticality: bool = False,
        paged_cookie: str | bytes | None = None,
        auto_escape: bool | None = None,
    ) -> bool: ...

    def add(
        self,
        dn: str,
        object_class: list[str] | str | None = None,
        attributes: dict[str, Any] | None = None,
        controls: Any = None,
    ) -> bool: ...

    def delete(
        self,
        dn: str,
        controls: Any = None,
    ) -> bool: ...

    def modify(
        self,
        dn: str,
        changes: dict[str, list[tuple[int, Any]]],
        controls: Any = None,
    ) -> bool: ...

    def modify_dn(
        self,
        dn: str,
        relative_dn: str,
        delete_old_dn: bool = True,
        new_superior: str | None = None,
        controls: Any = None,
    ) -> bool: ...

    def compare(
        self,
        dn: str,
        attribute: str,
        value: Any,
        controls: Any = None,
    ) -> bool: ...
