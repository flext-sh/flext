"""Asynchronous tasks for code analysis."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from django.conf import settings
from django.utils import timezone

from .models import (
    AnalysisSession,
    DeadCodeIssue,
    DuplicateCodeBlock,
    DuplicateLocation,
    FileAnalysis,
    QualityMetrics,
    SecurityIssue,
)

# Import the existing code analyzer
try:
    from code_analyzer.core.advanced_analyzer import (
        AdvancedCodeAnalyzer,  # type: ignore[import-not-found]
    )
    from code_analyzer.utils.config import (
        AnalyzerConfig,  # type: ignore[import-not-found]
    )
    from code_analyzer.utils.filesystem import (
        get_python_files,  # type: ignore[import-not-found]
    )
except ImportError:
    # Fallback for when the analyzer is not available
    AdvancedCodeAnalyzer = None
    AnalyzerConfig = None
    get_python_files = None

logger = logging.getLogger(__name__)


def run_code_analysis(session_id: str) -> None:
    """Run code analysis for a session.

    This function can be called synchronously or as a Celery task.
    """
    try:
        session = AnalysisSession.objects.get(id=session_id)
        logger.info(f"Starting analysis for session {session_id}")

        # Update session status
        session.status = "running"
        session.started_at = timezone.now()
        session.save()

        # Configure analyzer
        config = _create_analyzer_config(session)

        # Run analysis
        if AdvancedCodeAnalyzer is None:
            # Fallback to mock analysis for testing
            _run_mock_analysis(session)
        else:
            _run_real_analysis(session, config)

        # Mark as completed
        session.status = "completed"
        session.completed_at = timezone.now()
        session.save()

        logger.info(f"Analysis completed for session {session_id}")

    except AnalysisSession.DoesNotExist:
        logger.exception(f"Analysis session {session_id} not found")
    except Exception as e:
        logger.exception(f"Analysis failed for session {session_id}: {e}")
        try:
            session = AnalysisSession.objects.get(id=session_id)
            session.status = "failed"
            session.error_message = str(e)
            session.completed_at = timezone.now()
            session.save()
        except Exception:
            pass


def _create_analyzer_config(session: AnalysisSession) -> Any:
    """Create analyzer configuration from session settings."""
    if AnalyzerConfig is None:
        return None

    return AnalyzerConfig(
        analysis={
            "include_security": session.include_security,
            "include_dead_code": session.include_dead_code,
            "include_duplicates": session.include_duplicates,
            "include_documentation": True,  # Default value since field doesn't exist
            "include_complexity": True,  # Default value since field doesn't exist
            "complexity_threshold": session.complexity_threshold,
            "similarity_threshold": session.similarity_threshold,
        },
        paths={
            "source_dir": Path(session.flx_project.path),
            "output_dir": Path(str(settings.CODE_ANALYZER["DEFAULT_OUTPUT_DIR"]))
            / str(session.id),
        },
        performance={
            "max_workers": settings.CODE_ANALYZER["MAX_WORKERS"],
        },
    )


def _run_real_analysis(session: AnalysisSession, config: Any) -> None:
    """Run real code analysis using the advanced analyzer."""
    # Initialize analyzer
    analyzer = AdvancedCodeAnalyzer(
        source_dir=Path(session.flx_project.path),
        config=config,
    )

    # Run analysis
    results = analyzer.analyze()

    # Save results to database
    _save_analysis_results(session, results)


def _run_mock_analysis(session: AnalysisSession) -> None:
    """Run mock analysis for testing purposes."""
    import random
    import time

    # Simulate analysis time
    time.sleep(2)

    # Get Python files from flx_project
    project_path = Path(session.flx_project.path)
    python_files = list(project_path.rglob("*.py")) if project_path.exists() else []

    # Create mock file analyses
    total_lines = 0
    total_functions = 0
    total_classes = 0

    for file_path in python_files[:10]:  # Limit for demo
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = len(f.readlines())
        except Exception:
            lines = random.randint(10, 500)

        file_analysis = FileAnalysis.objects.create(
            session=session,
            file_path=str(file_path.relative_to(project_path)),
            file_name=file_path.name,
            lines_of_code=lines,
            comment_lines=random.randint(5, lines // 4),
            blank_lines=random.randint(3, lines // 6),
            complexity_score=random.uniform(60, 95),
            maintainability_score=random.uniform(65, 90),
            function_count=random.randint(1, 10),
            class_count=random.randint(0, 3),
        )

        total_lines += lines
        total_functions += file_analysis.function_count
        total_classes += file_analysis.class_count

        # Create some mock security issues
        if session.include_security and random.random() < 0.3:
            SecurityIssue.objects.create(
                session=session,
                severity=random.choice(["HIGH", "MEDIUM", "LOW"]),
                confidence=random.choice(["HIGH", "MEDIUM", "LOW"]),
                issue_type="hardcoded_password",
                test_id="B105",
                file_path=file_analysis.file_path,
                line_number=random.randint(1, lines),
                description="Possible hardcoded password found",
                recommendation="Use environment variables for sensitive data",
            )

        # Create some mock dead code issues
        if session.include_dead_code and random.random() < 0.4:
            DeadCodeIssue.objects.create(
                session=session,
                dead_type=random.choice(["function", "variable", "import"]),
                name=f"unused_{random.choice(['helper', 'utility', 'temp'])}",
                file_path=file_analysis.file_path,
                line_number=random.randint(1, lines),
                confidence=random.uniform(0.7, 1.0),
                size_estimate=random.randint(1, 20),
            )

    # Create mock duplicate blocks
    if session.include_duplicates:
        for _ in range(random.randint(1, 5)):
            block = DuplicateCodeBlock.objects.create(
                session=session,
                block_hash=f"hash_{random.randint(100000, 999999)}",
                lines_count=random.randint(5, 50),
                similarity_score=random.uniform(0.8, 1.0),
                content_preview="def example_function():\n    # Duplicate code detected\n    pass",
            )

            # Add locations for this duplicate block
            for file_analysis in random.sample(
                list(session.file_analyses.all()),
                min(2, session.file_analyses.count()),
            ):
                DuplicateLocation.objects.create(
                    duplicate_block=block,
                    file_path=file_analysis.file_path,
                    start_line=random.randint(
                        1,
                        max(1, file_analysis.lines_of_code - block.lines_count),
                    ),
                    end_line=random.randint(1, file_analysis.lines_of_code),
                )

    # Create quality metrics
    security_issues_count = session.security_issues.count()
    dead_code_count = session.dead_code_issues.count()
    duplicate_blocks_count = session.duplicate_blocks.count()

    # Calculate mock scores
    overall_score = random.uniform(70, 95)
    complexity_score = random.uniform(75, 90)
    security_score = max(50, 100 - (security_issues_count * 10))

    QualityMetrics.objects.create(
        session=session,
        overall_score=overall_score,
        complexity_score=complexity_score,
        maintainability_score=random.uniform(70, 85),
        security_score=security_score,
        duplication_score=max(50, 100 - (duplicate_blocks_count * 15)),
        total_files=len(python_files),
        total_lines=total_lines,
        total_functions=total_functions,
        total_classes=total_classes,
        avg_complexity=random.uniform(5, 15),
        max_complexity=random.uniform(15, 30),
        complex_functions_count=random.randint(0, 5),
        docstring_coverage=random.uniform(0.4, 0.9),
        documented_functions=random.randint(total_functions // 2, total_functions),
        security_issues_count=security_issues_count,
        dead_code_items_count=dead_code_count,
        duplicate_blocks_count=duplicate_blocks_count,
        duplicate_lines_ratio=random.uniform(0.02, 0.15),
        technical_debt_ratio=random.uniform(0.1, 0.4),
        estimated_debt_hours=random.uniform(5, 50),
    )


def _save_analysis_results(session: AnalysisSession, results: dict[str, Any]) -> None:
    """Save analysis results to database."""
    # Save file analyses
    for file_path, file_data in results.get("files", {}).items():
        FileAnalysis.objects.create(
            session=session,
            file_path=str(file_path),
            file_name=Path(file_path).name,
            lines_of_code=file_data.get("lines_of_code", 0),
            comment_lines=file_data.get("comment_lines", 0),
            blank_lines=file_data.get("blank_lines", 0),
            complexity_score=file_data.get("complexity_score", 0),
            maintainability_score=file_data.get("maintainability_score", 0),
            function_count=file_data.get("function_count", 0),
            class_count=file_data.get("class_count", 0),
        )

    # Save security issues
    for issue_data in results.get("security_issues", []):
        SecurityIssue.objects.create(
            session=session,
            severity=issue_data.severity,
            confidence=issue_data.confidence,
            issue_type=issue_data.type,
            test_id=getattr(issue_data, "test_id", ""),
            file_path=issue_data.file_path,
            line_number=issue_data.line_number,
            description=issue_data.description,
            recommendation=issue_data.recommendation,
        )

    # Save dead code issues
    for issue_data in results.get("dead_code_issues", []):
        DeadCodeIssue.objects.create(
            session=session,
            dead_type=issue_data.type,
            name=issue_data.name,
            file_path=issue_data.file_path,
            line_number=issue_data.line_number,
            confidence=issue_data.confidence,
        )

    # Save duplicate blocks
    for block_data in results.get("duplicate_blocks", []):
        duplicate_block = DuplicateCodeBlock.objects.create(
            session=session,
            block_hash=block_data.hash,
            lines_count=block_data.lines_count,
            similarity_score=block_data.similarity_score,
            content_preview=block_data.content_preview,
        )

        # Save duplicate locations
        for location_data in block_data.locations:
            DuplicateLocation.objects.create(
                duplicate_block=duplicate_block,
                file_path=location_data["file_path"],
                start_line=location_data["start_line"],
                end_line=location_data["end_line"],
            )

    # Save quality metrics
    if "quality_metrics" in results:
        metrics = results["quality_metrics"]
        QualityMetrics.objects.create(
            session=session,
            overall_score=metrics.overall_score,
            complexity_score=metrics.complexity_score,
            maintainability_score=metrics.maintainability_score,
            security_score=metrics.security_score,
            duplication_score=metrics.duplication_score,
            total_files=metrics.size_metrics.total_files,
            total_lines=metrics.size_metrics.total_lines,
            total_functions=metrics.size_metrics.total_functions,
            total_classes=metrics.size_metrics.total_classes,
            avg_complexity=metrics.complexity_metrics.average,
            max_complexity=metrics.complexity_metrics.maximum,
            complex_functions_count=metrics.complexity_metrics.functions_over_threshold,
            docstring_coverage=metrics.quality_indicators.docstring_coverage,
            documented_functions=getattr(
                metrics.quality_indicators,
                "documented_functions",
                0,
            ),
            security_issues_count=metrics.quality_indicators.security_issues_count,
            dead_code_items_count=metrics.quality_indicators.unused_functions_count,
            duplicate_blocks_count=len(results.get("duplicate_blocks", [])),
            duplicate_lines_ratio=metrics.quality_indicators.duplicate_lines_ratio,
            technical_debt_ratio=getattr(metrics, "technical_debt_ratio", 0.1),
            estimated_debt_hours=getattr(metrics, "estimated_debt_hours", 10.0),
        )


# For Celery integration (when available)
try:
    from celery import shared_task

    # Make run_code_analysis itself a shared task
    run_code_analysis = shared_task(run_code_analysis)

    @shared_task
    def run_code_analysis_async(session_id: str) -> None:
        """Celery task wrapper for code analysis."""
        return run_code_analysis(session_id)

    @shared_task(bind=True, name="analyzer.run_analysis_task")
    def run_analysis_task(
        self,
        session_id: int,
        backend_names: list[str] | None = None,
    ):
        """Run analysis in background using new multi-backend system."""
        from .multi_backend_analyzer import MultiBackendAnalyzer

        try:
            # Update task status
            self.update_state(state="PROGRESS", meta={"status": "Starting analysis..."})

            # Get session and flx_project
            session = AnalysisSession.objects.get(id=session_id)
            flx_project = session.flx_project

            logger.info(
                f"Starting background analysis for session {session_id}, flx_project: {flx_project.name}"
            )

            # Update session status
            session.status = "running"
            session.started_at = timezone.now()
            session.save()

            # Update task status
            self.update_state(
                state="PROGRESS",
                meta={
                    "status": "Initializing backends...",
                    "session_id": session_id,
                    "project_name": flx_project.name,
                },
            )

            # Run analysis
            analyzer = MultiBackendAnalyzer(
                flx_project=flx_project,
                backend_names=backend_names or ["ast", "external", "quality"],
            )
            analyzer.session = session  # Use existing session

            # Update task status
            self.update_state(
                state="PROGRESS",
                meta={
                    "status": "Running analysis...",
                    "session_id": session_id,
                    "project_name": flx_project.name,
                },
            )

            # Run the analysis (this will update the session)
            completed_session = analyzer.analyze()

            logger.info(f"Background analysis completed for session {session_id}")

            return {
                "status": "completed",
                "session_id": session_id,
                "project_name": flx_project.name,
                "files_analyzed": completed_session.files_analyzed or 0,
                "issues_found": completed_session.detected_issues.count(),
                "duration": (
                    str(completed_session.duration)
                    if completed_session.duration
                    else None
                ),
            }

        except AnalysisSession.DoesNotExist:
            error_msg = f"Analysis session {session_id} not found"
            logger.exception(error_msg)
            return {"status": "failed", "error": error_msg}

        except Exception as e:
            error_msg = f"Analysis failed for session {session_id}: {str(e)}"
            logger.exception(error_msg)

            # Update session status on failure
            try:
                session = AnalysisSession.objects.get(id=session_id)
                session.status = "failed"
                session.completed_at = timezone.now()
                session.error_message = str(e)
                session.save()
            except AnalysisSession.DoesNotExist:
                pass

            return {"status": "failed", "error": error_msg}

    @shared_task(bind=True, name="analyzer.cleanup_old_sessions")
    def cleanup_old_sessions(_self):
        """Clean up old analysis sessions and their data."""
        from datetime import timedelta

        try:
            # Delete sessions older than 30 days
            cutoff_date = timezone.now() - timedelta(days=30)
            old_sessions = AnalysisSession.objects.filter(created_at__lt=cutoff_date)

            count = old_sessions.count()
            old_sessions.delete()

            logger.info(f"Cleaned up {count} old analysis sessions")
        except Exception as e:
            error_msg = f"Cleanup failed: {str(e)}"
            logger.exception(error_msg)
            return {"status": "failed", "error": error_msg}
        else:
            return {"status": "completed", "cleaned_sessions": count}

except ImportError:
    # Celery not available, create a mock delay function
    class MockTask:
        def delay(self, session_id: str) -> None:
            # Run synchronously if Celery is not available
            run_code_analysis(session_id)

    run_code_analysis.delay = MockTask().delay  # type: ignore[attr-defined]
    run_analysis_task = MockTask()
    cleanup_old_sessions = MockTask()
