#!/usr/bin/env python3
"""FLEXT Documentation Link Validator.

Validates external and internal links in documentation files with retry logic,
caching, and comprehensive reporting.
"""

import asyncio
import json
import re
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

import aiohttp
from flext_core import FlextCore


@dataclass
class LinkResult:
    """Result of link validation."""

    url: str
    status: str
    status_code: int | None = None
    error_message: str | None = None
    response_time: float = 0.0
    redirect_url: str | None = None
    retries: int = 0


@dataclass
class ValidationResults:
    """Comprehensive validation results."""

    total_links: int = 0
    valid_links: int = 0
    broken_links: int = 0
    redirected_links: int = 0
    timeout_links: int = 0
    results: list[LinkResult] = field(default_factory=list)
    errors_by_domain: dict[str, FlextCore.Types.StringList] = field(
        default_factory=lambda: defaultdict(list)
    )


class LinkValidator:
    """Advanced link validation system."""

    def __init__(self, config: dict[str, object] | None = None) -> None:
        self.config = config or {}
        self.timeout = self.config.get("timeout", 10)
        self.max_retries = self.config.get("max_retries", 3)
        self.concurrent_requests = self.config.get("concurrent_requests", 10)
        self.user_agent = self.config.get(
            "user_agent", "FLEXT-Docs-Validator/1.0 (https://github.com/flext-sh/flext)"
        )
        self.cache_file = Path(self.config.get("cache_file", "docs/.link_cache.json"))
        self.cache_duration = self.config.get("cache_duration", 86400)  # 24 hours

        # Load cache
        self.cache = self.load_cache()

    def load_cache(self) -> dict[str, dict]:
        """Load link validation cache."""
        if self.cache_file.exists():
            try:
                with Path(self.cache_file).open(encoding="utf-8") as f:
                    data = json.load(f)
                    # Clean expired entries
                    current_time = time.time()
                    return {
                        url: result
                        for url, result in data.items()
                        if current_time - result.get("timestamp", 0)
                        < self.cache_duration
                    }
            except (json.JSONDecodeError, KeyError):
                pass
        return {}

    def save_cache(self) -> None:
        """Save link validation cache."""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with Path(self.cache_file).open("w", encoding="utf-8") as f:
            json.dump(self.cache, f, indent=2)

    def extract_links_from_file(self, file_path: Path) -> list[tuple[str, int]]:
        """Extract all links from a markdown file with line numbers."""
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            links = []
            for line_num, line in enumerate(lines, 1):
                # Find markdown links: [text](url)
                markdown_links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", line)
                for _, url in markdown_links:
                    if url.startswith(("http://", "https://")):
                        links.append((url, line_num))

            return links
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return []

    async def validate_link_async(
        self, session: aiohttp.ClientSession, url: str, retry_count: int = 0
    ) -> LinkResult:
        """Validate a single link asynchronously with retries."""
        start_time = time.time()

        # Check cache first
        cache_key = url
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if time.time() - cached["timestamp"] < self.cache_duration:
                return LinkResult(
                    url=url,
                    status=cached["status"],
                    status_code=cached.get("status_code"),
                    error_message=cached.get("error_message"),
                    response_time=cached.get("response_time", 0),
                    redirect_url=cached.get("redirect_url"),
                    retries=retry_count,
                )

        try:
            headers = {"User-Agent": self.user_agent}
            async with session.head(
                url, headers=headers, allow_redirects=True, timeout=self.timeout
            ) as response:
                response_time = time.time() - start_time
                redirect_url = str(response.url) if str(response.url) != url else None

                if response.status == 405:  # Method not allowed, try GET
                    async with session.get(
                        url, headers=headers, allow_redirects=True, timeout=self.timeout
                    ) as get_response:
                        response_time = time.time() - start_time
                        redirect_url = (
                            str(get_response.url)
                            if str(get_response.url) != url
                            else None
                        )

                        result = LinkResult(
                            url=url,
                            status="valid" if get_response.status < 400 else "broken",
                            status_code=get_response.status,
                            response_time=response_time,
                            redirect_url=redirect_url,
                            retries=retry_count,
                        )
                else:
                    result = LinkResult(
                        url=url,
                        status="valid" if response.status < 400 else "broken",
                        status_code=response.status,
                        response_time=response_time,
                        redirect_url=redirect_url,
                        retries=retry_count,
                    )

                # Handle redirects
                if response.status in {301, 302, 307, 308}:
                    result.status = "redirected"

        except TimeoutError:
            result = LinkResult(
                url=url,
                status="timeout",
                error_message="Request timed out",
                response_time=time.time() - start_time,
                retries=retry_count,
            )
        except aiohttp.ClientError as e:
            result = LinkResult(
                url=url,
                status="error",
                error_message=str(e),
                response_time=time.time() - start_time,
                retries=retry_count,
            )
        except Exception as e:
            result = LinkResult(
                url=url,
                status="error",
                error_message=f"Unexpected error: {e}",
                response_time=time.time() - start_time,
                retries=retry_count,
            )

        # Cache result
        self.cache[cache_key] = {
            "status": result.status,
            "status_code": result.status_code,
            "error_message": result.error_message,
            "response_time": result.response_time,
            "redirect_url": result.redirect_url,
            "timestamp": time.time(),
        }

        # Retry logic for certain errors
        if result.status in {"timeout", "error"} and retry_count < self.max_retries:
            await asyncio.sleep(1)  # Brief delay before retry
            return await self.validate_link_async(session, url, retry_count + 1)

        return result

    async def validate_links_batch(
        self, links: FlextCore.Types.StringList
    ) -> list[LinkResult]:
        """Validate multiple links concurrently."""
        async with aiohttp.ClientSession() as session:
            semaphore = asyncio.Semaphore(self.concurrent_requests)

            async def validate_with_semaphore(url: str) -> LinkResult:
                async with semaphore:
                    return await self.validate_link_async(session, url)

            tasks = [validate_with_semaphore(url) for url in links]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append(
                        LinkResult(
                            url=links[i] if i < len(links) else "unknown",
                            status="error",
                            error_message=f"Validation failed: {result}",
                        )
                    )
                else:
                    processed_results.append(result)

            return processed_results

    def validate_internal_links(
        self, doc_files: list[Path]
    ) -> dict[str, FlextCore.Types.StringList]:
        """Validate internal links between documentation files."""
        issues = defaultdict(list)

        # Build file mapping (filename -> path)
        file_map = {}
        for doc_file in doc_files:
            file_map[doc_file.name] = doc_file
            file_map[doc_file.stem] = doc_file  # Also map without extension

        for doc_file in doc_files:
            links = self.extract_links_from_file(doc_file)
            for url, line_num in links:
                if not url.startswith(("http://", "https://")):
                    # Internal link - check if target exists
                    if url.startswith(("./", "../")):
                        # Relative path
                        try:
                            target_path = (doc_file.parent / url).resolve()
                            if not target_path.exists():
                                issues[str(doc_file)].append(
                                    f"Line {line_num}: Broken internal link '{url}'"
                                )
                        except Exception:
                            issues[str(doc_file)].append(
                                f"Line {line_num}: Invalid relative link '{url}'"
                            )
                    elif url in file_map:
                        # File reference by name
                        continue  # Valid
                    elif "#" in url:
                        # Anchor link - check if file exists
                        base_url = url.split("#")[0]
                        if base_url and base_url not in file_map:
                            issues[str(doc_file)].append(
                                f"Line {line_num}: Broken anchor link '{url}'"
                            )
                    # Check if it's a valid file reference
                    elif url not in file_map:
                        issues[str(doc_file)].append(
                            f"Line {line_num}: Broken internal link '{url}'"
                        )

        return dict[str, object](issues)

    def analyze_link_health(self, results: list[LinkResult]) -> ValidationResults:
        """Analyze link validation results."""
        validation_results = ValidationResults()

        for result in results:
            validation_results.total_links += 1
            validation_results.results.append(result)

            if result.status == "valid":
                validation_results.valid_links += 1
            elif result.status == "broken":
                validation_results.broken_links += 1
                domain = urlparse(result.url).netloc
                validation_results.errors_by_domain[domain].append(result.url)
            elif result.status == "redirected":
                validation_results.redirected_links += 1
            elif result.status == "timeout":
                validation_results.timeout_links += 1

        return validation_results

    def generate_report(
        self,
        validation_results: ValidationResults,
        internal_issues: dict[str, FlextCore.Types.StringList],
    ) -> str:
        """Generate comprehensive validation report."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        report = f"""# FLEXT Link Validation Report

**Generated:** {timestamp}

## 📊 Summary

| Metric | Value | Status |
|--------|-------|---------|
| Total Links | {validation_results.total_links} | ✅ |
| Valid Links | {validation_results.valid_links} | {"✅" if validation_results.valid_links > 0 else "⚠️"} |
| Broken Links | {validation_results.broken_links} | {"❌" if validation_results.broken_links > 0 else "✅"} |
| Redirected Links | {validation_results.redirected_links} | {"⚠️" if validation_results.redirected_links > 0 else "✅"} |
| Timeout Links | {validation_results.timeout_links} | {"⚠️" if validation_results.timeout_links > 0 else "✅"} |
| Internal Link Issues | {sum(len(issues) for issues in internal_issues.values())} | {"❌" if internal_issues else "✅"} |

## 🔗 External Link Issues

"""

        if validation_results.broken_links > 0:
            report += "### Broken Links\n\n"
            for result in validation_results.results:
                if result.status == "broken":
                    report += f"- **{result.url}**\n"
                    report += f"  - Status: HTTP {result.status_code}\n"
                    if result.error_message:
                        report += f"  - Error: {result.error_message}\n"
                    report += "\n"

        if validation_results.errors_by_domain:
            report += "### Issues by Domain\n\n"
            for domain, urls in validation_results.errors_by_domain.items():
                report += f"#### {domain} ({len(urls)} issues)\n\n"
                for url in urls[:5]:  # Show first 5 per domain
                    report += f"- {url}\n"
                if len(urls) > 5:
                    report += f"- ... and {len(urls) - 5} more\n"
                report += "\n"

        # Internal link issues
        if internal_issues:
            report += "## 🔗 Internal Link Issues\n\n"
            for file_path, issues in internal_issues.items():
                report += f"### {file_path}\n\n"
                for issue in issues:
                    report += f"- {issue}\n"
                report += "\n"

        # Recommendations
        report += """## 💡 Recommendations

"""

        if validation_results.broken_links > 0:
            report += (
                f"- **Fix {validation_results.broken_links} broken external links**\n"
            )
        if validation_results.timeout_links > 0:
            report += f"- **Review {validation_results.timeout_links} timeout links** (may be temporarily unreachable)\n"
        if validation_results.redirected_links > 0:
            report += f"- **Update {validation_results.redirected_links} redirected links** to use final URLs\n"
        if internal_issues:
            report += f"- **Fix {sum(len(issues) for issues in internal_issues.values())} internal link issues**\n"

        if validation_results.total_links > 0:
            health_score = (
                validation_results.valid_links / validation_results.total_links
            )
            report += f"\n## 📈 Link Health Score: {health_score:.2%}\n"

        return report


def main() -> None:
    """Main entry point for link validation."""
    import argparse

    parser = argparse.ArgumentParser(description="FLEXT Documentation Link Validator")
    parser.add_argument(
        "files", nargs="*", help="Specific files to validate (default: all docs)"
    )
    parser.add_argument("--config", help="Configuration file")
    parser.add_argument("--output", "-o", help="Output report file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--external-only", action="store_true", help="Validate only external links"
    )
    parser.add_argument(
        "--internal-only", action="store_true", help="Validate only internal links"
    )

    args = parser.parse_args()

    # Configuration
    config = {}
    if args.config and Path(args.config).exists():
        with Path(args.config).open(encoding="utf-8") as f:
            config = json.load(f)

    validator = LinkValidator(config)

    # Discover files
    if args.files:
        doc_files = [
            Path(f)
            for f in args.files
            if Path(f).exists() and f.endswith((".md", ".mdx"))
        ]
    else:
        doc_files = []
        for pattern in ["*.md", "*.mdx"]:
            doc_files.extend(Path().rglob(pattern))

    if not doc_files:
        print("No documentation files found!")
        return

    print(f"📁 Found {len(doc_files)} documentation files")

    all_external_links = set()
    internal_issues = {}

    # Extract all links
    for doc_file in doc_files:
        links = validator.extract_links_from_file(doc_file)
        for url, _ in links:
            if url.startswith(("http://", "https://")):
                all_external_links.add(url)

    # Validate external links
    if not args.internal_only:
        print(f"🔗 Validating {len(all_external_links)} external links...")
        external_results = asyncio.run(
            validator.validate_links_batch(list(all_external_links))
        )
        validator.save_cache()

    # Validate internal links
    if not args.external_only:
        print("🔗 Validating internal links...")
        internal_issues = validator.validate_internal_links(doc_files)

    # Analyze results
    if not args.internal_only:
        validation_results = validator.analyze_link_health(external_results)
        report = validator.generate_report(validation_results, internal_issues)
    else:
        # Internal-only mode
        validation_results = ValidationResults()
        report = validator.generate_report(validation_results, internal_issues)

    # Output
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"📄 Report saved to: {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
