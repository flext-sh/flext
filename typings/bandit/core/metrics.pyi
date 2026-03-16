"""Type stubs for bandit.core.metrics module."""

class Metrics:
    """Bandit metric gathering.

    This class is a singleton used to gather and process metrics collected when
    processing a code base with bandit. Metric collection is stateful, that
    is, an active metric block will be set when requested and all subsequent
    operations will effect that metric block until it is replaced by a setting
    a new one.
    """

    data: dict[str, dict[str, int]]
    def __init__(self) -> None: ...
    def begin(self, fname: str) -> None:
        """Begin a new metric block.

        This starts a new metric collection name "fname" and makes is active.
        :param fname: the metrics unique name, normally the file name.
        """
    def note_nosec(self, num: int = ...) -> None:
        """Note a "nosec" comment.

        Increment the currently active metrics nosec count.
        :param num: number of nosecs seen, defaults to 1
        """
    def note_skipped_test(self, num: int = ...) -> None:
        """Note a "nosec BXXX, BYYY, ..." comment.

        Increment the currently active metrics skipped_tests count.
        :param num: number of skipped_tests seen, defaults to 1
        """
    def count_locs(self, lines: list[bytes]) -> None:
        """Count lines of code.

        We count lines that are not empty and are not comments. The result is
        added to our currently active metrics loc count (normally this is 0).

        :param lines: lines in the file to process
        """
    def count_issues(self, scores: list[dict[str, list[int]]]) -> None: ...
    def aggregate(self) -> None:
        """Do final aggregation of metrics."""
