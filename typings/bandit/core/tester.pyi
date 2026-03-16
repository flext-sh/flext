
import logging

from bandit.core.context import Context
from bandit.core.metrics import Metrics
from bandit.core.test_set import BanditTestSet

LOG: logging.Logger

class BanditTester:
    def __init__(
        self,
        testset: BanditTestSet,
        debug: bool,
        nosec_lines: dict[int, set[str]],
        metrics: Metrics,
    ) -> None: ...
    def run_tests(
        self, raw_context: dict[str, object], checktype: str
    ) -> dict[str, list[int]]: ...
    @staticmethod
    def report_error(test: str, context: Context, error: Exception) -> None: ...
