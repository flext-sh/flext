#!/usr/bin/env python3
"""Analyze documentation scripts for migration to flext-quality."""

import json
import re
from pathlib import Path
from typing import Any


def analyze_script_functionality(script_path: Path) -> dict[str, Any]:
    """Analyze a single documentation script for its functionality."""
    content = script_path.read_text(encoding="utf-8")

    analysis = {
        "script_path": str(script_path),
        "name": script_path.stem,
        "size_bytes": script_path.stat().st_size,
        "functions": [],
        "features": [],
        "dependencies": [],
        "classification": None,
        "migration_recommendation": None,
    }

    # Extract function definitions
    function_pattern = r"def\s+(\w+)\s*\("
    functions = re.findall(function_pattern, content)
    analysis["functions"] = functions

    # Detect common documentation features
    feature_patterns = {
        "link_validation": r"(link|url|href|404|validate)",
        "content_audit": r"(audit|quality|score|metric)",
        "documentation_generation": r"(generate|build|create|doc.*gen)",
        "synchronization": r"(sync|update|merge|git)",
        "markdown_processing": r"(markdown|md|frontmatter)",
        "styling": r"(style|format|lint|check.*style)",
        "templating": r"(template|jinja|render)",
        "dashboard": r"(dashboard|ui|web|report)",
        "automation": r"(schedule|cron|auto|batch)",
        "configuration": r"(config|settings|profile)",
        "qa": r"(qa|quality|test|validate)",
        "optimization": r"(optim|compress|reduce)",
    }

    for feature, pattern in feature_patterns.items():
        if re.search(pattern, content, re.IGNORECASE):
            analysis["features"].append(feature)

    # Extract dependencies
    import_pattern = r"^(?:from|import)\s+([.\w]+)"
    imports = re.findall(import_pattern, content, re.MULTILINE)
    analysis["dependencies"] = list(set(imports))

    # Classify script
    if "dashboard" in analysis["features"]:
        analysis["classification"] = "UI/Dashboard"
    elif "synchronization" in analysis["features"]:
        analysis["classification"] = "Version Control Sync"
    elif "link_validation" in analysis["features"]:
        analysis["classification"] = "Link Validation"
    elif "documentation_generation" in analysis["features"]:
        analysis["classification"] = "Documentation Generation"
    elif "qa" in analysis["features"] or "quality" in analysis["name"].lower():
        analysis["classification"] = "Quality Assurance"
    elif "automation" in analysis["features"]:
        analysis["classification"] = "Automation/Scheduling"
    elif "optimization" in analysis["features"]:
        analysis["classification"] = "Content Optimization"
    elif "styling" in analysis["features"]:
        analysis["classification"] = "Style Validation"
    else:
        analysis["classification"] = "Other"

    return analysis


def generate_migration_matrix(analyses: list[dict[str, Any]]) -> str:
    """Generate migration decision matrix."""
    lines = []
    lines.extend((
        "\n" + "=" * 120,
        "DOCUMENTATION SCRIPT MIGRATION ANALYSIS MATRIX",
        "=" * 120,
        "",
    ))

    # Group by classification
    by_classification = {}
    for analysis in analyses:
        classification = analysis["classification"]
        if classification not in by_classification:
            by_classification[classification] = []
        by_classification[classification].append(analysis)

    # Print by classification
    for classification in sorted(by_classification.keys()):
        lines.extend((f"\n{classification.upper()}", "-" * 120))

        for analysis in by_classification[classification]:
            lines.extend((
                f"\n📄 {analysis['name']}",
                f"   Path: {analysis['script_path']}",
                f"   Size: {analysis['size_bytes']} bytes",
                f"   Functions: {', '.join(analysis['functions'][:5])}",
            ))
            if len(analysis["functions"]) > 5:
                lines.append(
                    f"             ... and {len(analysis['functions']) - 5} more"
                )
            lines.extend((
                f"   Features: {', '.join(analysis['features'])}",
                f"   Dependencies: {', '.join(analysis['dependencies'][:5])}",
            ))

    lines.extend((
        "\n" + "=" * 120,
        "FLEXT-QUALITY DOC CAPABILITIES",
        "=" * 120,
        """\nThe 'flext-quality doc comprehensive' command provides:\n- ✅ Content Audit (quality scoring, metrics collection)\n- ✅ Link Validation (404 checking, URL validation)\n- ✅ Style Validation (markdown consistency, formatting)\n- ✅ Content Optimization (compression, structure improvement)\n- ✅ Report Generation (comprehensive documentation reports)\n- ✅ Profile-based customization (advanced, basic, custom profiles)\n- ❓ Dashboard/UI (not native, but can be extended)\n- ❓ Git Synchronization (not native, but can be extended)\n- ❓ Scheduling/Automation (not native, but can be extended)\n""",
        "\n" + "=" * 120,
        "MIGRATION RECOMMENDATIONS BY FEATURE",
        "=" * 120,
    ))

    recommendations = {
        "Link Validation": (
            "MIGRATE",
            "Fully covered by flext-quality doc link_validation",
        ),
        "Content Audit": (
            "MIGRATE",
            "Fully covered by flext-quality doc content_audit",
        ),
        "Style Validation": (
            "MIGRATE",
            "Fully covered by flext-quality doc style_validation",
        ),
        "Documentation Generation": (
            "MIGRATE",
            "Fully covered by flext-quality doc generation",
        ),
        "Content Optimization": (
            "MIGRATE",
            "Fully covered by flext-quality doc optimization",
        ),
        "Quality Assurance": (
            "MIGRATE",
            "Fully covered by flext-quality doc quality checks",
        ),
        "UI/Dashboard": (
            "ENHANCE",
            "Partial coverage - needs flext-quality dashboard enhancement",
        ),
        "Version Control Sync": (
            "ENHANCE",
            "Partial coverage - needs flext-quality git sync enhancement",
        ),
        "Automation/Scheduling": (
            "ENHANCE",
            "Partial coverage - consider external scheduler + flext-quality",
        ),
        "Other": ("REVIEW", "Requires case-by-case analysis"),
    }

    for classification in sorted(recommendations.keys()):
        action, reason = recommendations[classification]
        lines.extend((f"\n{classification}: [{action}]", f"  Reason: {reason}"))

    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    import sys

    # Load inventory
    inventory_file = Path("scripts/doc_scripts_inventory.json")
    if not inventory_file.exists():
        print(
            "Error: doc_scripts_inventory.json not found. Run discover_doc_scripts.py first."
        )
        sys.exit(1)

    with Path(inventory_file).open(encoding="utf-8") as f:
        inventory = json.load(f)

    print("Analyzing documentation scripts...")
    print()

    analyses = []
    for script_info in inventory["script_details"]:
        script_path = Path(script_info["full_path"])
        if script_path.exists():
            print(f"  Analyzing: {script_info['project']}/{script_info['script_path']}")
            analysis = analyze_script_functionality(script_path)
            analyses.append(analysis)

    # Generate migration matrix
    matrix = generate_migration_matrix(analyses)
    print(matrix)

    # Save analysis results
    output_file = Path("scripts/doc_scripts_analysis.json")
    with Path(output_file).open("w", encoding="utf-8") as f:
        json.dump(
            {
                "analyzed_scripts": len(analyses),
                "analyses": analyses,
                "timestamp": str(Path.cwd()),
            },
            f,
            indent=2,
        )

    print(f"\n✅ Analysis saved to: {output_file}")


if __name__ == "__main__":
    main()
