"""Orchestrator for LDAP ETL pipeline.

This module coordinates the execution of tap-ldap, dbt-ldap, and target-ldap.
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
from typing import TYPE_CHECKING

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

if TYPE_CHECKING:
    from pathlib import Path

    from flx_ldap.config import FlxLDAPConfig

logger = logging.getLogger(__name__)
console = Console()


class LDAPOrchestrator:
    """Orchestrates LDAP ETL pipeline operations."""

    def __init__(self, config: FlxLDAPConfig) -> None:
        """Initialize orchestrator.

        Args:
            config: Configuration for all components

        """
        self.config = config
        self.console = console
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Set up logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(self.config.output_path / "flx-ldap.log"),
            ],
        )

    def run_tap(
        self,
        catalog_path: Path | None = None,
        state_path: Path | None = None,
        output_path: Path | None = None,
    ) -> tuple[bool, Path | None]:
        """Run tap-ldap to extract data.

        Args:
            catalog_path: Path to catalog file
            state_path: Path to state file
            output_path: Path to output file

        Returns:
            Tuple of (success, output_path)

        """
        if not self.config.tap:
            logger.error("No tap configuration provided")
            return False, None

        output_path = output_path or self.config.output_path / "tap-output.jsonl"
        catalog_path = catalog_path or self.config.catalog_path

        # Build tap command
        cmd = ["tap-ldap", "--config", "-"]

        if catalog_path and catalog_path.exists():
            cmd.extend(["--catalog", str(catalog_path)])
        else:
            cmd.append("--discover")

        if state_path and state_path.exists():
            cmd.extend(["--state", str(state_path)])

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task("Running tap-ldap...", total=None)

                # Run tap with config from stdin
                with output_path.open("w", encoding="utf-8") as output_file:
                    process = subprocess.Popen(
                        cmd,
                        stdin=subprocess.PIPE,
                        stdout=output_file,
                        stderr=subprocess.PIPE,
                        text=True,
                    )

                    # Send config to stdin
                    _stdout, stderr = process.communicate(
                        input=json.dumps(self.config.to_tap_config())
                    )

                    if process.returncode != 0:
                        logger.error("tap-ldap failed: %s", stderr)
                        return False, None

                progress.update(task, completed=True)

            self.console.print(f"[green]✓[/green] Data extracted to {output_path}")
            return True, output_path

        except Exception as e:
            logger.exception("Failed to run tap-ldap: %s", e)
            return False, None

    def run_dbt(
        self,
        command: str = "run",
        models: list[str] | None = None,
        *,
        full_refresh: bool = False,
    ) -> bool:
        """Run dbt-ldap transformations.

        Args:
            command: dbt command (run, test, snapshot, etc.)
            models: Specific models to run
            full_refresh: Whether to do full refresh

        Returns:
            True if successful

        """
        if not self.config.dbt:
            logger.error("No dbt configuration provided")
            return False

        # Build dbt command
        cmd = ["dbt", command]
        cmd.extend(self.config.to_dbt_args())

        if models or self.config.dbt.models:
            models_list = models or self.config.dbt.models or []
            cmd.extend(["--select", " ".join(models_list)])

        if full_refresh:
            cmd.append("--full-refresh")

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task(f"Running dbt {command}...", total=None)

                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                )

                progress.update(task, completed=True)

            self.console.print(f"[green]✓[/green] dbt {command} completed successfully")

            # Parse dbt output for summary
            if "Completed successfully" in process.stdout:
                self.console.print(process.stdout.split("Completed successfully")[0])

            return True

        except subprocess.CalledProcessError as e:
            logger.error("dbt %s failed: %s", command, e.stderr)
            self.console.print(f"[red]✗[/red] dbt {command} failed")
            return False

    def run_target(
        self,
        input_path: Path | None = None,
        *,
        dry_run: bool = False,
    ) -> bool:
        """Run target-ldap to load data.

        Args:
            input_path: Path to input file
            dry_run: Whether to do a dry run

        Returns:
            True if successful

        """
        if not self.config.target:
            logger.error("No target configuration provided")
            return False

        input_path = input_path or self.config.output_path / "tap-output.jsonl"

        if not input_path.exists():
            logger.error("Input file not found: %s", input_path)
            return False

        # Build target command
        cmd = ["target-ldap", "--config", "-"]

        # Add dry run config if needed
        target_config = self.config.to_target_config()
        if dry_run:
            target_config["validate_records"] = True
            # Could add a dry_run flag to target-ldap

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task("Running target-ldap...", total=None)

                # Run target with config from stdin and data from file
                with input_path.open(encoding="utf-8") as input_file:
                    process = subprocess.Popen(
                        cmd,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )

                    # Send config and data
                    _stdout, stderr = process.communicate(
                        input=json.dumps(target_config) + "\n" + input_file.read()
                    )

                    if process.returncode != 0:
                        logger.error("target-ldap failed: %s", stderr)
                        return False

                progress.update(task, completed=True)

            self.console.print("[green]✓[/green] Data loaded successfully")
            return True

        except Exception as e:
            logger.exception("Failed to run target-ldap: %s", e)
            return False

    def run_sync(
        self,
        catalog_path: Path | None = None,
        state_path: Path | None = None,
        *,
        transform: bool = True,
        dry_run: bool = False,
    ) -> bool:
        """Run complete sync pipeline.

        Args:
            catalog_path: Path to catalog file
            state_path: Path to state file
            transform: Whether to run dbt transformations
            dry_run: Whether to do a dry run

        Returns:
            True if all steps successful

        """
        self.console.print("[bold]Starting LDAP sync pipeline...[/bold]")

        # Step 1: Extract
        self.console.print("\n[bold]Step 1: Extract data from source LDAP[/bold]")
        success, output_path = self.run_tap(catalog_path, state_path)
        if not success:
            self.console.print("[red]✗[/red] Extraction failed")
            return False

        # Step 2: Transform (optional)
        if transform and self.config.dbt:
            self.console.print("\n[bold]Step 2: Transform data with dbt[/bold]")
            if not self.run_dbt("run"):
                self.console.print("[red]✗[/red] Transformation failed")
                return False

        # Step 3: Load
        self.console.print("\n[bold]Step 3: Load data to target LDAP[/bold]")
        if not self.run_target(output_path, dry_run=dry_run):
            self.console.print("[red]✗[/red] Loading failed")
            return False

        self.console.print(
            "\n[bold green]✓ Sync pipeline completed successfully![/bold green]"
        )
        return True

    def run_migration(
        self,
        source_catalog: Path | None = None,
        target_catalog: Path | None = None,
        *,
        compare_first: bool = True,
    ) -> bool:
        """Run LDAP migration workflow.

        Args:
            source_catalog: Source catalog path
            target_catalog: Target catalog path
            compare_first: Whether to compare before migration

        Returns:
            True if successful

        """
        if not self.config.migration:
            logger.error("No migration configuration provided")
            return False

        self.console.print("[bold]Starting LDAP migration...[/bold]")

        # Step 1: Extract from source
        self.console.print("\n[bold]Step 1: Extract from source LDAP[/bold]")
        source_output = self.config.output_path / "source-data.jsonl"

        # Use source tap config
        original_tap = self.config.tap
        self.config.tap = self.config.migration.source_tap_config

        success, _ = self.run_tap(source_catalog, output_path=source_output)
        if not success:
            self.config.tap = original_tap
            return False

        # Step 2: Compare if enabled
        if compare_first and self.config.migration.target_tap_config:
            self.console.print(
                "\n[bold]Step 2: Extract from target for comparison[/bold]"
            )
            target_output = self.config.output_path / "target-data.jsonl"

            self.config.tap = self.config.migration.target_tap_config
            success, _ = self.run_tap(target_catalog, output_path=target_output)

            if success:
                self._compare_extracts(source_output, target_output)

        # Step 3: Transform if configured
        if self.config.dbt:
            self.console.print("\n[bold]Step 3: Transform data[/bold]")
            if not self.run_dbt("run"):
                self.config.tap = original_tap
                return False

        # Step 4: Load to target
        self.console.print("\n[bold]Step 4: Load to target LDAP[/bold]")
        self.config.target = self.config.migration.target_config

        if not self.run_target(source_output, dry_run=self.config.migration.dry_run):
            self.config.tap = original_tap
            return False

        self.config.tap = original_tap
        self.console.print(
            "\n[bold green]✓ Migration completed successfully![/bold green]"
        )
        return True

    def _compare_extracts(self, source_path: Path, target_path: Path) -> None:
        """Compare source and target extracts.

        Args:
            source_path: Path to source data
            target_path: Path to target data

        """
        try:
            # Count records by stream
            source_counts: dict[str, int] = {}
            target_counts: dict[str, int] = {}

            with source_path.open(encoding="utf-8") as f:
                for line in f:
                    record = json.loads(line)
                    if record.get("type") == "RECORD":
                        stream = record.get("stream", "unknown")
                        source_counts[stream] = source_counts.get(stream, 0) + 1

            with target_path.open(encoding="utf-8") as f:
                for line in f:
                    record = json.loads(line)
                    if record.get("type") == "RECORD":
                        stream = record.get("stream", "unknown")
                        target_counts[stream] = target_counts.get(stream, 0) + 1

            # Display comparison
            self.console.print("\n[bold]Source vs Target Comparison:[/bold]")
            all_streams = set(source_counts.keys()) | set(target_counts.keys())

            for stream in sorted(all_streams):
                source = source_counts.get(stream, 0)
                target = target_counts.get(stream, 0)
                diff = source - target

                if diff == 0:
                    status = "[green]✓[/green]"
                elif diff > 0:
                    status = f"[yellow]+{diff}[/yellow]"
                else:
                    status = f"[red]{diff}[/red]"

                self.console.print(f"  {stream}: {source} → {target} {status}")

        except Exception as e:
            logger.warning("Failed to compare extracts: %s", e)

    def validate_config(self) -> bool:
        """Validate configuration.

        Returns:
            True if configuration is valid

        """
        issues = []

        # Check tap config
        if self.config.tap:
            if not self.config.tap.host:
                issues.append("Tap: Missing host")
            if not self.config.tap.base_dn:
                issues.append("Tap: Missing base_dn")

        # Check target config
        if self.config.target:
            if not self.config.target.host:
                issues.append("Target: Missing host")
            if not self.config.target.base_dn:
                issues.append("Target: Missing base_dn")

        # Check dbt config
        if self.config.dbt and not self.config.dbt.project_dir.exists():
            issues.append(
                f"DBT: Project directory not found: {self.config.dbt.project_dir}"
            )

        if issues:
            self.console.print("[bold red]Configuration issues found:[/bold red]")
            for issue in issues:
                self.console.print(f"  • {issue}")
            return False

        self.console.print("[green]✓[/green] Configuration is valid")
        return True
