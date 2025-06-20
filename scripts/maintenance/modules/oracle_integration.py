#!/usr/bin/env python3
"""Oracle Integration Module

Unified Oracle WMS/OIC integration automation module.
Consolidates all Oracle integration scripts across the workspace.
"""

import os
import time
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .base import CustomFixModule, Issue


class OracleIntegrationModule(CustomFixModule):
    """Module for unified Oracle WMS/OIC integration automation."""

    name = "oracle_integration"
    description = "Unified Oracle WMS/OIC integration automation"

    # Oracle connection configurations
    ORACLE_CONFIGS = {
        "wms": {
            "host": "ORACLE_HOST",
            "port": ("ORACLE_PORT", 1521),
            "service_name": "ORACLE_SERVICE_NAME",
            "username": "ORACLE_USERNAME",
            "password": "ORACLE_PASSWORD",
            "schema": "ORACLE_SCHEMA",
            "timeout": ("CONNECTION_TIMEOUT", 30),
        },
        "oic": {
            "base_url": "OIC_IDCS_CLIENT_AUD",
            "client_id": "OIC_IDCS_CLIENT_ID",
            "client_secret": "OIC_IDCS_CLIENT_SECRET",
            "token_url": "OIC_IDCS_URL",
            "instance_id": "OIC_INSTANCE_ID",
            "region": "OIC_REGION",
            "environment": ("OIC_ENVIRONMENT", "test"),
        }
    }

    # Common Oracle operations
    ORACLE_OPERATIONS = {
        "connection_test": {
            "name": "Test Oracle Connection",
            "description": "Verify Oracle database connectivity",
            "timeout": 30,
        },
        "schema_validation": {
            "name": "Validate Schema",
            "description": "Validate Oracle schema structure",
            "timeout": 60,
        },
        "data_extraction": {
            "name": "Extract Data",
            "description": "Extract data from Oracle tables",
            "timeout": 300,
        },
        "data_loading": {
            "name": "Load Data",
            "description": "Load data into Oracle tables",
            "timeout": 600,
        },
        "integration_sync": {
            "name": "Integration Sync",
            "description": "Synchronize data between systems",
            "timeout": 900,
        }
    }

    # WMS-specific table mappings
    WMS_TABLE_MAPPINGS = {
        "inventory": {
            "source_table": "wms_inventory",
            "target_table": "inv_inventory",
            "key_fields": ["item_id", "location_id"],
            "sync_fields": ["quantity", "status", "last_updated"],
        },
        "orders": {
            "source_table": "wms_orders",
            "target_table": "inv_orders",
            "key_fields": ["order_id"],
            "sync_fields": ["status", "priority", "created_date"],
        },
        "shipments": {
            "source_table": "wms_shipments",
            "target_table": "inv_shipments",
            "key_fields": ["shipment_id"],
            "sync_fields": ["carrier", "tracking_number", "ship_date"],
        },
        "receipts": {
            "source_table": "wms_receipts",
            "target_table": "inv_receipts",
            "key_fields": ["receipt_id"],
            "sync_fields": ["received_quantity", "received_date", "status"],
        }
    }

    # OIC integration patterns
    OIC_INTEGRATION_PATTERNS = {
        "rest_inbound": {
            "pattern": "REST -> OIC -> Oracle",
            "trigger": "REST webhook",
            "transformation": "OIC mapper",
            "target": "Oracle database",
        },
        "rest_outbound": {
            "pattern": "Oracle -> OIC -> REST",
            "trigger": "Database event",
            "transformation": "OIC mapper",
            "target": "External REST API",
        },
        "file_inbound": {
            "pattern": "File -> OIC -> Oracle",
            "trigger": "File arrival",
            "transformation": "File adapter + mapper",
            "target": "Oracle database",
        },
        "scheduled_sync": {
            "pattern": "Oracle -> OIC -> External",
            "trigger": "Scheduled process",
            "transformation": "OIC orchestration",
            "target": "Multiple systems",
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.console = Console()
        self.oracle_connections: dict[str, Any] = {}
        self.integration_results: dict[str, Any] = {}

    def load_oracle_config(self, config_type: str) -> dict[str, Any]:
        """Load Oracle configuration from environment variables."""
        if config_type not in self.ORACLE_CONFIGS:
            raise ValueError(f"Unknown config type: {config_type}")

        config_template = self.ORACLE_CONFIGS[config_type]
        config: dict = {}

        for key, value in config_template.items():
            if isinstance(value, tuple):
                env_var, default = value
                config[key] = os.getenv(env_var, default)
                config[key] = os.getenv(value)

        return config

    def test_oracle_connection(self, config_type: str) -> tuple[bool, str]:
        """Test Oracle database connection."""
        try:
            config = self.load_oracle_config(config_type)

            if config_type == "wms":
                # Test Oracle database connection
                import oracledb

                dsn = f"{
                    config['host']}:{
                    config['port']}/{
                    config['service_name']}"
                connection = oracledb.connect(
                    user=config['username'],
                    password=config['password'],
                    dsn=dsn
                )

                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1 FROM DUAL")
                    result = cursor.fetchone()

                connection.close()
                return True, f"Oracle connection successful: {result[0]}"

            if config_type == "oic":
                # Test OIC REST API connection
                import requests

                token_url = f"{config['token_url']}/oauth2/v1/token"
                auth_data = {
                    "grant_type": "client_credentials",
                    "scope": config['base_url']
                }

                response = requests.post(
                    token_url,
                    auth=(config['client_id'], config['client_secret']),
                    data=auth_data,
                    timeout=config.get('timeout', 30)
                )

                if response.status_code == 200:
                    return True, "OIC authentication successful"
                return False, f"OIC authentication failed: {
                    response.status_code}"

        except ImportError as e:
            return False, f"Missing Oracle client library: {e}"
        except Exception as e:
            return False, f"Connection failed: {e}"

    def validate_oracle_schema(
            self, config_type: str, table_name: str) -> tuple[bool, dict[str, Any]]:
        """Validate Oracle schema structure."""
        try:
            config = self.load_oracle_config(config_type)

            if config_type == "wms":
                import oracledb

                dsn = f"{
                    config['host']}:{
                    config['port']}/{
                    config['service_name']}"
                connection = oracledb.connect(
                    user=config['username'],
                    password=config['password'],
                    dsn=dsn
                )

                with connection.cursor() as cursor:
                    # Get table structure
                    cursor.execute("""
                        SELECT column_name, data_type, nullable, data_default
                        FROM all_tab_columns
                        WHERE owner = :schema AND table_name = :table
                        ORDER BY column_id
                    """, schema=config['schema'], table=table_name.upper())

                    columns: list = []
                    for row in cursor.fetchall():
                        columns.append({
                            "name": row[0],
                            "type": row[1],
                            "nullable": row[2] == "Y",
                            "default": row[3]
                        })

                    # Get indexes
                    cursor.execute("""
                        SELECT index_name, column_name, uniqueness
                        FROM all_ind_columns ic
                        JOIN all_indexes i ON ic.index_name = i.index_name
                        WHERE ic.table_owner = :schema AND ic.table_name = :table
                        ORDER BY ic.column_position
                    """, schema=config['schema'], table=table_name.upper())

                    indexes: list = []
                    for row in cursor.fetchall():
                        indexes.append({
                            "name": row[0],
                            "column": row[1],
                            "unique": row[2] == "UNIQUE"
                        })

                connection.close()

                schema_info = {
                    "table_name": table_name,
                    "columns": columns,
                    "indexes": indexes,
                    "column_count": len(columns),
                    "index_count": len(indexes)
                }

                return True, schema_info

        except Exception as e:
            return False, {"error": str(e)}

    def extract_oracle_data(self,
                            config_type: str,
                            table_name: str,
                            conditions: str = None,
                            limit: int = 1000) -> tuple[bool,
                                                        list[dict[str,
                                                                  Any]]]:
        """Extract data from Oracle tables."""
        try:
            config = self.load_oracle_config(config_type)

            if config_type == "wms":
                import oracledb

                dsn = f"{
                    config['host']}:{
                    config['port']}/{
                    config['service_name']}"
                connection = oracledb.connect(
                    user=config['username'],
                    password=config['password'],
                    dsn=dsn
                )

                # Build query
                query = f"SELECT * FROM {config['schema']}.{table_name}"
                if conditions:
                    query += f" WHERE {conditions}"
                query += f" ORDER BY ROWNUM FETCH FIRST {limit} ROWS ONLY"

                with connection.cursor() as cursor:
                    cursor.execute(query)
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()

                    data: list = []
                    for row in rows:
                        record = dict(zip(columns, row, strict=False))
                        # Convert datetime objects to strings
                        for key, value in record.items():
                            if hasattr(value, 'isoformat'):
                                record[key] = value.isoformat()
                        data.append(record)

                connection.close()
                return True, data

        except Exception as e:
            return False, [{"error": str(e)}]

    def load_oracle_data(self,
                         config_type: str,
                         table_name: str,
                         data: list[dict[str,
                                         Any]],
                         mode: str = "insert") -> tuple[bool,
                                                        dict[str,
                                                             Any]]:
        """Load data into Oracle tables."""
        try:
            config = self.load_oracle_config(config_type)

            if config_type == "wms":
                import oracledb

                dsn = f"{
                    config['host']}:{
                    config['port']}/{
                    config['service_name']}"
                connection = oracledb.connect(
                    user=config['username'],
                    password=config['password'],
                    dsn=dsn
                )

                results = {
                    "total_records": len(data),
                    "inserted": 0,
                    "updated": 0,
                    "errors": 0,
                    "error_details": []
                }

                with connection.cursor() as cursor:
                    for record in data:
                        try:
                            if mode == "insert":
                                columns = list(record.keys())
                                placeholders = [f":{col}" for col in columns]
                                query = f"""
                                    INSERT INTO {config['schema']}.{table_name}
                                    ({', '.join(columns)})
                                    VALUES ({', '.join(placeholders)})
                                """
                                cursor.execute(query, record)
                                results["inserted"] += 1

                            elif mode == "upsert":
                                # Implement MERGE statement for upsert
                                # This is a simplified version
                                columns = list(record.keys())
                                key_columns = self._get_key_columns(table_name)

                                merge_query = self._build_merge_query(
                                    table_name, columns, key_columns, config['schema'])
                                cursor.execute(merge_query, record)
                                results["updated"] += 1

                        except Exception as e:
                            results["errors"] += 1
                            results["error_details"].append({
                                "record": record,
                                "error": str(e)
                            })

                connection.commit()
                connection.close()

                return True, results

        except Exception as e:
            return False, {"error": str(e)}

    def _get_key_columns(self, table_name: str) -> list[str]:
        """Get key columns for a table based on mappings."""
        for _mapping_name, mapping in self.WMS_TABLE_MAPPINGS.items():
            if mapping["target_table"] == table_name or mapping["source_table"] == table_name:
                return mapping["key_fields"]
        return ["id"]  # Default fallback

    def _build_merge_query(self, table_name: str, columns: list[str],
                           key_columns: list[str], schema: str) -> str:
        """Build Oracle MERGE query for upsert operations."""
        # Simplified MERGE query builder
        key_conditions = " AND ".join(
            [f"t.{col} = :{col}" for col in key_columns])
        update_assignments = ", ".join(
            [f"{col} = :{col}" for col in columns if col not in key_columns])
        insert_columns = ", ".join(columns)
        insert_values = ", ".join([f":{col}" for col in columns])

        return f"""
            MERGE INTO {schema}.{table_name} t
            USING (SELECT {insert_values} FROM DUAL) s ON ({key_conditions})
            WHEN MATCHED THEN UPDATE SET {update_assignments}
            WHEN NOT MATCHED THEN INSERT ({insert_columns}) VALUES ({insert_values})
        """

    def run_integration_pipeline(
            self, pipeline_name: str, config: dict[str, Any]) -> dict[str, Any]:
        """Run a complete Oracle integration pipeline."""
        pipeline_start = time.time()

        results = {
            "pipeline_name": pipeline_name,
            "start_time": pipeline_start,
            "steps": [],
            "success": True,
            "total_records": 0,
            "errors": []
        }

        try:
            # Step 1: Test connections
            if self.verbose:
                self.console.print(
                    f"[blue]Testing Oracle connections for {pipeline_name}[/blue]")

            for conn_type in config.get("connection_types", ["wms"]):
                success, message = self.test_oracle_connection(conn_type)
                results["steps"].append({
                    "step": f"test_{conn_type}_connection",
                    "success": success,
                    "message": message
                })
                if not success:
                    results["success"] = False
                    results["errors"].append(
                        f"Connection test failed: {message}")

            # Step 2: Schema validation
            if results["success"] and config.get("validate_schema", True):
                if self.verbose:
                    self.console.print("[blue]Validating Oracle schema[/blue]")

                for table in config.get("tables", []):
                    success, schema_info = self.validate_oracle_schema(
                        "wms", table)
                    results["steps"].append({
                        "step": f"validate_schema_{table}",
                        "success": success,
                        "details": schema_info
                    })
                    if not success:
                        results["success"] = False
                        results["errors"].append(
                            f"Schema validation failed for {table}")

            # Step 3: Data extraction
            if results["success"] and config.get("extract_data", True):
                if self.verbose:
                    self.console.print(
                        "[blue]Extracting data from Oracle[/blue]")

                for table in config.get("source_tables", []):
                    conditions = config.get(
                        "extraction_conditions", {}).get(table)
                    limit = config.get("extraction_limit", 1000)

                    success, data = self.extract_oracle_data(
                        "wms", table, conditions, limit)
                    results["steps"].append({
                        "step": f"extract_data_{table}",
                        "success": success,
                        "record_count": len(data) if success else 0
                    })

                    if success:
                        results["total_records"] += len(data)
                        # Store extracted data for next step
                        if "extracted_data" not in results:
                            results["extracted_data"] = {}
                        results["extracted_data"][table] = data
                        results["success"] = False
                        results["errors"].append(
                            f"Data extraction failed for {table}")

            # Step 4: Data transformation (if needed)
            if results["success"] and config.get("transform_data", False):
                if self.verbose:
                    self.console.print("[blue]Transforming data[/blue]")

                # Apply transformations based on configuration
                transform_success = self._apply_data_transformations(
                    results.get("extracted_data", {}),
                    config.get("transformations", {})
                )

                results["steps"].append({
                    "step": "transform_data",
                    "success": transform_success
                })

                if not transform_success:
                    results["success"] = False
                    results["errors"].append("Data transformation failed")

            # Step 5: Data loading
            if results["success"] and config.get("load_data", True):
                if self.verbose:
                    self.console.print("[blue]Loading data to Oracle[/blue]")

                for table, data in results.get("extracted_data", {}).items():
                    target_table = config.get(
                        "table_mappings", {}).get(
                        table, table)
                    load_mode = config.get("load_mode", "insert")

                    success, load_results = self.load_oracle_data(
                        "wms", target_table, data, load_mode)
                    results["steps"].append({
                        "step": f"load_data_{target_table}",
                        "success": success,
                        "details": load_results
                    })

                    if not success:
                        results["success"] = False
                        results["errors"].append(
                            f"Data loading failed for {target_table}")

        except Exception as e:
            results["success"] = False
            results["errors"].append(f"Pipeline execution failed: {e}")

        results["end_time"] = time.time()
        results["duration"] = results["end_time"] - results["start_time"]

        return results

    def _apply_data_transformations(self, data: dict[str, list[dict]],
                                    transformations: dict[str, Any]) -> bool:
        """Apply data transformations based on configuration."""
        try:
            for table_name, table_data in data.items():
                table_transforms = transformations.get(table_name, {})

                for record in table_data:
                    # Apply field mappings
                    if "field_mappings" in table_transforms:
                        for old_field, new_field in table_transforms["field_mappings"].items(
                        ):
                            if old_field in record:
                                record[new_field] = record.pop(old_field)

                    # Apply data type conversions
                    if "type_conversions" in table_transforms:
                        for field, target_type in table_transforms["type_conversions"].items(
                        ):
                            if field in record and record[field] is not None:
                                if target_type == "int":
                                    record[field] = int(record[field])
                                elif target_type == "float":
                                    record[field] = float(record[field])
                                elif target_type == "str":
                                    record[field] = str(record[field])

                    # Apply default values
                    if "default_values" in table_transforms:
                        for field, default_value in table_transforms["default_values"].items(
                        ):
                            if field not in record or record[field] is None:
                                record[field] = default_value

            return True
        except Exception:
            return False

    def analyze(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze files for Oracle integration opportunities."""
        issues: list = []

        # Check for Oracle integration patterns
        if file_path.suffix == ".py":
            lines = content.split("\n")

            for i, line in enumerate(lines, 1):
                line_stripped = line.strip()

                # Check for hardcoded Oracle connections
                if any(
                    pattern in line_stripped for pattern in [
                        "cx_Oracle.connect(",
                        "oracledb.connect("]):
                    if "os.getenv" not in line and "config" not in line:
                        issues.append(
                            Issue(
                                line=i,
                                column=1,
                                code="ORACLE001",
                                message="Hardcoded Oracle connection found",
                                suggestion="Use environment variables or configuration files for Oracle connections"))

                # Check for missing error handling in Oracle operations
                if "cursor.execute(" in line_stripped:
                    # Look for try/except in surrounding lines
                    context_lines = lines[max(0, i - 5):min(len(lines), i + 5)]
                    if not any(
                            "try:" in ctx_line or "except" in ctx_line for ctx_line in context_lines):
                        issues.append(
                            Issue(
                                line=i,
                                column=1,
                                code="ORACLE002",
                                message="Oracle operation without error handling",
                                suggestion="Add try/except block around Oracle operations"))

                # Check for inefficient queries
                if "SELECT *" in line_stripped.upper() and "FROM" in line_stripped.upper():
                    issues.append(
                        Issue(
                            line=i,
                            column=line.find("SELECT"),
                            code="ORACLE003",
                            message="SELECT * query found (potentially inefficient)",
                            suggestion="Specify only required columns in SELECT statements"))

        # Check for configuration files
        elif file_path.name in ["config.json", "config.yaml", ".env"]:
            if "ORACLE" not in content.upper():
                issues.append(Issue(
                    line=1,
                    column=1,
                    code="ORACLE004",
                    message="Oracle configuration missing",
                    suggestion="Add Oracle connection configuration"
                ))

        return issues

    def apply_fixes(self, content: str, issues: list[Issue]) -> str:
        """Apply Oracle integration fixes to content."""
        lines = content.split("\n")

        for issue in issues:
            if issue.code == "ORACLE001":  # Fix hardcoded connections
                line_idx = issue.line - 1
                if line_idx < len(lines):
                    line = lines[line_idx]
                    if "cx_Oracle.connect(" in line or "oracledb.connect(" in line:
                        # Add comment suggesting configuration
                        lines[line_idx] = line + \
                            "  # TODO: Move to configuration"

            elif issue.code == "ORACLE002":  # Add error handling
                line_idx = issue.line - 1
                if line_idx < len(lines):
                    line = lines[line_idx]
                    indent = len(line) - len(line.lstrip())

                    # Wrap in try/except
                    lines[line_idx] = " " * indent + "try:"
                    lines.insert(line_idx + 1,
                                 " " * (indent + 4) + line.strip())
                    lines.insert(line_idx + 2,
                                 " " * indent + "except Exception as e:")
                    lines.insert(line_idx + 3, " " * (indent + 4) +
                                 "logger.error(f'Oracle operation failed: {e}')")
                    lines.insert(line_idx + 4, " " * (indent + 4) + "raise")

        return "\n".join(lines)

    def run_oracle_integration_workflow(
            self, workspace_path: Path = None) -> dict[str, Any]:
        """Run Oracle integration workflow across the workspace."""
        if workspace_path is None:
            workspace_path = Path.cwd()

        if self.verbose:
            self.console.print(
                f"[blue]Running Oracle integration workflow in: {workspace_path}[/blue]")

        # Find Oracle-related projects
        oracle_projects: list = []
        for project_dir in workspace_path.iterdir():
            if project_dir.is_dir() and not project_dir.name.startswith("."):
                if any(oracle_keyword in project_dir.name.lower()
                       for oracle_keyword in ["oracle", "wms", "oic"]):
                    oracle_projects.append(project_dir)

        if self.verbose:
            self.console.print(
                f"[green]Found {
                    len(oracle_projects)} Oracle-related projects[/green]")

        workflow_results = {
            "total_projects": len(oracle_projects),
            "successful_integrations": 0,
            "failed_integrations": 0,
            "project_results": {},
        }

        for project_path in oracle_projects:
            project_name = project_path.name

            if self.verbose:
                self.console.print(
                    f"[yellow]Processing Oracle project: {project_name}[/yellow]")

            try:
                # Determine integration type
                if "wms" in project_name.lower():
                    integration_config = {
                        "connection_types": ["wms"],
                        "tables": ["inventory", "orders", "shipments"],
                        "extract_data": True,
                        "load_mode": "upsert"
                    }
                elif "oic" in project_name.lower():
                    integration_config = {
                        "connection_types": ["oic"],
                        "validate_schema": False,
                        "extract_data": False,
                        "test_endpoints": True
                    }
                    integration_config = {
                        "connection_types": ["wms", "oic"],
                        "basic_test": True
                    }

                # Run integration pipeline
                if not self.dry_run:
                    pipeline_results = self.run_integration_pipeline(
                        project_name, integration_config)

                    if pipeline_results["success"]:
                        workflow_results["successful_integrations"] += 1
                        workflow_results["failed_integrations"] += 1

                    workflow_results["project_results"][project_name] = pipeline_results
                    if self.verbose:
                        self.console.print(
                            f"[cyan][DRY RUN] Would run integration for {project_name}[/cyan]")
                    workflow_results["successful_integrations"] += 1

            except Exception as e:
                workflow_results["project_results"][project_name] = {
                    "success": False,
                    "error": str(e)
                }
                workflow_results["failed_integrations"] += 1
                if self.verbose:
                    self.console.print(
                        f"[red]Error processing {project_name}: {e}[/red]")

        # Show summary
        if self.verbose:
            self._show_integration_summary(workflow_results)

        return workflow_results

    def _show_integration_summary(self, results: dict[str, Any]) -> None:
        """Show Oracle integration summary."""
        # Results table
        table = Table(title="Oracle Integration Results")
        table.add_column("Project", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Type", style="blue")
        table.add_column("Records Processed")

        for project_name, result in results["project_results"].items():
            if isinstance(result, dict) and "success" in result:
                status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
                integration_type = "WMS" if "wms" in project_name.lower(
                ) else "OIC" if "oic" in project_name.lower() else "Mixed"
                records = str(result.get("total_records", "N/A"))
                status = "❌ ERROR"
                integration_type = "Unknown"
                records = "0"

            table.add_row(project_name, status, integration_type, records)

        self.console.print(table)

        # Summary panel
        success_rate = (
            results["successful_integrations"] /
            results["total_projects"] *
            100) if results["total_projects"] > 0 else 0

        panel_text = (
            f"🏢 Oracle Projects: {results['total_projects']}\n"
            f"✅ Successful: {results['successful_integrations']}\n"
            f"❌ Failed: {results['failed_integrations']}\n"
            f"📊 Success Rate: {success_rate:.1f}%"
        )

        panel_style = "green" if success_rate == 100 else "yellow" if success_rate >= 80 else "red"
        self.console.print(
            Panel(
                panel_text,
                title="Oracle Integration Summary",
                border_style=panel_style))

    def run_workspace_oracle_integration(
            self, workspace_path: Path = None) -> bool:
        """Run Oracle integration across the entire workspace."""
        results = self.run_oracle_integration_workflow(workspace_path)
        return results["failed_integrations"] == 0
