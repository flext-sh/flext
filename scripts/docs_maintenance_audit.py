#!/usr/bin/env python3
# Owner-Skill: .claude/skills/scripts-maintenance/SKILL.md
"""Documentation audit utility for Makefile.docs and CI workflow."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from html import escape
from pathlib import Path

EXCLUDED_DIRS = {".git", ".venv", "node_modules", "dist", "build", "__pycache__"}
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


@dataclass(frozen=True)
class Issue:
    file: str
    issue_type: str
    severity: str
    message: str


@dataclass(frozen=True)
class Summary:
    total_files: int
    total_issues: int
    severity_counts: dict[str, int]


def find_markdown_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.md"):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        files.append(path)
    return sorted(files)


def normalize_target(raw_target: str) -> str:
    target = raw_target.strip()
    if "#" in target:
        target = target.split("#", maxsplit=1)[0]
    if "?" in target:
        target = target.split("?", maxsplit=1)[0]
    return target


def is_external(target: str) -> bool:
    lower = target.lower()
    return lower.startswith(("http://", "https://", "mailto:", "tel:", "data:"))


def collect_issues(root: Path, markdown_files: list[Path]) -> list[Issue]:
    issues: list[Issue] = []
    for md_file in markdown_files:
        rel_file = md_file.relative_to(root).as_posix()
        content = md_file.read_text(encoding="utf-8", errors="ignore")

        for line_number, line in enumerate(content.splitlines(), start=1):
            for raw_link in LINK_RE.findall(line):
                link = normalize_target(raw_link)
                if not link or link.startswith("#") or is_external(link):
                    continue
                target = (md_file.parent / link).resolve()
                try:
                    exists = target.exists()
                except OSError:
                    exists = False
                if not exists:
                    issues.append(
                        Issue(
                            file=rel_file,
                            issue_type="broken_link",
                            severity="high",
                            message=f"line {line_number}: target not found -> {raw_link}",
                        ),
                    )

        if "TODO" in content:
            issues.append(
                Issue(
                    file=rel_file,
                    issue_type="todo_marker",
                    severity="low",
                    message="contains TODO marker",
                ),
            )

    return issues


def summarize(markdown_files: list[Path], issues: list[Issue]) -> Summary:
    by_severity: dict[str, int] = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for issue in issues:
        by_severity[issue.severity] = by_severity.get(issue.severity, 0) + 1
    return Summary(
        total_files=len(markdown_files),
        total_issues=len(issues),
        severity_counts=by_severity,
    )


def to_markdown(summary: Summary, issues: list[Issue]) -> str:
    lines = [
        "# Documentation Audit Report",
        "",
        f"**Total Files Scanned:** {summary.total_files}",
        f"**Total Issues Found:** {summary.total_issues}",
        "",
        "## Severity Breakdown",
    ]
    severity_counts = summary.severity_counts
    lines.extend(
        f"- {sev}: {severity_counts.get(sev, 0)}"
        for sev in ("critical", "high", "medium", "low")
    )

    lines.append("")
    if not issues:
        lines.append("No issues found.")
        return "\n".join(lines) + "\n"

    lines.extend(
        [
            "## Issues",
            "",
            "| file | issue_type | severity | message |",
            "|---|---|---|---|",
        ],
    )
    lines.extend(
        f"| {issue.file} | {issue.issue_type} | {issue.severity} | {issue.message} |"
        for issue in issues
    )
    return "\n".join(lines) + "\n"


def to_json(summary: Summary, issues: list[Issue]) -> str:
    payload = {
        "summary": asdict(summary),
        "issues": [asdict(i) for i in issues],
    }
    return json.dumps(payload, indent=2, ensure_ascii=True) + "\n"


def to_html(summary: Summary, issues: list[Issue]) -> str:
    rows = "".join(
        f"<tr><td>{escape(i.file)}</td><td>{escape(i.issue_type)}</td><td>{escape(i.severity)}</td><td>{escape(i.message)}</td></tr>"
        for i in issues
    )
    if not rows:
        rows = "<tr><td colspan='4'>No issues found.</td></tr>"
    sev = summary.severity_counts
    return (
        "<html><body>"
        "<h1>Documentation Audit Report</h1>"
        f"<p><strong>Total Files Scanned:</strong> {summary.total_files}</p>"
        f"<p><strong>Total Issues Found:</strong> {summary.total_issues}</p>"
        "<ul>"
        f"<li>critical: {sev.get('critical', 0)}</li>"
        f"<li>high: {sev.get('high', 0)}</li>"
        f"<li>medium: {sev.get('medium', 0)}</li>"
        f"<li>low: {sev.get('low', 0)}</li>"
        "</ul>"
        "<table border='1' cellpadding='4' cellspacing='0'>"
        "<thead><tr><th>file</th><th>issue_type</th><th>severity</th><th>message</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></body></html>\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Documentation maintenance audit")
    parser.add_argument("--root", default=".", help="Root folder to scan")
    parser.add_argument("--output", required=True, help="Output report file")
    parser.add_argument(
        "--format", choices=["markdown", "json", "html"], default="markdown"
    )
    parser.add_argument(
        "--check-external-links", action="store_true", help="Accepted for compatibility"
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    markdown_files = find_markdown_files(root)
    issues = collect_issues(root, markdown_files)
    summary = summarize(markdown_files, issues)

    if args.format == "json":
        output_text = to_json(summary, issues)
    elif args.format == "html":
        output_text = to_html(summary, issues)
    else:
        output_text = to_markdown(summary, issues)

    output_path = Path(args.output)
    output_path.write_text(output_text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
