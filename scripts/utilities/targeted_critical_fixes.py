#!/usr/bin/env python3
"""Targeted fixes for critical issues without breaking syntax - TASK: FLX-CRITICAL-FIX."""

import subprocess
from pathlib import Path


def fix_broken_files() -> None:
    """Fix files that were broken by the previous script."""

    flx_path = Path("/home/marlonsc/pyauto/flx/src/flx")

    # Files that are known to have issues
    problem_files = [
        "core/domain/customer.py",
        "core/domain/events.py",
        "adapters/outbound/analytics.py",
        "adapters/outbound/database.py",
        "adapters/inbound/fastapi_enterprise.py",
        "adapters/inbound/fire_cli.py",
        "adapters/mixins/behavioral/__init__.py",
    ]

    for file_rel_path in problem_files:
        file_path = flx_path / file_rel_path
        if not file_path.exists():
            continue

        try:
            content = file_path.read_text()

            # Fix common structural issues caused by the script

            # Fix docstring and import order issues
            lines = content.splitlines()
            fixed_lines: list = []

            for line in lines:
                # Skip completely broken lines
                if (
                    line.strip() in {'"""', "'''"}
                    and not line.strip().startswith('"""')
                    and not line.strip().startswith("'''")
                ):
                    continue

                # Fix import statements that got mangled
                if line.strip().startswith("from ") and "import" not in line:
                    continue  # Skip broken import lines

                # Fix lines that became orphaned
                if (
                    line.strip()
                    and not line.startswith(" ")
                    and not line.startswith("\t")
                ):
                    # This is likely a class/function definition or import
                    if (
                        any(
                            keyword in line
                            for keyword in [
                                "class ",
                                "def ",
                                "async def ",
                                "import ",
                                "from ",
                            ]
                        )
                        or line.strip().startswith('"""')
                        or line.strip().startswith("'''")
                        or line.strip().startswith("#")
                    ):
                        fixed_lines.append(line)
                        # This might be orphaned content, skip it for now
                        continue
                    fixed_lines.append(line)

            # Write back the fixed content
            if len(fixed_lines) > 10:  # Only if we have substantial content
                file_path.write_text("\n".join(fixed_lines))

        except Exception:
            pass


def restore_core_files() -> None:
    """Restore core files to a working state."""

    # Customer domain entity - restore essential structure
    customer_content = '''"""Customer domain entity with comprehensive enterprise business rules."""

from __future__ import annotations

from datetime import UTC, date, datetime
from enum import Enum
from typing import Self

from pydantic import BaseModel, Field, computed_field

from flx.core.base import Entity, Identifiable, Timestamped, Versionable
from flx.core.domain.events import DomainEvent


class CustomerStatus(str, Enum):
    """Customer lifecycle status enumeration."""
    PENDING_VERIFICATION = "pending_verification"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"
    REJECTED = "rejected"


class VerificationStatus(str, Enum):
    """Identity verification status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class Address(BaseModel):
    """Customer address value object."""
    street: str = Field(min_length=1, max_length=200)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=2, max_length=50)
    postal_code: str = Field(pattern=r'^[0-9A-Z\\-\\s]{3,12}$')
    country: str = Field(min_length=2, max_length=2, pattern=r'^[A-Z]{2}$')


class CustomerCreated(DomainEvent):
    """Event published when customer is created."""
    customer_id: str
    name: str
    email: str
    creation_timestamp: datetime
    initial_status: CustomerStatus


class Customer(Entity, Identifiable, Timestamped, Versionable):
    """Customer entity implementing comprehensive business rules."""

    name: str = Field(min_length=1, max_length=100)
    email: str = Field(pattern=r'^[^@]+@[^@]+\\.[^@]+$')
    date_of_birth: date
    phone: str = Field(pattern=r'^\\+?[1-9]\\d{1,14}$')
    address: Address
    status: CustomerStatus = Field(default=CustomerStatus.PENDING_VERIFICATION)
    risk_score: float = Field(ge=0.0, le=1.0, default=0.0)
    verification_status: VerificationStatus = Field(default=VerificationStatus.PENDING)
    risk_tolerance: str = Field(default="moderate", pattern=r'^(conservative|moderate|aggressive)$')

    @computed_field
    @property
    def age(self) -> int:
        """Calculate customer age."""
        return (date.today() - self.date_of_birth).days // 365

    @computed_field
    @property
    def is_adult(self) -> bool:
        """Check if customer is adult."""
        return self.age >= 18

    @classmethod
    def create(
        cls,
        name: str,
        email: str,
        date_of_birth: date,
        phone: str,
        address: Address,
        initial_risk_tolerance: str = "moderate"
    ) -> Self:
        """Create new customer with validation."""
        age = (date.today() - date_of_birth).days // 365
        if age < 18:
            raise ValueError(f"Customer must be 18 or older. Current age: {age}")

        customer = cls(
            name=name,
            email=email,
            date_of_birth=date_of_birth,
            phone=phone,
            address=address,
            status=CustomerStatus.PENDING_VERIFICATION,
            verification_status=VerificationStatus.PENDING,
            risk_score=0.0,
            risk_tolerance=initial_risk_tolerance
        )

        customer._add_event(CustomerCreated(
            customer_id=customer.id,
            name=name,
            email=email,
            creation_timestamp=customer.created_at,
            initial_status=customer.status
        ))

        return customer
'''

    customer_file = Path("/home/marlonsc/pyauto/flx/src/flx/core/domain/customer.py")
    customer_file.write_text(customer_content)


def main() -> None:
    """Run targeted critical fixes."""

    # First, try to fix broken files
    fix_broken_files()

    # Restore core files that are essential
    restore_core_files()

    # Apply only safe automatic fixes
    subprocess.run(
        [
            "ruff",
            "check",
            "/home/marlonsc/pyauto/flx/src/flx/",
            "--fix",
            "--select=W292,I001",
        ],
        capture_output=True,
        text=True,
        cwd="/home/marlonsc/pyauto/flx",
        check=False,
    )

    # Check final status
    subprocess.run(
        ["ruff", "check", "/home/marlonsc/pyauto/flx/src/flx/", "--statistics"],
        capture_output=True,
        text=True,
        cwd="/home/marlonsc/pyauto/flx",
        check=False,
    )


if __name__ == "__main__":
    main()
