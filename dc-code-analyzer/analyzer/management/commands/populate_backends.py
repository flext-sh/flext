"""
Django management command to populate backend and issue type data.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from analyzer.models import AnalysisBackendModel, IssueType


class Command(BaseCommand):
    help = "Populate backend and issue type data automatically"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force update existing data",
        )

    def handle(self, *_args, **options):
        self.stdout.write(
            self.style.SUCCESS("🚀 Populating backend and issue type data..."),
        )

        force_update = options["force"]

        # Create or update backends
        self._create_backends(force_update)

        # Create or update issue types
        self._create_issue_types(force_update)

        self.stdout.write(
            self.style.SUCCESS("✅ Backend and issue type data populated successfully!"),
        )

    def _create_backends(self, force_update):
        """Create or update backend definitions."""
        backends_data = [
            {
                "name": "ast",
                "display_name": "AST Analyzer",
                "description": "Python Abstract Syntax Tree analysis for structural code analysis",
                "capabilities": [
                    "class_analysis",
                    "function_analysis",
                    "variable_analysis",
                    "import_analysis",
                    "complexity_basic",
                ],
                "execution_order": 10,
                "default_enabled": True,
            },
            {
                "name": "external",
                "display_name": "External Tools",
                "description": "Integration with external security and quality tools (bandit, vulture)",
                "capabilities": [
                    "security_analysis",
                    "dead_code_detection",
                    "vulnerability_scanning",
                ],
                "execution_order": 20,
                "default_enabled": True,
            },
            {
                "name": "quality",
                "display_name": "Quality Metrics",
                "description": "Code quality metrics using radon (complexity, maintainability, Halstead)",
                "capabilities": [
                    "complexity_analysis",
                    "maintainability_index",
                    "halstead_metrics",
                    "raw_metrics",
                ],
                "execution_order": 30,
                "default_enabled": True,
            },
        ]

        for backend_data in backends_data:
            backend, created = AnalysisBackendModel.objects.get_or_create(
                name=backend_data["name"],
                defaults=backend_data,
            )

            if created:
                self.stdout.write(f"  ✅ Created backend: {backend.display_name}")
            elif force_update:
                for key, value in backend_data.items():
                    if key != "name":
                        setattr(backend, key, value)
                backend.updated_at = timezone.now()
                backend.save()
                self.stdout.write(f"  🔄 Updated backend: {backend.display_name}")
            else:
                self.stdout.write(f"  ℹ️  Backend exists: {backend.display_name}")

    def _create_issue_types(self, force_update):
        """Create or update issue type definitions."""

        # Get backend objects
        try:
            ast_backend = AnalysisBackendModel.objects.get(name="ast")
            external_backend = AnalysisBackendModel.objects.get(name="external")
            quality_backend = AnalysisBackendModel.objects.get(name="quality")
        except AnalysisBackendModel.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f"Backend not found: {e}"))
            return

        issue_types_data = [
            # AST Backend Issues
            {
                "backend": ast_backend,
                "code": "AST001",
                "name": "Missing Class Docstring",
                "description": "Class definition without documentation",
                "category": "documentation",
                "severity": "LOW",
                "recommendation": "Add a docstring to document the class purpose and usage",
            },
            {
                "backend": ast_backend,
                "code": "AST002",
                "name": "Missing Function Docstring",
                "description": "Function or method without documentation",
                "category": "documentation",
                "severity": "LOW",
                "recommendation": "Add a docstring to document function parameters and return value",
            },
            {
                "backend": ast_backend,
                "code": "AST003",
                "name": "Complex Function",
                "description": "Function with high cyclomatic complexity",
                "category": "complexity",
                "severity": "MEDIUM",
                "recommendation": "Consider breaking down the function into smaller, simpler functions",
            },
            {
                "backend": ast_backend,
                "code": "AST004",
                "name": "Too Many Parameters",
                "description": "Function has too many parameters",
                "category": "quality",
                "severity": "MEDIUM",
                "recommendation": "Consider using data classes or parameter objects to reduce parameter count",
            },
            {
                "backend": ast_backend,
                "code": "AST005",
                "name": "Deep Inheritance",
                "description": "Class with deep inheritance hierarchy",
                "category": "maintainability",
                "severity": "MEDIUM",
                "recommendation": "Consider composition over inheritance or flattening the hierarchy",
            },
            # External Tools Issues (Bandit Security)
            {
                "backend": external_backend,
                "code": "B101",
                "name": "Use of assert detected",
                "description": "Assert statements are removed when compiling to optimized byte code",
                "category": "security",
                "severity": "LOW",
                "recommendation": "Use explicit exception raising instead of assert for production code",
                "documentation_url": "https://bandit.readthedocs.io/en/latest/plugins/b101_assert_used.html",
            },
            {
                "backend": external_backend,
                "code": "B102",
                "name": "Test for exec used",
                "description": "Use of exec detected",
                "category": "security",
                "severity": "MEDIUM",
                "recommendation": "Avoid using exec() as it can execute arbitrary code",
                "documentation_url": "https://bandit.readthedocs.io/en/latest/plugins/b102_exec_used.html",
            },
            {
                "backend": external_backend,
                "code": "B103",
                "name": "Set bad file permissions",
                "description": "Chmod setting a permissive mask",
                "category": "security",
                "severity": "HIGH",
                "recommendation": "Use more restrictive file permissions",
                "documentation_url": (
                    "https://bandit.readthedocs.io/en/latest/plugins/"
                    "b103_set_bad_file_permissions.html"
                ),
            },
            {
                "backend": external_backend,
                "code": "B105",
                "name": "Hardcoded password string",
                "description": "Possible hardcoded password",
                "category": "security",
                "severity": "MEDIUM",
                "recommendation": "Use environment variables or secure configuration for passwords",
                "documentation_url": (
                    "https://bandit.readthedocs.io/en/latest/plugins/"
                    "b105_hardcoded_password_string.html"
                ),
            },
            {
                "backend": external_backend,
                "code": "B106",
                "name": "Hardcoded password funcarg",
                "description": "Possible hardcoded password in function arguments",
                "category": "security",
                "severity": "MEDIUM",
                "recommendation": "Avoid hardcoding passwords in function parameters",
                "documentation_url": (
                    "https://bandit.readthedocs.io/en/latest/plugins/"
                    "b106_hardcoded_password_funcarg.html"
                ),
            },
            {
                "backend": external_backend,
                "code": "B107",
                "name": "Hardcoded password default",
                "description": "Possible hardcoded password in function defaults",
                "category": "security",
                "severity": "MEDIUM",
                "recommendation": "Use None as default and load password from secure configuration",
                "documentation_url": (
                    "https://bandit.readthedocs.io/en/latest/plugins/"
                    "b107_hardcoded_password_default.html"
                ),
            },
            {
                "backend": external_backend,
                "code": "B108",
                "name": "Hardcoded tmp directory",
                "description": "Probable insecure usage of temp file/directory",
                "category": "security",
                "severity": "MEDIUM",
                "recommendation": "Use tempfile module for secure temporary file handling",
                "documentation_url": (
                    "https://bandit.readthedocs.io/en/latest/plugins/"
                    "b108_hardcoded_tmp_directory.html"
                ),
            },
            {
                "backend": external_backend,
                "code": "B301",
                "name": "Pickle and modules that wrap it",
                "description": "Pickle library appears to be in use",
                "category": "security",
                "severity": "MEDIUM",
                "recommendation": "Consider using safer serialization formats like JSON",
                "documentation_url": "https://bandit.readthedocs.io/en/latest/plugins/b301_pickle.html",
            },
            {
                "backend": external_backend,
                "code": "B401",
                "name": "Import telnet library",
                "description": "A telnet-related module is being imported",
                "category": "security",
                "severity": "HIGH",
                "recommendation": "Use SSH instead of telnet for secure communication",
                "documentation_url": "https://bandit.readthedocs.io/en/latest/plugins/b401_import_telnet.html",
            },
            {
                "backend": external_backend,
                "code": "B501",
                "name": "Request with no cert validation",
                "description": "Requesting network resources without certificate verification",
                "category": "security",
                "severity": "HIGH",
                "recommendation": "Enable SSL certificate verification in requests",
                "documentation_url": (
                    "https://bandit.readthedocs.io/en/latest/plugins/"
                    "b501_request_with_no_cert_validation.html"
                ),
            },
            # Dead Code Issues (Vulture)
            {
                "backend": external_backend,
                "code": "V001",
                "name": "Unused Function",
                "description": "Function is defined but never used",
                "category": "dead_code",
                "severity": "LOW",
                "recommendation": "Remove unused function or mark as intentionally unused",
            },
            {
                "backend": external_backend,
                "code": "V002",
                "name": "Unused Variable",
                "description": "Variable is assigned but never used",
                "category": "dead_code",
                "severity": "LOW",
                "recommendation": "Remove unused variable or prefix with underscore if intentionally unused",
            },
            {
                "backend": external_backend,
                "code": "V003",
                "name": "Unused Import",
                "description": "Module is imported but never used",
                "category": "dead_code",
                "severity": "LOW",
                "recommendation": "Remove unused import statement",
            },
            {
                "backend": external_backend,
                "code": "V004",
                "name": "Unused Class",
                "description": "Class is defined but never used",
                "category": "dead_code",
                "severity": "MEDIUM",
                "recommendation": "Remove unused class or ensure it's being used properly",
            },
            # Quality Backend Issues (Radon)
            {
                "backend": quality_backend,
                "code": "R901",
                "name": "Too Complex Function",
                "description": "Function has very high cyclomatic complexity",
                "category": "complexity",
                "severity": "HIGH",
                "recommendation": "Refactor function to reduce complexity by breaking it into smaller functions",
            },
            {
                "backend": quality_backend,
                "code": "R902",
                "name": "Too Many Instance Attributes",
                "description": "Class has too many instance attributes",
                "category": "quality",
                "severity": "MEDIUM",
                "recommendation": "Consider breaking class into smaller classes or using composition",
            },
            {
                "backend": quality_backend,
                "code": "R903",
                "name": "Too Many Public Methods",
                "description": "Class has too many public methods",
                "category": "quality",
                "severity": "MEDIUM",
                "recommendation": "Consider extracting related methods into separate classes",
            },
            {
                "backend": quality_backend,
                "code": "R904",
                "name": "Too Many Branches",
                "description": "Function has too many branches",
                "category": "complexity",
                "severity": "MEDIUM",
                "recommendation": "Simplify conditional logic or use polymorphism",
            },
            {
                "backend": quality_backend,
                "code": "R905",
                "name": "Too Many Arguments",
                "description": "Function has too many arguments",
                "category": "quality",
                "severity": "MEDIUM",
                "recommendation": "Use parameter objects or reduce number of parameters",
            },
            {
                "backend": quality_backend,
                "code": "R906",
                "name": "Too Many Local Variables",
                "description": "Function has too many local variables",
                "category": "quality",
                "severity": "MEDIUM",
                "recommendation": "Extract logic into separate functions or methods",
            },
            {
                "backend": quality_backend,
                "code": "M001",
                "name": "Low Maintainability Index",
                "description": "Code has low maintainability index score",
                "category": "maintainability",
                "severity": "MEDIUM",
                "recommendation": "Improve code quality by reducing complexity and adding documentation",
            },
            {
                "backend": quality_backend,
                "code": "H001",
                "name": "High Halstead Difficulty",
                "description": "Code has high Halstead difficulty score",
                "category": "complexity",
                "severity": "MEDIUM",
                "recommendation": "Simplify code structure and reduce operator/operand complexity",
            },
        ]

        created_count = 0
        updated_count = 0

        for issue_data in issue_types_data:
            issue_type, created = IssueType.objects.get_or_create(
                backend=issue_data["backend"],
                code=issue_data["code"],
                defaults=issue_data,
            )

            if created:
                created_count += 1
            elif force_update:
                for key, value in issue_data.items():
                    if key not in {"backend", "code"}:
                        setattr(issue_type, key, value)
                issue_type.updated_at = timezone.now()
                issue_type.save()
                updated_count += 1

        self.stdout.write(f"  ✅ Created {created_count} issue types")
        if force_update:
            self.stdout.write(f"  🔄 Updated {updated_count} issue types")
