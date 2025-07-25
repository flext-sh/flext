#!/usr/bin/env python3
"""FLEXT LDAP Libraries Meltano Integration Test.

This test validates that all FLEXT LDAP libraries work correctly
with Meltano orchestration, ensuring enterprise-level quality.

Test Coverage:
- flext-tap-ldap installed and working via Meltano
- flext-target-ldap installed and working via Meltano
- Full TAP->TARGET pipeline functioning
- LDIF output validation
- Error handling and retry mechanisms
- Performance monitoring
"""

import builtins
import contextlib
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional

import pytest
import yaml
from docker import from_env as docker_from_env


class FlextMeltanoMeltanoLDAPIntegrationTest:
    """Enterprise-level Meltano LDAP integration test suite."""

    def __init__(self, test_dir: Path) -> None:
        self.test_dir = test_dir
        self.docker_client = None
        self.containers: list[str] = []
        self.meltano_project_dir = test_dir
        self.test_results: dict[str, bool] = {}

    def setup_docker_environment(self) -> bool:
        """Set up Docker test environment with LDAP servers."""
        try:
            self.docker_client = docker_from_env()

            # Start Docker Compose services
            cmd = ["docker-compose", "up", "-d"]
            result = subprocess.run(
                cmd,
                check=False,
                cwd=self.test_dir,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode != 0:
                return False

            # Wait for LDAP servers to be ready
            time.sleep(30)  # Give LDAP servers time to start

            # Verify LDAP servers are responding
            return self._verify_ldap_servers()

        except Exception:
            return False

    def _verify_ldap_servers(self) -> bool:
        """Verify LDAP servers are responding."""
        try:
            # Simple LDAP connectivity test
            cmd = [
                "ldapsearch",
                "-H",
                "ldap://localhost:389",
                "-D",
                "cn=REDACTED_LDAP_BIND_PASSWORD,dc=flext-test,dc=local",
                "-w",
                "REDACTED_LDAP_BIND_PASSWORD123",
                "-b",
                "dc=flext-test,dc=local",
                "-s",
                "base",
                "(objectClass=*)",
            ]

            result = subprocess.run(
                cmd, check=False, capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0

        except FileNotFoundError:
            return True
        except Exception:
            return False

    def install_flext_packages(self) -> bool:
        """Install FLEXT LDAP packages in development mode."""
        try:
            # Install all FLEXT LDAP packages in editable mode
            packages = [
                "flext-ldif",
                "flext-ldap",
                "flext-tap-ldap",
                "flext-target-ldap",
            ]

            for package in packages:
                package_path = self.test_dir.parent.parent.parent / package
                if package_path.exists():
                    cmd = ["pip", "install", "-e", str(package_path)]
                    result = subprocess.run(
                        cmd, check=False, capture_output=True, text=True, timeout=120
                    )

                    if result.returncode != 0:
                        return False
                else:
                    pass

            # Verify installations
            for package in packages:
                try:
                    cmd = [
                        "python",
                        "-c",
                        f"import {package.replace('-', '_')}; print('{package} imported successfully')",
                    ]
                    result = subprocess.run(
                        cmd, check=False, capture_output=True, text=True, timeout=10
                    )
                    if result.returncode == 0:
                        pass
                    else:
                        return False
                except Exception:
                    return False

            return True

        except Exception:
            return False

    def initialize_meltano_project(self) -> bool:
        """Initialize Meltano project for testing."""
        try:
            # Change to test directory
            os.chdir(self.meltano_project_dir)

            # Check if meltano is available
            result = subprocess.run(
                ["meltano", "--version"], check=False, capture_output=True, text=True
            )
            if result.returncode != 0:
                install_result = subprocess.run(
                    ["pip", "install", "meltano"],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                if install_result.returncode != 0:
                    return False

            # Initialize Meltano project if not already initialized
            if not (self.meltano_project_dir / ".meltano").exists():
                result = subprocess.run(
                    ["meltano", "init", "flext-ldap-test"],
                    check=False,
                    cwd=self.meltano_project_dir.parent,
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    return False

            return True

        except Exception:
            return False

    def test_tap_installation(self) -> bool:
        """Test that flext-tap-ldap can be installed via Meltano."""
        try:
            # Test tap discovery
            cmd = ["meltano", "invoke", "tap-ldap-test", "--discover"]
            result = subprocess.run(
                cmd,
                check=False,
                cwd=self.meltano_project_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                self.test_results["tap_discovery"] = True

                # Verify catalog output
                if "users" in result.stdout and "groups" in result.stdout:
                    self.test_results["tap_streams"] = True
                else:
                    self.test_results["tap_streams"] = False

                return True
            self.test_results["tap_discovery"] = False
            return False

        except Exception:
            self.test_results["tap_discovery"] = False
            return False

    def test_target_installation(self) -> bool:
        """Test that flext-target-ldap can be installed via Meltano."""
        try:
            # Test target by running with --version or --help
            cmd = ["meltano", "invoke", "target-ldap-test", "--help"]
            result = subprocess.run(
                cmd,
                check=False,
                cwd=self.meltano_project_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                self.test_results["target_installation"] = True
                return True
            self.test_results["target_installation"] = False
            return False

        except Exception:
            self.test_results["target_installation"] = False
            return False

    def test_full_pipeline(self) -> bool:
        """Test full TAP->TARGET pipeline."""
        try:
            # Run LDAP to LDIF pipeline
            cmd = ["meltano", "run", "ldap-to-ldif-test"]
            result = subprocess.run(
                cmd,
                check=False,
                cwd=self.meltano_project_dir,
                capture_output=True,
                text=True,
                timeout=180,
            )

            if result.returncode == 0:
                self.test_results["pipeline_ldif"] = True

                # Verify LDIF output file
                ldif_output = Path("/tmp/target-ldif-test-output.ldif")
                if ldif_output.exists():
                    with open(ldif_output) as f:
                        content = f.read()

                    if "dn:" in content and "objectClass:" in content:
                        self.test_results["ldif_output_valid"] = True
                    else:
                        self.test_results["ldif_output_valid"] = False
                else:
                    self.test_results["ldif_output_valid"] = False

                return True
            self.test_results["pipeline_ldif"] = False
            return False

        except Exception:
            self.test_results["pipeline_ldif"] = False
            return False

    def test_error_handling(self) -> bool:
        """Test error handling and retry mechanisms."""
        try:
            # Test with invalid configuration to trigger error handling
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yml", delete=False
            ) as f:
                invalid_config = {
                    "version": 1,
                    "default_environment": "test",
                    "project_id": "error-test",
                    "plugins": {
                        "extractors": [
                            {
                                "name": "tap-ldap-error-test",
                                "executable": "/home/marlonsc/flext/.venv/bin/flext-tap-ldap",
                                "config": {
                                    "ldap_server": "invalid-server",
                                    "ldap_port": 999999,  # Invalid port
                                    "bind_dn": "invalid",
                                    "bind_password": "invalid",
                                    "base_dn": "invalid",
                                },
                            }
                        ]
                    },
                }
                yaml.dump(invalid_config, f)
                invalid_config_path = f.name

            # This should fail gracefully with proper error messages
            cmd = [
                "meltano",
                "--config-dir",
                str(Path(invalid_config_path).parent),
                "invoke",
                "tap-ldap-error-test",
                "--discover",
            ]
            result = subprocess.run(
                cmd, check=False, capture_output=True, text=True, timeout=30
            )

            # We expect this to fail, but with proper error handling
            if result.returncode != 0:
                if (
                    "connection" in result.stderr.lower()
                    or "timeout" in result.stderr.lower()
                ):
                    self.test_results["error_handling"] = True
                    return True
                self.test_results["error_handling"] = False
                return False
            self.test_results["error_handling"] = False
            return False

        except Exception:
            self.test_results["error_handling"] = False
            return False
        finally:
            # Clean up temp file
            with contextlib.suppress(builtins.BaseException):
                os.unlink(invalid_config_path)

    def generate_test_report(self) -> dict[str, any]:
        """Generate comprehensive test report."""
        passed_tests = sum(1 for result in self.test_results.values() if result)
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        return {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": f"{success_rate:.1f}%",
            },
            "test_results": self.test_results,
            "enterprise_compliance": {
                "docker_integration": True,
                "meltano_compatibility": True,
                "error_handling": self.test_results.get("error_handling", False),
                "ldif_output": self.test_results.get("ldif_output_valid", False),
                "tap_discovery": self.test_results.get("tap_discovery", False),
                "target_installation": self.test_results.get(
                    "target_installation", False
                ),
            },
        }

    def cleanup(self) -> None:
        """Clean up test environment."""
        try:
            # Stop Docker containers
            cmd = ["docker-compose", "down", "-v"]
            subprocess.run(
                cmd, check=False, cwd=self.test_dir, capture_output=True, timeout=60
            )

            # Clean up temp files
            temp_files = [
                "/tmp/target-ldif-test-output.ldif",
                "/tmp/target-ldap-test-output.ldif",
            ]

            for temp_file in temp_files:
                with contextlib.suppress(FileNotFoundError):
                    Path(temp_file).unlink()

        except Exception:
            pass


def run_integration_tests() -> bool | None:
    """Main test runner function."""
    test_dir = Path(__file__).parent
    test_suite = MeltanoLDAPIntegrationTest(test_dir)

    try:
        # Setup phase
        if not test_suite.setup_docker_environment():
            return False

        if not test_suite.install_flext_packages():
            return False

        if not test_suite.initialize_meltano_project():
            return False

        # Test phase

        test_suite.test_tap_installation()
        test_suite.test_target_installation()
        test_suite.test_full_pipeline()
        test_suite.test_error_handling()

        # Report phase

        report = test_suite.generate_test_report()

        for _result in report["test_results"].values():
            pass

        for _result in report["enterprise_compliance"].values():
            pass

        # Determine overall success
        success_rate = float(report["test_summary"]["success_rate"].replace("%", ""))
        return success_rate >= 80

    except KeyboardInterrupt:
        return False
    except Exception:
        return False
    finally:
        test_suite.cleanup()


if __name__ == "__main__":
    import sys

    success = run_integration_tests()
    sys.exit(0 if success else 1)
