"""FLX-Meltano Integration Example.

This example demonstrates how to use Meltano plugins as native FLX adapters
with complete workflow orchestration and state management.
"""

import asyncio
import os
from pathlib import Path

import structlog

from flx.adapters.outbound.meltano_factory import MeltanoAdapterFactory
from flx.ports.outbound.meltano_plugins import (
    MeltanoPluginConfig,
    MeltanoWorkflowConfig,
)

logger = structlog.get_logger(__name__)


async def basic_meltano_integration_example():
    """Demonstrate basic Meltano integration with FLX."""

    # Create project directory
    project_root = Path.cwd() / "meltano_projects" / "basic_example"
    project_root.mkdir(parents=True, exist_ok=True)

    try:
        # Create Meltano adapter using factory
        adapter = MeltanoAdapterFactory.create_adapter(
            project_root=str(project_root),
            config_template="development",
        )

        # Connect to Meltano
        await adapter.connect()

        # Get system information
        await adapter.get_system_info()

        # Initialize Meltano project if needed
        await adapter.initialize_meltano_project(
            project_name="basic_example", project_path=str(project_root.parent)
        )

        # Discover available plugins
        await adapter.discover_plugins(plugin_type="extractors", search_term="postgres")

        # Health check
        await adapter.health_check()

        await adapter.disconnect()

    except Exception as e:
        logger.error("Basic integration failed", error=str(e))


async def complete_pipeline_example():
    """Demonstrate complete ELT pipeline setup."""

    # Setup environment
    os.environ["MELTANO_PROJECT_ROOT"] = str(
        Path.cwd() / "meltano_projects" / "pipeline_example"
    )
    os.environ["MELTANO_CONFIG_TEMPLATE"] = "production"

    try:
        # Create adapter from environment
        adapter = MeltanoAdapterFactory.create_from_environment()
        await adapter.connect()

        # Setup complete pipeline with PostgreSQL to Snowflake template
        pipeline_adapter = await MeltanoAdapterFactory.setup_complete_pipeline(
            project_root=os.environ["MELTANO_PROJECT_ROOT"],
            plugin_template="postgres_to_snowflake",
            config_template="production",
            install_plugins=True,
            create_workflow=True,
        )

        # Configure extractor (tap-postgres)
        postgres_config = {
            "host": "localhost",
            "port": 5432,
            "user": "postgres",
            "password": "password",
            "dbname": "source_db",
        }

        await pipeline_adapter.update_plugin_config("tap-postgres", postgres_config)

        # Configure loader (target-snowflake)
        snowflake_config = {
            "account": "your_account",
            "user": "your_user",
            "password": "your_password",
            "role": "your_role",
            "database": "your_database",
            "warehouse": "your_warehouse",
            "schema": "public",
        }

        await pipeline_adapter.update_plugin_config(
            "target-snowflake", snowflake_config
        )

        # Test plugins
        await pipeline_adapter.test_plugin("tap-postgres")

        # List all plugins
        await pipeline_adapter.list_plugins(installed_only=True)

        # List workflows
        await pipeline_adapter.list_workflows()

        await pipeline_adapter.disconnect()

    except Exception as e:
        logger.error("Pipeline setup failed", error=str(e))


async def state_management_example():
    """Demonstrate state management capabilities."""

    project_root = Path.cwd() / "meltano_projects" / "state_example"

    try:
        adapter = MeltanoAdapterFactory.create_adapter(
            project_root=str(project_root),
            config_template="development",
        )

        await adapter.connect()

        # Set some state
        sample_state = {
            "singer_state": {
                "bookmarks": {
                    "users": {
                        "replication_key": "updated_at",
                        "replication_key_value": "2023-01-01T00:00:00Z",
                    }
                }
            }
        }

        state_id = "tap-postgres-to-target-snowflake"

        await adapter.set_state(state_id, sample_state)

        # Retrieve state
        retrieved_state = await adapter.get_state(state_id)
        if retrieved_state:
            pass

        # List all states
        await adapter.list_states()

        # Merge states example
        await adapter.set_state("source_state", sample_state)
        await adapter.merge_states("source_state", state_id)

        # Clear state
        await adapter.clear_state("source_state")

        await adapter.disconnect()

    except Exception as e:
        logger.error("State management failed", error=str(e))


async def workflow_orchestration_example():
    """Demonstrate workflow orchestration with Airflow."""

    project_root = Path.cwd() / "meltano_projects" / "workflow_example"

    try:
        adapter = MeltanoAdapterFactory.create_adapter(
            project_root=str(project_root),
            config_template="production",
            custom_config={
                "airflow_config": {
                    "dags_directory": "/tmp/airflow_dags",
                    "webserver_host": "localhost",
                    "webserver_port": 8080,
                }
            },
        )

        await adapter.connect()

        # Create a custom workflow
        workflow_config = MeltanoWorkflowConfig(
            name="daily_sales_pipeline",
            extractors=["tap-salesforce", "tap-postgres"],
            loaders=["target-snowflake"],
            transformers=["dbt-snowflake"],
            orchestrator="airflow",
            schedule="0 2 * * *",  # Daily at 2 AM
            environment="prod",
            state_backend="s3",
        )

        await adapter.create_workflow(workflow_config)

        # Generate Airflow DAG
        await adapter.generate_airflow_dag(workflow_config)

        # Deploy to Airflow
        await adapter.deploy_to_airflow(
            workflow_name="daily_sales_pipeline",
            airflow_config=adapter.config.airflow_config,
        )

        # Schedule workflow
        await adapter.schedule_workflow(
            workflow_name="daily_sales_pipeline",
            schedule="0 2 * * *",
            orchestrator="airflow",
        )

        # Execute workflow (dry run)
        await adapter.execute_workflow(
            workflow_name="daily_sales_pipeline",
            environment="prod",
            dry_run=True,
        )

        await adapter.disconnect()

    except Exception as e:
        logger.error("Workflow orchestration failed", error=str(e))


async def advanced_plugin_management_example():
    """Demonstrate advanced plugin management."""

    project_root = Path.cwd() / "meltano_projects" / "advanced_example"

    try:
        adapter = MeltanoAdapterFactory.create_adapter(
            project_root=str(project_root),
            config_template="data_lake",
        )

        await adapter.connect()

        # Install specific plugins with custom configurations
        plugins_to_install = [
            MeltanoPluginConfig(
                name="tap-github",
                plugin_type="extractors",
                namespace="tap_github",
                variant="meltanolabs",
                settings={
                    "repositories": ["owner/repo1", "owner/repo2"],
                    "auth_token": "your_github_token",
                },
                env={
                    "GITHUB_API_URL": "https://api.github.com",
                },
            ),
            MeltanoPluginConfig(
                name="target-jsonl",
                plugin_type="loaders",
                namespace="target_jsonl",
                settings={
                    "destination_path": "/tmp/github_data",
                },
            ),
        ]

        for plugin in plugins_to_install:
            await adapter.install_plugin(plugin)

        # List all extractors
        await adapter.list_plugins(plugin_type="extractors", installed_only=True)

        # Run ELT pipeline
        await adapter.run_elt_pipeline(
            extractor="tap-github",
            loader="target-jsonl",
            state_id="github-pipeline",
        )

        # Get plugin configuration
        await adapter.get_plugin_config("tap-github")

        # Update plugin configuration
        await adapter.update_plugin_config(
            "tap-github",
            {
                "repositories": ["owner/repo1", "owner/repo2", "owner/repo3"],
            },
        )

        # Test plugin
        await adapter.test_plugin("tap-github")

        await adapter.disconnect()

    except Exception as e:
        logger.error("Advanced plugin management failed", error=str(e))


async def demonstrate_crud_interface():
    """Demonstrate CRUD interface for unified access."""

    project_root = Path.cwd() / "meltano_projects" / "crud_example"

    try:
        adapter = MeltanoAdapterFactory.create_adapter(
            project_root=str(project_root),
            config_template="development",
        )

        await adapter.connect()

        # Using CRUD interface for plugins

        # Check if plugin exists
        await adapter.exists("plugin:tap-csv")

        # Set plugin configuration using CRUD interface
        csv_config = {
            "files": ["/path/to/data.csv"],
            "csv_files_definition": "/path/to/definition.json",
        }

        await adapter.set("plugin:tap-csv", csv_config)

        # Get plugin configuration using CRUD interface
        retrieved_config = await adapter.get("plugin:tap-csv")
        if retrieved_config:
            pass

        # Using CRUD interface for state

        state_data = {
            "singer_state": {"bookmarks": {"file1": {"last_modified": "2023-01-01"}}}
        }

        await adapter.set("state:csv-pipeline", state_data)

        retrieved_state = await adapter.get("state:csv-pipeline")
        if retrieved_state:
            pass

        # Check if state exists
        await adapter.exists("state:csv-pipeline")

        # Delete state using CRUD interface
        await adapter.delete("state:csv-pipeline")

        # Verify deletion
        await adapter.exists("state:csv-pipeline")

        await adapter.disconnect()

    except Exception as e:
        logger.error("CRUD interface demonstration failed", error=str(e))


async def show_available_templates():
    """Show available configuration and plugin templates."""

    templates = MeltanoAdapterFactory.get_available_templates()

    for _name, config in templates["config_templates"].items():
        pass

    for _name, config in templates["plugin_templates"].items():
        ", ".join(config.get("extractors", []))
        ", ".join(config.get("loaders", []))


async def main():
    """Run all examples."""

    # Show available templates
    await show_available_templates()

    # Run examples
    await basic_meltano_integration_example()
    await state_management_example()
    await demonstrate_crud_interface()

    # Advanced examples (commented out to avoid actual installations)


if __name__ == "__main__":
    # Configure logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Run examples
    asyncio.run(main())
