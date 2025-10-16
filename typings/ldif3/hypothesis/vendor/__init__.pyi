from collections.abc import Callable, Generator, Iterable, Sequence
from contextlib import contextmanager
from io import TextIOBase
from typing import TYPE_CHECKING, Any, TypeVar

from hypothesis.control import BuildContext

"""
Python advanced pretty printer.  This pretty printer is intended to
replace the old `pprint` python module which does not allow developers
to provide their own pretty print callbacks.
This module is based on ruby's `prettyprint.rb` library by `Tanaka Akira`.
Example Usage
-------------
To get a string of the output use `pretty`::
    from pretty import pretty
    string = pretty(complex_object)
Extending
---------
The pretty library allows developers to add pretty printing rules for their
own objects.  This process is straightforward.  All you have to do is to
add a `_repr_pretty_` method to your object and call the methods on the
pretty printer passed::
    class MyObject(object):
        def _repr_pretty_(self, p, cycle):
            ...
Here is an example implementation of a `_repr_pretty_` method for a list
subclass::
    class MyList(list):
        def _repr_pretty_(self, p, cycle):
            if cycle:
                p.text('MyList(...)')
            else:
                with p.group(8, 'MyList([', '])'):
                    for idx, item in enumerate(self):
                        if idx:
                            p.text(',')
                            p.breakable()
                        p.pretty(item)
The `cycle` parameter is `True` if pretty detected a cycle.  You *have* to
react to that or the result is an infinite loop.  `p.text()` just adds
non breaking text to the output, `p.breakable()` either adds a whitespace
or breaks here.  If you pass it an argument it's used instead of the
default space.  `p.pretty` prettyprints another object using the pretty print
method.
The first parameter to the `group` function specifies the extra indentation
of the next line.  In this example the next item will either be on the same
line (if the items are short enough) or aligned with the right edge of the
opening bracket of `MyList`.
If you just want to indent something you can use the group function
without open / close parameters.  You can also use this code::
    with p.indent(2):
        ...
Inheritance diagram:
.. inheritance-diagram:: IPython.lib.pretty
   :parts: 3
:copyright: 2007 by Armin Ronacher.
            Portions (c) 2009 by Robert Kern.
:license: BSD License.
"""
if TYPE_CHECKING: ...
T = TypeVar("T")
type PrettyPrintFunction = Callable[[Any, RepresentationPrinter, bool], None]
__all__ = ["IDKey", "RepresentationPrinter", "pretty"]

def pretty(obj: object) -> str: ...

class IDKey:
    def __init__(self, value: object) -> None: ...
    def __hash__(self) -> int: ...
    def __eq__(self, __o: object) -> bool: ...

class RepresentationPrinter:
    def __init__(
        self, output: TextIOBase | None = ..., *, context: BuildContext | None = ...
    ) -> None: ...
    def pretty(self, obj: object) -> None: ...
    def text(self, obj: str) -> None: ...
    def breakable(self, sep: str = ...) -> None: ...
    def break_(self) -> None: ...
    @contextmanager
    def indent(self, indent: int) -> Generator[None]: ...
    @contextmanager
    def group(
        self, indent: int = ..., open: str = ..., close: str = ...
    ) -> Generator[None]: ...
    def begin_group(self, indent: int = ..., open: str = ...) -> None: ...
    def end_group(self, dedent: int = ..., close: str = ...) -> None: ...
    def flush(self) -> None: ...
    def getvalue(self) -> str: ...
    def maybe_repr_known_object_as_call(
        self,
        obj: object,
        cycle: bool,
        name: str,
        args: Sequence[object],
        kwargs: dict[str, object],
    ) -> None: ...
    def repr_call(
        self,
        func_name: str,
        args: Sequence[object],
        kwargs: dict[str, object],
        *,
        force_split: bool | None = ...,
        arg_slices: dict[str, tuple[int, int]] | None = ...,
        leading_comment: str | None = ...,
        avoid_realization: bool = ...,
    ) -> None: ...

class Printable:
    def output(self, stream: TextIOBase, output_width: int) -> int: ...

class Text(Printable):
    def __init__(self) -> None: ...
    def output(self, stream: TextIOBase, output_width: int) -> int: ...
    def add(self, obj: str, width: int) -> None: ...

class Breakable(Printable):
    def __init__(self, seq: str, width: int, pretty: RepresentationPrinter) -> None: ...
    def output(self, stream: TextIOBase, output_width: int) -> int: ...

class Group(Printable):
    def __init__(self, depth: int) -> None: ...

class GroupQueue:
    def __init__(self, *groups: Group) -> None: ...
    def enq(self, group: Group) -> None: ...
    def deq(self) -> Group | None: ...
    def remove(self, group: Group) -> None: ...

def get_class_name(cls: type[object]) -> str: ...
def pprint_fields(
    obj: object, p: RepresentationPrinter, cycle: bool, fields: Iterable[str]
) -> None: ...

_type_pprinters: dict[type, PrettyPrintFunction] = ...
_deferred_type_pprinters: dict[tuple[str, str], PrettyPrintFunction] = ...

def for_type_by_name(
    type_module: str, type_name: str, func: PrettyPrintFunction
) -> PrettyPrintFunction | None: ...

_singleton_pprinters: dict[int, PrettyPrintFunction] = ...

class _ReprDots: ...
