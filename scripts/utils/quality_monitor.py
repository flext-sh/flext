#!/usr/bin/env python3
"""Code quality monitoring script for FLX.

This script monitors code quality metrics and prevents regression
by tracking complexity, duplication, and other quality indicators.
"""

import argparse
import ast
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class QualityMetrics:
    """Code quality metrics for a file or module."""

    file_path: str
    lines_of_code: int
    cyclomatic_complexity: int
    function_count: int
    class_count: int
    max_function_complexity: int
    max_function_parameters: int
    max_function_returns: int
    duplicate_blocks: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "file_path": self.file_path,
            "lines_of_code": self.lines_of_code,
            "cyclomatic_complexity": self.cyclomatic_complexity,
            "function_count": self.function_count,
            "class_count": self.class_count,
            "max_function_complexity": self.max_function_complexity,
            "max_function_parameters": self.max_function_parameters,
            "max_function_returns": self.max_function_returns,
            "duplicate_blocks": self.duplicate_blocks,
        }


class ComplexityAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze code complexity."""

    def __init__(self) -> None:
        self.complexity = 0
        self.function_complexities: list[int] = []
        self.function_parameters: list[int] = []
        self.function_returns: list[int] = []
        self.function_count = 0
        self.class_count = 0
        self.current_function_complexity = 0
        self.current_function_returns = 0

    def visit_function_def(self, node: ast.FunctionDef) -> None:
        """Visit function definition."""
        self.function_count += 1

        # Count parameters
        param_count = len(node.args.args)
        if node.args.vararg:
            param_count += 1
        if node.args.kwarg:
            param_count += 1
        param_count += len(node.args.kwonlyargs)

        self.function_parameters.append(param_count)

        # Analyze function complexity
        old_complexity = self.current_function_complexity
        old_returns = self.current_function_returns
        self.current_function_complexity = 1  # Base complexity
        self.current_function_returns = 0

        self.generic_visit(node)

        self.function_complexities.append(self.current_function_complexity)
        self.function_returns.append(self.current_function_returns)

        self.complexity += self.current_function_complexity
        self.current_function_complexity = old_complexity
        self.current_function_returns = old_returns

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definition."""
        self.visit_function_def(node)

    def visit_class_def(self, node: ast.ClassDef) -> None:
        """Visit class definition."""
        self.class_count += 1
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        """Visit if statement."""
        self.current_function_complexity += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        """Visit while loop."""
        self.current_function_complexity += 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        """Visit for loop."""
        self.current_function_complexity += 1
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        """Visit try statement."""
        self.current_function_complexity += 1
        self.generic_visit(node)

    def visit_except_handler(self, node: ast.ExceptHandler) -> None:
        """Visit except handler."""
        self.current_function_complexity += 1
        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> None:
        """Visit with statement."""
        self.current_function_complexity += 1
        self.generic_visit(node)

    def visit_Return(self, node: ast.Return) -> None:
        """Visit return statement."""
        self.current_function_returns += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        """Visit boolean operation."""
        self.current_function_complexity += len(node.values) - 1
        self.generic_visit(node)


def analyze_file(file_path: Path) -> QualityMetrics:
    """Analyze a Python file for quality metrics."""
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        analyzer = ComplexityAnalyzer()
        analyzer.visit(tree)

        lines_of_code = len([line for line in content.splitlines() if line.strip()])

        return QualityMetrics(
            file_path=str(file_path),
            lines_of_code=lines_of_code,
            cyclomatic_complexity=analyzer.complexity,
            function_count=analyzer.function_count,
            class_count=analyzer.class_count,
            max_function_complexity=(
                max(analyzer.function_complexities)
                if analyzer.function_complexities
                else 0
            ),
            max_function_parameters=(
                max(analyzer.function_parameters) if analyzer.function_parameters else 0
            ),
            max_function_returns=(
                max(analyzer.function_returns) if analyzer.function_returns else 0
            ),
            duplicate_blocks=0,  # TODO: Implement duplicate detection
        )

    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return QualityMetrics(
            file_path=str(file_path),
            lines_of_code=0,
            cyclomatic_complexity=0,
            function_count=0,
            class_count=0,
            max_function_complexity=0,
            max_function_parameters=0,
            max_function_returns=0,
            duplicate_blocks=0,
        )


def analyze_directory(directory: Path) -> list[QualityMetrics]:
    """Analyze all Python files in a directory."""
    metrics: list = []

    for py_file in directory.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        file_metrics = analyze_file(py_file)
        metrics.append(file_metrics)

    return metrics


def generate_report(metrics: list[QualityMetrics]) -> dict[str, Any]:
    """Generate a quality report from metrics."""
    if not metrics:
        return {}

    total_loc = sum(m.lines_of_code for m in metrics)
    total_complexity = sum(m.cyclomatic_complexity for m in metrics)
    total_functions = sum(m.function_count for m in metrics)
    total_classes = sum(m.class_count for m in metrics)

    # Find problematic files
    high_complexity_files = [
        m
        for m in metrics
        if m.max_function_complexity > 15 or m.cyclomatic_complexity > 50
    ]

    high_parameter_files = [m for m in metrics if m.max_function_parameters > 6]

    high_return_files = [m for m in metrics if m.max_function_returns > 6]

    return {
        "summary": {
            "total_files": len(metrics),
            "total_lines_of_code": total_loc,
            "total_complexity": total_complexity,
            "total_functions": total_functions,
            "total_classes": total_classes,
            "average_complexity_per_file": total_complexity / len(metrics),
            "average_functions_per_file": total_functions / len(metrics),
        },
        "issues": {
            "high_complexity_files": len(high_complexity_files),
            "high_parameter_files": len(high_parameter_files),
            "high_return_files": len(high_return_files),
        },
        "problematic_files": {
            "high_complexity": [m.file_path for m in high_complexity_files],
            "high_parameters": [m.file_path for m in high_parameter_files],
            "high_returns": [m.file_path for m in high_return_files],
        },
        "detailed_metrics": [m.to_dict() for m in metrics],
    }


def save_baseline(metrics: list[QualityMetrics], baseline_file: Path) -> None:
    """Save quality metrics as baseline."""
    report = generate_report(metrics)

    with open(baseline_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Baseline saved to {baseline_file}")


def compare_with_baseline(
    current_metrics: list[QualityMetrics],
    baseline_file: Path,
) -> tuple[bool, dict[str, Any]]:
    """Compare current metrics with baseline."""
    if not baseline_file.exists():
        print(f"Baseline file {baseline_file} not found. Creating new baseline.")
        save_baseline(current_metrics, baseline_file)
        return True, {}

    with open(baseline_file, encoding="utf-8") as f:
        baseline = json.load(f)

    current_report = generate_report(current_metrics)

    # Compare key metrics
    comparison = {
        "complexity_change": (
            current_report["summary"]["total_complexity"]
            - baseline["summary"]["total_complexity"]
        ),
        "high_complexity_files_change": (
            current_report["issues"]["high_complexity_files"]
            - baseline["issues"]["high_complexity_files"]
        ),
        "high_parameter_files_change": (
            current_report["issues"]["high_parameter_files"]
            - baseline["issues"]["high_parameter_files"]
        ),
        "high_return_files_change": (
            current_report["issues"]["high_return_files"]
            - baseline["issues"]["high_return_files"]
        ),
    }

    # Check for regressions
    has_regression = (
        comparison["complexity_change"] > 10
        or comparison["high_complexity_files_change"] > 0
        or comparison["high_parameter_files_change"] > 0
        or comparison["high_return_files_change"] > 0
    )

    return not has_regression, comparison


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser(description="Monitor code quality metrics")
    parser.add_argument("directory", type=Path, help="Directory to analyze")
    parser.add_argument(
        "--baseline",
        type=Path,
        default=Path("quality_baseline.json"),
        help="Baseline file path",
    )
    parser.add_argument(
        "--save-baseline",
        action="store_true",
        help="Save current metrics as baseline",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check against baseline and exit with error if regression",
    )
    parser.add_argument("--report", type=Path, help="Save detailed report to file")

    args = parser.parse_args()

    if not args.directory.exists():
        print(f"Directory {args.directory} does not exist")
        sys.exit(1)

    print(f"Analyzing {args.directory}...")
    metrics = analyze_directory(args.directory)

    if args.save_baseline:
        save_baseline(metrics, args.baseline)
        return

    report = generate_report(metrics)

    # Print summary
    print("\n=== Quality Report ===")
    print(f"Files analyzed: {report['summary']['total_files']}")
    print(f"Total lines of code: {report['summary']['total_lines_of_code']}")
    print(f"Total complexity: {report['summary']['total_complexity']}")
    print(
        f"Average complexity per file: {
            report['summary']['average_complexity_per_file']:.2f
        }",
    )

    print("\n=== Issues ===")
    print(f"High complexity files: {report['issues']['high_complexity_files']}")
    print(f"High parameter files: {report['issues']['high_parameter_files']}")
    print(f"High return files: {report['issues']['high_return_files']}")

    if report["problematic_files"]["high_complexity"]:
        print("\nHigh complexity files:")
        for file_path in report["problematic_files"]["high_complexity"]:
            print(f"  - {file_path}")

    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"\nDetailed report saved to {args.report}")

    if args.check:
        passed, comparison = compare_with_baseline(metrics, args.baseline)

        if not passed:
            print("\n❌ Quality regression detected!")
            print(f"Complexity change: {comparison['complexity_change']}")
            print(
                f"High complexity files change: {
                    comparison['high_complexity_files_change']
                }",
            )
            print(
                f"High parameter files change: {
                    comparison['high_parameter_files_change']
                }",
            )
            print(f"High return files change: {comparison['high_return_files_change']}")
            sys.exit(1)
            print("\n✅ Quality check passed!")


if __name__ == "__main__":
    main()
