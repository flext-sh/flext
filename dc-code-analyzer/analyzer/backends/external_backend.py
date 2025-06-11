"""External tools backend for security and quality analysis."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .base import AnalysisBackend, AnalysisResult


class ExternalToolsBackend(AnalysisBackend):
    """Backend using external tools like bandit, vulture, etc."""

    @property
    def name(self) -> str:
        return "external"

    @property
    def description(self) -> str:
        return "External tools for security and dead code analysis"

    @property
    def capabilities(self) -> list[str]:
        return [
            "security_analysis",
            "dead_code_analysis",
            "dependency_analysis",
        ]

    def is_available(self) -> bool:
        """Check if external tools are available."""
        tools = ["bandit", "vulture"]
        for tool in tools:
            try:
                subprocess.run(
                    [tool, "--version"],
                    capture_output=True,
                    check=True,
                    timeout=10,
                )
            except (
                subprocess.CalledProcessError,
                FileNotFoundError,
                subprocess.TimeoutExpired,
            ):
                self.logger.warning(f"Tool {tool} not available")
                return False
        return True

    def analyze(self, python_files: list[Path]) -> AnalysisResult:
        """Analyze using external tools."""
        result = AnalysisResult()

        if not python_files:
            return result

        # Run bandit for security analysis
        try:
            security_issues = self._run_bandit(python_files)
            result.security_issues.extend(security_issues)
        except Exception as e:
            self.logger.exception(f"Bandit analysis failed: {e}")
            result.errors.append(
                {"tool": "bandit", "error": str(e), "backend": self.name},
            )

        # Run vulture for dead code analysis
        try:
            dead_code_issues = self._run_vulture(python_files)
            # Add to results (you might want to create a separate field)
            result.quality_metrics["dead_code_issues"] = dead_code_issues
        except Exception as e:
            self.logger.exception(f"Vulture analysis failed: {e}")
            result.errors.append(
                {"tool": "vulture", "error": str(e), "backend": self.name},
            )

        return result

    def _run_bandit(self, python_files: list[Path]) -> list[dict]:
        """Run bandit security analysis."""
        security_issues = []

        try:
            # Run bandit directly on files (no --files option needed)
            cmd = [
                "bandit",
                "-f",
                "json",
                "-ll",  # Low confidence
            ] + [str(f) for f in python_files]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=str(self.project_path),
                check=False,
            )

            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    for issue in data.get("results", []):
                        security_issue = {
                            "file_path": self._get_relative_path(
                                Path(issue["filename"]),
                            ),
                            "line_number": issue["line_number"],
                            "issue_type": issue["test_name"],
                            "severity": issue["issue_severity"],
                            "confidence": issue["issue_confidence"],
                            "description": issue["issue_text"],
                            "code_snippet": issue.get("code", ""),
                            "cwe_id": issue.get("cwe", {}).get("id", ""),
                            "more_info": issue.get("more_info", ""),
                        }
                        security_issues.append(security_issue)
                except json.JSONDecodeError as e:
                    self.logger.exception(f"Failed to parse bandit JSON output: {e}")

        except Exception as e:
            self.logger.exception(f"Bandit execution failed: {e}")

        return security_issues

    def _run_vulture(self, python_files: list[Path]) -> list[dict]:
        """Run vulture dead code analysis."""
        dead_code_issues = []

        try:
            cmd = ["vulture", "--json"] + [str(f) for f in python_files]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=str(self.project_path),
                check=False,
            )

            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    for issue in data:
                        dead_code_issue = {
                            "file_path": self._get_relative_path(
                                Path(issue["filename"]),
                            ),
                            "line_number": issue["lineno"],
                            "issue_type": issue["typ"],
                            "name": issue["name"],
                            "message": issue["message"],
                            "confidence": issue.get("confidence", 100),
                        }
                        dead_code_issues.append(dead_code_issue)
                except json.JSONDecodeError as e:
                    self.logger.exception(f"Failed to parse vulture JSON output: {e}")

        except Exception as e:
            self.logger.exception(f"Vulture execution failed: {e}")

        return dead_code_issues
