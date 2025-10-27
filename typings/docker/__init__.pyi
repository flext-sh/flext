"""Type stubs for docker (docker-py).

PEP 561 compliant type stubs for the docker library.
"""

from typing import Any

from docker.client import DockerClient
from docker.errors import APIError, DockerException, NotFound

def from_env(
    version: str | None = None,
    timeout: int | None = None,
    ssl_version: int | None = None,
    assert_hostname: bool | None = None,
    **kwargs: Any,
) -> DockerClient:
    """Create a Docker client configured from environment variables."""
    ...

__all__ = ["DockerClient", "APIError", "DockerException", "NotFound", "from_env"]
