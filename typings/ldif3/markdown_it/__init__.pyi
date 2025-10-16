from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypedDict, TypeVar

from markdown_it import MarkdownIt

from .utils import EnvType

"""
class Ruler

Helper class, used by [[MarkdownIt#core]], [[MarkdownIt#block]] and
[[MarkdownIt#inline]] to manage sequences of functions (rules):

- keep rules in defined order
- assign the name to each rule
- enable/disable rules
- add/replace rules
- allow assign rules to additional named chains (in the same)
- caching lists of active rules

You will not need use this class directly until write plugins. For simple
rules control use [[MarkdownIt.disable]], [[MarkdownIt.enable]] and
[[MarkdownIt.use]].
"""
if TYPE_CHECKING: ...

class StateBase:
    def __init__(self, src: str, md: MarkdownIt, env: EnvType) -> None: ...
    @property
    def src(self) -> str: ...
    @src.setter
    def src(self, value: str) -> None: ...
    @property
    def srcCharCode(self) -> tuple[int, ...]: ...

class RuleOptionsType(TypedDict, total=False):
    alt: list[str]

RuleFuncTv = TypeVar("RuleFuncTv")

@dataclass(slots=True)
class Rule[RuleFuncTv]:
    name: str
    enabled: bool
    fn: RuleFuncTv = ...
    alt: list[str]

class Ruler[RuleFuncTv]:
    def __init__(self) -> None: ...
    def __find__(self, name: str) -> int: ...
    def __compile__(self) -> None: ...
    def at(
        self, ruleName: str, fn: RuleFuncTv, options: RuleOptionsType | None = ...
    ) -> None: ...
    def before(
        self,
        beforeName: str,
        ruleName: str,
        fn: RuleFuncTv,
        options: RuleOptionsType | None = ...,
    ) -> None: ...
    def after(
        self,
        afterName: str,
        ruleName: str,
        fn: RuleFuncTv,
        options: RuleOptionsType | None = ...,
    ) -> None: ...
    def push(
        self, ruleName: str, fn: RuleFuncTv, options: RuleOptionsType | None = ...
    ) -> None: ...
    def enable(
        self, names: str | Iterable[str], ignoreInvalid: bool = ...
    ) -> list[str]: ...
    def enableOnly(
        self, names: str | Iterable[str], ignoreInvalid: bool = ...
    ) -> list[str]: ...
    def disable(
        self, names: str | Iterable[str], ignoreInvalid: bool = ...
    ) -> list[str]: ...
    def getRules(self, chainName: str = ...) -> list[RuleFuncTv]: ...
    def get_all_rules(self) -> list[str]: ...
    def get_active_rules(self) -> list[str]: ...
