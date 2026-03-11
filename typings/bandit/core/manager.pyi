import logging
import re

from bandit.core.config import BanditConfig
from bandit.core.issue import Issue

LOG: logging.Logger
NOSEC_COMMENT: re.Pattern[str]
NOSEC_COMMENT_TESTS: re.Pattern[str]
PROGRESS_THRESHOLD: int

class BanditManager:
    scope: list[object]

    def __init__(
        self,
        config: BanditConfig,
        agg_type: str,
        debug: bool = ...,
        verbose: bool = ...,
        quiet: bool = ...,
        profile: dict[str, object] | None = ...,
        ignore_nosec: bool = ...,
    ) -> None: ...
    def get_skipped(self) -> list[tuple[str, str]]: ...
    def get_issue_list(
        self, sev_level: str = ..., conf_level: str = ...
    ) -> list[Issue]: ...
    def populate_baseline(self, data: str) -> None: ...
    def filter_results(self, sev_filter: str, conf_filter: str) -> list[Issue]: ...
    def results_count(self, sev_filter: str = ..., conf_filter: str = ...) -> int: ...
    def output_results(
        self,
        lines: int,
        sev_level: str,
        conf_level: str,
        output_file: object,
        output_format: str,
        template: str | None = ...,
    ) -> None: ...
    def discover_files(
        self,
        targets: list[str],
        recursive: bool = ...,
        excluded_paths: str = ...,
    ) -> None: ...
    def run_tests(self) -> None: ...
