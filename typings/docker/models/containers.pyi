"""Type stubs for docker.models.containers module."""

from typing import Any

class Container:
    """Docker container model.

    Represents a Docker container with methods for lifecycle management.
    """

    # Attributes
    attrs: dict[str, Any]
    id: str
    name: str
    status: str

    def kill(self, signal: str | int | None = None) -> None:
        """Kill or send a signal to the container.

        Args:
            signal: The signal to send. Can be a signal name (str) like "SIGKILL"
                   or a signal number (int). Defaults to SIGKILL if not specified.

        Raises:
            docker.errors.APIError: If the server returns an error.

        """
        ...

    def stop(self, timeout: int | None = None) -> None:
        """Stop the container.

        Args:
            timeout: Timeout in seconds to wait for the container to stop
                    before sending SIGKILL.

        """
        ...

    def reload(self) -> None:
        """Reload this object from the server."""
        ...

    def remove(self, v: bool = False, link: bool = False, force: bool = False) -> None:
        """Remove the container.

        Args:
            v: Remove volumes associated with the container.
            link: Remove the specified link.
            force: Force removal of a running container.

        """
        ...
