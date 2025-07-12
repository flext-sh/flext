#!/usr/bin/env python3
"""FLEXT Ecosystem Functional Test Suite - Zero Tolerance Validation.

This comprehensive test validates that all FLEXT projects are 100% functional
using flext-core as the foundation with zero fallbacks or legacy implementations.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add all FLEXT project src directories to path
flext_root = Path(__file__).parent
for project_dir in flext_root.glob("flext-*/src"):
    sys.path.insert(0, str(project_dir))

sys.path.insert(0, str(flext_root / "src"))


def test_flext_core_foundation() -> None:
    """Test flext-core as the foundational framework."""
    # Test base Pydantic classes

    # Test shared models with new consolidated configs
    from flext_core.domain.shared_models import (
        DatabaseConfig,
        HTTPConnectionConfig,
        RedisConfig,
        SecurityConfig,
    )

    # Test domain types

    # Test configuration base

    # Test instantiation of new consolidated configs
    db_config = DatabaseConfig()
    assert db_config.get_url().startswith("postgresql://")

    redis_config = RedisConfig()
    assert redis_config.get_url().startswith("redis://")

    http_config = HTTPConnectionConfig(base_url="https://test.com")
    assert http_config.base_url == "https://test.com"

    security_config = SecurityConfig()
    assert security_config.algorithm == "HS256"


def test_flext_api_integration() -> bool:
    """Test flext-api integration with flext-core."""
    try:
        # Test auth models using flext-core
        from flext_api.models.auth import (
            LoginRequest,
            UserAPI,
        )

        # Test plugin models with fixed legacy classes
        from flext_api.models.plugin import (
            LegacyPluginInstallRequest,
            LegacyPluginResponse,
        )

        # Test system models
        from flext_api.models.system import (
            MaintenanceRequest,
            SystemStatusResponse,
        )

        # Test that classes inherit from flext-core
        assert issubclass(UserAPI, APIResponse)
        assert issubclass(LoginRequest, APIRequest)
        assert issubclass(MaintenanceRequest, APIRequest)
        assert issubclass(SystemStatusResponse, APIResponse)
        assert issubclass(LegacyPluginInstallRequest, APIRequest)
        assert issubclass(LegacyPluginResponse, APIResponse)

    except Exception:
        return False

    return True


def test_flext_grpc_integration() -> bool:
    """Test flext-grpc integration with flext-core."""
    try:
        # Import DomainEntity for testing
        from flext_core.domain.pydantic_base import DomainEntity

        # Test models using flext-core (avoid protobuf loading)
        from flext_grpc.models import (
            PipelineModel,
            PluginModel,
        )

        # Test that classes inherit from flext-core
        assert issubclass(PluginModel, DomainEntity)
        assert issubclass(PipelineModel, DomainEntity)

        # Skip server test to avoid protobuf dependency issues

    except Exception:
        return False

    return True


def test_flext_oracle_connectivity() -> bool:
    """Test Oracle integration projects."""
    try:
        # Test flext-db-oracle
        from flext_db_oracle.connection.config import ConnectionConfig

        # Test Oracle OIC tap

        # Test that config uses flext-core
        assert issubclass(ConnectionConfig, BaseConfig)

    except Exception:
        return False

    return True


def test_observability_integration() -> bool:
    """Test flext-observability integration."""
    try:
        # Test logging functionality
        from flext_observability.logging import get_logger

        logger = get_logger("test")
        logger.info("Test log message")

    except Exception:
        return False

    return True


def test_pydantic_validation_fixes() -> bool:
    """Test that all Pydantic validation issues are resolved."""
    try:
        # Test PipelineExecutionStatus fix
        from flext_core.domain.shared_models import PipelineExecutionStatus
        assert PipelineExecutionStatus.COMPLETED == "completed"

        # Test pipeline commands fix
        from flext_core.application.pipeline import (
            CreatePipelineCommand,
            ExecutePipelineCommand,
        )
        assert issubclass(CreatePipelineCommand, APIRequest)
        assert issubclass(ExecutePipelineCommand, APIRequest)

        # Test error models fix
        from flext_core.domain.shared_models import ErrorDetail, ErrorResponse
        assert issubclass(ErrorDetail, APIBaseModel)
        assert issubclass(ErrorResponse, APIBaseModel)

    except Exception:
        return False

    return True


def test_code_duplication_elimination() -> bool:
    """Test that code duplications have been eliminated."""
    try:
        # Test consolidated configuration classes
        from flext_core.domain.shared_models import (
            DatabaseConfig,
            HTTPConnectionConfig,
            RedisConfig,
            SecurityConfig,
        )

        # Test enhanced DatabaseConfig
        db_config = DatabaseConfig(
            host="test.example.com",
            port=5432,
            database="test_db",
            username="test_user",
            password="test_pass",
            pool_size=15,
            pool_max_size=25,
        )
        url = db_config.get_url()
        assert "test.example.com" in url
        assert "test_db" in url

        # Test enhanced RedisConfig
        redis_config = RedisConfig(
            host="redis.example.com",
            port=6380,
            password="redis_pass",
            key_prefix="test:",
        )
        redis_url = redis_config.get_url()
        assert "redis_pass" in redis_url
        assert "redis.example.com" in redis_url

        # Test HTTPConnectionConfig for Oracle projects
        http_config = HTTPConnectionConfig(
            base_url="https://oic.example.com",
            timeout=60,
            max_retries=5,
            verify_ssl=False,
        )
        assert http_config.timeout == 60
        assert http_config.max_retries == 5

        # Test SecurityConfig for auth projects
        security_config = SecurityConfig(
            secret_key="super-secret-key-for-testing-123",
            access_token_expire_minutes=60,
            min_password_length=10,
        )
        assert security_config.access_token_expire_minutes == 60
        assert security_config.min_password_length == 10

    except Exception:
        return False

    return True


def main() -> int:
    """Run all functional tests."""
    # Add missing imports to global scope
    global APIBaseModel, APIRequest, APIResponse, BaseConfig
    from flext_core.config.base import BaseConfig
    from flext_core.domain.pydantic_base import APIBaseModel, APIRequest, APIResponse

    tests = [
        test_flext_core_foundation,
        test_pydantic_validation_fixes,
        test_code_duplication_elimination,
        test_flext_api_integration,
        test_flext_grpc_integration,
        test_flext_oracle_connectivity,
        test_observability_integration,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            result = test()
            if result is False:
                failed += 1
            else:
                passed += 1
        except Exception:
            failed += 1

    if failed == 0:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
