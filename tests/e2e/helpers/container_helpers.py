"""Container management utilities for E2E tests."""

import subprocess
import time
from pathlib import Path
from typing import Any

import docker


class ContainerManager:
    """Manage Docker containers for E2E tests."""

    def __init__(self, compose_file: Path) -> None:
        self.compose_file = compose_file
        self.compose_dir = compose_file.parent
        self.client = docker.from_env()

    def start_services(
        self,
        services: list[str] | None = None,
        wait_for_healthy: bool = True,
        timeout: int = 60,
    ) -> None:
        """Start docker-compose services."""
        cmd = ["docker-compose", "-f", str(self.compose_file), "up", "-d"]

        if services:
            cmd.extend(services)

        result = subprocess.run(
            cmd, cwd=self.compose_dir, capture_output=True, text=True, check=False
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to start services: {result.stderr}")

        if wait_for_healthy:
            self.wait_for_services(services, timeout)

    def stop_services(
        self, services: list[str] | None = None, remove_volumes: bool = False
    ) -> None:
        """Stop docker-compose services."""
        cmd = ["docker-compose", "-f", str(self.compose_file), "down"]

        if remove_volumes:
            cmd.append("-v")

        if services:
            cmd.extend(services)

        subprocess.run(cmd, cwd=self.compose_dir, capture_output=True, check=False)

    def restart_service(self, service: str) -> None:
        """Restart a specific service."""
        cmd = ["docker-compose", "-f", str(self.compose_file), "restart", service]

        subprocess.run(cmd, cwd=self.compose_dir, capture_output=True, check=True)

    def get_service_logs(
        self, service: str, lines: int = 100, follow: bool = False
    ) -> str:
        """Get logs from a service."""
        cmd = ["docker-compose", "-f", str(self.compose_file), "logs"]

        if not follow:
            cmd.append("--no-follow")

        cmd.extend(["--tail", str(lines), service])

        result = subprocess.run(
            cmd, cwd=self.compose_dir, capture_output=True, text=True, check=False
        )

        return result.stdout

    def exec_in_service(
        self, service: str, command: list[str], user: str | None = None
    ) -> subprocess.CompletedProcess:
        """Execute command in a service container."""
        cmd = ["docker-compose", "-f", str(self.compose_file), "exec", "-T"]

        if user:
            cmd.extend(["-u", user])

        cmd.append(service)
        cmd.extend(command)

        return subprocess.run(
            cmd, cwd=self.compose_dir, capture_output=True, text=True, check=False
        )

    def wait_for_services(
        self, services: list[str] | None = None, timeout: int = 60
    ) -> None:
        """Wait for services to be healthy."""
        start_time = time.time()

        if not services:
            # Get all services from compose file
            result = subprocess.run(
                ["docker-compose", "-f", str(self.compose_file), "ps", "--services"],
                cwd=self.compose_dir,
                capture_output=True,
                text=True,
                check=False,
            )
            services = result.stdout.strip().split("\n")

        while time.time() - start_time < timeout:
            all_healthy = True

            for service in services:
                if not self._is_service_healthy(service):
                    all_healthy = False
                    break

            if all_healthy:
                return

            time.sleep(2)

        raise TimeoutError(f"Services did not become healthy within {timeout} seconds")

    def get_service_info(self, service: str) -> dict[str, Any]:
        """Get information about a service."""
        container = self._get_container(service)

        if not container:
            return {}

        return {
            "id": container.id,
            "name": container.name,
            "status": container.status,
            "health": container.health if hasattr(container, "health") else None,
            "ports": container.ports,
            "labels": container.labels,
            "image": container.image.tags[0] if container.image.tags else None,
        }

    def get_service_port(self, service: str, internal_port: int) -> int | None:
        """Get the external port mapping for a service."""
        container = self._get_container(service)

        if not container:
            return None

        port_key = f"{internal_port}/tcp"
        if port_key in container.ports:
            mappings = container.ports[port_key]
            if mappings and len(mappings) > 0:
                return int(mappings[0]["HostPort"])

        return None

    def backup_volume(self, volume_name: str, backup_path: Path) -> None:
        """Backup a Docker volume to a tar file."""
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        # Create a temporary container to access the volume
        container = self.client.containers.run(
            "alpine",
            command="tar czf /backup.tar.gz /data",
            volumes={volume_name: {"bind": "/data", "mode": "ro"}},
            detach=True,
            remove=False,
        )

        # Wait for backup to complete
        container.wait()

        # Copy backup file
        bits, _ = container.get_archive("/backup.tar.gz")

        with open(backup_path, "wb") as f:
            for chunk in bits:
                f.write(chunk)

        # Remove temporary container
        container.remove()

    def restore_volume(self, volume_name: str, backup_path: Path) -> None:
        """Restore a Docker volume from a tar file."""
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        # Create volume if it doesn't exist
        try:
            self.client.volumes.get(volume_name)
        except docker.errors.NotFound:
            self.client.volumes.create(volume_name)

        # Create a temporary container to restore the volume
        container = self.client.containers.run(
            "alpine",
            command="sh -c 'cd /data && tar xzf /backup.tar.gz --strip-components=1'",
            volumes={volume_name: {"bind": "/data", "mode": "rw"}},
            detach=True,
            remove=False,
        )

        # Copy backup file to container
        with open(backup_path, "rb") as f:
            container.put_archive("/", f.read())

        # Wait for restore to complete
        container.wait()

        # Remove temporary container
        container.remove()

    def _get_container(self, service: str) -> docker.models.containers.Container | None:
        """Get container object for a service."""
        # Get container name from docker-compose
        result = subprocess.run(
            ["docker-compose", "-f", str(self.compose_file), "ps", "-q", service],
            cwd=self.compose_dir,
            capture_output=True,
            text=True,
            check=False,
        )

        container_id = result.stdout.strip()

        if not container_id:
            return None

        try:
            return self.client.containers.get(container_id)
        except docker.errors.NotFound:
            return None

    def _is_service_healthy(self, service: str) -> bool:
        """Check if a service is healthy."""
        container = self._get_container(service)

        if not container:
            return False

        if container.status != "running":
            return False

        # Check health status if available
        try:
            if hasattr(container, "health"):
                health = container.attrs.get("State", {}).get("Health", {})
                return health.get("Status") == "healthy"
        except:
            pass

        # For services without health checks, assume healthy if running
        return True

    def cleanup_all(self) -> None:
        """Clean up all containers, volumes, and networks."""
        # Stop all services
        self.stop_services(remove_volumes=True)

        # Remove any orphaned containers
        subprocess.run(
            ["docker-compose", "-f", str(self.compose_file), "rm", "-f", "-s", "-v"],
            cwd=self.compose_dir,
            capture_output=True,
            check=False,
        )

        # Prune networks
        self.client.networks.prune()


class ServiceHealthChecker:
    """Health checkers for specific services."""

    @staticmethod
    def check_ldap(host: str, port: int, bind_dn: str, password: str) -> bool:
        """Check if LDAP service is healthy."""
        try:
            from ldap3 import Connection, Server

            server = Server(host, port=port)
            conn = Connection(server, user=bind_dn, password=password, auto_bind=True)
            conn.unbind()
            return True
        except:
            return False

    @staticmethod
    def check_postgres(
        host: str, port: int, database: str, user: str, password: str
    ) -> bool:
        """Check if PostgreSQL service is healthy."""
        try:
            import psycopg2

            conn = psycopg2.connect(
                host=host, port=port, database=database, user=user, password=password
            )
            conn.close()
            return True
        except:
            return False
