#!/usr/bin/env python3
"""Generate linting report for FLEXT workspace."""

import json
import operator
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any


def analyze_project_linting(project_path: Path) -> dict[str, Any]:
    """Analyze linting issues for a single project."""
    try:
        # Run ruff check with JSON output
        result = subprocess.run(
            ["ruff", "check", "--output-format", "json", str(project_path)],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            return {"total": 0, "by_code": {}, "status": "clean"}

        issues = json.loads(result.stdout)
        by_code: defaultdict[str, int] = defaultdict(int)

        for issue in issues:
            by_code[issue["code"]] += 1

        return {"total": len(issues), "by_code": dict(by_code), "status": "has_issues"}
    except Exception as e:
        return {"total": 0, "by_code": {}, "status": f"error: {e}"}


def main() -> None:
    """Generate linting report for all projects."""
    workspace_root = Path(__file__).parent.parent

    # Collect all FLEXT projects
    projects = [
        path
        for path in sorted(workspace_root.iterdir())
        if path.is_dir()
        and path.name.startswith("flext-")
        and not path.name.startswith(".")
    ]

    # Also add other projects
    for name in ["client-a-oud-mig", "client-b-meltano-native", "client-b-poc-oic-wms"]:
        path = workspace_root / name
        if path.exists():
            projects.append(path)

    total_issues = 0
    all_codes: defaultdict[str, int] = defaultdict(int)

    print("# FLEXT WORKSPACE LINTING REPORT")
    print("=" * 80)
    print()

    for project in sorted(projects):
        print(f"\n## {project.name}")
        print("-" * 40)

        analysis = analyze_project_linting(project)
        total_issues += analysis["total"]

        if analysis["status"] == "clean":
            print("✅ No linting issues!")
        elif analysis["status"].startswith("error"):
            print(f"❌ {analysis['status']}")
        else:
            print(f"Total issues: {analysis['total']}")
            print("\nTop issues:")

            # Sort by count
            sorted_codes = sorted(
                analysis["by_code"].items(), key=operator.itemgetter(1), reverse=True
            )[:5]

            for code, count in sorted_codes:
                all_codes[code] += count
                print(f"  - {code}: {count}")

    print("\n" + "=" * 80)
    print("\n## WORKSPACE SUMMARY")
    print(f"Total projects analyzed: {len(projects)}")
    print(f"Total linting issues: {total_issues}")
    print("\nMost common issues across workspace:")

    sorted_all_codes = sorted(
        all_codes.items(), key=operator.itemgetter(1), reverse=True
    )[:10]
    for code, count in sorted_all_codes:
        print(f"  - {code}: {count}")

    print("\n## RECOMMENDED PRIORITY")
    print("Based on issue types, fix in this order:")
    print("1. Import sorting (I001, I002) - Safe to auto-fix")
    print("2. Whitespace issues (W291, W292, W293) - Safe to auto-fix")
    print("3. Line length (E501) - Requires manual review")
    print("4. Undefined names (F821) - Requires understanding context")
    print("5. Unused imports/variables (F401, F841) - May have side effects")


if __name__ == "__main__":
    main()
