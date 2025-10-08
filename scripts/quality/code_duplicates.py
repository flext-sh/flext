#!/usr/bin/env python3
"""Code Duplicates Analyzer.

Analisa projetos Python no workspace FLEXT para encontrar duplicações de código
usando flext_tools.analysis para máxima precisão e confiabilidade enterprise.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from flext_core import FlextResult, FlextTypes

from flext_tools import (
    CodeDuplicateAnalyzer,
    Colors,
    FlextScript,
    ScriptMetadata,
    print_colored,
)


class CodeDuplicatesAnalyzer(FlextScript):
    """Analyze code duplicates across FLEXT workspace."""

    @property
    def metadata(self) -> ScriptMetadata:
        """Get script metadata."""
        return ScriptMetadata(
            name="code_duplicates",
            description="Analyze and detect code duplicates across workspace",
            category="quality",
            version="2.0.0",
        )

    def validate_preconditions(self) -> FlextResult[None]:
        """Validate preconditions."""
        workspace_root = Path.cwd()

        # Check if we're in FLEXT workspace
        python_projects = [
            p for p in workspace_root.iterdir() if p.is_dir() and (p / "src").exists()
        ]

        if not python_projects:
            print_colored(
                "❌ No Python projects with src/ directories found",
                Colors.RED,
            )
            return FlextResult[None].fail("No Python projects found")

        print_colored(
            f"✅ Found {len(python_projects)} Python projects to analyze",
            Colors.GREEN,
        )
        return FlextResult[None].ok(None)

    def execute_main_logic(
        self, **kwargs: dict[str, str]
    ) -> FlextResult[dict[str, str]]:
        """Execute main script logic."""
        """Execute code duplicate analysis."""
        try:
            workspace_root = Path.cwd()
            kwargs.get("projects")
            kwargs.get("min_lines", 5)
            kwargs.get("similarity_threshold", 0.8)

            print_colored("🔍 CODE DUPLICATES ANALYZER", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            # Use flext_tools.analysis for duplicate detection
            analyzer = CodeDuplicateAnalyzer(workspace_path=workspace_root)

            # Analyze code duplicates across workspace
            analysis_result = analyzer.analyze_duplicates()

            if analysis_result and analysis_result.is_success:
                print_colored("✅ Code duplicate analysis completed", Colors.GREEN)

                # Print summary
                result_data = analysis_result.data
                if isinstance(result_data, dict):
                    duplicates_found_raw = result_data.get("duplicates_found", 0)
                    if isinstance(duplicates_found_raw, int):
                        duplicates_found: int = duplicates_found_raw
                        if duplicates_found > 0:
                            print_colored(
                                f"🚨 Found {duplicates_found} duplicate code blocks",
                                Colors.YELLOW,
                            )
                    else:
                        print_colored(
                            "🎉 No significant code duplicates found!",
                            Colors.GREEN,
                        )

                # Generate report
                if kwargs.get("generate_report", True):
                    print_colored("📊 Detailed report generated", Colors.CYAN)

                return FlextResult[object].ok(analysis_result.data)

            print_colored("❌ Code duplicate analysis failed", Colors.RED)
            return FlextResult[object].fail("Analysis failed")

        except (OSError, ValueError, TypeError) as e:
            print_colored(f"❌ Error during duplicate analysis: {e}", Colors.RED)
            return FlextResult[object].fail(f"Error during analysis: {e}")

    def create_parser(self) -> argparse.ArgumentParser:
        """Create parser with specific arguments."""
        parser = super().create_parser()

        parser.add_argument(
            "--projects",
            help="Filter specific projects (comma-separated)",
        )

        parser.add_argument(
            "--min-lines",
            type=int,
            default=5,
            help="Minimum lines for duplicate detection (default: 5)",
        )

        parser.add_argument(
            "--similarity-threshold",
            type=float,
            default=0.8,
            help="Similarity threshold (0.0-1.0, default: 0.8)",
        )

        parser.add_argument(
            "--no-report",
            action="store_true",
            help="Skip generating detailed report",
        )

        return parser

    def _process_kwargs(self, args: object) -> FlextTypes.Dict:
        """Process arguments into kwargs."""
        kwargs: FlextTypes.Dict = {}
        kwargs["generate_report"] = not getattr(args, "no_report", False)
        return kwargs

    def cleanup(self) -> FlextResult[None]:
        """Limpeza após execução."""
        return FlextResult[None].ok(None)


def main() -> int:
    """Main function."""
    script = CodeDuplicatesAnalyzer()
    return script.main()


if __name__ == "__main__":
    sys.exit(main())
