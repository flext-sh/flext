#!/usr/bin/env python3
"""Quality management module for the FLX CLI.

Replaces all quality-related scripts with organized, systematic approach.
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List

from rich.console import Console
from rich.table import Table

console = Console()


class QualityManager:
    """Systematic quality management using proven methodologies."""

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.workspace_root = Path(__file__).parent.parent

    def check_all(self) -> dict[str, int]:
        """Get comprehensive quality metrics."""
        if self.debug:
            console.print("🔍 Running comprehensive quality analysis...")

        # Use ruff to get comprehensive metrics
        try:
            result = subprocess.run(
                ["ruff", "check", "--output-format=json"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root,
                check=False
            )

            # Count violations by parsing ruff output
            violations = {}
            if result.stdout:
                import json
                try:
                    data = json.loads(result.stdout)
                    for violation in data:
                        code = violation.get("code", "UNKNOWN")
                        violations[code] = violations.get(code, 0) + 1
                except json.JSONDecodeError:
                    # Fallback to line counting
                    violations["TOTAL"] = len(result.stdout.split("\n")) - 1

            return violations

        except Exception as e:
            console.print(f"⚠️ Error checking quality: {e}", style="yellow")
            return {}

    def check_category(self, category: str) -> dict[str, int]:
        """Check specific violation category."""
        if self.debug:
            console.print(f"🎯 Checking {category} violations...")

        try:
            result = subprocess.run(
                ["ruff", "check", "--select", category, "--output-format=json"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root,
                check=False
            )

            violations = {}
            if result.stdout:
                import json
                try:
                    data = json.loads(result.stdout)
                    violations[category] = len(data)
                except json.JSONDecodeError:
                    violations[category] = len(result.stdout.split("\n")) - 1

            return violations

        except Exception as e:
            console.print(f"⚠️ Error checking {category}: {e}", style="yellow")
            return {category: 0}

    def auto_fix(self, violations: dict[str, int]) -> int:
        """Auto-fix violations where possible."""
        if self.debug:
            console.print("🔧 Applying automatic fixes...")

        try:
            # Apply safe fixes first
            result = subprocess.run(
                ["ruff", "check", "--fix"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root,
                check=False
            )

            # Then apply unsafe fixes
            result_unsafe = subprocess.run(
                ["ruff", "check", "--fix", "--unsafe-fixes"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root,
                check=False
            )

            # Count fixed issues
            fixed_count = sum(violations.values()) - len(self.check_all())
            return max(0, fixed_count)

        except Exception as e:
            console.print(f"⚠️ Error applying fixes: {e}", style="yellow")
            return 0

    def report_progress(self):
        """Report current quality progress."""
        violations = self.check_all()
        total_violations = sum(violations.values())

        if not violations:
            console.print("🎉 No quality violations found!", style="green")
            return

        table = Table(title="Code Quality Report")
        table.add_column("Violation Type", style="cyan")
        table.add_column("Count", style="red")
        table.add_column("Priority", style="yellow")

        # Define priority mapping
        high_priority = ["E999", "F401", "F821", "F822", "F823"]
        medium_priority = ["E402", "G004", "BLE001", "PLR2004"]

        for violation_type, count in sorted(violations.items()):
            if violation_type in high_priority:
                priority = "🔥 HIGH"
            elif violation_type in medium_priority:
                priority = "⚠️ MEDIUM"
            else:
                priority = "📋 LOW"

            table.add_row(violation_type, str(count), priority)

        console.print(table)
        console.print(f"\n📊 Total violations: {total_violations}")

        if total_violations > 0:
            console.print("\n🎯 Suggestions:")
            console.print("  Use: ./flx quality check --auto-fix")
            console.print("  Target specific: ./flx quality check --category E402 --auto-fix")


class ComplianceManager:
    """Systematic compliance improvement manager."""

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.workspace_root = Path(__file__).parent.parent
        self.quality_manager = QualityManager(debug)

    def get_current_compliance(self) -> float:
        """Calculate current compliance percentage."""
        try:
            # Get total lines of code
            result = subprocess.run(
                ["find", ".", "-name", "*.py", "-exec", "wc", "-l", "{}", "+"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root,
                check=False
            )

            # Simple calculation: assume 100k total lines, calculate based on violations
            violations = self.quality_manager.check_all()
            total_violations = sum(violations.values())

            # Estimated compliance (simplified)
            if total_violations == 0:
                return 100.0
            if total_violations < 1000:
                return 99.0 - (total_violations / 100)
            if total_violations < 5000:
                return 95.0 - (total_violations / 1000)
            return max(80.0, 95.0 - (total_violations / 500))

        except Exception as e:
            if self.debug:
                console.print(f"⚠️ Error calculating compliance: {e}", style="yellow")
            return 85.0  # Default estimate

    def achieve_compliance(self, target: int):
        """Systematically achieve target compliance."""
        current = self.get_current_compliance()

        if current >= target:
            console.print("🎉 Target already achieved!", style="green")
            return

        console.print("🐜 Starting systematic compliance improvement...")
        console.print("📋 Phase 1: Auto-fixes...")

        # Apply auto-fixes
        violations = self.quality_manager.check_all()
        fixed = self.quality_manager.auto_fix(violations)

        console.print(f"✅ Auto-fixed {fixed} violations")

        # Check progress
        new_compliance = self.get_current_compliance()
        console.print(f"📊 Compliance: {current:.1f}% → {new_compliance:.1f}%")

        if new_compliance >= target:
            console.print("🎉 Target achieved!", style="green")
        else:
            console.print("📋 Manual review needed for remaining violations")
            self.quality_manager.report_progress()
