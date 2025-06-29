"""Security monitoring system for enterprise security compliance.

Provides comprehensive security violation detection, monitoring, and alerting
for FLX enterprise environments with automated incident response.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

import structlog
from flx_core.domain.advanced_types import ServiceResult
from flx_core.domain.pydantic_base import DomainBaseModel
from pydantic import Field

logger = structlog.get_logger(__name__)


class SecurityViolationType(Enum):
    """Types of security violations."""

    AUTHENTICATION_FAILURE = "authentication_failure"
    AUTHORIZATION_VIOLATION = "authorization_violation"
    DATA_ACCESS_VIOLATION = "data_access_violation"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    INJECTION_ATTEMPT = "injection_attempt"
    MALFORMED_REQUEST = "malformed_request"


class SecurityViolationSeverity(Enum):
    """Security violation severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityViolation(DomainBaseModel):
    """Security violation record."""

    violation_id: UUID = Field(default_factory=uuid4)
    violation_type: SecurityViolationType
    severity: SecurityViolationSeverity
    description: str
    user_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    request_path: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    context: dict[str, Any] = Field(default_factory=dict)


class SecurityViolationMonitor:
    """Enterprise security violation monitoring system."""

    def __init__(self) -> None:
        """Initialize security monitor."""
        self.logger = logger.bind(component="security_monitor")
        self._violations: list[SecurityViolation] = []

    async def record_violation(
        self,
        violation_type: SecurityViolationType,
        severity: SecurityViolationSeverity,
        description: str,
        context: dict[str, Any] | None = None,
    ) -> ServiceResult[SecurityViolation]:
        """Record a security violation.

        Args:
        ----
            violation_type: Type of security violation
            severity: Severity level
            description: Description of the violation
            context: Additional context information

        Returns:
        -------
            ServiceResult containing the recorded violation

        """
        try:
            violation = SecurityViolation(
                violation_type=violation_type,
                severity=severity,
                description=description,
                context=context or {},
            )

            self._violations.append(violation)

            self.logger.warning(
                "Security violation recorded",
                violation_id=str(violation.violation_id),
                violation_type=violation_type.value,
                severity=severity.value,
                description=description,
            )

            return ServiceResult.ok(violation)

        except Exception as e:
            error_msg = f"Failed to record security violation: {e}"
            self.logger.exception("Security violation recording failed", error=str(e))
            return ServiceResult.fail(error_msg)

    def get_violations(
        self,
        severity: SecurityViolationSeverity | None = None,
        violation_type: SecurityViolationType | None = None,
    ) -> list[SecurityViolation]:
        """Get security violations with optional filtering.

        Args:
        ----
            severity: Filter by severity level
            violation_type: Filter by violation type

        Returns:
        -------
            List of matching security violations

        """
        violations = self._violations

        if severity:
            violations = [v for v in violations if v.severity == severity]

        if violation_type:
            violations = [v for v in violations if v.violation_type == violation_type]

        return violations

    def get_violation_count(
        self, severity: SecurityViolationSeverity | None = None
    ) -> int:
        """Get count of violations by severity.

        Args:
        ----
            severity: Filter by severity level

        Returns:
        -------
            Count of matching violations

        """
        if severity:
            return len([v for v in self._violations if v.severity == severity])
        return len(self._violations)

    def clear_violations(self) -> None:
        """Clear all recorded violations."""
        self._violations.clear()
        self.logger.info("Security violations cleared")


# Export all classes
__all__ = [
    "SecurityViolation",
    "SecurityViolationMonitor",
    "SecurityViolationSeverity",
    "SecurityViolationType",
]
