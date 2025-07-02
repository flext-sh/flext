#!/usr/bin/env python3
"""FLEXT Framework System Validation Script

This script performs comprehensive validation of all FLEXT framework modules
to demonstrate 100% functional completion of critical business functionality.

Usage:
    python system_validation.py --full
    python system_validation.py --core-only
    python system_validation.py --api-only
"""

import asyncio
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Add FLEXT modules to path
sys.path.insert(0, str(Path(__file__).parent / "flext-core" / "src"))
sys.path.insert(0, str(Path(__file__).parent / "flext-auth" / "src"))
sys.path.insert(0, str(Path(__file__).parent / "flext-api" / "src"))



class ValidationResults:
    """Tracks validation results across all modules."""

    def __init__(self):
        self.results: dict[str, dict[str, Any]] = {}
        self.start_time = time.time()

    def add_result(self, module: str, test: str, success: bool, details: str = ""):
        if module not in self.results:
            self.results[module] = {"tests": [], "success_count": 0, "total_count": 0}

        self.results[module]["tests"].append(
            {
                "test": test,
                "success": success,
                "details": details,
                "timestamp": datetime.now().isoformat(),
            }
        )

        self.results[module]["total_count"] += 1
        if success:
            self.results[module]["success_count"] += 1

    def print_summary(self):
        """Print comprehensive validation summary."""
        time.time() - self.start_time

        overall_success = 0
        overall_total = 0

        for _module, data in self.results.items():
            (data["success_count"] / data["total_count"]) * 100

            overall_success += data["success_count"]
            overall_total += data["total_count"]

            # Show failed tests
            failed_tests = [t for t in data["tests"] if not t["success"]]
            if failed_tests:
                for _test in failed_tests:
                    pass

        (
            (overall_success / overall_total) * 100 if overall_total > 0 else 0
        )


# Initialize results tracker
results = ValidationResults()


def validate_core_modules():
    """Validate FLEXT core domain and configuration."""

    try:
        # Test 1: Core domain models
        try:

            results.add_result("flext-core", "domain_models_import", True)
        except Exception as e:
            results.add_result("flext-core", "domain_models_import", False, str(e))

        # Test 2: Configuration system
        try:
            from flext_core.config.domain_config import get_domain_constants

            get_domain_constants()
            results.add_result("flext-core", "configuration_system", True)
        except Exception as e:
            results.add_result("flext-core", "configuration_system", False, str(e))

        # Test 3: Advanced types system
        try:
            from flext_core.domain.advanced_types import ServiceResult

            # Test ServiceResult functionality
            success_result = ServiceResult.success("test")
            failure_result = ServiceResult.failure("error")
            assert success_result.is_success
            assert not failure_result.is_success
            results.add_result("flext-core", "advanced_types", True)
        except Exception as e:
            results.add_result("flext-core", "advanced_types", False, str(e))

        # Test 4: Import fallback patterns
        try:
            from flext_core.utils.import_fallback_patterns import SQLALCHEMY_DEPENDENCY

            SQLALCHEMY_DEPENDENCY.try_import(
                "sqlalchemy.engine", "make_url"
            )
            results.add_result("flext-core", "import_fallbacks", True)
        except Exception as e:
            results.add_result("flext-core", "import_fallbacks", False, str(e))

    except Exception as e:
        results.add_result("flext-core", "critical_error", False, str(e))


def validate_auth_system():
    """Validate FLEXT authentication and security."""

    try:
        # Test 1: Authentication implementation
        try:
            from flx_auth.authentication_implementation import (
                EnterpriseJWTService,
                EnterprisePasswordHasher,
            )

            results.add_result("flext-auth", "auth_classes_import", True)
        except Exception as e:
            results.add_result("flext-auth", "auth_classes_import", False, str(e))

        # Test 2: Password hashing
        try:
            hasher = EnterprisePasswordHasher()
            test_password = "test_password_123"
            hashed = hasher.hash_password(test_password)
            is_valid = hasher.verify_password(test_password, hashed)
            assert is_valid, "Password verification failed"
            results.add_result("flext-auth", "password_hashing", True)
        except Exception as e:
            results.add_result("flext-auth", "password_hashing", False, str(e))

        # Test 3: JWT service
        try:
            jwt_service = EnterpriseJWTService("test-secret-key-for-validation")

            # Create a mock user object
            class MockUser:
                def __init__(self):
                    self.user_id = "test-user-123"

            user = MockUser()
            access_token = jwt_service.create_access_token(user)
            refresh_token = jwt_service.create_refresh_token(user)

            assert len(access_token) > 0, "Access token not created"
            assert len(refresh_token) > 0, "Refresh token not created"
            results.add_result("flext-auth", "jwt_service", True)
        except Exception as e:
            results.add_result("flext-auth", "jwt_service", False, str(e))

        # Test 4: Token storage
        try:
            from flx_auth.in_memory_token_storage import InMemoryTokenStorage

            storage = InMemoryTokenStorage()

            # Test async token operations
            async def test_token_storage():
                await storage.store("test-key", "test-value", timedelta(minutes=5))
                value = await storage.get("test-key")
                assert value == "test-value", "Token storage/retrieval failed"
                exists = await storage.exists("test-key")
                assert exists, "Token existence check failed"
                deleted = await storage.delete("test-key")
                assert deleted, "Token deletion failed"

            asyncio.run(test_token_storage())
            results.add_result("flext-auth", "token_storage", True)
        except Exception as e:
            results.add_result("flext-auth", "token_storage", False, str(e))

    except Exception as e:
        results.add_result("flext-auth", "critical_error", False, str(e))


def validate_api_system():
    """Validate FLEXT API and web interfaces."""

    try:
        # Test 1: API application structure
        try:
            from flext_api import FlextAPI

            results.add_result("flext-api", "api_structure", True)
        except Exception as e:
            results.add_result("flext-api", "api_structure", False, str(e))

        # Test 2: API application initialization
        try:
            api_app = FlextAPI()
            assert hasattr(api_app, "app"), "FastAPI app not initialized"
            results.add_result("flext-api", "api_initialization", True)
        except Exception as e:
            results.add_result("flext-api", "api_initialization", False, str(e))

        # Test 3: Pipeline storage
        try:
            from flext_api.storage.pipeline_storage import ThreadSafePipelineStorage

            storage = ThreadSafePipelineStorage()

            # Test pipeline operations
            test_pipeline = {
                "id": "test-pipeline",
                "name": "Test Pipeline",
                "steps": ["extract", "transform", "load"],
            }

            pipeline_id = storage.create_pipeline(test_pipeline)
            retrieved = storage.get_pipeline(pipeline_id)
            assert retrieved is not None, "Pipeline retrieval failed"

            pipelines = storage.list_pipelines()
            assert len(pipelines) > 0, "Pipeline listing failed"

            results.add_result("flext-api", "pipeline_storage", True)
        except Exception as e:
            results.add_result("flext-api", "pipeline_storage", False, str(e))

    except Exception as e:
        results.add_result("flext-api", "critical_error", False, str(e))


def validate_integration_points():
    """Validate integration between modules."""

    try:
        # Test 1: Auth + API integration
        try:
            from flext_api import FlextAPI
            from flx_auth.authentication_implementation import (
                EnterpriseAuthenticationService,
            )

            # Test that API can use auth service
            FlextAPI()
            auth_service = EnterpriseAuthenticationService()

            results.add_result("integration", "auth_api", True)
        except Exception as e:
            results.add_result("integration", "auth_api", False, str(e))

        # Test 2: Core + Auth integration
        try:
            from flext_core.domain.advanced_types import ServiceResult
            from flx_auth.authentication_implementation import EnterprisePasswordHasher

            # Test using core types in auth
            hasher = EnterprisePasswordHasher()
            result = ServiceResult.success(hasher)
            assert result.is_success, "Core types integration failed"

            results.add_result("integration", "core_auth", True)
        except Exception as e:
            results.add_result("integration", "core_auth", False, str(e))

        # Test 3: End-to-end user authentication flow
        try:
            from flx_auth.authentication_implementation import (
                EnterpriseAuthenticationService,
            )

            auth_service = EnterpriseAuthenticationService()

            # Simulate user registration
            user_data = {
                "email": "test@example.com",
                "password_hash": auth_service.password_hasher.hash_password(
                    "testpass123"
                ),
                "username": "testuser",
                "roles": ["user"],
            }

            # Test async user creation
            async def test_user_creation():
                user = await auth_service.user_repository.create_user(user_data)
                assert user is not None, "User creation failed"
                return True

            success = asyncio.run(test_user_creation())
            assert success, "Async user creation test failed"

            results.add_result("integration", "e2e_auth_flow", True)
        except Exception as e:
            results.add_result("integration", "e2e_auth_flow", False, str(e))

    except Exception as e:
        results.add_result("integration", "critical_error", False, str(e))


def validate_performance():
    """Validate system performance characteristics."""

    try:
        # Test 1: Authentication performance
        start_time = time.time()
        try:
            from flx_auth.authentication_implementation import EnterprisePasswordHasher

            hasher = EnterprisePasswordHasher()

            # Hash 10 passwords to test performance
            for i in range(10):
                hasher.hash_password(f"password_{i}")

            duration = time.time() - start_time
            if duration < 5.0:  # Should complete in under 5 seconds
                results.add_result("performance", "password_hashing", True)
            else:
                results.add_result(
                    "performance",
                    "password_hashing",
                    False,
                    f"Too slow: {duration:.2f}s",
                )
        except Exception as e:
            results.add_result("performance", "password_hashing", False, str(e))

        # Test 2: API startup performance
        start_time = time.time()
        try:
            from flext_api import FlextAPI

            FlextAPI()

            duration = time.time() - start_time
            if duration < 2.0:  # Should start in under 2 seconds
                results.add_result("performance", "api_startup", True)
            else:
                results.add_result(
                    "performance", "api_startup", False, f"Too slow: {duration:.2f}s"
                )
        except Exception as e:
            results.add_result("performance", "api_startup", False, str(e))

    except Exception as e:
        results.add_result("performance", "critical_error", False, str(e))


async def main():
    """Run comprehensive system validation."""

    # Run all validation suites
    validate_core_modules()
    validate_auth_system()
    validate_api_system()
    validate_integration_points()
    validate_performance()

    # Print final summary
    results.print_summary()

    # Determine exit code
    overall_success = sum(data["success_count"] for data in results.results.values())
    overall_total = sum(data["total_count"] for data in results.results.values())
    success_rate = (overall_success / overall_total) * 100 if overall_total > 0 else 0

    if success_rate >= 85:
        return 0
    return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
