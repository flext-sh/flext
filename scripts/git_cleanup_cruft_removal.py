#!/usr/bin/env python3
"""
Git Cruft Removal Script for FLEXT Workspace

This script provides intelligent cruft detection and removal strategies:
- Remove WIP/temp/test commits
- Squash consecutive version bump commits
- Remove typo-fix commits (merge into previous)
- Filter merge commits
- Remove commits with no meaningful changes

Usage:
    python git_cleanup_cruft_removal.py --repo /path/to/repo --strategy aggressive
    python git_cleanup_cruft_removal.py --repo . --dry-run
"""

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class CrufтRemovalConfig:
    """Configuration for cruft removal."""
    remove_wip: bool = True
    remove_version_only: bool = True
    remove_typo_fixes: bool = True
    remove_merge_commits: bool = False
    squash_consecutive_versions: bool = True
    min_commit_message_length: int = 10


class CruftDetector:
    """Detects various types of cruft commits."""

    @staticmethod
    def is_wip_commit(message: str) -> bool:
        """Check if commit is WIP/temp/test cruft."""
        lower_msg = message.lower().strip()
        cruft_patterns = [
            'wip', 'tmp', 'temp', 'test', 'asdf', 'fuck', 'shit',
            'debug', 'checkpoint', 'save', 'backup', 'oops',
            'fix fix', 'quick fix', 'hotfix'
        ]
        return any(lower_msg.startswith(p) for p in cruft_patterns)

    @staticmethod
    def is_version_only(message: str) -> bool:
        """Check if commit is just a version number."""
        msg = message.strip()
        # Match patterns like "0.9.0", "v1.2.3", "1.0"
        import re
        version_pattern = r'^v?\d+\.\d+(\.\d+)?$'
        return bool(re.match(version_pattern, msg))

    @staticmethod
    def is_typo_fix(message: str) -> bool:
        """Check if commit is just a typo fix."""
        lower_msg = message.lower().strip()
        typo_patterns = [
            'fix typo', 'typo', 'fix typos', 'typos',
            'fix spelling', 'spelling', 'fix whitespace',
            'whitespace', 'formatting'
        ]
        return any(p in lower_msg for p in typo_patterns)

    @staticmethod
    def is_lint_fix(message: str) -> bool:
        """Check if commit is just a lint/format fix."""
        lower_msg = message.lower().strip()
        lint_patterns = [
            'fix lint', 'lint', 'fix linting', 'linting',
            'run black', 'black', 'run ruff', 'ruff',
            'run isort', 'isort', 'fix formatting'
        ]
        return any(p in lower_msg for p in lint_patterns)

    @staticmethod
    def is_merge_commit(message: str) -> bool:
        """Check if commit is a merge commit."""
        return message.startswith('Merge ')

    @staticmethod
    def is_too_short(message: str, min_length: int = 10) -> bool:
        """Check if commit message is too short to be meaningful."""
        return len(message.strip()) < min_length


class GitCruftRemover:
    """Removes cruft commits from git history."""

    def __init__(self, repo_path: Path, config: CrufтRemovalConfig):
        self.repo_path = repo_path
        self.config = config
        self.detector = CruftDetector()

    def analyze_cruft(self) -> dict:
        """Analyze repository to identify cruft commits."""
        cmd = ['git', '-C', str(self.repo_path), 'log', '--all', '--format=%H|||%s']
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        analysis = {
            'total_commits': 0,
            'wip_commits': [],
            'version_only': [],
            'typo_fixes': [],
            'lint_fixes': [],
            'merge_commits': [],
            'too_short': [],
            'total_cruft': 0
        }

        for line in result.stdout.strip().split('\n'):
            if not line:
                continue

            sha, message = line.split('|||', 1)
            analysis['total_commits'] += 1

            is_cruft = False

            if self.config.remove_wip and self.detector.is_wip_commit(message):
                analysis['wip_commits'].append((sha, message))
                is_cruft = True

            if self.config.remove_version_only and self.detector.is_version_only(message):
                analysis['version_only'].append((sha, message))
                is_cruft = True

            if self.config.remove_typo_fixes and self.detector.is_typo_fix(message):
                analysis['typo_fixes'].append((sha, message))
                is_cruft = True

            if self.detector.is_lint_fix(message):
                analysis['lint_fixes'].append((sha, message))
                is_cruft = True

            if self.config.remove_merge_commits and self.detector.is_merge_commit(message):
                analysis['merge_commits'].append((sha, message))
                is_cruft = True

            if self.detector.is_too_short(message, self.config.min_commit_message_length):
                analysis['too_short'].append((sha, message))

            if is_cruft:
                analysis['total_cruft'] += 1

        return analysis

    def generate_removal_script(self, analysis: dict, output_path: Path):
        """Generate Python callback script for git-filter-repo."""
        script_content = '''#!/usr/bin/env python3
"""
Auto-generated cruft removal callback for git-filter-repo

This script removes the following types of cruft:
'''

        if self.config.remove_wip:
            script_content += f"- WIP/temp commits: {len(analysis['wip_commits'])} commits\n"
        if self.config.remove_version_only:
            script_content += f"- Version-only commits: {len(analysis['version_only'])} commits\n"
        if self.config.remove_typo_fixes:
            script_content += f"- Typo fix commits: {len(analysis['typo_fixes'])} commits\n"
        if self.config.remove_merge_commits:
            script_content += f"- Merge commits: {len(analysis['merge_commits'])} commits\n"

        script_content += '''
Total cruft to remove: {total} commits
Original total: {original} commits
After cleanup: {after} commits ({percentage:.1f}% reduction)
"""

import re

def is_wip_commit(message):
    """Check if commit is WIP/temp/test cruft."""
    lower_msg = message.lower()
    cruft_patterns = [
        b'wip', b'tmp', b'temp', b'test', b'asdf', b'debug',
        b'checkpoint', b'save', b'backup', b'oops'
    ]
    return any(lower_msg.startswith(p) for p in cruft_patterns)

def is_version_only(message):
    """Check if commit is just a version number."""
    msg = message.strip()
    version_pattern = rb'^v?\\d+\\.\\d+(\\.\\d+)?$'
    return bool(re.match(version_pattern, msg))

def is_typo_fix(message):
    """Check if commit is just a typo fix."""
    lower_msg = message.lower()
    return b'typo' in lower_msg or b'spelling' in lower_msg

def is_lint_fix(message):
    """Check if commit is just a lint fix."""
    lower_msg = message.lower()
    return b'lint' in lower_msg or b'black' in lower_msg or b'ruff' in lower_msg

def is_merge_commit(message):
    """Check if commit is a merge commit."""
    return message.startswith(b'Merge ')

# This function will be called by git-filter-repo for each commit
def process_commit(commit, metadata):
    """Filter out cruft commits."""
    message = commit.message

    # Check all cruft patterns
    is_cruft = False

'''.format(
            total=analysis['total_cruft'],
            original=analysis['total_commits'],
            after=analysis['total_commits'] - analysis['total_cruft'],
            percentage=(analysis['total_cruft'] / analysis['total_commits'] * 100) if analysis['total_commits'] > 0 else 0
        )

        if self.config.remove_wip:
            script_content += "    if is_wip_commit(message):\n        is_cruft = True\n\n"

        if self.config.remove_version_only:
            script_content += "    if is_version_only(message):\n        is_cruft = True\n\n"

        if self.config.remove_typo_fixes:
            script_content += "    if is_typo_fix(message):\n        is_cruft = True\n\n"

        script_content += "    if is_lint_fix(message):\n        is_cruft = True\n\n"

        if self.config.remove_merge_commits:
            script_content += "    if is_merge_commit(message):\n        is_cruft = True\n\n"

        script_content += '''
    # Skip (remove) cruft commits
    if is_cruft:
        commit.skip()
'''

        output_path.write_text(script_content)
        output_path.chmod(0o755)
        return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Intelligent cruft removal for git history"
    )
    parser.add_argument("--repo", type=Path, required=True,
                       help="Path to git repository")
    parser.add_argument("--strategy", choices=['conservative', 'moderate', 'aggressive'],
                       default='moderate',
                       help="Cruft removal strategy")
    parser.add_argument("--dry-run", action="store_true",
                       help="Analyze only, don't generate removal script")
    parser.add_argument("--no-wip", action="store_true",
                       help="Don't remove WIP commits")
    parser.add_argument("--no-version", action="store_true",
                       help="Don't remove version-only commits")
    parser.add_argument("--no-typo", action="store_true",
                       help="Don't remove typo fix commits")
    parser.add_argument("--remove-merges", action="store_true",
                       help="Remove merge commits")

    args = parser.parse_args()

    # Configure based on strategy
    if args.strategy == 'conservative':
        config = CrufтRemovalConfig(
            remove_wip=not args.no_wip,
            remove_version_only=False,
            remove_typo_fixes=False,
            remove_merge_commits=args.remove_merges,
            squash_consecutive_versions=False,
            min_commit_message_length=5
        )
    elif args.strategy == 'moderate':
        config = CrufтRemovalConfig(
            remove_wip=not args.no_wip,
            remove_version_only=not args.no_version,
            remove_typo_fixes=not args.no_typo,
            remove_merge_commits=args.remove_merges,
            squash_consecutive_versions=True,
            min_commit_message_length=10
        )
    else:  # aggressive
        config = CrufтRemovalConfig(
            remove_wip=True,
            remove_version_only=True,
            remove_typo_fixes=True,
            remove_merge_commits=True,
            squash_consecutive_versions=True,
            min_commit_message_length=15
        )

    remover = GitCruftRemover(args.repo, config)

    print(f"\n{'='*60}")
    print(f"🗑️  CRUFT ANALYSIS: {args.repo.name}")
    print(f"{'='*60}\n")
    print(f"Strategy: {args.strategy.upper()}")
    print("")

    # Analyze cruft
    analysis = remover.analyze_cruft()

    # Display results
    print(f"📊 Repository Statistics:")
    print(f"   Total commits: {analysis['total_commits']}")
    print(f"   Total cruft detected: {analysis['total_cruft']}")
    print(f"   After cleanup: {analysis['total_commits'] - analysis['total_cruft']}")
    reduction = (analysis['total_cruft'] / analysis['total_commits'] * 100) if analysis['total_commits'] > 0 else 0
    print(f"   Reduction: {reduction:.1f}%")
    print("")

    print(f"🔍 Cruft Breakdown:")
    if config.remove_wip:
        print(f"   WIP/temp commits: {len(analysis['wip_commits'])}")
        if analysis['wip_commits'][:3]:
            for sha, msg in analysis['wip_commits'][:3]:
                print(f"      • {sha[:8]}: {msg[:50]}")
            if len(analysis['wip_commits']) > 3:
                print(f"      ... and {len(analysis['wip_commits']) - 3} more")

    if config.remove_version_only:
        print(f"   Version-only commits: {len(analysis['version_only'])}")
        if analysis['version_only'][:3]:
            for sha, msg in analysis['version_only'][:3]:
                print(f"      • {sha[:8]}: {msg}")
            if len(analysis['version_only']) > 3:
                print(f"      ... and {len(analysis['version_only']) - 3} more")

    if config.remove_typo_fixes:
        print(f"   Typo fix commits: {len(analysis['typo_fixes'])}")
        if analysis['typo_fixes'][:3]:
            for sha, msg in analysis['typo_fixes'][:3]:
                print(f"      • {sha[:8]}: {msg[:50]}")
            if len(analysis['typo_fixes']) > 3:
                print(f"      ... and {len(analysis['typo_fixes']) - 3} more")

    if analysis['lint_fixes']:
        print(f"   Lint/format commits: {len(analysis['lint_fixes'])}")

    if config.remove_merge_commits and analysis['merge_commits']:
        print(f"   Merge commits: {len(analysis['merge_commits'])}")

    print("")

    if args.dry_run:
        print(f"{'='*60}")
        print("✅ DRY RUN - No changes made")
        print(f"{'='*60}")
        print("")
        print("To apply cruft removal:")
        print(f"  1. python {sys.argv[0]} --repo {args.repo} --strategy {args.strategy}")
        print("  2. Review generated callback script")
        print("  3. Run git-filter-repo with the callback")
        return

    # Generate removal script
    output_path = args.repo / ".git" / "history-cleanup" / "cruft-removal-callback.py"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    script_path = remover.generate_removal_script(analysis, output_path)

    print(f"{'='*60}")
    print("✅ CRUFT REMOVAL SCRIPT GENERATED")
    print(f"{'='*60}")
    print("")
    print(f"Script location: {script_path}")
    print("")
    print("Next steps:")
    print("")
    print("1. Review the script:")
    print(f"   cat {script_path}")
    print("")
    print("2. Create backup:")
    print(f"   cd {args.repo}")
    print("   git tag pre-cruft-removal-$(date +%Y%m%d)")
    print("")
    print("3. Apply cruft removal:")
    print(f"   cd {args.repo}")
    print(f"   git filter-repo --force --commit-callback {script_path}")
    print("")
    print("4. Verify results:")
    print("   git log --oneline | head -20")
    print(f"   git rev-list --all --count  # Should be ~{analysis['total_commits'] - analysis['total_cruft']}")
    print("")
    print(f"⚠️  WARNING: This will remove {analysis['total_cruft']} commits permanently!")
    print("")


if __name__ == "__main__":
    main()
