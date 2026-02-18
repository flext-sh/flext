import sqlalchemy.cyextension.immutabledict
from . import _collections as _collections, _concurrency_py3k as _concurrency_py3k, _has_cy as _has_cy, compat as compat, concurrency as concurrency, deprecations as deprecations, langhelpers as langhelpers, preloaded as preloaded, queue as queue, topological as topological, typing as typing

EMPTY_DICT: sqlalchemy.cyextension.immutabledict.immutabledict
EMPTY_SET: frozenset
NONE_SET: frozenset
arm: bool
cpython: bool
freethreading: bool
has_refcount_gc: bool
is64bit: bool
osx: bool
py310: bool
py311: bool
py312: bool
py313: bool
py314: bool
py38: bool
py39: bool
pypy: bool
win32: bool
