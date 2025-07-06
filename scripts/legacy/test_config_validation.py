#!/usr/bin/env python3
"""Comprehensive test script for configuration validation system.

Copyright (c) 2024 FLEXT TAP ORACLE WMS
SPDX-License-Identifier: MIT

This script tests both the JSON Schema-based validator and the original
ConfigValidator to ensure they work together properly.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Imports after path setup to avoid import errors
from tap_oracle_wms.config_schema import (
    ConfigSchemaValidator,
    generate_config_documentation,
)
from tap_oracle_wms.config_validator import ConfigValidationError, ConfigValidator


def test_json_schema_validation() -> None:
    """Test JSON Schema-based validation."""
    # Test base schema
    validator = ConfigSchemaValidator("base")

    # Test minimal valid config
    minimal_config = {
        "base_url": "https://wms-server.company.com",
        "username": "wms_user",
        "password": "secure_password",
        "wms_metadata_only_mode": "true",
    }

    _is_valid, _errors, _warnings = validator.validate(minimal_config)

    # Test invalid config
    invalid_config = {
        "base_url": "not-a-url",
        "username": "",
        "wms_metadata_only_mode": "false",  # Should be "true"
    }

    _is_valid, errors, _warnings = validator.validate(invalid_config)

    # Test production config generation
    prod_config = validator.generate_example_config("production")
    _is_valid, _errors, _warnings = validator.validate(prod_config)


def test_config_validator() -> None:
    """Test original ConfigValidator."""
    validator = ConfigValidator()

    # Test valid configuration
    valid_config = {
        "base_url": "https://wms-prod.company.com",
        "username": "production_user",
        "password": "secure_prod_password",
        "auth_method": "basic",
        "page_size": 1200,  # Within Oracle WMS limit of 1250
        "max_page_size": 1250,
        "request_timeout": 60,
        "max_retries": 3,
        "cache_ttl_seconds": 1800,
        "replication_key": "mod_ts",
        "incremental_overlap_minutes": 10,
        "lookback_minutes": 15,
        "company_code": "PROD",
        "facility_code": "MAIN",
        "company_timezone": "UTC",
        "currency_code": "USD",
        "entities": ["allocation", "order_hdr", "item_master"],
        "force_full_table": False,
        "enable_incremental": True,
    }

    try:
        validator.validate_config(valid_config)
    except Exception:
        return False
    else:
        return True

    # Test invalid configuration
    invalid_config = {
        "base_url": "invalid-url",
        "username": "",
        "password": "test",
        "auth_method": "invalid",
        "page_size": -1,
        "request_timeout": 0,
        "max_retries": -5,
        "currency_code": "INVALID",
        "entities": [123, ""],  # Invalid entity types
    }

    try:
        validator.validate_config(invalid_config)
    except Exception:
        # Expected to fail with invalid config
        return True
    else:
        return False


def test_integration() -> None:
    """Test integration between both validation systems."""
    # Create config that should pass both validators
    config = {
        "base_url": "https://wms-integration.company.com",
        "username": "integration_user",
        "password": "integration_password",
        "wms_metadata_only_mode": "true",
        "auth_method": "basic",
        "api_version": "v10",
        "endpoint_prefix": "/wms/lgfapi",
        "request_timeout": 30,
        "batch_size": 1000,
        "rate_limit_delay": 1.0,
        "max_retries": 3,
        "pagination_mode": "hateoas",
        "page_size": 1000,
        "enable_incremental": True,
        "replication_key": "mod_ts",
        "lookback_minutes": 5,
        "incremental_overlap_minutes": 5,
        "selected_entities": ["allocation", "order_hdr", "order_dtl"],
        "flattening_enabled": True,
        "force_full_table": False,
        "log_level": "INFO",
        "structured_logging": True,
        "enable_performance_logging": True,
        "enable_caching": True,
        "cache_ttl": 300,
        "dev_mode": False,
    }

    # Test with JSON Schema validator
    schema_validator = ConfigSchemaValidator("base")
    _is_valid, errors, _warnings = schema_validator.validate(config)

    if errors:
        for _error in errors:
            pass

    # Test with ConfigValidator (need to adapt config keys)
    config_validator_config = {
        "base_url": config["base_url"],
        "username": config["username"],
        "password": config["password"],
        "auth_method": config["auth_method"],
        "wms_api_version": config["api_version"],
        "endpoint_prefix": config["endpoint_prefix"],
        "page_mode": "sequenced",  # ConfigValidator expects "sequenced" not "hateoas"
        "page_size": config["page_size"],
        "max_page_size": 5000,
        "request_timeout": config["request_timeout"],
        "max_retries": config["max_retries"],
        "cache_ttl_seconds": config["cache_ttl"],
        "replication_key": config["replication_key"],
        "incremental_overlap_minutes": config["incremental_overlap_minutes"],
        "lookback_minutes": config["lookback_minutes"],
        "company_code": "*",
        "facility_code": "*",
        "company_timezone": "UTC",
        "currency_code": "USD",
        "entities": config["selected_entities"],
        "force_full_table": config["force_full_table"],
        "enable_incremental": config["enable_incremental"],
    }

    config_validator = ConfigValidator()
    try:
        config_validator.validate_config(config_validator_config)
    except (ConfigValidationError, ValueError, TypeError):
        return False
    else:
        return True


def test_documentation_generation() -> None:
    """Test configuration documentation generation."""
    try:
        doc = generate_config_documentation()

        # Check that key sections are present
        required_sections = [
            "# Oracle WMS Tap Configuration Reference",
            "## Configuration Properties",
            "### Connection",
            "### Performance",
            "## Configuration Examples",
        ]

        return all(section in doc for section in required_sections)
    except (ImportError, ModuleNotFoundError, AttributeError):
        return False


def main() -> None:
    """Run all configuration validation tests."""
    tests = [
        test_json_schema_validation,
        test_config_validator,
        test_integration,
        test_documentation_generation,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except (ImportError, ConfigValidationError, ValueError, TypeError) as e:
            # Log specific test failures for debugging
            print(f"Test {test.__name__} failed: {e}")

    if passed == total:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
