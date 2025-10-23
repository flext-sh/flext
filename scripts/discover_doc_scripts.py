#!/usr/bin/env python3
"""Discover and analyze documentation maintenance scripts in all FLEXT projects."""

import json
from pathlib import Path
from typing import Any


def discover_doc_scripts(workspace_root: Path) -> dict[str, Any]:
    """Discover documentation maintenance scripts across all projects."""
    patterns = [
        "docs/maintenance/*.py",
        "scripts/*doc*.py",
        "scripts/*maintenance*.py",
        "docs/**/*maintenance*.py",
    ]

    findings = {
        "workspace_root": str(workspace_root),
        "projects_scanned": 0,
        "projects_with_doc_scripts": [],
        "total_scripts_found": 0,
        "script_details": [],
    }

    # Scan all flext-* and client-a-* and client-b-* directories
    for project_dir in sorted(workspace_root.glob("flext-*")):
        if not project_dir.is_dir():
            continue

        findings["projects_scanned"] += 1
        project_name = project_dir.name

        # Search for documentation scripts
        found_scripts = []

        for pattern in patterns:
            found_scripts.extend(
                script_file
                for script_file in project_dir.glob(pattern)
                if script_file.is_file() and script_file.suffix == ".py"
            )

        if found_scripts:
            findings["projects_with_doc_scripts"].append(project_name)
            findings["total_scripts_found"] += len(found_scripts)

            for script_file in found_scripts:
                rel_path = script_file.relative_to(project_dir)
                script_info = {
                    "project": project_name,
                    "script_path": str(rel_path),
                    "full_path": str(script_file),
                    "size_bytes": script_file.stat().st_size,
                    "has_if_main": "__main__" in script_file.read_text(),
                }
                findings["script_details"].append(script_info)

    # Also scan other project prefixes
    for prefix in ["client-a-", "client-b-"]:
        for project_dir in sorted(workspace_root.glob(f"{prefix}*")):
            if not project_dir.is_dir():
                continue

            findings["projects_scanned"] += 1
            project_name = project_dir.name

            found_scripts = []
            for pattern in patterns:
                for script_file in project_dir.glob(pattern):
                    if script_file.is_file() and script_file.suffix == ".py":
                        found_scripts.append(script_file)

            if found_scripts:
                findings["projects_with_doc_scripts"].append(project_name)
                findings["total_scripts_found"] += len(found_scripts)

                for script_file in found_scripts:
                    rel_path = script_file.relative_to(project_dir)
                    script_info = {
                        "project": project_name,
                        "script_path": str(rel_path),
                        "full_path": str(script_file),
                        "size_bytes": script_file.stat().st_size,
                        "has_if_main": "__main__" in script_file.read_text(),
                    }
                    findings["script_details"].append(script_info)

    return findings


def generate_report(findings: dict[str, Any]) -> str:
    """Generate a summary report of documentation scripts."""
    report = []
    report.extend((
        "=" * 80,
        "FLEXT ECOSYSTEM DOCUMENTATION SCRIPT DISCOVERY REPORT",
        "=" * 80,
        "",
        "SUMMARY",
        "-" * 80,
        f"Projects Scanned: {findings['projects_scanned']}",
        f"Projects with Doc Scripts: {len(findings['projects_with_doc_scripts'])}",
        f"Total Scripts Found: {findings['total_scripts_found']}",
        "",
    ))

    if findings["projects_with_doc_scripts"]:
        report.extend(("PROJECTS WITH DOCUMENTATION SCRIPTS", "-" * 80))
        report.extend(
            f"  • {project}"
            for project in sorted(findings["projects_with_doc_scripts"])
        )
        report.append("")

    if findings["script_details"]:
        report.extend(("DETAILED SCRIPT INVENTORY", "-" * 80))
        for script in findings["script_details"]:
            report.extend((
                f"\nProject: {script['project']}",
                f"  Path: {script['script_path']}",
                f"  Size: {script['size_bytes']} bytes",
                f"  Standalone: {'Yes' if script['has_if_main'] else 'No'}",
            ))

    report.extend((
        "",
        "=" * 80,
        "NEXT STEPS",
        "=" * 80,
        "1. Review each script for functionality",
        "2. Determine if functionality is covered by flext-quality doc",
        "3. Migrate or justify each script",
        "4. Remove redundant scripts",
        "",
    ))

    return "\n".join(report)


def main() -> None:
    """Main entry point."""
    import sys

    workspace_root = Path.cwd()
    print(f"Scanning workspace: {workspace_root}")
    print()

    findings = discover_doc_scripts(workspace_root)

    # Print report
    report = generate_report(findings)
    print(report)

    # Save findings to JSON
    output_file = workspace_root / "scripts" / "doc_scripts_inventory.json"
    output_file.parent.mkdir(exist_ok=True)

    with Path(output_file).open("w", encoding="utf-8") as f:
        json.dump(findings, f, indent=2)

    print(f"✅ Detailed findings saved to: {output_file}")
    print()

    if findings["total_scripts_found"] == 0:
        print("✅ No documentation scripts found - ecosystem is clean!")
        sys.exit(0)
    else:
        print(
            f"⚠️  Found {findings['total_scripts_found']} documentation scripts "
            "requiring review"
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
