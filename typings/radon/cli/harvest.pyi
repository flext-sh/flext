"""Type stubs for radon.cli.harvest module."""

from collections.abc import Generator, Iterable, Sequence

from radon.metrics import Halstead, HalsteadReport
from radon.visitors import Class, Function

"""This module holds the base Harvester class and all its subclassess."""

SUPPORTS_IPYNB: bool

type HarvesterResult = tuple[str, object]
type TerminalLine = tuple[str | list[str], tuple[object, ...], dict[str, object]]

class Harvester:
    """Base class defining the interface of a Harvester object.

    A Harvester has the following lifecycle:

    1. **Initialization**: `h = Harvester(paths, config)`

    2. **Execution**: `r = h.results`. `results` holds an iterable object.
       The first time `results` is accessed, `h.run()` is called. This method
       should not be subclassed. Instead, the :meth:`gobble` method should be
       implemented.

    3. **Reporting**: the methods *as_json* and *as_xml* return a string
       with the corrisponding format. The method *to_terminal* is a generator
       that yields the lines to be printed in the terminal.

    This class is meant to be subclasses and cannot be used directly, since
    the methods :meth:`gobble`, :meth:`as_xml` and :meth:`to_terminal` are
    not implemented.
    """

    paths: Sequence[str]
    config: object
    _results: list[HarvesterResult]

    def __init__(self, paths: Sequence[str], config: object) -> None:
        """Initialize the Harvester.

        *paths* is a list of paths to analyze.
        *config* is a :class:`~radon.cli.Config` object holding the
        configuration values specific to the Harvester.
        """
        ...

    def _iter_filenames(self) -> Generator[str]:
        """A wrapper around :func:`~radon.cli.tools.iter_filenames`."""
        ...

    def gobble(self, fobj: object) -> object:
        """Subclasses must implement this method to define behavior.

        This method is called for every file to analyze. *fobj* is the file
        object. This method should return the results from the analysis,
        preferably a dictionary.
        """
        ...

    def run(self) -> Generator[HarvesterResult]:
        """Start the analysis. For every file, this method calls the
        :meth:`gobble` method. Results are yielded as tuple:
        ``(filename, analysis_results)``.
        """
        ...

    @property
    def results(
        self,
    ) -> list[HarvesterResult] | Generator[HarvesterResult]:
        """This property holds the results of the analysis.

        The first time it is accessed, an iterator is returned. Its
        elements are cached into a list as it is iterated over. Therefore, if
        `results` is accessed multiple times after the first one, a list will
        be returned.
        """
        ...

    def as_json(self) -> str:
        """Format the results as JSON."""
        ...

    def as_xml(self) -> str:
        """Format the results as XML."""
        ...

    def as_md(self) -> str:
        """Format the results as Markdown."""
        ...

    def as_codeclimate_issues(self) -> list[str]:
        """Format the results as Code Climate issues."""
        ...

    def to_terminal(self) -> Generator[TerminalLine]:
        """Yields tuples representing lines to be printed to a terminal.

        The tuples have the following format: ``(line, args, kwargs)``.
        The line is then formatted with `line.format(*args, **kwargs)`.
        """
        ...

class CCHarvester(Harvester):
    """A class that analyzes Python modules' Cyclomatic Complexity."""

    def gobble(self, fobj: object) -> list[Function | Class]:
        """Analyze the content of the file object."""
        ...

    def _to_dicts(self) -> dict[str, object]:
        """Format the results as a dictionary of dictionaries."""
        ...

    def as_json(self) -> str:
        """Format the results as JSON."""
        ...

    def as_xml(self) -> str:
        """Format the results as XML. This is meant to be compatible with
        Jenkin's CCM plugin. Therefore not all the fields are kept.
        """
        ...

    def as_md(self) -> str:
        """Format the results as Markdown."""
        ...

    def as_codeclimate_issues(self) -> list[str]:
        """Format the result as Code Climate issues."""
        ...

    def to_terminal(self) -> Generator[TerminalLine]:
        """Yield lines to be printed in a terminal."""
        ...

class RawHarvester(Harvester):
    """A class that analyzes Python modules' raw metrics."""

    headers: list[str]

    def gobble(self, fobj: object) -> dict[str, int]:
        """Analyze the content of the file object."""
        ...

    def as_xml(self) -> str:
        """Placeholder method. Currently not implemented."""
        ...

    def to_terminal(self) -> Generator[TerminalLine]:
        """Yield lines to be printed to a terminal."""
        ...

class MIHarvester(Harvester):
    """A class that analyzes Python modules' Maintainability Index."""

    def gobble(self, fobj: object) -> dict[str, float | str]:
        """Analyze the content of the file object."""
        ...

    @property
    def filtered_results(self) -> Generator[tuple[str, dict[str, object]]]:
        """Filter results with respect with their rank."""
        ...

    def _sort(
        self,
        results: Iterable[tuple[str, dict[str, object]]],
    ) -> Iterable[tuple[str, dict[str, object]]]: ...
    def as_json(self) -> str:
        """Format the results as JSON."""
        ...

    def as_xml(self) -> str:
        """Placeholder method. Currently not implemented."""
        ...

    def to_terminal(self) -> Generator[TerminalLine]:
        """Yield lines to be printed to a terminal."""
        ...

class HCHarvester(Harvester):
    """Computes the Halstead Complexity of Python modules."""

    by_function: bool

    def __init__(self, paths: Sequence[str], config: object) -> None: ...
    def gobble(self, fobj: object) -> Halstead:
        """Analyze the content of the file object."""
        ...

    def as_json(self) -> str:
        """Format the results as JSON."""
        ...

    def to_terminal(self) -> Generator[TerminalLine]:
        """Yield lines to be printed to the terminal."""
        ...

    def _to_dicts(self) -> dict[str, dict[str, object]]:
        """Format the results as a dictionary of dictionaries."""
        ...

def hal_report_to_terminal(
    report: HalsteadReport,
    base_indent: int = ...,
) -> Generator[TerminalLine]:
    """Yield lines from the HalsteadReport to print to the terminal."""
    ...
