from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    type ConfigDict = dict[str, str | list[str]]

def load_config_dict_from_file(filepath: Path) -> ConfigDict | None: ...
def locate_config(
    invocation_dir: Path, args: Iterable[Path]
) -> tuple[Path | None, Path | None, ConfigDict]: ...
def get_common_ancestor(invocation_dir: Path, paths: Iterable[Path]) -> Path: ...
def get_dirs_from_args(args: Iterable[str]) -> list[Path]: ...

CFG_PYTEST_SECTION = ...

def determine_setup(
    *,
    inifile: str | None,
    args: Sequence[str],
    rootdir_cmd_arg: str | None,
    invocation_dir: Path,
) -> tuple[Path, Path | None, ConfigDict]: ...
def is_fs_root(p: Path) -> bool: ...
