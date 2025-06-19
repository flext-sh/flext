# 🛠️ FLX Adapter Example - Scripts and Automation

> **Module**: Development and deployment scripts for FLX Adapter Example project with automation utilities | **Audience**: DevOps Engineers, Developers, System Administrators | **Status**: Production Ready

## 📋 **Overview**

Comprehensive collection of scripts and automation utilities for the FLX Adapter Example project, providing essential functionality for development workflows, deployment automation, testing procedures, and maintenance tasks. These scripts demonstrate best practices for FLX framework project automation.

---

## 🧭 **Navigation Context**

**🏠 Root**: [PyAuto Home](../../README.md) → **📂 Component**: [FLX Adapter Example](../README.md) → **📂 Current**: Scripts and Automation

---

## 🎯 **Module Purpose**

This scripts module provides essential automation utilities for the FLX Adapter Example project, including development environment setup, deployment procedures, testing automation, database management, and maintenance scripts following enterprise automation standards.

### **Key Script Categories**

- **Development Scripts** - Environment setup and development workflow automation
- **Build and Deployment** - CI/CD pipeline scripts and deployment automation
- **Testing Scripts** - Test execution and validation automation
- **Database Scripts** - Database setup, migration, and maintenance
- **Monitoring Scripts** - Health checks and performance monitoring
- **Utility Scripts** - Common utilities and helper scripts

---

## 📁 **Scripts Structure**

```
scripts/
├── development/
│   ├── setup_dev_environment.py     # Complete development setup
│   ├── start_local_services.py      # Start local dependencies
│   ├── reset_dev_database.py        # Reset development database
│   └── generate_test_data.py        # Generate test data fixtures
├── build/
│   ├── build_application.py         # Application build automation
│   ├── create_docker_image.py       # Docker image creation
│   ├── run_quality_checks.py        # Code quality validation
│   └── package_application.py       # Application packaging
├── deployment/
│   ├── deploy_to_staging.py         # Staging deployment
│   ├── deploy_to_production.py      # Production deployment
│   ├── rollback_deployment.py       # Deployment rollback
│   └── health_check_deployment.py   # Post-deployment validation
├── testing/
│   ├── run_all_tests.py             # Complete test suite execution
│   ├── run_performance_tests.py     # Performance testing automation
│   ├── run_security_tests.py        # Security testing validation
│   └── generate_test_reports.py     # Test reporting and analysis
├── database/
│   ├── setup_database.py            # Database initialization
│   ├── run_migrations.py            # Database migration execution
│   ├── backup_database.py           # Database backup automation
│   └── seed_database.py             # Database seeding with fixtures
├── monitoring/
│   ├── health_check.py              # Application health monitoring
│   ├── performance_monitor.py       # Performance metrics collection
│   ├── log_analyzer.py              # Log analysis and alerting
│   └── system_status.py             # System status reporting
└── utilities/
    ├── clean_temp_files.py          # Temporary file cleanup
    ├── update_dependencies.py       # Dependency management
    ├── generate_documentation.py    # Documentation generation
    └── validate_configuration.py    # Configuration validation
```

---

## 🔧 **Script Categories**

### **1. Development Scripts (development/)**

#### **Development Environment Setup (setup_dev_environment.py)**

```python
#!/usr/bin/env python3
"""Complete development environment setup for FLX Adapter Example.

This script automates the entire development environment setup including
Python environment, dependencies, database, and configuration.
"""

import os
import sys
import subprocess
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Optional

class DevEnvironmentSetup:
    """Development environment setup automation."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = self._setup_logging()

    def setup_complete_environment(self) -> None:
        """Setup complete development environment."""

        self.logger.info("Starting FLX Adapter Example development setup...")

        try:
            # 1. Validate system requirements
            self._validate_system_requirements()

            # 2. Setup Python environment
            self._setup_python_environment()

            # 3. Start local services
            self._start_local_services()

            # 4. Setup database
            self._setup_development_database()

            # 5. Generate configuration
            self._generate_development_config()

            # 6. Install pre-commit hooks
            self._install_pre_commit_hooks()

            # 7. Generate test data
            self._generate_test_data()

            # 8. Validate setup
            self._validate_complete_setup()

            self.logger.info("✅ Development environment setup completed successfully!")
            self._print_next_steps()

        except Exception as e:
            self.logger.error(f"❌ Setup failed: {e}")
            sys.exit(1)

    def _validate_system_requirements(self) -> None:
        """Validate required system tools and versions."""

        self.logger.info("Validating system requirements...")

        requirements = {
            "python": ("3.9", "python --version"),
            "poetry": ("1.5", "poetry --version"),
            "docker": ("20.0", "docker --version"),
            "docker-compose": ("2.0", "docker-compose --version")
        }

        for tool, (min_version, command) in requirements.items():
            try:
                result = subprocess.run(
                    command.split(),
                    capture_output=True,
                    text=True,
                    check=True
                )
                self.logger.info(f"✅ {tool}: {result.stdout.strip()}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                raise EnvironmentError(f"Required tool not found: {tool} >= {min_version}")

    def _setup_python_environment(self) -> None:
        """Setup Python virtual environment with Poetry."""

        self.logger.info("Setting up Python environment...")

        # Install dependencies
        subprocess.run(
            ["poetry", "install", "--with", "dev,test"],
            cwd=self.project_root,
            check=True
        )

        # Verify installation
        result = subprocess.run(
            ["poetry", "run", "python", "-c", "import flx_adapter_example; print('✅ Package installed')"],
            cwd=self.project_root,
            capture_output=True,
            text=True,
            check=True
        )
        self.logger.info(result.stdout.strip())

    def _start_local_services(self) -> None:
        """Start local development services with Docker."""

        self.logger.info("Starting local services...")

        # Start PostgreSQL and Redis
        subprocess.run([
            "docker-compose",
            "-f", "docker-compose.dev.yml",
            "up", "-d",
            "postgres", "redis"
        ], cwd=self.project_root, check=True)

        # Wait for services to be ready
        self._wait_for_services()

    def _wait_for_services(self) -> None:
        """Wait for local services to be ready."""

        import time
        import psycopg2
        import redis

        # Wait for PostgreSQL
        self.logger.info("Waiting for PostgreSQL...")
        for attempt in range(30):
            try:
                conn = psycopg2.connect(
                    host="localhost",
                    port=5432,
                    user="flx_dev",
                    password="dev_password",
                    database="flx_adapter_example_dev"
                )
                conn.close()
                self.logger.info("✅ PostgreSQL is ready")
                break
            except psycopg2.OperationalError:
                time.sleep(1)
        else:
            raise RuntimeError("PostgreSQL did not start within 30 seconds")

        # Wait for Redis
        self.logger.info("Waiting for Redis...")
        for attempt in range(30):
            try:
                r = redis.Redis(host="localhost", port=6379)
                r.ping()
                self.logger.info("✅ Redis is ready")
                break
            except redis.ConnectionError:
                time.sleep(1)
        else:
            raise RuntimeError("Redis did not start within 30 seconds")

    def _setup_development_database(self) -> None:
        """Setup development database with schema."""

        self.logger.info("Setting up development database...")

        # Run database migrations
        subprocess.run([
            "poetry", "run", "alembic", "upgrade", "head"
        ], cwd=self.project_root, check=True)

        self.logger.info("✅ Database schema created")

    def _generate_development_config(self) -> None:
        """Generate development configuration files."""

        self.logger.info("Generating development configuration...")

        config_content = """# Development configuration for FLX Adapter Example
environment: development

database:
  url: "postgresql+asyncpg://flx_dev:dev_password@localhost:5432/flx_adapter_example_dev"
  echo: true
  pool_size: 5

redis:
  url: "redis://localhost:6379/0"

logging:
  level: DEBUG
  format: detailed

api:
  host: "0.0.0.0"
  port: 8000
  debug: true
  reload: true

testing:
  test_database_url: "postgresql+asyncpg://flx_dev:dev_password@localhost:5432/flx_adapter_example_test"
"""

        config_file = self.project_root / "config" / "development.yaml"
        config_file.parent.mkdir(exist_ok=True)
        config_file.write_text(config_content)

        self.logger.info(f"✅ Configuration written to {config_file}")

    def _generate_test_data(self) -> None:
        """Generate test data for development."""

        self.logger.info("Generating test data...")

        subprocess.run([
            "poetry", "run", "python", "-m", "scripts.database.seed_database"
        ], cwd=self.project_root, check=True)

        self.logger.info("✅ Test data generated")

    def _validate_complete_setup(self) -> None:
        """Validate complete development setup."""

        self.logger.info("Validating complete setup...")

        # Test database connection
        subprocess.run([
            "poetry", "run", "python", "-c",
            "import asyncio; from flx_adapter_example.infrastructure.database import test_connection; asyncio.run(test_connection())"
        ], cwd=self.project_root, check=True)

        # Run quick health check
        subprocess.run([
            "poetry", "run", "python", "-m", "scripts.monitoring.health_check"
        ], cwd=self.project_root, check=True)

        self.logger.info("✅ Setup validation completed")

    def _print_next_steps(self) -> None:
        """Print next steps for developer."""

        next_steps = """
🎉 Development environment setup completed!

Next steps:
1. Activate the environment:
   poetry shell

2. Start the development server:
   poetry run uvicorn flx_adapter_example.main:app --reload

3. Run tests:
   poetry run pytest

4. View API documentation:
   http://localhost:8000/docs

5. Access development database:
   psql -h localhost -U flx_dev -d flx_adapter_example_dev

Happy coding! 🚀
"""
        print(next_steps)

if __name__ == "__main__":
    setup = DevEnvironmentSetup(Path(__file__).parent.parent)
    setup.setup_complete_environment()
```

#### **Local Services Management (start_local_services.py)**

```python
#!/usr/bin/env python3
"""Start and manage local development services."""

import subprocess
import time
import logging
from pathlib import Path

class LocalServicesManager:
    """Manage local development services."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logging.getLogger(__name__)

    def start_all_services(self) -> None:
        """Start all required local services."""

        services = [
            ("PostgreSQL", self._start_postgres),
            ("Redis", self._start_redis),
            ("Jaeger", self._start_jaeger),
            ("Prometheus", self._start_prometheus)
        ]

        for service_name, start_func in services:
            try:
                self.logger.info(f"Starting {service_name}...")
                start_func()
                self.logger.info(f"✅ {service_name} started successfully")
            except Exception as e:
                self.logger.error(f"❌ Failed to start {service_name}: {e}")
                raise

    def _start_postgres(self) -> None:
        """Start PostgreSQL service."""
        subprocess.run([
            "docker", "run", "-d",
            "--name", "flx-postgres-dev",
            "-e", "POSTGRES_USER=flx_dev",
            "-e", "POSTGRES_PASSWORD=dev_password",
            "-e", "POSTGRES_DB=flx_adapter_example_dev",
            "-p", "5432:5432",
            "postgres:14"
        ], check=True)

    def _start_redis(self) -> None:
        """Start Redis service."""
        subprocess.run([
            "docker", "run", "-d",
            "--name", "flx-redis-dev",
            "-p", "6379:6379",
            "redis:7-alpine"
        ], check=True)

    def stop_all_services(self) -> None:
        """Stop all local services."""
        containers = ["flx-postgres-dev", "flx-redis-dev", "flx-jaeger-dev", "flx-prometheus-dev"]

        for container in containers:
            try:
                subprocess.run(["docker", "stop", container], check=True)
                subprocess.run(["docker", "rm", container], check=True)
                self.logger.info(f"✅ Stopped {container}")
            except subprocess.CalledProcessError:
                self.logger.warning(f"Container {container} not found or already stopped")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    manager = LocalServicesManager(Path(__file__).parent.parent)

    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "stop":
        manager.stop_all_services()
    else:
        manager.start_all_services()
```

### **2. Build Scripts (build/)**

#### **Application Build Automation (build_application.py)**

```python
#!/usr/bin/env python3
"""Application build automation for FLX Adapter Example."""

import subprocess
import logging
from pathlib import Path
from typing import Dict, List

class ApplicationBuilder:
    """Automate application build process."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logging.getLogger(__name__)

    def build_application(self, build_type: str = "development") -> None:
        """Build application with specified configuration."""

        self.logger.info(f"Starting {build_type} build...")

        # 1. Clean previous build
        self._clean_build_artifacts()

        # 2. Run code quality checks
        self._run_quality_checks()

        # 3. Run tests
        self._run_tests()

        # 4. Build Python package
        self._build_python_package()

        # 5. Create Docker image
        if build_type in ["staging", "production"]:
            self._build_docker_image(build_type)

        # 6. Generate build report
        self._generate_build_report(build_type)

        self.logger.info(f"✅ {build_type} build completed successfully!")

    def _clean_build_artifacts(self) -> None:
        """Clean previous build artifacts."""

        self.logger.info("Cleaning build artifacts...")

        # Remove build directories
        build_dirs = ["build", "dist", "*.egg-info"]
        for pattern in build_dirs:
            subprocess.run(f"rm -rf {pattern}", shell=True, cwd=self.project_root)

        # Remove Python cache
        subprocess.run("find . -type d -name __pycache__ -delete", shell=True, cwd=self.project_root)
        subprocess.run("find . -name '*.pyc' -delete", shell=True, cwd=self.project_root)

    def _run_quality_checks(self) -> None:
        """Run code quality checks."""

        self.logger.info("Running code quality checks...")

        # Format check
        subprocess.run([
            "poetry", "run", "black", "--check", "."
        ], cwd=self.project_root, check=True)

        # Lint check
        subprocess.run([
            "poetry", "run", "ruff", "check", "."
        ], cwd=self.project_root, check=True)

        # Type check
        subprocess.run([
            "poetry", "run", "mypy", "flx_adapter_example"
        ], cwd=self.project_root, check=True)

        self.logger.info("✅ Code quality checks passed")

    def _run_tests(self) -> None:
        """Run test suite."""

        self.logger.info("Running tests...")

        subprocess.run([
            "poetry", "run", "pytest",
            "--cov=flx_adapter_example",
            "--cov-report=html",
            "--cov-report=xml",
            "--junit-xml=test-results.xml"
        ], cwd=self.project_root, check=True)

        self.logger.info("✅ Tests passed")

    def _build_python_package(self) -> None:
        """Build Python package."""

        self.logger.info("Building Python package...")

        subprocess.run([
            "poetry", "build"
        ], cwd=self.project_root, check=True)

        self.logger.info("✅ Python package built")

    def _build_docker_image(self, build_type: str) -> None:
        """Build Docker image."""

        self.logger.info(f"Building Docker image for {build_type}...")

        tag = f"flx-adapter-example:{build_type}"

        subprocess.run([
            "docker", "build",
            "-t", tag,
            "-f", f"Dockerfile.{build_type}",
            "."
        ], cwd=self.project_root, check=True)

        self.logger.info(f"✅ Docker image built: {tag}")

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)

    build_type = sys.argv[1] if len(sys.argv) > 1 else "development"
    builder = ApplicationBuilder(Path(__file__).parent.parent)
    builder.build_application(build_type)
```

### **3. Testing Scripts (testing/)**

#### **Comprehensive Test Execution (run_all_tests.py)**

```python
#!/usr/bin/env python3
"""Execute comprehensive test suite for FLX Adapter Example."""

import subprocess
import logging
import time
from pathlib import Path
from typing import Dict, List

class TestSuiteRunner:
    """Execute and manage comprehensive test suite."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logging.getLogger(__name__)

    def run_complete_test_suite(self) -> Dict[str, bool]:
        """Run complete test suite with all test categories."""

        self.logger.info("Starting comprehensive test suite execution...")

        test_results = {}

        # 1. Unit tests
        test_results["unit"] = self._run_unit_tests()

        # 2. Integration tests
        test_results["integration"] = self._run_integration_tests()

        # 3. End-to-end tests
        test_results["e2e"] = self._run_e2e_tests()

        # 4. Performance tests
        test_results["performance"] = self._run_performance_tests()

        # 5. Security tests
        test_results["security"] = self._run_security_tests()

        # 6. Generate comprehensive report
        self._generate_test_report(test_results)

        # 7. Check overall results
        all_passed = all(test_results.values())

        if all_passed:
            self.logger.info("✅ All tests passed successfully!")
        else:
            self.logger.error("❌ Some tests failed")
            failed_tests = [test for test, passed in test_results.items() if not passed]
            self.logger.error(f"Failed test categories: {failed_tests}")

        return test_results

    def _run_unit_tests(self) -> bool:
        """Run unit tests."""

        self.logger.info("Running unit tests...")

        try:
            subprocess.run([
                "poetry", "run", "pytest",
                "tests/unit/",
                "-v",
                "--cov=flx_adapter_example",
                "--cov-report=html:htmlcov/unit",
                "--junit-xml=test-results-unit.xml"
            ], cwd=self.project_root, check=True)

            self.logger.info("✅ Unit tests passed")
            return True

        except subprocess.CalledProcessError:
            self.logger.error("❌ Unit tests failed")
            return False

    def _run_integration_tests(self) -> bool:
        """Run integration tests."""

        self.logger.info("Running integration tests...")

        try:
            # Start test services
            subprocess.run([
                "docker-compose", "-f", "docker-compose.test.yml", "up", "-d"
            ], cwd=self.project_root, check=True)

            # Wait for services
            time.sleep(10)

            # Run integration tests
            subprocess.run([
                "poetry", "run", "pytest",
                "tests/integration/",
                "-v",
                "--junit-xml=test-results-integration.xml"
            ], cwd=self.project_root, check=True)

            self.logger.info("✅ Integration tests passed")
            return True

        except subprocess.CalledProcessError:
            self.logger.error("❌ Integration tests failed")
            return False
        finally:
            # Cleanup test services
            subprocess.run([
                "docker-compose", "-f", "docker-compose.test.yml", "down"
            ], cwd=self.project_root)

    def _run_performance_tests(self) -> bool:
        """Run performance tests."""

        self.logger.info("Running performance tests...")

        try:
            subprocess.run([
                "poetry", "run", "pytest",
                "tests/performance/",
                "-v",
                "--benchmark-only",
                "--benchmark-json=benchmark-results.json"
            ], cwd=self.project_root, check=True)

            self.logger.info("✅ Performance tests passed")
            return True

        except subprocess.CalledProcessError:
            self.logger.error("❌ Performance tests failed")
            return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    runner = TestSuiteRunner(Path(__file__).parent.parent)
    results = runner.run_complete_test_suite()

    import sys
    sys.exit(0 if all(results.values()) else 1)
```

### **4. Database Scripts (database/)**

#### **Database Setup and Migration (setup_database.py)**

```python
#!/usr/bin/env python3
"""Database setup and migration script."""

import asyncio
import logging
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine

class DatabaseSetup:
    """Database setup and initialization."""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.logger = logging.getLogger(__name__)

    async def setup_database(self) -> None:
        """Setup database with schema and initial data."""

        self.logger.info("Setting up database...")

        # 1. Create database if not exists
        await self._create_database_if_not_exists()

        # 2. Run migrations
        await self._run_migrations()

        # 3. Seed with initial data
        await self._seed_initial_data()

        # 4. Validate setup
        await self._validate_database_setup()

        self.logger.info("✅ Database setup completed")

    async def _create_database_if_not_exists(self) -> None:
        """Create database if it doesn't exist."""

        # Implementation for database creation
        pass

    async def _run_migrations(self) -> None:
        """Run database migrations."""

        import subprocess

        subprocess.run([
            "poetry", "run", "alembic", "upgrade", "head"
        ], check=True)

    async def _seed_initial_data(self) -> None:
        """Seed database with initial data."""

        engine = create_async_engine(self.database_url)

        # Add initial data seeding logic
        pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    import sys
    database_url = sys.argv[1] if len(sys.argv) > 1 else "postgresql+asyncpg://flx_dev:dev_password@localhost:5432/flx_adapter_example_dev"

    setup = DatabaseSetup(database_url)
    asyncio.run(setup.setup_database())
```

---

## 🔄 **Script Usage Examples**

### **Development Workflow**

```bash
# Complete development setup
./scripts/development/setup_dev_environment.py

# Start local services
./scripts/development/start_local_services.py

# Reset development database
./scripts/database/reset_dev_database.py

# Generate fresh test data
./scripts/development/generate_test_data.py
```

### **Build and Test Workflow**

```bash
# Run all tests
./scripts/testing/run_all_tests.py

# Build application
./scripts/build/build_application.py production

# Run quality checks
./scripts/build/run_quality_checks.py

# Performance testing
./scripts/testing/run_performance_tests.py
```

### **Deployment Workflow**

```bash
# Deploy to staging
./scripts/deployment/deploy_to_staging.py --version 1.2.0

# Health check
./scripts/monitoring/health_check.py --environment staging

# Deploy to production
./scripts/deployment/deploy_to_production.py --version 1.2.0

# Rollback if needed
./scripts/deployment/rollback_deployment.py --version 1.1.0
```

---

## 🧪 **Script Testing**

### **Script Validation Tests**

```python
import pytest
import subprocess
from pathlib import Path

class TestDevelopmentScripts:
    """Test development scripts functionality."""

    def test_setup_script_validation(self):
        """Test development setup script validation."""
        script_path = Path("scripts/development/setup_dev_environment.py")

        # Test script syntax
        result = subprocess.run([
            "python", "-m", "py_compile", str(script_path)
        ], capture_output=True)

        assert result.returncode == 0, "Script has syntax errors"

    def test_build_script_dry_run(self):
        """Test build script in dry-run mode."""
        result = subprocess.run([
            "python", "scripts/build/build_application.py", "--dry-run"
        ], capture_output=True, text=True)

        assert result.returncode == 0
        assert "Build completed" in result.stdout
```

---

## 🔗 **Cross-References**

### **Component Documentation**

- [Component Overview](../README.md) - Complete FLX Adapter Example documentation
- [Source Implementation](../src/README.md) - Source code structure
- [Tests](../tests/README.md) - Testing framework and procedures

### **Framework Documentation**

- [FLX Framework](../../flx/README.md) - Core framework documentation
- [Development Guide](../../docs/development/README.md) - Development workflows
- [Deployment Guide](../../docs/deployment/README.md) - Deployment procedures

### **External Tools**

- [Poetry Documentation](https://python-poetry.org/docs/) - Dependency management
- [Docker Documentation](https://docs.docker.com/) - Containerization
- [Pytest Documentation](https://docs.pytest.org/) - Testing framework

---

**📂 Module**: Scripts and Automation | **🏠 Component**: [FLX Adapter Example](../README.md) | **Framework**: Python 3.9+ | **Updated**: 2025-06-19
