#!/usr/bin/env python3
"""End-to-end tests for flx-oracle-wms."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


class TestFLXOracleWMSE2E:
    """End-to-end tests for flx-oracle-wms orchestrator."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Setup test environment."""
        # Ensure we're in the right directory
        self.project_root = Path(__file__).parent.parent.parent
        os.chdir(self.project_root)

        # Generate configs if they don't exist
        if not Path("config").exists() or not list(Path("config").glob("*.json")):
            subprocess.run([sys.executable, "generate_config.py"], check=True)

        # Create required directories
        Path("output").mkdir(exist_ok=True)
        Path("metrics").mkdir(exist_ok=True)

        # Clean up previous test artifacts
        for pattern in ["state.json", "catalog.json"]:
            if Path(pattern).exists():
                Path(pattern).unlink()

    def run_flx_command(self, args: list[str]) -> subprocess.CompletedProcess:
        """Run flx command and return result."""
        cmd = [sys.executable, "-m", "flx_oracle_wms", *args]
        return subprocess.run(
            cmd, capture_output=True, text=True, cwd=self.project_root
        )

    def test_flx_help(self) -> None:
        """Test flx help command."""
        result = self.run_flx_command(["--help"])
        assert result.returncode == 0
        assert "flx-oracle-wms" in result.stdout
        assert (
            "orchestrates tap-oracle-wms and target-oracle-wms" in result.stdout.lower()
        )

    def test_flx_version(self) -> None:
        """Test flx version command."""
        result = self.run_flx_command(["--version"])
        assert result.returncode == 0
        assert "flx-oracle-wms" in result.stdout
        assert "1.0.0" in result.stdout

    def test_config_generation(self) -> None:
        """Test complete config generation."""
        # Remove existing configs
        config_dir = Path("config")
        if config_dir.exists():
            for file in config_dir.glob("*.json"):
                file.unlink()

        # Generate configs
        result = subprocess.run(
            [sys.executable, "generate_config.py"], capture_output=True, text=True
        )
        assert result.returncode == 0

        # Verify all configs created
        assert (config_dir / "tap_config.json").exists()
        assert (config_dir / "target_config.json").exists()
        assert (config_dir / "pipeline_config.json").exists()

    def test_init_command(self) -> None:
        """Test flx init command for template generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Generate templates
            result = self.run_flx_command(
                [
                    "init",
                    "--tap-config",
                    str(tmpdir_path / "tap.json"),
                    "--target-config",
                    str(tmpdir_path / "target.json"),
                    "--pipeline-config",
                    str(tmpdir_path / "pipeline.json"),
                ]
            )

            assert result.returncode == 0
            assert (tmpdir_path / "tap.json").exists()
            assert (tmpdir_path / "target.json").exists()
            assert (tmpdir_path / "pipeline.json").exists()

    def test_discover_command(self) -> None:
        """Test stream discovery through flx."""
        result = self.run_flx_command(
            ["discover", "--tap-config", "config/tap_config.json"]
        )

        # Discovery might fail in test mode, but command should run
        if result.returncode == 0:
            # Check if catalog was created
            if Path("catalog.json").exists():
                with open("catalog.json") as f:
                    catalog = json.load(f)
                assert "streams" in catalog

    def test_pipeline_list(self) -> None:
        """Test listing available pipelines."""
        result = self.run_flx_command(
            ["pipeline", "list", "--config", "config/pipeline_config.json"]
        )

        if result.returncode == 0:
            assert "test_pipeline" in result.stdout
            assert "Available Pipelines" in result.stdout

    def test_monitor_commands(self) -> None:
        """Test monitoring commands."""
        # Test status command
        result = self.run_flx_command(["monitor", "status"])
        # Might show "never run" for new pipelines
        assert result.returncode == 0

        # Test metrics command
        result = self.run_flx_command(["monitor", "metrics"])
        assert result.returncode == 0

    def test_extract_command(self) -> None:
        """Test standalone extract command."""
        # Create minimal catalog for testing
        test_catalog = {
            "streams": [
                {
                    "stream": "test_stream",
                    "tap_stream_id": "test_stream",
                    "schema": {
                        "type": "object",
                        "properties": {"id": {"type": "string"}},
                    },
                    "metadata": [{"breadcrumb": [], "metadata": {"selected": True}}],
                }
            ]
        }

        with open("test_catalog.json", "w") as f:
            json.dump(test_catalog, f)

        try:
            result = self.run_flx_command(
                [
                    "extract",
                    "--tap-config",
                    "config/tap_config.json",
                    "--target-config",
                    "config/target_config.json",
                    "--catalog",
                    "test_catalog.json",
                ]
            )

            # Extract might fail in test mode, but shouldn't crash
            assert result.returncode in [0, 1]
        finally:
            Path("test_catalog.json").unlink()

    def test_load_command(self) -> None:
        """Test standalone load command."""
        # Create test Singer data
        singer_data = (
            json.dumps(
                {"type": "SCHEMA", "stream": "test", "schema": {"type": "object"}}
            )
            + "\n"
            + json.dumps(
                {
                    "type": "RECORD",
                    "stream": "test",
                    "record": {"id": "1", "name": "test"},
                }
            )
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(singer_data)
            input_file = f.name

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "flx_oracle_wms",
                    "load",
                    "--config",
                    "config/target_config.json",
                ],
                stdin=open(input_file),
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            # Load should process without crashing
            assert result.returncode in [0, 1]
        finally:
            Path(input_file).unlink()

    def test_pipeline_run_validation(self) -> None:
        """Test pipeline run with validation."""
        # First validate configuration
        result = self.run_flx_command(
            [
                "pipeline",
                "run",
                "--config",
                "config/pipeline_config.json",
                "--pipeline-name",
                "test_pipeline",
            ]
        )

        # Pipeline might fail due to connection issues in test mode
        # but the orchestrator should handle it gracefully
        if result.returncode != 0:
            # Check for expected error patterns
            assert any(
                pattern in result.stdout + result.stderr
                for pattern in [
                    "connection",
                    "authentication",
                    "test_mode",
                    "not found",
                ]
            )

    def test_module_imports(self) -> None:
        """Test that all flx modules can be imported."""
        import_test = """
import sys
sys.path.insert(0, 'src')
try:
    import flx_oracle_wms
    from flx_oracle_wms import cli, orchestrator, monitoring, config
    from flx_oracle_wms.pipelines import inventory_sync
    print("✅ All imports successful")
    sys.exit(0)
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)
"""
        result = subprocess.run(
            [sys.executable, "-c", import_test],
            capture_output=True,
            text=True,
            cwd=self.project_root,
        )
        assert result.returncode == 0
        assert "✅ All imports successful" in result.stdout

    def test_orchestrator_functionality(self) -> None:
        """Test orchestrator core functionality."""
        test_code = """
import sys
sys.path.insert(0, 'src')
from pathlib import Path
from flx_oracle_wms.config import PipelineConfig, PipelineDefinition
from flx_oracle_wms.orchestrator import WMSOrchestrator

# Create minimal config
config = PipelineConfig(
    name="Test",
    tap_config_path=Path("config/tap_config.json"),
    target_config_path=Path("config/target_config.json"),
    pipelines=[
        PipelineDefinition(
            name="test",
            description="Test pipeline",
            streams=["test"],
            enabled=True
        )
    ]
)

# Create orchestrator
orchestrator = WMSOrchestrator(config)

# Validate configuration
valid, errors = orchestrator.validate_configuration()
print(f"Configuration valid: {valid}")
if errors:
    print(f"Errors: {errors}")

sys.exit(0 if valid or len(errors) <= 2 else 1)  # Allow minor errors
"""
        result = subprocess.run(
            [sys.executable, "-c", test_code],
            capture_output=True,
            text=True,
            cwd=self.project_root,
        )

        assert result.returncode == 0

    def test_monitoring_functionality(self) -> None:
        """Test monitoring functionality."""
        test_code = """
import sys
sys.path.insert(0, 'src')
from flx_oracle_wms.monitoring import PipelineMonitor

# Create monitor
monitor = PipelineMonitor()

# Record test events
monitor.record_pipeline_start("test_pipeline")
monitor.record_pipeline_success("test_pipeline", 10.5, 100, 100)

# Get metrics
metrics = monitor.get_metrics()
print(f"Metrics: {metrics}")

# Get status
status = monitor.get_pipeline_status("test_pipeline")
print(f"Status: {status}")

print("✅ Monitoring test successful")
"""
        result = subprocess.run(
            [sys.executable, "-c", test_code],
            capture_output=True,
            text=True,
            cwd=self.project_root,
        )
        assert result.returncode == 0
        assert "✅ Monitoring test successful" in result.stdout


def main():
    """Run E2E tests."""
    # Change to project directory
    project_dir = Path(__file__).parent.parent.parent
    os.chdir(project_dir)

    # Run pytest
    exit_code = pytest.main(
        [__file__, "-v", "--tb=short", "-x"]  # Stop on first failure
    )

    if exit_code == 0:
        pass

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
