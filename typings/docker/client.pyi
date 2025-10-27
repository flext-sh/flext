"""Type stubs for docker.client module."""

from typing import Any

class DockerClient:
    """Docker API client."""

    containers: Any
    images: Any
    networks: Any
    volumes: Any

    def __init__(
        self,
        base_url: str | None = None,
        version: str | None = None,
        timeout: int | None = None,
        tls: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialize Docker client."""
        ...

    @classmethod
    def from_env(
        cls,
        version: str | None = None,
        timeout: int | None = None,
        ssl_version: int | None = None,
        assert_hostname: bool | None = None,
        **kwargs: Any,
    ) -> DockerClient:
        """Create a Docker client configured from environment variables."""
        ...
