"""Base classes and utilities for quality tests."""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

REPORT_DIR = Path(tempfile.mkdtemp() + "/flext_quality_reports")
REPORT_DIR.mkdir(exist_ok=True)


class BaseQualityAnalyzer:
    """Base class for quality analyzers."""

    def __init__(
        self, workspace_root: str = "/home/marlonsc/flext", test_type: str = "generic",
    ) -> None:
        self.workspace_root = Path(workspace_root)
        self.test_type = test_type
        self.timestamp = datetime.now().isoformat()

    def find_python_files(self) -> list[Path]:
        """Find all Python files in src/ directories."""
        python_files: list[Path] = []
        for src_dir in self.workspace_root.rglob("src"):
            if src_dir.is_dir():
                python_files.extend(src_dir.rglob("*.py"))
        return python_files

    def save_report(
        self,
        report_data: dict[str, Any],
        output_format: str = "json",
    ) -> Path:
        """Save report to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if output_format == "json":
            report_file = REPORT_DIR / f"flext_{self.test_type}_report_{timestamp}.json"
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, default=str)
        elif output_format == "markdown":
            report_file = REPORT_DIR / f"flext_{self.test_type}_report_{timestamp}.md"
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(self.generate_markdown_report(report_data))
        return report_file

    def generate_markdown_report(self, report_data: dict[str, Any]) -> str:
        """Generate markdown report. Override in subclasses."""
        return f"""# {self.test_type.upper()} Quality Report

**Generated:** {self.timestamp}
**Workspace:** {self.workspace_root}

## Summary
{json.dumps(report_data.get("summary", {}), indent=2)}

## Details
{json.dumps(report_data.get("details", {}), indent=2)}
"""

    def run_analysis(self) -> dict[str, Any]:
        """Run analysis. Override in subclasses."""
        msg = "Subclasses must implement run_analysis()"
        raise NotImplementedError(msg)
