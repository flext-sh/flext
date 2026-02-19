#!/usr/bin/env python3
# Owner-Skill: .claude/skills/scripts-testing/SKILL.md
"""Quick FLEXT Pytest Analysis - Generate SARIF/JSON reports for failing tests.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Constants
PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "test-analysis-output"
VENV_PATH = PROJECT_ROOT / ".venv" / "bin" / "activate"

PROJECTS = [
    "flext-core",
    "flext-cli",
    "flext-observability",
    "flext-grpc",
    "flext-web",
    "flext-api",
    "flext-auth",
]


def run_pytest_quick(project_path: Path, project_name: str) -> dict[str, object]:
    """Run pytest and return basic results."""
    try:
        cmd = ["python", "-m", "pytest", "--tb=line", "-q", "--maxfail=5", "tests/"]

        result = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=120,  # 2 minutes per project
            check=False,
            env=os.environ.copy(),
        )

        # Parse basic results
        lines = result.stdout.split("\n") + result.stderr.split("\n")
        passed = 0
        failed = 0
        failed_tests = []

        for line in lines:
            if line.startswith("PASSED"):
                passed += 1
            elif line.startswith(("FAILED", "ERROR")):
                failed += 1
                # Extract test name
                if "::" in line:
                    test_name = line.split("::")[-1].strip()
                    failed_tests.append(test_name)

        return {
            "project": project_name,
            "exit_code": result.returncode,
            "passed": passed,
            "failed": failed,
            "failed_tests": failed_tests[:10],  # Limit
            "stdout": result.stdout[-1000:],  # Last 1000 chars
            "stderr": result.stderr[-1000:],
            "timestamp": time.time(),
        }

    except subprocess.TimeoutExpired:
        return {
            "project": project_name,
            "exit_code": -1,
            "error": "Timeout after 120 seconds",
            "timestamp": time.time(),
        }
    except Exception as e:
        return {
            "project": project_name,
            "exit_code": -2,
            "error": str(e),
            "timestamp": time.time(),
        }


def generate_sarif_report(results: list[dict[str, object]]) -> dict[str, object]:
    """Generate SARIF report from results."""
    runs = []

    for result in results:
        run = {
            "tool": {"driver": {"name": "pytest", "version": "7.0.0"}},
            "results": [],
        }

        for test_name in result.get("failed_tests", []):
            run["results"].append({
                "ruleId": test_name,
                "level": "error",
                "message": {"text": f"Test failed in {result['project']}"},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": f"{result['project']}/tests/"},
                        },
                    },
                ],
            })

        if run["results"]:  # Only add runs with failures
            runs.append(run)

    return {
        "version": "2.1.0",
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "runs": runs,
    }


def main() -> None:
    """Main analysis function."""
    if not VENV_PATH.exists():
        print("❌ Virtual environment not found")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("🚀 Starting Quick FLEXT Pytest Analysis...")

    all_results = []
    failed_projects = []

    for project_name in PROJECTS:
        project_path = PROJECT_ROOT / project_name
        if not project_path.exists():
            print(f"⚠️  Project {project_name} not found, skipping")
            continue

        print(f"🔍 Analyzing {project_name}...")

        result = run_pytest_quick(project_path, project_name)
        all_results.append(result)

        if result["exit_code"] != 0:
            failed_projects.append(project_name)
            print(f"❌ {project_name}: {result.get('failed', 0)} failed")
        else:
            print(f"✅ {project_name}: {result.get('passed', 0)} passed")

        # Save individual result
        result_file = OUTPUT_DIR / f"{project_name}_result.json"
        with result_file.open("w") as f:
            json.dump(result, f, indent=2)

    # Generate consolidated report
    consolidated = {
        "timestamp": time.time(),
        "total_projects": len(all_results),
        "failed_projects": failed_projects,
        "results": all_results,
        "summary": {
            "total_passed": sum(r.get("passed", 0) for r in all_results),
            "total_failed": sum(r.get("failed", 0) for r in all_results),
            "projects_with_failures": len(failed_projects),
        },
    }

    # Save consolidated JSON
    consolidated_file = OUTPUT_DIR / "consolidated_analysis.json"
    with consolidated_file.open("w") as f:
        json.dump(consolidated, f, indent=2)

    # Generate SARIF
    sarif_report = generate_sarif_report(all_results)
    sarif_file = OUTPUT_DIR / "failures.sarif"
    with sarif_file.open("w") as f:
        json.dump(sarif_report, f, indent=2)

    print("\n📊 Analysis Complete!")
    print(f"📁 Results saved to: {OUTPUT_DIR}")
    print("📋 Consolidated: consolidated_analysis.json")
    print("🔍 SARIF Report: failures.sarif")

    if failed_projects:
        print(f"❌ Projects with failures: {', '.join(failed_projects)}")
        sys.exit(1)
    else:
        print("🎉 All projects passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
