"""Quality analysis backend using radon and other quality metrics."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from .base import AnalysisBackend, AnalysisResult


class QualityBackend(AnalysisBackend):
    """Backend for code quality analysis using radon and other tools."""

    @property
    def name(self) -> str:
        return "quality"

    @property
    def description(self) -> str:
        return "Code quality analysis using radon for complexity metrics"

    @property
    def capabilities(self) -> list[str]:
        return [
            "complexity_analysis",
            "maintainability_analysis",
            "halstead_metrics",
            "raw_metrics",
        ]

    def is_available(self) -> bool:
        """Check if radon is available."""
        try:
            subprocess.run(
                ["radon", "--version"],
                capture_output=True,
                check=True,
                timeout=10,
            )
            return True
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            self.logger.warning("Radon not available")
            return False

    def analyze(self, python_files: list[Path]) -> AnalysisResult:
        """Analyze using radon and other quality tools."""
        result = AnalysisResult()

        if not python_files:
            return result

        # Run different radon analyses
        try:
            # Cyclomatic complexity
            cc_data = self._run_radon_cc(python_files)
            result.quality_metrics["cyclomatic_complexity"] = cc_data

            # Maintainability index
            mi_data = self._run_radon_mi(python_files)
            result.quality_metrics["maintainability_index"] = mi_data

            # Halstead metrics
            hal_data = self._run_radon_hal(python_files)
            result.quality_metrics["halstead_metrics"] = hal_data

            # Raw metrics
            raw_data = self._run_radon_raw(python_files)
            result.quality_metrics["raw_metrics"] = raw_data

        except Exception as e:
            self.logger.exception(f"Quality analysis failed: {e}")
            result.errors.append(
                {"tool": "radon", "error": str(e), "backend": self.name},
            )

        return result

    def _run_radon_cc(self, python_files: list[Path]) -> dict:
        """Run radon cyclomatic complexity analysis."""
        try:
            cmd = ["radon", "cc", "-s", "-j"] + [str(f) for f in python_files]

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
                    processed_data: dict[str, list[dict[str, Any]]] = {}

                    for file_path, functions in data.items():
                        rel_path = self._get_relative_path(Path(file_path))
                        processed_data[rel_path] = []

                        # Skip if functions is not a list (sometimes radon returns error
                        # strings)
                        if not isinstance(functions, list):
                            continue

                        for func in functions:
                            func_data = {
                                "type": func["type"],
                                "name": func["name"],
                                "line_number": func["lineno"],
                                "column": func["col_offset"],
                                "complexity": func["complexity"],
                                "rank": func["rank"],
                                "classname": func.get("classname", ""),
                            }
                            processed_data[rel_path].append(func_data)

                    return processed_data

                except json.JSONDecodeError as e:
                    self.logger.exception(f"Failed to parse radon CC JSON: {e}")

        except Exception as e:
            self.logger.exception(f"Radon CC execution failed: {e}")

        return {}

    def _run_radon_mi(self, python_files: list[Path]) -> dict:
        """Run radon maintainability index analysis."""
        try:
            cmd = ["radon", "mi", "-s", "-j"] + [str(f) for f in python_files]

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
                    processed_data: dict[str, dict[str, Any]] = {}

                    for file_path, mi_data in data.items():
                        rel_path = self._get_relative_path(Path(file_path))
                        processed_data[rel_path] = {
                            "maintainability_index": mi_data["mi"],
                            "rank": mi_data["rank"],
                        }

                    return processed_data

                except json.JSONDecodeError as e:
                    self.logger.exception(f"Failed to parse radon MI JSON: {e}")

        except Exception as e:
            self.logger.exception(f"Radon MI execution failed: {e}")

        return {}

    def _run_radon_hal(self, python_files: list[Path]) -> dict:
        """Run radon Halstead metrics analysis."""
        try:
            cmd = ["radon", "hal", "-j"] + [str(f) for f in python_files]

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
                    processed_data: dict[str, list[dict[str, Any]]] = {}

                    for file_path, functions in data.items():
                        rel_path = self._get_relative_path(Path(file_path))
                        processed_data[rel_path] = []

                        # Skip if functions is not a list (sometimes radon returns error
                        # strings)
                        if not isinstance(functions, list):
                            continue

                        for func in functions:
                            func_data = {
                                "type": func["type"],
                                "name": func["name"],
                                "line_number": func["lineno"],
                                "column": func["col_offset"],
                                "h1": func["h1"],  # Unique operators
                                "h2": func["h2"],  # Unique operands
                                "N1": func["N1"],  # Total operators
                                "N2": func["N2"],  # Total operands
                                "vocabulary": func["vocabulary"],
                                "length": func["length"],
                                "calculated_length": func["calculated_length"],
                                "volume": func["volume"],
                                "difficulty": func["difficulty"],
                                "effort": func["effort"],
                                "time": func["time"],
                                "bugs": func["bugs"],
                            }
                            processed_data[rel_path].append(func_data)

                    return processed_data

                except json.JSONDecodeError as e:
                    self.logger.exception(f"Failed to parse radon HAL JSON: {e}")

        except Exception as e:
            self.logger.exception(f"Radon HAL execution failed: {e}")

        return {}

    def _run_radon_raw(self, python_files: list[Path]) -> dict:
        """Run radon raw metrics analysis."""
        try:
            cmd = ["radon", "raw", "-s", "-j"] + [str(f) for f in python_files]

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
                    processed_data: dict[str, dict[str, Any]] = {}

                    for file_path, metrics in data.items():
                        rel_path = self._get_relative_path(Path(file_path))
                        processed_data[rel_path] = {
                            "loc": metrics["loc"],  # Lines of code
                            "lloc": metrics["lloc"],  # Logical lines of code
                            "sloc": metrics["sloc"],  # Source lines of code
                            "comments": metrics["comments"],
                            "multi": metrics["multi"],  # Multi-line strings
                            "blank": metrics["blank"],
                        }

                    return processed_data

                except json.JSONDecodeError as e:
                    self.logger.exception(f"Failed to parse radon RAW JSON: {e}")

        except Exception as e:
            self.logger.exception(f"Radon RAW execution failed: {e}")

        return {}
