"""Integrated code analysis engine for Django Code Analyzer."""

from __future__ import annotations

import ast
import logging
from pathlib import Path
from typing import Any

from bandit import config as bandit_config
from bandit.core import manager as bandit_manager
from django.utils import timezone
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from vulture import Vulture

from .models import (
    AnalysisSession,
    DeadCodeIssue,
    DuplicateCodeBlock,
    DuplicateLocation,
    FileAnalysis,
    QualityMetrics,
    SecurityIssue,
)

logger = logging.getLogger(__name__)


class CodeAnalysisEngine:
    """Comprehensive code analysis engine."""

    def __init__(self, session: AnalysisSession):
        self.session = session
        self.flx_project = session.flx_project
        self.project_path = Path(self.flx_project.path)
        self.results: dict[str, Any] = {
            "files_analyzed": 0,
            "total_lines": 0,
            "security_issues": [],
            "dead_code_issues": [],
            "duplicate_blocks": [],
            "quality_metrics": {},
        }

    def run_analysis(self) -> bool:
        """Run complete code analysis."""
        try:
            logger.info(f"Starting analysis for flx_project: {self.flx_project.name}")

            # Update session status
            self.session.status = "running"
            self.session.started_at = timezone.now()
            self.session.save()

            # Run analysis components
            python_files = self._find_python_files()

            if not python_files:
                self._raise_no_files_error()

            # Analyze individual files
            for file_path in python_files:
                self._analyze_file(file_path)

            # Run security analysis if enabled
            if self.session.include_security:
                self._run_security_analysis()

            # Run dead code analysis if enabled
            if self.session.include_dead_code:
                self._run_dead_code_analysis()

            # Run duplicate detection if enabled
            if self.session.include_duplicates:
                self._run_duplicate_analysis()

            # Calculate quality metrics
            self._calculate_quality_metrics()

            # Update session completion
            self.session.status = "completed"
            self.session.completed_at = timezone.now()
            quality_metrics = self.results.get("quality_metrics", {})
            if quality_metrics and isinstance(quality_metrics, dict):
                self.session.overall_score = quality_metrics.get("overall_score", 0.0)
            else:
                self.session.overall_score = 0.0
            self.session.quality_grade = self._calculate_grade(
                self.session.overall_score or 0.0,
            )
            self.session.save()

            logger.info(f"Analysis completed successfully for: {self.flx_project.name}")
            return True
        except Exception as e:
            logger.exception(
                f"Analysis failed for flx_project {self.flx_project.name}: {e}",
            )
            self.session.status = "failed"
            self.session.error_message = str(e)
            self.session.completed_at = timezone.now()
            self.session.save()
            return False

    def _raise_no_files_error(self) -> None:
        """Raise error when no Python files are found."""
        raise ValueError("No Python files found in flx_project path")

    def _find_python_files(self) -> list[Path]:
        """Find all Python files in the flx_project."""
        python_files = []

        if not self.project_path.exists():
            raise FileNotFoundError(f"Project path does not exist: {self.project_path}")

        for py_file in self.project_path.rglob("*.py"):
            # Skip hidden files and directories
            if not any(part.startswith(".") for part in py_file.parts):
                python_files.append(py_file)

        logger.info(f"Found {len(python_files)} Python files")
        return python_files

    def _analyze_file(self, file_path: Path) -> FileAnalysis | None:
        """Analyze a single Python file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Basic file metrics
            lines = content.splitlines()
            lines_of_code = len(
                [
                    line
                    for line in lines
                    if line.strip() and not line.strip().startswith("#")
                ],
            )
            comment_lines = len(
                [line for line in lines if line.strip().startswith("#")],
            )
            blank_lines = len([line for line in lines if not line.strip()])

            # Parse AST for complexity analysis
            try:
                tree = ast.parse(content)
                complexity_data = cc_visit(content)
                maintainability_data = mi_visit(content, multi=True)

                # Count functions and classes
                function_count = len(
                    [
                        node
                        for node in ast.walk(tree)
                        if isinstance(node, ast.FunctionDef)
                    ],
                )
                class_count = len(
                    [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)],
                )

                # Calculate complexity score
                avg_complexity = sum(item.complexity for item in complexity_data) / max(
                    len(complexity_data),
                    1,
                )

            except SyntaxError:
                avg_complexity = 0
                function_count = 0
                class_count = 0
                maintainability_data = 0

            # Create FileAnalysis record
            relative_path = str(file_path.relative_to(self.project_path))

            file_analysis = FileAnalysis.objects.create(
                session=self.session,
                file_path=relative_path,
                file_name=file_path.name,
                lines_of_code=lines_of_code,
                comment_lines=comment_lines,
                blank_lines=blank_lines,
                complexity_score=float(avg_complexity),
                maintainability_score=(
                    float(maintainability_data)
                    if isinstance(maintainability_data, int | float)
                    else 0.0
                ),
                function_count=function_count,
                class_count=class_count,
            )

            self.results["files_analyzed"] = self.results.get("files_analyzed", 0) + 1
            self.results["total_lines"] = self.results.get("total_lines", 0) + len(
                lines
            )

        except Exception as e:
            logger.exception(f"Error analyzing file {file_path}: {e}")
            return None
        else:
            return file_analysis

    def _run_security_analysis(self) -> None:
        """Run Bandit security analysis."""
        try:
            logger.info("Running security analysis with Bandit")

            # Configure Bandit
            config = bandit_config.BanditConfig()
            b_mgr = bandit_manager.BanditManager(config, "file")

            # Scan files
            for py_file in self._find_python_files():
                try:
                    b_mgr.discover_files([str(py_file)])
                except Exception as e:
                    logger.warning(f"Could not scan {py_file}: {e}")
                    continue

            b_mgr.run_tests()

            # Process results
            for result in b_mgr.get_issue_list():
                SecurityIssue.objects.create(
                    session=self.session,
                    severity=result.severity,
                    confidence=result.confidence,
                    issue_type=result.test,
                    test_id=result.test_id,
                    file_path=result.fname,
                    line_number=result.lineno,
                    description=result.text,
                    recommendation=f"Fix {result.test}: {result.text}",
                    code_snippet=result.get_code(max_lines=3, tabbed=False),
                )

            logger.info(f"Found {len(b_mgr.get_issue_list())} security issues")

        except Exception as e:
            logger.exception(f"Security analysis failed: {e}")

    def _run_dead_code_analysis(self) -> None:
        """Run Vulture dead code analysis."""
        try:
            logger.info("Running dead code analysis with Vulture")

            vulture = Vulture()
            vulture.scavenge([str(self.project_path)])

            for item in vulture.unreachable_code:
                DeadCodeIssue.objects.create(
                    session=self.session,
                    dead_type="unreachable",
                    name=str(item),
                    file_path=item.filename if hasattr(item, "filename") else "unknown",
                    line_number=(
                        item.first_lineno if hasattr(item, "first_lineno") else 0
                    ),
                    confidence=1.0,
                    size_estimate=1,
                )

            for item in vulture.unused_code:
                item_type = (
                    "function"
                    if hasattr(item, "typ") and "function" in str(item.typ)
                    else "variable"
                )

                DeadCodeIssue.objects.create(
                    session=self.session,
                    dead_type=item_type,
                    name=item.name if hasattr(item, "name") else str(item),
                    file_path=item.filename if hasattr(item, "filename") else "unknown",
                    line_number=(
                        item.first_lineno if hasattr(item, "first_lineno") else 0
                    ),
                    confidence=item.confidence if hasattr(item, "confidence") else 1.0,
                    size_estimate=1,
                )

            total_issues = len(vulture.unreachable_code) + len(vulture.unused_code)
            logger.info(f"Found {total_issues} dead code issues")

        except Exception as e:
            logger.exception(f"Dead code analysis failed: {e}")

    def _run_duplicate_analysis(self) -> None:
        """Run duplicate code detection."""
        try:
            logger.info("Running duplicate code analysis")

            # Simple duplicate detection based on file similarity
            files_content = {}

            for py_file in self._find_python_files():
                try:
                    with open(py_file, encoding="utf-8") as f:
                        content = f.read()
                        files_content[py_file] = content
                except Exception as e:
                    logger.warning(f"Could not read {py_file}: {e}")
                    continue

            # Find similar files
            similarity_threshold = self.session.similarity_threshold
            compared_pairs = set()

            for file1, content1 in files_content.items():
                for file2, content2 in files_content.items():
                    if file1 >= file2:  # Avoid duplicate comparisons
                        continue

                    pair = tuple(sorted([str(file1), str(file2)]))
                    if pair in compared_pairs:
                        continue
                    compared_pairs.add(pair)

                    # Simple similarity check
                    similarity = self._calculate_similarity(content1, content2)

                    if similarity >= similarity_threshold:
                        # Create duplicate block
                        block = DuplicateCodeBlock.objects.create(
                            session=self.session,
                            block_hash=f"dup_{len(compared_pairs)}",
                            lines_count=min(
                                len(content1.splitlines()),
                                len(content2.splitlines()),
                            ),
                            similarity_score=similarity,
                            content_preview=(
                                content1[:200] + "..."
                                if len(content1) > 200
                                else content1
                            ),
                        )

                        # Create locations
                        for file_path in [file1, file2]:
                            relative_path = str(
                                file_path.relative_to(self.project_path),
                            )
                            content = files_content[file_path]
                            lines = content.splitlines()

                            DuplicateLocation.objects.create(
                                duplicate_block=block,
                                file_path=relative_path,
                                start_line=1,
                                end_line=len(lines),
                            )

            count = DuplicateCodeBlock.objects.filter(session=self.session).count()
            logger.info(f"Found {count} duplicate blocks")

        except Exception as e:
            logger.exception(f"Duplicate analysis failed: {e}")

    def _calculate_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two code contents."""
        from difflib import SequenceMatcher

        # Normalize content
        lines1 = [line.strip() for line in content1.splitlines() if line.strip()]
        lines2 = [line.strip() for line in content2.splitlines() if line.strip()]

        matcher = SequenceMatcher(None, lines1, lines2)
        return matcher.ratio()

    def _calculate_quality_metrics(self) -> None:
        """Calculate overall quality metrics."""
        try:
            # Get file analyses
            file_analyses = FileAnalysis.objects.filter(session=self.session)

            if not file_analyses.exists():
                return

            # Basic metrics
            total_files = file_analyses.count()
            total_lines = sum(fa.lines_of_code for fa in file_analyses)
            total_functions = sum(fa.function_count for fa in file_analyses)
            total_classes = sum(fa.class_count for fa in file_analyses)

            # Complexity metrics
            avg_complexity = (
                sum(fa.complexity_score for fa in file_analyses) / total_files
            )
            max_complexity = max(fa.complexity_score for fa in file_analyses)
            complex_functions_count = sum(
                1
                for fa in file_analyses
                if fa.complexity_score > self.session.complexity_threshold
            )

            # Issue counts
            security_issues_count = SecurityIssue.objects.filter(
                session=self.session,
            ).count()
            dead_code_items_count = DeadCodeIssue.objects.filter(
                session=self.session,
            ).count()
            duplicate_blocks_count = DuplicateCodeBlock.objects.filter(
                session=self.session,
            ).count()

            # Calculate component scores (0-100)
            complexity_score = max(0, 100 - (avg_complexity * 10))
            security_score = max(0, 100 - (security_issues_count * 5))
            maintainability_score = max(0, 100 - (complex_functions_count * 10))
            duplication_score = max(0, 100 - (duplicate_blocks_count * 10))
            documentation_score = 75  # Placeholder - could be enhanced

            # Overall score (weighted average)
            overall_score = (
                complexity_score * 0.25
                + security_score * 0.25
                + maintainability_score * 0.2
                + duplication_score * 0.15
                + documentation_score * 0.15
            )

            # Create QualityMetrics record
            QualityMetrics.objects.create(
                session=self.session,
                overall_score=overall_score,
                complexity_score=complexity_score,
                maintainability_score=maintainability_score,
                security_score=security_score,
                documentation_score=documentation_score,
                duplication_score=duplication_score,
                total_files=total_files,
                total_lines=total_lines,
                total_functions=total_functions,
                total_classes=total_classes,
                avg_complexity=avg_complexity,
                max_complexity=max_complexity,
                complex_functions_count=complex_functions_count,
                docstring_coverage=0.5,  # Placeholder
                documented_functions=int(total_functions * 0.5),  # Placeholder
                security_issues_count=security_issues_count,
                dead_code_items_count=dead_code_items_count,
                duplicate_blocks_count=duplicate_blocks_count,
                duplicate_lines_ratio=0.1,  # Placeholder
                technical_debt_ratio=max_complexity / 10 if max_complexity > 0 else 0,
                estimated_debt_hours=complex_functions_count * 2,
            )

            self.results["quality_metrics"] = {
                "overall_score": overall_score,
                "complexity_score": complexity_score,
                "security_score": security_score,
                "maintainability_score": maintainability_score,
                "duplication_score": duplication_score,
                "documentation_score": documentation_score,
            }

            logger.info(
                f"Quality metrics calculated. Overall score: {overall_score:.1f}",
            )

        except Exception as e:
            logger.exception(f"Quality metrics calculation failed: {e}")

    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from numeric score."""
        grade_thresholds = [
            (90, "A+"),
            (85, "A"),
            (80, "A-"),
            (75, "B+"),
            (70, "B"),
            (65, "B-"),
            (60, "C+"),
            (55, "C"),
            (50, "C-"),
            (45, "D+"),
            (40, "D"),
        ]

        for threshold, grade in grade_thresholds:
            if score >= threshold:
                return grade
        return "F"
