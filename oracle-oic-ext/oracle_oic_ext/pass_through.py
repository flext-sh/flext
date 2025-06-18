"""Pass-through invoker for Oracle OIC extension."""

from __future__ import annotations

import sys

import structlog
from meltano.edk.process import Invoker, log_subprocess_error

log = structlog.get_logger()


def pass_through_cli() -> None:
    """Pass through CLI for Oracle OIC extension."""
    log.debug("Running pass-through invoker", command=sys.argv[1:])

    # Pass through to actual command
    invoker = Invoker("oracle-oic-ext")

    try:
        invoker.run(*sys.argv[1:])
    except Exception as e:
        log_subprocess_error(
            "oracle-oic-ext invocation failed",
            e,
            "oracle-oic-ext",
        )
        sys.exit(1)


if __name__ == "__main__":
    pass_through_cli()
