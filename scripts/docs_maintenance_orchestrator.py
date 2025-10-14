#!/usr/bin/env python3
"""FLEXT Documentation Maintenance Orchestrator.

Comprehensive documentation maintenance system that coordinates all maintenance operations
with quality assurance, validation, and automated updates.
"""

import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from flext_core import FlextCore


@dataclass
class MaintenanceResults:
    """Comprehensive maintenance results."""

    timestamp: datetime
    audit_results: dict[str, object] = field(default_factory=dict)
    validation_results: dict[str, object] = field(default_factory=dict)
    optimization_results: dict[str, object] = field(default_factory=dict)
    sync_results: dict[str, object] = field(default_factory=dict)
    reports_generated: FlextCore.Types.StringList = field(default_factory=list)
    errors: FlextCore.Types.StringList = field(default_factory=list)
    warnings: FlextCore.Types.StringList = field(default_factory=list)


class DocumentationMaintenanceOrchestrator:
    """Main orchestrator for comprehensive documentation maintenance."""

    def __init__(self, config_file: str | None = None) -> None:
        self.config_file = config_file or "docs/docs_maintenance_config.json"
        self.config = self.load_config()
        self.output_dir = Path(self.config.get("output_dir", "docs/reports"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize sub-systems
        self.maintenance_system = None
        self.link_validator = None
        self.style_checker = None
        self.sync_system = None

    def load_config(self) -> dict[str, object]:
        """Load configuration from file or use defaults."""
        default_config = {
            "output_dir": "docs/reports",
            "audit_enabled": True,
            "validation_enabled": True,
            "optimization_enabled": True,
            "sync_enabled": False,  # Disabled by default for safety
            "verbose": False,
            "parallel_processing": True,
            "max_concurrent": 5,
            "maintenance_schedule": {
                "audit": "daily",
                "validation": "weekly",
                "optimization": "weekly",
                "sync": "manual",
            },
        }

        if Path(self.config_file).exists():
            try:
                with Path(self.config_file).open(encoding="utf-8") as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")

        return default_config

    def initialize_subsystems(self) -> None:
        """Initialize all maintenance subsystems."""
        try:
            # Import and initialize subsystems
            from docs_link_validator import LinkValidator
            from docs_maintenance_system import DocumentationMaintenanceSystem
            from docs_style_checker import DocumentationStyleChecker
            from docs_sync_system import DocumentationSyncSystem

            self.maintenance_system = DocumentationMaintenanceSystem(self.config_file)
            self.link_validator = LinkValidator(self.config)
            self.style_checker = DocumentationStyleChecker(self.config)
            self.sync_system = DocumentationSyncSystem(self.config)

        except ImportError as e:
            print(f"Error initializing subsystems: {e}")
            print("Make sure all maintenance scripts are in the scripts/ directory")
            sys.exit(1)

    def run_comprehensive_audit(self, verbose: bool = False) -> dict[str, object]:
        """Run comprehensive documentation audit."""
        if not self.maintenance_system:
            self.initialize_subsystems()

        print("🔍 Running comprehensive documentation audit...")

        try:
            # Run the maintenance system audit
            audit_result = self.maintenance_system.run_audit(verbose=verbose)

            results = {
                "total_files": audit_result.total_files,
                "completeness_score": audit_result.completeness_score,
                "issues_found": sum(
                    len(issues) for issues in audit_result.issues.values()
                ),
                "broken_links": audit_result.broken_links,
                "missing_images": audit_result.missing_images,
                "outdated_files": audit_result.outdated_files,
                "style_issues": audit_result.style_issues,
                "issues_by_category": {
                    k: len(v) for k, v in audit_result.issues.items()
                },
            }

            # Generate audit report
            report_file = f"docs_maintenance_audit_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.md"
            report_path = self.output_dir / report_file
            report_content = self.maintenance_system.generate_report(audit_result)
            report_path.write_text(report_content, encoding="utf-8")

            results["report_file"] = str(report_path)

            print("✅ Comprehensive audit complete!")
            return results

        except Exception as e:
            error_msg = f"Audit failed: {e}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}

    def run_link_validation(self, verbose: bool = False) -> dict[str, object]:
        """Run comprehensive link validation."""
        if not self.link_validator:
            self.initialize_subsystems()

        print("🔗 Running comprehensive link validation...")

        try:
            # Discover documentation files
            doc_files = []
            for pattern in ["*.md", "*.mdx"]:
                doc_files.extend(Path().rglob(pattern))

            if not doc_files:
                return {"error": "No documentation files found"}

            # Validate all links
            all_external_links = set()
            internal_issues = {}

            for doc_file in doc_files:
                links = self.link_validator.extract_links_from_file(doc_file)
                for url, _ in links:
                    if url.startswith(("http://", "https://")):
                        all_external_links.add(url)

            # Validate external links
            print(f"  Validating {len(all_external_links)} external links...")
            external_results = self.link_validator.validate_links_batch(
                list(all_external_links)
            )

            # Validate internal links
            print("  Validating internal links...")
            internal_issues = self.link_validator.validate_internal_links(doc_files)

            # Analyze results
            validation_results = self.link_validator.analyze_link_health(
                external_results
            )
            report = self.link_validator.generate_report(
                validation_results, internal_issues
            )

            # Save report
            report_file = (
                f"docs_link_validation_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.md"
            )
            report_path = self.output_dir / report_file
            report_path.write_text(report, encoding="utf-8")

            results = {
                "total_links": validation_results.total_links,
                "valid_links": validation_results.valid_links,
                "broken_links": validation_results.broken_links,
                "redirected_links": validation_results.redirected_links,
                "timeout_links": validation_results.timeout_links,
                "internal_issues": sum(
                    len(issues) for issues in internal_issues.values()
                ),
                "report_file": str(report_path),
            }

            print("✅ Link validation complete!")
            return results

        except Exception as e:
            error_msg = f"Link validation failed: {e}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}

    def run_style_checking(self, verbose: bool = False) -> dict[str, object]:
        """Run comprehensive style checking."""
        if not self.style_checker:
            self.initialize_subsystems()

        print("🎨 Running comprehensive style checking...")

        try:
            # Discover documentation files
            doc_files = []
            for pattern in ["*.md", "*.mdx"]:
                doc_files.extend(Path().rglob(pattern))

            if not doc_files:
                return {"error": "No documentation files found"}

            # Check all files
            results = self.style_checker.check_files(doc_files)
            report = self.style_checker.generate_report(results)

            # Save report
            report_file = (
                f"docs_style_check_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.md"
            )
            report_path = self.output_dir / report_file
            report_path.write_text(report, encoding="utf-8")

            style_results = {
                "total_files": results.total_files,
                "files_with_issues": len(results.files_with_issues),
                "total_issues": results.total_issues,
                "critical_issues": len(results.issues_by_severity.get("critical", [])),
                "high_priority": len(results.issues_by_severity.get("high", [])),
                "issues_by_type": {
                    k: len(v) for k, v in results.issues_by_type.items()
                },
                "report_file": str(report_path),
            }

            print("✅ Style checking complete!")
            return style_results

        except Exception as e:
            error_msg = f"Style checking failed: {e}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}

    def run_optimization(
        self, dry_run: bool = False, verbose: bool = False
    ) -> dict[str, object]:
        """Run content optimization."""
        if not self.maintenance_system:
            self.initialize_subsystems()

        print("🔧 Running content optimization...")

        try:
            optimization_results = self.maintenance_system.optimize_content(
                dry_run=dry_run
            )

            if verbose:
                print(f"  Files processed: {optimization_results['files_processed']}")
                print(
                    f"  Optimizations applied: {optimization_results['optimizations_applied']}"
                )

            return optimization_results

        except Exception as e:
            error_msg = f"Optimization failed: {e}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}

    def run_synchronization(
        self, dry_run: bool = False, verbose: bool = False
    ) -> dict[str, object]:
        """Run synchronization with version control."""
        if not self.sync_system:
            self.initialize_subsystems()

        print("🔄 Running synchronization...")

        try:
            # Run maintenance workflow
            results = self.sync_system.run_maintenance_workflow(dry_run=dry_run)

            if verbose:
                if "commit_hash" in results.get("sync_result", {}):
                    print(f"  Commit: {results['sync_result']['commit_hash']}")
                else:
                    print(
                        f"  Status: {results['sync_result'].get('message', 'No changes')}"
                    )

            return results

        except Exception as e:
            error_msg = f"Synchronization failed: {e}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}

    def run_full_maintenance_cycle(
        self, dry_run: bool = False, verbose: bool = False
    ) -> MaintenanceResults:
        """Run complete maintenance cycle."""
        print("🚀 Starting full documentation maintenance cycle...")

        results = MaintenanceResults(timestamp=datetime.now(UTC))

        # Initialize subsystems
        self.initialize_subsystems()

        # 1. Run audit
        if self.config.get("audit_enabled", True):
            print("\n1️⃣ Content Quality Audit")
            results.audit_results = self.run_comprehensive_audit(verbose=verbose)

        # 2. Run validation
        if self.config.get("validation_enabled", True):
            print("\n2️⃣ Link and Reference Validation")
            results.validation_results = self.run_link_validation(verbose=verbose)

        # 3. Run style checking
        if self.config.get("style_check_enabled", True):
            print("\n3️⃣ Style and Consistency Checking")
            style_results = self.run_style_checking(verbose=verbose)
            results.audit_results.update(style_results)

        # 4. Run optimization
        if self.config.get("optimization_enabled", True):
            print("\n4️⃣ Content Optimization")
            results.optimization_results = self.run_optimization(
                dry_run=dry_run, verbose=verbose
            )

        # 5. Run synchronization
        if self.config.get("sync_enabled", False):
            print("\n5️⃣ Version Control Synchronization")
            results.sync_results = self.run_synchronization(
                dry_run=dry_run, verbose=verbose
            )

        # Generate comprehensive report
        print("\n6️⃣ Generating Comprehensive Report")
        comprehensive_report = self.generate_comprehensive_report(results)
        report_file = f"docs_maintenance_comprehensive_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.md"
        report_path = self.output_dir / report_file
        report_path.write_text(comprehensive_report, encoding="utf-8")
        results.reports_generated.append(str(report_path))

        print("✅ Full maintenance cycle complete!")
        print(f"📄 Comprehensive report: {report_path}")

        return results

    def generate_comprehensive_report(self, results: MaintenanceResults) -> str:
        """Generate comprehensive maintenance report."""
        report = f"""# FLEXT Documentation Maintenance Report

**Generated:** {results.timestamp.strftime("%Y-%m-%d %H:%M:%S")}

## 📊 Executive Summary

### Maintenance Cycle Overview
- **Audit Results:** {results.audit_results.get("issues_found", 0)} issues found across {results.audit_results.get("total_files", 0)} files
- **Link Validation:** {results.validation_results.get("broken_links", 0)} broken links, {results.validation_results.get("internal_issues", 0)} internal issues
- **Style Issues:** {results.audit_results.get("total_issues", 0)} total style issues
- **Optimizations:** {results.optimization_results.get("optimizations_applied", 0)} files optimized
- **Synchronization:** {results.sync_results.get("sync_result", {}).get("changes_committed", 0)} changes committed

### Quality Scores
- **Completeness:** {results.audit_results.get("completeness_score", 0):.2%}
- **Link Health:** {results.validation_results.get("valid_links", 0) / max(1, results.validation_results.get("total_links", 1)):.2%}
- **Style Quality:** {(1 - results.audit_results.get("total_issues", 0) / max(1, results.audit_results.get("total_files", 1) * 10)):.2%}

## 🔍 Detailed Results

"""

        # Audit Results
        if results.audit_results:
            report += """### Content Quality Audit

"""
            report += (
                f"- **Files Analyzed:** {results.audit_results.get('total_files', 0)}\n"
            )
            report += f"- **Completeness Score:** {results.audit_results.get('completeness_score', 0):.2%}\n"
            report += (
                f"- **Issues Found:** {results.audit_results.get('issues_found', 0)}\n"
            )
            report += (
                f"- **Broken Links:** {results.audit_results.get('broken_links', 0)}\n"
            )
            report += f"- **Missing Images:** {results.audit_results.get('missing_images', 0)}\n"
            report += f"- **Outdated Files:** {results.audit_results.get('outdated_files', 0)}\n"
            report += (
                f"- **Style Issues:** {results.audit_results.get('style_issues', 0)}\n"
            )

        # Validation Results
        if results.validation_results:
            report += """
### Link and Reference Validation

"""
            report += f"- **Total Links:** {results.validation_results.get('total_links', 0)}\n"
            report += f"- **Valid Links:** {results.validation_results.get('valid_links', 0)}\n"
            report += f"- **Broken Links:** {results.validation_results.get('broken_links', 0)}\n"
            report += f"- **Redirected Links:** {results.validation_results.get('redirected_links', 0)}\n"
            report += f"- **Timeout Links:** {results.validation_results.get('timeout_links', 0)}\n"
            report += f"- **Internal Issues:** {results.validation_results.get('internal_issues', 0)}\n"

        # Optimization Results
        if results.optimization_results:
            report += """
### Content Optimization

"""
            report += f"- **Files Processed:** {results.optimization_results.get('files_processed', 0)}\n"
            report += f"- **Optimizations Applied:** {results.optimization_results.get('optimizations_applied', 0)}\n"

        # Sync Results
        if results.sync_results:
            report += """
### Version Control Synchronization

"""
            sync_result = results.sync_results.get("sync_result", {})
            report += (
                f"- **Changes Committed:** {sync_result.get('changes_committed', 0)}\n"
            )
            if "commit_hash" in sync_result:
                report += f"- **Commit Hash:** {sync_result['commit_hash']}\n"
            if sync_result.get("errors"):
                report += f"- **Errors:** {len(sync_result['errors'])}\n"

        # Errors and Warnings
        if results.errors:
            report += """
### Errors Encountered

"""
            for error in results.errors:
                report += f"- ❌ {error}\n"

        if results.warnings:
            report += """
### Warnings

"""
            for warning in results.warnings:
                report += f"- ⚠️ {warning}\n"

        # Recommendations
        report += """
## 💡 Recommendations

"""

        # Generate recommendations based on results
        issues_found = results.audit_results.get("issues_found", 0)
        broken_links = results.validation_results.get("broken_links", 0)
        style_issues = results.audit_results.get("total_issues", 0)

        if issues_found > 0:
            report += f"- **Address {issues_found} content quality issues**\n"
        if broken_links > 0:
            report += f"- **Fix {broken_links} broken links**\n"
        if style_issues > 0:
            report += f"- **Resolve {style_issues} style consistency issues**\n"

        report += "- **Schedule regular maintenance** to prevent quality degradation\n"
        report += "- **Review and update configuration** based on team preferences\n"
        report += "- **Set up automated CI/CD integration** for continuous quality monitoring\n"

        # Next Steps
        report += """
## 🎯 Next Steps

1. **Immediate Actions (This Week):**
   - Review critical issues requiring immediate attention
   - Fix broken links and missing images
   - Address accessibility and style issues

2. **Short-term Goals (Next Month):**
   - Implement automated maintenance scheduling
   - Set up monitoring and alerting systems
   - Improve documentation contribution guidelines

3. **Long-term Vision (Next Quarter):**
   - Achieve 95%+ documentation quality score
   - Implement AI-assisted content improvement
   - Establish comprehensive documentation governance

---
*Report generated by FLEXT Documentation Maintenance Orchestrator*
"""

        return report


def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="FLEXT Documentation Maintenance Orchestrator"
    )
    parser.add_argument(
        "command",
        choices=[
            "audit",
            "validate",
            "style",
            "optimize",
            "sync",
            "comprehensive",
            "status",
        ],
        help="Maintenance command to run",
    )
    parser.add_argument("--config", help="Configuration file")
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--no-sync", action="store_true", help="Skip synchronization (for safety)"
    )

    args = parser.parse_args()

    # Initialize orchestrator
    orchestrator = DocumentationMaintenanceOrchestrator(args.config)

    # Override config with command line args
    if args.no_sync:
        orchestrator.config["sync_enabled"] = False

    try:
        if args.command == "status":
            print("📊 Documentation Maintenance Status")
            print("=" * 50)

            # Quick status check
            doc_count = len(list(Path().rglob("*.md")))
            print(f"📁 Total documentation files: {doc_count}")

            # Git status
            try:
                result = subprocess.run(
                    ["git", "status", "--porcelain", "docs/"],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                changes = len([
                    line for line in result.stdout.split("\n") if line.strip()
                ])
                print(f"🔄 Uncommitted changes: {changes}")
            except:
                print("🔄 Git status: Unable to check")

            print("\n💡 Use 'comprehensive' command for full maintenance cycle")

        elif args.command == "audit":
            results = orchestrator.run_comprehensive_audit(verbose=args.verbose)
            print("\n📊 Audit Summary:")
            print(f"   Files: {results.get('total_files', 0)}")
            print(f"   Completeness: {results.get('completeness_score', 0):.2%}")
            print(f"   Issues: {results.get('issues_found', 0)}")

        elif args.command == "validate":
            results = orchestrator.run_link_validation(verbose=args.verbose)
            print("\n🔗 Validation Summary:")
            print(f"   Links: {results.get('total_links', 0)}")
            print(f"   Broken: {results.get('broken_links', 0)}")
            print(f"   Valid: {results.get('valid_links', 0)}")

        elif args.command == "style":
            results = orchestrator.run_style_checking(verbose=args.verbose)
            print("\n🎨 Style Check Summary:")
            print(f"   Files: {results.get('total_files', 0)}")
            print(f"   Issues: {results.get('total_issues', 0)}")
            print(f"   Critical: {results.get('critical_issues', 0)}")

        elif args.command == "optimize":
            results = orchestrator.run_optimization(
                dry_run=args.dry_run, verbose=args.verbose
            )
            print("\n🔧 Optimization Summary:")
            print(f"   Processed: {results.get('files_processed', 0)}")
            print(f"   Optimized: {results.get('optimizations_applied', 0)}")

        elif args.command == "sync":
            results = orchestrator.run_synchronization(
                dry_run=args.dry_run, verbose=args.verbose
            )
            print("\n🔄 Sync Summary:")
            sync_result = results.get("sync_result", {})
            if "commit_hash" in sync_result:
                print(f"   Commit: {sync_result['commit_hash']}")
                print(f"   Changes: {sync_result.get('changes_committed', 0)}")
            else:
                print(f"   Status: {sync_result.get('message', 'No changes')}")

        elif args.command == "comprehensive":
            results = orchestrator.run_full_maintenance_cycle(
                dry_run=args.dry_run, verbose=args.verbose
            )

            print("\n🎉 Comprehensive Maintenance Complete!")
            print("=" * 50)
            print("📊 Summary:")
            print(
                f"   Audit: {results.audit_results.get('issues_found', 0)} issues found"
            )
            print(
                f"   Links: {results.validation_results.get('broken_links', 0)} broken"
            )
            print(f"   Style: {results.audit_results.get('total_issues', 0)} issues")
            print(
                f"   Optimized: {results.optimization_results.get('optimizations_applied', 0)} files"
            )

            if results.reports_generated:
                print("\n📄 Reports Generated:")
                for report in results.reports_generated:
                    print(f"   - {report}")

    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
