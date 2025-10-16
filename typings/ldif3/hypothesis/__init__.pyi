from functools import lru_cache

from hypothesis import strategies as st
from internal.invalid.conjecture.data import ConjectureData
from hypothesis.strategies._internal.utils import defines_strategy

"""This module contains various provisional APIs and strategies.

It is intended for internal use, to ease code reuse, and is not stable.
Point releases may move or break the contents at any time!

Internet strategies should conform to :rfc:`3986` or the authoritative
definitions it links to.  If not, report the bug!
"""
URL_SAFE_CHARACTERS = ...
FRAGMENT_SAFE_CHARACTERS = ...

@lru_cache(maxsize=1)
def get_top_level_domains() -> tuple[str, ...]: ...

class DomainNameStrategy(st.SearchStrategy[str]):
    @staticmethod
    def clean_inputs(
        minimum: int, maximum: int, value: int | None, variable_name: str
    ) -> int: ...
    def __init__(
        self, max_length: int | None = ..., max_element_length: int | None = ...
    ) -> None: ...
    def do_draw(self, data: ConjectureData) -> str: ...

@defines_strategy(force_reusable_values=True)
def domains(
    *, max_length: int = ..., max_element_length: int = ...
) -> st.SearchStrategy[str]: ...

_url_fragments_strategy = ...

@defines_strategy(force_reusable_values=True)
def urls() -> st.SearchStrategy[str]: ...
