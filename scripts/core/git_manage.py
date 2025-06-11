#!/usr/bin/env python3
"""
Git Management Script

Provides Git operations for the pyauto workspace.

This script handles:
1. Git status checking
2. Committing changes
3. Fetching updates
4. Pushing changes
5. Branch operations

Usage:
    python git_manage.py [command] [options]
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Absolute paths
WORKSPACE_ROOT = Path("/home/marlonsc/pyauto")

# Colors for terminal output
COLORS = {
    "GREEN": "\033[0;32m",
    "YELLOW": "\033[0;33m",
    "RED": "\033[0;31m",
    "BLUE": "\033[0;34m",
    "MAGENTA": "\033[0;35m",
    "CYAN": "\033[0;36m",
    "NC": "\033[0m",  # No Color
}


def colorize(text: str, color: str) -> str:
    """Add color to terminal output."""
    return f"{COLORS.get(color, '')}{text}{COLORS['NC']}"


def is_git_repo(path: Path) -> bool:
    """Check if a directory is a git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=str(path),
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0 and result.stdout.strip() == "true"
    except Exception:
        return False


def run_git_command(
    cmd: list[str],
    cwd: Path | None = None,
    capture_output: bool = False,
    check: bool = True,
) -> subprocess.CompletedProcess:
    """Run a git command."""
    git_cmd = ["git"] + cmd
    working_dir = cwd if cwd else WORKSPACE_ROOT

    # Check if directory is a git repository
    if not is_git_repo(working_dir):
        print(colorize(f"Error: {working_dir} is not a git repository", "RED"))
        if check:
            sys.exit(1)

        # Return a fake CompletedProcess with error information
        class FakeCompletedProcess:
            def __init__(self):
                self.returncode = 1
                self.stdout = ""
                self.stderr = f"Not a git repository: {working_dir}"

        return FakeCompletedProcess()

    try:
        return subprocess.run(
            git_cmd,
            cwd=str(working_dir),
            capture_output=capture_output,
            text=True,
            check=check,
        )
    except subprocess.CalledProcessError as e:
        print(f"{colorize('Error:', 'RED')} {e}")
        if capture_output and e.stderr:
            print(e.stderr)
        if check:
            sys.exit(1)
        return e


def get_git_status() -> str:
    """Get git status."""
    result = run_git_command(["status", "-s"], capture_output=True)
    return result.stdout


def show_git_status() -> None:
    """Show git status."""
    print(colorize("Git Status:", "YELLOW"))

    status = get_git_status()
    if not status.strip():
        print(colorize("Working tree clean", "GREEN"))
    else:
        print(status)


def git_fetch(remote: str = "origin") -> None:
    """Fetch updates from remote."""
    print(colorize(f"Fetching updates from {remote}...", "YELLOW"))

    run_git_command(["fetch", remote])

    print(colorize("Fetch complete!", "GREEN"))


def git_commit(message: str | None = None) -> None:
    """Commit changes."""
    # Show status first
    show_git_status()

    # If no changes, exit
    status = get_git_status()
    if not status.strip():
        print(colorize("No changes to commit", "YELLOW"))
        return

    # Get commit message
    if not message:
        message = input("Enter commit message: ")

    if not message:
        print(colorize("Commit message cannot be empty", "RED"))
        return

    print(colorize(f"Committing changes with message: {message}", "YELLOW"))

    # Add all changes
    run_git_command(["add", "."])

    # Commit
    run_git_command(["commit", "-m", message])

    print(colorize("Commit complete!", "GREEN"))


def git_push(remote: str = "origin", branch: str | None = None) -> None:
    """Push changes to remote."""
    push_cmd = ["push", remote]

    if branch:
        push_cmd.append(branch)

    remote_branch = f"{remote}/{branch}" if branch else remote
    print(colorize(f"Pushing to {remote_branch}...", "YELLOW"))

    run_git_command(push_cmd)

    print(colorize("Push complete!", "GREEN"))


def git_create_branch(branch_name: str, base_branch: str | None = None) -> None:
    """Create a new branch."""
    create_cmd = ["checkout", "-b", branch_name]

    if base_branch:
        # First checkout the base branch
        run_git_command(["checkout", base_branch])
        print(colorize(f"Switched to base branch: {base_branch}", "YELLOW"))

    print(colorize(f"Creating new branch: {branch_name}...", "YELLOW"))

    run_git_command(create_cmd)

    print(colorize(f"Branch {branch_name} created and checked out!", "GREEN"))


def git_checkout(branch_name: str) -> None:
    """Switch to a branch."""
    print(colorize(f"Switching to branch: {branch_name}...", "YELLOW"))

    run_git_command(["checkout", branch_name])

    print(colorize(f"Switched to {branch_name}!", "GREEN"))


def git_log(count: int = 10) -> None:
    """Show git log."""
    print(colorize(f"Last {count} commits:", "YELLOW"))

    result = run_git_command(["log", f"-{count}", "--oneline"], capture_output=True)
    print(result.stdout)


def git_diff(staged: bool = False) -> None:
    """Show changes."""
    if staged:
        print(colorize("Staged changes:", "YELLOW"))
        result = run_git_command(["diff", "--staged"], capture_output=True)
    else:
        print(colorize("Unstaged changes:", "YELLOW"))
        result = run_git_command(["diff"], capture_output=True)

    if not result.stdout.strip():
        print(colorize("No changes", "GREEN"))
    else:
        print(result.stdout)


def git_stash(
    pop: bool = False,
    apply: bool = False,
    list_stashes: bool = False,
) -> None:
    """Stash operations."""
    if list_stashes:
        print(colorize("Stash list:", "YELLOW"))
        result = run_git_command(["stash", "list"], capture_output=True)
        if not result.stdout.strip():
            print(colorize("No stashes", "GREEN"))
        else:
            print(result.stdout)
        return

    if pop:
        print(colorize("Popping stash...", "YELLOW"))
        run_git_command(["stash", "pop"])
        print(colorize("Stash popped!", "GREEN"))
        return

    if apply:
        print(colorize("Applying stash...", "YELLOW"))
        run_git_command(["stash", "apply"])
        print(colorize("Stash applied!", "GREEN"))
        return

    # Default is to stash
    print(colorize("Stashing changes...", "YELLOW"))
    run_git_command(["stash"])
    print(colorize("Changes stashed!", "GREEN"))


def git_branch_list() -> None:
    """list branches."""
    print(colorize("Local branches:", "YELLOW"))
    result = run_git_command(["branch"], capture_output=True)
    print(result.stdout)

    print(colorize("Remote branches:", "YELLOW"))
    result = run_git_command(["branch", "-r"], capture_output=True)
    print(result.stdout)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Git management utilities")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Status command
    subparsers.add_parser("status", help="Show git status")

    # Fetch command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch updates from remote")
    fetch_parser.add_argument("--remote", default="origin", help="Remote to fetch from")

    # Commit command
    commit_parser = subparsers.add_parser("commit", help="Commit changes")
    commit_parser.add_argument("--message", "-m", help="Commit message")

    # Push command
    push_parser = subparsers.add_parser("push", help="Push changes to remote")
    push_parser.add_argument("--remote", default="origin", help="Remote to push to")
    push_parser.add_argument("--branch", help="Branch to push")

    # Branch commands
    branch_parser = subparsers.add_parser("branch", help="Branch operations")
    branch_subparsers = branch_parser.add_subparsers(
        dest="branch_command",
        help="Branch command",
    )

    # Create branch
    create_branch_parser = branch_subparsers.add_parser(
        "create",
        help="Create a new branch",
    )
    create_branch_parser.add_argument("name", help="Branch name")
    create_branch_parser.add_argument("--base", help="Base branch")

    # Checkout branch
    checkout_branch_parser = branch_subparsers.add_parser(
        "checkout",
        help="Checkout a branch",
    )
    checkout_branch_parser.add_argument("name", help="Branch name")

    # list branches
    branch_subparsers.add_parser("list", help="list branches")

    # Log command
    log_parser = subparsers.add_parser("log", help="Show commit log")
    log_parser.add_argument(
        "--count",
        "-n",
        type=int,
        default=10,
        help="Number of commits to show",
    )

    # Diff command
    diff_parser = subparsers.add_parser("diff", help="Show changes")
    diff_parser.add_argument(
        "--staged",
        "-s",
        action="store_true",
        help="Show staged changes",
    )

    # Stash commands
    stash_parser = subparsers.add_parser("stash", help="Stash operations")
    stash_parser.add_argument("--pop", action="store_true", help="Pop stash")
    stash_parser.add_argument("--apply", action="store_true", help="Apply stash")
    stash_parser.add_argument("--list", action="store_true", help="list stashes")

    args = parser.parse_args()

    # Process commands
    if args.command == "status":
        show_git_status()

    elif args.command == "fetch":
        git_fetch(args.remote)

    elif args.command == "commit":
        git_commit(args.message)

    elif args.command == "push":
        git_push(args.remote, args.branch)

    elif args.command == "branch":
        if args.branch_command == "create":
            git_create_branch(args.name, args.base)
        elif args.branch_command == "checkout":
            git_checkout(args.name)
        elif args.branch_command == "list":
            git_branch_list()
        else:
            branch_parser.print_help()

    elif args.command == "log":
        git_log(args.count)

    elif args.command == "diff":
        git_diff(args.staged)

    elif args.command == "stash":
        git_stash(args.pop, args.apply, args.list)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
