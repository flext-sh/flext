from typing import TypeVar

_T = TypeVar("_T")

class Factory[T]:
    class Meta:
        model: type | None = None
        django_get_or_create: tuple[str, ...] = ()
        abstract: bool = False
        strategy: str = "create"

    @classmethod
    def create(cls, **kwargs: _T) -> _T: ...
    @classmethod
    def build(cls, **kwargs: _T) -> _T: ...
    @classmethod
    def create_batch(cls, size: int, **kwargs: _T) -> list[_T]: ...
    @classmethod
    def build_batch(cls, size: int, **kwargs: _T) -> list[_T]: ...
