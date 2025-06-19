"""Advanced schema analysis and intelligence for flx-ldap.

This module provides sophisticated schema discovery, analysis, and migration
planning capabilities extracted and enhanced from client-a-oud-mig.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
import logging
import re
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from pathlib import Path

# Import from ldap-core-shared if available
try:
    # Import only what we actually use
    # Currently no imports are used, so we just check availability
    import ldap_core_shared  # noqa: F401

    LDAP_CORE_AVAILABLE = True
except ImportError:
    LDAP_CORE_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class AttributeDefinition:
    """Definition of an LDAP attribute."""

    name: str
    oid: str | None = None
    syntax: str | None = None
    description: str | None = None
    single_valued: bool = False
    equality_rule: str | None = None
    ordering_rule: str | None = None
    substring_rule: str | None = None
    usage: str = "userApplications"
    is_custom: bool = True
    source_defined: bool = False
    target_compatible: bool | None = None


@dataclass
class ObjectClassDefinition:
    """Definition of an LDAP object class."""

    name: str
    oid: str | None = None
    description: str | None = None
    superior: list[str] = field(default_factory=list)
    structural: bool = True
    must_attributes: list[str] = field(default_factory=list)
    may_attributes: list[str] = field(default_factory=list)
    is_custom: bool = True
    source_defined: bool = False
    target_compatible: bool | None = None


@dataclass
class SchemaCompatibilityReport:
    """Report on schema compatibility between source and target."""

    compatible: bool
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    custom_attributes: list[AttributeDefinition] = field(default_factory=list)
    custom_object_classes: list[ObjectClassDefinition] = field(default_factory=list)
    migration_requirements: list[str] = field(default_factory=list)
    estimated_effort: str = "low"  # low, medium, high, critical


@dataclass
class SchemaAnalysisResult:
    """Complete schema analysis result."""

    source_schema: dict[str, Any]
    target_schema: dict[str, Any] | None = None
    compatibility_report: SchemaCompatibilityReport | None = None
    migration_plan: dict[str, Any] | None = None
    analysis_timestamp: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )
    recommendations: list[str] = field(default_factory=list)


class SchemaAnalyzer:
    """Advanced schema analyzer for LDAP migrations.

    Provides sophisticated schema discovery, analysis, and compatibility
    checking capabilities extracted from client-a-oud-mig.
    """

    # Standard LDAP attributes and object classes
    STANDARD_ATTRIBUTES: ClassVar[set[str]] = {
        # Core LDAP attributes
        "cn",
        "sn",
        "givenName",
        "displayName",
        "description",
        "mail",
        "telephoneNumber",
        "facsimileTelephoneNumber",
        "mobile",
        "physicalDeliveryOfficeName",
        "title",
        "department",
        "manager",
        "employeeID",
        "employeeNumber",
        "uid",
        "uidNumber",
        "gidNumber",
        "homeDirectory",
        "loginShell",
        "gecos",
        "userPassword",
        # Organizational attributes
        "o",
        "ou",
        "organizationName",
        "organizationalUnitName",
        "street",
        "l",
        "st",
        "postalCode",
        "c",
        "countryName",
        "localityName",
        "stateOrProvinceName",
        # Group attributes
        "member",
        "memberOf",
        "memberUid",
        "uniqueMember",  # System attributes
        "objectClass",
        "dn",
        "distinguishedName",
        "entryDN",
        "hasSubordinates",
        "numSubordinates",
        "subschemaSubentry",
        "createTimestamp",
        "modifyTimestamp",
        "creatorsName",
        "modifiersName",
        "entryUUID",
        "entryCSN",
        # Internet attributes
        "userCertificate",
        "cACertificate",
        "jpegPhoto",
        "audio",
        "userSMIMECertificate",
    }

    STANDARD_OBJECT_CLASSES: ClassVar[set[str]] = {
        # Person classes
        "person",
        "organizationalPerson",
        "inetOrgPerson",
        "posixAccount",
        "shadowAccount",
        # Group classes
        "group",
        "groupOfNames",
        "groupOfUniqueNames",
        "posixGroup",
        "groupOfURLs",
        # Organizational classes
        "organization",
        "organizationalUnit",
        "domain",
        "dcObject",
        "locality",
        "country",
        "organizationalRole",
        # System classes
        "top",
        "alias",
        "referral",
        "extensibleObject",
        "subschema",
    }

    ORACLE_SPECIFIC_PREFIXES: ClassVar[list[str]] = [
        "orcl",
        "oracle",
        "odi",
        "oud",
        "oid",
        "ovd",
        "oaam",
        "oim",
    ]

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize schema analyzer."""
        self.config = config or {}
        self.analysis_cache: dict[str, SchemaAnalysisResult] = {}

    def analyze_ldap_schema(
        self, connection_config: dict[str, Any]
    ) -> SchemaAnalysisResult:
        """Analyze schema from LDAP server connection.

        Args:
            connection_config: LDAP connection configuration

        Returns:
            Complete schema analysis result

        """
        cache_key = f"{connection_config.get('host')}:{connection_config.get('port')}"

        if cache_key in self.analysis_cache:
            logger.info("Using cached schema analysis for %s", cache_key)
            return self.analysis_cache[cache_key]

        logger.info("Analyzing LDAP schema for %s", cache_key)

        try:
            schema_data = self._extract_schema_from_ldap(connection_config)

            result = SchemaAnalysisResult(
                source_schema=schema_data,
                recommendations=self._generate_schema_recommendations(schema_data),
            )

            # Cache the result
            self.analysis_cache[cache_key] = result

            return result

        except Exception as e:
            logger.error("Failed to analyze schema: %s", e)
            # Return basic result with error info
            return SchemaAnalysisResult(
                source_schema={"error": str(e)},
                recommendations=[f"Schema analysis failed: {e}"],
            )

    def analyze_catalog_schema(self, catalog: dict[str, Any]) -> SchemaAnalysisResult:
        """Analyze schema from tap catalog.

        Args:
            catalog: Singer catalog dictionary

        Returns:
            Schema analysis result

        """
        logger.info("Analyzing schema from catalog")

        schema_data = self._extract_schema_from_catalog(catalog)

        return SchemaAnalysisResult(
            source_schema=schema_data,
            recommendations=self._generate_schema_recommendations(schema_data),
        )

    def compare_schemas(
        self,
        source_result: SchemaAnalysisResult,
        target_connection_config: dict[str, Any],
    ) -> SchemaCompatibilityReport:
        """Compare source and target schemas for compatibility.

        Args:
            source_result: Source schema analysis result
            target_connection_config: Target LDAP connection config

        Returns:
            Compatibility report

        """
        logger.info("Comparing schemas for compatibility")

        # Analyze target schema
        target_result = self.analyze_ldap_schema(target_connection_config)
        source_result.target_schema = target_result.source_schema

        # Compare schemas
        compatibility_report = self._compare_schema_definitions(
            source_result.source_schema, target_result.source_schema
        )

        source_result.compatibility_report = compatibility_report

        return compatibility_report

    def generate_migration_plan(
        self, analysis_result: SchemaAnalysisResult
    ) -> dict[str, Any]:
        """Generate detailed migration plan based on schema analysis.

        Args:
            analysis_result: Schema analysis result

        Returns:
            Detailed migration plan

        """
        logger.info("Generating schema migration plan")

        compatibility = analysis_result.compatibility_report

        plan = {
            "migration_id": f"schema_migration_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
            "analysis_summary": {
                "custom_attributes": (
                    len(compatibility.custom_attributes) if compatibility else 0
                ),
                "custom_object_classes": (
                    len(compatibility.custom_object_classes) if compatibility else 0
                ),
                "compatibility_issues": (
                    len(compatibility.issues) if compatibility else 0
                ),
                "estimated_effort": (
                    compatibility.estimated_effort if compatibility else "unknown"
                ),
            },
            "phases": [],
            "validation_steps": [],
            "rollback_plan": [],
        }

        # Phase 1: Pre-migration validation
        plan["phases"].append(
            {
                "phase": 1,
                "name": "Pre-migration Validation",
                "description": "Validate source and target environments",
                "steps": [
                    "Backup source schema",
                    "Verify target LDAP connectivity",
                    "Check target LDAP permissions",
                    "Validate schema modification rights",
                ],
                "estimated_duration": "1-2 hours",
            }
        )

        # Phase 2: Custom schema elements migration
        if compatibility and (
            compatibility.custom_attributes or compatibility.custom_object_classes
        ):
            plan["phases"].append(
                {
                    "phase": 2,
                    "name": "Custom Schema Migration",
                    "description": "Migrate custom attributes and object classes",
                    "steps": self._generate_schema_migration_steps(compatibility),
                    "estimated_duration": "2-4 hours",
                }
            )

        # Phase 3: Schema validation
        plan["phases"].append(
            {
                "phase": 3,
                "name": "Schema Validation",
                "description": "Validate migrated schema elements",
                "steps": [
                    "Verify custom attributes are accessible",
                    "Verify custom object classes are usable",
                    "Test attribute syntax validation",
                    "Validate object class hierarchy",
                ],
                "estimated_duration": "30-60 minutes",
            }
        )

        # Add validation steps
        plan["validation_steps"] = [
            "Verify all custom attributes migrated successfully",
            "Confirm object class definitions match source",
            "Test creation of entries with custom schema",
            "Validate attribute value constraints",
        ]

        # Add rollback plan
        plan["rollback_plan"] = [
            "Remove custom object classes in reverse dependency order",
            "Remove custom attributes",
            "Restore original schema if needed",
            "Verify system stability",
        ]

        analysis_result.migration_plan = plan
        return plan

    def _extract_schema_from_ldap(
        self, connection_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Extract schema information from LDAP server.

        This would connect to the LDAP server and extract schema definitions.
        For now, we'll create a mock implementation.
        """
        # In a real implementation, this would:
        # 1. Connect to LDAP server using connection_config
        # 2. Query subschemaSubentry
        # 3. Extract attributeTypes and objectClasses
        # 4. Parse LDAP schema definitions

        # Mock schema data for demonstration
        return {
            "attributes": {
                "customEmployeeID": {
                    "oid": "1.3.6.1.4.1.12345.1.1.1",
                    "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
                    "single_valued": True,
                    "description": "Custom employee identifier",
                },
                "customDepartmentCode": {
                    "oid": "1.3.6.1.4.1.12345.1.1.2",
                    "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
                    "single_valued": True,
                    "description": "Department code",
                },
            },
            "object_classes": {
                "customEmployee": {
                    "oid": "1.3.6.1.4.1.12345.1.2.1",
                    "superior": ["inetOrgPerson"],
                    "structural": True,
                    "must": ["customEmployeeID"],
                    "may": ["customDepartmentCode"],
                    "description": "Custom employee object class",
                }
            },
            "connection_info": {
                "host": connection_config.get("host"),
                "port": connection_config.get("port"),
                "extracted_at": datetime.now(UTC).isoformat(),
            },
        }

    def _extract_schema_from_catalog(self, catalog: dict[str, Any]) -> dict[str, Any]:
        """Extract schema information from Singer catalog."""
        schema_data = {
            "attributes": {},
            "object_classes": set(),
            "streams": {},
            "extracted_from": "singer_catalog",
        }

        for stream in catalog.get("streams", []):
            stream_name = stream.get("stream")
            stream_schema = stream.get("schema", {})
            properties = stream_schema.get("properties", {})

            schema_data["streams"][stream_name] = {
                "properties": list(properties.keys()),
                "property_count": len(properties),
            }

            # Analyze properties for custom attributes
            for prop_name, prop_def in properties.items():
                if prop_name not in self.STANDARD_ATTRIBUTES:
                    schema_data["attributes"][prop_name] = {
                        "type": prop_def.get("type", "string"),
                        "description": prop_def.get("description"),
                        "found_in_stream": stream_name,
                        "is_custom": True,
                    }

                # Extract object classes if available
                if prop_name == "objectClass":
                    enum_values = prop_def.get("enum", [])
                    for oc in enum_values:
                        if oc not in self.STANDARD_OBJECT_CLASSES:
                            schema_data["object_classes"].add(oc)

        # Convert set to list for JSON serialization
        schema_data["object_classes"] = list(schema_data["object_classes"])

        return schema_data

    def _compare_schema_definitions(
        self, source_schema: dict[str, Any], target_schema: dict[str, Any]
    ) -> SchemaCompatibilityReport:
        """Compare source and target schema definitions."""
        report = SchemaCompatibilityReport(compatible=True)

        source_attrs = source_schema.get("attributes", {})
        target_attrs = target_schema.get("attributes", {})

        source_ocs = source_schema.get("object_classes", {})
        target_ocs = target_schema.get("object_classes", {})

        # Check attribute compatibility
        for attr_name, attr_def in source_attrs.items():
            if attr_name not in target_attrs:
                # Custom attribute not in target
                custom_attr = AttributeDefinition(
                    name=attr_name,
                    oid=attr_def.get("oid"),
                    syntax=attr_def.get("syntax"),
                    description=attr_def.get("description"),
                    single_valued=attr_def.get("single_valued", False),
                    source_defined=True,
                    target_compatible=False,
                )
                report.custom_attributes.append(custom_attr)
                report.issues.append(
                    f"Custom attribute '{attr_name}' not found in target"
                )
                report.compatible = False

        # Check object class compatibility
        for oc_name, oc_def in source_ocs.items():
            if oc_name not in target_ocs:
                # Custom object class not in target
                custom_oc = ObjectClassDefinition(
                    name=oc_name,
                    oid=oc_def.get("oid"),
                    description=oc_def.get("description"),
                    superior=oc_def.get("superior", []),
                    structural=oc_def.get("structural", True),
                    must_attributes=oc_def.get("must", []),
                    may_attributes=oc_def.get("may", []),
                    source_defined=True,
                    target_compatible=False,
                )
                report.custom_object_classes.append(custom_oc)
                report.issues.append(
                    f"Custom object class '{oc_name}' not found in target"
                )
                report.compatible = False

        # Determine migration requirements
        if report.custom_attributes or report.custom_object_classes:
            report.migration_requirements.append("Schema migration required")

            if (
                len(report.custom_attributes) > 10
                or len(report.custom_object_classes) > 5
            ):
                report.estimated_effort = "high"
            elif (
                len(report.custom_attributes) > 5
                or len(report.custom_object_classes) > 2
            ):
                report.estimated_effort = "medium"
            else:
                report.estimated_effort = "low"

        # Add Oracle-specific warnings
        oracle_attrs = [
            attr
            for attr in source_attrs
            if any(
                attr.lower().startswith(prefix)
                for prefix in self.ORACLE_SPECIFIC_PREFIXES
            )
        ]

        if oracle_attrs:
            report.warnings.append(
                f"Found {len(oracle_attrs)} Oracle-specific attributes that may need transformation"
            )

        return report

    def _generate_schema_migration_steps(
        self, compatibility: SchemaCompatibilityReport
    ) -> list[str]:
        """Generate specific schema migration steps."""
        steps = []

        if compatibility.custom_attributes:
            steps.extend(
                [
                    f"Export {len(compatibility.custom_attributes)} custom attribute definitions",
                    "Convert attribute syntax to target format",
                    "Import custom attributes to target schema",
                ]
            )

        if compatibility.custom_object_classes:
            steps.extend(
                [
                    f"Export {len(compatibility.custom_object_classes)} "
                    "custom object class definitions",
                    "Resolve object class dependencies",
                    "Import custom object classes in dependency order",
                ]
            )

        steps.extend(
            [
                "Verify schema consistency",
                "Test sample entry creation",
                "Update schema cache if needed",
            ]
        )

        return steps

    def _generate_schema_recommendations(
        self, schema_data: dict[str, Any]
    ) -> list[str]:
        """Generate recommendations based on schema analysis."""
        recommendations = []

        custom_attrs = schema_data.get("attributes", {})
        custom_ocs = schema_data.get("object_classes", [])

        if custom_attrs:
            recommendations.append(
                f"Found {len(custom_attrs)} custom attributes - plan schema migration carefully"
            )

        if custom_ocs:
            recommendations.append(
                f"Found {len(custom_ocs)} custom object classes - verify dependencies"
            )

        # Check for Oracle-specific elements
        oracle_elements = [
            attr_name
            for attr_name in custom_attrs
            if any(
                attr_name.lower().startswith(prefix)
                for prefix in self.ORACLE_SPECIFIC_PREFIXES
            )
        ]

        if oracle_elements:
            recommendations.append(
                f"Oracle-specific elements detected: {oracle_elements[:3]}... "
                "- consider transformation rules"
            )

        # Performance recommendations
        if len(custom_attrs) > 20:
            recommendations.append(
                "Large number of custom attributes - consider batch migration approach"
            )

        if not custom_attrs and not custom_ocs:
            recommendations.append(
                "Standard schema detected - migration should be straightforward"
            )

        return recommendations

    def extract_ldif_schema(self, ldif_file_path: Path) -> dict[str, Any]:
        """Extract schema information from LDIF file.

        Args:
            ldif_file_path: Path to LDIF file

        Returns:
            Schema information extracted from LDIF

        """
        logger.info("Extracting schema from LDIF file: %s", ldif_file_path)

        schema_data = {
            "attributes_found": set(),
            "object_classes_found": set(),
            "entry_types": defaultdict(int),
            "attribute_usage": defaultdict(int),
            "file_info": {
                "path": str(ldif_file_path),
                "size_bytes": (
                    ldif_file_path.stat().st_size if ldif_file_path.exists() else 0
                ),
                "analyzed_at": datetime.now(UTC).isoformat(),
            },
        }

        if not ldif_file_path.exists():
            logger.error("LDIF file not found: %s", ldif_file_path)
            return schema_data

        try:
            with ldif_file_path.open("r", encoding="utf-8") as f:
                current_entry = {}
                entry_count = 0

                for _line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # Skip comments and empty lines
                    if not line or line.startswith("#"):
                        continue

                    # Check for entry separator
                    if line.startswith("dn:"):
                        # Process previous entry if exists
                        if current_entry:
                            self._process_ldif_entry_for_schema(
                                current_entry, schema_data
                            )
                            entry_count += 1

                        # Start new entry
                        current_entry = {"dn": line[3:].strip()}
                        continue

                    # Parse attribute line
                    if ":" in line:
                        attr_name, attr_value = line.split(":", 1)
                        attr_name = attr_name.strip()
                        attr_value = attr_value.strip()

                        # Handle base64 values
                        if attr_value.startswith(":"):
                            attr_value = attr_value[
                                1:
                            ].strip()  # Remove second colon for base64

                        if attr_name not in current_entry:
                            current_entry[attr_name] = []
                        current_entry[attr_name].append(attr_value)

                # Process last entry
                if current_entry:
                    self._process_ldif_entry_for_schema(current_entry, schema_data)
                    entry_count += 1

                schema_data["file_info"]["total_entries"] = entry_count

        except Exception as e:
            logger.error("Error processing LDIF file: %s", e)
            schema_data["error"] = str(e)

        # Convert sets to lists for JSON serialization
        schema_data["attributes_found"] = list(schema_data["attributes_found"])
        schema_data["object_classes_found"] = list(schema_data["object_classes_found"])
        schema_data["entry_types"] = dict(schema_data["entry_types"])
        schema_data["attribute_usage"] = dict(schema_data["attribute_usage"])

        return schema_data

    def _process_ldif_entry_for_schema(
        self, entry: dict[str, Any], schema_data: dict[str, Any]
    ) -> None:
        """Process a single LDIF entry for schema extraction."""
        # Track all attributes
        for attr_name in entry:
            if attr_name != "dn":
                schema_data["attributes_found"].add(attr_name)
                schema_data["attribute_usage"][attr_name] += 1

        # Track object classes
        object_classes = entry.get("objectClass", [])
        for oc in object_classes:
            schema_data["object_classes_found"].add(oc)

        # Classify entry type
        entry_type = self._classify_ldif_entry(object_classes)
        schema_data["entry_types"][entry_type] += 1

    def _classify_ldif_entry(self, object_classes: list[str]) -> str:
        """Classify LDIF entry based on object classes."""
        oc_lower = [oc.lower() for oc in object_classes]

        if "person" in oc_lower or "inetorgperson" in oc_lower:
            return "user"
        if "groupofnames" in oc_lower or "groupofuniquenames" in oc_lower:
            return "group"
        if "organizationalunit" in oc_lower:
            return "organizational_unit"
        if "organization" in oc_lower:
            return "organization"
        if "domain" in oc_lower:
            return "domain"
        if any(oc.lower().startswith("orcl") for oc in oc_lower):
            return "oracle_specific"
        return "other"

    def validate_schema_consistency(
        self, analysis_result: SchemaAnalysisResult
    ) -> dict[str, Any]:
        """Validate schema consistency and generate validation report.

        Args:
            analysis_result: Schema analysis result to validate

        Returns:
            Validation report

        """
        validation_report = {
            "valid": True,
            "issues": [],
            "warnings": [],
            "checks_performed": [],
            "validation_timestamp": datetime.now(UTC).isoformat(),
        }

        source_schema = analysis_result.source_schema
        compatibility = analysis_result.compatibility_report

        # Check 1: Verify custom attributes have valid syntax
        custom_attrs = source_schema.get("attributes", {})
        for attr_name, attr_def in custom_attrs.items():
            validation_report["checks_performed"].append(
                f"validate_attribute_{attr_name}"
            )

            # Check for valid OID
            oid = attr_def.get("oid")
            if not oid or not re.match(r"^\d+(\.\d+)*$", oid):
                validation_report["issues"].append(
                    f"Attribute '{attr_name}' has invalid OID: {oid}"
                )
                validation_report["valid"] = False

        # Check 2: Verify object class dependencies
        if compatibility:
            for oc_def in compatibility.custom_object_classes:
                validation_report["checks_performed"].append(
                    f"validate_objectclass_{oc_def.name}"
                )

                # Check superior classes
                for superior in oc_def.superior:
                    if superior not in self.STANDARD_OBJECT_CLASSES:
                        validation_report["warnings"].append(
                            f"Object class '{oc_def.name}' extends custom class '{superior}'"
                        )

        # Check 3: Verify schema completeness
        if not custom_attrs and not (
            compatibility and compatibility.custom_object_classes
        ):
            validation_report["warnings"].append("No custom schema elements detected")

        return validation_report
