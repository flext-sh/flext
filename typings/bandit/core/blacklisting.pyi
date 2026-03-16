"""Type stubs for bandit.core.blacklisting module."""

from bandit.core.issue import Issue

def report_issue(check: dict[str, object], name: str) -> Issue: ...
def blacklist(
    context: object, config: dict[str, list[dict[str, object]]]
) -> Issue | None:
    """Generic blacklist test, B001.

    This generic blacklist test will be called for any encountered node with
    defined blacklist data available. This data is loaded via plugins using
    the 'bandit.blacklists' entry point. Please see the documentation for more
    details. Each blacklist datum has a unique bandit ID that may be used for
    filtering purposes, or alternatively all blacklisting can be filtered using
    the id of this built in test, 'B001'.
    """
