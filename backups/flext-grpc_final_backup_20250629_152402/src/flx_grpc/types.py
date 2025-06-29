"""Type definitions for gRPC using Python 3.13 advanced patterns.

This module provides protocol definitions for gRPC types to avoid
direct dependency on untyped gRPC modules while maintaining type safety.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Callable, Sequence

    from flx_core.domain.advanced_types import MetadataDict

# Type variables for generic protocols
TRequest = TypeVar("TRequest", contravariant=True)
TResponse = TypeVar("TResponse", covariant=True)
TServicer = TypeVar("TServicer")

# Python 3.13 type aliases for gRPC - with strict validation
type GrpcMetadata = Sequence[tuple[str, str | bytes]]
type GrpcStatusCode = int  # grpc.StatusCode values are integers
type GrpcStatus = object  # grpc.Status object
type GrpcServerCredentials = object  # grpc.ServerCredentials object
type GrpcHandlerCallDetails = object  # grpc.HandlerCallDetails object
type GrpcContinuation = Callable[[object], object]


class ServicerContext:
    """ServicerContext - Service Layer.

    Implementa serviço de aplicação com lógica de negócio específica.
    Coordena operações complexas entre múltiplos componentes.

    Arquitetura: Service Layer Pattern
    Transações: Atomic operations with rollback
    Padrões: Application services, orchestration

    Attributes:
    ----------
    Sem atributos públicos documentados.

    Methods:
    -------
    abort(): Método específico da classe
    abort_with_status(): Método específico da classe
    auth_context(): Método específico da classe
    peer(): Método específico da classe
    peer_identities(): Método específico da classe
    peer_identity_key(): Método específico da classe
    invocation_metadata(): Método específico da classe
    send_initial_metadata(): Inicializa componente
    set_trailing_metadata(): Método específico da classe
    set_code(): Método específico da classe
    set_details(): Método específico da classe

    Examples:
    --------
    Uso típico da classe:

    ```python
    service = ServicerContext(config)
    result = await service.process(data)
    ```

    See Also:
    --------
    - [Documentação da Arquitetura](../../docs/architecture/index.md)
    - [Padrões de Design](../../docs/architecture/001-clean-architecture-ddd.md)

    Note:
    ----
    Esta classe segue os padrões Service Layer Pattern estabelecidos no projeto.

    """

    """Protocol for gRPC servicer context."""

    def abort(self, code: GrpcStatusCode, details: str = "") -> None:
        """Abort the RPC with given status code and details."""

    def abort_with_status(self, status: GrpcStatus) -> None:
        """Abort the RPC with given status."""

    def auth_context(self) -> MetadataDict:
        """Get authentication context metadata.

        Retrieves authentication context information from the gRPC request,
        providing access to security metadata and user credentials.

        Returns:
        -------
            MetadataDict: Dictionary containing authentication context metadata.

        Note:
        ----
            Provides gRPC authentication context.

        """

    def peer(self) -> str:
        """Get peer address for connection identification.

        Retrieves the address of the client that initiated the gRPC connection
        for security logging and connection tracking purposes.

        Returns:
        -------
            str: Client peer address and port information.

        Note:
        ----
            Provides connection tracking for security and monitoring.

        """

    def peer_identities(self) -> Sequence[bytes] | None:
        """Get peer certificate identities for authentication.

        Retrieves client certificate identities from the gRPC connection
        for enterprise authentication and authorization processing.

        Returns:
        -------
            Sequence[bytes] | None: Client certificate identities or None if unavailable.

        Note:
        ----
            Supports enterprise PKI authentication and identity verification.

        """

    def peer_identity_key(self) -> str | None:
        """Get peer identity key from authentication context.

        Retrieves the identity key used for client authentication
        in enterprise PKI and certificate-based authentication systems.

        Returns:
        -------
            str | None: Identity key string or None if not available.

        Note:
        ----
            Enables enterprise identity verification and access control.

        """

    def invocation_metadata(self) -> GrpcMetadata:
        """Get request metadata for processing and authentication.

        Retrieves metadata sent by the client with the gRPC request,
        including authentication tokens, tracing headers, and custom metadata.

        Returns:
        -------
            GrpcMetadata: Request metadata key-value pairs.

        Note:
        ----
            Provides request context and metadata processing.

        """

    def send_initial_metadata(self, metadata: GrpcMetadata) -> None:
        """Send initial metadata to the client.

        Sends metadata headers to the client before streaming response data,
        useful for providing response context and additional information.

        Args:
        ----
            metadata: Metadata key-value pairs to send to client.

        Note:
        ----
            Enables enterprise response metadata and context communication.

        """

    def set_trailing_metadata(self, metadata: GrpcMetadata) -> None:
        """Set trailing metadata for response completion.

        Sets metadata that will be sent after the response body,
        typically used for final status information and metrics.

        Args:
        ----
            metadata: Trailing metadata key-value pairs.

        Note:
        ----
            Supports enterprise response finalization and metrics reporting.

        """

    def set_code(self, code: GrpcStatusCode) -> None:
        """Set response status code for error handling.

        Sets the gRPC status code for the response to indicate
        success, errors, or specific conditions to the client.

        Args:
        ----
            code: gRPC status code (OK, NOT_FOUND, INTERNAL, etc.).

        Note:
        ----
            Implements enterprise error reporting and status communication.

        """

    def set_details(self, details: str) -> None:
        """Set detailed error or status message.

        Sets descriptive text providing additional information about
        the response status, particularly useful for error conditions.

        Args:
        ----
            details: Human-readable status or error message.

        Note:
        ----
            Provides error messaging and diagnostic information.

        """


class UnaryUnaryMethod[TRequest, TResponse]:
    r"""UnaryUnaryMethod - Framework Component.

    Implementa componente central do framework com funcionalidades específicas.
    Segue padrões arquiteturais estabelecidos.

    Arquitetura: Enterprise Patterns
    Padrões: SOLID principles, clean code

    Attributes:
    ----------
    Sem atributos públicos documentados.

    Methods:
    -------
    Sem métodos públicos documentados.

    Examples:
    --------
    Uso típico da classe:

    ```python
    instance = UnaryUnaryMethod()\n    result = instance.method()
    ```

    See Also:
    --------
    - [Documentação da Arquitetura](../../docs/architecture/index.md)
    - [Padrões de Design](../../docs/architecture/001-clean-architecture-ddd.md)

    Note:
    ----
    Esta classe segue os padrões Enterprise Patterns estabelecidos no projeto.

    """

    """Protocol for unary-unary RPC method."""

    async def __call__(self, request: TRequest, context: ServicerContext) -> TResponse:
        """Handle unary request and return single response.

        Processes a single request message and returns a single response
        with proper error handling and enterprise monitoring.

        Args:
        ----
            request: Client request message.
            context: gRPC service context for metadata and control.

        Returns:
        -------
            TResponse: Single response message.

        Note:
        ----
            Implements enterprise unary RPC processing with full monitoring.

        """


class UnaryStreamMethod[TRequest, TResponse]:
    r"""UnaryStreamMethod - Framework Component.

    Implementa componente central do framework com funcionalidades específicas.
    Segue padrões arquiteturais estabelecidos.

    Arquitetura: Enterprise Patterns
    Padrões: SOLID principles, clean code

    Attributes:
    ----------
    Sem atributos públicos documentados.

    Methods:
    -------
    Sem métodos públicos documentados.

    Examples:
    --------
    Uso típico da classe:

    ```python
    instance = UnaryStreamMethod()\n    result = instance.method()
    ```

    See Also:
    --------
    - [Documentação da Arquitetura](../../docs/architecture/index.md)
    - [Padrões de Design](../../docs/architecture/001-clean-architecture-ddd.md)

    Note:
    ----
    Esta classe segue os padrões Enterprise Patterns estabelecidos no projeto.

    """

    """Protocol for unary-stream RPC method."""

    async def __call__(self, request: TRequest, context: ServicerContext) -> AsyncIterator[TResponse]:
        """Handle single request and stream multiple responses.

        Processes a single request message and yields multiple response messages
        for streaming data scenarios with enterprise monitoring.

        Args:
        ----
            request: Single client request message.
            context: gRPC service context for metadata and control.

        Yields:
        ------
            TResponse: Stream of response messages.

        Note:
        ----
            Implements enterprise streaming RPC with proper async iteration.

        """


class StreamUnaryMethod[TRequest, TResponse]:
    r"""StreamUnaryMethod - Framework Component.

    Implementa componente central do framework com funcionalidades específicas.
    Segue padrões arquiteturais estabelecidos.

    Arquitetura: Enterprise Patterns
    Padrões: SOLID principles, clean code

    Attributes:
    ----------
    Sem atributos públicos documentados.

    Methods:
    -------
    Sem métodos públicos documentados.

    Examples:
    --------
    Uso típico da classe:

    ```python
    instance = StreamUnaryMethod()\n    result = instance.method()
    ```

    See Also:
    --------
    - [Documentação da Arquitetura](../../docs/architecture/index.md)
    - [Padrões de Design](../../docs/architecture/001-clean-architecture-ddd.md)

    Note:
    ----
    Esta classe segue os padrões Enterprise Patterns estabelecidos no projeto.

    """

    """Protocol for stream-unary RPC method."""

    async def __call__(self, request_iterator: AsyncIterator[TRequest], context: ServicerContext) -> TResponse:
        """Handle streaming requests and return single response.

        Processes multiple request messages from a stream and returns
        a single response with enterprise aggregation and processing.

        Args:
        ----
            request_iterator: Stream of client request messages.
            context: gRPC service context for metadata and control.

        Returns:
        -------
            TResponse: Single aggregated response message.

        Note:
        ----
            Implements enterprise stream-to-unary RPC with aggregation.

        """


class StreamStreamMethod[TRequest, TResponse]:
    r"""StreamStreamMethod - Framework Component.

    Implementa componente central do framework com funcionalidades específicas.
    Segue padrões arquiteturais estabelecidos.

    Arquitetura: Enterprise Patterns
    Padrões: SOLID principles, clean code

    Attributes:
    ----------
    Sem atributos públicos documentados.

    Methods:
    -------
    Sem métodos públicos documentados.

    Examples:
    --------
    Uso típico da classe:

    ```python
    instance = StreamStreamMethod()\n    result = instance.method()
    ```

    See Also:
    --------
    - [Documentação da Arquitetura](../../docs/architecture/index.md)
    - [Padrões de Design](../../docs/architecture/001-clean-architecture-ddd.md)

    Note:
    ----
    Esta classe segue os padrões Enterprise Patterns estabelecidos no projeto.

    """

    """Protocol for stream-stream RPC method."""

    async def __call__(
        self, request_iterator: AsyncIterator[TRequest], context: ServicerContext
    ) -> AsyncIterator[TResponse]:
        """Handle streaming requests and stream responses.

        Processes multiple request messages from a stream and yields
        multiple response messages for full bidirectional streaming.

        Args:
        ----
            request_iterator: Stream of client request messages.
            context: gRPC service context for metadata and control.

        Yields:
        ------
            TResponse: Stream of response messages.

        Note:
        ----
            Implements enterprise bidirectional streaming with full async processing.

        """


class GrpcServer:
    """Protocol for gRPC server lifecycle management.

    Defines the interface for gRPC server operations including
    startup, shutdown, and service registration for enterprise deployment.

    Note:
    ----
        Provides gRPC server management with proper lifecycle control.

    """

    async def start(self) -> None:
        """Start the gRPC server for handling requests.

        Initiates the gRPC server to begin accepting and processing
        client requests with proper resource initialization.

        Note:
        ----
            Implements enterprise server startup with resource management.

        """

    async def stop(self, grace: float | None = None) -> None:
        """Stop the gRPC server gracefully.

        Initiates graceful shutdown of the gRPC server, allowing existing
        requests to complete before stopping.

        Note:
        ----
            Implements enterprise server shutdown with graceful request handling.

        """

    async def wait_for_termination(self, timeout: float | None = None) -> bool:
        """Wait for server termination with optional timeout.

        Blocks until the server has completely shut down, with optional
        timeout for enterprise deployment and lifecycle management.

        Args:
        ----
            timeout: Maximum time to wait for termination, None for indefinite.

        Returns:
        -------
            bool: True if server terminated within timeout, False otherwise.

        Note:
        ----
            Provides server lifecycle management with timeout control.

        """

    def add_insecure_port(self, address: str) -> int:
        """Add an insecure port for development and testing.

        Configures the server to listen on an insecure port without TLS,
        primarily for development environments and internal networks.

        Args:
        ----
            address: Network address and port to bind (e.g., 'localhost:50051').

        Returns:
        -------
            int: Bound port number.

        Note:
        ----
            Use only for development - enterprise deployments require secure ports.

        """

    def add_secure_port(self, address: str, server_credentials: GrpcServerCredentials) -> int:
        """Add a secure TLS port for production deployment.

        Configures the server to listen on a secure port with TLS encryption
        and client authentication for enterprise production environments.

        Args:
        ----
            address: Network address and port to bind (e.g., '0.0.0.0:443').
            server_credentials: TLS server credentials for secure communication.

        Returns:
        -------
            int: Bound port number.

        Note:
        ----
            Required for enterprise production deployments with security requirements.

        """


class ServerInterceptor:
    r"""ServerInterceptor - Server Component.

    Implementa componente servidor com protocolos específicos. Gerencia conexões e processamento de requisições.

    Arquitetura: Enterprise Patterns
    Padrões: SOLID principles, clean code

    Attributes:
    ----------
    Sem atributos públicos documentados.

    Methods:
    -------
    intercept_service(): Método específico da classe

    Examples:
    --------
    Uso típico da classe:

    ```python
    instance = ServerInterceptor()\n    result = instance.method()
    ```

    See Also:
    --------
    - [Documentação da Arquitetura](../../docs/architecture/index.md)
    - [Padrões de Design](../../docs/architecture/001-clean-architecture-ddd.md)

    Note:
    ----
    Esta classe segue os padrões Enterprise Patterns estabelecidos no projeto.

    """

    """Protocol for gRPC server interceptor."""

    def intercept_service(self, continuation: GrpcContinuation, handler_call_details: GrpcHandlerCallDetails) -> object:
        """Intercept gRPC service calls for middleware processing.

        Provides middleware functionality for authentication, logging,
        metrics collection, and other cross-cutting concerns.

        Args:
        ----
            continuation: Next handler in the interceptor chain.
            handler_call_details: Details about the gRPC call being intercepted.

        Returns:
        -------
            object: Result from the continuation or modified response.

        Note:
        ----
            Enables enterprise middleware patterns for security and monitoring.

        """


# Reflection pattern for automatic servicer registration


class ServicerRegistration:
    """Protocol for servicer registration using reflection."""

    @classmethod
    def register_methods(cls) -> MetadataDict:
        """Register RPC methods using reflection."""

    @classmethod
    def get_service_name(cls) -> str:
        """Get service name for registration."""
