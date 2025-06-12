# PyAuto Dependency Standardization Report

Generated on: /home/marlonsc/pyauto

## Standard Dependency Versions

| Dependency | Version | Category |
|------------|---------|----------|
| pydantic | ^2.11.5 | Core Framework |
| sqlalchemy | ^2.0.0 | Core Framework |
| fastapi | ^0.115.0 | Core Framework |
| httpx | ^0.28.1 | Core Framework |
| oracledb | ^2.5.0 | Database |
| alembic | ^1.14.0 | Database |
| aiosqlite | ^0.21.0 | Database |
| click | ^8.2.1 | CLI & UI |
| typer | ^0.9.0 | CLI & UI |
| rich | ^14.0.0 | CLI & UI |
| cyclopts | ^3.1.0 | CLI & UI |
| pytest (dev) | ^8.4.0 | Testing |
| pytest-asyncio (dev) | ^0.23.5.post1,<0.24.0 | Testing |
| pytest-cov (dev) | ^6.1.1 | Testing |
| mypy (dev) | ^1.16.0 | Testing |
| black (dev) | ^25.1.0 | Code Quality |
| isort (dev) | ^6.0.1 | Code Quality |
| ruff (dev) | ^0.11.13 | Code Quality |
| bandit (dev) | ^1.8.0 | Code Quality |
| pandas | ^2.2.0 | Data Processing |
| pyarrow | ^18.0.0 | Data Processing |
| openpyxl | ^3.1.0 | Data Processing |
| python-dotenv | ^1.1.0 | Configuration |
| pyyaml | ^6.0.2 | Configuration |
| jinja2 | ^3.1.0 | Configuration |

## Benefits of Standardization

- ✅ Eliminates version conflicts between projects
- 🔧 Ensures compatibility across the monorepo
- 📦 Simplifies dependency management
- 🚀 Enables shared tooling and configurations
- 🔒 Improves security through consistent updates

## Local Path Dependencies

The following projects maintain local path dependencies:

- `flx-database-oracle` → depends on `flx`
- `flx-http-oracle-oic` → depends on `flx`
- `flx-http-oracle-wms` → depends on `flx`
- `algar-mig-oud` → depends on `flx`
- `gruponos-poc-oic-wms` → depends on all FLX adapters
