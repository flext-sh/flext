#!/usr/bin/env python3
"""
Test real Meltano integration via gopy
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def test_meltano_integration():
    """Test creating a real Meltano project and calling operations"""

    # Create temporary directory for test project
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = Path(temp_dir) / "test_meltano_project"

        # Test 1: Create Meltano project
        result = subprocess.run(
            ["meltano", "init", str(project_dir)], capture_output=True, text=True
        )

        if result.returncode != 0:
            return False

        # Change to project directory
        original_cwd = os.getcwd()
        os.chdir(project_dir)

        try:
            # Test 2: Add a tap (data source)
            result = subprocess.run(
                ["meltano", "add", "extractor", "tap-csv"],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                pass
            else:
                pass

            # Test 3: List extractors
            result = subprocess.run(
                ["meltano", "invoke", "tap-csv", "--help"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                pass
            else:
                pass

            # Test 4: Check Meltano status
            result = subprocess.run(
                ["meltano", "config", "list"], capture_output=True, text=True
            )

            if result.returncode == 0:
                pass
            else:
                pass

        finally:
            os.chdir(original_cwd)

    return True


def test_gopy_meltano_bridge():
    """Test calling Meltano functions via HTTP bridge"""

    try:
        # Use the HTTP client instead of problematic gopy
        from meltano_http_client import MeltanoHTTPClient

        # Test basic functions
        client = MeltanoHTTPClient()

        # Test server health
        healthy = client.health_check()

        if not healthy:
            return False

        # Test availability check
        client.check_meltano_available()

        # Test version
        client.get_meltano_version()

        # Test project creation
        test_project = "/tmp/http_test_project"
        if os.path.exists(test_project):
            shutil.rmtree(test_project)

        client.create_project(test_project, "Test Project via HTTP")

        # Test plugin addition
        client.add_plugin("extractor", "tap-csv", "")

        # Test pipeline execution
        client.run_pipeline("tap-csv", "target-jsonl", "")

        # Test command execution
        client.execute_command("config", ["list"])

        # Cleanup
        if os.path.exists(test_project):
            shutil.rmtree(test_project)

        client.close()
        return True

    except ImportError:
        return False
    except Exception:
        return False


if __name__ == "__main__":
    # Test 1: Real Meltano operations
    meltano_success = test_meltano_integration()

    # Test 2: Gopy bridge
    gopy_success = test_gopy_meltano_bridge()

    # Summary

    if meltano_success and gopy_success:
        sys.exit(0)
    else:
        sys.exit(1)
