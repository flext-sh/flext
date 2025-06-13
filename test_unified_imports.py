#!/usr/bin/env python3
"""Test script demonstrating unified imports across PyAuto monorepo.

This script validates that all PyAuto projects can be imported together
without conflicts and that their main classes are accessible for
integration patterns.

The test demonstrates the user's request: "padronize e unifique o uso de
bibliotecas via poetry para que o pyauto importe todos os projetos para
evitar problemas de compatibilidade"
"""

import sys
from pathlib import Path

# Add all project source paths to sys.path
projects = [
    "flx/src",
    "flx-database-oracle/src",
    "flx-http-oracle-oic/src",
    "flx-http-oracle-wms/src",
    "client-a-mig-oud/src",
    "client-b-poc-oic-wms/src",
    "flx-adapter-example/src",
]

for project in projects:
    path = Path(__file__).parent / project
    if path.exists():
        sys.path.insert(0, str(path))


def test_core_framework_import() -> bool | None:
    """Test FLX core framework import."""
    try:
        import flx
        from flx import Bootstrap, Entity, get_logger
        return True
    except ImportError:
        return False


def test_oracle_adapters_import():
    """Test Oracle adapter imports."""
    success = True

    # Database adapter
    try:
        import flx_database_oracle
        from flx_database_oracle import FlxDatabaseConfig, FlxOracleDbAdapter
    except ImportError:
        success = False

    # OIC adapter
    try:
        import flx_http_oracle_oic
        from flx_http_oracle_oic import OracleOicClient, OracleOicConfig
    except ImportError:
        success = False

    # WMS adapter
    try:
        import flx_http_oracle_wms
        from flx_http_oracle_wms import WmsClient, WmsConfig
    except ImportError:
        success = False

    return success


def test_implementation_projects():
    """Test implementation project imports."""
    success = True

    # client-a migration
    try:
        import client-a_oud_mig
    except ImportError:
        success = False

    # client-b POC
    try:
        import gn_oic_wms_db
    except ImportError:
        success = False

    return success


def test_integration_pattern() -> bool | None:
    """Test that projects can work together."""
    try:
        # Import all main components
        from flx import get_logger
        from flx_database_oracle import FlxDatabaseConfig
        from flx_http_oracle_oic import OracleOicConfig
        from flx_http_oracle_wms import WmsConfig

        # Test logger integration
        logger = get_logger(__name__)
        logger.info("Testing unified logging across projects")

        # Test configuration pattern
        FlxDatabaseConfig(
            host="localhost",
            port=1521,
            service_name="ORCL",
            username="test",
            password="test",
        )

        OracleOicConfig(
            base_url="https://test.oraclecloud.com",
            username="test_user",
            password="test_password",
            instance_id="test_instance",
            region="us-ashburn-1",
            client_id="test_client_id",
            client_secret="test_client_secret",
            client_aud="test_audience",
            idcs_url="https://test-idcs.oracle.com",
        )

        WmsConfig(
            base_url="https://test-wms.oracle.com",
            username="test_user",
            password="test_password",
        )

        return True

    except Exception:
        return False


def main() -> int:
    """Run all import tests."""
    results = []

    # Run all tests
    results.append(test_core_framework_import())
    results.append(test_oracle_adapters_import())
    results.append(test_implementation_projects())
    results.append(test_integration_pattern())

    # Summary
    passed = sum(results)
    total = len(results)

    if passed == total:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
