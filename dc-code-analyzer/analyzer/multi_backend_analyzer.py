"""Multi-backend analyzer orchestrator."""

from __future__ import annotations

import logging
import time
from pathlib import Path

from django.utils import timezone

from .backends import AnalysisResult, get_backend
from .models import (  # New backend management models
    AnalysisBackendModel,
    AnalysisSession,
    BackendStatistics,
    ClassAnalysis,
    DetectedIssue,
    FileAnalysis,
    FunctionAnalysis,
    ImportAnalysis,
    IssueType,
    PackageAnalysis,
    QualityMetrics,
    SecurityIssue,
    VariableAnalysis,
)

logger = logging.getLogger(__name__)


class MultiBackendAnalyzer:
    """Orchestrates analysis across multiple backends."""

    def __init__(self, flx_project, backend_names: list[str] | None = None):
        self.flx_project = flx_project
        self.backend_names = backend_names or ["ast", "external", "quality"]
        self.session: AnalysisSession | None = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def analyze(self) -> AnalysisSession:
        """Run analysis using all configured backends."""
        self.logger.info(
            f"Starting multi-backend analysis for flx_project: {self.flx_project.name}",
        )

        # Create analysis session
        self.session = AnalysisSession.objects.create(
            flx_project=self.flx_project,
            status="running",
            backends_used=self.backend_names,
            started_at=timezone.now(),
        )

        try:
            # Find Python files
            project_path = Path(self.flx_project.path)
            python_files = self._find_python_files(project_path)

            if not python_files:
                assert self.session is not None
                self.session.status = "completed"
                self.session.completed_at = timezone.now()
                self.session.error_message = "No Python files found"
                self.session.save()
                return self.session

            self.logger.info(f"Found {len(python_files)} Python files to analyze")

            # Run backends and collect statistics
            combined_result = AnalysisResult()
            backend_stats = {}

            for backend_name in self.backend_names:
                start_time = time.time()
                backend_model = self._get_or_create_backend_model(backend_name)

                try:
                    backend_class = get_backend(backend_name)
                    backend = backend_class(self.session, project_path)

                    if not backend.is_available():
                        execution_time = time.time() - start_time
                        self.logger.warning(
                            f"Backend {backend_name} is not available, skipping",
                        )

                        # Track skipped statistics
                        backend_stats[backend_name] = {
                            "backend_model": backend_model,
                            "execution_time": execution_time,
                            "files_processed": 0,
                            "issues_found": 0,
                            "status": "skipped",
                            "error_message": "Backend not available",
                            "result": None,
                        }
                        continue

                    self.logger.info(f"Running backend: {backend_name}")
                    result = backend.analyze(python_files)
                    execution_time = time.time() - start_time

                    combined_result.merge(result)

                    # Track successful statistics
                    backend_stats[backend_name] = {
                        "backend_model": backend_model,
                        "execution_time": execution_time,
                        "files_processed": len(python_files),
                        "issues_found": len(result.security_issues)
                        + len(
                            [
                                e
                                for e in result.errors
                                if isinstance(e, dict)
                                and e.get("backend") == backend_name
                            ],
                        ),
                        "status": "success",
                        "error_message": "",
                        "result": result,
                    }

                except Exception as e:
                    execution_time = time.time() - start_time
                    error_msg = str(e)

                    self.logger.exception(f"Backend {backend_name} failed: {e}")
                    combined_result.errors.append(
                        {"backend": backend_name, "error": error_msg},
                    )

                    # Track failed statistics
                    backend_stats[backend_name] = {
                        "backend_model": backend_model,
                        "execution_time": execution_time,
                        "files_processed": 0,
                        "issues_found": 0,
                        "status": "failed",
                        "error_message": error_msg,
                        "result": None,
                    }

            # Save results to database
            self._save_results(combined_result, backend_stats)

            # Update session
            assert self.session is not None
            
            # Check if all backends failed - if so, mark analysis as failed
            successful_backends = [
                name for name, stats in backend_stats.items() 
                if stats["status"] == "success"
            ]
            
            # Only mark as failed if ALL backends failed AND we attempted multiple backends
            if not successful_backends and backend_stats and len(self.backend_names) > 1:
                self.session.status = "failed"
                self.session.error_message = "All backends failed to execute"
            else:
                self.session.status = "completed"
                if combined_result.errors:
                    self.session.error_message = (
                        f"Analysis completed with {len(combined_result.errors)} errors"
                    )
            
            self.session.completed_at = timezone.now()
            self.session.files_analyzed = len(python_files)
            self.session.save()

            self.logger.info(
                f"Analysis completed for flx_project: {self.flx_project.name}",
            )

        except Exception as e:
            self.logger.exception(f"Analysis failed: {e}")
            assert self.session is not None
            self.session.status = "failed"
            self.session.completed_at = timezone.now()
            self.session.error_message = str(e)
            self.session.save()

        return self.session

    def _find_python_files(self, path: Path) -> list[Path]:
        """Find all Python files in the flx_project directory."""
        python_files = []
        try:
            for py_file in path.rglob("*.py"):
                # Skip hidden files, __pycache__, .venv, etc.
                if not any(
                    part.startswith(".") or part == "__pycache__"
                    for part in py_file.parts
                ):
                    python_files.append(py_file)
        except Exception as e:
            self.logger.exception(f"Error finding Python files: {e}")

        return python_files

    def _get_or_create_backend_model(self, backend_name: str) -> AnalysisBackendModel:
        """Get or create backend model for tracking."""
        # Format display name: capitalize first letter only, keep underscores as-is
        display_name = backend_name.capitalize()
        
        backend_model, _created = AnalysisBackendModel.objects.get_or_create(
            name=backend_name,
            defaults={
                "display_name": display_name,
                "description": f"Backend {backend_name}",
                "is_active": True,
                "is_available": True,
            },
        )
        return backend_model

    def _save_results(
        self, result: AnalysisResult, backend_stats: dict | None = None
    ) -> None:
        """Save analysis results to the database."""
        assert self.session is not None
        self.logger.info("Saving analysis results to database")

        # Save all data components
        package_objects = self._save_packages(result)
        file_objects = self._save_files(result, package_objects)
        class_objects = self._save_classes(result, file_objects, package_objects)
        self._save_functions(result, file_objects, package_objects, class_objects)
        self._save_variables(result, file_objects, package_objects, class_objects)
        self._save_imports(result, file_objects, package_objects)
        self._save_security_issues(result)
        self._save_quality_metrics(result)
        self._save_detected_issues(result, file_objects)

        # Save backend statistics if provided
        if backend_stats:
            self._save_backend_statistics(backend_stats)

        self.logger.info("Analysis results saved successfully")

    def _save_packages(self, result: AnalysisResult) -> dict[str, PackageAnalysis]:
        """Save package analysis data."""
        package_objects = {}
        for pkg_data in result.packages:
            package_obj = PackageAnalysis.objects.create(
                session=self.session,
                name=pkg_data["name"],
                full_path=pkg_data["full_path"],
                python_files_count=pkg_data.get("python_files_count", 0),
                total_lines=pkg_data.get("total_lines", 0),
                code_lines=pkg_data.get("code_lines", 0),
                comment_lines=pkg_data.get("comment_lines", 0),
                blank_lines=pkg_data.get("blank_lines", 0),
                avg_complexity=pkg_data.get("avg_complexity", 0.0),
                max_complexity=pkg_data.get("max_complexity", 0.0),
                total_functions=pkg_data.get("total_functions", 0),
                total_classes=pkg_data.get("total_classes", 0),
            )
            package_objects[pkg_data["name"]] = package_obj
        return package_objects

    def _save_files(
        self,
        result: AnalysisResult,
        _package_objects: dict[str, PackageAnalysis],
    ) -> dict[str, FileAnalysis]:
        """Save file analysis data."""
        file_objects = {}
        for file_data in result.files:
            file_obj = FileAnalysis.objects.create(
                session=self.session,
                file_path=file_data["file_path"],
                file_name=file_data["file_name"],
                lines_of_code=file_data.get("lines_of_code", 0),
                comment_lines=file_data.get("comment_lines", 0),
                blank_lines=file_data.get("blank_lines", 0),
                complexity_score=file_data.get("complexity_score", 0.0),
                maintainability_score=file_data.get("maintainability_score", 0.0),
                function_count=file_data.get("function_count", 0),
                class_count=file_data.get("class_count", 0),
            )
            file_objects[file_data["file_path"]] = file_obj
        return file_objects

    def _save_classes(
        self,
        result: AnalysisResult,
        file_objects: dict[str, FileAnalysis],
        package_objects: dict[str, PackageAnalysis],
    ) -> dict[str, ClassAnalysis]:
        """Save class analysis data."""
        class_objects = {}
        for class_data in result.classes:
            file_obj = self._find_file_object(file_objects, class_data)
            package_obj = self._find_package_object(package_objects, class_data)

            if file_obj and package_obj:
                class_obj, _created = ClassAnalysis.objects.get_or_create(
                    file_analysis=file_obj,
                    name=class_data["name"],
                    line_start=class_data["line_start"],
                    defaults={
                        "package_analysis": package_obj,
                        "full_name": class_data["full_name"],
                        "line_end": class_data["line_end"],
                        "lines_of_code": class_data.get("lines_of_code", 0),
                        "method_count": class_data.get("method_count", 0),
                        "property_count": class_data.get("property_count", 0),
                        "class_method_count": class_data.get("class_method_count", 0),
                        "static_method_count": class_data.get("static_method_count", 0),
                        "base_classes": class_data.get("base_classes", []),
                        "inheritance_depth": class_data.get("inheritance_depth", 0),
                        "has_docstring": class_data.get("has_docstring", False),
                        "docstring_length": class_data.get("docstring_length", 0),
                        "is_abstract": class_data.get("is_abstract", False),
                        "is_dataclass": class_data.get("is_dataclass", False),
                    },
                )
                class_objects[class_data["full_name"]] = class_obj
        return class_objects

    def _save_functions(
        self,
        result: AnalysisResult,
        file_objects: dict[str, FileAnalysis],
        package_objects: dict[str, PackageAnalysis],
        class_objects: dict[str, ClassAnalysis],
    ) -> None:
        """Save function analysis data."""
        for func_data in result.functions:
            file_obj = self._find_file_object(file_objects, func_data)
            package_obj = self._find_package_object(package_objects, func_data)
            class_obj = class_objects.get(func_data.get("class_name", ""))

            if file_obj and package_obj:
                FunctionAnalysis.objects.get_or_create(
                    file_analysis=file_obj,
                    name=func_data["name"],
                    line_start=func_data["line_start"],
                    defaults={
                        "class_analysis": class_obj,
                        "package_analysis": package_obj,
                        "full_name": func_data["full_name"],
                        "function_type": func_data.get("function_type", "function"),
                        "line_end": func_data["line_end"],
                        "lines_of_code": func_data.get("lines_of_code", 0),
                        "parameter_count": func_data.get("parameter_count", 0),
                        "return_statement_count": func_data.get(
                            "return_statement_count",
                            0,
                        ),
                        "cyclomatic_complexity": func_data.get(
                            "cyclomatic_complexity",
                            1,
                        ),
                        "complexity_level": func_data.get("complexity_level", "low"),
                        "has_docstring": func_data.get("has_docstring", False),
                        "has_type_hints": func_data.get("has_type_hints", False),
                        "docstring_length": func_data.get("docstring_length", 0),
                    },
                )

    def _save_variables(
        self,
        result: AnalysisResult,
        file_objects: dict[str, FileAnalysis],
        package_objects: dict[str, PackageAnalysis],
        class_objects: dict[str, ClassAnalysis],
    ) -> None:
        """Save variable analysis data."""
        for var_data in result.variables:
            file_obj = self._find_file_object(file_objects, var_data)
            package_obj = self._find_package_object(package_objects, var_data)
            class_obj = class_objects.get(var_data.get("class_name", ""))

            if file_obj and package_obj:
                VariableAnalysis.objects.get_or_create(
                    file_analysis=file_obj,
                    name=var_data["name"],
                    line_number=var_data["line_number"],
                    defaults={
                        "class_analysis": class_obj,
                        "package_analysis": package_obj,
                        "full_name": var_data["full_name"],
                        "variable_type": var_data.get("variable_type", "local_var"),
                        "scope_type": var_data.get("scope_type", "function"),
                        "is_constant": var_data.get("is_constant", False),
                    },
                )

    def _save_imports(
        self,
        result: AnalysisResult,
        file_objects: dict[str, FileAnalysis],
        package_objects: dict[str, PackageAnalysis],
    ) -> None:
        """Save import analysis data."""
        for import_data in result.imports:
            file_obj = self._find_file_object(file_objects, import_data)
            package_obj = self._find_package_object(package_objects, import_data)

            if file_obj and package_obj:
                ImportAnalysis.objects.get_or_create(
                    file_analysis=file_obj,
                    module_name=import_data["module_name"],
                    import_name=import_data.get("import_name", ""),
                    line_number=import_data["line_number"],
                    defaults={
                        "package_analysis": package_obj,
                        "alias": import_data.get("alias", ""),
                        "import_type": import_data.get("import_type", "third_party"),
                        "is_wildcard": import_data.get("is_wildcard", False),
                    },
                )

    def _save_security_issues(self, result: AnalysisResult) -> None:
        """Save security issues data."""
        for issue_data in result.security_issues:
            SecurityIssue.objects.create(
                session=self.session,
                file_path=issue_data.get("file_path", ""),
                line_number=issue_data.get("line_number", 0),
                issue_type=issue_data.get("issue_type", ""),
                test_id=issue_data.get("test_id", ""),
                severity=issue_data.get("severity", "MEDIUM"),
                confidence=issue_data.get("confidence", "MEDIUM"),
                description=issue_data.get("description", ""),
                recommendation=issue_data.get("recommendation", ""),
                code_snippet=issue_data.get("code_snippet", ""),
            )

    def _save_quality_metrics(self, result: AnalysisResult) -> None:
        """Save quality metrics data."""
        # Always create quality metrics from analysis result
        QualityMetrics.objects.create(
            session=self.session,
            overall_score=result.quality_metrics.get("overall_score", 0.0),
            complexity_score=result.quality_metrics.get("complexity_score", 0.0),
            maintainability_score=result.quality_metrics.get("maintainability_score", 0.0),
            security_score=result.quality_metrics.get("security_score", 0.0),
            documentation_score=result.quality_metrics.get("documentation_score", 0.0),
            duplication_score=result.quality_metrics.get("duplication_score", 0.0),
            total_files=len(result.files),
            total_lines=sum(f.get("lines_of_code", 0) for f in result.files),
            total_functions=len(result.functions),
            total_classes=len(result.classes),
            avg_complexity=result.quality_metrics.get("avg_complexity", 0.0),
            max_complexity=result.quality_metrics.get("max_complexity", 0.0),
            complex_functions_count=result.quality_metrics.get("complex_functions_count", 0),
            docstring_coverage=result.quality_metrics.get("docstring_coverage", 0.0),
            documented_functions=result.quality_metrics.get("documented_functions", 0),
            security_issues_count=len(result.security_issues),
            dead_code_items_count=result.quality_metrics.get("dead_code_items_count", 0),
            duplicate_blocks_count=result.quality_metrics.get("duplicate_blocks_count", 0),
            duplicate_lines_ratio=result.quality_metrics.get("duplicate_lines_ratio", 0.0),
            technical_debt_ratio=result.quality_metrics.get("technical_debt_ratio", 0.0),
            estimated_debt_hours=result.quality_metrics.get("estimated_debt_hours", 0.0),
        )

    def _find_file_object(self, file_objects: dict, data: dict) -> FileAnalysis | None:
        """Find file object for a data item."""
        # Try to extract file path from the data
        if "file_path" in data:
            return file_objects.get(data["file_path"])

        # For AST data, try to match based on file path in full_name
        full_name = data.get("full_name", "")
        if full_name:
            # Extract likely file path from full_name
            parts = full_name.split(".")
            if len(parts) > 1:
                # Try to find a file that matches the module part
                for file_path, file_obj in file_objects.items():
                    file_path_obj = Path(file_path)
                    file_stem = file_path_obj.stem
                    if file_stem in parts or any(part in file_path for part in parts):
                        return file_obj  # type: ignore[no-any-return]

        return None

    def _find_file_object_by_path(
        self,
        file_objects: dict,
        file_path: str,
    ) -> FileAnalysis | None:
        """Find file object by file path."""
        return file_objects.get(file_path)

    def _find_package_object(
        self,
        package_objects: dict,
        data: dict,
    ) -> PackageAnalysis | None:
        """Find package object for a data item."""
        # First try direct package_name match
        if "package_name" in data:
            package_name = data["package_name"]
            if package_name in package_objects:
                return package_objects[package_name]

        # Extract from full_name
        full_name = data.get("full_name", "")
        if "." in full_name:
            package_name = full_name.split(".")[0]
            if package_name in package_objects:
                return package_objects[package_name]

        # Default to __main__ package if available
        if "__main__" in package_objects:
            return package_objects["__main__"]
        
        # Return any available package as fallback
        return next(iter(package_objects.values())) if package_objects else None

    def _save_detected_issues(self, result: AnalysisResult, file_objects: dict):
        """Save detected issues using the new DetectedIssue model."""
        self.logger.info("Saving detected issues to database")

        # Process security issues from external backend
        for issue_data in result.security_issues:
            self._create_detected_issue(
                issue_data=issue_data,
                backend_name="external",
                file_objects=file_objects,
                issue_category="security",
            )

        # Process other issues from results (if they exist)
        for error_data in result.errors:
            if isinstance(error_data, dict) and "backend" in error_data:
                self._create_detected_issue(
                    issue_data=error_data,
                    backend_name=error_data["backend"],
                    file_objects=file_objects,
                    issue_category="quality",
                )

    def _create_detected_issue(
        self,
        issue_data: dict,
        backend_name: str,
        file_objects: dict,
        issue_category: str,
    ):
        """Create a DetectedIssue record with proper issue type mapping."""
        try:
            # Get or create backend model
            backend_model = self._get_or_create_backend_model(backend_name)

            # Determine issue code based on the issue data
            issue_code = self._extract_issue_code(issue_data, backend_name)

            # Find or create the issue type
            issue_type = self._get_or_create_issue_type(
                backend_model=backend_model,
                issue_code=issue_code,
                issue_data=issue_data,
                category=issue_category,
            )

            # Get the file analysis object
            file_path = issue_data.get("file_path", "")
            file_analysis = file_objects.get(file_path)

            # Create the detected issue
            DetectedIssue.objects.create(
                session=self.session,
                issue_type=issue_type,
                file_analysis=file_analysis,
                file_path=file_path,
                line_number=issue_data.get("line_number", 0),
                column=issue_data.get("column", 0),
                message=issue_data.get(
                    "description",
                    issue_data.get("error", "Unknown issue"),
                ),
                code_snippet=issue_data.get("code_snippet", ""),
                confidence=issue_data.get("confidence", "MEDIUM"),
                context=issue_data.get("context", {}),
                raw_data=issue_data,
            )

        except Exception as e:
            self.logger.exception(f"Failed to create detected issue: {e}")

    def _extract_issue_code(self, issue_data: dict, backend_name: str) -> str:
        """Extract issue code from issue data."""
        # Try various fields that might contain the issue code
        if "test_id" in issue_data:
            return str(issue_data["test_id"])
        if "issue_type" in issue_data:
            return str(issue_data["issue_type"])
        if "code" in issue_data:
            return str(issue_data["code"])
        # Generate a generic code based on backend
        if backend_name == "external":
            return "EXT001"
        if backend_name == "quality":
            return "Q001"
        if backend_name == "ast":
            return "AST001"
        return "GEN001"

    def _get_or_create_issue_type(
        self,
        backend_model: AnalysisBackendModel,
        issue_code: str,
        issue_data: dict,
        category: str,
    ) -> IssueType:
        """Get or create an issue type for the detected issue."""
        issue_type, created = IssueType.objects.get_or_create(
            backend=backend_model,
            code=issue_code,
            defaults={
                "name": issue_data.get("issue_type", f"Issue {issue_code}"),
                "description": issue_data.get(
                    "description",
                    "Issue detected during analysis",
                ),
                "category": category,
                "severity": issue_data.get("severity", "MEDIUM").upper(),
                "recommendation": issue_data.get("recommendation", ""),
                "is_active": True,
            },
        )

        if created:
            self.logger.info(
                f"Created new issue type: {backend_model.name}:{issue_code}",
            )

        return issue_type

    def _save_backend_statistics(self, backend_stats: dict):
        """Save backend execution statistics."""
        self.logger.info("Saving backend statistics to database")

        for backend_name, stats in backend_stats.items():
            try:
                # Calculate issues breakdown
                issues_by_severity: dict[str, int] = {}
                issues_by_category: dict[str, int] = {}

                if stats.get("result"):
                    result = stats["result"]

                    # Count security issues by severity
                    for issue in result.security_issues:
                        severity = issue.get("severity", "MEDIUM")
                        issues_by_severity[severity] = (
                            issues_by_severity.get(severity, 0) + 1
                        )

                        # Categorize security issues
                        issues_by_category["security"] = (
                            issues_by_category.get("security", 0) + 1
                        )

                    # Count errors by backend
                    for error in result.errors:
                        if (
                            isinstance(error, dict)
                            and error.get("backend") == backend_name
                        ):
                            issues_by_severity["ERROR"] = (
                                issues_by_severity.get("ERROR", 0) + 1
                            )
                            issues_by_category["system"] = (
                                issues_by_category.get("system", 0) + 1
                            )

                # Create the statistics record
                BackendStatistics.objects.create(
                    session=self.session,
                    backend=stats["backend_model"],
                    execution_time=stats["execution_time"],
                    files_processed=stats["files_processed"],
                    issues_found=stats["issues_found"],
                    status=stats["status"],
                    error_message=stats["error_message"],
                    issues_by_severity=issues_by_severity,
                    issues_by_category=issues_by_category,
                )

                self.logger.info(f"Saved statistics for backend: {backend_name}")

            except Exception as e:
                self.logger.exception(
                    f"Failed to save statistics for backend {backend_name}: {e}",
                )
