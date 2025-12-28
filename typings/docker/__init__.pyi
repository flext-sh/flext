"""Type stubs for docker package."""

from typing import Any

from docker.models.containers import ContainerCollection

def from_env(**kwargs: Any) -> DockerClient: ...

class DockerClient:
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    @property
    def containers(self) -> ContainerCollection: ...
    @property
    def api(self) -> Any: ...
