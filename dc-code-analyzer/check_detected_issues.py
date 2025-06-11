#!/usr/bin/env python
"""Check detected issues in the database."""

import os

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "code_analyzer_web.settings")
django.setup()

# Django imports must come after django.setup()
from analyzer.models import AnalysisSession, IssueType  # noqa: E402


def check_detected_issues():
    """Check detected issues in the latest session."""
    print("🔍 Checking Detected Issues")
    print("=" * 50)

    # Get the latest session
    try:
        session = AnalysisSession.objects.latest("id")
        print(f"Latest session: {session.id}")
        print(f"Session status: {session.status}")
        print(f"Backends used: {session.backends_used}")
        print()

        # Check detected issues
        detected_issues = session.detected_issues.all()
        print(f"📊 Detected Issues: {detected_issues.count()}")

        if detected_issues.exists():
            print("\nIssues by severity:")
            for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
                count = detected_issues.filter(issue_type__severity=severity).count()
                if count > 0:
                    print(f"  {severity}: {count}")

            print("\nFirst 5 issues:")
            for i, issue in enumerate(detected_issues[:5], 1):
                print(f"  {i}. {issue.issue_type.code} - {issue.issue_type.name}")
                print(f"     File: {issue.file_path}:{issue.line_number}")
                print(
                    f"     Severity: {issue.severity} | Backend: {issue.backend_name}",
                )
                print(f"     Message: {issue.message[:80]}...")
                print()

        # Check backend statistics
        backend_stats = session.backend_statistics.all()
        print(f"📈 Backend Statistics: {backend_stats.count()}")

        for stat in backend_stats:
            name = stat.backend.name
            status = stat.status
            time = stat.execution_time
            issues = stat.issues_found
            print(f"  {name}: {status} - {time:.2f}s - {issues} issues")

        # Check issue types
        print(f"\n🏷️  Total Issue Types: {IssueType.objects.count()}")
        for backend_name in ["ast", "external", "quality"]:
            count = IssueType.objects.filter(backend__name=backend_name).count()
            print(f"  {backend_name}: {count} issue types")

    except AnalysisSession.DoesNotExist:
        print("No analysis session found")


if __name__ == "__main__":
    check_detected_issues()
