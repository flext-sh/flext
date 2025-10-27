"""Type stubs for python-on-whales.

PEP 561 compliant type stubs for the python-on-whales library.
"""

from python_on_whales.docker_client import DockerClient

# Pre-instantiated docker client (the main export)
docker: DockerClient

__all__ = ["DockerClient", "docker"]
