"""Django models for the code analyzer."""

from __future__ import annotations

from django.db import models


class Project(models.Model):
    """A code flx_project to be analyzed."""

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    path = models.CharField(
        max_length=500,
        help_text="Path to the flx_project directory",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Package information
    package_name = models.CharField(max_length=200, blank=True, null=True)
    package_version = models.CharField(max_length=50, blank=True, null=True)
    is_installed_package = models.BooleanField(default=False)
    install_location = models.CharField(max_length=500, blank=True, null=True)
    package_type = models.CharField(
        max_length=20,
        choices=[
            ("source", "Source Installation"),
            ("wheel", "Wheel Package"),
            ("system", "System Package"),
            ("local", "Local Package"),
        ],
        blank=True,
        null=True,
    )

    # Calculated flx_project metrics
    total_files = models.IntegerField(default=0)
    total_lines = models.IntegerField(default=0)
    python_files = models.IntegerField(default=0)

    class Meta:
        db_table = "analyzer_project"
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["package_name"]),
        ]

    def __str__(self):
        return self.name


class AnalysisSession(models.Model):
    """Analysis session for a flx_project."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    GRADE_CHOICES = [
        ("A+", "A+"),
        ("A", "A"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B", "B"),
        ("B-", "B-"),
        ("C+", "C+"),
        ("C", "C"),
        ("C-", "C-"),
        ("D+", "D+"),
        ("D", "D"),
        ("F", "F"),
    ]

    flx_project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="analysis_sessions",
    )
    name = models.CharField(max_length=200, default="Analysis Session")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Analysis configuration
    include_security = models.BooleanField(default=True)
    include_dead_code = models.BooleanField(default=True)
    include_duplicates = models.BooleanField(default=True)
    complexity_threshold = models.FloatField(default=10.0)
    similarity_threshold = models.FloatField(default=0.8)
    backends_used = models.JSONField(
        default=list,
        help_text="List of analysis backends used",
    )

    # Results
    overall_score = models.FloatField(null=True, blank=True)
    quality_grade = models.CharField(
        max_length=2,
        choices=GRADE_CHOICES,
        null=True,
        blank=True,
    )
    files_analyzed = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = "analyzer_analysis_session"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.flx_project.name} - {self.name} ({self.status})"

    @property
    def duration(self):
        """Calculate duration of analysis."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None


class FileAnalysis(models.Model):
    """Analysis results for a single file."""

    session = models.ForeignKey(
        AnalysisSession,
        on_delete=models.CASCADE,
        related_name="file_analyses",
    )
    file_path = models.CharField(max_length=500)
    file_name = models.CharField(max_length=255)

    # Metrics
    lines_of_code = models.IntegerField()
    comment_lines = models.IntegerField()
    blank_lines = models.IntegerField()
    complexity_score = models.FloatField()
    maintainability_score = models.FloatField()
    function_count = models.IntegerField()
    class_count = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analyzer_file_analysis"
        indexes = [
            models.Index(fields=["session", "file_path"]),
            models.Index(fields=["complexity_score"]),
        ]

    def __str__(self):
        return f"{self.file_name} (LOC: {self.lines_of_code})"

    @property
    def total_lines(self):
        """Total lines in the file."""
        return self.lines_of_code + self.comment_lines + self.blank_lines


class SecurityIssue(models.Model):
    """Security issues found by analysis."""

    SEVERITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("CRITICAL", "Critical"),
    ]

    CONFIDENCE_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
    ]

    session = models.ForeignKey(
        AnalysisSession,
        on_delete=models.CASCADE,
        related_name="security_issues",
    )
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    confidence = models.CharField(max_length=10, choices=CONFIDENCE_CHOICES)
    issue_type = models.CharField(max_length=100)
    test_id = models.CharField(max_length=50)
    file_path = models.CharField(max_length=500)
    line_number = models.IntegerField()
    description = models.TextField()
    recommendation = models.TextField()
    code_snippet = models.TextField(blank=True)
    is_fixed = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analyzer_security_issue"
        indexes = [
            models.Index(fields=["session", "severity"]),
            models.Index(fields=["file_path"]),
        ]

    def __str__(self):
        return f"{self.severity} - {self.issue_type} in {self.file_path}:{self.line_number}"


class DeadCodeIssue(models.Model):
    """Dead code issues found by analysis."""

    DEAD_TYPE_CHOICES = [
        ("function", "Unused Function"),
        ("variable", "Unused Variable"),
        ("import", "Unused Import"),
        ("class", "Unused Class"),
        ("unreachable", "Unreachable Code"),
    ]

    session = models.ForeignKey(
        AnalysisSession,
        on_delete=models.CASCADE,
        related_name="dead_code_issues",
    )
    dead_type = models.CharField(max_length=20, choices=DEAD_TYPE_CHOICES)
    name = models.CharField(max_length=200)
    file_path = models.CharField(max_length=500)
    line_number = models.IntegerField()
    confidence = models.FloatField()
    size_estimate = models.IntegerField(help_text="Lines of code that could be removed")
    is_fixed = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analyzer_dead_code_issue"
        indexes = [
            models.Index(fields=["session", "dead_type"]),
            models.Index(fields=["file_path"]),
        ]

    def __str__(self):
        return f"{self.dead_type} - {self.name} in {self.file_path}:{self.line_number}"


class DuplicateCodeBlock(models.Model):
    """Duplicate code blocks found by analysis."""

    session = models.ForeignKey(
        AnalysisSession,
        on_delete=models.CASCADE,
        related_name="duplicate_blocks",
    )
    block_hash = models.CharField(max_length=64, unique=True)
    lines_count = models.IntegerField()
    similarity_score = models.FloatField()
    content_preview = models.TextField()
    is_refactored = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analyzer_duplicate_code_block"
        indexes = [
            models.Index(fields=["session", "similarity_score"]),
        ]

    def __str__(self):
        return f"Duplicate block ({self.lines_count} lines, {self.similarity_score:.2f} similarity)"


class DuplicateLocation(models.Model):
    """Location of a duplicate code block."""

    duplicate_block = models.ForeignKey(
        DuplicateCodeBlock,
        on_delete=models.CASCADE,
        related_name="locations",
    )
    file_path = models.CharField(max_length=500)
    start_line = models.IntegerField()
    end_line = models.IntegerField()

    class Meta:
        db_table = "analyzer_duplicate_location"
        indexes = [
            models.Index(fields=["duplicate_block", "file_path"]),
        ]

    def __str__(self):
        return f"{self.file_path}:{self.start_line}-{self.end_line}"


class QualityMetrics(models.Model):
    """Overall quality metrics for an analysis session."""

    session = models.OneToOneField(
        AnalysisSession,
        on_delete=models.CASCADE,
        related_name="quality_metrics",
    )

    # Overall scores (0-100)
    overall_score = models.FloatField()
    complexity_score = models.FloatField()
    maintainability_score = models.FloatField()
    security_score = models.FloatField()
    documentation_score = models.FloatField()
    duplication_score = models.FloatField()

    # File metrics
    total_files = models.IntegerField()
    total_lines = models.IntegerField()
    total_functions = models.IntegerField()
    total_classes = models.IntegerField()

    # Complexity metrics
    avg_complexity = models.FloatField()
    max_complexity = models.FloatField()
    complex_functions_count = models.IntegerField()

    # Documentation metrics
    docstring_coverage = models.FloatField()
    documented_functions = models.IntegerField()

    # Issue counts
    security_issues_count = models.IntegerField()
    dead_code_items_count = models.IntegerField()
    duplicate_blocks_count = models.IntegerField()

    # Technical debt
    duplicate_lines_ratio = models.FloatField()
    technical_debt_ratio = models.FloatField()
    estimated_debt_hours = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analyzer_quality_metrics"

    def __str__(self):
        return f"Quality Metrics for {self.session} (Score: {self.overall_score:.1f})"


class AnalysisReport(models.Model):
    """Generated analysis reports."""

    REPORT_TYPE_CHOICES = [
        ("summary", "Summary Report"),
        ("detailed", "Detailed Report"),
        ("security", "Security Report"),
        ("quality", "Quality Report"),
        ("custom", "Custom Report"),
    ]

    FORMAT_CHOICES = [
        ("html", "HTML"),
        ("markdown", "Markdown"),
        ("pdf", "PDF"),
        ("json", "JSON"),
    ]

    session = models.ForeignKey(
        AnalysisSession,
        on_delete=models.CASCADE,
        related_name="reports",
    )
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    content = models.TextField()
    file_path = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    download_count = models.IntegerField(default=0)

    class Meta:
        db_table = "analyzer_analysis_report"
        indexes = [
            models.Index(fields=["session", "report_type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.report_type})"


# === NEW HIERARCHICAL ANALYSIS MODELS ===


class PackageAnalysis(models.Model):
    """Analysis results for a Python package."""

    session = models.ForeignKey(
        AnalysisSession,
        on_delete=models.CASCADE,
        related_name="package_analyses",
    )
    name = models.CharField(max_length=200)
    full_path = models.CharField(max_length=500)
    is_namespace = models.BooleanField(default=False)

    # Package metrics
    total_files = models.IntegerField(default=0)
    python_files_count = models.IntegerField(default=0)
    total_lines = models.IntegerField(default=0)
    code_lines = models.IntegerField(default=0)
    comment_lines = models.IntegerField(default=0)
    blank_lines = models.IntegerField(default=0)

    # Complexity metrics
    avg_complexity = models.FloatField(default=0.0)
    max_complexity = models.FloatField(default=0.0)
    total_functions = models.IntegerField(default=0)
    total_classes = models.IntegerField(default=0)
    total_methods = models.IntegerField(default=0)

    # Quality scores
    maintainability_score = models.FloatField(default=0.0)
    test_coverage = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analyzer_package_analysis"
        unique_together = [["session", "name"]]
        indexes = [
            models.Index(fields=["session", "name"]),
            models.Index(fields=["maintainability_score"]),
        ]

    def __str__(self):
        return f"{self.name} (Files: {self.python_files_count})"


class ClassAnalysis(models.Model):
    """Analysis results for a Python class."""

    COMPLEXITY_LEVELS = [
        ("low", "Low (1-5)"),
        ("medium", "Medium (6-10)"),
        ("high", "High (11-20)"),
        ("very_high", "Very High (21+)"),
    ]

    file_analysis = models.ForeignKey(
        FileAnalysis,
        on_delete=models.CASCADE,
        related_name="class_analyses",
    )
    package_analysis = models.ForeignKey(
        PackageAnalysis,
        on_delete=models.CASCADE,
        related_name="classes",
    )

    name = models.CharField(max_length=200)
    full_name = models.CharField(max_length=500)  # package.module.ClassName
    line_start = models.IntegerField()
    line_end = models.IntegerField()

    # Class metrics
    lines_of_code = models.IntegerField(default=0)
    method_count = models.IntegerField(default=0)
    property_count = models.IntegerField(default=0)
    class_method_count = models.IntegerField(default=0)
    static_method_count = models.IntegerField(default=0)

    # Inheritance info
    base_classes = models.JSONField(default=list)
    inheritance_depth = models.IntegerField(default=0)

    # Complexity
    complexity_score = models.FloatField(default=0.0)
    complexity_level = models.CharField(
        max_length=20,
        choices=COMPLEXITY_LEVELS,
        default="low",
    )

    # Documentation
    has_docstring = models.BooleanField(default=False)
    docstring_length = models.IntegerField(default=0)

    # Design patterns
    is_abstract = models.BooleanField(default=False)
    is_singleton = models.BooleanField(default=False)
    is_dataclass = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analyzer_class_analysis"
        unique_together = [["file_analysis", "name", "line_start"]]
        indexes = [
            models.Index(fields=["file_analysis", "name"]),
            models.Index(fields=["complexity_score"]),
            models.Index(fields=["method_count"]),
        ]

    def __str__(self):
        return f"{self.name} (Methods: {self.method_count})"


class FunctionAnalysis(models.Model):
    """Analysis results for functions and methods."""

    FUNCTION_TYPES = [
        ("function", "Function"),
        ("method", "Method"),
        ("classmethod", "Class Method"),
        ("staticmethod", "Static Method"),
        ("property", "Property"),
        ("async_function", "Async Function"),
        ("async_method", "Async Method"),
    ]

    COMPLEXITY_LEVELS = [
        ("low", "Low (1-5)"),
        ("medium", "Medium (6-10)"),
        ("high", "High (11-20)"),
        ("very_high", "Very High (21+)"),
    ]

    file_analysis = models.ForeignKey(
        FileAnalysis,
        on_delete=models.CASCADE,
        related_name="function_analyses",
    )
    class_analysis = models.ForeignKey(
        ClassAnalysis,
        on_delete=models.CASCADE,
        related_name="methods",
        null=True,
        blank=True,
    )
    package_analysis = models.ForeignKey(
        PackageAnalysis,
        on_delete=models.CASCADE,
        related_name="functions",
    )

    name = models.CharField(max_length=200)
    full_name = models.CharField(max_length=500)  # package.module.Class.method
    function_type = models.CharField(
        max_length=20,
        choices=FUNCTION_TYPES,
        default="function",
    )

    # Location
    line_start = models.IntegerField()
    line_end = models.IntegerField()

    # Function metrics
    lines_of_code = models.IntegerField(default=0)
    parameter_count = models.IntegerField(default=0)
    return_statement_count = models.IntegerField(default=0)

    # Complexity
    cyclomatic_complexity = models.IntegerField(default=1)
    cognitive_complexity = models.IntegerField(default=0)
    complexity_level = models.CharField(
        max_length=20,
        choices=COMPLEXITY_LEVELS,
        default="low",
    )

    # Documentation
    has_docstring = models.BooleanField(default=False)
    has_type_hints = models.BooleanField(default=False)
    docstring_length = models.IntegerField(default=0)

    # Code quality indicators
    has_too_many_parameters = models.BooleanField(default=False)
    has_long_parameter_list = models.BooleanField(default=False)
    is_too_long = models.BooleanField(default=False)

    # Function signature
    parameters = models.JSONField(default=list)
    return_type = models.CharField(max_length=100, blank=True)
    decorators = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analyzer_function_analysis"
        unique_together = [["file_analysis", "name", "line_start"]]
        indexes = [
            models.Index(fields=["file_analysis", "name"]),
            models.Index(fields=["function_type"]),
            models.Index(fields=["cyclomatic_complexity"]),
            models.Index(fields=["complexity_level"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.function_type}, CC: {self.cyclomatic_complexity})"


class VariableAnalysis(models.Model):
    """Analysis results for variables and constants."""

    VARIABLE_TYPES = [
        ("constant", "Constant"),
        ("global_var", "Global Variable"),
        ("class_var", "Class Variable"),
        ("instance_var", "Instance Variable"),
        ("local_var", "Local Variable"),
        ("parameter", "Parameter"),
    ]

    SCOPE_TYPES = [
        ("module", "Module Level"),
        ("class", "Class Level"),
        ("function", "Function Level"),
    ]

    file_analysis = models.ForeignKey(
        FileAnalysis,
        on_delete=models.CASCADE,
        related_name="variable_analyses",
    )
    class_analysis = models.ForeignKey(
        ClassAnalysis,
        on_delete=models.CASCADE,
        related_name="variables",
        null=True,
        blank=True,
    )
    function_analysis = models.ForeignKey(
        FunctionAnalysis,
        on_delete=models.CASCADE,
        related_name="variables",
        null=True,
        blank=True,
    )
    package_analysis = models.ForeignKey(
        PackageAnalysis,
        on_delete=models.CASCADE,
        related_name="variables",
    )

    name = models.CharField(max_length=200)
    full_name = models.CharField(max_length=500)
    variable_type = models.CharField(max_length=20, choices=VARIABLE_TYPES)
    scope_type = models.CharField(max_length=20, choices=SCOPE_TYPES)

    # Location
    line_number = models.IntegerField()

    # Type information
    inferred_type = models.CharField(max_length=100, blank=True)
    has_type_annotation = models.BooleanField(default=False)
    type_annotation = models.CharField(max_length=200, blank=True)

    # Value information
    is_constant = models.BooleanField(default=False)
    initial_value = models.TextField(blank=True)
    is_unused = models.BooleanField(default=False)

    # Naming conventions
    follows_naming_convention = models.BooleanField(default=True)
    naming_issue = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analyzer_variable_analysis"
        unique_together = [["file_analysis", "name", "line_number"]]
        indexes = [
            models.Index(fields=["variable_type"]),
            models.Index(fields=["is_unused"]),
            models.Index(fields=["is_constant"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.variable_type})"


class ImportAnalysis(models.Model):
    """Analysis results for imports."""

    IMPORT_TYPES = [
        ("standard", "Standard Library"),
        ("third_party", "Third Party"),
        ("local", "Local/Project"),
        ("relative", "Relative Import"),
    ]

    file_analysis = models.ForeignKey(
        FileAnalysis,
        on_delete=models.CASCADE,
        related_name="import_analyses",
    )
    package_analysis = models.ForeignKey(
        PackageAnalysis,
        on_delete=models.CASCADE,
        related_name="imports",
    )

    module_name = models.CharField(max_length=200)
    import_name = models.CharField(max_length=200, blank=True)  # For "from X import Y"
    alias = models.CharField(max_length=200, blank=True)  # For "import X as Y"
    import_type = models.CharField(max_length=20, choices=IMPORT_TYPES)

    # Location
    line_number = models.IntegerField()

    # Import details
    is_wildcard = models.BooleanField(default=False)  # from module import *
    is_unused = models.BooleanField(default=False)
    usage_count = models.IntegerField(default=0)

    # Quality checks
    is_circular = models.BooleanField(default=False)
    is_deprecated = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analyzer_import_analysis"
        unique_together = [
            ["file_analysis", "module_name", "import_name", "line_number"],
        ]
        indexes = [
            models.Index(fields=["import_type"]),
            models.Index(fields=["is_unused"]),
            models.Index(fields=["is_circular"]),
        ]

    def __str__(self):
        if self.import_name:
            return f"from {self.module_name} import {self.import_name}"
        return f"import {self.module_name}"


# === BACKEND MANAGEMENT MODELS ===


class AnalysisBackendModel(models.Model):
    """Model to manage available analysis backends."""

    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField()
    version = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(default=False)

    # Configuration
    capabilities = models.JSONField(default=list)
    default_enabled = models.BooleanField(default=True)
    execution_order = models.IntegerField(default=100)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_check_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "analyzer_backend"
        ordering = ["execution_order", "name"]
        indexes = [
            models.Index(fields=["is_active", "is_available"]),
            models.Index(fields=["execution_order"]),
        ]

    def __str__(self):
        return f"{self.display_name} ({'Active' if self.is_active else 'Inactive'})"


class IssueType(models.Model):
    """Types of issues that can be detected by backends."""

    SEVERITY_CHOICES = [
        ("INFO", "Info"),
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("CRITICAL", "Critical"),
    ]

    CATEGORY_CHOICES = [
        ("security", "Security"),
        ("quality", "Code Quality"),
        ("complexity", "Complexity"),
        ("dead_code", "Dead Code"),
        ("style", "Code Style"),
        ("documentation", "Documentation"),
        ("performance", "Performance"),
        ("maintainability", "Maintainability"),
        ("best_practices", "Best Practices"),
    ]

    backend = models.ForeignKey(
        AnalysisBackendModel,
        on_delete=models.CASCADE,
        related_name="issue_types",
    )

    # Issue identification
    code = models.CharField(max_length=50)  # e.g., "B101", "C901", etc.
    name = models.CharField(max_length=200)
    description = models.TextField()

    # Classification
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)

    # Documentation
    recommendation = models.TextField(blank=True)
    documentation_url = models.URLField(blank=True)
    examples = models.JSONField(default=list)

    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "analyzer_issue_type"
        unique_together = [["backend", "code"]]
        indexes = [
            models.Index(fields=["backend", "category"]),
            models.Index(fields=["severity", "category"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.backend.name}:{self.code} - {self.name}"


class DetectedIssue(models.Model):
    """Specific issues detected during analysis."""

    session = models.ForeignKey(
        AnalysisSession,
        on_delete=models.CASCADE,
        related_name="detected_issues",
    )
    issue_type = models.ForeignKey(
        IssueType,
        on_delete=models.CASCADE,
        related_name="detections",
    )
    file_analysis = models.ForeignKey(
        FileAnalysis,
        on_delete=models.CASCADE,
        related_name="detected_issues",
        null=True,
        blank=True,
    )

    # Location information
    file_path = models.CharField(max_length=500)
    line_number = models.IntegerField()
    column = models.IntegerField(default=0)

    # Issue details
    message = models.TextField()
    code_snippet = models.TextField(blank=True)
    context = models.JSONField(default=dict)

    # Confidence and metadata from backend
    confidence = models.CharField(
        max_length=10,
        choices=[("LOW", "Low"), ("MEDIUM", "Medium"), ("HIGH", "High")],
        default="MEDIUM",
    )
    raw_data = models.JSONField(default=dict)

    # Resolution tracking
    is_false_positive = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    # Detection metadata
    detected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analyzer_detected_issue"
        indexes = [
            models.Index(fields=["session", "issue_type"]),
            models.Index(fields=["file_path", "line_number"]),
            models.Index(fields=["is_resolved", "is_false_positive"]),
            models.Index(fields=["detected_at"]),
        ]

    def __str__(self):
        return f"{self.issue_type.code} in {self.file_path}:{self.line_number}"

    @property
    def severity(self):
        return self.issue_type.severity

    @property
    def category(self):
        return self.issue_type.category

    @property
    def backend_name(self):
        return self.issue_type.backend.name


# === BACKEND STATISTICS ===


class BackendStatistics(models.Model):
    """Statistics for backend performance and results."""

    session = models.ForeignKey(
        AnalysisSession,
        on_delete=models.CASCADE,
        related_name="backend_statistics",
    )
    backend = models.ForeignKey(
        AnalysisBackendModel,
        on_delete=models.CASCADE,
        related_name="statistics",
    )

    # Execution metrics
    execution_time = models.FloatField()  # seconds
    files_processed = models.IntegerField()
    issues_found = models.IntegerField()

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ("success", "Success"),
            ("partial", "Partial Success"),
            ("failed", "Failed"),
            ("skipped", "Skipped"),
        ],
        default="success",
    )
    error_message = models.TextField(blank=True)

    # Results breakdown
    issues_by_severity = models.JSONField(default=dict)
    issues_by_category = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "analyzer_backend_statistics"
        unique_together = [["session", "backend"]]
        indexes = [
            models.Index(fields=["session", "status"]),
            models.Index(fields=["backend", "created_at"]),
        ]

    def __str__(self):
        return f"{self.backend.name} - {self.session} ({self.status})"
