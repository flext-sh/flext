#!/usr/bin/env python3
"""
Heuristic-Based Git History Rewriter for FLEXT Workspace

This script analyzes git commit history and generates improved commit messages
using intelligent heuristics, following conventional commit format and FLEXT context.

No API keys required - works completely offline!

Usage:
    python git_history_rewriter.py --repo /path/to/repo
    python git_history_rewriter.py --batch-submodules  # Process all submodules
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class CommitInfo:
    """Represents a git commit with metadata."""
    sha: str
    author: str
    date: str
    message: str
    files_changed: list[str]
    diff_stats: str


class GitHistoryAnalyzer:
    """Analyzes git repository commit history."""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    def get_commit_list(self, branch: str = "HEAD") -> list[str]:
        """Get list of all commit SHAs."""
        cmd = ["git", "-C", str(self.repo_path), "rev-list", branch]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip().split("\n")

    def get_commit_info(self, sha: str) -> CommitInfo:
        """Get detailed information about a commit."""
        # Get commit metadata
        cmd = ["git", "-C", str(self.repo_path), "show",
               "--format=%an%n%ad%n%s%n%b", "--no-patch", sha]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split("\n")
        author = lines[0]
        date = lines[1]
        message = "\n".join(lines[2:])

        # Get files changed
        cmd = ["git", "-C", str(self.repo_path), "show",
               "--name-only", "--format=", sha]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        files_changed = [f for f in result.stdout.strip().split("\n") if f]

        # Get diff stats
        cmd = ["git", "-C", str(self.repo_path), "show",
               "--stat", "--format=", sha]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        diff_stats = result.stdout.strip()

        return CommitInfo(
            sha=sha,
            author=author,
            date=date,
            message=message,
            files_changed=files_changed,
            diff_stats=diff_stats
        )


class AICommitMessageRewriter:
    """Rewrites commit messages using intelligent heuristics."""

    SYSTEM_PROMPT = """Git commit message heuristics for FLEXT Enterprise Data Integration Platform.

FLEXT Context:
- Python 3.13 enterprise data integration framework
- Modular architecture with domain libraries (flext-core, flext-ldap, flext-api, etc.)
- ETL/ELT pipelines using Meltano, Singer, DBT
- Oracle, LDAP, LDIF data sources
- Following SOLID principles and type-safe patterns

Your task: Rewrite commit messages to follow Conventional Commits format:

Format: <type>(<scope>): <description>

Types: feat, fix, refactor, docs, style, test, chore, perf, ci, build
Scopes: core, ldap, api, cli, web, db, meltano, observability, etc.

Rules:
1. Be concise but descriptive (max 72 chars for subject)
2. Use present tense ("add" not "added")
3. Don't capitalize first letter after colon
4. Focus on WHAT and WHY, not HOW
5. Remove noise like "WIP", "tmp", version numbers as sole message
6. Combine similar consecutive commits conceptually
7. Preserve important context (issue numbers, breaking changes)

Examples:
- "0.9.0" → "chore(release): bump version to 0.9.0"
- "fix typo" → "docs: correct typos in documentation"
- "WIP async" → "feat(core): implement async execution patterns"
"""

    def __init__(self, api_key: Optional[str] = None):
        # No API key needed for heuristic approach
        pass

    def rewrite_message(self, commit: CommitInfo) -> str:
        """Rewrite commit message using intelligent heuristics."""
        original = commit.message.split("\n")[0].strip()
        return self._apply_heuristics(original, commit)

    def _apply_heuristics(self, message: str, commit: CommitInfo) -> str:
        """Apply rule-based conventional commit transformations."""
        # Version bump commits
        if message.strip() and all(c in '0123456789.' for c in message.strip()):
            return f"chore(release): bump version to {message.strip()}"

        # WIP/tmp commits
        if message.lower().startswith(('wip', 'tmp', 'temp', 'test')):
            files = commit.files_changed
            if files:
                main_dir = files[0].split('/')[0] if '/' in files[0] else 'core'
                return f"feat({main_dir}): work in progress on {main_dir}"

        # Typo fixes
        if 'typo' in message.lower():
            return "docs: correct typos in documentation"

        # Lint/format fixes
        if any(word in message.lower() for word in ['lint', 'format', 'black', 'ruff', 'isort']):
            return "style: apply code formatting and linting"

        # Already conventional format
        conventional_types = ['feat', 'fix', 'docs', 'style', 'refactor', 'perf', 'test', 'chore', 'build', 'ci', 'revert']
        for type_ in conventional_types:
            if message.startswith(f"{type_}(") or message.startswith(f"{type_}:"):
                return message

        # Default: try to infer type from files changed
        files = commit.files_changed
        if files:
            # Detect scope from file paths
            if any('test' in f.lower() for f in files):
                return f"test: {message}"
            elif any(f.endswith('.md') for f in files):
                return f"docs: {message}"
            elif any('src/' in f for f in files):
                main_dir = next((f.split('/')[1] for f in files if 'src/' in f and len(f.split('/')) > 1), 'core')
                return f"feat({main_dir}): {message}"

        # Fallback: chore
        return f"chore: {message}"

    def batch_rewrite(self, commits: list[CommitInfo],
                     output_file: Path) -> dict[str, str]:
        """Rewrite multiple commits and save mapping."""
        mapping = {}
        total = len(commits)

        print(f"🔄 Processing {total} commits...")

        for i, commit in enumerate(commits, 1):
            print(f"  [{i}/{total}] {commit.sha[:8]}: {commit.message[:50]}...")

            # Skip if already looks good
            original = commit.message.split("\n")[0]
            if self._looks_conventional(original):
                print(f"    ✓ Already conventional, keeping")
                mapping[commit.sha] = original
                continue

            new_message = self.rewrite_message(commit)
            mapping[commit.sha] = new_message

            print(f"    → {new_message}")

        # Save mapping file for git-filter-repo
        self._save_mapping(mapping, output_file)

        return mapping

    def _looks_conventional(self, message: str) -> bool:
        """Check if message already follows conventional commits."""
        types = ["feat", "fix", "refactor", "docs", "style", "test",
                "chore", "perf", "ci", "build"]
        for type_ in types:
            if message.startswith(f"{type_}(") or message.startswith(f"{type_}:"):
                return True
        return False

    def _save_mapping(self, mapping: dict[str, str], output_file: Path):
        """Save commit SHA to message mapping for git-filter-repo."""
        # Format: old_message==>new_message
        lines = []
        for sha, new_msg in mapping.items():
            # git-filter-repo expects literal old message
            lines.append(f"{new_msg}")

        output_file.write_text("\n".join(lines))
        print(f"\n✅ Saved {len(mapping)} mappings to {output_file}")


class HistoryCleanupOrchestrator:
    """Orchestrates the full history cleanup process."""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.analyzer = GitHistoryAnalyzer(repo_path)
        self.rewriter = AICommitMessageRewriter()
        self.output_dir = repo_path / ".git" / "history-cleanup"
        self.output_dir.mkdir(exist_ok=True)

    def analyze_and_generate_mapping(self):
        """Main workflow: analyze commits and generate rewrite mapping."""
        print(f"\n{'='*60}")
        print(f"🔍 ANALYZING: {self.repo_path.name}")
        print(f"{'='*60}\n")

        # Get all commits
        print("📊 Fetching commit history...")
        commit_shas = self.analyzer.get_commit_list()
        print(f"   Found {len(commit_shas)} commits\n")

        # Analyze each commit
        print("📖 Analyzing commit details...")
        commits = []
        for sha in commit_shas[:100]:  # Limit for initial run
            commit = self.analyzer.get_commit_info(sha)
            commits.append(commit)
        print(f"   Analyzed {len(commits)} commits (limited to 100 for safety)\n")

        # Rewrite messages
        mapping_file = self.output_dir / "commit-msg-mapping.txt"
        self.rewriter.batch_rewrite(commits, mapping_file)

        # Generate summary
        self._generate_summary(commits, mapping_file)

        return mapping_file

    def _generate_summary(self, commits: list[CommitInfo], mapping_file: Path):
        """Generate cleanup summary report."""
        summary_file = self.output_dir / "cleanup-summary.json"

        summary = {
            "repo": str(self.repo_path),
            "total_commits_analyzed": len(commits),
            "mapping_file": str(mapping_file),
            "authors": list(set(c.author for c in commits)),
            "files_affected": len(set(f for c in commits for f in c.files_changed)),
        }

        summary_file.write_text(json.dumps(summary, indent=2))
        print(f"\n📄 Summary saved to {summary_file}")


def main():
    parser = argparse.ArgumentParser(description="Heuristic-based git history rewriter")
    parser.add_argument("--repo", type=Path, help="Path to git repository")
    parser.add_argument("--batch-submodules", action="store_true",
                       help="Process all submodules in current directory")

    args = parser.parse_args()

    if args.batch_submodules:
        # Find all submodules
        result = subprocess.run(
            ["git", "submodule", "status"],
            capture_output=True, text=True, check=True
        )
        submodules = [line.split()[1] for line in result.stdout.strip().split("\n")]

        for submodule in submodules:
            submodule_path = Path.cwd() / submodule
            if submodule_path.exists():
                orchestrator = HistoryCleanupOrchestrator(submodule_path)
                orchestrator.analyze_and_generate_mapping()
            else:
                print(f"⚠️  Submodule not found: {submodule}")

    elif args.repo:
        orchestrator = HistoryCleanupOrchestrator(args.repo)
        mapping_file = orchestrator.analyze_and_generate_mapping()

        print(f"\n{'='*60}")
        print("✅ ANALYSIS COMPLETE")
        print(f"{'='*60}")
        print(f"\nNext steps:")
        print(f"1. Review generated mapping: {mapping_file}")
        print(f"2. Create backup: git tag pre-cleanup-backup")
        print(f"3. Run git-filter-repo:")
        print(f"   cd {args.repo}")
        print(f"   git filter-repo --replace-message {mapping_file} --force")
        print(f"\n💡 Tip: Use Cursor AI to review and improve suggestions")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
