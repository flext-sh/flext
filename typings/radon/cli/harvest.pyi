

from collections.abc import Generator, Iterable, Sequence

from radon.metrics import Halstead, HalsteadReport
from radon.visitors import Class, Function

"""This module holds the base Harvester class and all its subclassess."""

SUPPORTS_IPYNB: bool
MI_RANKS: dict[str, str]
RANKS_COLORS: dict[str, str]
RESET: str

type HarvesterResult = tuple[str, object]
type TerminalLine = tuple[str | list[str], tuple[object, ...], dict[str, object]]

class Harvester:
    

    paths: Sequence[str]
    config: object
    _results: list[HarvesterResult]

    def __init__(self, paths: Sequence[str], config: object) -> None:
        
        ...

    def _iter_filenames(self) -> Generator[str]:
        
        ...

    def gobble(self, fobj: object) -> object:
        
        ...

    def run(self) -> Generator[HarvesterResult]:
        
        ...

    @property
    def results(
        self,
    ) -> list[HarvesterResult] | Generator[HarvesterResult]:
        
        ...

    def as_json(self) -> str:
        
        ...

    def as_xml(self) -> str:
        
        ...

    def as_md(self) -> str:
        
        ...

    def as_codeclimate_issues(self) -> list[str]:
        
        ...

    def to_terminal(self) -> Generator[TerminalLine]:
        
        ...

class CCHarvester(Harvester):
    

    def gobble(self, fobj: object) -> list[Function | Class]:
        
        ...

    def _to_dicts(self) -> dict[str, object]:
        
        ...

    def as_json(self) -> str:
        
        ...

    def as_xml(self) -> str:
        
        ...

    def as_md(self) -> str:
        
        ...

    def as_codeclimate_issues(self) -> list[str]:
        
        ...

    def to_terminal(self) -> Generator[TerminalLine]:
        
        ...

class RawHarvester(Harvester):
    

    headers: list[str]

    def gobble(self, fobj: object) -> dict[str, int]:
        
        ...

    def as_xml(self) -> str:
        
        ...

    def to_terminal(self) -> Generator[TerminalLine]:
        
        ...

class MIHarvester(Harvester):
    

    def gobble(self, fobj: object) -> dict[str, float | str]:
        
        ...

    @property
    def filtered_results(self) -> Generator[tuple[str, dict[str, object]]]:
        
        ...

    def _sort(
        self,
        results: Iterable[tuple[str, dict[str, object]]],
    ) -> Iterable[tuple[str, dict[str, object]]]: ...
    def as_json(self) -> str:
        
        ...

    def as_xml(self) -> str:
        
        ...

    def to_terminal(self) -> Generator[TerminalLine]:
        
        ...

class HCHarvester(Harvester):
    

    by_function: bool

    def __init__(self, paths: Sequence[str], config: object) -> None: ...
    def gobble(self, fobj: object) -> Halstead:
        
        ...

    def as_json(self) -> str:
        
        ...

    def to_terminal(self) -> Generator[TerminalLine]:
        
        ...

    def _to_dicts(self) -> dict[str, dict[str, object]]:
        
        ...

def hal_report_to_terminal(
    report: HalsteadReport,
    base_indent: int = ...,
) -> Generator[TerminalLine]:
    
    ...
