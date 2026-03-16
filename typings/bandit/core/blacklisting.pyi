

from bandit.core.issue import Issue

def report_issue(check: dict[str, object], name: str) -> Issue: ...
def blacklist(
    context: object, config: dict[str, list[dict[str, object]]]
) -> Issue | None:
    ...
