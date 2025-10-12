#!/usr/bin/env python3
"""FLEXT Documentation Synchronization System.

Automated git integration, change tracking, and synchronization for documentation maintenance.
"""

import json
import subprocess
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

from flext_core import FlextCore


@dataclass
class GitChange:
    """Represents a git change."""

    file_path: Path
    change_type: str  # "modified", "added", "deleted", "renamed"
    old_path: Path | None = None
    lines_added: int = 0
    lines_removed: int = 0


@dataclass
class SyncResult:
    """Results of synchronization operations."""

    timestamp: datetime
    changes_committed: list[GitChange] = field(default_factory=list)
    files_processed: int = 0
    errors: FlextCore.Types.StringList = field(default_factory=list)
    commit_hash: str | None = None
    branch: str | None = None


class DocumentationSyncSystem:
    """Automated documentation synchronization with git integration."""

    def __init__(self, config: dict | None = None) -> None:
        self.config = config or {}
        self.auto_commit = self.config.get("auto_commit", False)
        self.commit_message_template = self.config.get(
            "commit_message_template", "docs: automated maintenance - {changes}"
        )
        self.backup_before_changes = self.config.get("backup_before_changes", True)

    def get_git_status(self) -> dict[str, list[Path]]:
        """Get current git status for documentation files."""
        try:
            # Get status of docs directory
            result = subprocess.run(
                ["git", "status", "--porcelain", "docs/"],
                capture_output=True,
                text=True,
                check=True,
            )

            status = {"modified": [], "added": [], "deleted": [], "untracked": []}

            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    status_code = line[:2]
                    file_path = Path(line[3:].strip())

                    if status_code in {"M ", "MM"}:
                        status["modified"].append(file_path)
                    elif status_code in {"A ", "AM"}:
                        status["added"].append(file_path)
                    elif status_code == " D":
                        status["deleted"].append(file_path)
                    elif status_code == "??":
                        status["untracked"].append(file_path)

            return status

        except subprocess.CalledProcessError as e:
            print(f"Error getting git status: {e}")
            return {"modified": [], "added": [], "deleted": [], "untracked": []}

    def get_recent_changes(self, days: int = 7) -> list[GitChange]:
        """Get recent changes to documentation files."""
        try:
            since_date = (datetime.now(UTC) - timedelta(days=days)).strftime("%Y-%m-%d")

            result = subprocess.run(
                [
                    "git",
                    "log",
                    "--since",
                    since_date,
                    "--name-status",
                    "--pretty=format:",
                    "--",
                    "docs/",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            changes = []
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        change_type = parts[0]
                        file_path = Path(parts[1])

                        # Handle renames
                        old_path = None
                        if len(parts) >= 3 and change_type.startswith("R"):
                            old_path = Path(parts[2])

                        change = GitChange(
                            file_path=file_path,
                            change_type=self.normalize_change_type(change_type),
                            old_path=old_path,
                        )
                        changes.append(change)

            return changes

        except subprocess.CalledProcessError as e:
            print(f"Error getting recent changes: {e}")
            return []

    def normalize_change_type(self, git_status: str) -> str:
        """Normalize git change type to readable format."""
        mapping = {
            "A": "added",
            "M": "modified",
            "D": "deleted",
            "R": "renamed",
            "C": "copied",
            "U": "updated",
            "T": "type_changed",
        }
        return mapping.get(git_status, git_status.lower())

    def create_backup(self, files: list[Path]) -> Path | None:
        """Create backup of files before modification."""
        if not self.backup_before_changes or not files:
            return None

        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        backup_dir = Path(f"docs/backups/backup_{timestamp}")
        backup_dir.mkdir(parents=True, exist_ok=True)

        for file_path in files:
            if file_path.exists():
                backup_path = backup_dir / file_path.name
                try:
                    backup_path.write_text(
                        file_path.read_text(encoding="utf-8"), encoding="utf-8"
                    )
                except Exception as e:
                    print(f"Warning: Could not backup {file_path}: {e}")

        return backup_dir

    def commit_changes(
        self, message: str, files: list[Path] | None = None
    ) -> SyncResult:
        """Commit documentation changes to git."""
        result = SyncResult(timestamp=datetime.now(UTC))

        try:
            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                check=True,
            )
            result.branch = branch_result.stdout.strip()

            # Add files
            if files:
                for file_path in files:
                    subprocess.run(["git", "add", str(file_path)], check=True)
            else:
                subprocess.run(["git", "add", "docs/"], check=True)

            # Check if there are changes to commit
            status_result = subprocess.run(
                ["git", "status", "--porcelain", "docs/"],
                capture_output=True,
                text=True,
                check=True,
            )

            if not status_result.stdout.strip():
                result.errors.append("No changes to commit")
                return result

            # Create backup if enabled
            if self.backup_before_changes:
                backup_dir = self.create_backup(files or [])
                if backup_dir:
                    result.errors.append(f"Backup created at: {backup_dir}")

            # Commit changes
            subprocess.run(["git", "commit", "-m", message], check=True)

            # Get commit hash
            hash_result = subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
            )
            result.commit_hash = hash_result.stdout.strip()

            # Get details of committed changes
            show_result = subprocess.run(
                ["git", "show", "--name-status", result.commit_hash],
                capture_output=True,
                text=True,
                check=True,
            )

            for line in show_result.stdout.strip().split("\n"):
                if line.strip() and not line.startswith("commit "):
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        change = GitChange(
                            file_path=Path(parts[1]),
                            change_type=self.normalize_change_type(parts[0]),
                        )
                        result.changes_committed.append(change)

            result.files_processed = len(result.changes_committed)

        except subprocess.CalledProcessError as e:
            result.errors.append(f"Git operation failed: {e}")
        except Exception as e:
            result.errors.append(f"Unexpected error: {e}")

        return result

    def generate_sync_report(
        self, result: SyncResult, audit_results: dict | None = None
    ) -> str:
        """Generate comprehensive synchronization report."""
        report = f"""# FLEXT Documentation Sync Report

**Generated:** {result.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
**Branch:** {result.branch or "unknown"}
**Commit:** {result.commit_hash or "none"}

## 📊 Sync Summary

| Metric | Value | Status |
|--------|-------|---------|
| Files Processed | {result.files_processed} | ✅ |
| Changes Committed | {len(result.changes_committed)} | {"✅" if result.changes_committed else "⚠️"} |
| Errors | {len(result.errors)} | {"❌" if result.errors else "✅"} |

"""

        if result.changes_committed:
            report += """## 🔄 Committed Changes

| File | Change Type |
|------|-------------|
"""

            for change in result.changes_committed:
                report += f"| {change.file_path} | {change.change_type} |\n"

            report += "\n"

        if result.errors:
            report += """## ⚠️ Errors Encountered

"""
            for error in result.errors:
                report += f"- {error}\n"

            report += "\n"

        if audit_results:
            report += """## 🔍 Audit Summary

"""
            report += f"- **Total Files:** {audit_results.get('total_files', 0)}\n"
            report += f"- **Completeness Score:** {audit_results.get('completeness_score', 0):.2%}\n"
            report += f"- **Issues Found:** {audit_results.get('issues_found', 0)}\n"

        # Recommendations
        report += """
## 💡 Recommendations

"""

        if result.changes_committed:
            report += f"- ✅ Successfully committed {len(result.changes_committed)} documentation changes\n"

        if result.errors:
            report += "- ⚠️ Review errors and consider manual intervention\n"

        if audit_results and audit_results.get("issues_found", 0) > 0:
            report += f"- 🔧 Address {audit_results['issues_found']} outstanding documentation issues\n"

        report += "- 📈 Schedule regular maintenance to keep documentation healthy\n"

        return report

    def run_maintenance_workflow(
        self, audit_results: dict | None = None, dry_run: bool = False
    ) -> dict[str, any]:
        """Run complete maintenance workflow."""
        print("🔄 Starting documentation maintenance workflow...")

        results = {
            "timestamp": datetime.now(UTC).isoformat(),
            "git_status": {},
            "sync_result": {},
            "audit_summary": audit_results or {},
            "report": "",
        }

        # Get git status
        print("📋 Checking git status...")
        results["git_status"] = self.get_git_status()

        # Check for changes
        total_changes = sum(len(files) for files in results["git_status"].values())
        if total_changes == 0:
            print("✅ No documentation changes to sync")
            results["sync_result"] = {"message": "No changes to sync"}
        else:
            print(f"📝 Found {total_changes} documentation changes")

            if not dry_run and self.auto_commit:
                # Generate commit message
                change_summary = []
                for change_type, files in results["git_status"].items():
                    if files:
                        change_summary.append(f"{len(files)} {change_type}")

                commit_message = self.commit_message_template.format(
                    changes=", ".join(change_summary)
                )

                # Commit changes
                print("💾 Committing changes...")
                sync_result = self.commit_changes(commit_message)
                results["sync_result"] = {
                    "timestamp": sync_result.timestamp.isoformat(),
                    "changes_committed": len(sync_result.changes_committed),
                    "commit_hash": sync_result.commit_hash,
                    "branch": sync_result.branch,
                    "errors": sync_result.errors,
                }
            else:
                results["sync_result"] = {
                    "message": f"Would commit {total_changes} changes (dry run)",
                    "dry_run": True,
                }

        # Generate report
        if not dry_run and results.get("sync_result", {}).get("commit_hash"):
            # Create SyncResult object for reporting
            sync_result = SyncResult(
                timestamp=datetime.fromisoformat(results["sync_result"]["timestamp"]),
                commit_hash=results["sync_result"]["commit_hash"],
                branch=results["sync_result"]["branch"],
            )
            results["report"] = self.generate_sync_report(sync_result, audit_results)
        else:
            results["report"] = "Maintenance workflow completed (dry run)"

        print("✅ Maintenance workflow complete!")
        return results


def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="FLEXT Documentation Sync System")
    parser.add_argument(
        "action",
        choices=["status", "commit", "workflow", "report"],
        help="Sync action to perform",
    )
    parser.add_argument("--message", "-m", help="Custom commit message")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done"
    )
    parser.add_argument("--audit-data", help="JSON file with audit results")
    parser.add_argument("--output", "-o", help="Output report file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Load audit data if provided
    audit_results = None
    if args.audit_data and Path(args.audit_data).exists():
        with Path(args.audit_data).open(encoding="utf-8") as f:
            audit_results = json.load(f)

    # Initialize system
    config = {"auto_commit": not args.dry_run, "backup_before_changes": True}

    sync_system = DocumentationSyncSystem(config)

    try:
        if args.action == "status":
            status = sync_system.get_git_status()
            print("📋 Documentation Git Status:")
            for change_type, files in status.items():
                if files:
                    print(f"  {change_type.title()}: {len(files)} files")
                    if args.verbose:
                        for file_path in files[:5]:  # Show first 5
                            print(f"    - {file_path}")
                        if len(files) > 5:
                            print(f"    ... and {len(files) - 5} more")

        elif args.action == "commit":
            message = args.message or "docs: automated maintenance updates"
            result = sync_system.commit_changes(message)

            print("💾 Commit Results:")
            print(f"  Branch: {result.branch}")
            print(f"  Commit: {result.commit_hash}")
            print(f"  Changes: {len(result.changes_committed)}")

            if result.errors:
                print("  Errors:")
                for error in result.errors:
                    print(f"    - {error}")

        elif args.action == "workflow":
            results = sync_system.run_maintenance_workflow(audit_results, args.dry_run)

            print("🔄 Workflow Results:")
            print(f"  Status: {results['sync_result'].get('message', 'Completed')}")

            if "commit_hash" in results.get("sync_result", {}):
                print(f"  Commit: {results['sync_result']['commit_hash']}")

        elif args.action == "report":
            # Generate a status report
            status = sync_system.get_git_status()
            recent_changes = sync_system.get_recent_changes()

            report = f"""# Documentation Status Report

**Generated:** {datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")}

## Current Status

"""

            for change_type, files in status.items():
                if files:
                    report += f"### {change_type.title()} Files ({len(files)})\n\n"
                    for file_path in files[:10]:  # Limit output
                        report += f"- {file_path}\n"
                    if len(files) > 10:
                        report += f"- ... and {len(files) - 10} more\n"
                    report += "\n"

            report += "## Recent Changes (Last 7 Days)\n\n"
            report += f"**Total Changes:** {len(recent_changes)}\n\n"

            if recent_changes:
                for change in recent_changes[:20]:  # Show recent changes
                    report += f"- {change.change_type}: {change.file_path}\n"
                if len(recent_changes) > 20:
                    report += f"- ... and {len(recent_changes) - 20} more changes\n"

            if args.output:
                Path(args.output).write_text(report, encoding="utf-8")
                print(f"📄 Report saved to: {args.output}")
            else:
                print(report)

    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        return
    except Exception as e:
        print(f"❌ Error: {e}")
        return


if __name__ == "__main__":
    main()
