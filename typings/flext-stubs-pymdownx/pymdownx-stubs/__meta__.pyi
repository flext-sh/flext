# @flext-generated: typing-stubs

from collections import namedtuple
from typing import Self

"""Meta related things."""
RE_VER = ...
REL_MAP = ...
DEV_STATUS = ...
PRE_REL_MAP = ...

class Version(
    namedtuple("Version", ["major", "minor", "micro", "release", "pre", "post", "dev"])
):
    def __new__(
        cls,
        major: int,
        minor: int,
        micro: int,
        release: str = ...,
        pre: int = ...,
        post: int = ...,
        dev: int = ...,
    ) -> Self: ...

def parse_version(ver: str) -> Version: ...

__version_info__ = ...
__version__ = ...
