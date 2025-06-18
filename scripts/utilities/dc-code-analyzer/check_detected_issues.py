#!/usr/bin/env python
"""Check detected issues in the database."""

import os

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "code_analyzer_web.settings")
django.setup()

# Django imports must come after django.setup()
from analyzer.models import AnalysisSession, IssueType  # noqa: E402


def check_detected_issues() -> None:
    """Check detected issues in the latest session."""
    # Get the latest session
    try:
        session = AnalysisSession.objects.latest("id")

        # Check detected issues
        detected_issues = session.detected_issues.all()

        if detected_issues.exists():
            for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
                count = detected_issues.filter(issue_type__severity=severity).count()
                if count > 0:
                    pass

            for _i, _issue in enumerate(detected_issues[:5], 1):
                pass

        # Check backend statistics
        backend_stats = session.backend_statistics.all()

        for _stat in backend_stats:
            pass

        # Check issue types
        for backend_name in ["ast", "external", "quality"]:
            count = IssueType.objects.filter(backend__name=backend_name).count()

    except AnalysisSession.DoesNotExist:
        pass


if __name__ == "__main__":
    check_detected_issues()
