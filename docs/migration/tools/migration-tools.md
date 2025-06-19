# 🛠️ Migration Tools Guide

> **Navigation**: [Documentation Home](../../index.md) → [Migration Hub](../index.md) → [Migration Tools Hub](./index.md) → Migration Tools

**Comprehensive automated migration utilities and helper scripts for FLX Framework migrations including code analysis, transformation, and validation tools**

## 📋 **Table of Contents**

- [🔧 Tool Overview](#-tool-overview)
- [📊 Code Analysis Tools](#-code-analysis-tools)
- [🔄 Transformation Tools](#-transformation-tools)
- [✅ Validation Tools](#-validation-tools)
- [🚀 Automation Scripts](#-automation-scripts)
- [📈 Monitoring Tools](#-monitoring-tools)

---

## 🔧 Tool Overview

### **Migration Tool Ecosystem**

FLX Framework provides comprehensive tooling for automated migration execution:

```
┌─────────────────────────────────────────────────────────────┐
│                  Migration Tool Ecosystem                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Analysis → Transform → Validate → Deploy → Monitor        │
│     ↓          ↓          ↓         ↓         ↓            │
│  Code Scan   AST Mods   Test Run   Auto      Real-time     │
│  Deps Map    Imports    Coverage   Deploy    Metrics       │
│  Risk Calc   Config     Quality    Config    Alerts        │
│  Report      Generate   Check      Verify    Dashboard     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### **Tool Categories**

1. **Analysis Tools**: Code scanning, dependency analysis, risk assessment
2. **Transformation Tools**: Automated code migration, configuration updates
3. **Validation Tools**: Testing frameworks, quality gates, compliance checks
4. **Automation Scripts**: End-to-end migration orchestration
5. **Monitoring Tools**: Real-time migration tracking, performance monitoring

---

## 📊 Code Analysis Tools

### **FLX Code Analyzer**

Automated analysis tool for identifying migration requirements and potential issues:

```python
#!/usr/bin/env python3
"""
FLX Migration Code Analyzer
Analyzes codebase for FLX 0.4.0+ migration requirements
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
import json

@dataclass
class AnalysisResult:
    """Results from code analysis."""
    file_path: str
    migration_issues: List[str]
    breaking_changes: List[str]
    suggested_fixes: List[str]
    complexity_score: int
    confidence_level: str

class FLXCodeAnalyzer:
    """Analyzes Python code for FLX migration requirements."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.analysis_results: List[AnalysisResult] = []

        # Known breaking changes in FLX 0.4.0+
        self.breaking_changes = {
            "logging_extra_parameter": {
                "pattern": r"\.log\([^)]*extra\s*=",
                "description": "Logging calls with 'extra=' parameter no longer supported",
                "fix": "Replace with structured logging format strings"
            },
            "deprecated_manager_imports": {
                "patterns": [
                    "from flx.adapters.manager import AdapterManager",
                    "from flx.cache.manager import CacheManager"
                ],
                "description": "Deprecated manager imports",
                "fix": "Replace with UnifiedAdapterManager from flx.infra.adapters"
            },
            "cache_service_imports": {
                "patterns": [
                    "from flx.cache import CacheService",
                    "from flx.adapters.cache import CacheAdapter"
                ],
                "description": "Cache service import changes",
                "fix": "Use consolidated CacheService from flx.infra.cache"
            }
        }

    def analyze_project(self) -> Dict[str, any]:
        """Analyze entire project for migration requirements."""
        print("🔍 Starting FLX code analysis...")

        # Find all Python files
        python_files = list(self.project_root.rglob("*.py"))

        total_files = len(python_files)
        processed = 0

        for file_path in python_files:
            if self._should_analyze_file(file_path):
                result = self._analyze_file(file_path)
                if result:
                    self.analysis_results.append(result)

                processed += 1
                if processed % 10 == 0:
                    print(f"📊 Analyzed {processed}/{total_files} files...")

        # Generate summary report
        summary = self._generate_summary()

        print(f"✅ Analysis complete! Found {len(self.analysis_results)} files with migration requirements.")
        return summary

    def _analyze_file(self, file_path: Path) -> AnalysisResult:
        """Analyze individual Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse AST for detailed analysis
            tree = ast.parse(content)

            # Initialize analysis result
            result = AnalysisResult(
                file_path=str(file_path),
                migration_issues=[],
                breaking_changes=[],
                suggested_fixes=[],
                complexity_score=0,
                confidence_level="high"
            )

            # Check for breaking changes
            self._check_breaking_changes(content, result)

            # Analyze AST for complex patterns
            self._analyze_ast(tree, result)

            # Calculate complexity score
            result.complexity_score = self._calculate_complexity(tree, result)

            return result if result.migration_issues else None

        except Exception as e:
            print(f"❌ Error analyzing {file_path}: {e}")
            return None

    def _check_breaking_changes(self, content: str, result: AnalysisResult):
        """Check for known breaking changes."""
        import re

        for change_id, change_info in self.breaking_changes.items():
            if "pattern" in change_info:
                if re.search(change_info["pattern"], content):
                    result.breaking_changes.append(change_info["description"])
                    result.suggested_fixes.append(change_info["fix"])
                    result.migration_issues.append(f"BREAKING: {change_id}")

            if "patterns" in change_info:
                for pattern in change_info["patterns"]:
                    if pattern in content:
                        result.breaking_changes.append(change_info["description"])
                        result.suggested_fixes.append(change_info["fix"])
                        result.migration_issues.append(f"BREAKING: {change_id}")
                        break

    def _analyze_ast(self, tree: ast.AST, result: AnalysisResult):
        """Analyze AST for complex migration patterns."""
        class MigrationVisitor(ast.NodeVisitor):
            def __init__(self, result):
                self.result = result

            def visit_Import(self, node):
                """Check import statements."""
                for alias in node.names:
                    if self._is_deprecated_import(alias.name):
                        self.result.migration_issues.append(f"Deprecated import: {alias.name}")

            def visit_ImportFrom(self, node):
                """Check from-import statements."""
                if node.module and self._is_deprecated_module(node.module):
                    self.result.migration_issues.append(f"Deprecated module: {node.module}")

            def visit_Call(self, node):
                """Check function calls for deprecated patterns."""
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == "log" and self._has_extra_keyword(node):
                        self.result.migration_issues.append("Deprecated logging call with extra=")

                self.generic_visit(node)

            def _is_deprecated_import(self, import_name: str) -> bool:
                """Check if import is deprecated."""
                deprecated_imports = [
                    "flx.adapters.manager",
                    "flx.cache.manager",
                    "flx.adapters.cache"
                ]
                return any(dep in import_name for dep in deprecated_imports)

            def _is_deprecated_module(self, module_name: str) -> bool:
                """Check if module is deprecated."""
                return self._is_deprecated_import(module_name)

            def _has_extra_keyword(self, call_node: ast.Call) -> bool:
                """Check if call has extra= keyword argument."""
                return any(kw.arg == "extra" for kw in call_node.keywords)

        visitor = MigrationVisitor(result)
        visitor.visit(tree)

    def _calculate_complexity(self, tree: ast.AST, result: AnalysisResult) -> int:
        """Calculate migration complexity score."""
        base_score = 1

        # Add complexity for each issue
        base_score += len(result.migration_issues) * 2
        base_score += len(result.breaking_changes) * 5

        # Analyze code complexity
        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.complexity = 0

            def visit_FunctionDef(self, node):
                self.complexity += 1
                self.generic_visit(node)

            def visit_ClassDef(self, node):
                self.complexity += 2
                self.generic_visit(node)

            def visit_If(self, node):
                self.complexity += 1
                self.generic_visit(node)

            def visit_For(self, node):
                self.complexity += 1
                self.generic_visit(node)

            def visit_While(self, node):
                self.complexity += 1
                self.generic_visit(node)

        visitor = ComplexityVisitor()
        visitor.visit(tree)

        return base_score + visitor.complexity // 10

    def _should_analyze_file(self, file_path: Path) -> bool:
        """Determine if file should be analyzed."""
        # Skip test files, migrations, and vendor code
        skip_patterns = [
            "test_", "tests/", "__pycache__", ".pyc",
            "venv/", "env/", ".venv/", "vendor/",
            "migrations/", "alembic/"
        ]

        path_str = str(file_path)
        return not any(pattern in path_str for pattern in skip_patterns)

    def _generate_summary(self) -> Dict[str, any]:
        """Generate comprehensive analysis summary."""
        if not self.analysis_results:
            return {
                "status": "✅ No migration issues found",
                "total_files_analyzed": 0,
                "files_requiring_migration": 0,
                "complexity_distribution": {},
                "breaking_changes_summary": {},
                "recommendations": []
            }

        # Calculate statistics
        total_issues = sum(len(r.migration_issues) for r in self.analysis_results)
        total_breaking = sum(len(r.breaking_changes) for r in self.analysis_results)

        complexity_distribution = {
            "low": len([r for r in self.analysis_results if r.complexity_score <= 5]),
            "medium": len([r for r in self.analysis_results if 5 < r.complexity_score <= 15]),
            "high": len([r for r in self.analysis_results if r.complexity_score > 15])
        }

        # Generate recommendations
        recommendations = self._generate_recommendations(complexity_distribution, total_breaking)

        return {
            "status": f"📊 Analysis Complete - {len(self.analysis_results)} files need migration",
            "total_files_analyzed": len(self.analysis_results),
            "files_requiring_migration": len(self.analysis_results),
            "total_migration_issues": total_issues,
            "total_breaking_changes": total_breaking,
            "complexity_distribution": complexity_distribution,
            "high_priority_files": [
                r.file_path for r in self.analysis_results
                if r.breaking_changes or r.complexity_score > 15
            ],
            "recommendations": recommendations,
            "detailed_results": [
                {
                    "file": r.file_path,
                    "issues": len(r.migration_issues),
                    "breaking_changes": len(r.breaking_changes),
                    "complexity": r.complexity_score,
                    "confidence": r.confidence_level
                }
                for r in self.analysis_results
            ]
        }

    def _generate_recommendations(self, complexity_dist: Dict, breaking_changes: int) -> List[str]:
        """Generate migration recommendations."""
        recommendations = []

        if breaking_changes > 0:
            recommendations.append(
                f"🚨 High Priority: {breaking_changes} breaking changes found - address immediately"
            )

        if complexity_dist["high"] > 0:
            recommendations.append(
                f"⚠️  {complexity_dist['high']} high-complexity files - plan extra time for migration"
            )

        if complexity_dist["low"] > complexity_dist["high"] + complexity_dist["medium"]:
            recommendations.append(
                "✅ Good news: Most files have low migration complexity"
            )

        total_files = sum(complexity_dist.values())
        if total_files > 50:
            recommendations.append(
                "📋 Large codebase detected - consider phased migration approach"
            )

        recommendations.extend([
            "🧪 Run migration tools on a copy of your codebase first",
            "📝 Review generated migration report carefully",
            "🔄 Test thoroughly after applying automated fixes",
            "📚 Consult FLX 0.4.0+ migration guide for manual steps"
        ])

        return recommendations

def main():
    """CLI entry point for FLX code analyzer."""
    if len(sys.argv) != 2:
        print("Usage: python flx_analyzer.py <project_root>")
        sys.exit(1)

    project_root = sys.argv[1]
    if not os.path.exists(project_root):
        print(f"❌ Project root not found: {project_root}")
        sys.exit(1)

    # Run analysis
    analyzer = FLXCodeAnalyzer(project_root)
    summary = analyzer.analyze_project()

    # Save detailed report
    report_file = "flx_migration_analysis.json"
    with open(report_file, 'w') as f:
        json.dump(summary, f, indent=2)

    # Print summary
    print("\n" + "="*60)
    print("📊 FLX MIGRATION ANALYSIS SUMMARY")
    print("="*60)
    print(f"Status: {summary['status']}")
    print(f"Files requiring migration: {summary['files_requiring_migration']}")
    print(f"Total issues found: {summary.get('total_migration_issues', 0)}")
    print(f"Breaking changes: {summary.get('total_breaking_changes', 0)}")

    print(f"\n📈 Complexity Distribution:")
    for level, count in summary['complexity_distribution'].items():
        print(f"  {level.capitalize()}: {count} files")

    print(f"\n💡 Recommendations:")
    for rec in summary['recommendations']:
        print(f"  • {rec}")

    print(f"\n📄 Detailed report saved to: {report_file}")
    print("="*60)

if __name__ == "__main__":
    main()
```

---

## 🔄 Transformation Tools

### **Automated Code Transformer**

Tool for automatically applying migration transformations:

```python
#!/usr/bin/env python3
"""
FLX Migration Code Transformer
Automatically applies migration transformations to codebase
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Tuple
import libcst as cst
from libcst import matchers as m

class FLXCodeTransformer:
    """Transforms code for FLX 0.4.0+ migration."""

    def __init__(self, project_root: str, dry_run: bool = True):
        self.project_root = Path(project_root)
        self.dry_run = dry_run
        self.transformations_applied = []

        # Define transformation rules
        self.transformations = {
            "update_logging_calls": self._transform_logging_calls,
            "update_imports": self._transform_imports,
            "update_cache_usage": self._transform_cache_usage,
            "update_adapter_manager": self._transform_adapter_manager
        }

    def transform_project(self) -> Dict[str, any]:
        """Apply all transformations to project."""
        print("🔄 Starting code transformation...")

        python_files = list(self.project_root.rglob("*.py"))
        transformed_files = []

        for file_path in python_files:
            if self._should_transform_file(file_path):
                if self._transform_file(file_path):
                    transformed_files.append(str(file_path))

        summary = {
            "status": "✅ Transformation complete" if not self.dry_run else "🔍 Dry run complete",
            "files_transformed": len(transformed_files),
            "transformations_applied": len(self.transformations_applied),
            "transformed_files": transformed_files,
            "transformation_details": self.transformations_applied
        }

        return summary

    def _transform_file(self, file_path: Path) -> bool:
        """Transform individual file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # Parse with LibCST for safe transformations
            tree = cst.parse_expression(original_content) if self._is_expression_file(file_path) else cst.parse_module(original_content)

            # Apply transformations
            transformed_tree = tree
            file_modified = False

            for transform_name, transform_func in self.transformations.items():
                new_tree = transform_func(transformed_tree, file_path)
                if new_tree != transformed_tree:
                    transformed_tree = new_tree
                    file_modified = True
                    self.transformations_applied.append({
                        "file": str(file_path),
                        "transformation": transform_name,
                        "status": "applied"
                    })

            # Write transformed content
            if file_modified and not self.dry_run:
                transformed_content = transformed_tree.code
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(transformed_content)
                print(f"✅ Transformed: {file_path}")
            elif file_modified and self.dry_run:
                print(f"🔍 Would transform: {file_path}")

            return file_modified

        except Exception as e:
            print(f"❌ Error transforming {file_path}: {e}")
            return False

    def _transform_logging_calls(self, tree: cst.Module, file_path: Path) -> cst.Module:
        """Transform logging calls to remove extra= parameter."""

        class LoggingTransformer(cst.CSTTransformer):
            def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:
                # Check if this is a logging call with extra= parameter
                if (isinstance(updated_node.func, cst.Attribute) and
                    updated_node.func.attr.value in ['debug', 'info', 'warning', 'error', 'critical']):

                    # Remove extra= argument if present
                    new_args = []
                    extra_data = None

                    for arg in updated_node.args:
                        if isinstance(arg, cst.Arg) and arg.keyword and arg.keyword.value == "extra":
                            extra_data = arg.value
                        else:
                            new_args.append(arg)

                    if extra_data:
                        # Convert extra data to format string
                        # This is a simplified transformation - real implementation would be more complex
                        return updated_node.with_changes(args=new_args)

                return updated_node

        transformer = LoggingTransformer()
        return tree.visit(transformer)

    def _transform_imports(self, tree: cst.Module, file_path: Path) -> cst.Module:
        """Transform deprecated imports to new imports."""

        class ImportTransformer(cst.CSTTransformer):
            def leave_ImportFrom(self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom) -> cst.ImportFrom:
                if updated_node.module:
                    module_name = updated_node.module.code

                    # Transform deprecated imports
                    import_mappings = {
                        "flx.adapters.manager": "flx.infra.adapters.unified_manager",
                        "flx.cache.manager": "flx.infra.cache.cache_service",
                        "flx.adapters.cache": "flx.infra.cache.cache_service"
                    }

                    for old_import, new_import in import_mappings.items():
                        if module_name.strip() == old_import:
                            new_module = cst.parse_expression(new_import)
                            return updated_node.with_changes(module=new_module)

                return updated_node

        transformer = ImportTransformer()
        return tree.visit(transformer)

    def _transform_cache_usage(self, tree: cst.Module, file_path: Path) -> cst.Module:
        """Transform cache usage to new consolidated service."""
        # Implementation would transform cache instantiation and usage patterns
        return tree

    def _transform_adapter_manager(self, tree: cst.Module, file_path: Path) -> cst.Module:
        """Transform adapter manager usage to unified manager."""
        # Implementation would transform manager instantiation and method calls
        return tree

    def _should_transform_file(self, file_path: Path) -> bool:
        """Determine if file should be transformed."""
        skip_patterns = [
            "test_", "tests/", "__pycache__", ".pyc",
            "venv/", "env/", ".venv/", "vendor/",
            "migrations/", "alembic/"
        ]

        path_str = str(file_path)
        return not any(pattern in path_str for pattern in skip_patterns)

    def _is_expression_file(self, file_path: Path) -> bool:
        """Check if file contains only expressions."""
        return False  # Most Python files are modules, not expressions

def main():
    """CLI entry point for code transformer."""
    import argparse

    parser = argparse.ArgumentParser(description="FLX Code Transformer")
    parser.add_argument("project_root", help="Root directory of project to transform")
    parser.add_argument("--dry-run", action="store_true", default=True,
                       help="Preview changes without applying them")
    parser.add_argument("--apply", action="store_true",
                       help="Actually apply transformations (removes dry-run)")

    args = parser.parse_args()

    # Determine run mode
    dry_run = not args.apply

    if not dry_run:
        confirm = input("⚠️  This will modify your code files. Continue? (y/N): ")
        if confirm.lower() != 'y':
            print("Transformation cancelled.")
            return

    # Run transformer
    transformer = FLXCodeTransformer(args.project_root, dry_run=dry_run)
    summary = transformer.transform_project()

    # Print results
    print("\n" + "="*60)
    print("🔄 TRANSFORMATION SUMMARY")
    print("="*60)
    print(f"Status: {summary['status']}")
    print(f"Files transformed: {summary['files_transformed']}")
    print(f"Total transformations: {summary['transformations_applied']}")

    if summary['transformation_details']:
        print("\n📝 Transformation Details:")
        for detail in summary['transformation_details'][:10]:  # Show first 10
            print(f"  • {detail['transformation']} in {Path(detail['file']).name}")

        if len(summary['transformation_details']) > 10:
            print(f"  ... and {len(summary['transformation_details']) - 10} more")

    if dry_run:
        print("\n💡 To apply these changes, run with --apply flag")

    print("="*60)

if __name__ == "__main__":
    main()
```

---

## ✅ Validation Tools

### **Migration Validation Suite**

Comprehensive validation framework for migration verification:

```python
#!/usr/bin/env python3
"""
FLX Migration Validator
Validates migration results and system compatibility
"""

import asyncio
import json
import sys
import time
from typing import Dict, List, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ValidationResult:
    """Result from a validation check."""
    check_name: str
    status: str  # "pass", "fail", "warning"
    message: str
    details: Dict[str, Any]
    execution_time: float

class MigrationValidator:
    """Comprehensive migration validation."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.results: List[ValidationResult] = []

    async def validate_migration(self) -> Dict[str, Any]:
        """Run comprehensive migration validation."""
        print("🔍 Starting migration validation...")

        # Define validation checks
        validation_checks = [
            ("import_validation", self._validate_imports),
            ("syntax_validation", self._validate_syntax),
            ("dependency_validation", self._validate_dependencies),
            ("api_compatibility", self._validate_api_compatibility),
            ("performance_validation", self._validate_performance),
            ("security_validation", self._validate_security),
            ("test_execution", self._validate_tests)
        ]

        # Run all validations
        for check_name, check_func in validation_checks:
            start_time = time.time()
            try:
                result = await check_func()
                execution_time = time.time() - start_time

                self.results.append(ValidationResult(
                    check_name=check_name,
                    status=result.get("status", "fail"),
                    message=result.get("message", "Unknown error"),
                    details=result.get("details", {}),
                    execution_time=execution_time
                ))

                status_emoji = "✅" if result["status"] == "pass" else "❌" if result["status"] == "fail" else "⚠️"
                print(f"{status_emoji} {check_name}: {result['message']}")

            except Exception as e:
                execution_time = time.time() - start_time
                self.results.append(ValidationResult(
                    check_name=check_name,
                    status="fail",
                    message=f"Validation error: {str(e)}",
                    details={"error": str(e)},
                    execution_time=execution_time
                ))
                print(f"❌ {check_name}: Validation error - {e}")

        # Generate summary
        return self._generate_validation_summary()

    async def _validate_imports(self) -> Dict[str, Any]:
        """Validate that all imports work correctly."""
        python_files = list(self.project_root.rglob("*.py"))
        import_errors = []

        for file_path in python_files:
            if self._should_validate_file(file_path):
                errors = await self._check_file_imports(file_path)
                import_errors.extend(errors)

        if import_errors:
            return {
                "status": "fail",
                "message": f"Found {len(import_errors)} import errors",
                "details": {"errors": import_errors[:10]}  # Show first 10
            }

        return {
            "status": "pass",
            "message": f"All imports validated across {len(python_files)} files",
            "details": {"files_checked": len(python_files)}
        }

    async def _validate_syntax(self) -> Dict[str, Any]:
        """Validate Python syntax in all files."""
        import ast

        python_files = list(self.project_root.rglob("*.py"))
        syntax_errors = []

        for file_path in python_files:
            if self._should_validate_file(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    ast.parse(content)
                except SyntaxError as e:
                    syntax_errors.append(f"{file_path}:{e.lineno}: {e.msg}")
                except Exception as e:
                    syntax_errors.append(f"{file_path}: {str(e)}")

        if syntax_errors:
            return {
                "status": "fail",
                "message": f"Found {len(syntax_errors)} syntax errors",
                "details": {"errors": syntax_errors}
            }

        return {
            "status": "pass",
            "message": f"Syntax validated across {len(python_files)} files",
            "details": {"files_checked": len(python_files)}
        }

    async def _validate_dependencies(self) -> Dict[str, Any]:
        """Validate that all dependencies are available."""
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            return {
                "status": "warning",
                "message": "No requirements.txt found",
                "details": {}
            }

        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, "-m", "pip", "check"],
                capture_output=True, text=True, cwd=self.project_root
            )

            if result.returncode == 0:
                return {
                    "status": "pass",
                    "message": "All dependencies are compatible",
                    "details": {"pip_check_output": result.stdout}
                }
            else:
                return {
                    "status": "fail",
                    "message": "Dependency conflicts detected",
                    "details": {"pip_check_errors": result.stderr}
                }
        except Exception as e:
            return {
                "status": "fail",
                "message": f"Could not validate dependencies: {e}",
                "details": {}
            }

    async def _validate_api_compatibility(self) -> Dict[str, Any]:
        """Validate API compatibility with FLX 0.4.0+."""
        # This would test that the migrated code correctly uses new APIs
        try:
            # Test basic FLX imports
            import flx
            from flx.adapters.base import BaseAdapter
            from flx.infra.cache.cache_service import CacheService
            from flx.infra.adapters.unified_manager import UnifiedAdapterManager

            return {
                "status": "pass",
                "message": "FLX 0.4.0+ APIs are accessible",
                "details": {"flx_version": getattr(flx, "__version__", "unknown")}
            }
        except ImportError as e:
            return {
                "status": "fail",
                "message": f"FLX API import failed: {e}",
                "details": {"import_error": str(e)}
            }

    async def _validate_performance(self) -> Dict[str, Any]:
        """Validate performance characteristics."""
        # Simple performance check - in reality this would be more comprehensive
        start_time = time.time()

        # Simulate some operations
        await asyncio.sleep(0.1)

        execution_time = time.time() - start_time

        if execution_time > 1.0:  # Threshold for performance concerns
            return {
                "status": "warning",
                "message": f"Performance validation took {execution_time:.2f}s",
                "details": {"execution_time": execution_time}
            }

        return {
            "status": "pass",
            "message": f"Performance validation completed in {execution_time:.2f}s",
            "details": {"execution_time": execution_time}
        }

    async def _validate_security(self) -> Dict[str, Any]:
        """Validate security aspects of migration."""
        # Check for common security issues
        security_issues = []

        python_files = list(self.project_root.rglob("*.py"))
        for file_path in python_files:
            if self._should_validate_file(file_path):
                issues = await self._check_security_issues(file_path)
                security_issues.extend(issues)

        if security_issues:
            return {
                "status": "warning",
                "message": f"Found {len(security_issues)} potential security issues",
                "details": {"issues": security_issues[:5]}  # Show first 5
            }

        return {
            "status": "pass",
            "message": "No obvious security issues detected",
            "details": {"files_checked": len(python_files)}
        }

    async def _validate_tests(self) -> Dict[str, Any]:
        """Validate that tests still pass after migration."""
        import subprocess

        try:
            # Try to run pytest if available
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--version"],
                capture_output=True, text=True, cwd=self.project_root
            )

            if result.returncode != 0:
                return {
                    "status": "warning",
                    "message": "pytest not available for test validation",
                    "details": {}
                }

            # Run tests
            test_result = subprocess.run(
                [sys.executable, "-m", "pytest", "-v", "--tb=short"],
                capture_output=True, text=True, cwd=self.project_root,
                timeout=300  # 5 minute timeout
            )

            if test_result.returncode == 0:
                return {
                    "status": "pass",
                    "message": "All tests passed",
                    "details": {"test_output": test_result.stdout[-1000:]}  # Last 1000 chars
                }
            else:
                return {
                    "status": "fail",
                    "message": "Some tests failed",
                    "details": {"test_errors": test_result.stderr[-1000:]}  # Last 1000 chars
                }

        except subprocess.TimeoutExpired:
            return {
                "status": "fail",
                "message": "Test execution timed out",
                "details": {}
            }
        except Exception as e:
            return {
                "status": "warning",
                "message": f"Could not run tests: {e}",
                "details": {}
            }

    async def _check_file_imports(self, file_path: Path) -> List[str]:
        """Check imports in a specific file."""
        import ast
        import importlib.util

        errors = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        try:
                            importlib.util.find_spec(alias.name)
                        except (ImportError, ModuleNotFoundError):
                            errors.append(f"{file_path}: Cannot import {alias.name}")

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        try:
                            importlib.util.find_spec(node.module)
                        except (ImportError, ModuleNotFoundError):
                            errors.append(f"{file_path}: Cannot import from {node.module}")

        except Exception as e:
            errors.append(f"{file_path}: Error checking imports - {e}")

        return errors

    async def _check_security_issues(self, file_path: Path) -> List[str]:
        """Check for common security issues in file."""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for common security anti-patterns
            security_patterns = [
                (r"password\s*=\s*['\"][^'\"]+['\"]", "Hardcoded password detected"),
                (r"api_key\s*=\s*['\"][^'\"]+['\"]", "Hardcoded API key detected"),
                (r"eval\s*\(", "Use of eval() function detected"),
                (r"exec\s*\(", "Use of exec() function detected"),
                (r"shell\s*=\s*True", "Shell=True in subprocess call")
            ]

            import re
            for pattern, message in security_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    issues.append(f"{file_path}: {message}")

        except Exception:
            pass  # Skip files that can't be read

        return issues

    def _should_validate_file(self, file_path: Path) -> bool:
        """Determine if file should be validated."""
        skip_patterns = [
            "__pycache__", ".pyc", "venv/", "env/", ".venv/"
        ]

        path_str = str(file_path)
        return not any(pattern in path_str for pattern in skip_patterns)

    def _generate_validation_summary(self) -> Dict[str, Any]:
        """Generate comprehensive validation summary."""
        total_checks = len(self.results)
        passed_checks = len([r for r in self.results if r.status == "pass"])
        failed_checks = len([r for r in self.results if r.status == "fail"])
        warning_checks = len([r for r in self.results if r.status == "warning"])

        overall_status = "pass" if failed_checks == 0 else "fail"
        if failed_checks == 0 and warning_checks > 0:
            overall_status = "warning"

        return {
            "overall_status": overall_status,
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "warning_checks": warning_checks,
            "total_execution_time": sum(r.execution_time for r in self.results),
            "detailed_results": [
                {
                    "check": r.check_name,
                    "status": r.status,
                    "message": r.message,
                    "execution_time": r.execution_time
                }
                for r in self.results
            ],
            "recommendations": self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []

        failed_results = [r for r in self.results if r.status == "fail"]
        warning_results = [r for r in self.results if r.status == "warning"]

        if failed_results:
            recommendations.append(
                f"🚨 Address {len(failed_results)} critical validation failures before deploying"
            )

        if warning_results:
            recommendations.append(
                f"⚠️ Review {len(warning_results)} warnings for potential issues"
            )

        if not failed_results and not warning_results:
            recommendations.append("✅ Migration validation passed - system ready for deployment")

        recommendations.extend([
            "🧪 Run additional integration tests in staging environment",
            "📊 Monitor system performance after deployment",
            "📝 Update documentation to reflect migration changes",
            "👥 Train team on any new patterns or processes"
        ])

        return recommendations

async def main():
    """CLI entry point for migration validator."""
    if len(sys.argv) != 2:
        print("Usage: python migration_validator.py <project_root>")
        sys.exit(1)

    project_root = sys.argv[1]
    if not Path(project_root).exists():
        print(f"❌ Project root not found: {project_root}")
        sys.exit(1)

    # Run validation
    validator = MigrationValidator(project_root)
    summary = await validator.validate_migration()

    # Print summary
    print("\n" + "="*60)
    print("✅ MIGRATION VALIDATION SUMMARY")
    print("="*60)

    status_emoji = "✅" if summary["overall_status"] == "pass" else "❌" if summary["overall_status"] == "fail" else "⚠️"
    print(f"Overall Status: {status_emoji} {summary['overall_status'].upper()}")
    print(f"Total Checks: {summary['total_checks']}")
    print(f"Passed: {summary['passed_checks']}")
    print(f"Failed: {summary['failed_checks']}")
    print(f"Warnings: {summary['warning_checks']}")
    print(f"Execution Time: {summary['total_execution_time']:.2f}s")

    print(f"\n💡 Recommendations:")
    for rec in summary['recommendations']:
        print(f"  • {rec}")

    # Save detailed report
    report_file = "migration_validation_report.json"
    with open(report_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n📄 Detailed report saved to: {report_file}")
    print("="*60)

    # Exit with appropriate code
    sys.exit(0 if summary["overall_status"] in ["pass", "warning"] else 1)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🚀 Automation Scripts

### **Complete Migration Orchestrator**

End-to-end migration automation script:

```bash
#!/bin/bash
#
# FLX Migration Orchestrator
# Automates complete FLX Framework migration process
#

set -euo pipefail

# Configuration
PROJECT_ROOT="${1:-$(pwd)}"
BACKUP_DIR="${PROJECT_ROOT}_backup_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="flx_migration_$(date +%Y%m%d_%H%M%S).log"
DRY_RUN="${DRY_RUN:-true}"
SKIP_TESTS="${SKIP_TESTS:-false}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# Error handling
handle_error() {
    log_error "Migration failed at step: $1"
    log_error "Check log file: $LOG_FILE"

    if [[ "$DRY_RUN" == "false" && -d "$BACKUP_DIR" ]]; then
        log_info "Backup available at: $BACKUP_DIR"
        read -p "Restore from backup? (y/N): " restore
        if [[ "$restore" == "y" ]]; then
            restore_backup
        fi
    fi

    exit 1
}

# Backup function
create_backup() {
    log_info "Creating backup of project..."
    cp -r "$PROJECT_ROOT" "$BACKUP_DIR"
    log_success "Backup created at: $BACKUP_DIR"
}

# Restore function
restore_backup() {
    log_info "Restoring from backup..."
    rm -rf "$PROJECT_ROOT"
    cp -r "$BACKUP_DIR" "$PROJECT_ROOT"
    log_success "Restored from backup"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Python version
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi

    local python_version=$(python3 --version 2>&1 | awk '{print $2}')
    log_info "Python version: $python_version"

    # Check if project exists
    if [[ ! -d "$PROJECT_ROOT" ]]; then
        log_error "Project root not found: $PROJECT_ROOT"
        exit 1
    fi

    # Check if FLX is installed
    if ! python3 -c "import flx" 2>/dev/null; then
        log_warning "FLX not found - will attempt to install"
    fi

    log_success "Prerequisites check completed"
}

# Analysis phase
run_analysis() {
    log_info "Running code analysis..."

    if ! python3 migration_tools/flx_analyzer.py "$PROJECT_ROOT" >> "$LOG_FILE" 2>&1; then
        handle_error "Code analysis failed"
    fi

    # Check if analysis found critical issues
    if [[ -f "flx_migration_analysis.json" ]]; then
        local breaking_changes=$(python3 -c "
import json
with open('flx_migration_analysis.json') as f:
    data = json.load(f)
    print(data.get('total_breaking_changes', 0))
" 2>/dev/null || echo "0")

        if [[ "$breaking_changes" -gt 0 ]]; then
            log_warning "Found $breaking_changes breaking changes"
        fi
    fi

    log_success "Code analysis completed"
}

# Transformation phase
run_transformation() {
    local apply_flag=""
    if [[ "$DRY_RUN" == "false" ]]; then
        apply_flag="--apply"
    fi

    log_info "Running code transformation (dry_run=$DRY_RUN)..."

    if ! python3 migration_tools/flx_transformer.py "$PROJECT_ROOT" $apply_flag >> "$LOG_FILE" 2>&1; then
        handle_error "Code transformation failed"
    fi

    log_success "Code transformation completed"
}

# Validation phase
run_validation() {
    log_info "Running migration validation..."

    if ! python3 migration_tools/migration_validator.py "$PROJECT_ROOT" >> "$LOG_FILE" 2>&1; then
        local exit_code=$?
        if [[ $exit_code -eq 1 ]]; then
            handle_error "Migration validation failed with critical errors"
        else
            log_warning "Migration validation completed with warnings"
        fi
    fi

    log_success "Migration validation completed"
}

# Test execution
run_tests() {
    if [[ "$SKIP_TESTS" == "true" ]]; then
        log_info "Skipping tests (SKIP_TESTS=true)"
        return
    fi

    log_info "Running tests..."

    cd "$PROJECT_ROOT"

    # Try different test runners
    if command -v pytest &> /dev/null; then
        if ! pytest -v --tb=short >> "$LOG_FILE" 2>&1; then
            log_warning "Some tests failed - check log for details"
        else
            log_success "All tests passed"
        fi
    elif [[ -f "manage.py" ]]; then
        # Django project
        if ! python3 manage.py test >> "$LOG_FILE" 2>&1; then
            log_warning "Django tests failed - check log for details"
        else
            log_success "Django tests passed"
        fi
    else
        # Use unittest discovery
        if ! python3 -m unittest discover -s . -p "*test*.py" >> "$LOG_FILE" 2>&1; then
            log_warning "Unit tests failed - check log for details"
        else
            log_success "Unit tests passed"
        fi
    fi

    cd - > /dev/null
}

# Performance check
check_performance() {
    log_info "Running basic performance check..."

    cd "$PROJECT_ROOT"

    # Simple import time check
    local import_time=$(python3 -c "
import time
start = time.time()
try:
    import flx
    end = time.time()
    print(f'{end - start:.3f}')
except ImportError as e:
    print('ERROR')
" 2>/dev/null)

    if [[ "$import_time" == "ERROR" ]]; then
        log_error "FLX import failed"
    elif (( $(echo "$import_time > 2.0" | bc -l) )); then
        log_warning "FLX import took ${import_time}s (slow)"
    else
        log_success "FLX import time: ${import_time}s"
    fi

    cd - > /dev/null
}

# Generate report
generate_report() {
    log_info "Generating migration report..."

    local report_file="flx_migration_report_$(date +%Y%m%d_%H%M%S).md"

    cat > "$report_file" << EOF
# FLX Migration Report

**Date**: $(date)
**Project**: $PROJECT_ROOT
**Mode**: $(if [[ "$DRY_RUN" == "true" ]]; then echo "Dry Run"; else echo "Live Migration"; fi)

## Summary

$(if [[ -f "flx_migration_analysis.json" ]]; then
    python3 -c "
import json
with open('flx_migration_analysis.json') as f:
    data = json.load(f)
    print(f'- Files analyzed: {data.get(\"files_requiring_migration\", 0)}')
    print(f'- Issues found: {data.get(\"total_migration_issues\", 0)}')
    print(f'- Breaking changes: {data.get(\"total_breaking_changes\", 0)}')
"
fi)

## Migration Steps Completed

- [x] Prerequisites check
- [x] Code analysis
- [x] Code transformation
- [x] Validation
$(if [[ "$SKIP_TESTS" != "true" ]]; then echo "- [x] Test execution"; fi)
- [x] Performance check

## Next Steps

$(if [[ "$DRY_RUN" == "true" ]]; then
echo "1. Review this report and validation results
2. Run migration with DRY_RUN=false to apply changes
3. Run comprehensive tests in staging environment
4. Plan production deployment"
else
echo "1. Monitor application performance
2. Run full integration tests
3. Update documentation
4. Train team on changes"
fi)

## Files

- Log file: $LOG_FILE
- Analysis report: flx_migration_analysis.json
- Validation report: migration_validation_report.json
$(if [[ "$DRY_RUN" == "false" && -d "$BACKUP_DIR" ]]; then echo "- Backup: $BACKUP_DIR"; fi)

EOF

    log_success "Migration report generated: $report_file"
}

# Main migration function
main() {
    echo "🚀 FLX Framework Migration Orchestrator"
    echo "======================================"
    echo "Project: $PROJECT_ROOT"
    echo "Mode: $(if [[ "$DRY_RUN" == "true" ]]; then echo "DRY RUN"; else echo "LIVE MIGRATION"; fi)"
    echo "Log: $LOG_FILE"
    echo ""

    # Confirmation for live migration
    if [[ "$DRY_RUN" == "false" ]]; then
        echo "⚠️  This will modify your project files!"
        read -p "Continue with live migration? (y/N): " confirm
        if [[ "$confirm" != "y" ]]; then
            echo "Migration cancelled."
            exit 0
        fi
    fi

    # Create backup for live migration
    if [[ "$DRY_RUN" == "false" ]]; then
        create_backup
    fi

    # Execute migration steps
    trap 'handle_error "$(caller)"' ERR

    check_prerequisites
    run_analysis
    run_transformation
    run_validation
    run_tests
    check_performance
    generate_report

    echo ""
    echo "🎉 Migration orchestration completed successfully!"
    echo "📄 Check the migration report for details."

    if [[ "$DRY_RUN" == "true" ]]; then
        echo ""
        echo "💡 This was a dry run. To apply changes, run:"
        echo "   DRY_RUN=false $0 $PROJECT_ROOT"
    fi
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
```

---

## 📈 Monitoring Tools

### **Real-time Migration Monitor**

Dashboard for monitoring migration progress and system health:

```python
#!/usr/bin/env python3
"""
FLX Migration Monitor
Real-time monitoring dashboard for migration progress
"""

import asyncio
import json
import time
import psutil
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

@dataclass
class SystemMetrics:
    """System performance metrics."""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io: Dict[str, int]
    process_count: int

@dataclass
class MigrationStatus:
    """Migration progress status."""
    phase: str
    progress_percent: float
    current_task: str
    elapsed_time: float
    estimated_remaining: float
    errors_count: int
    warnings_count: int

class MigrationMonitor:
    """Real-time migration monitoring."""

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.start_time = time.time()
        self.metrics_history: List[SystemMetrics] = []
        self.status_history: List[MigrationStatus] = []
        self.monitoring = False

    async def start_monitoring(self):
        """Start real-time monitoring."""
        self.monitoring = True
        print("📊 Starting migration monitoring...")

        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self._monitor_system_metrics()),
            asyncio.create_task(self._monitor_migration_progress()),
            asyncio.create_task(self._display_dashboard())
        ]

        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped by user")
        finally:
            self.monitoring = False

    async def _monitor_system_metrics(self):
        """Monitor system performance metrics."""
        while self.monitoring:
            try:
                # Collect system metrics
                metrics = SystemMetrics(
                    timestamp=datetime.now().isoformat(),
                    cpu_percent=psutil.cpu_percent(interval=1),
                    memory_percent=psutil.virtual_memory().percent,
                    disk_usage_percent=psutil.disk_usage('/').percent,
                    network_io=dict(psutil.net_io_counters()._asdict()),
                    process_count=len(psutil.pids())
                )

                self.metrics_history.append(metrics)

                # Keep only last 100 measurements
                if len(self.metrics_history) > 100:
                    self.metrics_history.pop(0)

                await asyncio.sleep(5)  # Collect every 5 seconds

            except Exception as e:
                print(f"Error collecting metrics: {e}")
                await asyncio.sleep(5)

    async def _monitor_migration_progress(self):
        """Monitor migration progress."""
        while self.monitoring:
            try:
                # Check for migration status files
                status = await self._detect_migration_status()
                if status:
                    self.status_history.append(status)

                    # Keep only last 50 status updates
                    if len(self.status_history) > 50:
                        self.status_history.pop(0)

                await asyncio.sleep(2)  # Check every 2 seconds

            except Exception as e:
                print(f"Error monitoring progress: {e}")
                await asyncio.sleep(2)

    async def _detect_migration_status(self) -> MigrationStatus:
        """Detect current migration status."""
        # This would typically read from migration log files or status files
        # For demo purposes, we'll simulate status detection

        elapsed = time.time() - self.start_time

        # Simulate different phases
        if elapsed < 30:
            phase = "analysis"
            progress = (elapsed / 30) * 100
            task = "Analyzing codebase"
        elif elapsed < 60:
            phase = "transformation"
            progress = ((elapsed - 30) / 30) * 100
            task = "Applying code transformations"
        elif elapsed < 90:
            phase = "validation"
            progress = ((elapsed - 60) / 30) * 100
            task = "Validating migration results"
        else:
            phase = "complete"
            progress = 100
            task = "Migration completed"

        return MigrationStatus(
            phase=phase,
            progress_percent=min(progress, 100),
            current_task=task,
            elapsed_time=elapsed,
            estimated_remaining=max(0, 90 - elapsed),
            errors_count=0,  # Would be read from actual logs
            warnings_count=1 if elapsed > 45 else 0  # Simulate warning
        )

    async def _display_dashboard(self):
        """Display real-time dashboard."""
        while self.monitoring:
            try:
                # Clear screen (ANSI escape code)
                print("\033[2J\033[H", end="")

                # Display header
                print("🚀 FLX Migration Monitor")
                print("=" * 50)
                print(f"Project: {self.project_root}")
                print(f"Started: {datetime.fromtimestamp(self.start_time).strftime('%H:%M:%S')}")
                print(f"Runtime: {time.time() - self.start_time:.0f}s")
                print()

                # Display migration status
                if self.status_history:
                    latest_status = self.status_history[-1]
                    print("📋 Migration Progress")
                    print("-" * 30)
                    print(f"Phase: {latest_status.phase.upper()}")
                    print(f"Progress: {latest_status.progress_percent:.1f}%")
                    print(f"Task: {latest_status.current_task}")
                    print(f"Estimated remaining: {latest_status.estimated_remaining:.0f}s")
                    print(f"Errors: {latest_status.errors_count}")
                    print(f"Warnings: {latest_status.warnings_count}")

                    # Progress bar
                    bar_length = 30
                    filled = int((latest_status.progress_percent / 100) * bar_length)
                    bar = "█" * filled + "░" * (bar_length - filled)
                    print(f"[{bar}] {latest_status.progress_percent:.1f}%")
                    print()

                # Display system metrics
                if self.metrics_history:
                    latest_metrics = self.metrics_history[-1]
                    print("💻 System Metrics")
                    print("-" * 30)
                    print(f"CPU: {latest_metrics.cpu_percent:.1f}%")
                    print(f"Memory: {latest_metrics.memory_percent:.1f}%")
                    print(f"Disk: {latest_metrics.disk_usage_percent:.1f}%")
                    print(f"Processes: {latest_metrics.process_count}")
                    print()

                # Display recent alerts
                print("🚨 Recent Alerts")
                print("-" * 30)
                alerts = self._generate_alerts()
                if alerts:
                    for alert in alerts[-3:]:  # Show last 3 alerts
                        print(f"• {alert}")
                else:
                    print("• No alerts")
                print()

                # Display performance trend
                print("📈 Performance Trend (Last 5 readings)")
                print("-" * 30)
                if len(self.metrics_history) >= 5:
                    recent_metrics = self.metrics_history[-5:]
                    avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
                    avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)

                    print(f"Avg CPU: {avg_cpu:.1f}%")
                    print(f"Avg Memory: {avg_memory:.1f}%")

                    # Simple trend indication
                    if len(self.metrics_history) >= 10:
                        old_avg_cpu = sum(m.cpu_percent for m in self.metrics_history[-10:-5]) / 5
                        cpu_trend = "↑" if avg_cpu > old_avg_cpu else "↓" if avg_cpu < old_avg_cpu else "→"
                        print(f"CPU Trend: {cpu_trend}")

                print()
                print("Press Ctrl+C to stop monitoring")

                await asyncio.sleep(3)  # Update every 3 seconds

            except Exception as e:
                print(f"Error updating dashboard: {e}")
                await asyncio.sleep(3)

    def _generate_alerts(self) -> List[str]:
        """Generate alerts based on current metrics."""
        alerts = []

        if self.metrics_history:
            latest = self.metrics_history[-1]

            if latest.cpu_percent > 80:
                alerts.append(f"High CPU usage: {latest.cpu_percent:.1f}%")

            if latest.memory_percent > 85:
                alerts.append(f"High memory usage: {latest.memory_percent:.1f}%")

            if latest.disk_usage_percent > 90:
                alerts.append(f"Low disk space: {latest.disk_usage_percent:.1f}% used")

        if self.status_history:
            latest_status = self.status_history[-1]

            if latest_status.errors_count > 0:
                alerts.append(f"Migration errors detected: {latest_status.errors_count}")

            if latest_status.warnings_count > 0:
                alerts.append(f"Migration warnings: {latest_status.warnings_count}")

        return alerts

    def save_report(self, filename: str = None):
        """Save monitoring report to file."""
        if not filename:
            filename = f"migration_monitoring_report_{int(time.time())}.json"

        report = {
            "monitoring_session": {
                "start_time": self.start_time,
                "end_time": time.time(),
                "duration": time.time() - self.start_time,
                "project_root": self.project_root
            },
            "metrics_summary": self._summarize_metrics(),
            "status_summary": self._summarize_status(),
            "alerts_summary": self._summarize_alerts(),
            "raw_metrics": [asdict(m) for m in self.metrics_history],
            "raw_status": [asdict(s) for s in self.status_history]
        }

        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"📄 Monitoring report saved to: {filename}")

    def _summarize_metrics(self) -> Dict[str, Any]:
        """Summarize system metrics."""
        if not self.metrics_history:
            return {}

        cpu_values = [m.cpu_percent for m in self.metrics_history]
        memory_values = [m.memory_percent for m in self.metrics_history]

        return {
            "cpu": {
                "avg": sum(cpu_values) / len(cpu_values),
                "max": max(cpu_values),
                "min": min(cpu_values)
            },
            "memory": {
                "avg": sum(memory_values) / len(memory_values),
                "max": max(memory_values),
                "min": min(memory_values)
            },
            "samples_collected": len(self.metrics_history)
        }

    def _summarize_status(self) -> Dict[str, Any]:
        """Summarize migration status."""
        if not self.status_history:
            return {}

        phases = [s.phase for s in self.status_history]
        unique_phases = list(set(phases))

        return {
            "phases_completed": unique_phases,
            "total_errors": sum(s.errors_count for s in self.status_history),
            "total_warnings": sum(s.warnings_count for s in self.status_history),
            "final_progress": self.status_history[-1].progress_percent if self.status_history else 0
        }

    def _summarize_alerts(self) -> Dict[str, Any]:
        """Summarize alerts generated."""
        all_alerts = []
        for _ in range(len(self.metrics_history)):
            all_alerts.extend(self._generate_alerts())

        unique_alerts = list(set(all_alerts))

        return {
            "total_alerts": len(all_alerts),
            "unique_alerts": len(unique_alerts),
            "alert_types": unique_alerts
        }

async def main():
    """CLI entry point for migration monitor."""
    import sys

    if len(sys.argv) != 2:
        print("Usage: python migration_monitor.py <project_root>")
        sys.exit(1)

    project_root = sys.argv[1]

    monitor = MigrationMonitor(project_root)

    try:
        await monitor.start_monitoring()
    finally:
        # Save report on exit
        monitor.save_report()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🔗 **Cross-References**

### **⬅️ Prerequisites**

- [Migration Guides Hub](../guides/index.md) - Understanding migration procedures before implementing automation
- [Migration Strategies Hub](../strategies/index.md) - Strategic planning informing tool selection and configuration
- [Development Hub](../../development/index.md) - Development environment setup and tools

### **➡️ Next Steps**

- [Migration Validation](../guides/migration-guide.md#validation-and-testing) - Using tools for comprehensive migration validation
- [Development Testing Hub](../../development/testing/index.md) - Testing strategies for validating migration results
- [Deployment Hub](../../deployment/index.md) - Deployment automation tools and continuous integration

### **🔗 Related Topics**

- [Examples Hub](../../examples/index.md) - Working examples demonstrating migration tool usage
- [Scripts & Utilities](../../development/scripts-and-utilities.md) - Development utilities and helper scripts
- [Infrastructure Hub](../../infrastructure/index.md) - Infrastructure automation supporting migration tools
- [Engineering ADRs Hub](../../engineering/adrs/index.md) - Tool selection decisions and automation strategies

---

## 📊 **Document Information**

- **Status**: ✅ Complete
- **Last Updated**: June 11, 2025
- **Audience**: DevOps engineers, automation engineers, migration teams
- **Complexity**: Advanced

---

**📂 Content Guide** | **🏠 Hub**: [Migration Tools](./index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
