"""Rich error handling utilities for enhanced debugging and monitoring.

This module provides centralized error handling with rich formatting,
structured logging integration, and configurable output for different
environments (development, testing, production).
"""

from __future__ import annotations

import functools
import sys
from contextlib import contextmanager
from typing import TYPE_CHECKING, TextIO

import structlog
from rich.console import Console
from rich.traceback import install as install_rich_traceback

if TYPE_CHECKING:
    from collections.abc import Iterator

logger = structlog.get_logger(__name__)

# Configure rich traceback globally with development-friendly defaults
install_rich_traceback(
    show_locals=True,
    max_frames=20,
    width=120,
    extra_lines=3,
    theme="ansi_dark",
    word_wrap=True,
    suppress=[
        # Suppress noisy framework tracebacks
        "click",
        "fastapi",
        "starlette",
        "uvicorn",
        "sqlalchemy.engine",
        "asyncio",
    ],
)


class RichErrorHandler:
    """Enhanced error handling with rich formatting and structured logging."""

    def __init__(
        self,
        console: Console | None = None,
        *,
        show_locals: bool = True,
        max_frames: int = 20,
        extra_lines: int = 3,
        suppress_frameworks: bool = True,
    ) -> None:
        """Initialize rich error handler.

        Args:
        ----
            console: Rich console instance (creates default if None)
            show_locals: Whether to show local variables in tracebacks
            max_frames: Maximum number of stack frames to show
            extra_lines: Extra lines of code context around each frame
            suppress_frameworks: Whether to suppress common framework noise

        """
        self.console = console or Console(file=sys.stderr, force_terminal=True)
        self.show_locals = show_locals
        self.max_frames = max_frames
        self.extra_lines = extra_lines

        self.suppress_patterns = (
            [
                "click",
                "fastapi",
                "starlette",
                "uvicorn",
                "sqlalchemy.engine",
                "asyncio",
            ]
            if suppress_frameworks
            else []
        )

    def print_exception(
        self,
        _exc: BaseException | None = None,
        *,
        show_locals: bool | None = None,
        max_frames: int | None = None,
        extra_lines: int | None = None,
        theme: str = "ansi_dark",
        word_wrap: bool = True,
    ) -> None:
        """Print rich formatted exception with configurable options.

        Args:
        ----
            exc: Exception to format (uses current exception if None)
            show_locals: Override default show_locals setting
            max_frames: Override default max_frames setting
            extra_lines: Override default extra_lines setting
            theme: Rich theme for syntax highlighting
            word_wrap: Whether to wrap long lines

        """
        self.console.print_exception(
            show_locals=show_locals if show_locals is not None else self.show_locals,
            max_frames=max_frames if max_frames is not None else self.max_frames,
            extra_lines=extra_lines if extra_lines is not None else self.extra_lines,
            theme=theme,
            word_wrap=word_wrap,
            suppress=self.suppress_patterns,
        )

    def log_and_print_exception(
        self, message: str, exc: BaseException | None = None, **log_kwargs: object
    ) -> None:
        """Log structured message and print rich exception.

        Args:
        ----
            message: Log message
            exc: Exception to format and log
            **log_kwargs: Additional structured logging fields

        """
        # Log structured message
        logger.error(message, **log_kwargs)

        # Print rich formatted exception
        self.print_exception(exc)

    @contextmanager
    def error_context(
        self,
        message: str,
        *,
        re_raise: bool = True,
        log_level: str = "exception",
        **log_kwargs: object,
    ) -> Iterator[None]:
        """Context manager for enhanced error handling.

        Args:
        ----
            message: Context message for logging
            re_raise: Whether to re-raise caught exceptions
            log_level: Logging level for caught exceptions
            **log_kwargs: Additional structured logging fields

        Yields:
        ------
            None: Context for executing code with error handling

        Example:
        -------
            with error_handler.error_context("Database initialization"):
                await database.initialize()

        """
        try:
            yield
        except (
            RuntimeError,
            ValueError,
            TypeError,
            ImportError,
            OSError,
            ConnectionError,
        ) as e:
            # Log with appropriate level
            if log_level == "exception":
                logger.exception(message, error=str(e), **log_kwargs)
            else:
                getattr(logger, log_level)(message, error=str(e), **log_kwargs)

            # Print rich formatted exception
            self.print_exception(e)

            if re_raise:
                raise


# ZERO TOLERANCE - Modern Python 3.13 singleton pattern using functools.lru_cache


@functools.lru_cache(maxsize=1)
def get_error_handler() -> RichErrorHandler:
    """Get the global rich error handler instance."""
    return RichErrorHandler()


def configure_error_handler(
    console: Console | None = None,
    *,
    show_locals: bool = True,
    max_frames: int = 20,
    extra_lines: int = 3,
    suppress_frameworks: bool = True,
) -> None:
    """Configure the global error handler.

    Args:
    ----
        console: Rich console instance
        show_locals: Whether to show local variables
        max_frames: Maximum stack frames to show
        extra_lines: Extra lines of code context
        suppress_frameworks: Whether to suppress framework noise

    """
    # ZERO TOLERANCE: Clear cache and create new handler with configuration
    get_error_handler.cache_clear()

    # Create new configured handler using factory pattern
    @functools.lru_cache(maxsize=1)
    def _get_configured_handler() -> RichErrorHandler:
        return RichErrorHandler(
            console=console,
            show_locals=show_locals,
            max_frames=max_frames,
            extra_lines=extra_lines,
            suppress_frameworks=suppress_frameworks,
        )

    # Replace the global getter with configured version
    globals()["get_error_handler"] = _get_configured_handler


def print_exception(exc: BaseException | None = None, **kwargs: object) -> None:
    """Print rich formatted exception using global handler."""
    get_error_handler().print_exception(exc, **kwargs)


def log_and_print_exception(
    message: str, exc: BaseException | None = None, **log_kwargs: object
) -> None:
    """Log and print exception using global handler."""
    get_error_handler().log_and_print_exception(message, exc, **log_kwargs)


@contextmanager
def error_context(
    message: str,
    *,
    re_raise: bool = True,
    log_level: str = "exception",
    **log_kwargs: object,
) -> Iterator[None]:
    """Error context using global handler."""
    with get_error_handler().error_context(
        message,
        re_raise=re_raise,
        log_level=log_level,
        **log_kwargs,
    ):
        yield


# Configure rich traceback for production environments
def configure_production_traceback(
    *,
    show_locals: bool = False,
    max_frames: int = 10,
    console_file: TextIO | None = None,
) -> None:
    """Configure rich traceback for production environments.

    Args:
    ----
        show_locals: Whether to show local variables (security risk in production)
        max_frames: Limit stack frames for performance
        console_file: File to write tracebacks to (defaults to stderr)

    """
    install_rich_traceback(
        show_locals=show_locals,
        max_frames=max_frames,
        width=120,
        extra_lines=1,
        theme="ansi_dark",
        word_wrap=True,
        console=Console(file=console_file or sys.stderr, force_terminal=False),
        suppress=[
            "click",
            "fastapi",
            "starlette",
            "uvicorn",
            "sqlalchemy.engine",
            "asyncio",
            "concurrent.futures",
            "threading",
        ],
    )


# Export main components
__all__ = [
    "RichErrorHandler",
    "configure_error_handler",
    "configure_production_traceback",
    "error_context",
    "get_error_handler",
    "log_and_print_exception",
    "print_exception",
]
