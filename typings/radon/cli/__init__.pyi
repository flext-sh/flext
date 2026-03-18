import configparser
from collections.abc import Callable, Generator, Iterable, Sequence
from contextlib import contextmanager
from typing import TypeVar, override

from radon.cli.harvest import Harvester

"""In this module the CLI interface is created."""

TOMLLIB_PRESENT: bool
CONFIG_SECTION_NAME: str

T = TypeVar("T")

class FileConfig:
    file_cfg: configparser.ConfigParser

    def __init__(self) -> None: ...
    def get_value(self, key: str, type: type[T], default: T) -> T: ...
    @staticmethod
    def toml_config() -> dict[str, object]: ...
    @staticmethod
    def file_config() -> configparser.ConfigParser: ...

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
) -> None: ...
def raw(
    paths: Sequence[str],
    exclude: str | None = ...,
    ignore: str | None = ...,
    summary: bool = ...,
    json: bool = ...,
    output_file: str | None = ...,
    include_ipynb: bool = ...,
    ipynb_cells: bool = ...,
) -> None: ...
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
) -> None: ...
def hal(
    paths: Sequence[str],
    exclude: str | None = ...,
    ignore: str | None = ...,
    json: bool = ...,
    functions: bool = ...,
    output_file: str | None = ...,
    include_ipynb: bool = ...,
    ipynb_cells: bool = ...,
) -> None: ...

class Config:
    config_values: dict[str, object]

    def __init__(self, **kwargs: object) -> None: ...
    def __getattr__(self, attr: str) -> object: ...
    @override
    def __eq__(self, other: object) -> bool: ...
    @classmethod
    def from_function(cls, func: Callable[..., object]) -> Config: ...

def log_result(harvester: Harvester, **kwargs: object) -> None: ...
def log(msg: str, *args: object, **kwargs: object) -> None: ...
def log_list(lst: Iterable[str], *args: object, **kwargs: object) -> None: ...
def log_error(msg: str, *args: object, **kwargs: object) -> None: ...
@contextmanager
def outstream(outfile: str | None = ...) -> Generator[object]: ...
