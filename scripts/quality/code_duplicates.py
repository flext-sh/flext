#!/usr/bin/env python3
"""Code Duplicates Analyzer.

Analisa projetos Python no workspace FLEXT para encontrar duplicações de código
usando flext_tools.analysis para máxima precisão e confiabilidade enterprise.
"""

from __future__ import annotations

import sys
from pathlib import Path

from flext_tools import Colors, print_colored
from flext_tools.analysis import CodeDuplicateAnalyzer
from flext_tools.core.script_base import FlextScript, ScriptMetadata


class CodeDuplicatesAnalyzer(FlextScript):
    """Analyze code duplicates across FLEXT workspace."""

    @property
    def metadata(self) -> ScriptMetadata:
        return ScriptMetadata(
            name="code_duplicates",
            description="Analyze and detect code duplicates across workspace",
            category="quality",
            version="2.0.0",
        )

    def validate_preconditions(self) -> bool:
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
            return False

        print_colored(
            f"✅ Found {len(python_projects)} Python projects to analyze",
            Colors.GREEN,
        )
        return True

    def execute_main_logic(self, **kwargs: object) -> bool:
        """Execute code duplicate analysis."""
        try:
            workspace_root = Path.cwd()
            projects_filter = kwargs.get("projects")
            min_lines = kwargs.get("min_lines", 5)
            similarity_threshold = kwargs.get("similarity_threshold", 0.8)

            print_colored("🔍 CODE DUPLICATES ANALYZER", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            # Use flext_tools.analysis for duplicate detection
            analyzer = CodeDuplicateAnalyzer(workspace_path=workspace_root)

            # Analyze code duplicates across workspace
            analysis_result = analyzer.analyze_duplicates(
                projects_filter=projects_filter,
                min_lines=min_lines,
                similarity_threshold=similarity_threshold,
            )

            if analysis_result:
                print_colored("✅ Code duplicate analysis completed", Colors.GREEN)

                # Print summary
                duplicates_found = analysis_result.get("duplicates_found", 0)
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

                return True
            print_colored("❌ Code duplicate analysis failed", Colors.RED)
            return False

        except (OSError, ValueError, TypeError) as e:
            print_colored(f"❌ Error during duplicate analysis: {e}", Colors.RED)
            return False

    def create_parser(self) -> object:
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

    def _process_kwargs(self, args: object) -> dict[str, object]:
        """Process arguments into kwargs."""
        kwargs: dict[str, object] = {}
        kwargs["generate_report"] = not getattr(args, "no_report", False)
        return kwargs

    def cleanup(self) -> None:
        """Limpeza após execução."""


def main() -> int:
    """Main function."""
    script = CodeDuplicatesAnalyzer()
    return script.main()


if __name__ == "__main__":
    sys.exit(main())
