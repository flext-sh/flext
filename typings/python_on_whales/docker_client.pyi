"""Type stubs for python_on_whales.docker_client module."""

from pathlib import Path
from typing import Literal

class ClientConfig:
    """Configuration for Docker client."""

    compose_files: list[str]

class ComposeManager:
    """Docker Compose operations manager."""

    def up(
        self,
        services: list[str] = [],
        detach: bool = True,
        build: bool = False,
        force_recreate: bool = False,
        no_build: bool = False,
        no_deps: bool = False,
        pull: str | None = None,
        quiet: bool = False,
        remove_orphans: bool = False,
        scale: dict[str, int] = {},
        stream_logs: bool = False,
        timeout: int | None = None,
        wait: bool = False,
    ) -> None:
        """Bring up compose services."""

    def down(
        self,
        remove_orphans: bool = False,
        remove_images: str | None = None,
        timeout: int | None = None,
        volumes: bool = False,
    ) -> None:
        """Bring down compose services."""

class DockerClient:
    """Python-on-whales Docker client.

    This is the main client for interacting with Docker using python-on-whales.
    """

    # Configuration
    client_config: ClientConfig

    # Managers
    compose: ComposeManager

    def __init__(
        self,
        config: str | Path | None = None,
        context: str | None = None,
        debug: bool | None = None,
        host: str | None = None,
        log_level: str | None = None,
        tls: bool | None = None,
        tlscacert: str | Path | None = None,
        tlscert: str | Path | None = None,
        tlskey: str | Path | None = None,
        tlsverify: bool | None = None,
        client_config: ClientConfig | None = None,
        compose_files: list[str | Path] = [],
        compose_profiles: list[str] = [],
        compose_env_file: str | Path | None = None,
        compose_env_files: list[str | Path] = [],
        compose_project_name: str | None = None,
        compose_project_directory: str | Path | None = None,
        compose_compatibility: bool | None = None,
        client_binary: str = "docker",
        client_call: list[str] = ["docker"],
        client_type: Literal["docker", "podman", "nerdctl", "unknown"] = "unknown",
    ) -> None:
        """Initialize Docker client."""
