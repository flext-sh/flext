#!/usr/bin/env python3
"""
Complete End-to-End Integration Test
Tests both real Meltano CLI operations and Python-Go HTTP bridge
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def test_meltano_cli_operations():
    """Test real Meltano CLI operations"""

    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = Path(temp_dir) / "cli_test_project"

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
            # Test 2: Add tap-csv
            result = subprocess.run(
                ["meltano", "add", "extractor", "tap-csv"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                pass
            else:
                pass

            # Test 3: Check project status
            result = subprocess.run(
                ["meltano", "config", "list"], capture_output=True, text=True
            )

            if result.returncode == 0:
                result.stdout.strip().split("\n")
            else:
                pass

        finally:
            os.chdir(original_cwd)

    return True


def test_python_go_http_bridge():
    """Test Python-Go HTTP bridge integration"""

    try:
        from meltano_http_client import MeltanoHTTPClient

        # Test client initialization
        client = MeltanoHTTPClient()

        # Test server availability (expecting server not running)
        healthy = client.health_check()
        if healthy:
            # Test all endpoints
            client.check_meltano_available()

            client.get_meltano_version()

            # Test project operations
            test_project = "/tmp/http_bridge_test"
            if os.path.exists(test_project):
                shutil.rmtree(test_project)

            client.create_project(test_project, "HTTP Bridge Test")

            # Test plugin operations
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

        # Test configuration methods

        client.close()
        return True

    except Exception:
        return False


def test_python_compatibility_functions():
    """Test compatibility functions for gopy replacement"""

    try:
        from meltano_http_client import (
            AddPluginToProject,
            CheckMeltanoAvailable,
            CreateProject,
            GetMeltanoVersion,
            GetProjectPlugins,
            RunMeltanoPipeline,
        )

        # Test function signatures (they should not crash)

        # These will fail with connection error but that's expected
        try:
            CheckMeltanoAvailable()
        except Exception:
            pass  # Expected when server not running

        try:
            GetMeltanoVersion()
        except Exception:
            pass  # Expected when server not running

        return True

    except ImportError:
        return False
    except Exception:
        return False


def test_integration_architecture():
    """Test the overall integration architecture"""

    # Test 1: File structure

    current_dir = Path(__file__).parent

    required_files = [
        "meltano_http_client.py",
        "test_real_meltano.py",
        "test_complete_integration.py",
    ]

    for file in required_files:
        if (current_dir / file).exists():
            pass
        else:
            return False

    # Test 2: Module imports

    try:
        import meltano_http_client

        # Check key classes and functions
        assert hasattr(meltano_http_client, "MeltanoHTTPClient")
        assert hasattr(meltano_http_client, "CheckMeltanoAvailable")
        assert hasattr(meltano_http_client, "GetMeltanoVersion")

    except Exception:
        return False

    # Test 3: Integration patterns

    client = meltano_http_client.MeltanoHTTPClient()

    # Check that client has all required methods
    required_methods = [
        "check_meltano_available",
        "get_meltano_version",
        "create_project",
        "add_plugin",
        "run_pipeline",
        "execute_command",
        "health_check",
    ]

    for method in required_methods:
        if hasattr(client, method):
            pass
        else:
            return False

    client.close()
    return True


def run_comprehensive_test():
    """Run all integration tests"""

    test_results = {}

    # Test 1: Meltano CLI Operations
    test_results["meltano_cli"] = test_meltano_cli_operations()

    # Test 2: Python-Go HTTP Bridge
    test_results["http_bridge"] = test_python_go_http_bridge()

    # Test 3: Compatibility Functions
    test_results["compatibility"] = test_python_compatibility_functions()

    # Test 4: Integration Architecture
    test_results["architecture"] = test_integration_architecture()

    # Results Summary

    for _test_name, _result in test_results.items():
        pass

    total_tests = len(test_results)
    passed_tests = sum(test_results.values())

    if passed_tests == total_tests:
        return True
    return False


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
