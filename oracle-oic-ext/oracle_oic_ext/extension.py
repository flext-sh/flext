"""Oracle Integration Cloud extension implementation."""

from __future__ import annotations

import subprocess
import sys

import structlog
from meltano.edk import models
from meltano.edk.extension import ExtensionBase

from oracle_oic_ext.lifecycle import LifecycleManager
from oracle_oic_ext.monitoring import MonitoringService

log = structlog.get_logger()


class OracleOICExtension(ExtensionBase):
    """Extension for Oracle Integration Cloud operations."""

    def __init__(self) -> None:
        """Initialize the Oracle OIC extension."""
        self.oracle_oic_bin = "oracle-oic-ext"
        self.lifecycle_manager = None
        self.monitoring_service = None

    def invoke(self, command_name: str | None, *command_args) -> None:
        """Invoke the extension command."""
        if not command_name:
            # Show help if no command provided
            self._show_help()
            return

        # Initialize services with config
        self._initialize_services()

        # Route to appropriate handler
        if command_name.startswith("lifecycle:"):
            self._handle_lifecycle_command(command_name, *command_args)
        elif command_name.startswith("monitor:"):
            self._handle_monitoring_command(command_name, *command_args)
        elif command_name.startswith("extract:"):
            self._handle_extraction_command(command_name, *command_args)
        elif command_name.startswith("transform:"):
            self._handle_transformation_command(command_name, *command_args)
        else:
            log.error(f"Unknown command: {command_name}")
            sys.exit(1)

    def describe(self) -> models.Describe:
        """Describe the extension's capabilities."""
        return models.Describe(
            commands=[
                # Lifecycle Management Commands
                models.ExtensionCommand(
                    name="lifecycle:activate",
                    description="Activate an integration",
                    args="INTEGRATION_ID [VERSION]",
                ),
                models.ExtensionCommand(
                    name="lifecycle:deactivate",
                    description="Deactivate an integration",
                    args="INTEGRATION_ID [VERSION]",
                ),
                models.ExtensionCommand(
                    name="lifecycle:bulk-activate",
                    description="Activate multiple integrations",
                    args="--file INTEGRATION_LIST_FILE",
                ),
                models.ExtensionCommand(
                    name="lifecycle:bulk-deactivate",
                    description="Deactivate multiple integrations",
                    args="--file INTEGRATION_LIST_FILE",
                ),
                models.ExtensionCommand(
                    name="lifecycle:status",
                    description="Check integration status",
                    args="INTEGRATION_ID [VERSION]",
                ),
                # Monitoring Commands
                models.ExtensionCommand(
                    name="monitor:health",
                    description="Check OIC instance health",
                    args="[--detailed]",
                ),
                models.ExtensionCommand(
                    name="monitor:performance",
                    description="Get performance metrics",
                    args="[--window HOURS]",
                ),
                models.ExtensionCommand(
                    name="monitor:errors",
                    description="Analyze error patterns",
                    args="[--window HOURS] [--integration INTEGRATION_ID]",
                ),
                models.ExtensionCommand(
                    name="monitor:usage",
                    description="Get usage analytics",
                    args="[--window DAYS]",
                ),
                # Advanced Extraction Commands
                models.ExtensionCommand(
                    name="extract:artifacts",
                    description="Extract integration artifacts (.iar files)",
                    args="--output-dir DIRECTORY [--integration INTEGRATION_ID]",
                ),
                models.ExtensionCommand(
                    name="extract:logs",
                    description="Extract execution logs",
                    args="--output-dir DIRECTORY [--window HOURS]",
                ),
                models.ExtensionCommand(
                    name="extract:metadata",
                    description="Extract comprehensive metadata",
                    args="--output-dir DIRECTORY",
                ),
                # Transformation Commands
                models.ExtensionCommand(
                    name="transform:flatten",
                    description="Flatten nested data structures",
                    args="--input-file FILE --output-file FILE",
                ),
                models.ExtensionCommand(
                    name="transform:mask",
                    description="Mask sensitive data",
                    args="--input-file FILE --output-file FILE --fields FIELD_LIST",
                ),
            ]
        )

    def _initialize_services(self) -> None:
        """Initialize services with configuration."""
        config = self.config

        # Initialize lifecycle manager
        self.lifecycle_manager = LifecycleManager(
            base_url=config.get("base_url"),
            auth_config={
                "oauth_client_id": config.get("oauth_client_id"),
                "oauth_client_secret": config.get("oauth_client_secret"),
                "oauth_token_url": config.get("oauth_token_url"),
            },
        )

        # Initialize monitoring service
        self.monitoring_service = MonitoringService(
            base_url=config.get("base_url"),
            auth_config={
                "oauth_client_id": config.get("oauth_client_id"),
                "oauth_client_secret": config.get("oauth_client_secret"),
                "oauth_token_url": config.get("oauth_token_url"),
            },
        )

    def _handle_lifecycle_command(self, command: str, *args) -> None:
        """Handle lifecycle management commands."""
        cmd = command.split(":", 1)[1]

        if cmd == "activate":
            if len(args) < 1:
                log.error("Integration ID required")
                sys.exit(1)
            integration_id = args[0]
            version = args[1] if len(args) > 1 else "01.00.0000"
            self.lifecycle_manager.activate_integration(integration_id, version)

        elif cmd == "deactivate":
            if len(args) < 1:
                log.error("Integration ID required")
                sys.exit(1)
            integration_id = args[0]
            version = args[1] if len(args) > 1 else "01.00.0000"
            self.lifecycle_manager.deactivate_integration(integration_id, version)

        elif cmd == "status":
            if len(args) < 1:
                log.error("Integration ID required")
                sys.exit(1)
            integration_id = args[0]
            version = args[1] if len(args) > 1 else "01.00.0000"
            status = self.lifecycle_manager.get_integration_status(
                integration_id, version
            )
            log.info(f"Integration {integration_id}|{version} status: {status}")

        else:
            log.error(f"Unknown lifecycle command: {cmd}")
            sys.exit(1)

    def _handle_monitoring_command(self, command: str, *args) -> None:
        """Handle monitoring commands."""
        cmd = command.split(":", 1)[1]

        if cmd == "health":
            detailed = "--detailed" in args
            health = self.monitoring_service.check_health(detailed=detailed)
            log.info("OIC Health Status", **health)

        elif cmd == "performance":
            window_hours = 24
            for i, arg in enumerate(args):
                if arg == "--window" and i + 1 < len(args):
                    window_hours = int(args[i + 1])
            metrics = self.monitoring_service.get_performance_metrics(window_hours)
            log.info("Performance Metrics", **metrics)

        elif cmd == "errors":
            window_hours = 24
            integration_id = None
            for i, arg in enumerate(args):
                if arg == "--window" and i + 1 < len(args):
                    window_hours = int(args[i + 1])
                elif arg == "--integration" and i + 1 < len(args):
                    integration_id = args[i + 1]
            errors = self.monitoring_service.analyze_errors(
                window_hours, integration_id
            )
            log.info("Error Analysis", **errors)

        else:
            log.error(f"Unknown monitoring command: {cmd}")
            sys.exit(1)

    def _handle_extraction_command(self, command: str, *args) -> None:
        """Handle advanced extraction commands."""
        cmd = command.split(":", 1)[1]

        if cmd == "artifacts":
            # Parse arguments
            output_dir = None
            integration_id = None
            for i, arg in enumerate(args):
                if arg == "--output-dir" and i + 1 < len(args):
                    output_dir = args[i + 1]
                elif arg == "--integration" and i + 1 < len(args):
                    integration_id = args[i + 1]

            if not output_dir:
                log.error("--output-dir required")
                sys.exit(1)

            # Use tap-oracle-oic with specific configuration
            tap_config = {
                **self.config,
                "extract_artifacts": True,
                "artifact_directory": output_dir,
            }
            if integration_id:
                tap_config["integration_filter"] = integration_id

            # Run tap-oracle-oic in artifact extraction mode
            self._run_tap_extraction(tap_config)

        else:
            log.error(f"Unknown extraction command: {cmd}")
            sys.exit(1)

    def _handle_transformation_command(self, command: str, *args) -> None:
        """Handle data transformation commands."""
        cmd = command.split(":", 1)[1]

        log.info(f"Transformation command '{cmd}' not yet implemented")
        sys.exit(1)

    def _run_tap_extraction(self, config: dict) -> None:
        """Run tap-oracle-oic for extraction."""
        try:
            # Run tap-oracle-oic with specific config
            cmd = ["tap-oracle-oic", "--config", "-"]
            proc = subprocess.run(
                cmd,
                input=str(config).encode(),
                capture_output=True,
                text=True,
            )
            if proc.returncode != 0:
                log.error("Extraction failed", stderr=proc.stderr)
                sys.exit(1)
            log.info("Extraction completed successfully")
        except Exception as e:
            log.error("Failed to run extraction", error=str(e))
            sys.exit(1)

    def _show_help(self) -> None:
        """Show extension help."""
        log.info("Oracle OIC Extension Commands:")
        for cmd in self.describe().commands:
            log.info(f"  {cmd.name}: {cmd.description}")
            if cmd.args:
                log.info(f"    Args: {cmd.args}")
