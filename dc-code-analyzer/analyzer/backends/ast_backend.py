"""AST-based analysis backend for detailed code structure analysis."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from .base import AnalysisBackend, AnalysisResult


class ASTVisitor(ast.NodeVisitor):
    """AST visitor to extract detailed code structure information."""

    def __init__(self, file_path: Path, package_name: str):
        self.file_path = file_path
        self.package_name = package_name
        self.current_class: dict[str, Any] | None = None
        self.current_function: dict[str, Any] | None = None
        self.scope_stack: list[str] = []

        # Results
        self.classes: list[dict[str, Any]] = []
        self.functions: list[dict[str, Any]] = []
        self.variables: list[dict[str, Any]] = []
        self.imports: list[dict[str, Any]] = []
        self.constants: list[dict[str, Any]] = []

        # Context tracking
        self.class_stack: list[dict[str, Any]] = []
        self.function_stack: list[dict[str, Any]] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        """Visit class definition."""
        # Extract class analysis into smaller helper methods
        full_name = self._calculate_class_full_name(node)
        base_classes = self._extract_base_classes(node)
        decorators, is_dataclass, is_abstract = self._analyze_class_decorators(node)
        method_counts = self._count_class_methods(node)

        class_info = {
            "name": node.name,
            "full_name": full_name,
            "line_start": node.lineno,
            "line_end": node.end_lineno or node.lineno,
            "base_classes": base_classes,
            "inheritance_depth": len(self.class_stack),
            "method_count": method_counts["method_count"],
            "property_count": method_counts["property_count"],
            "class_method_count": method_counts["classmethod_count"],
            "static_method_count": method_counts["staticmethod_count"],
            "has_docstring": ast.get_docstring(node) is not None,
            "docstring_length": len(ast.get_docstring(node) or ""),
            "is_abstract": is_abstract,
            "is_dataclass": is_dataclass,
            "decorators": decorators,
            "lines_of_code": (node.end_lineno or node.lineno) - node.lineno + 1,
        }

        self.classes.append(class_info)

        # Update context
        self.class_stack.append(class_info)
        self.current_class = class_info

        # Visit children
        self.generic_visit(node)

        # Restore context
        self.class_stack.pop()
        self.current_class = self.class_stack[-1] if self.class_stack else None

    def _calculate_class_full_name(self, node: ast.ClassDef) -> str:
        """Calculate the full qualified name for a class."""
        full_name_parts = [self.package_name] if self.package_name != "__main__" else []
        full_name_parts.extend([cls["name"] for cls in self.class_stack])
        full_name_parts.append(node.name)
        return ".".join(full_name_parts)

    def _extract_base_classes(self, node: ast.ClassDef) -> list[str]:
        """Extract base class names from a class definition."""
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(ast.unparse(base))
        return base_classes

    def _analyze_class_decorators(
        self, node: ast.ClassDef
    ) -> tuple[list[str], bool, bool]:
        """Analyze class decorators and special patterns."""
        decorators = [ast.unparse(d) for d in node.decorator_list]
        is_dataclass = any("dataclass" in d for d in decorators)
        is_abstract = any("ABC" in str(base) for base in node.bases)
        return decorators, is_dataclass, is_abstract

    def _count_class_methods(self, node: ast.ClassDef) -> dict[str, int]:
        """Count different types of methods in a class."""
        method_count = 0
        property_count = 0
        classmethod_count = 0
        staticmethod_count = 0

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_count += 1
                for decorator in item.decorator_list:
                    if isinstance(decorator, ast.Name):
                        if decorator.id == "property":
                            property_count += 1
                        elif decorator.id == "classmethod":
                            classmethod_count += 1
                        elif decorator.id == "staticmethod":
                            staticmethod_count += 1

        return {
            "method_count": method_count,
            "property_count": property_count,
            "classmethod_count": classmethod_count,
            "staticmethod_count": staticmethod_count,
        }

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        """Visit function definition."""
        self._visit_function_def(node, "function")

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802
        """Visit async function definition."""
        self._visit_function_def(node, "async_function")

    def _visit_function_def(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        func_type: str,
    ) -> None:
        """Handle both regular and async function definitions."""
        # Calculate full name
        full_name_parts = [self.package_name] if self.package_name != "__main__" else []
        full_name_parts.extend([cls["name"] for cls in self.class_stack])
        full_name_parts.extend([func["name"] for func in self.function_stack])
        full_name_parts.append(node.name)
        full_name = ".".join(full_name_parts)

        # Determine function type
        if self.current_class:
            func_type = (
                "async_method" if isinstance(node, ast.AsyncFunctionDef) else "method"
            )
        else:
            func_type = (
                "async_function"
                if isinstance(node, ast.AsyncFunctionDef)
                else "function"
            )

        # Check decorators
        decorators = [ast.unparse(d) for d in node.decorator_list]
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                if decorator.id == "property":
                    func_type = "property"
                elif decorator.id == "classmethod":
                    func_type = "classmethod"
                elif decorator.id == "staticmethod":
                    func_type = "staticmethod"

        # Analyze parameters
        args = node.args
        param_count = len(args.args)
        if args.vararg:
            param_count += 1
        if args.kwarg:
            param_count += 1
        param_count += len(args.kwonlyargs)

        # Get parameter information
        parameters = []
        for arg in args.args:
            param_info = {
                "name": arg.arg,
                "type_annotation": (
                    ast.unparse(arg.annotation) if arg.annotation else None
                ),
                "has_default": False,
            }
            parameters.append(param_info)

        # Count return statements
        return_count = sum(1 for node in ast.walk(node) if isinstance(node, ast.Return))

        # Calculate complexity (basic cyclomatic complexity)
        complexity = self._calculate_complexity(node)
        complexity_level = self._get_complexity_level(complexity)

        # Check for code quality issues
        has_too_many_params = param_count > 7
        is_too_long = (node.end_lineno or node.lineno) - node.lineno > 50

        # Get return type
        return_type = ast.unparse(node.returns) if node.returns else ""

        function_info = {
            "name": node.name,
            "full_name": full_name,
            "function_type": func_type,
            "line_start": node.lineno,
            "line_end": node.end_lineno or node.lineno,
            "lines_of_code": (node.end_lineno or node.lineno) - node.lineno + 1,
            "parameter_count": param_count,
            "return_statement_count": return_count,
            "cyclomatic_complexity": complexity,
            "complexity_level": complexity_level,
            "has_docstring": ast.get_docstring(node) is not None,
            "has_type_hints": node.returns is not None
            or any(arg.annotation for arg in args.args),
            "docstring_length": len(ast.get_docstring(node) or ""),
            "has_too_many_parameters": has_too_many_params,
            "is_too_long": is_too_long,
            "parameters": parameters,
            "return_type": return_type,
            "decorators": decorators,
            "class_name": self.current_class["name"] if self.current_class else None,
        }

        self.functions.append(function_info)

        # Update context
        self.function_stack.append(function_info)
        self.current_function = function_info

        # Visit children
        self.generic_visit(node)

        # Restore context
        self.function_stack.pop()
        self.current_function = self.function_stack[-1] if self.function_stack else None

    def visit_Import(self, node: ast.Import) -> None:  # noqa: N802
        """Visit import statement."""
        for alias in node.names:
            import_info = {
                "module_name": alias.name,
                "import_name": "",
                "alias": alias.asname or "",
                "line_number": getattr(node, "lineno", 0),
                "is_wildcard": False,
                "import_type": self._classify_import(alias.name),
            }
            self.imports.append(import_info)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:  # noqa: N802
        """Visit from...import statement."""
        module_name = node.module or ""
        for alias in node.names:
            import_info = {
                "module_name": module_name,
                "import_name": alias.name,
                "alias": alias.asname or "",
                "line_number": getattr(node, "lineno", 0),
                "is_wildcard": alias.name == "*",
                "import_type": self._classify_import(module_name),
            }
            self.imports.append(import_info)

    def visit_Assign(self, node: ast.Assign) -> None:  # noqa: N802
        """Visit assignment statement."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self._analyze_variable(target.id, node)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:  # noqa: N802
        """Visit annotated assignment."""
        if isinstance(node.target, ast.Name):
            self._analyze_variable(node.target.id, node, has_annotation=True)
        self.generic_visit(node)

    def _analyze_variable(
        self, name: str, node: ast.AST, has_annotation: bool = False
    ) -> None:
        """Analyze a variable assignment."""
        # Determine variable type and scope
        if self.current_function:
            scope_type = "function"
            var_type = "local_var"
        elif self.current_class:
            scope_type = "class"
            var_type = "instance_var" if name.startswith("_") else "class_var"
        else:
            scope_type = "module"
            var_type = "constant" if name.isupper() else "global_var"

        # Build full name
        full_name_parts = [self.package_name] if self.package_name != "__main__" else []
        if self.current_class:
            full_name_parts.append(self.current_class["name"])
        if self.current_function:
            full_name_parts.append(self.current_function["name"])
        full_name_parts.append(name)
        full_name = ".".join(full_name_parts)

        # Get initial value if possible
        initial_value = ""
        if hasattr(node, "value") and node.value:
            try:
                initial_value = ast.unparse(node.value)[:200]  # Limit length
            except Exception:
                initial_value = "<complex_expression>"

        # Check naming conventions
        follows_convention = self._check_naming_convention(name, var_type)

        variable_info = {
            "name": name,
            "full_name": full_name,
            "variable_type": var_type,
            "scope_type": scope_type,
            "line_number": getattr(node, "lineno", 0),
            "has_type_annotation": has_annotation,
            "type_annotation": (
                ast.unparse(node.annotation)
                if hasattr(node, "annotation") and node.annotation
                else ""
            ),
            "is_constant": var_type == "constant",
            "initial_value": initial_value,
            "follows_naming_convention": follows_convention,
            "class_name": self.current_class["name"] if self.current_class else None,
            "function_name": (
                self.current_function["name"] if self.current_function else None
            ),
        }

        self.variables.append(variable_info)

    def _calculate_complexity(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> int:
        """Calculate cyclomatic complexity for a function."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(
                child,
                ast.If
                | ast.While
                | ast.For
                | ast.AsyncFor
                | ast.ExceptHandler
                | ast.And
                | ast.Or
                | ast.comprehension,
            ):
                complexity += 1

        return complexity

    def _get_complexity_level(self, complexity: int) -> str:
        """Get complexity level based on complexity score."""
        if complexity <= 5:
            return "low"
        if complexity <= 10:
            return "medium"
        if complexity <= 20:
            return "high"
        return "very_high"

    def _classify_import(self, module_name: str) -> str:
        """Classify import type."""
        if not module_name:
            return "relative"

        # Standard library modules (simplified list)
        stdlib_modules = {
            "os",
            "sys",
            "json",
            "csv",
            "datetime",
            "collections",
            "itertools",
            "functools",
            "operator",
            "math",
            "random",
            "string",
            "re",
            "time",
            "pathlib",
            "typing",
            "abc",
            "dataclasses",
            "enum",
            "logging",
        }

        if module_name.split(".")[0] in stdlib_modules:
            return "standard"
        if module_name.startswith("."):
            return "relative"
        if any(
            part in module_name
            for part in ["django", "flask", "requests", "numpy", "pandas"]
        ):
            return "third_party"
        return "local"

    def _check_naming_convention(self, name: str, var_type: str) -> bool:
        """Check if variable follows Python naming conventions."""
        if var_type == "constant":
            return name.isupper() and "_" in name or len(name) <= 3
        if var_type in {"class_var", "instance_var"}:
            return name.islower() or name.startswith("_")
        return name.islower() or "_" in name


class ASTBackend(AnalysisBackend):
    """AST-based backend for detailed code structure analysis."""

    @property
    def name(self) -> str:
        return "ast"

    @property
    def description(self) -> str:
        return "AST-based analysis for detailed code structure (classes, functions, variables)"

    @property
    def capabilities(self) -> list[str]:
        return [
            "package_structure",
            "class_analysis",
            "function_analysis",
            "variable_analysis",
            "import_analysis",
            "complexity_analysis",
            "type_analysis",
        ]

    def analyze(self, python_files: list[Path]) -> AnalysisResult:
        """Analyze Python files using AST parsing."""
        result = AnalysisResult()

        # Track packages
        packages: dict[str, dict[str, Any]] = {}

        for file_path in python_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                # Parse AST
                tree = ast.parse(content, filename=str(file_path))

                # Get package info
                package_name = self._get_package_name(file_path)
                relative_path = self._get_relative_path(file_path)

                # Create visitor and analyze
                visitor = ASTVisitor(file_path, package_name)
                visitor.visit(tree)

                # Create file analysis data
                lines = content.splitlines()
                code_lines = len(
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

                file_data = {
                    "file_path": relative_path,
                    "file_name": file_path.name,
                    "package_name": package_name,
                    "lines_of_code": code_lines,
                    "comment_lines": comment_lines,
                    "blank_lines": blank_lines,
                    "total_lines": len(lines),
                    "complexity_score": sum(
                        func["cyclomatic_complexity"] for func in visitor.functions
                    )
                    / max(len(visitor.functions), 1),
                    "function_count": len(visitor.functions),
                    "class_count": len(visitor.classes),
                    "import_count": len(visitor.imports),
                    "variable_count": len(visitor.variables),
                }

                result.files.append(file_data)
                result.classes.extend(visitor.classes)
                result.functions.extend(visitor.functions)
                result.variables.extend(visitor.variables)
                result.imports.extend(visitor.imports)

                # Track package data
                if package_name not in packages:
                    packages[package_name] = {
                        "name": package_name,
                        "full_path": str(file_path.parent),
                        "files": [],
                        "total_lines": 0,
                        "code_lines": 0,
                        "comment_lines": 0,
                        "blank_lines": 0,
                        "total_functions": 0,
                        "total_classes": 0,
                        "complexity_scores": [],
                    }

                pkg = packages[package_name]
                pkg["files"].append(file_data)
                pkg["total_lines"] += file_data["total_lines"]
                pkg["code_lines"] += file_data["lines_of_code"]
                pkg["comment_lines"] += file_data["comment_lines"]
                pkg["blank_lines"] += file_data["blank_lines"]
                pkg["total_functions"] += file_data["function_count"]
                pkg["total_classes"] += file_data["class_count"]
                pkg["complexity_scores"].append(file_data["complexity_score"])

            except Exception as e:
                self.logger.exception(f"Error analyzing {file_path}: {e}")
                result.errors.append(
                    {"file": str(file_path), "error": str(e), "backend": self.name},
                )

        # Process package data
        for _pkg_name, pkg_data in packages.items():
            pkg_data["python_files_count"] = len(pkg_data["files"])
            pkg_data["avg_complexity"] = sum(pkg_data["complexity_scores"]) / max(
                len(pkg_data["complexity_scores"]),
                1,
            )
            pkg_data["max_complexity"] = (
                max(pkg_data["complexity_scores"])
                if pkg_data["complexity_scores"]
                else 0
            )
            del pkg_data["complexity_scores"]  # Remove temporary data
            del pkg_data["files"]  # Remove temporary data
            result.packages.append(pkg_data)

        return result
