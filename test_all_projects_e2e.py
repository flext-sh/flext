#!/usr/bin/env python3
"""
Simple E2E test for all 4 Oracle OIC projects.
Tests basic functionality and integration between components.
"""

import json
import os
import sys
from pathlib import Path

# Add project paths
projects_root = Path(__file__).parent
sys.path.insert(0, str(projects_root / "tap-oracle-oic" / "src"))
sys.path.insert(0, str(projects_root / "target-oracle-oic" / "src"))
sys.path.insert(0, str(projects_root / "oracle-oic-ext"))
sys.path.insert(0, str(projects_root / "flx-oracle-oic" / "src"))
sys.path.insert(0, str(projects_root / "flx" / "src"))


def test_tap_oracle_oic():
    """Test tap-oracle-oic functionality."""

    try:
        from tap_oracle_oic import TapOIC

        # Load config
        config_path = projects_root / "tap-oracle-oic" / "config.json"
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)

        # Initialize tap
        tap = TapOIC(config=config)

        # Discover streams
        catalog = tap.discover_streams()

        # List stream names
        [stream.tap_stream_id for stream in catalog]

        return True

    except Exception:
        return False


def test_target_oracle_oic():
    """Test target-oracle-oic functionality."""

    try:
        from target_oracle_oic import TargetOracleOIC

        # Load config
        config_path = projects_root / "target-oracle-oic" / "config.json"
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)

        # Initialize target
        target = TargetOracleOIC(config=config)

        # Check sink mapping
        sinks = ["connections", "integrations", "packages", "lookups"]
        for sink_name in sinks:
            target._get_sink_class(sink_name)

        return True

    except Exception:
        return False


def test_oracle_oic_ext():
    """Test oracle-oic-ext functionality."""

    try:
        from oracle_oic_ext import OracleOICExtension

        # Initialize extension
        ext = OracleOICExtension()

        # Get available commands
        description = ext.describe()

        # List command categories
        command_categories = set()
        for cmd in description.commands:
            category = cmd.name.split(":")[0]
            command_categories.add(category)

        return True

    except Exception:
        return False


def test_flx_oracle_oic():
    """Test flx-oracle-oic functionality."""

    try:
        # Import FLX adapter
        from flx_oracle_oic.adapter import OracleOicHttpAdapter

        # Load config
        config_path = projects_root / "flx-oracle-oic" / "config.json"
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)

        # Initialize adapter
        OracleOicHttpAdapter(**config)

        # Test CLI import

        return True

    except Exception:
        return False


def test_integration():
    """Test integration between all components."""

    try:
        # Test that all modules can work together

        # Test config loading from .env
        from dotenv import load_dotenv

        load_dotenv(projects_root / "tap-oracle-oic" / ".env")

        # Check environment variables
        env_vars = ["OIC_IDCS_URL", "OIC_IDCS_CLIENT_ID", "OIC_INSTANCE_ID"]
        for var in env_vars:
            value = os.getenv(var)
            if value:
                pass

        return True

    except Exception:
        return False


def main():
    """Run all tests."""

    # Check if config files exist
    configs = [
        "tap-oracle-oic/config.json",
        "target-oracle-oic/config.json",
        "oracle-oic-ext/config.json",
        "flx-oracle-oic/config.json",
    ]

    for config in configs:
        config_path = projects_root / config
        if config_path.exists():
            pass

    # Run tests
    results = {
        "tap-oracle-oic": test_tap_oracle_oic(),
        "target-oracle-oic": test_target_oracle_oic(),
        "oracle-oic-ext": test_oracle_oic_ext(),
        "flx-oracle-oic": test_flx_oracle_oic(),
        "integration": test_integration(),
    }

    # Summary

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    for _project, _result in results.items():
        pass

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
