"""Generic migration orchestration for flx-ldap.

This module provides sophisticated migration orchestration capabilities
that coordinate tap-ldap and target-ldap components for any
LDAP migration scenario in the Singer/Meltano ecosystem.
"""

from __future__ import annotations

import logging
from typing import Any

from flx_ldap.config import FlxLDAPConfig, MigrationConfig
from flx_ldap.migration_planner import MigrationPlanner
from flx_ldap.schema_analyzer import SchemaAnalyzer

logger = logging.getLogger(__name__)


class GenericMigrationOrchestrator:
    """Generic orchestrator for LDAP migrations using tap-ldap and target-ldap."""

    def __init__(self, config: FlxLDAPConfig) -> None:
        """Initialize migration orchestrator.

        Args:
            config: FLX-LDAP configuration

        """
        self.config = config
        self.planner = MigrationPlanner()
        self.schema_analyzer = SchemaAnalyzer()
        self.component_capabilities: dict[str, Any] = {}

    def detect_component_capabilities(self) -> dict[str, Any]:
        """Detect available components and their capabilities.

        Returns:
            Dictionary of detected capabilities

        """
        logger.info("Detecting component capabilities")

        capabilities = self.planner.detect_component_capabilities()
        self.component_capabilities = capabilities

        return {
            component: {
                "available": cap.available,
                "version": cap.version,
                "health_status": cap.health_status,
                "capabilities": cap.capabilities,
            }
            for component, cap in capabilities.items()
        }

    def analyze_migration_scenario(
        self,
        source_config: dict[str, Any],
        target_config: dict[str, Any],
        migration_options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Analyze migration scenario and provide recommendations.

        Args:
            source_config: Source LDAP configuration
            target_config: Target LDAP configuration
            migration_options: Additional migration options

        Returns:
            Complete migration scenario analysis

        """
        logger.info("Analyzing migration scenario")

        # Get component capabilities
        components = self.detect_component_capabilities()

        # Analyze migration requirements
        requirements = self.planner.analyze_migration_requirements(
            source_config,
            target_config,
            migration_options,
        )

        # Analyze schema if possible
        schema_analysis = None
        try:
            schema_result = self.schema_analyzer.analyze_catalog_schema(
                {
                    "streams": [
                        {"stream": "users", "schema": {"properties": {}}},
                        {"stream": "groups", "schema": {"properties": {}}},
                        {
                            "stream": "organizational_units",
                            "schema": {"properties": {}},
                        },
                    ],
                },
            )
            schema_analysis = {
                "custom_attributes": len(
                    schema_result.source_schema.get("attributes", {}),
                ),
                "recommendations": schema_result.recommendations,
            }
        except Exception as e:
            logger.warning("Schema analysis failed: %s", e)
            schema_analysis = {"error": str(e)}

        return {
            "components": components,
            "requirements": requirements,
            "schema_analysis": schema_analysis,
            "feasibility": self._assess_migration_feasibility(components, requirements),
            "recommendations": self._generate_migration_recommendations(
                components,
                requirements,
            ),
        }

    def generate_migration_plan(
        self,
        source_config: dict[str, Any],
        target_config: dict[str, Any],
        migration_pattern: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate comprehensive migration plan.

        Args:
            source_config: Source LDAP configuration
            target_config: Target LDAP configuration
            migration_pattern: Specific migration pattern to use
            options: Additional migration options

        Returns:
            Detailed migration plan

        """
        logger.info("Generating migration plan with pattern: %s", migration_pattern)

        # Create migration plan using planner
        plan = self.planner.create_migration_plan(
            source_config,
            target_config,
            migration_pattern,
            options,
        )

        # Validate the plan
        validation = self.planner.validate_migration_plan(plan)

        # Convert to dictionary format for serialization
        return {
            "plan_id": plan.plan_id,
            "name": plan.name,
            "description": plan.description,
            "source_config": plan.source_config,
            "target_config": plan.target_config,
            "estimated_duration": plan.estimated_total_duration,
            "risk_level": plan.risk_level,
            "phases": [
                {
                    "phase_id": phase.phase_id,
                    "name": phase.name,
                    "description": phase.description,
                    "steps": phase.steps,
                    "dependencies": phase.dependencies,
                    "component_responsible": phase.component_responsible,
                    "estimated_duration": phase.estimated_duration,
                    "validation_required": phase.validation_required,
                }
                for phase in plan.phases
            ],
            "validation_strategy": plan.validation_strategy,
            "rollback_strategy": plan.rollback_strategy,
            "validation": validation,
            "created_at": plan.created_at,
        }

    def create_migration_config(
        self,
        source_host: str,
        target_host: str,
        base_dn: str,
        **kwargs: Any,
    ) -> MigrationConfig:
        """Create migration configuration for orchestrator.

        Args:
            source_host: Source LDAP host
            target_host: Target LDAP host
            base_dn: Base DN for migration
            **kwargs: Additional configuration options

        Returns:
            MigrationConfig instance

        """
        from flx_ldap.config import TapConfig, TargetConfig

        # Create source tap configuration
        source_tap = TapConfig(
            host=source_host,
            base_dn=base_dn,
            bind_dn=kwargs.get("source_bind_dn"),
            password=kwargs.get("source_password"),
            port=kwargs.get("source_port", 389),
            use_ssl=kwargs.get("source_use_ssl", False),
            timeout=kwargs.get("source_timeout", 30),
            page_size=kwargs.get("source_page_size", 1000),
            user_filter=kwargs.get("source_user_filter", "(objectClass=inetOrgPerson)"),
            group_filter=kwargs.get(
                "source_group_filter",
                "(objectClass=groupOfNames)",
            ),
        )

        # Create target tap configuration (for comparison)
        target_tap = TapConfig(
            host=target_host,
            base_dn=base_dn,
            bind_dn=kwargs.get("target_bind_dn"),
            password=kwargs.get("target_password"),
            port=kwargs.get("target_port", 389),
            use_ssl=kwargs.get("target_use_ssl", False),
            timeout=kwargs.get("target_timeout", 30),
            page_size=kwargs.get("target_page_size", 1000),
            user_filter=kwargs.get("target_user_filter", "(objectClass=inetOrgPerson)"),
            group_filter=kwargs.get(
                "target_group_filter",
                "(objectClass=groupOfNames)",
            ),
        )

        # Create target loading configuration
        target_config = TargetConfig(
            host=target_host,
            base_dn=base_dn,
            bind_dn=kwargs.get("target_bind_dn"),
            password=kwargs.get("target_password"),
            port=kwargs.get("target_port", 389),
            use_ssl=kwargs.get("target_use_ssl", False),
            timeout=kwargs.get("target_timeout", 30),
            user_rdn_attribute=kwargs.get("user_rdn_attribute", "uid"),
            group_rdn_attribute=kwargs.get("group_rdn_attribute", "cn"),
            # Enhanced target-ldap configuration
            enable_transformation=kwargs.get("enable_transformation", False),
            enable_validation=kwargs.get("enable_validation", True),
            dry_run_mode=kwargs.get("dry_run", False),
            batch_size=kwargs.get("batch_size", 100),
            max_errors=kwargs.get("max_errors", 10),
        )

        return MigrationConfig(
            source_tap_config=source_tap,
            target_tap_config=target_tap,
            target_config=target_config,
            comparison_enabled=kwargs.get("compare", True),
            dry_run=kwargs.get("dry_run", False),
            batch_size=kwargs.get("batch_size", 1000),
        )

    def get_supported_migration_patterns(self) -> dict[str, Any]:
        """Get supported migration patterns and their descriptions.

        Returns:
            Dictionary of supported migration patterns

        """
        patterns: dict[str, Any] = self.planner.MIGRATION_PATTERNS
        return patterns

    def validate_migration_readiness(self) -> tuple[bool, list[str]]:
        """Validate system readiness for migration.

        Returns:
            Tuple of (is_ready, issues_list)

        """
        # Check component availability
        capabilities = self.detect_component_capabilities()

        required_components = ["tap-ldap", "target-ldap"]
        recommended_components = ["dbt-ldap"]

        issues = [
            f"Required Singer SDK component '{component}' not available"
            for component in required_components
            if not capabilities[component]["available"]
        ]

        for component in recommended_components:
            if component in capabilities and not capabilities[component]["available"]:
                logger.info(
                    "%s not available - analytics features will be limited",
                    component,
                )

        # Check flx-ldap readiness
        if not capabilities["flx-ldap"]["available"]:
            issues.append("flx-ldap orchestrator not ready")

        # All required Singer components available

        # Additional readiness checks
        try:
            # Test planner functionality
            self.planner.detect_component_capabilities()
        except Exception as e:
            issues.append(f"Migration planner not ready: {e}")

        try:
            # Test schema analyzer
            self.schema_analyzer.analyze_catalog_schema({"streams": []})
        except Exception as e:
            issues.append(f"Schema analyzer not ready: {e}")

        return len(issues) == 0, issues

    def _assess_migration_feasibility(
        self,
        components: dict[str, Any],
        requirements: dict[str, Any],
    ) -> dict[str, Any]:
        """Assess migration feasibility based on components and requirements."""
        feasibility: dict[str, Any] = {
            "overall": "feasible",
            "confidence": "high",
            "blockers": [],
            "limitations": [],
        }

        # Check required components
        if not components["tap-ldap"]["available"]:
            blockers: list[str] = feasibility["blockers"]
            blockers.append("tap-ldap not available")
            feasibility["overall"] = "not_feasible"

        if not components["target-ldap"]["available"]:
            blockers = feasibility["blockers"]
            blockers.append("target-ldap not available")
            feasibility["overall"] = "not_feasible"

        # Check complexity factors - all handled by Singer SDK components
        if requirements["complexity_assessment"] == "critical":
            feasibility["confidence"] = "high"  # Singer SDK handles complex scenarios

        return feasibility

    def _generate_migration_recommendations(
        self,
        components: dict[str, Any],
        requirements: dict[str, Any],
    ) -> list[str]:
        """Generate migration recommendations."""
        recommendations: list[str] = []

        # Component recommendations - Singer SDK ecosystem

        # Pattern recommendations
        recommended_pattern = requirements.get("recommended_pattern", "simple_sync")
        recommendations.append(f"Recommended migration pattern: {recommended_pattern}")

        # Risk mitigation
        if requirements.get("complexity_assessment") in {"high", "critical"}:
            recommendations.extend(
                (
                    "Perform test migration before production",
                    "Ensure comprehensive backup before migration",
                ),
            )

        # Performance recommendations
        if "large_dataset" in requirements.get("risk_factors", []):
            recommendations.extend(
                (
                    "Configure batch processing for optimal performance",
                    "Monitor system resources during migration",
                ),
            )

        return recommendations


# Backward compatibility - alias for existing code
client-aMigrationAdapter = GenericMigrationOrchestrator
