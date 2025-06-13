"""OIC Orchestration.

This module provides functionality for orchestrating Oracle Integration Cloud integrations.
"""

import json
import logging
import time
from datetime import datetime

import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


class OICOrchestrator:
    """Orchestrator for OIC integrations."""

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        config_file: str | None = None,
        config: dict | None = None,
    ) -> None:
        """Initialize OIC orchestrator.

        Args:
            base_url: OIC base URL
            username: OIC username
            password: OIC password
            config_file: Path to orchestration configuration file
            config: Orchestration configuration dictionary

        """
        self.base_url = base_url.rstrip("/")
        self.auth = HTTPBasicAuth(username, password)
        self.session = requests.Session()

        # Load configuration
        if config:
            self.config = config
        elif config_file:
            with open(config_file, encoding="utf-8") as f:
                self.config = json.load(f)
        else:
            self.config = {}

        # Initialize execution stats
        self.stats = {
            "started_at": None,
            "completed_at": None,
            "total_integrations": 0,
            "successful": 0,
            "failed": 0,
            "integrations": [],
        }

    def get_integrations(self) -> list[dict]:
        """Get list of all integrations.

        Returns:
            list of integration configurations

        """
        endpoint = f"{self.base_url}/ic/api/integration/v1/integrations"
        response = self.session.get(endpoint, auth=self.auth, timeout=60)
        response.raise_for_status()
        return response.json()

    def get_integration(self, integration_id: str) -> dict:
        """Get details of a specific integration.

        Args:
            integration_id: ID of the integration

        Returns:
            Integration details

        """
        endpoint = (
            f"{self.base_url}/ic/api/integration/v1/integrations/{integration_id}"
        )
        response = self.session.get(endpoint, auth=self.auth, timeout=60)
        response.raise_for_status()
        return response.json()

    def execute_integration(
        self,
        integration_id: str,
        payload: dict | None = None,
    ) -> dict:
        """Execute an integration.

        Args:
            integration_id: ID of the integration to execute
            payload: Optional payload data

        Returns:
            Execution details

        """
        endpoint = f"{self.base_url}/ic/api/integration/v1/integrations/{integration_id}/execute"

        # Use empty dict if payload is None
        json_data = payload or {}

        logger.info(f"Executing integration: {integration_id}")

        response = self.session.post(
            endpoint,
            auth=self.auth,
            json=json_data,
            timeout=120,
        )
        response.raise_for_status()

        return response.json()

    def get_execution_status(self, execution_id: str) -> dict:
        """Get status of an integration execution.

        Args:
            execution_id: ID of the execution

        Returns:
            Execution status

        """
        endpoint = (
            f"{self.base_url}/ic/api/integration/v1/monitoring/instances/{execution_id}"
        )
        response = self.session.get(endpoint, auth=self.auth, timeout=60)
        response.raise_for_status()

        return response.json()

    def wait_for_completion(
        self,
        execution_id: str,
        timeout_seconds: int = 300,
        polling_interval: int = 10,
    ) -> dict:
        """Wait for an integration execution to complete.

        Args:
            execution_id: ID of the execution
            timeout_seconds: Timeout in seconds
            polling_interval: Polling interval in seconds

        Returns:
            Final execution status

        """
        logger.info(f"Waiting for execution {execution_id} to complete")

        start_time = time.time()
        end_time = start_time + timeout_seconds

        while time.time() < end_time:
            status = self.get_execution_status(execution_id)

            if status.get("status") in {"COMPLETED", "FAILED", "CANCELLED"}:
                logger.info(
                    f"Execution {execution_id} completed with status: {status.get('status')}",
                )
                return status

            logger.debug(f"Execution {execution_id} status: {status.get('status')}")
            time.sleep(polling_interval)

        logger.warning(
            f"Execution {execution_id} timed out after {timeout_seconds} seconds",
        )
        return {"status": "TIMEOUT", "executionId": execution_id}

    def execute_dependency_group(self, group: dict) -> list[dict]:
        """Execute a group of integrations with dependencies.

        Args:
            group: Dependency group configuration

        Returns:
            list of execution results

        """
        group_name = group.get("name", "Unnamed Group")
        integrations = group.get("integrations", [])
        timeout = group.get("timeout", 600)

        logger.info(f"Executing dependency group: {group_name}")

        results = []
        for integration in integrations:
            integration_id = integration.get("id")
            payload = integration.get("payload")
            wait = integration.get("wait", True)

            try:
                # Execute integration
                execution = self.execute_integration(integration_id, payload)
                execution_id = execution.get("executionId")

                execution_result = {
                    "integration_id": integration_id,
                    "execution_id": execution_id,
                    "started_at": datetime.now().isoformat(),
                    "completed_at": None,
                    "status": "RUNNING",
                }

                # Wait for completion if required
                if wait:
                    status = self.wait_for_completion(execution_id, timeout)
                    execution_result.update(
                        {
                            "completed_at": datetime.now().isoformat(),
                            "status": status.get("status"),
                            "details": status,
                        },
                    )

                results.append(execution_result)

                # Stop group execution if integration failed
                if wait and execution_result.get("status") != "COMPLETED":
                    logger.warning(
                        f"Integration {integration_id} failed, stopping group execution",
                    )
                    break

            except Exception as e:
                logger.exception(f"Error executing integration {integration_id}: {e!s}")
                results.append(
                    {
                        "integration_id": integration_id,
                        "error": str(e),
                        "status": "ERROR",
                        "started_at": datetime.now().isoformat(),
                        "completed_at": datetime.now().isoformat(),
                    },
                )
                break

        return results

    def execute_parallel_group(self, group: dict) -> list[dict]:
        """Execute a group of integrations in parallel.

        Args:
            group: Parallel group configuration

        Returns:
            list of execution results

        """
        group_name = group.get("name", "Unnamed Group")
        integrations = group.get("integrations", [])
        timeout = group.get("timeout", 600)
        wait_all = group.get("wait_all", True)

        logger.info(f"Executing parallel group: {group_name}")

        # Start all integrations
        executions = []
        for integration in integrations:
            integration_id = integration.get("id")
            payload = integration.get("payload")

            try:
                # Execute integration
                execution = self.execute_integration(integration_id, payload)
                execution_id = execution.get("executionId")

                executions.append(
                    {
                        "integration_id": integration_id,
                        "execution_id": execution_id,
                        "started_at": datetime.now().isoformat(),
                        "completed_at": None,
                        "status": "RUNNING",
                    },
                )

            except Exception as e:
                logger.exception(f"Error executing integration {integration_id}: {e!s}")
                executions.append(
                    {
                        "integration_id": integration_id,
                        "error": str(e),
                        "status": "ERROR",
                        "started_at": datetime.now().isoformat(),
                        "completed_at": datetime.now().isoformat(),
                    },
                )

        # Wait for all integrations to complete if required
        if wait_all:
            for execution in executions:
                if execution.get("status") != "ERROR":
                    execution_id = execution.get("execution_id")
                    try:
                        status = self.wait_for_completion(execution_id, timeout)
                        execution.update(
                            {
                                "completed_at": datetime.now().isoformat(),
                                "status": status.get("status"),
                                "details": status,
                            },
                        )
                    except Exception as e:
                        logger.exception(
                            f"Error waiting for execution {execution_id}: {e!s}",
                        )
                        execution.update(
                            {
                                "completed_at": datetime.now().isoformat(),
                                "status": "ERROR",
                                "error": str(e),
                            },
                        )

        return executions

    def execute_schedule(self, schedule_config: dict | None = None) -> dict:
        """Execute integrations according to a schedule.

        Args:
            schedule_config: Schedule configuration (uses self.config if None)

        Returns:
            Execution statistics

        """
        config = schedule_config or self.config

        # Reset stats
        self.stats = {
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "total_integrations": 0,
            "successful": 0,
            "failed": 0,
            "integrations": [],
        }

        # Get groups from config
        dependency_groups = config.get("dependency_groups", [])
        parallel_groups = config.get("parallel_groups", [])

        # Execute dependency groups
        for group in dependency_groups:
            results = self.execute_dependency_group(group)
            self.stats["integrations"].extend(results)

            # Update stats
            for result in results:
                self.stats["total_integrations"] += 1
                if result.get("status") == "COMPLETED":
                    self.stats["successful"] += 1
                else:
                    self.stats["failed"] += 1

        # Execute parallel groups
        for group in parallel_groups:
            results = self.execute_parallel_group(group)
            self.stats["integrations"].extend(results)

            # Update stats
            for result in results:
                self.stats["total_integrations"] += 1
                if result.get("status") == "COMPLETED":
                    self.stats["successful"] += 1
                else:
                    self.stats["failed"] += 1

        # Update completion time
        self.stats["completed_at"] = datetime.now().isoformat()

        logger.info(
            f"Schedule execution completed: {self.stats['successful']} successful, {self.stats['failed']} failed",
        )
        return self.stats

    def save_execution_results(self, output_file: str) -> None:
        """Save execution results to a file.

        Args:
            output_file: Output file path

        """
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, indent=2)

        logger.info(f"Saved execution results to {output_file}")

    def load_execution_results(self, input_file: str) -> dict:
        """Load execution results from a file.

        Args:
            input_file: Input file path

        Returns:
            Execution statistics

        """
        with open(input_file, encoding="utf-8") as f:
            self.stats = json.load(f)

        logger.info(f"Loaded execution results from {input_file}")
        return self.stats
