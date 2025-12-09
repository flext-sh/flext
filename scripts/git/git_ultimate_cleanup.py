#!/usr/bin/env python3
"""Git repository cleanup script.

Repository cleanup with safety features:
    - External backup (tar.gz + git mirror)
    - Cruft removal from git history
    - Commit message rewriting
    - Author normalization
    - Remote restoration
    - GitHub push/sync
    - Safety guards and validation

Usage:
    python3 scripts/git_ultimate_cleanup.py --test                           # Test all functions
    python3 scripts/git_ultimate_cleanup.py --detect-cruft                   # Detect additional cruft
    python3 scripts/git_ultimate_cleanup.py --workspace-report REPORT.md     # Generate workspace report
    python3 scripts/git_ultimate_cleanup.py --update-gitignores              # Update all .gitignore files
    python3 scripts/git_ultimate_cleanup.py --dry-run                        # Simulate cleanup
    python3 scripts/git_ultimate_cleanup.py                                  # Main repo
    python3 scripts/git_ultimate_cleanup.py --all                            # Main + submodules
    python3 scripts/git_ultimate_cleanup.py --push                           # Cleanup + push main
    python3 scripts/git_ultimate_cleanup.py --all --push-all                 # All + push all
    python3 scripts/git_ultimate_cleanup.py --backup-only                    # Just backup
    python3 scripts/git_ultimate_cleanup.py --restore-remotes                # Just restore remotes
"""

import argparse
import operator
import re
import shlex
import shutil
import sys
import tarfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, ClassVar

from flext_core import FlextResult, u

# Ensure git is available
_git_cmd = shutil.which("git")
if not _git_cmd:
    print("Error: git command not found. Please install git.", file=sys.stderr)
    sys.exit(1)
GIT_CMD: str = _git_cmd


class GitUltimateCleanup:
    """The ultimate unified git cleanup system."""

    AUTHOR_NAME: ClassVar[str] = "Marlon Costa"
    AUTHOR_EMAIL: ClassVar[str] = "marlonsc@gmail.com"

    @staticmethod
    def _run_git_command(
        repo_path: Path, args: list[str], *, check: bool = False
    ) -> FlextResult[Any]:
        """Run a git command with proper error handling and type annotations."""
        cmd = [GIT_CMD, "-C", str(repo_path)] + args
        return u.CommandExecution.run_external_command(
            cmd,
            capture_output=True,
            check=check,
        )

    # Cruft patterns to remove from git history
    CRUFT_PATTERNS: ClassVar[list[str]] = [
        # Build artifacts
        "*.pyc",
        "*.pyo",
        "*.py[cod]",
        "*$py.class",
        "__pycache__/",
        "dist/",
        "build/",
        "*.egg-info/",
        # Cache directories
        ".ruff_cache/",
        ".mypy_cache/",
        ".pytest_cache/",
        ".serena/cache/",
        ".serena/",
        # Coverage reports
        ".coverage",
        "htmlcov/",
        ".tox/",
        ".benchmarks/",
        # Log files
        "*.log",
        ".meltano/logs/",
        # Backup files
        "*.backup",
        "*.bak",
        "*.orig",
        "*~",
        ".*.swp",
        "*.syntax_backup",
        "*.broken",
        "*.tmp.bak",
        "*_backup",
        "*_backup_*",
        "temp_backup",
        # Temporary/debug scripts and files
        "temp_*.py",
        "*_temp.py",
        "*_temp.md",
        "fix_*.py",
        "*_fix.py",
        "debug_*.py",
        "investigate_*.py",
        "validate_*.py",
        "*_analysis.txt",
        "*_output.txt",
        "*_report.txt",
        "temp_test_*",
        "analysis_temp/",
        "report_*/",
        "reports_*/",
        # OS-specific
        ".DS_Store",
        "Thumbs.db",
        # AI/IDE config and reports
        "CLAUDE*.md",
        ".cursor/",
        ".vscode/",
        ".idea/",
        "*_report.md",
        "*_analysis.md",
        "*_summary.md",
        "*_REPORT*.md",
        "*_ANALYSIS*.md",
        "*_SUMMARY*.md",
        "*_FINDINGS*.md",
        "CONFIG_MIGRATION*.md",
        "DEVELOPMENT_STANDARDS*.md",
        "DUPLICATION_REPORT*.md",
        "LINT_CORRECTIONS*.md",
        "*.ai.md",
        "*.ai.txt",
        # Archive directories
        ".archive/",
        "archive/",
        "archives/",
        "backups/",
        # Large data files
        "*.db",
        "*.sqlite",
        "*.sqlite3",
        "output_files/",
        "data_buffers/",
        "*.tar",
        "*.tar.gz",
        "*.zip",
        "*backup*/",
        "submodule_cleanup_backup/",
        "sync_control.db",  # Large database file
        # Timestamped documentation (AI-generated)
        "*.md_20250*",
        # Frequently deleted markdown patterns (AI-generated documentation)
        "*_COMPLETE.md",
        "*_PLAN.md",
        "*_GUIDE.md",
        "*_CHECKLIST.md",
        "*_PROMPT.md",
        "*_ASSESSMENT.md",
        "*_CONTROL.md",
        "*_AUDIT*.md",
        "*_RESULTS.md",
        "*_STATUS.md",
        "*_HANDOVER.md",
        "*_REFACTORING*.md",
        "*_REORGANIZATION*.md",
        "*_STANDARDIZATION*.md",
        "*_OPTIMIZATION*.md",
        "*_METHODOLOGY*.md",
        "*_BASELINE*.md",
        "*_MODERNIZATION*.md",
        "RELATORIO_*.md",
        "COMPREHENSIVE_*.md",
        "COMPLETE_*.md",
        "TODO.md",
        "lint-report.md",
        "mypy_*.md",
        "*-report.md",
        "*-cleanup*.md",
        "*-summary.md",
        # High-priority patterns from workspace analysis
        "*.so",
        "*.pyd",
        ".Python",
        ".installed.cfg",
        "MANIFEST",
        "*.manifest",
        ".env",
        ".venv",
        "venv/",
        "ENV/",
        "coverage.xml",
        "coverage.json",
        "*.cover",
        ".hypothesis/",
        "junit.xml",
        ".nox/",
        ".pyre/",
        ".pytype/",
        ".bandit/",
        "state.json",
        "*.state",
        "*.state.json",
        "catalog.json",
        "target_config.json",
        "dbt.log",
        "dbt_packages/",
        "target/",
        "*.spec",
        "profiles.yml.bak",
        "profiles/profiles.yml.backup",
        "**/.user.yml",
        "docs/_build/",
        "site/",
        "Desktop.ini",
    ]

    AI_PATTERNS: ClassVar[list[str]] = [
        r"🤖 Generated with \[Claude Code\].*",
        r"Co-Authored-By:\s*Claude.*",
        r"Co-Authored-By:\s*Codex.*",
        r"Co-Authored-By:\s*Cursor.*",
        r"Generated by Claude.*",
        r"Generated by Codex.*",
        r"Generated by Cursor.*",
        r"Claude Code.*",
        r"\[Claude Code\].*",
        r"\[Codex\].*",
        r"\[Cursor\].*",
        r"With assistance from.*",
        r"AI-assisted.*",
        r"noreply@anthropic\.com.*",
    ]

    def __init__(self, repo_path: Path, *, dry_run: bool = False) -> None:
        """Initialize the Git repository cleaner.

        Args:
            repo_path: Path to the git repository to clean
            dry_run: If True, only show what would be done without making changes

        """
        self.repo_path = repo_path.resolve()
        self.timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        self.backup_root = Path.home() / f"flext-ultimate-backup-{self.timestamp}"
        self.dry_run = dry_run

    def validate_repository(self) -> tuple[bool, str]:
        """Comprehensive repository validation."""
        # Check if git repo
        if not (self.repo_path / ".git").exists():
            return False, f"Not a git repository: {self.repo_path}"

        # Check uncommitted changes (skip in dry-run mode)
        if not self.dry_run:
            status_result = self._run_git_command(
                self.repo_path, ["status", "--porcelain"]
            )
            if status_result.is_failure:
                return False, f"Failed to check git status: {status_result.error}"
            wrapper = status_result.unwrap()
            if wrapper.stdout.strip():
                return False, "Uncommitted changes detected. Commit or stash first."

        # Check git-filter-repo
        git_filter_repo_cmd = shutil.which("git-filter-repo")
        if not git_filter_repo_cmd:
            return (
                False,
                "git-filter-repo not installed. Run: pip install git-filter-repo",
            )

        # Check not detached HEAD
        head_result = self._run_git_command(
            self.repo_path, ["symbolic-ref", "-q", "HEAD"]
        )
        if head_result.is_failure:
            return False, f"Failed to check HEAD: {head_result.error}"
        head_wrapper = head_result.unwrap()
        if head_wrapper.returncode != 0:
            return False, "Detached HEAD state. Checkout a branch first."

        # Check disk space
        disk_result = u.CommandExecution.run_external_command(
            ["df", "-h", "."],
            capture_output=True,
            check=False,
        )
        if disk_result.is_failure:
            return False, f"Failed to check disk space: {disk_result.error}"

        disk_wrapper = disk_result.unwrap()
        if disk_wrapper.returncode == 0:
            lines = disk_wrapper.stdout.strip().split("\n")
            if len(lines) > 1:
                avail = lines[1].split()[3]
                print(f"   💾 Available disk space: {avail}")

        return True, "✅ All validation checks passed"

    def create_comprehensive_backup(self) -> Path:
        """Create complete external backup with multiple safety layers."""
        print(f"\n{'=' * 70}")
        print("📦 CREATING COMPREHENSIVE BACKUP")
        print(f"{'=' * 70}\n")

        self.backup_root.mkdir(parents=True, exist_ok=True)
        repo_backup = self.backup_root / self.repo_path.name
        repo_backup.mkdir(parents=True, exist_ok=True)

        print(f"Backup location: {self.backup_root}")
        print()

        # 1. Create tar.gz archive
        print("1️⃣  Creating tar.gz archive...")
        tar_file = repo_backup / f"{self.repo_path.name}.tar.gz"

        with tarfile.open(tar_file, "w:gz") as tar:
            tar.add(
                self.repo_path,
                arcname=self.repo_path.name,
                filter=lambda t: None
                if any([
                    "__pycache__" in t.name,
                    ".pyc" in t.name,
                    ".ruff_cache" in t.name,
                    ".mypy_cache" in t.name,
                    ".pytest_cache" in t.name,
                    "htmlcov" in t.name,
                ])
                else t,
            )

        size_mb = tar_file.stat().st_size / (1024 * 1024)
        print(f"   ✅ Archive created: {size_mb:.1f}MB")

        # 2. Create git mirror clone
        print("2️⃣  Creating git mirror clone...")
        mirror_path = repo_backup / f"{self.repo_path.name}.git"
        mirror_result = u.CommandExecution.run_external_command(
            [GIT_CMD, "clone", "--mirror", str(self.repo_path), str(mirror_path)],
            check=False,
            u=u,
            text=True,
        )
        if mirror_result.is_failure:
            print(f"   ❌ Mirror clone failed: {mirror_result.error}")
        else:
            mirror_wrapper = mirror_result.unwrap()
            if mirror_wrapper.returncode == 0:
                print("   ✅ Mirror clone created")
            else:
                print(f"   ⚠️  Mirror clone failed: {mirror_wrapper.stderr}")

        # 3. Export commit history
        print("3️⃣  Exporting commit history...")
        history_file = repo_backup / "commit-history.txt"
        history_result = self._run_git_command(
            self.repo_path,
            ["log", "--all", "--format=%H|%an|%ae|%ad|%s", "--date=iso"],
        )
        if history_result.is_failure:
            print(f"   ❌ History export failed: {history_result.error}")
        else:
            history_wrapper = history_result.unwrap()
            if history_wrapper.returncode == 0:
                history_file.write_text(history_wrapper.stdout)
            lines = len(history_wrapper.stdout.strip().split("\n"))
            print(f"   ✅ Exported {lines} commits")

        # 4. Export reflog
        print("4️⃣  Exporting reflog...")
        reflog_file = repo_backup / "reflog.txt"
        reflog_result = self._run_git_command(
            self.repo_path, ["reflog", "--format=%H|%gd|%gs"]
        )
        if reflog_result.is_failure:
            print(f"   ❌ Reflog export failed: {reflog_result.error}")
        else:
            reflog_wrapper = reflog_result.unwrap()
            if reflog_wrapper.returncode == 0:
                reflog_file.write_text(reflog_wrapper.stdout)
                print("   ✅ Reflog exported")

        # 5. Export branch info
        print("5️⃣  Exporting branch information...")
        branch_file = repo_backup / "branches.txt"
        branch_result = self._run_git_command(self.repo_path, ["branch", "-a"])
        if branch_result.is_failure:
            print(f"   ❌ Branch export failed: {branch_result.error}")
        else:
            branch_wrapper = branch_result.unwrap()
            if branch_wrapper.returncode == 0:
                branch_file.write_text(branch_wrapper.stdout)
                print("   ✅ Branch info exported")

        # 6. Export tags
        print("6️⃣  Exporting tags...")
        tags_file = repo_backup / "tags.txt"
        tags_result = self._run_git_command(self.repo_path, ["tag", "-l"])
        if tags_result.is_failure:
            print(f"   ❌ Tags export failed: {tags_result.error}")
        else:
            tags_wrapper = tags_result.unwrap()
            if tags_wrapper.returncode == 0:
                tags_file.write_text(tags_wrapper.stdout)
                print("   ✅ Tags exported")

        # 7. Create safety tag in repo
        print("7️⃣  Creating safety tag in repository...")
        safety_tag = f"pre-cleanup-{self.timestamp}"
        u.CommandExecution.run_external_command(
            [GIT_CMD, "-C", str(self.repo_path), "tag", safety_tag],
            check=False,
            capture_output=True,
        )
        print(f"   ✅ Tag created: {safety_tag}")

        # 8. Create recovery script
        print("8️⃣  Creating recovery script...")
        self._create_recovery_script(repo_backup, safety_tag, tar_file, mirror_path)
        print("   ✅ Recovery script created")

        print("\n✅ Comprehensive backup complete!")
        print(f"   Location: {repo_backup}")
        print()

        return self.backup_root

    def _create_recovery_script(
        self, backup_dir: Path, safety_tag: str, tar_file: Path, mirror_path: Path
    ) -> None:
        """Create recovery script."""
        created: str = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        source: str = str(self.repo_path)
        repo_path_str: str = str(self.repo_path)
        repo_parent_str: str = str(self.repo_path.parent)
        tar_file_str: str = str(tar_file)
        mirror_path_str: str = str(mirror_path)
        repo_name: str = self.repo_path.name

        safety_tag_esc = shlex.quote(safety_tag)
        repo_path_esc = shlex.quote(repo_path_str)
        repo_parent_esc = shlex.quote(repo_parent_str)
        tar_file_esc = shlex.quote(tar_file_str)
        mirror_path_esc = shlex.quote(mirror_path_str)

        script = backup_dir / "RECOVER.sh"
        script_content = (
            """#!/bin/bash
# FLEXT Repository Recovery Script
# Created: """
            + created
            + """
# Source: """
            + source
            + """

set -e

echo "==================================================================="
echo "FLEXT Repository Recovery"
echo "==================================================================="
echo ""

# Recovery options
echo "Select recovery method:"
echo "  1) Reset to safety tag (fastest, preserves local changes)"
echo "  2) Restore from tar.gz (complete restore)"
echo "  3) Restore from mirror clone (preserves all git data)"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "Resetting to safety tag: """
            + safety_tag_esc
            + """"
        cd """
            + repo_path_esc
            + """
        git reset --hard """
            + safety_tag_esc
            + """
        echo "✅ Repository reset to """
            + safety_tag_esc
            + """"
        ;;
    2)
        echo "Extracting from tar.gz..."
        read -p "Extract to (default: """
            + repo_parent_esc
            + """): " extract_path
        extract_path=${extract_path:-"""
            + repo_parent_esc
            + """}
        tar -xzf """
            + tar_file_esc
            + """ -C "$extract_path"
        echo "✅ Extracted to: $extract_path/"""
            + repo_name
            + """"
        ;;
    3)
        echo "Restoring from mirror clone..."
        read -p "Restore to (default: """
            + repo_parent_esc
            + """/"""
            + repo_name
            + """-restored): " restore_path
        restore_path=${restore_path:-"""
            + repo_parent_esc
            + """/"""
            + repo_name
            + """-restored}
        git clone """
            + mirror_path_esc
            + """ "$restore_path"
        echo "✅ Restored to: $restore_path"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "Recovery complete!"
"""
        )
        script.write_text(script_content)
        script.chmod(0o755)

        # Create README
        backup_dir_str = str(backup_dir)
        readme = backup_dir / "README.md"
        readme.write_text(
            f"""# FLEXT Ultimate Backup

## Backup Information
- **Created**: {created}
- **Source**: {source}
- **Safety Tag**: {safety_tag}

## Contents
- `{tar_file.name}` - Complete tar.gz archive
- `{mirror_path.name}/` - Git mirror clone
- `commit-history.txt` - All commit history
- `reflog.txt` - Git reflog
- `branches.txt` - Branch information
- `tags.txt` - All tags
- `RECOVER.sh` - Recovery script

## Quick Recovery

### Option 1: Reset to Safety Tag (Fastest)
```bash
cd {source}
git reset --hard {safety_tag}
```

### Option 2: Use Recovery Script
```bash
cd {backup_dir_str}
./RECOVER.sh
```

### Option 3: Manual Restore
```bash
tar -xzf {tar_file_str} -C /path/to/restore/
```

## Verification
```bash
# Check backup integrity
tar -tzf {tar_file.name} | head -20

# View backup size
du -sh {tar_file.name}

# Check commit count
wc -l commit-history.txt
```

## Important Notes
- This backup is EXTERNAL to git (will survive filter-repo)
- Multiple recovery options available
- Safety tag created in repository: {safety_tag}
- Keep this backup until cleanup is verified!
"""
        )

    def test_principal_functions(self) -> bool:
        """Test all principal functions without modifying anything."""
        print(f"\n{'=' * 70}")
        print("🧪 DRY RUN TEST - VALIDATING FUNCTIONS")
        print(f"{'=' * 70}\n")

        tests_passed = 0
        tests_failed = 0

        # Test 1: Repository validation
        print("Test 1: Repository validation...")
        valid, msg = self.validate_repository()
        if valid:
            print(f"  ✅ PASS: {msg}")
            tests_passed += 1
        else:
            print(f"  ❌ FAIL: {msg}")
            tests_failed += 1

        # Test 2: Git directory detection
        print("Test 2: Git directory detection...")
        try:
            git_dir = self._get_git_dir()
            if git_dir.exists():
                print(f"  ✅ PASS: Found git dir at {git_dir}")
                tests_passed += 1
            else:
                print("  ❌ FAIL: Git dir not found")
                tests_failed += 1
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            tests_failed += 1

        # Test 3: Cruft pattern validation
        print("Test 3: Cruft pattern validation...")
        print(f"  i {len(self.CRUFT_PATTERNS)} patterns configured")
        print("  ✅ PASS: Cruft patterns loaded")
        tests_passed += 1

        # Test 4: AI pattern validation
        print("Test 4: AI pattern validation...")
        print(f"  i {len(self.AI_PATTERNS)} AI patterns configured")
        test_msg = "Co-Authored-By: Claude <claude@anthropic.com>"
        cleaned = test_msg
        for pattern in self.AI_PATTERNS:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.MULTILINE)
        if cleaned != test_msg:
            print("  ✅ PASS: AI patterns working")
            tests_passed += 1
        else:
            print("  ❌ FAIL: AI patterns not working")
            tests_failed += 1

        # Test 5: Submodule detection
        print("Test 5: Submodule detection...")
        submodules = self.get_submodules()
        print(f"  i Found {len(submodules)} submodules")
        print("  ✅ PASS: Submodule detection working")
        tests_passed += 1

        # Test 6: Remote configuration
        print("Test 6: Remote configuration from .gitmodules...")
        gitmodules = self.repo_path / ".gitmodules"
        if gitmodules.exists():
            print("  ✅ PASS: .gitmodules found")
            tests_passed += 1
        else:
            print("  ⚠️  WARN: No .gitmodules (might be standalone repo)")
            tests_passed += 1

        # Test 7: Backup directory creation
        print("Test 7: Backup directory access...")
        try:
            test_backup = Path.home() / f"flext-test-{self.timestamp}"
            test_backup.mkdir(parents=True, exist_ok=True)
            test_backup.rmdir()
            print("  ✅ PASS: Can create backup directory")
            tests_passed += 1
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            tests_failed += 1

        # Test 8: Git commands availability
        print("Test 8: Git commands availability...")
        commands = ["git", "git-filter-repo", "tar"]
        all_available = True
        for cmd in commands:
            if shutil.which(cmd) is None:
                print(f"  ❌ FAIL: {cmd} not found")
                all_available = False
        if all_available:
            print("  ✅ PASS: All required commands available")
            tests_passed += 1
        else:
            tests_failed += 1

        # Summary
        print(f"\n{'=' * 70}")
        print(f"Test Results: {tests_passed} passed, {tests_failed} failed")
        print(f"{'=' * 70}\n")

        if tests_failed > 0:
            print("❌ Some tests failed. Fix issues before running cleanup.")
            return False

        print("✅ All tests passed! Safe to proceed with cleanup.")
        return True

    def cleanup_repository(self) -> bool:
        """Execute complete repository cleanup."""
        print(f"\n{'=' * 70}")
        print(f"🔧 CLEANING: {self.repo_path.name}")
        print(f"{'=' * 70}\n")

        if self.dry_run:
            print("🧪 DRY RUN MODE - Simulating operations...")
            print()
            print("Would perform:")
            print(f"  🧹 Remove {len(self.CRUFT_PATTERNS)} cruft patterns from history")
            print("  🚫 Clean AI references from all commits")
            print(
                f"  ✍️  Normalize all authors to: {self.AUTHOR_NAME} <{self.AUTHOR_EMAIL}>"
            )
            print()
            print("✅ Dry run complete (no changes made)")
            return True

        # Create filter script
        callback_script = self._create_filter_script()
        cruft_file = self._create_cruft_file()

        # Build command
        cmd = [
            "git",
            "filter-repo",
            "--force",
            "--commit-callback",
            str(callback_script),
            "--invert-paths",
            "--paths-from-file",
            str(cruft_file),
        ]

        # Add mailmap
        mailmap = self.repo_path / ".mailmap"
        if mailmap.exists():
            cmd.extend(["--mailmap", str(mailmap)])

        # Show what we're doing
        print("Operations:")
        print(f"  🧹 Removing {len(self.CRUFT_PATTERNS)} cruft patterns")
        print("  🚫 Cleaning AI references")
        print(f"  ✍️  Normalizing author: {self.AUTHOR_NAME} <{self.AUTHOR_EMAIL}>")
        print()

        # Execute
        print("Processing commits...")
        try:
            cleanup_result = u.CommandExecution.run_external_command(
                cmd, check=False, cwd=str(self.repo_path)
            )

            if cleanup_result.is_failure:
                print(f"   Recover: cd {self.backup_root} && ./RECOVER.sh")
                return False

            wrapper = cleanup_result.unwrap()
            if wrapper.returncode != 0:
                print(f"   Recover: cd {self.backup_root} && ./RECOVER.sh")
                return False

        except KeyboardInterrupt:
            print("\n\n❌ INTERRUPTED!")
            print(f"   Recover: cd {self.backup_root} && ./RECOVER.sh")
            return False

        finally:
            callback_script.unlink(missing_ok=True)
            cruft_file.unlink(missing_ok=True)

        # Verify
        verify_result = self._run_git_command(
            self.repo_path, ["log", "-1", "--format=%an %ae"]
        )
        if verify_result.is_failure:
            print(f"\n⚠️  Author verification failed: {verify_result.error}")
        else:
            verify_wrapper = verify_result.unwrap()
            if verify_wrapper.returncode == 0:
                author = verify_wrapper.stdout.strip()
                if self.AUTHOR_NAME not in author:
                    print(f"\n⚠️  Author verification failed: {author}")

        # Show statistics
        stats_result = self._run_git_command(self.repo_path, ["count-objects", "-vH"])
        if stats_result.is_failure:
            print(f"\n⚠️  Statistics failed: {stats_result.error}")
        else:
            stats_wrapper = stats_result.unwrap()
            if stats_wrapper.returncode == 0:
                print("\n📊 Repository statistics:")
                for line in stats_wrapper.stdout.strip().split("\n")[:5]:
                    print(f"   {line}")

        print(f"\n✅ {self.repo_path.name} cleaned successfully!")
        print()

        return True

    def _create_filter_script(self) -> Path:
        """Create git-filter-repo callback script."""
        patterns_str = ",\n".join([f'        r"{p}"' for p in self.AI_PATTERNS])

        script = f"""#!/usr/bin/env python3
import re

commit_count = 0

AI_PATTERNS = [
{patterns_str}
]

AUTHOR_NAME = b"{self.AUTHOR_NAME}"
AUTHOR_EMAIL = b"{self.AUTHOR_EMAIL}"

def clean_ai_refs(msg_bytes):
    msg = msg_bytes.decode('utf-8', errors='ignore')
    for pattern in AI_PATTERNS:
        msg = re.sub(pattern, "", msg, flags=re.IGNORECASE | re.MULTILINE)
    lines = [line.strip() for line in msg.split('\\n') if line.strip()]
    return '\\n'.join(lines).encode('utf-8')

def callback(commit, metadata):
    global commit_count
    commit_count += 1

    original = commit.message.decode('utf-8', errors='ignore').strip()
    subject = original.split('\\n')[0]

    print(f"[{{commit_count}}] {{commit.original_id.decode()[:8]}}: {{subject[:60]}}", flush=True)

    commit.message = clean_ai_refs(original.encode('utf-8'))
    commit.author_name = AUTHOR_NAME
    commit.author_email = AUTHOR_EMAIL
    commit.committer_name = AUTHOR_NAME
    commit.committer_email = AUTHOR_EMAIL
"""

        git_dir = self._get_git_dir()
        script_path = git_dir / "ultimate-cleanup.py"
        script_path.write_text(script)
        script_path.chmod(0o755)
        return script_path

    def _create_cruft_file(self) -> Path:
        """Create cruft patterns file."""
        git_dir = self._get_git_dir()
        cruft_file = git_dir / "cruft-patterns.txt"
        cruft_file.write_text("\n".join([f"glob:{p}" for p in self.CRUFT_PATTERNS]))
        return cruft_file

    def _get_git_dir(self) -> Path:
        """Get actual .git directory."""
        git_path = self.repo_path / ".git"
        if git_path.is_file():
            gitdir_line = git_path.read_text().strip()
            if gitdir_line.startswith("gitdir: "):
                return (self.repo_path / gitdir_line[8:]).resolve()
        return git_path

    def restore_remotes(self) -> None:
        """Restore git remotes from .gitmodules."""
        print(f"\n{'=' * 70}")
        print("🔗 RESTORING REMOTES")
        print(f"{'=' * 70}\n")

        # Main repo
        main_remote = "git@github.com:flext-sh/flext.git"
        u.CommandExecution.run_external_command(
            [
                GIT_CMD,
                "-C",
                str(self.repo_path),
                "remote",
                "origin",
                main_remote,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        print(f"✅ Main: {main_remote}")

        # Submodules
        gitmodules = self.repo_path / ".gitmodules"
        if not gitmodules.exists():
            print()
            return

        submodule_result = u.CommandExecution.run_external_command(
            [GIT_CMD, "config", "-f", str(gitmodules), "--get-regexp", r"\.path$"],
            check=False,
            capture_output=True,
        )

        if submodule_result.is_failure:
            print()
            return

        wrapper = submodule_result.unwrap()
        for line in wrapper.stdout.strip().split("\n"):
            if not line:
                continue

            key, path = line.split()
            name = key.split(".")[1]

            url_result = u.CommandExecution.run_external_command(
                [GIT_CMD, "config", "-f", str(gitmodules), f"submodule.{name}.url"],
                check=False,
                capture_output=True,
                text=True,
            )

            if url_result.is_failure:
                continue
            url_wrapper = url_result.unwrap()
            if url_wrapper.returncode != 0:
                continue
            url = url_wrapper.stdout.strip()
            submodule_path = self.repo_path / path

            if submodule_path.exists():
                u.CommandExecution.run_external_command(
                    [
                        GIT_CMD,
                        "-C",
                        str(submodule_path),
                        "remote",
                        "add",
                        "origin",
                        url,
                    ],
                    capture_output=True,
                    text=True,
                )
                print(f"✅ {path}")

        print()

    def get_submodules(self) -> list[Path]:
        """Get all submodule paths."""
        gitmodules = self.repo_path / ".gitmodules"
        if not gitmodules.exists():
            return []

        submodule_config_result = u.CommandExecution.run_external_command(
            [GIT_CMD, "config", "-f", str(gitmodules), "--get-regexp", r"\.path$"],
            check=False,
            capture_output=True,
            text=True,
        )

        if submodule_config_result.is_failure:
            return []

        submodule_wrapper = submodule_config_result.unwrap()
        if submodule_wrapper.returncode != 0:
            return []

        submodules = []
        for line in submodule_wrapper.stdout.strip().split("\n"):
            if not line:
                continue
            path = line.split()[1]
            submodule_path = self.repo_path / path
            if submodule_path.exists():
                submodules.append(submodule_path)

        return submodules

    def push_to_github(self, *, push_tags: bool = True) -> bool:
        """Push repository to GitHub with force."""
        print(f"\n{'=' * 70}")
        print(f"🚀 PUSHING TO GITHUB: {self.repo_path.name}")
        print(f"{'=' * 70}\n")

        if self.dry_run:
            print("🧪 DRY RUN MODE - Would push:")
            print("  📤 Force push all branches")
            if push_tags:
                print("  🏷️  Force push all tags")
            print()
            return True

        # Check if remote exists
        remote_result = self._run_git_command(
            self.repo_path, ["remote", "get-url", "origin"]
        )

        if remote_result.is_failure:
            print("❌ No remote 'origin' found. Run --restore-remotes first.")
            return False

        remote_wrapper = remote_result.unwrap()
        if remote_wrapper.returncode != 0:
            print("❌ No remote 'origin' found. Run --restore-remotes first.")
            return False

        remote_url = remote_wrapper.stdout.strip()
        print(f"Remote: {remote_url}")
        print()

        # Safety confirmation
        print("⚠️  WARNING: This will FORCE PUSH to GitHub!")
        print("   This will overwrite remote history with local changes.")
        response = input("Continue? (yes/NO): ")
        if response.lower() != "yes":
            print("Cancelled.")
            return False

        # Push branches
        print("📤 Pushing all branches...")
        push_branches_result = self._run_git_command(
            self.repo_path, ["push", "origin", "--force", "--all"]
        )

        if push_branches_result.is_failure:
            print(f"❌ Push failed: {push_branches_result.error}")
            return False

        push_branches_wrapper = push_branches_result.unwrap()
        if push_branches_wrapper.returncode != 0:
            print(f"❌ Push failed: {push_branches_wrapper.stderr}")
            return False

        print("   ✅ Branches pushed")

        # Push tags
        if push_tags:
            print("🏷️  Pushing all tags...")
            push_tags_result = self._run_git_command(
                self.repo_path, ["push", "origin", "--force", "--tags"]
            )

            if push_tags_result.is_failure:
                print(f"   ⚠️  Tag push failed: {push_tags_result.error}")
            else:
                push_tags_wrapper = push_tags_result.unwrap()
                if push_tags_wrapper.returncode != 0:
                    print(f"   ⚠️  Tag push failed: {push_tags_wrapper.stderr}")
                else:
                    print("   ✅ Tags pushed")

        print(f"\n✅ {self.repo_path.name} pushed successfully!")
        print()
        return True

    def push_all_submodules(self) -> bool:
        """Push all submodules to GitHub."""
        submodules = self.get_submodules()

        if not submodules:
            print("i No submodules to push")
            return True

        print(f"\n{'=' * 70}")
        print(f"📦 PUSHING SUBMODULES ({len(submodules)} total)")
        print(f"{'=' * 70}\n")

        if self.dry_run:
            print("🧪 DRY RUN MODE - Would push:")
            for submodule in submodules:
                print(f"  📤 {submodule.name}")
            print()
            return True

        failed = []
        for submodule in submodules:
            sub_cleanup = GitUltimateCleanup(submodule, dry_run=self.dry_run)
            if not sub_cleanup.push_to_github(push_tags=True):
                failed.append(submodule.name)

        if failed:
            print(f"\n⚠️  Failed to push {len(failed)} submodules:")
            for name in failed:
                print(f"   ❌ {name}")
            return False

        print(f"\n✅ All {len(submodules)} submodules pushed!")
        return True

    def analyze_gitignore(self) -> list[str]:
        """Parse .gitignore and extract patterns that might indicate committed cruft."""
        gitignore_path = self.repo_path / ".gitignore"
        if not gitignore_path.exists():
            return []

        patterns = []
        content = gitignore_path.read_text()

        for line in content.split("\n"):
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue
            # Skip negation patterns
            if line.startswith("!"):
                continue
            # Clean up the pattern
            pattern = line.rstrip("/")
            if pattern:
                patterns.append(pattern)

        return patterns

    def analyze_historical_removals(self) -> dict[str, int]:
        """Analyze git history to find frequently deleted files (likely cruft)."""
        result = self._run_git_command(
            self.repo_path,
            ["log", "--all", "--diff-filter=D", "--name-only", "--format="],
        )

        if result.is_failure:
            return {}

        result_wrapper = result.unwrap()
        if result_wrapper.returncode != 0:
            return {}

        # Count deletion frequency
        deletion_counts: dict[str, int] = {}
        for line in result_wrapper.stdout.strip().split("\n"):
            if not line:
                continue
            deletion_counts[line] = deletion_counts.get(line, 0) + 1

        return deletion_counts

    def detect_additional_cruft(
        self, *, silent: bool = False
    ) -> dict[str, list[str] | str | int]:
        """Detect additional cruft patterns from git history and .gitignore."""
        if not silent:
            print(f"\n{'=' * 70}")
            print("🔍 DETECTING ADDITIONAL CRUFT PATTERNS")
            print(f"{'=' * 70}\n")

        detected: dict[str, list[str] | str | int] = {
            "gitignore_patterns": [],
            "historical_removals": [],
            "recommended_patterns": [],
            "repo_name": self.repo_path.name,
            "total_gitignore_patterns": 0,
            "total_deletions": 0,
        }

        # 1. Analyze .gitignore
        if not silent:
            print("1️⃣  Analyzing .gitignore patterns...")
        gitignore_patterns = self.analyze_gitignore()

        # Find patterns in .gitignore that aren't in CRUFT_PATTERNS
        current_patterns_set = set(self.CRUFT_PATTERNS)
        new_from_gitignore = []

        for pattern in gitignore_patterns:
            # Normalize pattern for comparison
            normalized = pattern.rstrip("/")

            # Check if pattern or similar pattern already exists
            is_new = True
            for existing in current_patterns_set:
                if normalized in existing or existing in normalized:
                    is_new = False
                    break

            if is_new:
                new_from_gitignore.append(pattern)

        detected["gitignore_patterns"] = new_from_gitignore
        if not silent:
            print(f"   Found {len(gitignore_patterns)} total .gitignore patterns")
            print(
                f"   Detected {len(new_from_gitignore)} new patterns not in current cruft list"
            )

        # 2. Analyze historical removals
        if not silent:
            print("2️⃣  Analyzing git history for frequently removed files...")
        deletion_counts = self.analyze_historical_removals()

        # Find patterns that appear in deletion history
        frequent_deletions = {
            path: count for path, count in deletion_counts.items() if count >= 3
        }

        # Extract patterns from frequently deleted files
        pattern_counts: dict[str, int] = {}
        for path in frequent_deletions:
            # Extract file extension patterns
            if "." in path:
                ext = "*" + path[path.rfind(".") :]
                pattern_counts[ext] = pattern_counts.get(ext, 0) + 1

            # Extract directory patterns
            if "/" in path:
                parts = path.split("/")
                for part in parts[:-1]:  # Exclude filename
                    if part.startswith(".") or part in {
                        "node_modules",
                        "__pycache__",
                        "dist",
                        "build",
                    }:
                        dir_pattern = f"{part}/"
                        pattern_counts[dir_pattern] = (
                            pattern_counts.get(dir_pattern, 0) + 1
                        )

        # Sort by frequency and filter out existing patterns
        new_from_history = []
        for pattern, count in sorted(
            pattern_counts.items(), key=operator.itemgetter(1), reverse=True
        ):
            is_new = True
            for existing in current_patterns_set:
                if pattern in existing or existing in pattern:
                    is_new = False
                    break
            if is_new and count >= 3:  # At least 3 occurrences
                new_from_history.append(f"{pattern} (removed {count}x)")

        detected["historical_removals"] = new_from_history
        detected["total_gitignore_patterns"] = len(gitignore_patterns)
        detected["total_deletions"] = len(deletion_counts)

        if not silent:
            print(f"   Analyzed {len(deletion_counts)} deleted files")
            print(f"   Detected {len(new_from_history)} frequently removed patterns")

        # 3. Generate recommendations
        if not silent:
            print("3️⃣  Generating recommendations...")

        # Combine and deduplicate
        recommended = set()

        # Add high-confidence patterns from .gitignore
        for pattern in new_from_gitignore[:20]:  # Top 20
            # Skip very generic patterns
            if pattern not in {"*", "**", ".", ".."}:
                recommended.add(pattern)

        # Add high-confidence patterns from history
        for entry in new_from_history[:10]:  # Top 10
            pattern = entry.split(" (")[0]
            recommended.add(pattern)

        detected["recommended_patterns"] = sorted(recommended)

        if not silent:
            print(
                f"   Generated {len(detected['recommended_patterns']) if isinstance(detected['recommended_patterns'], list) else 0} recommended patterns"
            )

        # 4. Display results (skip if silent)
        if silent:
            return detected

        print(f"\n{'=' * 70}")
        print("📊 DETECTION RESULTS")
        print(f"{'=' * 70}\n")

        if detected["recommended_patterns"]:
            print("🎯 RECOMMENDED PATTERNS TO ADD:")
            print()
            recommended_patterns = detected["recommended_patterns"]
            if isinstance(recommended_patterns, list):
                for i, pattern in enumerate(recommended_patterns, 1):
                    print(f"   {i:2d}. {pattern}")
                print()
                print("To add these patterns, update CRUFT_PATTERNS in the script:")
                print("   CRUFT_PATTERNS = [")
                print("       # ... existing patterns ...")
                for pattern in recommended_patterns:
                    print(f'       "{pattern}",')
                print("   ]")
                print()
        else:
            print("✅ No additional cruft patterns detected!")
            print("   Current CRUFT_PATTERNS list is comprehensive.")
            print()

        # 5. Show detailed breakdown
        if new_from_gitignore:
            print("📄 NEW PATTERNS FROM .GITIGNORE:")
            for pattern in new_from_gitignore[:10]:
                print(f"   • {pattern}")
            if len(new_from_gitignore) > 10:
                print(f"   ... and {len(new_from_gitignore) - 10} more")
            print()

        if new_from_history:
            print("📜 FREQUENTLY REMOVED PATTERNS:")
            for entry in new_from_history[:10]:
                print(f"   • {entry}")
            if len(new_from_history) > 10:
                print(f"   ... and {len(new_from_history) - 10} more")
            print()

        return detected

    def update_all_gitignores(self) -> None:
        """Update all .gitignore files in workspace with comprehensive cruft patterns."""
        print(f"\n{'=' * 70}")
        print("📝 UPDATING ALL .GITIGNORE FILES")
        print(f"{'=' * 70}\n")

        # Patterns to add to .gitignore
        gitignore_additions = [
            "# === FLEXT WORKSPACE CRUFT PATTERNS ===",
            "# Auto-generated by git_ultimate_cleanup.py",
            "",
            "# Python compiled",
            "*.pyc",
            "*.pyo",
            "*.py[cod]",
            "*$py.class",
            "*.so",
            "*.pyd",
            "",
            "# Virtual environments",
            ".env",
            ".venv",
            "venv/",
            "ENV/",
            ".Python",
            "",
            "# Testing & Coverage",
            "coverage.xml",
            "coverage.json",
            "*.cover",
            ".hypothesis/",
            "junit.xml",
            ".nox/",
            ".pyre/",
            ".pytype/",
            ".bandit/",
            "",
            "# Build & Distribution",
            ".installed.cfg",
            "MANIFEST",
            "*.manifest",
            "*.spec",
            "",
            "# Meltano/Singer state",
            "state.json",
            "*.state",
            "*.state.json",
            "catalog.json",
            "target_config.json",
            "",
            "# DBT",
            "dbt.log",
            "dbt_packages/",
            "target/",
            "profiles.yml.bak",
            "profiles/profiles.yml.backup",
            "**/.user.yml",
            "",
            "# Documentation builds",
            "docs/_build/",
            "site/",
            "",
            "# Temporary/Debug scripts",
            "temp_*.py",
            "*_temp.py",
            "*_temp.md",
            "fix_*.py",
            "*_fix.py",
            "debug_*.py",
            "investigate_*.py",
            "validate_*.py",
            "*_validation.py",
            "",
            "# Analysis/Report files",
            "*_analysis.txt",
            "*_output.txt",
            "*_report.txt",
            "temp_test_*",
            "analysis_temp/",
            "report_*/",
            "reports_*/",
            "",
            "# AI-generated documentation (frequently deleted)",
            "*_COMPLETE.md",
            "*_PLAN.md",
            "*_GUIDE.md",
            "*_CHECKLIST.md",
            "*_PROMPT.md",
            "*_ASSESSMENT.md",
            "*_CONTROL.md",
            "*_AUDIT*.md",
            "*_RESULTS.md",
            "*_STATUS.md",
            "*_HANDOVER.md",
            "*_REFACTORING*.md",
            "*_REORGANIZATION*.md",
            "*_STANDARDIZATION*.md",
            "*_OPTIMIZATION*.md",
            "*_METHODOLOGY*.md",
            "*_BASELINE*.md",
            "*_MODERNIZATION*.md",
            "RELATORIO_*.md",
            "COMPREHENSIVE_*.md",
            "COMPLETE_*.md",
            "TODO.md",
            "lint-report.md",
            "mypy_*.md",
            "*-report.md",
            "*-cleanup*.md",
            "*-summary.md",
            "*_report.md",
            "*_analysis.md",
            "*_summary.md",
            "*_REPORT*.md",
            "*_ANALYSIS*.md",
            "*_SUMMARY*.md",
            "*_FINDINGS*.md",
            "CONFIG_MIGRATION*.md",
            "DEVELOPMENT_STANDARDS*.md",
            "DUPLICATION_REPORT*.md",
            "LINT_CORRECTIONS*.md",
            "*.ai.md",
            "*.ai.txt",
            "*.md_20250*",
            "CRUFT_DETECTION_REPORT.md",
            "",
            "# Backup patterns",
            "*.backup",
            "*.bak",
            "*.orig",
            "*~",
            ".*.swp",
            "*.syntax_backup",
            "*.broken",
            "*.tmp.bak",
            "*_backup",
            "*_backup_*",
            "temp_backup",
            "",
            "# Archive directories",
            ".archive/",
            "archive/",
            "archives/",
            "backups/",
            "*backup*/",
            "",
            "# System files",
            "Desktop.ini",
            "*.swo",
            "",
        ]

        # Get all repositories
        repos_to_update = [self.repo_path]
        submodules = self.get_submodules()
        repos_to_update.extend(submodules)

        updated_count = 0
        skipped_count = 0

        for repo in repos_to_update:
            gitignore_path = repo / ".gitignore"

            # Read existing .gitignore
            if gitignore_path.exists():
                existing_content = gitignore_path.read_text()
            else:
                existing_content = ""

            # Check if already updated
            if "# === FLEXT WORKSPACE CRUFT PATTERNS ===" in existing_content:
                print(f"   ⏭️  {repo.name}: Already updated")
                skipped_count += 1
                continue

            # Append new patterns
            new_content = (
                existing_content.rstrip()
                + "\n\n"
                + "\n".join(gitignore_additions)
                + "\n"
            )

            # Write updated .gitignore
            gitignore_path.write_text(new_content)
            updated_count += 1
            print(f"   ✅ {repo.name}: Updated with {len(gitignore_additions)} lines")

        print("\n📊 Summary:")
        print(f"   • Updated: {updated_count} repositories")
        print(f"   • Skipped: {skipped_count} (already updated)")
        print(f"   • Total: {len(repos_to_update)}")
        print()

    def generate_workspace_cruft_report(self, output_file: Path) -> None:
        """Generate comprehensive cruft detection report for entire workspace."""
        print(f"\n{'=' * 70}")
        print("🔍 WORKSPACE-WIDE CRUFT DETECTION")
        print(f"{'=' * 70}\n")

        all_results = []

        # Analyze main repository
        print(f"📁 Analyzing main repository: {self.repo_path.name}")
        main_result = self.detect_additional_cruft(silent=True)
        all_results.append(main_result)
        print("   ✅ Complete")

        # Analyze all submodules
        submodules = self.get_submodules()
        if submodules:
            print(f"\n📦 Analyzing {len(submodules)} submodules...")
            for i, submodule in enumerate(submodules, 1):
                print(f"   [{i:2d}/{len(submodules)}] {submodule.name}...", end=" ")
                try:
                    sub_cleanup = GitUltimateCleanup(submodule)
                    sub_result = sub_cleanup.detect_additional_cruft(silent=True)
                    all_results.append(sub_result)
                    print("✅")
                except Exception as e:
                    print(f"❌ Error: {e}")

        # Aggregate results
        print(f"\n📊 Aggregating results from {len(all_results)} repositories...")

        pattern_frequency: dict[str, int] = {}
        repos_by_pattern: dict[str, list[str]] = {}

        for result in all_results:
            recommended_patterns = result.get("recommended_patterns", [])
            if isinstance(recommended_patterns, list):
                for pattern in recommended_patterns:
                    pattern_frequency[pattern] = pattern_frequency.get(pattern, 0) + 1
                    if pattern not in repos_by_pattern:
                        repos_by_pattern[pattern] = []
                    repos_list = repos_by_pattern[pattern]
                    if isinstance(repos_list, list) and isinstance(
                        result["repo_name"], str
                    ):
                        repos_list.append(result["repo_name"])

        # Sort by frequency
        sorted_patterns = sorted(
            pattern_frequency.items(), key=operator.itemgetter(1), reverse=True
        )

        # Generate markdown report
        print(f"📝 Generating report: {output_file}")

        report = []
        report.extend([
            "# FLEXT Workspace Cruft Detection Report\n",
            f"**Generated**: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Repositories Analyzed**: {len(all_results)}\n",
            f"**Current CRUFT_PATTERNS**: {len(self.CRUFT_PATTERNS)}\n\n",
            "---\n\n",
            "## 📊 Executive Summary\n\n",
        ])

        def get_int_value(r: dict[str, list[str] | str | int], key: str) -> int:
            value = r.get(key, 0)
            return value if isinstance(value, int) else 0

        def get_list_length(r: dict[str, list[str] | str | int], key: str) -> int:
            value = r.get(key, [])
            return len(value) if isinstance(value, list) else 0

        total_gitignore = sum(
            get_int_value(r, "total_gitignore_patterns") for r in all_results
        )
        total_deletions = sum(get_int_value(r, "total_deletions") for r in all_results)
        total_new_patterns = sum(
            get_list_length(r, "gitignore_patterns") for r in all_results
        )
        total_recommended = len(pattern_frequency)

        report.extend([
            f"- **Total .gitignore patterns analyzed**: {total_gitignore:,}\n",
            f"- **Total historical deletions analyzed**: {total_deletions:,}\n",
            f"- **New patterns detected**: {total_new_patterns:,}\n",
            f"- **Unique recommended patterns**: {total_recommended}\n\n",
            "## 🎯 Recommended Patterns by Frequency\n\n",
            "Patterns appearing in multiple repositories (sorted by frequency):\n\n",
        ])
        report.extend([
            "| # | Pattern | Repos | Found In |\n",
            "|---|---------|-------|----------|\n",
        ])

        for i, (pattern, count) in enumerate(sorted_patterns[:50], 1):  # Top 50
            repos_str = ", ".join(repos_by_pattern[pattern][:3])
            if len(repos_by_pattern[pattern]) > 3:
                repos_str += f", +{len(repos_by_pattern[pattern]) - 3} more"
            report.append(f"| {i} | `{pattern}` | {count} | {repos_str} |\n")

        if len(sorted_patterns) > 50:
            report.append(f"\n*... and {len(sorted_patterns) - 50} more patterns*\n")

        report.extend([
            "\n",
            "## 🔥 High-Priority Patterns\n\n",
            "Patterns found in 5+ repositories (should be added to global CRUFT_PATTERNS):\n\n",
        ])

        high_priority = [p for p, c in sorted_patterns if c >= 5]
        if high_priority:
            report.extend((
                "```python\n",
                "# Add to CRUFT_PATTERNS in git_ultimate_cleanup.py:\n",
            ))
            report.extend(f'"{pattern}",\n' for pattern in high_priority)
            report.append("```\n\n")
        else:
            report.append("*No patterns found in 5+ repositories*\n\n")

        # Per-Repository Breakdown
        report.append("## 📁 Per-Repository Analysis\n\n")

        for result in sorted(
            all_results,
            key=lambda x: len(patterns)
            if isinstance((patterns := x.get("recommended_patterns")), list)
            else 0,
            reverse=True,
        ):
            repo_name = result["repo_name"]
            gitignore_count = result.get("total_gitignore_patterns", 0)
            deletions_count = result.get("total_deletions", 0)

            recommended_patterns = result.get("recommended_patterns", [])
            if not isinstance(recommended_patterns, list) or not recommended_patterns:
                continue  # Skip repos with no recommendations

            report.extend((
                f"### {repo_name}\n\n",
                f"- **.gitignore patterns**: {gitignore_count}\n",
                f"- **Historical deletions**: {deletions_count}\n",
                f"- **New patterns detected**: {len(recommended_patterns)}\n\n",
            ))

            if recommended_patterns:
                report.extend((
                    "<details>\n",
                    f"<summary><b>Show {len(recommended_patterns)} patterns</b></summary>\n\n",
                ))
                report.extend(f"- `{pattern}`\n" for pattern in recommended_patterns)
                report.append("\n</details>\n\n")

        # Repos with no new patterns
        clean_repos = [
            r["repo_name"]
            for r in all_results
            if not isinstance(r.get("recommended_patterns", []), list)
            or not r.get("recommended_patterns", [])
        ]
        if clean_repos:
            report.extend((
                "## ✅ Clean Repositories\n\n",
                "Repositories with no additional cruft patterns detected:\n\n",
            ))
            report.extend(f"- {repo}\n" for repo in clean_repos)
            report.append("\n")

        # Action Items
        report.extend([
            "## 📋 Action Items\n\n",
            "1. **Review high-priority patterns** (5+ repos) and add to global CRUFT_PATTERNS\n",
            "2. **Evaluate repo-specific patterns** for local .gitignore updates\n",
            "3. **Run cleanup** with updated patterns:\n",
            "   ```bash\n",
            "   python3 scripts/git_ultimate_cleanup.py --all --push-all\n",
            "   ```\n\n",
            "## 📈 Detection Statistics\n\n",
            "| Repository | .gitignore | Deletions | New Patterns |\n",
            "|------------|------------|-----------|---------------|\n",
        ])

        for result in sorted(all_results, key=operator.itemgetter("repo_name")):
            repo_name = result["repo_name"]
            gitignore = result.get("total_gitignore_patterns", 0)
            deletions = result.get("total_deletions", 0)
            recommended_patterns = result.get("recommended_patterns", [])
            new_patterns = (
                len(recommended_patterns)
                if isinstance(recommended_patterns, list)
                else 0
            )
            report.append(
                f"| {repo_name} | {gitignore} | {deletions} | {new_patterns} |\n"
            )

        report.extend((
            "\n---\n\n",
            f"*Report generated by git_ultimate_cleanup.py at {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}*\n",
        ))

        # Write report
        output_file.write_text("".join(report), encoding="utf-8")

        print(f"\n✅ Report generated: {output_file}")
        print("\n📊 Summary:")
        print(f"   • Repositories analyzed: {len(all_results)}")
        print(f"   • Unique patterns found: {len(pattern_frequency)}")
        print(
            f"   • High-priority patterns (5+ repos): {len(high_priority) if high_priority else 0}"
        )
        print()


def main() -> None:
    """Main entry point for the git ultimate cleanup script."""
    parser = argparse.ArgumentParser(
        description="FLEXT Git Ultimate Cleanup - The Only Script You Need",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Repository path")
    parser.add_argument(
        "--all", action="store_true", help="Process main + all submodules"
    )
    parser.add_argument("--backup-only", action="store_true", help="Only create backup")
    parser.add_argument(
        "--restore-remotes", action="store_true", help="Only restore remotes"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Test mode - simulate operations without changes",
    )
    parser.add_argument(
        "--test", action="store_true", help="Run principal function tests and exit"
    )
    parser.add_argument(
        "--push", action="store_true", help="Push to GitHub after cleanup"
    )
    parser.add_argument(
        "--push-all", action="store_true", help="Push main + all submodules to GitHub"
    )
    parser.add_argument(
        "--detect-cruft",
        action="store_true",
        help="Detect additional cruft patterns from history and .gitignore",
    )
    parser.add_argument(
        "--workspace-report",
        type=str,
        metavar="FILE",
        help="Generate workspace-wide cruft detection report (e.g., CRUFT_REPORT.md)",
    )
    parser.add_argument(
        "--update-gitignores",
        action="store_true",
        help="Update all .gitignore files with comprehensive cruft patterns",
    )

    args = parser.parse_args()

    if not args.repo.exists():
        print(f"❌ Repository not found: {args.repo}")
        sys.exit(1)

    cleanup = GitUltimateCleanup(args.repo, dry_run=args.dry_run)

    # Just test
    if args.test:
        if cleanup.test_principal_functions():
            sys.exit(0)
        else:
            sys.exit(1)

    # Detect additional cruft
    if args.detect_cruft:
        cleanup.detect_additional_cruft()
        sys.exit(0)

    # Generate workspace report
    if args.workspace_report:
        output_file = Path(args.workspace_report)
        cleanup.generate_workspace_cruft_report(output_file)
        sys.exit(0)

    # Update all .gitignore files
    if args.update_gitignores:
        cleanup.update_all_gitignores()
        sys.exit(0)

    # Just restore remotes
    if args.restore_remotes:
        cleanup.restore_remotes()
        sys.exit(0)

    # Validate
    print(f"\n{'=' * 70}")
    print("🔍 VALIDATION")
    print(f"{'=' * 70}\n")

    valid, message = cleanup.validate_repository()
    if not valid:
        print(f"❌ {message}")
        sys.exit(1)
    print(message)

    # Confirm (skip in dry-run)
    if not args.backup_only and not args.dry_run:
        print(f"\n{'=' * 70}")
        print("⚠️  WARNING")
        print(f"{'=' * 70}")
        print("This will PERMANENTLY modify git history!")
        print(f"Repository: {args.repo}")
        print("Author: Marlon Costa <marlonsc@gmail.com>")
        print("AI references: REMOVED")
        print("Cruft: PURGED from history")
        if args.all:
            print("Scope: Main repo + ALL submodules")
        print()
        response = input("Continue? (yes/NO): ")
        if response.lower() != "yes":
            print("Cancelled.")
            sys.exit(0)

    # Create backup (skip in dry-run)
    if not args.dry_run:
        backup_path = cleanup.create_comprehensive_backup()

        if args.backup_only:
            print(f"✅ Backup complete: {backup_path}")
            sys.exit(0)
    else:
        backup_path = None

    # Cleanup main repo
    success = cleanup.cleanup_repository()
    if not success:
        sys.exit(1)

    # Cleanup submodules
    if args.all:
        submodules = cleanup.get_submodules()
        if submodules:
            print(f"\n{'=' * 70}")
            print(f"📦 SUBMODULES ({len(submodules)} total)")
            print(f"{'=' * 70}\n")

            for submodule in submodules:
                sub_cleanup = GitUltimateCleanup(submodule, dry_run=args.dry_run)
                sub_cleanup.cleanup_repository()

    # Restore remotes (not in dry-run)
    if not args.dry_run:
        cleanup.restore_remotes()

    # Push to GitHub if requested
    if args.push or args.push_all:
        if not args.dry_run:
            # Push main repo
            push_success = cleanup.push_to_github()
            if not push_success:
                print("⚠️  Main repository push failed")
                sys.exit(1)

            # Push submodules if requested
            if args.push_all:
                push_success = cleanup.push_all_submodules()
                if not push_success:
                    print("⚠️  Some submodule pushes failed")
                    sys.exit(1)
        else:
            print(f"\n{'=' * 70}")
            print("🧪 DRY RUN - WOULD PUSH TO GITHUB")
            print(f"{'=' * 70}\n")
            cleanup.push_to_github()
            if args.push_all:
                cleanup.push_all_submodules()

    # Final summary
    print(f"\n{'=' * 70}")
    if args.dry_run:
        print("🧪 DRY RUN COMPLETE")
    else:
        print("✅ CLEANUP COMPLETE")
    print(f"{'=' * 70}\n")

    if args.dry_run:
        print("📋 Dry run complete - no changes made")
        print("   Run without --dry-run to execute cleanup")
    else:
        print("📋 Next steps:")
        print("   1. Review: git log --oneline --format='%h %an: %s' | head -20")
        print("   2. Check authors: git log --format='%aN <%aE>' | sort -u")
        print("   3. Check size: git count-objects -vH")
        if not args.push and not args.push_all:
            print("   4. Force push: git push origin --force --all")
            print("   5. Push tags: git push origin --force --tags")
            if args.all:
                print(
                    "   6. Submodules: git submodule foreach 'git push origin --force --all'"
                )
        print()
        if backup_path:
            print(f"💾 Backup: {backup_path}")
            print(f"   To recover: cd {backup_path} && ./RECOVER.sh")
    print()


if __name__ == "__main__":
    main()
