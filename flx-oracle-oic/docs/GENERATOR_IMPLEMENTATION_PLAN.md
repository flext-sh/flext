# tap-oic Generator Implementation Plan

> **Date**: June 15, 2025
> **Version**: 3.0 Implementation Plan
> **Status**: READY FOR IMPLEMENTATION

## Executive Summary

This document provides the detailed implementation plan for extending tap-oic with integration generation and workflow creation capabilities. The plan leverages existing code architecture and introduces new components for programmatic integration creation.

## Table of Contents

1. [Implementation Architecture](#implementation-architecture)
2. [Phase 1: Foundation Components](#phase-1-foundation-components)
3. [Phase 2: Generator Engine](#phase-2-generator-engine)
4. [Phase 3: Workflow Creator](#phase-3-workflow-creator)
5. [Phase 4: Testing and Validation](#phase-4-testing-and-validation)
6. [Code Integration Points](#code-integration-points)
7. [Example Implementations](#example-implementations)

## Implementation Architecture

### New Module Structure

```
tap_oic/
├── generator/
│   ├── __init__.py
│   ├── core.py                 # Core generator engine
│   ├── iar_builder.py          # IAR file creation
│   ├── templates/
│   │   ├── __init__.py
│   │   ├── base.py            # Base template class
│   │   ├── database_to_rest.py
│   │   ├── rest_to_rest.py
│   │   ├── file_to_database.py
│   │   └── kafka_to_rest.py
│   ├── validators/
│   │   ├── __init__.py
│   │   ├── schema.py          # Schema validation
│   │   └── constraints.py     # OIC constraint validation
│   └── transformers/
│       ├── __init__.py
│       ├── mapper.py          # Field mapping
│       └── enricher.py        # Data enrichment
├── workflow/
│   ├── __init__.py            # (Already exists)
│   ├── creator.py             # New workflow creator
│   ├── dependency_manager.py  # Dependency resolution
│   └── executor.py            # Workflow execution
└── idl/
    ├── __init__.py
    ├── parser.py              # Parse YAML/JSON to objects
    ├── compiler.py            # Compile to OIC format
    └── schema.py              # IDL schema definitions
```

## Phase 1: Foundation Components

### 1.1 Integration Definition Language (IDL)

```python
# tap_oic/idl/schema.py
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class AdapterType(str, Enum):
    """Supported OIC adapter types"""
    ORACLE_DB = "oracle-db"
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    REST = "rest"
    SOAP = "soap"
    SALESFORCE = "salesforce"
    FILE = "file"
    FTP = "ftp"
    KAFKA = "kafka"

class SourceDefinition(BaseModel):
    """Source configuration for integration"""
    adapter: AdapterType
    connection: str = Field(..., description="Connection name in OIC")
    properties: Dict[str, Any] = Field(default_factory=dict)

    # Database specific
    query: Optional[str] = None
    table: Optional[str] = None

    # REST specific
    endpoint: Optional[str] = None
    method: Optional[str] = None

    # File specific
    directory: Optional[str] = None
    pattern: Optional[str] = None

class TransformationDefinition(BaseModel):
    """Transformation configuration"""
    mappings: List[Dict[str, Any]] = Field(default_factory=list)
    enrichments: List[Dict[str, Any]] = Field(default_factory=list)
    filters: List[str] = Field(default_factory=list)

class TargetDefinition(BaseModel):
    """Target configuration for integration"""
    adapter: AdapterType
    connection: str
    properties: Dict[str, Any] = Field(default_factory=dict)

    # REST specific
    endpoint: Optional[str] = None
    method: Optional[str] = None

    # Database specific
    table: Optional[str] = None
    operation: Optional[str] = "insert"  # insert, update, upsert

class IntegrationDefinition(BaseModel):
    """Complete integration definition"""
    api_version: str = "oic/v1"
    kind: str = "Integration"
    metadata: Dict[str, Any]
    spec: Dict[str, Any]

    class Config:
        extra = "allow"
```

### 1.2 IAR File Builder

```python
# tap_oic/generator/iar_builder.py
import zipfile
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, Optional
import tempfile
import shutil

class IARBuilder:
    """Build OIC Integration Archive (.iar) files"""

    def __init__(self):
        self.temp_dir = None

    def create_iar(
        self,
        integration_name: str,
        integration_def: Dict[str, Any],
        output_path: str
    ) -> str:
        """Create an IAR file from integration definition"""

        # Create temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            self.temp_dir = Path(temp_dir)

            # Create IAR structure
            self._create_directory_structure()

            # Generate integration files
            self._generate_integration_xml(integration_name, integration_def)
            self._generate_metadata_xml(integration_name, integration_def)
            self._generate_connections_xml(integration_def)
            self._generate_transformations(integration_def)

            # Create IAR archive
            iar_path = self._create_archive(output_path)

        return iar_path

    def _create_directory_structure(self):
        """Create OIC IAR directory structure"""
        dirs = [
            "ics",
            "ics/project",
            "ics/project/connections",
            "ics/project/integrations",
            "ics/project/transformations",
            "ics/project/lookups",
            "META-INF"
        ]

        for dir_path in dirs:
            (self.temp_dir / dir_path).mkdir(parents=True, exist_ok=True)

    def _generate_integration_xml(self, name: str, definition: Dict[str, Any]):
        """Generate integration.xml file"""
        root = ET.Element("integration")
        root.set("name", name)
        root.set("version", "01.00.0000")

        # Add source configuration
        source = ET.SubElement(root, "source")
        source_def = definition.get("source", {})
        source.set("adapter", source_def.get("adapter", ""))
        source.set("connection", source_def.get("connection", ""))

        # Add target configuration
        target = ET.SubElement(root, "target")
        target_def = definition.get("target", {})
        target.set("adapter", target_def.get("adapter", ""))
        target.set("connection", target_def.get("connection", ""))

        # Add transformations
        if "transformation" in definition:
            transform = ET.SubElement(root, "transformation")
            transform.set("ref", f"{name}_transformation.xsl")

        # Write XML file
        tree = ET.ElementTree(root)
        integration_path = self.temp_dir / f"ics/project/integrations/{name}.xml"
        tree.write(integration_path, encoding="utf-8", xml_declaration=True)

    def _generate_metadata_xml(self, name: str, definition: Dict[str, Any]):
        """Generate metadata.xml file"""
        root = ET.Element("metadata")

        # Add integration metadata
        integration = ET.SubElement(root, "integration")
        integration.set("name", name)
        integration.set("description", definition.get("description", ""))
        integration.set("pattern", definition.get("pattern", "scheduled"))

        # Add properties
        properties = ET.SubElement(integration, "properties")
        for key, value in definition.get("properties", {}).items():
            prop = ET.SubElement(properties, "property")
            prop.set("name", key)
            prop.set("value", str(value))

        # Write metadata file
        tree = ET.ElementTree(root)
        metadata_path = self.temp_dir / "META-INF/metadata.xml"
        tree.write(metadata_path, encoding="utf-8", xml_declaration=True)

    def _generate_connections_xml(self, definition: Dict[str, Any]):
        """Generate connections configuration"""
        # Implementation for connection definitions
        pass

    def _generate_transformations(self, definition: Dict[str, Any]):
        """Generate transformation files"""
        if "transformation" not in definition:
            return

        transform_def = definition["transformation"]

        # Generate XSLT for transformations
        xslt = self._create_xslt_transformation(transform_def)

        # Write transformation file
        transform_path = self.temp_dir / "ics/project/transformations/transformation.xsl"
        with open(transform_path, "w") as f:
            f.write(xslt)

    def _create_xslt_transformation(self, transform_def: Dict[str, Any]) -> str:
        """Create XSLT transformation from definition"""
        # Basic XSLT template
        xslt = '''<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <output>
'''

        # Add field mappings
        for mapping in transform_def.get("mappings", []):
            source_field = mapping.get("source")
            target_field = mapping.get("target")
            xslt += f'''            <{target_field}>
                <xsl:value-of select="//{source_field}"/>
            </{target_field}>
'''

        xslt += '''        </output>
    </xsl:template>
</xsl:stylesheet>'''

        return xslt

    def _create_archive(self, output_path: str) -> str:
        """Create ZIP archive from temporary directory"""
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in self.temp_dir.rglob('*'):
                if file_path.is_file():
                    arcname = str(file_path.relative_to(self.temp_dir))
                    zipf.write(file_path, arcname)

        return output_path
```

## Phase 2: Generator Engine

### 2.1 Core Generator

```python
# tap_oic/generator/core.py
from typing import Dict, Any, Optional, List
from pathlib import Path
import yaml
import json

from ..idl.schema import IntegrationDefinition
from ..idl.parser import IDLParser
from .iar_builder import IARBuilder
from .templates.base import BaseTemplate
from .validators.schema import SchemaValidator
from .validators.constraints import ConstraintValidator

class IntegrationGenerator:
    """Core integration generator engine"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.iar_builder = IARBuilder()
        self.schema_validator = SchemaValidator()
        self.constraint_validator = ConstraintValidator()
        self.templates = self._load_templates()

    def generate_from_yaml(self, yaml_path: str, output_dir: str = ".") -> str:
        """Generate integration from YAML configuration"""
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)

        return self.generate(config, output_dir)

    def generate_from_json(self, json_path: str, output_dir: str = ".") -> str:
        """Generate integration from JSON configuration"""
        with open(json_path, 'r') as f:
            config = json.load(f)

        return self.generate(config, output_dir)

    def generate(self, config: Dict[str, Any], output_dir: str = ".") -> str:
        """Generate integration from configuration dictionary"""

        # Parse and validate configuration
        integration = self._parse_configuration(config)
        self._validate_integration(integration)

        # Generate integration name
        integration_name = integration.metadata.get("name", "generated_integration")

        # Convert to OIC format
        oic_definition = self._convert_to_oic_format(integration)

        # Build IAR file
        output_path = Path(output_dir) / f"{integration_name}.iar"
        iar_path = self.iar_builder.create_iar(
            integration_name,
            oic_definition,
            str(output_path)
        )

        return iar_path

    def generate_from_template(
        self,
        template_name: str,
        parameters: Dict[str, Any],
        output_dir: str = "."
    ) -> str:
        """Generate integration from pre-built template"""

        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")

        template = self.templates[template_name]
        config = template.generate_config(parameters)

        return self.generate(config, output_dir)

    def generate_from_singer(
        self,
        tap: str,
        tap_config: Dict[str, Any],
        target: str,
        target_config: Dict[str, Any],
        transformations: Optional[List[Dict[str, Any]]] = None,
        output_dir: str = "."
    ) -> str:
        """Generate OIC integration from Singer tap/target combination"""

        # Map Singer components to OIC adapters
        source_adapter = self._map_tap_to_adapter(tap)
        target_adapter = self._map_target_to_adapter(target)

        # Create integration configuration
        config = {
            "apiVersion": "oic/v1",
            "kind": "Integration",
            "metadata": {
                "name": f"{tap}_to_{target}",
                "description": f"Integration from {tap} to {target}"
            },
            "spec": {
                "source": {
                    "adapter": source_adapter,
                    "connection": f"{tap}_connection",
                    **self._convert_tap_config(tap, tap_config)
                },
                "target": {
                    "adapter": target_adapter,
                    "connection": f"{target}_connection",
                    **self._convert_target_config(target, target_config)
                }
            }
        }

        # Add transformations if provided
        if transformations:
            config["spec"]["transformation"] = {
                "mappings": transformations
            }

        return self.generate(config, output_dir)

    def _parse_configuration(self, config: Dict[str, Any]) -> IntegrationDefinition:
        """Parse configuration into integration definition"""
        parser = IDLParser()
        return parser.parse(config)

    def _validate_integration(self, integration: IntegrationDefinition):
        """Validate integration against OIC constraints"""
        # Schema validation
        self.schema_validator.validate(integration)

        # OIC constraint validation
        self.constraint_validator.validate(integration)

    def _convert_to_oic_format(self, integration: IntegrationDefinition) -> Dict[str, Any]:
        """Convert integration definition to OIC format"""
        # Implementation to convert IDL to OIC-specific format
        return integration.dict()

    def _load_templates(self) -> Dict[str, BaseTemplate]:
        """Load available templates"""
        from .templates.database_to_rest import DatabaseToRestTemplate
        from .templates.rest_to_rest import RestToRestTemplate
        from .templates.file_to_database import FileToDatabaseTemplate
        from .templates.kafka_to_rest import KafkaToRestTemplate

        return {
            "database-to-rest": DatabaseToRestTemplate(),
            "rest-to-rest": RestToRestTemplate(),
            "file-to-database": FileToDatabaseTemplate(),
            "kafka-to-rest": KafkaToRestTemplate()
        }

    def _map_tap_to_adapter(self, tap: str) -> str:
        """Map Singer tap to OIC adapter"""
        mapping = {
            "tap-mysql": "mysql",
            "tap-postgres": "postgresql",
            "tap-oracle": "oracle-db",
            "tap-salesforce": "salesforce",
            "tap-rest-api": "rest",
            "tap-kafka": "kafka",
            "tap-s3-csv": "file"
        }
        return mapping.get(tap, "rest")

    def _map_target_to_adapter(self, target: str) -> str:
        """Map Singer target to OIC adapter"""
        mapping = {
            "target-postgres": "postgresql",
            "target-mysql": "mysql",
            "target-oracle": "oracle-db",
            "target-snowflake": "rest",  # Via REST API
            "target-rest-api": "rest",
            "target-kafka": "kafka",
            "target-s3": "file"
        }
        return mapping.get(target, "rest")

    def _convert_tap_config(self, tap: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Convert tap configuration to OIC source properties"""
        # Implementation specific to each tap type
        if tap == "tap-mysql":
            return {
                "query": config.get("query", "SELECT * FROM table"),
                "properties": {
                    "host": config.get("host"),
                    "port": config.get("port", 3306),
                    "database": config.get("database")
                }
            }
        # Add more tap conversions
        return {}

    def _convert_target_config(self, target: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Convert target configuration to OIC target properties"""
        # Implementation specific to each target type
        if target == "target-postgres":
            return {
                "table": config.get("default_target_schema", "public") + "." + config.get("table", "data"),
                "operation": "insert",
                "properties": {
                    "host": config.get("host"),
                    "port": config.get("port", 5432),
                    "database": config.get("dbname")
                }
            }
        # Add more target conversions
        return {}
```

## Phase 3: Workflow Creator

### 3.1 Workflow Definition and Creation

```python
# tap_oic/workflow/creator.py
from typing import Dict, Any, List, Optional
from enum import Enum
import networkx as nx
from ..generator.core import IntegrationGenerator
from ..idl.schema import IntegrationDefinition

class WorkflowStep:
    """Represents a step in the workflow"""

    def __init__(
        self,
        name: str,
        integration: str,
        condition: Optional[str] = None,
        depends_on: Optional[List[str]] = None,
        parallel: bool = False
    ):
        self.name = name
        self.integration = integration
        self.condition = condition
        self.depends_on = depends_on or []
        self.parallel = parallel

class WorkflowCreator:
    """Create and manage complex workflows"""

    def __init__(self):
        self.generator = IntegrationGenerator()
        self.steps: Dict[str, WorkflowStep] = {}
        self.graph = nx.DiGraph()

    def create_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create workflow from configuration"""

        # Parse workflow definition
        workflow_name = workflow_config["metadata"]["name"]
        steps = workflow_config["spec"]["steps"]

        # Build workflow graph
        for step_config in steps:
            step = WorkflowStep(**step_config)
            self.add_step(step)

        # Validate workflow
        self._validate_workflow()

        # Generate workflow integrations
        workflow_integrations = self._generate_workflow_integrations()

        # Create orchestration integration
        orchestration = self._create_orchestration_integration(
            workflow_name,
            workflow_integrations
        )

        return orchestration

    def add_step(self, step: WorkflowStep):
        """Add step to workflow"""
        self.steps[step.name] = step
        self.graph.add_node(step.name, step=step)

        # Add dependencies
        for dependency in step.depends_on:
            self.graph.add_edge(dependency, step.name)

    def _validate_workflow(self):
        """Validate workflow for cycles and missing dependencies"""
        # Check for cycles
        if not nx.is_directed_acyclic_graph(self.graph):
            raise ValueError("Workflow contains cycles")

        # Check all dependencies exist
        for step_name, step in self.steps.items():
            for dep in step.depends_on:
                if dep not in self.steps:
                    raise ValueError(f"Step '{step_name}' depends on unknown step '{dep}'")

    def _generate_workflow_integrations(self) -> List[Dict[str, Any]]:
        """Generate individual integrations for workflow steps"""
        integrations = []

        # Get topological order
        execution_order = list(nx.topological_sort(self.graph))

        for step_name in execution_order:
            step = self.steps[step_name]

            # Generate integration for step
            integration = {
                "name": f"{step_name}_integration",
                "integration_ref": step.integration,
                "condition": step.condition,
                "parallel": step.parallel,
                "dependencies": step.depends_on
            }

            integrations.append(integration)

        return integrations

    def _create_orchestration_integration(
        self,
        workflow_name: str,
        integrations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create main orchestration integration"""

        orchestration_config = {
            "apiVersion": "oic/v1",
            "kind": "WorkflowOrchestration",
            "metadata": {
                "name": workflow_name,
                "description": f"Orchestration for {workflow_name} workflow"
            },
            "spec": {
                "pattern": "orchestration",
                "steps": []
            }
        }

        # Build orchestration steps
        for integration in integrations:
            step = {
                "name": integration["name"],
                "type": "integration",
                "integration": integration["integration_ref"]
            }

            # Add condition if present
            if integration["condition"]:
                step["condition"] = integration["condition"]

            # Add parallel flag
            if integration["parallel"]:
                step["parallel"] = True

            orchestration_config["spec"]["steps"].append(step)

        return orchestration_config
```

## Phase 4: Testing and Validation

### 4.1 Integration Testing Framework

```python
# tap_oic/generator/tests/test_generator.py
import pytest
from unittest.mock import Mock, patch
from tap_oic.generator.core import IntegrationGenerator
from tap_oic.generator.iar_builder import IARBuilder

class TestIntegrationGenerator:
    """Test integration generator functionality"""

    def test_generate_from_yaml(self, tmp_path):
        """Test generating integration from YAML"""
        yaml_content = """
apiVersion: oic/v1
kind: Integration
metadata:
  name: test-integration
spec:
  source:
    adapter: oracle-db
    connection: test-db
    query: SELECT * FROM customers
  target:
    adapter: rest
    connection: test-api
    endpoint: /customers
    method: POST
"""
        yaml_file = tmp_path / "integration.yaml"
        yaml_file.write_text(yaml_content)

        generator = IntegrationGenerator()
        iar_path = generator.generate_from_yaml(str(yaml_file), str(tmp_path))

        assert iar_path.endswith(".iar")
        assert Path(iar_path).exists()

    def test_generate_from_singer(self, tmp_path):
        """Test generating from Singer components"""
        generator = IntegrationGenerator()

        iar_path = generator.generate_from_singer(
            tap="tap-mysql",
            tap_config={
                "host": "localhost",
                "database": "test",
                "user": "user"
            },
            target="target-postgres",
            target_config={
                "host": "localhost",
                "dbname": "analytics"
            },
            output_dir=str(tmp_path)
        )

        assert Path(iar_path).exists()

    def test_iar_builder(self, tmp_path):
        """Test IAR file builder"""
        builder = IARBuilder()

        integration_def = {
            "source": {
                "adapter": "oracle-db",
                "connection": "test-connection"
            },
            "target": {
                "adapter": "rest",
                "connection": "api-connection"
            }
        }

        output_path = tmp_path / "test.iar"
        iar_path = builder.create_iar(
            "test-integration",
            integration_def,
            str(output_path)
        )

        assert Path(iar_path).exists()
        assert zipfile.is_zipfile(iar_path)
```

## Code Integration Points

### 1. CLI Extension

```python
# tap_oic/cli_unified.py (additions)

@cli.group()
def generate():
    """Generate OIC integrations"""
    pass

@generate.command()
@click.option('--config', type=click.Path(exists=True), required=True)
@click.option('--output', type=click.Path(), default='.')
@click.option('--format', type=click.Choice(['yaml', 'json']), default='yaml')
def integration(config, output, format):
    """Generate integration from configuration file"""
    generator = IntegrationGenerator()

    if format == 'yaml':
        iar_path = generator.generate_from_yaml(config, output)
    else:
        iar_path = generator.generate_from_json(config, output)

    click.echo(f"Generated integration: {iar_path}")

@generate.command()
@click.option('--tap', required=True)
@click.option('--tap-config', type=click.Path(exists=True))
@click.option('--target', required=True)
@click.option('--target-config', type=click.Path(exists=True))
@click.option('--output', type=click.Path(), default='.')
def from_singer(tap, tap_config, target, target_config, output):
    """Generate integration from Singer tap/target"""
    generator = IntegrationGenerator()

    # Load configurations
    with open(tap_config) as f:
        tap_cfg = json.load(f)
    with open(target_config) as f:
        target_cfg = json.load(f)

    iar_path = generator.generate_from_singer(
        tap=tap,
        tap_config=tap_cfg,
        target=target,
        target_config=target_cfg,
        output_dir=output
    )

    click.echo(f"Generated integration: {iar_path}")

@cli.group()
def workflow():
    """Manage workflows"""
    pass

@workflow.command()
@click.option('--config', type=click.Path(exists=True), required=True)
@click.option('--output', type=click.Path(), default='.')
def create(config, output):
    """Create workflow from configuration"""
    creator = WorkflowCreator()

    with open(config) as f:
        workflow_config = yaml.safe_load(f)

    workflow = creator.create_workflow(workflow_config)

    # Generate workflow IAR
    generator = IntegrationGenerator()
    iar_path = generator.generate(workflow, output)

    click.echo(f"Generated workflow: {iar_path}")
```

### 2. Configuration Updates

```python
# tap_oic/config.py (additions)

# Generator configuration
CONFIG_SCHEMA["generator_enabled"] = Property(
    False,
    description="Enable integration generation features"
)

CONFIG_SCHEMA["template_directory"] = Property(
    None,
    description="Directory containing custom templates"
)

CONFIG_SCHEMA["iar_output_directory"] = Property(
    "./generated",
    description="Output directory for generated IAR files"
)

CONFIG_SCHEMA["validation_mode"] = Property(
    "strict",
    description="Validation mode: strict, permissive, or none"
)
```

## Example Implementations

### Example 1: Database to REST Integration

```yaml
# examples/database-to-rest.yaml
apiVersion: oic/v1
kind: Integration
metadata:
  name: customer-sync
  description: Sync customers from database to REST API
spec:
  source:
    adapter: oracle-db
    connection: PROD_DB
    query: |
      SELECT
        customer_id,
        first_name,
        last_name,
        email,
        created_date,
        modified_date
      FROM customers
      WHERE modified_date > :last_sync_time

  transformation:
    mappings:
      - source: customer_id
        target: id
      - source: first_name + ' ' + last_name
        target: full_name
      - source: email
        target: contact_email

    enrichments:
      - field: country
        value: "US"
      - field: source_system
        value: "ORACLE_DB"

  target:
    adapter: rest
    connection: API_GATEWAY
    endpoint: https://api.example.com/v1/customers
    method: POST
    headers:
      Content-Type: application/json
      X-API-Key: ${API_KEY}

  error_handling:
    retry_count: 3
    retry_interval: 60
    error_endpoint: https://api.example.com/v1/errors

  schedule:
    frequency: "*/15 * * * *"  # Every 15 minutes
    timezone: "UTC"
```

### Example 2: Complex Workflow

```yaml
# examples/order-processing-workflow.yaml
apiVersion: oic/v1
kind: Workflow
metadata:
  name: order-processing
  description: Complete order processing workflow
spec:
  steps:
    - name: validate-order
      integration: order-validation

    - name: check-inventory
      integration: inventory-check
      condition: "steps['validate-order'].status == 'valid'"
      depends_on: [validate-order]

    - name: reserve-inventory
      integration: inventory-reservation
      condition: "steps['check-inventory'].available == true"
      depends_on: [check-inventory]

    - name: process-payment
      integration: payment-processor
      depends_on: [reserve-inventory]

    - name: create-shipment
      integration: shipping-service
      depends_on: [process-payment]
      parallel: true

    - name: send-confirmation
      integration: notification-service
      depends_on: [process-payment]
      parallel: true

    - name: update-analytics
      integration: analytics-updater
      depends_on: [create-shipment, send-confirmation]

  error_handling:
    on_error: rollback
    notification: admin@example.com
```

### Example 3: Singer to OIC

```python
# examples/singer_to_oic.py
from tap_oic.generator import IntegrationGenerator

# Create generator
generator = IntegrationGenerator()

# Generate MySQL to Snowflake integration
iar_path = generator.generate_from_singer(
    tap="tap-mysql",
    tap_config={
        "host": "mysql.example.com",
        "port": 3306,
        "user": "reader",
        "password": "${MYSQL_PASSWORD}",
        "database": "sales"
    },
    target="target-snowflake",
    target_config={
        "account": "myaccount.snowflakecomputing.com",
        "database": "ANALYTICS",
        "warehouse": "COMPUTE_WH",
        "username": "loader",
        "password": "${SNOWFLAKE_PASSWORD}"
    },
    transformations=[
        {
            "type": "rename",
            "mappings": {
                "customer_id": "cust_id",
                "order_date": "purchase_date"
            }
        },
        {
            "type": "filter",
            "condition": "status != 'cancelled'"
        },
        {
            "type": "enrich",
            "fields": {
                "source_system": "mysql_sales",
                "extraction_timestamp": "${CURRENT_TIMESTAMP}"
            }
        }
    ]
)

print(f"Generated integration: {iar_path}")

# Deploy to OIC
from tap_oic import OICManagementClient

client = OICManagementClient(config)
result = client.import_integration_archive(iar_path)
print(f"Deployed integration: {result['id']}")
```

## Summary

This implementation plan provides:

1. **Complete architecture** for integration generation
2. **Detailed code examples** for all components
3. **Integration with existing** tap-oic codebase
4. **Testing framework** for validation
5. **Real-world examples** of usage

The plan leverages the existing tap-oic architecture while adding new capabilities for programmatic integration creation, making tap-oic a comprehensive platform for Oracle Integration Cloud management.
