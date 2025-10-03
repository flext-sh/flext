#!/usr/bin/env python3
"""Git commit message rewriter using cursor-agent CLI.

This script rewrites git commit messages using cursor-agent for intelligent
heuristic-based improvements following conventional commit format.

Usage:
    python git_commit_rewriter_cursor.py --repo /path/to/repo
"""

import argparse
import subprocess
import sys
from pathlib import Path


class GitCommitRewriter:
    """Rewrites commit messages using cursor-agent CLI."""

    REWRITE_PROMPT = """Rewrite this git commit message to follow Conventional Commits format.

Format: <type>(<scope>): <description>

Types: feat, fix, refactor, docs, style, test, chore, perf, ci, build
Scopes: core, ldap, api, cli, web, db, meltano, observability, etc.

Rules:
1. Be concise (max 72 chars)
2. Use present tense
3. Don't capitalize first letter after colon
4. Focus on WHAT and WHY

Examples:
- "0.9.0" → "chore(release): bump version to 0.9.0"
- "fix typo" → "docs: correct typos in documentation"
- "WIP async" → "feat(core): implement async execution patterns"
- "fix lint" → "style: apply code formatting and linting"
- "***REMOVED***" → infer from context

Original message: {message}

Files changed: {files}

Return ONLY the new commit message (one line, no quotes or explanation)."""

    def __init__(self, repo_path: Path) -> None:
        """Initialize GitCommitRewriter."""
        self.repo_path = repo_path

    def get_commits(self) -> list[tuple[str, str, list[str]]]:
        """Get commit history with messages and files."""
        # Get commit SHAs
        result = subprocess.run(
            ["git", "-C", str(self.repo_path), "rev-list", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        shas = result.stdout.strip().split("\n")

        commits = []
        for sha in shas:
            # Get commit message
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), "log", "-1", "--format=%s", sha],
                capture_output=True,
                text=True,
                check=True,
            )
            message = result.stdout.strip()

            # Get files changed
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), "show", "--name-only", "--format=", sha],
                capture_output=True,
                text=True,
                check=True,
            )
            files = [f for f in result.stdout.strip().split("\n") if f]

            commits.append((sha, message, files))

        return commits

    def rewrite_with_cursor_agent(self, message: str, files: list[str]) -> str:
        """Use cursor-agent to rewrite a commit message."""
        # Format files summary
        files_summary = ", ".join(files[:5])
        if len(files) > 5:
            files_summary += f" and {len(files) - 5} more"

        # Build prompt
        prompt = self.REWRITE_PROMPT.format(message=message, files=files_summary)

        # Call cursor-agent with --print
        try:
            result = subprocess.run(
                ["cursor-agent", "--print", prompt],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )

            if result.returncode != 0:
                print(f"    ⚠️  cursor-agent failed, keeping original: {message[:50]}")
                return message

            # Parse response
            new_message = result.stdout.strip()

            # Clean up response (remove quotes, extra text)
            if '"' in new_message:
                new_message = new_message.split('"')[1] if '"' in new_message else new_message

            # Take first line only
            new_message = new_message.split("\n")[0].strip()

            # Validate conventional format
            if ":" not in new_message or len(new_message) > 100:
                print(f"    ⚠️  Invalid format, keeping original: {message[:50]}")
                return message

            return new_message

        except subprocess.TimeoutExpired:
            print(f"    ⚠️  Timeout, keeping original: {message[:50]}")
            return message
        except Exception as e:
            print(f"    ⚠️  Error: {e}, keeping original: {message[:50]}")
            return message

    def generate_mapping(self, output_file: Path) -> None:
        """Generate commit message mapping file."""
        print(f"\n🔍 Analyzing repository: {self.repo_path.name}")

        commits = self.get_commits()
        print(f"   Found {len(commits)} commits\n")

        print("🔄 Rewriting commit messages with cursor-agent...\n")

        mapping_lines = []
        for i, (sha, old_msg, files) in enumerate(commits, 1):
            print(f"  [{i}/{len(commits)}] {sha[:8]}: {old_msg[:50]}...")

            # Check if already conventional
            if self._is_conventional(old_msg):
                print("    ✓ Already conventional, keeping")
                mapping_lines.append(f"literal:{old_msg}==>{old_msg}")
                continue

            # Rewrite with cursor-agent
            new_msg = self.rewrite_with_cursor_agent(old_msg, files)
            print(f"    → {new_msg}")

            mapping_lines.append(f"literal:{old_msg}==>{new_msg}")

        # Save mapping file
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("\n".join(mapping_lines), encoding="utf-8")

        print(f"\n✅ Saved {len(mapping_lines)} mappings to {output_file}")

    def _is_conventional(self, message: str) -> bool:
        """Check if message follows conventional commits."""
        types = ["feat", "fix", "refactor", "docs", "style", "test", "chore", "perf", "ci", "build"]
        return any(message.startswith((f"{t}(", f"{t}:")) for t in types)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Git commit rewriter using cursor-agent")
    parser.add_argument("--repo", type=Path, required=True, help="Path to git repository")

    args = parser.parse_args()

    if not args.repo.exists():
        print(f"❌ Repository not found: {args.repo}")
        sys.exit(1)

    # Initialize rewriter
    rewriter = GitCommitRewriter(args.repo)

    # Determine output location
    if (args.repo / ".git").is_dir():
        git_dir = args.repo / ".git"
    else:
        # Submodule - .git is a file
        git_dir = args.repo.parent / ".git" / "modules" / args.repo.name

    output_file = git_dir / "history-cleanup" / "commit-msg-mapping.txt"

    # Generate mapping
    rewriter.generate_mapping(output_file)

    print("\n✅ Ready for git-filter-repo:")
    print(f"   git filter-repo --force --replace-message {output_file}")


if __name__ == "__main__":
    main()
