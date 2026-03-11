from rich.console import RenderResult
from rich.console import ConsoleOptions
from typings.generated.rich.console import ConsoleOptions
from rich import Console
from typings.generated.rich.console import Console
from rich.console import Console
from rich.console import RenderableType
import typing

import rich.box
import rich.jupyter
from rich.measure import Measurement

TYPE_CHECKING: bool

class Panel(rich.jupyter.JupyterMixin):
    def __init__(self, renderable: RenderableType, box: rich.box.Box = ..., *, title=..., title_align: typing.Literal = ..., subtitle=..., subtitle_align: typing.Literal = ..., safe_box=..., expand: bool = ..., style=..., border_style=..., width=..., height=..., padding=..., highlight: bool = ...) -> None: ...
    @classmethod
    def fit(cls, renderable: RenderableType, box: rich.box.Box = ..., *, title=..., title_align: typing.Literal = ..., subtitle=..., subtitle_align: typing.Literal = ..., safe_box=..., style=..., border_style=..., width=..., height=..., padding=..., highlight: bool = ...) -> Panel: ...
    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult: ...
    def __rich_measure__(self, console: Console, options: ConsoleOptions) -> Measurement: ...
