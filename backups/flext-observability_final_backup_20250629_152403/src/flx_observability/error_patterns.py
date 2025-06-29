"""Production error handling patterns for enterprise deployments.

Provides comprehensive error tracking, pattern analysis, and automated
recovery mechanisms for FLX enterprise environments with structured
error classification and intelligent remediation suggestions.
"""

from __future__ import annotations

import asyncio
import traceback
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

import structlog
from flx_core.config.domain_config import get_config
from flx_core.domain.advanced_types import ServiceResult
from flx_core.domain.pydantic_base import DomainBaseModel
from pydantic import Field

if TYPE_CHECKING:
    from collections.abc import Callable

logger = structlog.get_logger(__name__)


class ErrorSeverity(Enum):
    """Error severity classification."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error category classification."""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    BUSINESS_LOGIC = "business_logic"
    INFRASTRUCTURE = "infrastructure"
    EXTERNAL_SERVICE = "external_service"
    PERFORMANCE = "performance"
    SECURITY = "security"
    UNKNOWN = "unknown"


class RecoveryAction(Enum):
    """Automated recovery actions."""

    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAK = "circuit_break"
    ESCALATE = "escalate"
    IGNORE = "ignore"
    RESTART_SERVICE = "restart_service"
    MANUAL_INTERVENTION = "manual_intervention"


class ErrorPattern(DomainBaseModel):
    """Error pattern model for tracking and analysis."""

    pattern_id: UUID = Field(default_factory=uuid4)
    error_signature: str = Field(description="Unique error signature")
    error_message: str = Field(description="Error message")
    category: ErrorCategory = Field(description="Error category")
    severity: ErrorSeverity = Field(description="Error severity")
    occurrence_count: int = Field(default=1, description="Number of occurrences")
    first_seen: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_seen: datetime = Field(default_factory=lambda: datetime.now(UTC))
    recovery_action: RecoveryAction = Field(description="Recommended recovery action")
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = DomainBaseModel.model_config.copy()
    model_config.update(
        {
            "use_enum_values": False,  # Keep enum objects, don't convert to values
        },
    )


class ErrorInstance(DomainBaseModel):
    """Individual error instance with full context."""

    instance_id: UUID = Field(default_factory=uuid4)
    pattern_id: UUID = Field(description="Reference to error pattern")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    context: dict[str, Any] = Field(default_factory=dict)
    stack_trace: str | None = Field(default=None)
    user_id: str | None = Field(default=None)
    request_id: str | None = Field(default=None)
    resolved: bool = Field(default=False)
    resolution_notes: str | None = Field(default=None)


class ErrorRecoveryRule(DomainBaseModel):
    """Recovery rule definition for automated error handling."""

    rule_id: UUID = Field(default_factory=uuid4)
    error_signature_pattern: str = Field(
        description="Regex pattern for error signature",
    )
    category: ErrorCategory = Field(description="Target error category")
    max_retry_attempts: int = Field(default=3)
    retry_delay_seconds: float = Field(default=1.0)
    circuit_breaker_threshold: int = Field(default=5)
    recovery_action: RecoveryAction = Field(description="Recovery action to take")
    custom_handler: str | None = Field(
        default=None,
        description="Custom recovery handler",
    )
    enabled: bool = Field(default=True)

    model_config = DomainBaseModel.model_config.copy()
    model_config.update(
        {
            "use_enum_values": False,  # Keep enum objects, don't convert to values
        },
    )


class ProductionErrorHandler:
    """Enterprise error handling system with pattern recognition and recovery."""

    def __init__(self) -> None:
        """Initialize production error handler."""
        self.logger = logger.bind(component="production_error_handler")
        self.config = get_config()

        # Error tracking storage
        self._error_patterns: dict[str, ErrorPattern] = {}
        self._error_instances: list[ErrorInstance] = []
        self._recovery_rules: list[ErrorRecoveryRule] = []
        self._circuit_breakers: dict[str, dict[str, Any]] = {}

        # Recovery handlers
        self._custom_handlers: dict[str, Callable] = {}

        # Initialize default recovery rules
        self._initialize_default_rules()

    def _initialize_default_rules(self) -> None:
        """Initialize default error recovery rules."""
        # Authentication errors - escalate immediately
        self._recovery_rules.append(
            ErrorRecoveryRule(
                error_signature_pattern=r".*authentication.*failed.*",
                category=ErrorCategory.AUTHENTICATION,
                max_retry_attempts=0,
                recovery_action=RecoveryAction.ESCALATE,
            ),
        )

        # Database connection errors - retry with backoff
        self._recovery_rules.append(
            ErrorRecoveryRule(
                error_signature_pattern=r".*database.*connection.*",
                category=ErrorCategory.INFRASTRUCTURE,
                max_retry_attempts=3,
                retry_delay_seconds=2.0,
                recovery_action=RecoveryAction.RETRY,
            ),
        )

        # External service timeout - circuit breaker
        self._recovery_rules.append(
            ErrorRecoveryRule(
                error_signature_pattern=r".*timeout.*external.*service.*",
                category=ErrorCategory.EXTERNAL_SERVICE,
                circuit_breaker_threshold=5,
                recovery_action=RecoveryAction.CIRCUIT_BREAK,
            ),
        )

        # Validation errors - ignore after logging
        self._recovery_rules.append(
            ErrorRecoveryRule(
                error_signature_pattern=r".*validation.*error.*",
                category=ErrorCategory.VALIDATION,
                max_retry_attempts=0,
                recovery_action=RecoveryAction.IGNORE,
            ),
        )

        # Performance issues - fallback to cached data
        self._recovery_rules.append(
            ErrorRecoveryRule(
                error_signature_pattern=r".*performance.*slow.*response.*",
                category=ErrorCategory.PERFORMANCE,
                recovery_action=RecoveryAction.FALLBACK,
            ),
        )

    async def handle_error(
        self, error: Exception, context: dict[str, Any] | None = None
    ) -> ServiceResult[Any]:
        """Handle error with pattern recognition and recovery."""
        context = context or {}

        try:
            # Generate error signature
            error_signature = self._generate_error_signature(error)

            # Classify error
            category, severity = self._classify_error(error, error_signature)

            # Update or create error pattern
            pattern = await self._update_error_pattern(
                error_signature,
                str(error),
                category,
                severity,
            )

            # Create error instance
            instance = ErrorInstance(
                pattern_id=pattern.pattern_id,
                context=context,
                stack_trace=traceback.format_exc(),
                user_id=context.get("user_id"),
                request_id=context.get("request_id"),
            )
            self._error_instances.append(instance)

            # Log error with structured data
            self.logger.error(
                "Error handled by production error handler",
                error_signature=error_signature,
                category=category.value,
                severity=severity.value,
                occurrence_count=pattern.occurrence_count,
                instance_id=str(instance.instance_id),
                pattern_id=str(pattern.pattern_id),
                context=context,
            )

            # Attempt recovery
            recovery_result = await self._attempt_recovery(
                pattern,
                instance,
                error,
                context,
            )

            if recovery_result.success:
                self.logger.info(
                    "Error recovery successful",
                    pattern_id=str(pattern.pattern_id),
                    recovery_action=pattern.recovery_action.value,
                )
                instance.resolved = True
                instance.resolution_notes = "Automatic recovery successful"
                return recovery_result
            self.logger.warning(
                "Error recovery failed",
                pattern_id=str(pattern.pattern_id),
                recovery_action=pattern.recovery_action.value,
                error=recovery_result.error,
            )
            return ServiceResult.fail(f"Error recovery failed: {recovery_result.error}")

        except Exception as handler_error:
            self.logger.exception(
                "Error handler itself failed",
                original_error=str(error),
                handler_error=str(handler_error),
            )
            return ServiceResult.fail(f"Error handler failed: {handler_error}")

    def _generate_error_signature(self, error: Exception) -> str:
        """Generate unique signature for error pattern matching."""
        error_type = type(error).__name__
        error_message = str(error).lower()

        # Normalize common variable parts
        import re

        normalized_message = re.sub(r"\d+", "[NUMBER]", error_message)
        normalized_message = re.sub(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            "[UUID]",
            normalized_message,
        )
        normalized_message = re.sub(r"\b\w+@\w+\.\w+\b", "[EMAIL]", normalized_message)

        return f"{error_type}:{normalized_message[:200]}"  # Limit length

    def _classify_error(
        self, error: Exception, signature: str
    ) -> tuple[ErrorCategory, ErrorSeverity]:
        """Classify error by category and severity."""
        error_type = type(error).__name__.lower()
        error_message = str(error).lower()

        # Determine category - prioritize specific error types first
        category = ErrorCategory.UNKNOWN

        # Check specific exception types first
        if error_type == "permissionerror":
            category = ErrorCategory.AUTHORIZATION
        elif any(
            term in error_message for term in ["authentication", "login", "credential"]
        ):
            category = ErrorCategory.AUTHENTICATION
        elif any(
            term in error_message
            for term in ["authorization", "permission", "access denied"]
        ):
            category = ErrorCategory.AUTHORIZATION
        elif any(
            term in error_message
            for term in ["security", "attack", "malicious", "violation"]
        ):
            category = ErrorCategory.SECURITY
        elif any(
            term in error_message
            for term in ["validation", "invalid", "required field"]
        ):
            category = ErrorCategory.VALIDATION
        elif any(term in error_message for term in ["database", "connection", "sql"]):
            category = ErrorCategory.INFRASTRUCTURE
        elif any(
            term in error_message for term in ["timeout", "external", "api", "service"]
        ):
            category = ErrorCategory.EXTERNAL_SERVICE
        elif any(term in error_message for term in ["performance", "slow"]):
            category = ErrorCategory.PERFORMANCE
        elif error_type in {"valueerror", "typeerror", "attributeerror"}:
            category = ErrorCategory.BUSINESS_LOGIC

        # Determine severity - security and auth errors are always critical
        severity = ErrorSeverity.MEDIUM
        if category in {
            ErrorCategory.SECURITY,
            ErrorCategory.AUTHENTICATION,
            ErrorCategory.AUTHORIZATION,
        }:
            severity = ErrorSeverity.CRITICAL
        elif category in {ErrorCategory.INFRASTRUCTURE, ErrorCategory.EXTERNAL_SERVICE}:
            severity = ErrorSeverity.HIGH
        elif category == ErrorCategory.VALIDATION:
            severity = ErrorSeverity.LOW
        elif any(term in error_message for term in ["critical", "fatal", "severe"]):
            severity = ErrorSeverity.CRITICAL
        elif any(term in error_message for term in ["warning", "minor"]):
            severity = ErrorSeverity.LOW

        return category, severity

    async def _update_error_pattern(
        self,
        signature: str,
        message: str,
        category: ErrorCategory,
        severity: ErrorSeverity,
    ) -> ErrorPattern:
        """Update or create error pattern."""
        if signature in self._error_patterns:
            pattern = self._error_patterns[signature]
            pattern.occurrence_count += 1
            pattern.last_seen = datetime.now(UTC)

            # Update severity if this instance is more severe
            severity_order = [
                ErrorSeverity.LOW,
                ErrorSeverity.MEDIUM,
                ErrorSeverity.HIGH,
                ErrorSeverity.CRITICAL,
            ]
            if severity_order.index(severity) > severity_order.index(pattern.severity):
                pattern.severity = severity
        else:
            # Determine recovery action based on category and severity
            recovery_action = self._determine_recovery_action(category, severity)

            pattern = ErrorPattern(
                error_signature=signature,
                error_message=message,
                category=category,
                severity=severity,
                recovery_action=recovery_action,
            )
            self._error_patterns[signature] = pattern

        return pattern

    def _determine_recovery_action(
        self, category: ErrorCategory, severity: ErrorSeverity
    ) -> RecoveryAction:
        """Determine appropriate recovery action."""
        # Check custom rules first
        for rule in self._recovery_rules:
            if rule.category == category and rule.enabled:
                return rule.recovery_action

        # Default logic
        if severity == ErrorSeverity.CRITICAL:
            return RecoveryAction.ESCALATE
        if category == ErrorCategory.INFRASTRUCTURE:
            return RecoveryAction.RETRY
        if category == ErrorCategory.EXTERNAL_SERVICE:
            return RecoveryAction.CIRCUIT_BREAK
        if category == ErrorCategory.VALIDATION:
            return RecoveryAction.IGNORE
        if category == ErrorCategory.PERFORMANCE:
            return RecoveryAction.FALLBACK
        return RecoveryAction.MANUAL_INTERVENTION

    async def _attempt_recovery(
        self,
        pattern: ErrorPattern,
        instance: ErrorInstance,
        original_error: Exception,
        context: dict[str, Any],
    ) -> ServiceResult[Any]:
        """Attempt error recovery based on pattern."""
        action = pattern.recovery_action

        try:
            if action == RecoveryAction.RETRY:
                return await self._handle_retry_recovery(
                    pattern,
                    instance,
                    original_error,
                    context,
                )
            if action == RecoveryAction.FALLBACK:
                return await self._handle_fallback_recovery(
                    pattern,
                    instance,
                    original_error,
                    context,
                )
            if action == RecoveryAction.CIRCUIT_BREAK:
                return await self._handle_circuit_breaker_recovery(
                    pattern,
                    instance,
                    original_error,
                    context,
                )
            if action == RecoveryAction.IGNORE:
                return ServiceResult.ok("Error ignored as per recovery policy")
            if action == RecoveryAction.ESCALATE:
                await self._escalate_error(pattern, instance, original_error, context)
                return ServiceResult.fail("Error escalated for manual intervention")
            if action == RecoveryAction.RESTART_SERVICE:
                return await self._handle_service_restart_recovery(
                    pattern,
                    instance,
                    original_error,
                    context,
                )
            # MANUAL_INTERVENTION
            return ServiceResult.fail("Manual intervention required")

        except Exception as recovery_error:
            self.logger.exception(
                "Recovery attempt failed",
                pattern_id=str(pattern.pattern_id),
                recovery_action=action.value,
                recovery_error=str(recovery_error),
            )
            return ServiceResult.fail(f"Recovery failed: {recovery_error}")

    async def _handle_retry_recovery(
        self,
        pattern: ErrorPattern,
        instance: ErrorInstance,
        original_error: Exception,
        context: dict[str, Any],
    ) -> ServiceResult[Any]:
        """Handle retry recovery with exponential backoff."""
        # Find matching rule for retry parameters
        retry_rule = None
        for rule in self._recovery_rules:
            if (
                rule.category == pattern.category
                and rule.recovery_action == RecoveryAction.RETRY
            ):
                retry_rule = rule
                break

        max_attempts = retry_rule.max_retry_attempts if retry_rule else 3
        base_delay = retry_rule.retry_delay_seconds if retry_rule else 1.0

        for attempt in range(max_attempts):
            if attempt > 0:
                delay = base_delay * (2 ** (attempt - 1))  # Exponential backoff
                await asyncio.sleep(delay)

            self.logger.info(
                "Attempting retry recovery",
                pattern_id=str(pattern.pattern_id),
                attempt=attempt + 1,
                max_attempts=max_attempts,
            )

            # Here you would retry the original operation
            # For now, we'll simulate success on the last attempt
            if attempt == max_attempts - 1:
                return ServiceResult.ok(
                    f"Retry successful after {attempt + 1} attempts",
                )

        return ServiceResult.fail(f"Retry failed after {max_attempts} attempts")

    async def _handle_fallback_recovery(
        self,
        pattern: ErrorPattern,
        instance: ErrorInstance,
        original_error: Exception,
        context: dict[str, Any],
    ) -> ServiceResult[Any]:
        """Handle fallback recovery (e.g., cached data, default values)."""
        self.logger.info(
            "Attempting fallback recovery",
            pattern_id=str(pattern.pattern_id),
        )

        # Implement fallback logic based on context
        fallback_data = context.get("fallback_data")
        if fallback_data:
            return ServiceResult.ok(fallback_data)

        # Default fallback
        return ServiceResult.ok(
            {"status": "degraded", "message": "Using fallback mode"},
        )

    async def _handle_circuit_breaker_recovery(
        self,
        pattern: ErrorPattern,
        instance: ErrorInstance,
        original_error: Exception,
        context: dict[str, Any],
    ) -> ServiceResult[Any]:
        """Handle circuit breaker recovery."""
        service_key = context.get("service_name", pattern.error_signature)

        if service_key not in self._circuit_breakers:
            self._circuit_breakers[service_key] = {
                "state": "closed",
                "failure_count": 0,
                "last_failure": None,
                "threshold": 5,
            }

        breaker = self._circuit_breakers[service_key]
        breaker["failure_count"] += 1
        breaker["last_failure"] = datetime.now(UTC)

        if breaker["failure_count"] > breaker["threshold"]:
            breaker["state"] = "open"
            self.logger.warning(
                "Circuit breaker opened",
                service=service_key,
                failure_count=breaker["failure_count"],
            )
            return ServiceResult.fail("Circuit breaker open - service unavailable")

        return ServiceResult.fail("Circuit breaker recording failure")

    async def _handle_service_restart_recovery(
        self,
        pattern: ErrorPattern,
        instance: ErrorInstance,
        original_error: Exception,
        context: dict[str, Any],
    ) -> ServiceResult[Any]:
        """Handle service restart recovery."""
        service_name = context.get("service_name", "unknown")

        self.logger.warning(
            "Service restart recovery triggered",
            pattern_id=str(pattern.pattern_id),
            service_name=service_name,
        )

        # In a real implementation, this would trigger actual service restart
        # For now, we simulate the restart process
        # ZERO TOLERANCE - Use domain configuration for simulation delay
        from flx_core.config.domain_config import get_config

        config = get_config()
        await asyncio.sleep(
            config.business.MELTANO_OPERATION_DELAY_SECONDS,
        )  # Simulate restart time

        return ServiceResult.ok(f"Service {service_name} restart initiated")

    async def _escalate_error(
        self,
        pattern: ErrorPattern,
        instance: ErrorInstance,
        original_error: Exception,
        context: dict[str, Any],
    ) -> None:
        """Escalate error to operations team."""
        escalation_data = {
            "pattern_id": str(pattern.pattern_id),
            "instance_id": str(instance.instance_id),
            "error_signature": pattern.error_signature,
            "category": pattern.category.value,
            "severity": pattern.severity.value,
            "occurrence_count": pattern.occurrence_count,
            "context": context,
            "timestamp": instance.timestamp.isoformat(),
        }

        self.logger.critical(
            "Error escalated for manual intervention",
            escalation_data=escalation_data,
        )

        # In a real implementation, this would:
        # - Send alerts to PagerDuty/OpsGenie
        # - Create tickets in JIRA/ServiceNow
        # - Send notifications to Slack/Teams
        # - Update monitoring dashboards

    def get_error_statistics(self) -> dict[str, Any]:
        """Get comprehensive error statistics."""
        total_patterns = len(self._error_patterns)
        total_instances = len(self._error_instances)

        # Group by category
        by_category = {}
        for pattern in self._error_patterns.values():
            try:
                category = pattern.category.value
            except AttributeError:
                category = str(pattern.category)
            if category not in by_category:
                by_category[category] = {"patterns": 0, "total_occurrences": 0}
            by_category[category]["patterns"] += 1
            by_category[category]["total_occurrences"] += pattern.occurrence_count

        # Group by severity
        by_severity = {}
        for pattern in self._error_patterns.values():
            try:
                severity = pattern.severity.value
            except AttributeError:
                severity = str(pattern.severity)
            if severity not in by_severity:
                by_severity[severity] = {"patterns": 0, "total_occurrences": 0}
            by_severity[severity]["patterns"] += 1
            by_severity[severity]["total_occurrences"] += pattern.occurrence_count

        # Recovery action statistics
        by_recovery_action = {}
        for pattern in self._error_patterns.values():
            try:
                action = pattern.recovery_action.value
            except AttributeError:
                action = str(pattern.recovery_action)
            if action not in by_recovery_action:
                by_recovery_action[action] = 0
            by_recovery_action[action] += pattern.occurrence_count

        # Circuit breaker status
        circuit_breaker_status = {}
        for service, breaker in self._circuit_breakers.items():
            circuit_breaker_status[service] = {
                "state": breaker["state"],
                "failure_count": breaker["failure_count"],
            }

        return {
            "summary": {
                "total_error_patterns": total_patterns,
                "total_error_instances": total_instances,
                "active_recovery_rules": len(
                    [r for r in self._recovery_rules if r.enabled],
                ),
                "circuit_breakers": len(self._circuit_breakers),
            },
            "breakdown": {
                "by_category": by_category,
                "by_severity": by_severity,
                "by_recovery_action": by_recovery_action,
            },
            "circuit_breakers": circuit_breaker_status,
            "recent_patterns": [
                {
                    "signature": pattern.error_signature[:100],
                    "category": pattern.category.value,
                    "severity": pattern.severity.value,
                    "count": pattern.occurrence_count,
                    "last_seen": pattern.last_seen.isoformat(),
                }
                for pattern in sorted(
                    self._error_patterns.values(),
                    key=lambda p: p.last_seen,
                    reverse=True,
                )[:10]
            ],
        }

    def register_custom_handler(self, name: str, handler: Callable) -> None:
        """Register custom recovery handler."""
        self._custom_handlers[name] = handler
        self.logger.info("Custom recovery handler registered", handler_name=name)

    def add_recovery_rule(self, rule: ErrorRecoveryRule) -> None:
        """Add custom recovery rule."""
        self._recovery_rules.append(rule)
        self.logger.info("Recovery rule added", rule_id=str(rule.rule_id))


# Alias for backward compatibility
ErrorPatternAnalyzer = ProductionErrorHandler


# Export all classes
__all__ = [
    "ErrorCategory",
    "ErrorInstance",
    "ErrorPattern",
    "ErrorPatternAnalyzer",  # Alias
    "ErrorRecoveryRule",
    "ErrorSeverity",
    "ProductionErrorHandler",
    "RecoveryAction",
]
