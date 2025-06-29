"""Plugin validation system for comprehensive plugin verification.

Copyright (c) 2025 FLX Team. All rights reserved.
"""

from __future__ import annotations

import inspect
import re
from pathlib import Path
from typing import Any, Type

from flx_plugin.core.base import Plugin
from flx_plugin.core.types import (
    PluginCapability,
    PluginType,
    PluginValidationError,
)


class ValidationRule:
    """Base validation rule for plugin verification."""

    def __init__(self, name: str, description: str, severity: str = "error") -> None:
        """Initialize validation rule.

        Args:
        ----
            name: Rule name
            description: Rule description
            severity: Rule severity (error, warning, info)

        """
        self.name = name
        self.description = description
        self.severity = severity

    def validate(self, plugin: Type[Plugin] | Plugin) -> tuple[bool, str | None]:
        """Validate plugin against rule.

        Args:
        ----
            plugin: Plugin class or instance to validate

        Returns:
        -------
            Tuple of (passed, error_message)

        """
        raise NotImplementedError("Validation rule must implement validate method")


class MetadataValidationRule(ValidationRule):
    """Validates plugin metadata completeness and correctness."""

    def __init__(self) -> None:
        """Initialize metadata validation rule."""
        super().__init__(
            "metadata_validation", "Validates plugin metadata is complete and valid"
        )

    def validate(self, plugin: Type[Plugin] | Plugin) -> tuple[bool, str | None]:
        """Validate plugin metadata."""
        # Get metadata from class or instance
        if inspect.isclass(plugin):
            if not hasattr(plugin, "get_metadata"):
                return False, "Plugin class missing get_metadata() method"
            # For class validation, we can't call get_metadata
            return True, None
        else:
            metadata = plugin.metadata

        # Validate required fields
        required_fields = ["id", "name", "version", "plugin_type"]
        missing_fields = []

        for field in required_fields:
            if not getattr(metadata, field, None):
                missing_fields.append(field)

        if missing_fields:
            return (
                False,
                f"Missing required metadata fields: {', '.join(missing_fields)}",
            )

        # Validate version format (semantic versioning)
        version_pattern = re.compile(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$")
        if not version_pattern.match(metadata.version):
            return (
                False,
                f"Invalid version format: {metadata.version} (expected semantic versioning)",
            )

        # Validate plugin ID format
        id_pattern = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
        if not id_pattern.match(metadata.id):
            return (
                False,
                f"Invalid plugin ID format: {metadata.id} (expected lowercase with hyphens)",
            )

        return True, None


class InterfaceValidationRule(ValidationRule):
    """Validates plugin implements required interface methods."""

    def __init__(self) -> None:
        """Initialize interface validation rule."""
        super().__init__(
            "interface_validation", "Validates plugin implements required interface"
        )

    def validate(self, plugin: Type[Plugin] | Plugin) -> tuple[bool, str | None]:
        """Validate plugin interface implementation."""
        plugin_class = plugin if inspect.isclass(plugin) else plugin.__class__

        # Check inheritance
        if not issubclass(plugin_class, Plugin):
            return False, "Plugin must inherit from Plugin base class"

        # Check required methods
        required_methods = [
            ("initialize", 0),  # (method_name, min_params)
            ("execute", 2),  # self, input_data, context
            ("cleanup", 0),
            ("health_check", 0),
        ]

        missing_methods = []
        invalid_methods = []

        for method_name, min_params in required_methods:
            if not hasattr(plugin_class, method_name):
                missing_methods.append(method_name)
                continue

            method = getattr(plugin_class, method_name)
            if not callable(method):
                invalid_methods.append(f"{method_name} (not callable)")
                continue

            # Check method signature
            sig = inspect.signature(method)
            param_count = len(sig.parameters)

            # Account for self parameter
            if param_count < min_params + 1:
                invalid_methods.append(
                    f"{method_name} (expected {min_params + 1} params, got {param_count})"
                )

        errors = []
        if missing_methods:
            errors.append(f"Missing methods: {', '.join(missing_methods)}")
        if invalid_methods:
            errors.append(f"Invalid methods: {', '.join(invalid_methods)}")

        if errors:
            return False, "; ".join(errors)

        return True, None


class CapabilityValidationRule(ValidationRule):
    """Validates plugin capabilities match its type."""

    def __init__(self) -> None:
        """Initialize capability validation rule."""
        super().__init__(
            "capability_validation",
            "Validates plugin capabilities are appropriate for its type",
        )

    def validate(self, plugin: Type[Plugin] | Plugin) -> tuple[bool, str | None]:
        """Validate plugin capabilities."""
        if inspect.isclass(plugin):
            # Can't validate capabilities for class
            return True, None

        metadata = plugin.metadata
        plugin_type = metadata.plugin_type
        capabilities = metadata.capabilities

        # Define expected capabilities by type
        type_capabilities = {
            PluginType.EXTRACTOR: [
                PluginCapability.DATA_EXTRACTION,
                PluginCapability.SCHEMA_INFERENCE,
            ],
            PluginType.LOADER: [
                PluginCapability.DATA_LOADING,
                PluginCapability.SCHEMA_VALIDATION,
            ],
            PluginType.TRANSFORMER: [
                PluginCapability.DATA_TRANSFORMATION,
                PluginCapability.DATA_VALIDATION,
            ],
        }

        expected = type_capabilities.get(plugin_type, [])
        if not expected:
            # No specific capabilities required for this type
            return True, None

        # Check if plugin has at least one expected capability
        plugin_caps = set(capabilities)
        expected_caps = set(cap.value for cap in expected)

        if not plugin_caps.intersection(expected_caps):
            return False, (
                f"Plugin type {plugin_type.value} should have at least one of: "
                f"{', '.join(expected_caps)}"
            )

        return True, None


class SecurityValidationRule(ValidationRule):
    """Validates plugin security constraints."""

    def __init__(self, strict_mode: bool = False) -> None:
        """Initialize security validation rule.

        Args:
        ----
            strict_mode: Enable strict security checks

        """
        super().__init__(
            "security_validation",
            "Validates plugin security constraints",
            severity="error" if strict_mode else "warning",
        )
        self.strict_mode = strict_mode

    def validate(self, plugin: Type[Plugin] | Plugin) -> tuple[bool, str | None]:
        """Validate plugin security."""
        plugin_class = plugin if inspect.isclass(plugin) else plugin.__class__

        # Get source code for analysis
        try:
            source = inspect.getsource(plugin_class)
        except Exception:
            if self.strict_mode:
                return False, "Unable to inspect plugin source code"
            return True, None

        # Check for dangerous patterns
        dangerous_patterns = [
            (r"\beval\s*\(", "Use of eval() function"),
            (r"\bexec\s*\(", "Use of exec() function"),
            (r"\b__import__\s*\(", "Dynamic imports detected"),
            (r"\bsubprocess\.", "Subprocess execution detected"),
            (r"\bos\.system\s*\(", "System command execution detected"),
            (r"\bopen\s*\([^,)]*,\s*['\"]w", "File write operations detected"),
        ]

        security_issues = []

        for pattern, description in dangerous_patterns:
            if re.search(pattern, source):
                security_issues.append(description)

        if security_issues:
            if self.strict_mode:
                return False, f"Security violations: {'; '.join(security_issues)}"
            else:
                # In non-strict mode, we just warn
                return True, f"Security warnings: {'; '.join(security_issues)}"

        return True, None


class DependencyValidationRule(ValidationRule):
    """Validates plugin dependencies are available."""

    def __init__(self) -> None:
        """Initialize dependency validation rule."""
        super().__init__(
            "dependency_validation", "Validates plugin dependencies are available"
        )

    def validate(self, plugin: Type[Plugin] | Plugin) -> tuple[bool, str | None]:
        """Validate plugin dependencies."""
        if inspect.isclass(plugin):
            # Can't validate dependencies for class
            return True, None

        metadata = plugin.metadata
        dependencies = metadata.dependencies

        if not dependencies:
            return True, None

        missing_deps = []

        for dep in dependencies:
            # Extract package name from dependency spec
            package_name = dep.split(">=")[0].split("==")[0].split("<")[0].strip()

            try:
                __import__(package_name)
            except ImportError:
                missing_deps.append(package_name)

        if missing_deps:
            return False, f"Missing dependencies: {', '.join(missing_deps)}"

        return True, None


class ResourceValidationRule(ValidationRule):
    """Validates plugin resource requirements."""

    def __init__(self, max_memory_mb: int = 1024, max_cpu_cores: int = 4) -> None:
        """Initialize resource validation rule.

        Args:
        ----
            max_memory_mb: Maximum allowed memory in MB
            max_cpu_cores: Maximum allowed CPU cores

        """
        super().__init__(
            "resource_validation", "Validates plugin resource requirements"
        )
        self.max_memory_mb = max_memory_mb
        self.max_cpu_cores = max_cpu_cores

    def validate(self, plugin: Type[Plugin] | Plugin) -> tuple[bool, str | None]:
        """Validate plugin resource requirements."""
        if inspect.isclass(plugin):
            # Can't validate resources for class
            return True, None

        metadata = plugin.metadata

        # Check memory requirements
        if metadata.max_memory_mb and metadata.max_memory_mb > self.max_memory_mb:
            return False, (
                f"Plugin requires {metadata.max_memory_mb}MB memory, "
                f"but limit is {self.max_memory_mb}MB"
            )

        # Check CPU requirements
        if metadata.cpu_cores > self.max_cpu_cores:
            return False, (
                f"Plugin requires {metadata.cpu_cores} CPU cores, "
                f"but limit is {self.max_cpu_cores}"
            )

        return True, None


class PluginValidator:
    """Central plugin validation system."""

    def __init__(self) -> None:
        """Initialize plugin validator."""
        self.rules: list[ValidationRule] = []
        self._setup_default_rules()

    def _setup_default_rules(self) -> None:
        """Setup default validation rules."""
        self.add_rule(MetadataValidationRule())
        self.add_rule(InterfaceValidationRule())
        self.add_rule(CapabilityValidationRule())
        self.add_rule(SecurityValidationRule())
        self.add_rule(DependencyValidationRule())
        self.add_rule(ResourceValidationRule())

    def add_rule(self, rule: ValidationRule) -> None:
        """Add validation rule.

        Args:
        ----
            rule: Validation rule to add

        """
        self.rules.append(rule)

    def remove_rule(self, rule_name: str) -> None:
        """Remove validation rule by name.

        Args:
        ----
            rule_name: Name of rule to remove

        """
        self.rules = [r for r in self.rules if r.name != rule_name]

    def validate_plugin_class(self, plugin_class: Type[Plugin]) -> ValidationResult:
        """Validate plugin class.

        Args:
        ----
            plugin_class: Plugin class to validate

        Returns:
        -------
            Validation result with errors and warnings

        """
        return self._validate(plugin_class)

    def validate_plugin_instance(self, plugin: Plugin) -> ValidationResult:
        """Validate plugin instance.

        Args:
        ----
            plugin: Plugin instance to validate

        Returns:
        -------
            Validation result with errors and warnings

        """
        return self._validate(plugin)

    def _validate(self, plugin: Type[Plugin] | Plugin) -> ValidationResult:
        """Internal validation logic.

        Args:
        ----
            plugin: Plugin class or instance to validate

        Returns:
        -------
            Validation result

        """
        errors = []
        warnings = []
        info = []

        for rule in self.rules:
            try:
                passed, message = rule.validate(plugin)

                if not passed and message:
                    if rule.severity == "error":
                        errors.append(f"{rule.name}: {message}")
                    elif rule.severity == "warning":
                        warnings.append(f"{rule.name}: {message}")
                    else:
                        info.append(f"{rule.name}: {message}")
                elif passed and message:
                    # Rule passed but has informational message
                    if rule.severity == "warning":
                        warnings.append(f"{rule.name}: {message}")
                    else:
                        info.append(f"{rule.name}: {message}")

            except Exception as e:
                errors.append(f"{rule.name}: Validation error - {str(e)}")

        return ValidationResult(
            is_valid=len(errors) == 0, errors=errors, warnings=warnings, info=info
        )


class ValidationResult:
    """Plugin validation result container."""

    def __init__(
        self, is_valid: bool, errors: list[str], warnings: list[str], info: list[str]
    ) -> None:
        """Initialize validation result.

        Args:
        ----
            is_valid: Whether validation passed
            errors: List of error messages
            warnings: List of warning messages
            info: List of informational messages

        """
        self.is_valid = is_valid
        self.errors = errors
        self.warnings = warnings
        self.info = info

    def raise_if_invalid(self, plugin_id: str) -> None:
        """Raise exception if validation failed.

        Args:
        ----
            plugin_id: Plugin ID for error context

        Raises:
        ------
            PluginValidationError: If validation failed

        """
        if not self.is_valid:
            raise PluginValidationError(
                f"Plugin validation failed for {plugin_id}",
                plugin_id=plugin_id,
                validation_failures=self.errors,
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns
        -------
            Dictionary with validation results

        """
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "info_count": len(self.info),
        }


def validate_plugin_path(path: Path) -> bool:
    """Validate plugin file path.

    Args:
    ----
        path: Path to plugin file

    Returns:
    -------
        True if path is valid plugin location

    """
    if not path.exists():
        return False

    if not path.is_file():
        return False

    if path.suffix != ".py":
        return False

    # Check if file looks like a plugin
    with open(path) as f:
        content = f.read()

    # Basic heuristics
    if "class" not in content:
        return False

    if "Plugin" not in content and "plugin" not in content.lower():
        return False

    return True


def validate_plugin_config(
    config: dict[str, Any], schema: dict[str, Any]
) -> tuple[bool, list[str]]:
    """Validate plugin configuration against schema.

    Args:
    ----
        config: Plugin configuration
        schema: JSON schema for validation

    Returns:
    -------
        Tuple of (is_valid, errors)

    """
    errors = []

    # Basic validation without jsonschema dependency
    required = schema.get("required", [])
    properties = schema.get("properties", {})

    # Check required fields
    for field in required:
        if field not in config:
            errors.append(f"Missing required field: {field}")

    # Check field types
    for field, value in config.items():
        if field in properties:
            expected_type = properties[field].get("type")
            if expected_type:
                actual_type = type(value).__name__
                type_map = {
                    "string": "str",
                    "integer": "int",
                    "number": "float",
                    "boolean": "bool",
                    "array": "list",
                    "object": "dict",
                }

                expected_python_type = type_map.get(expected_type, expected_type)

                if actual_type != expected_python_type:
                    # Special case for number type (int is valid for float)
                    if not (expected_type == "number" and actual_type == "int"):
                        errors.append(
                            f"Field '{field}' has wrong type: "
                            f"expected {expected_type}, got {actual_type}"
                        )

    return len(errors) == 0, errors
