"""Type stubs for radon.cli.__init__ module."""

import configparser
from collections.abc import Callable, Generator, Iterable, Sequence
from contextlib import contextmanager
from typing import TypeVar

from radon.cli.harvest import Harvester

"""In this module the CLI interface is created."""

TOMLLIB_PRESENT: bool
CONFIG_SECTION_NAME: str

T = TypeVar("T")

class FileConfig:
    """Yield default options by reading local configuration files."""

    file_cfg: configparser.ConfigParser

    def __init__(self) -> None: ...
    def get_value(self, key: str, type: type[T], default: T) -> T: ...
    @staticmethod
    def toml_config() -> dict[str, object]: ...
    @staticmethod
    def file_config() -> configparser.ConfigParser:
        """Return any file configuration discovered"""
        ...

_cfg: FileConfig
program: object

def cc(
    paths: Sequence[str],
    min: str = ...,
    max: str = ...,
    show_complexity: bool = ...,
    average: bool = ...,
    exclude: str | None = ...,
    ignore: str | None = ...,
    order: str = ...,
    json: bool = ...,
    no_assert: bool = ...,
    show_closures: bool = ...,
    total_average: bool = ...,
    xml: bool = ...,
    md: bool = ...,
    codeclimate: bool = ...,
    output_file: str | None = ...,
    include_ipynb: bool = ...,
    ipynb_cells: bool = ...,
) -> None:
    """Analyze the given Python modules and compute Cyclomatic
    Complexity (CC).

    The output can be filtered using the *min* and *max* flags. In addition
    to that, by default complexity score is not displayed.

    :param paths: The paths where to find modules or packages to analyze. More
        than one path is allowed.
    :param -n, --min <str>: The minimum complexity to display (default to A).
    :param -x, --max <str>: The maximum complexity to display (default to F).
    :param -e, --exclude <str>: Exclude files only when their path matches one
        of these glob patterns. Usually needs quoting at the command line.
    :param -i, --ignore <str>: Ignore directories when their name matches one
        of these glob patterns: radon won't even descend into them. By default,
        hidden directories (starting with '.') are ignored.
    :param -s, --show-complexity: Whether or not to show the actual complexity
        score together with the A-F rank. Default to False.
    :param -a, --average: If True, at the end of the analysis display the
        average complexity. Default to False.
    :param --total-average: Like `-a, --average`, but it is not influenced by
        `min` and `max`. Every analyzed block is counted, no matter whether it
        is displayed or not.
    :param -o, --order <str>: The ordering function. Can be SCORE, LINES or
        ALPHA.
    :param -j, --json: Format results in JSON.
    :param --xml: Format results in XML (compatible with CCM).
    :param --md: Format results in Markdown.
    :param --codeclimate: Format results for Code Climate.
    :param --no-assert: Do not count `assert` statements when computing
        complexity.
    :param --show-closures: Add closures/inner classes to the output.
    :param -O, --output-file <str>: The output file (default to stdout).
    :param --include-ipynb: Include IPython Notebook files
    :param --ipynb-cells: Include reports for individual IPYNB cells
    """
    ...

def raw(
    paths: Sequence[str],
    exclude: str | None = ...,
    ignore: str | None = ...,
    summary: bool = ...,
    json: bool = ...,
    output_file: str | None = ...,
    include_ipynb: bool = ...,
    ipynb_cells: bool = ...,
) -> None:
    """Analyze the given Python modules and compute raw metrics.

    :param paths: The paths where to find modules or packages to analyze. More
        than one path is allowed.
    :param -e, --exclude <str>: Exclude files only when their path matches one
        of these glob patterns. Usually needs quoting at the command line.
    :param -i, --ignore <str>: Ignore directories when their name matches one
        of these glob patterns: radon won't even descend into them. By default,
        hidden directories (starting with '.') are ignored.
    :param -s, --summary:  If given, at the end of the analysis display the
        summary of the gathered metrics. Default to False.
    :param -j, --json: Format results in JSON. Note that the JSON export does
        not include the summary (enabled with `-s, --summary`).
    :param -O, --output-file <str>: The output file (default to stdout).
    :param --include-ipynb: Include IPython Notebook files
    :param --ipynb-cells: Include reports for individual IPYNB cells
    """
    ...

def mi(
    paths: Sequence[str],
    min: str = ...,
    max: str = ...,
    multi: bool = ...,
    exclude: str | None = ...,
    ignore: str | None = ...,
    show: bool = ...,
    json: bool = ...,
    sort: bool = ...,
    output_file: str | None = ...,
    include_ipynb: bool = ...,
    ipynb_cells: bool = ...,
) -> None:
    """Analyze the given Python modules and compute the Maintainability Index.

    The maintainability index (MI) is a compound metric, with the primary aim
    being to determine how easy it will be to maintain a particular body of
    code.

    :param paths: The paths where to find modules or packages to analyze. More
        than one path is allowed.
    :param -n, --min <str>: The minimum MI to display (default to A).
    :param -x, --max <str>: The maximum MI to display (default to C).
    :param -e, --exclude <str>: Exclude files only when their path matches one
        of these glob patterns. Usually needs quoting at the command line.
    :param -i, --ignore <str>: Ignore directories when their name matches one
        of these glob patterns: radon won't even descend into them. By default,
        hidden directories (starting with '.') are ignored.
    :param -m, --multi: If given, multiline strings are not counted as
        comments.
    :param -s, --show: If given, the actual MI value is shown in results.
    :param -j, --json: Format results in JSON.
    :param --sort: If given, results are sorted in ascending order.
    :param -O, --output-file <str>: The output file (default to stdout).
    :param --include-ipynb: Include IPython Notebook files
    :param --ipynb-cells: Include reports for individual IPYNB cells
    """
    ...

def hal(
    paths: Sequence[str],
    exclude: str | None = ...,
    ignore: str | None = ...,
    json: bool = ...,
    functions: bool = ...,
    output_file: str | None = ...,
    include_ipynb: bool = ...,
    ipynb_cells: bool = ...,
) -> None:
    """Analyze the given Python modules and compute their Halstead metrics.

    The Halstead metrics are a series of measurements meant to quantitatively
    measure the complexity of code, including the difficulty a programmer would
    have in writing it.

    :param paths: The paths where to find modules or packages to analyze. More
        than one path is allowed.
    :param -e, --exclude <str>: Exclude files only when their path matches one
        of these glob patterns. Usually needs quoting at the command line.
    :param -i, --ignore <str>: Ignore directories when their name matches one
        of these glob patterns: radon won't even descend into them. By default,
        hidden directories (starting with '.') are ignored.
    :param -j, --json: Format results in JSON.
    :param -f, --functions: Analyze files by top-level functions instead of as
        a whole.
    :param -O, --output-file <str>: The output file (default to stdout).
    :param --include-ipynb: Include IPython Notebook files
    :param --ipynb-cells: Include reports for individual IPYNB cells
    """
    ...

class Config:
    """An object holding config values."""

    config_values: dict[str, object]

    def __init__(self, **kwargs: object) -> None:
        """Configuration values are passed as keyword parameters."""
        ...

    def __getattr__(self, attr: str) -> object:
        """If an attribute is not found inside the config values, the request
        is handed to `__getattribute__`.
        """
        ...

    def __eq__(self, other: object) -> bool:
        """Two Config objects are equals if their contents are equal."""
        ...

    @classmethod
    def from_function(cls, func: Callable[..., object]) -> Config:
        """Construct a Config object from a function's defaults."""
        ...

def log_result(harvester: Harvester, **kwargs: object) -> None:
    """Log the results of an :class:`~radon.cli.harvest.Harvester object.

    Keywords parameters determine how the results are formatted. If *json* is
    `True`, then `harvester.as_json()` is called. If *xml* is `True`, then
    `harvester.as_xml()` is called. If *codeclimate* is True, then
    `harvester.as_codeclimate_issues()` is called.
    Otherwise, `harvester.to_terminal()` is executed and `kwargs` is directly
    passed to the :func:`~radon.cli.log` function.
    """
    ...

def log(msg: str, *args: object, **kwargs: object) -> None:
    """Log a message, passing *args* to the strings' `format()` method.

    *indent*, if present as a keyword argument, specifies the indent level, so
    that `indent=0` will log normally, `indent=1` will indent the message by 4
    spaces, &c..
    *noformat*, if present and True, will cause the message not to be formatted
    in any way.
    """
    ...

def log_list(lst: Iterable[str], *args: object, **kwargs: object) -> None:
    """Log an entire list, line by line. All the arguments are directly passed
    to :func:`~radon.cli.log`.
    """
    ...

def log_error(msg: str, *args: object, **kwargs: object) -> None:
    """Log an error message. Arguments are the same as log()."""
    ...

@contextmanager
def outstream(outfile: str | None = ...) -> Generator[object]:
    """Encapsulate output stream creation as a context manager"""
    ...
