"""Lightweight connection handling for MCP servers."""

from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager, AsyncExitStack
from types import TracebackType
from typing import Self

from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client

from . import t

_RESULT_ARITY_REQUEST = 2
_RESULT_ARITY_FULL = 3


def _result_pair(result: t.VariadicTuple[object]) -> tuple[object, object]:
    """Split a context-manager result into its read/write pair.

    Versioned clients expose an extra trailing element; keep only the pair.
    """
    if len(result) == _RESULT_ARITY_REQUEST:
        first, second = result
        return first, second
    if len(result) == _RESULT_ARITY_FULL:
        first, second, _ = result
        return first, second
    sentinel = f"Unexpected context result: {result}"
    raise ValueError(sentinel)


class MCPConnection(ABC):
    """Base class for MCP server connections."""

    session: ClientSession | None
    _stack: AsyncExitStack | None

    def __init__(self) -> None:
        """Initialize the base connection state."""
        self.session = None
        self._stack = None

    @abstractmethod
    def _create_context(self) -> AbstractAsyncContextManager[object]:
        """Create the connection context based on connection type."""

    async def _attach(self, context: AbstractAsyncContextManager[object]) -> None:
        """Enter the transport context and initialize one session."""
        result = await self._stack.enter_async_context(context)
        read, write = _result_pair(result)
        self.session = await self._stack.enter_async_context(ClientSession(read, write))
        await self.session.initialize()

    async def __aenter__(self) -> Self:
        """Initialize MCP server connection."""
        self._stack = AsyncExitStack()
        await self._stack.__aenter__()
        try:
            context = self._create_context()
            await self._attach(context)
        except BaseException:
            await self._stack.__aexit__(None, None, None)
            raise
        else:
            return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Clean up MCP server connection resources."""
        if self._stack:
            await self._stack.__aexit__(exc_type, exc_val, exc_tb)
        self.session = None
        self._stack = None

    async def list_tools(self) -> list[dict[str, object]]:
        """Retrieve available tools from the MCP server."""
        response = await self.session.list_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema,
            }
            for tool in response.tools
        ]

    async def call_tool(self, tool_name: str, arguments: dict[str, object]) -> object:
        """Call a tool on the MCP server with provided arguments."""
        result = await self.session.call_tool(tool_name, arguments=arguments)
        return result.content


class MCPConnectionStdio(MCPConnection):
    """MCP connection using standard input/output."""

    def __init__(
        self,
        command: str,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
    ) -> None:
        """Initialize one stdio connection."""
        super().__init__()
        self.command = command
        self.args = args or []
        self.env = env

    def _create_context(self) -> AbstractAsyncContextManager[object]:
        """Create the stdio transport context."""
        return stdio_client(
            StdioServerParameters(command=self.command, args=self.args, env=self.env)
        )


class MCPConnectionSSE(MCPConnection):
    """MCP connection using Server-Sent Events."""

    def __init__(self, url: str, headers: dict[str, str] | None = None) -> None:
        """Initialize one Server-Sent Events connection."""
        super().__init__()
        self.url = url
        self.headers = headers or {}

    def _create_context(self) -> AbstractAsyncContextManager[object]:
        """Create the Server-Sent Events transport context."""
        return sse_client(url=self.url, headers=self.headers)


class MCPConnectionHTTP(MCPConnection):
    """MCP connection using Streamable HTTP."""

    def __init__(self, url: str, headers: dict[str, str] | None = None) -> None:
        """Initialize one Streamable HTTP connection."""
        super().__init__()
        self.url = url
        self.headers = headers or {}

    def _create_context(self) -> AbstractAsyncContextManager[object]:
        """Create the Streamable HTTP transport context."""
        return streamablehttp_client(url=self.url, headers=self.headers)


def create_connection(
    transport: str,
    command: str | None = None,
    args: list[str] | None = None,
    env: dict[str, str] | None = None,
    url: str | None = None,
    headers: dict[str, str] | None = None,
) -> MCPConnection:
    """Factory function to create the appropriate MCP connection.

    Args:
        transport: Connection type ("stdio", "sse", or "http")
        command: Command to run (stdio only)
        args: Command arguments (stdio only)
        env: Environment variables (stdio only)
        url: Server URL (sse and http only)
        headers: HTTP headers (sse and http only)

    Returns:
        MCPConnection instance

    """
    transport = transport.lower()

    if transport == "stdio":
        if not command:
            msg = "Command is required for stdio transport"
            raise ValueError(msg)
        return MCPConnectionStdio(command=command, args=args, env=env)

    if transport == "sse":
        if not url:
            msg = "URL is required for sse transport"
            raise ValueError(msg)
        return MCPConnectionSSE(url=url, headers=headers)

    if transport in {"http", "streamable_http", "streamable-http"}:
        if not url:
            msg = "URL is required for http transport"
            raise ValueError(msg)
        return MCPConnectionHTTP(url=url, headers=headers)

    msg = f"Unsupported transport type: {transport}. Use 'stdio', 'sse', or 'http'"
    raise ValueError(msg)
