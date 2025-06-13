"""OIC Endpoint Configuration Utilities.

This module provides utilities for configuring OIC endpoints.
"""

import json
import logging

from tap_oic.client import OICClient

logger = logging.getLogger(__name__)


class EndpointConfigurator:
    """Configurator for OIC endpoints."""

    def __init__(self, client: OICClient) -> None:
        """Initialize endpoint configurator.

        Args:
            client: OIC client instance

        """
        self.client = client

    def create_ftp_endpoint(
        self,
        name: str,
        host: str,
        port: int,
        username: str,
        password: str,
        folder_path: str,
    ) -> dict:
        """Create an FTP endpoint in OIC.

        Args:
            name: Endpoint name
            host: FTP server hostname
            port: FTP server port
            username: FTP username
            password: FTP password
            folder_path: Path to FTP folder

        Returns:
            Created endpoint configuration

        """
        config = {
            "name": name,
            "identifier": name.replace(" ", "_").lower(),
            "connectionType": "FTP",
            "description": f"FTP connection to {host}",
            "properties": {
                "hostName": host,
                "port": port,
                "username": username,
                "password": password,
                "folderPath": folder_path,
                "securityPolicy": "NONE",
            },
        }

        logger.info(f"Creating FTP endpoint: {name}")
        return self.client.create_endpoint(config)

    def create_rest_endpoint(
        self,
        name: str,
        url: str,
        auth_type: str = "BASIC",
        username: str | None = None,
        password: str | None = None,
    ) -> dict:
        """Create a REST endpoint in OIC.

        Args:
            name: Endpoint name
            url: Base URL for REST service
            auth_type: Authentication type (BASIC, OAUTH, NONE)
            username: Username for Basic auth
            password: Password for Basic auth

        Returns:
            Created endpoint configuration

        """
        config = {
            "name": name,
            "identifier": name.replace(" ", "_").lower(),
            "connectionType": "REST",
            "description": f"REST connection to {url}",
            "properties": {"connectionUrl": url, "securityPolicy": auth_type},
        }

        if auth_type == "BASIC" and username and password:
            config["properties"]["username"] = username
            config["properties"]["password"] = password

        logger.info(f"Creating REST endpoint: {name}")
        return self.client.create_endpoint(config)

    def create_adb_endpoint(
        self,
        name: str,
        host: str,
        port: int,
        service_name: str,
        username: str,
        password: str,
    ) -> dict:
        """Create an Oracle ADB endpoint in OIC.

        Args:
            name: Endpoint name
            host: Database hostname
            port: Database port
            service_name: Database service name
            username: Database username
            password: Database password

        Returns:
            Created endpoint configuration

        """
        config = {
            "name": name,
            "identifier": name.replace(" ", "_").lower(),
            "connectionType": "ORACLE",
            "description": f"Oracle ADB connection to {host}",
            "properties": {
                "hostname": host,
                "port": port,
                "serviceName": service_name,
                "username": username,
                "password": password,
                "securityPolicy": "BASIC_AUTH",
            },
        }

        logger.info(f"Creating Oracle ADB endpoint: {name}")
        return self.client.create_endpoint(config)

    def create_wms_endpoint(
        self,
        name: str,
        url: str,
        client_id: str,
        client_secret: str,
    ) -> dict:
        """Create a WMS endpoint in OIC.

        Args:
            name: Endpoint name
            url: WMS API base URL
            client_id: OAuth client ID
            client_secret: OAuth client secret

        Returns:
            Created endpoint configuration

        """
        config = {
            "name": name,
            "identifier": name.replace(" ", "_").lower(),
            "connectionType": "REST",
            "description": f"WMS connection to {url}",
            "properties": {
                "connectionUrl": url,
                "securityPolicy": "OAUTH2_CLIENT_CREDENTIALS_GRANT",
                "clientId": client_id,
                "clientSecret": client_secret,
            },
        }

        logger.info(f"Creating WMS endpoint: {name}")
        return self.client.create_endpoint(config)

    def export_endpoint_config(self, configs: list[dict], filepath: str) -> None:
        """Export endpoint configurations to a file.

        Args:
            configs: list of endpoint configurations
            filepath: Path to output file

        """
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(configs, f, indent=2)
        logger.info(f"Exported {len(configs)} endpoint configurations to {filepath}")

    def import_endpoint_config(self, filepath: str) -> list[dict]:
        """Import endpoint configurations from a file.

        Args:
            filepath: Path to input file

        Returns:
            list of created endpoint configurations

        """
        with open(filepath, encoding="utf-8") as f:
            configs = json.load(f)

        results = []
        for config in configs:
            logger.info(f"Importing endpoint: {config.get('name')}")
            result = self.client.create_endpoint(config)
            results.append(result)

        return results
