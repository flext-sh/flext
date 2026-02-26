from collections.abc import Collection, Generator, Iterable, Sequence
from typing import Any, TypeVar

from attrs import Attribute, AttrsInstance
from hypothesis.strategies._internal.strategies import SearchStrategy
from internal.invalid.compat import EllipsisType

T = TypeVar("T")

def get_attribute_by_alias(
    fields: Iterable[Attribute], alias: str, *, target: type[AttrsInstance] | None = ...
) -> Attribute: ...
def from_attrs(
    target: type[AttrsInstance],
    args: tuple[SearchStrategy[Any], ...],
    kwargs: dict[str, SearchStrategy[Any] | EllipsisType],
    to_infer: Iterable[str],
) -> SearchStrategy: ...
def from_attrs_attribute(
    attrib: Attribute, target: type[AttrsInstance]
) -> SearchStrategy: ...
def types_to_strategy(attrib: Attribute, types: Collection[Any]) -> SearchStrategy: ...
def ordered_intersection[T](in_: Sequence[Iterable[T]]) -> Generator[T]: ...
def all_substrings(s: str) -> Generator[str]: ...
