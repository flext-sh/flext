"""Generic migration planning engine for flx-ldap.

This module provides sophisticated migration planning and orchestration
capabilities for any LDAP-to-LDAP migration scenario, using tap-ldap
and target-ldap components in the Singer/Meltano ecosystem.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
import logging
from typing import Any, ClassVar

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
class MigrationPhase:
    """Definition of a migration phase."""

    phase_id: str
    name: str
    description: str
    steps: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    estimated_duration: str = "unknown"
    component_responsible: str = "flx-ldap"  # flx-ldap, tap-ldap, target-ldap, ldap-ext
    validation_required: bool = True
    rollback_steps: list[str] = field(default_factory=list)


@dataclass
class MigrationPlan:
    """Complete migration plan definition."""

    plan_id: str
    name: str
    description: str
    source_config: dict[str, Any]
    target_config: dict[str, Any]
    phases: list[MigrationPhase] = field(default_factory=list)
    estimated_total_duration: str = "unknown"
    risk_level: str = "medium"  # low, medium, high, critical
    validation_strategy: dict[str, Any] = field(default_factory=dict)
    rollback_strategy: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    created_by: str = "flx-ldap"


@dataclass
class ComponentCapability:
    """Capability definition for a component."""

    component_name: str
    version: str | None = None
    capabilities: list[str] = field(default_factory=list)
    configuration_schema: dict[str, Any] = field(default_factory=dict)
    available: bool = True
    health_status: str = "unknown"


class MigrationPlanner:
    """Generic migration planner for LDAP migrations.

    This planner orchestrates tap-ldap and target-ldap components
    to create comprehensive migration plans for any LDAP scenario.
    """

    # Singer SDK / Meltano EDK Component responsibilities
    COMPONENT_RESPONSIBILITIES: ClassVar[dict[str, list[str]]] = {
        "tap-ldap": [
            "source_data_extraction",
            "ldif_file_processing",
            "schema_discovery",
            "incremental_extraction",
            "data_validation",
        ],
        "target-ldap": [
            "data_loading",
            "data_transformation",
            "schema_application",
            "data_validation_on_load",
            "dry_run_simulation",
        ],
        "dbt-ldap": [
            "data_modeling",
            "analytics_transformation",
            "data_testing",
            "documentation_generation",
            "incremental_builds",
        ],
        "flx-ldap": [
            "orchestration",
            "migration_planning",
            "component_coordination",
            "progress_tracking",
            "error_handling",
        ],
    }

    # Migration patterns
    MIGRATION_PATTERNS: ClassVar[dict[str, dict[str, Any]]] = {
        "simple_sync": {
            "description": "Simple one-time synchronization",
            "phases": ["extract", "transform", "load", "validate"],
            "complexity": "low",
            "use_cases": ["dev_to_test", "backup_restore", "simple_replication"],
        },
        "incremental_migration": {
            "description": "Incremental migration with state tracking",
            "phases": [
                "initial_extract",
                "delta_extract",
                "transform",
                "load",
                "validate",
            ],
            "complexity": "medium",
            "use_cases": ["live_migration", "continuous_sync", "gradual_cutover"],
        },
        "complex_transformation": {
            "description": "Migration with extensive data transformation",
            "phases": [
                "schema_analysis",
                "extract",
                "complex_transform",
                "validation",
                "load",
                "verify",
            ],
            "complexity": "high",
            "use_cases": ["oracle_to_openldap", "ad_to_ldap", "legacy_migration"],
        },
        "enterprise_migration": {
            "description": "Enterprise-grade migration with full validation",
            "phases": [
                "planning",
                "schema_migration",
                "test_migration",
                "incremental_sync",
                "validation",
                "cutover",
            ],
            "complexity": "critical",
            "use_cases": [
                "production_migration",
                "enterprise_consolidation",
                "vendor_migration",
            ],
        },
    }

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize migration planner."""
        self.config = config or {}
        self.component_capabilities: dict[str, ComponentCapability] = {}

    def detect_component_capabilities(self) -> dict[str, ComponentCapability]:
        """Detect available components and their capabilities.

        Returns:
            Dictionary of component capabilities

        """
        logger.info("Detecting component capabilities")

        capabilities = {}

        # Check tap-ldap
        try:
            import tap_ldap

            capabilities["tap-ldap"] = ComponentCapability(
                component_name="tap-ldap",
                version=getattr(tap_ldap, "__version__", "unknown"),
                capabilities=self.COMPONENT_RESPONSIBILITIES["tap-ldap"],
                available=True,
                health_status="available",
            )
        except ImportError:
            capabilities["tap-ldap"] = ComponentCapability(
                component_name="tap-ldap",
                available=False,
                health_status="not_installed",
            )

        # Check target-ldap
        try:
            import target_ldap

            capabilities["target-ldap"] = ComponentCapability(
                component_name="target-ldap",
                version=getattr(target_ldap, "__version__", "unknown"),
                capabilities=self.COMPONENT_RESPONSIBILITIES["target-ldap"],
                available=True,
                health_status="available",
            )
        except ImportError:
            capabilities["target-ldap"] = ComponentCapability(
                component_name="target-ldap",
                available=False,
                health_status="not_installed",
            )

        # Check dbt-ldap (Meltano EDK component)
        try:
            import dbt  # type: ignore[import-untyped]

            capabilities["dbt-ldap"] = ComponentCapability(
                component_name="dbt-ldap",
                version=getattr(dbt, "__version__", "unknown"),
                capabilities=self.COMPONENT_RESPONSIBILITIES["dbt-ldap"],
                available=True,
                health_status="available",
            )
        except ImportError:
            capabilities["dbt-ldap"] = ComponentCapability(
                component_name="dbt-ldap", available=False, health_status="optional"
            )

        # flx-ldap itself
        capabilities["flx-ldap"] = ComponentCapability(
            component_name="flx-ldap",
            capabilities=self.COMPONENT_RESPONSIBILITIES["flx-ldap"],
            available=True,
            health_status="active",
        )

        self.component_capabilities = capabilities
        return capabilities

    def analyze_migration_requirements(
        self,
        source_config: dict[str, Any],
        target_config: dict[str, Any],
        migration_options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Analyze migration requirements and recommend approach.

        Args:
            source_config: Source LDAP configuration
            target_config: Target LDAP configuration
            migration_options: Additional migration options

        Returns:
            Migration requirements analysis

        """
        logger.info("Analyzing migration requirements")

        options = migration_options or {}

        analysis = {
            "source_analysis": self._analyze_source_requirements(source_config),
            "target_analysis": self._analyze_target_requirements(target_config),
            "complexity_assessment": "medium",
            "recommended_pattern": "simple_sync",
            "estimated_duration": "2-4 hours",
            "risk_factors": [],
            "component_requirements": {},
            "validation_strategy": {},
        }

        # Determine complexity based on requirements
        complexity_factors = []

        # Check for schema customizations
        if options.get("custom_schema", False):
            complexity_factors.append("custom_schema")
            analysis["risk_factors"].append(
                "Custom schema elements require careful migration"
            )

        # Check for large datasets
        estimated_entries = options.get("estimated_entries", 0)
        if estimated_entries > 100000:
            complexity_factors.append("large_dataset")
            analysis["risk_factors"].append("Large dataset requires batch processing")

        # Check for transformation requirements
        if options.get("data_transformation_required", False):
            complexity_factors.append("data_transformation")
            analysis["risk_factors"].append("Data transformation increases complexity")

        # Check for live migration
        if options.get("live_migration", False):
            complexity_factors.append("live_migration")
            analysis["risk_factors"].append("Live migration requires careful timing")

        # Determine recommended pattern
        if not complexity_factors:
            analysis["recommended_pattern"] = "simple_sync"
            analysis["complexity_assessment"] = "low"
            analysis["estimated_duration"] = "1-2 hours"
        elif len(complexity_factors) <= 2:
            analysis["recommended_pattern"] = "incremental_migration"
            analysis["complexity_assessment"] = "medium"
            analysis["estimated_duration"] = "4-8 hours"
        elif len(complexity_factors) <= 3:
            analysis["recommended_pattern"] = "complex_transformation"
            analysis["complexity_assessment"] = "high"
            analysis["estimated_duration"] = "1-2 days"
        else:
            analysis["recommended_pattern"] = "enterprise_migration"
            analysis["complexity_assessment"] = "critical"
            analysis["estimated_duration"] = "3-5 days"

        # Define component requirements for Singer/Meltano ecosystem
        pattern = self.MIGRATION_PATTERNS[analysis["recommended_pattern"]]
        analysis["component_requirements"] = {
            "tap-ldap": "required",
            "target-ldap": "required",
            "dbt-ldap": (
                "recommended"
                if pattern["complexity"] in ["medium", "high", "critical"]
                else "optional"
            ),
            "ldap-core-shared": "recommended",
        }

        # Define validation strategy
        analysis["validation_strategy"] = {
            "pre_migration": [
                "connectivity_check",
                "permissions_check",
                "schema_validation",
            ],
            "during_migration": ["progress_monitoring", "error_tracking"],
            "post_migration": [
                "data_integrity_check",
                "count_validation",
                "functional_testing",
            ],
        }

        return analysis

    def create_migration_plan(
        self,
        source_config: dict[str, Any],
        target_config: dict[str, Any],
        migration_pattern: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> MigrationPlan:
        """Create comprehensive migration plan.

        Args:
            source_config: Source LDAP configuration
            target_config: Target LDAP configuration
            migration_pattern: Migration pattern to use
            options: Additional options

        Returns:
            Complete migration plan

        """
        logger.info("Creating migration plan with pattern: %s", migration_pattern)

        # Analyze requirements if pattern not specified
        if not migration_pattern:
            analysis = self.analyze_migration_requirements(
                source_config, target_config, options
            )
            migration_pattern = analysis["recommended_pattern"]

        pattern_config = self.MIGRATION_PATTERNS.get(
            migration_pattern, self.MIGRATION_PATTERNS["simple_sync"]
        )

        plan_id = f"migration_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"

        plan = MigrationPlan(
            plan_id=plan_id,
            name=f"LDAP Migration - {pattern_config['description']}",
            description=(
                f"Migration from {source_config.get('host', 'source')} "
                f"to {target_config.get('host', 'target')}"
            ),
            source_config=source_config,
            target_config=target_config,
            estimated_total_duration=self._estimate_duration(
                migration_pattern, options
            ),
            risk_level=pattern_config["complexity"],
        )

        # Create phases based on pattern
        phases = self._create_phases_for_pattern(migration_pattern, options or {})
        plan.phases = phases

        # Add validation and rollback strategies
        plan.validation_strategy = self._create_validation_strategy(migration_pattern)
        plan.rollback_strategy = self._create_rollback_strategy(migration_pattern)

        return plan

    def _analyze_source_requirements(
        self, source_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze source LDAP requirements."""
        return {
            "host": source_config.get("host"),
            "port": source_config.get("port", 389),
            "ssl_required": source_config.get("use_ssl", False),
            "authentication": (
                "required" if source_config.get("bind_dn") else "anonymous"
            ),
            "base_dn": source_config.get("base_dn"),
            "estimated_complexity": "medium",
        }

    def _analyze_target_requirements(
        self, target_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze target LDAP requirements."""
        return {
            "host": target_config.get("host"),
            "port": target_config.get("port", 389),
            "ssl_required": target_config.get("use_ssl", False),
            "authentication": (
                "required" if target_config.get("bind_dn") else "anonymous"
            ),
            "base_dn": target_config.get("base_dn"),
            "write_permissions": "required",
            "estimated_complexity": "medium",
        }

    def _create_phases_for_pattern(
        self, pattern: str, options: dict[str, Any]
    ) -> list[MigrationPhase]:
        """Create migration phases for specific pattern."""
        phases = []

        if pattern == "simple_sync":
            phases = [
                MigrationPhase(
                    phase_id="pre_validation",
                    name="Pre-Migration Validation",
                    description="Validate source and target connectivity",
                    component_responsible="flx-ldap",
                    steps=[
                        "Test source LDAP connectivity",
                        "Test target LDAP connectivity",
                        "Validate permissions",
                        "Check available disk space",
                    ],
                    estimated_duration="15 minutes",
                ),
                MigrationPhase(
                    phase_id="extract",
                    name="Data Extraction",
                    description="Extract data from source LDAP",
                    component_responsible="tap-ldap",
                    steps=[
                        "Configure tap-ldap for source",
                        "Discover source schema",
                        "Extract all entries",
                        "Validate extracted data",
                    ],
                    dependencies=["pre_validation"],
                    estimated_duration="30-60 minutes",
                ),
                MigrationPhase(
                    phase_id="load",
                    name="Data Loading",
                    description="Load data to target LDAP",
                    component_responsible="target-ldap",
                    steps=[
                        "Configure target-ldap",
                        "Enable transformation if needed",
                        "Load data in batches",
                        "Monitor load progress",
                    ],
                    dependencies=["extract"],
                    estimated_duration="30-60 minutes",
                ),
                MigrationPhase(
                    phase_id="validation",
                    name="Migration Validation",
                    description="Validate migration success",
                    component_responsible="flx-ldap",
                    steps=[
                        "Compare entry counts",
                        "Validate sample entries",
                        "Test LDAP operations",
                        "Generate migration report",
                    ],
                    dependencies=["load"],
                    estimated_duration="15-30 minutes",
                ),
            ]

        elif pattern == "incremental_migration":
            phases = [
                MigrationPhase(
                    phase_id="initial_sync",
                    name="Initial Synchronization",
                    description="Perform initial full sync",
                    component_responsible="flx-ldap",
                    steps=[
                        "Full extraction with state tracking",
                        "Transform and load initial dataset",
                        "Establish sync baseline",
                    ],
                    estimated_duration="2-4 hours",
                ),
                MigrationPhase(
                    phase_id="incremental_sync",
                    name="Incremental Updates",
                    description="Process incremental changes",
                    component_responsible="tap-ldap",
                    steps=[
                        "Monitor source for changes",
                        "Extract delta changes",
                        "Apply changes to target",
                        "Update sync state",
                    ],
                    dependencies=["initial_sync"],
                    estimated_duration="ongoing",
                ),
            ]

        elif pattern == "complex_transformation":
            phases = [
                MigrationPhase(
                    phase_id="schema_analysis",
                    name="Schema Analysis",
                    description="Analyze source and target schemas",
                    component_responsible="flx-ldap",
                    steps=[
                        "Extract source schema",
                        "Analyze target compatibility",
                        "Plan schema transformations",
                        "Create transformation rules",
                    ],
                    estimated_duration="2-4 hours",
                ),
                MigrationPhase(
                    phase_id="transformation_setup",
                    name="Transformation Configuration",
                    description="Configure data transformations",
                    component_responsible="target-ldap",
                    steps=[
                        "Configure transformation engine",
                        "Set up attribute mappings",
                        "Configure object class conversions",
                        "Test transformation rules",
                    ],
                    dependencies=["schema_analysis"],
                    estimated_duration="1-2 hours",
                ),
                MigrationPhase(
                    phase_id="migration_execution",
                    name="Migration Execution",
                    description="Execute migration with transformations",
                    component_responsible="flx-ldap",
                    steps=[
                        "Extract with schema discovery",
                        "Apply transformations",
                        "Load transformed data",
                        "Validate transformations",
                    ],
                    dependencies=["transformation_setup"],
                    estimated_duration="4-8 hours",
                ),
            ]

        else:  # enterprise_migration
            phases = [
                MigrationPhase(
                    phase_id="planning",
                    name="Migration Planning",
                    description="Comprehensive migration planning",
                    component_responsible="flx-ldap",
                    estimated_duration="1-2 days",
                ),
                MigrationPhase(
                    phase_id="test_migration",
                    name="Test Migration",
                    description="Execute test migration",
                    component_responsible="flx-ldap",
                    dependencies=["planning"],
                    estimated_duration="4-8 hours",
                ),
                MigrationPhase(
                    phase_id="production_migration",
                    name="Production Migration",
                    description="Execute production migration",
                    component_responsible="flx-ldap",
                    dependencies=["test_migration"],
                    estimated_duration="8-16 hours",
                ),
            ]

        return phases

    def _estimate_duration(self, pattern: str, options: dict[str, Any] | None) -> str:
        """Estimate total migration duration."""
        base_durations = {
            "simple_sync": "2-4 hours",
            "incremental_migration": "4-8 hours",
            "complex_transformation": "1-2 days",
            "enterprise_migration": "3-5 days",
        }

        return base_durations.get(pattern, "unknown")

    def _create_validation_strategy(self, pattern: str) -> dict[str, Any]:
        """Create validation strategy for migration pattern."""
        return {
            "pre_migration": [
                "connectivity_validation",
                "permission_validation",
                "schema_compatibility_check",
            ],
            "during_migration": [
                "progress_monitoring",
                "error_rate_monitoring",
                "performance_monitoring",
            ],
            "post_migration": [
                "data_integrity_validation",
                "count_validation",
                "functional_testing",
                "performance_validation",
            ],
        }

    def _create_rollback_strategy(self, pattern: str) -> dict[str, Any]:
        """Create rollback strategy for migration pattern."""
        return {
            "automatic_triggers": [
                "error_rate_threshold_exceeded",
                "data_corruption_detected",
                "system_performance_degraded",
            ],
            "rollback_steps": [
                "stop_migration_process",
                "preserve_migration_logs",
                "restore_target_to_pre_migration_state",
                "validate_rollback_success",
            ],
            "manual_intervention_required": pattern
            in ["complex_transformation", "enterprise_migration"],
        }

    def validate_migration_plan(self, plan: MigrationPlan) -> dict[str, Any]:
        """Validate migration plan completeness and feasibility.

        Args:
            plan: Migration plan to validate

        Returns:
            Validation report

        """
        validation_report = {
            "valid": True,
            "issues": [],
            "warnings": [],
            "recommendations": [],
        }

        # Check component availability
        required_components = ["tap-ldap", "target-ldap"]
        for component in required_components:
            if component not in self.component_capabilities:
                self.detect_component_capabilities()

            capability = self.component_capabilities.get(component)
            if not capability or not capability.available:
                validation_report["issues"].append(
                    f"Required component '{component}' not available"
                )
                validation_report["valid"] = False

        # Check phase dependencies
        phase_ids = {phase.phase_id for phase in plan.phases}
        for phase in plan.phases:
            for dependency in phase.dependencies:
                if dependency not in phase_ids:
                    validation_report["issues"].append(
                        f"Phase '{phase.phase_id}' depends on missing phase '{dependency}'"
                    )
                    validation_report["valid"] = False

        # Check configuration completeness
        if not plan.source_config.get("host"):
            validation_report["issues"].append("Source host not configured")
            validation_report["valid"] = False

        if not plan.target_config.get("host"):
            validation_report["issues"].append("Target host not configured")
            validation_report["valid"] = False

        # Add recommendations
        if plan.risk_level in ["high", "critical"]:
            validation_report["recommendations"].append(
                "Consider test migration before production"
            )

        if len(plan.phases) > 5:
            validation_report["recommendations"].append(
                "Complex migration plan - ensure adequate monitoring"
            )

        return validation_report
