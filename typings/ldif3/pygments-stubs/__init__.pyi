from typing import Any, overload

class Formatter[T: (str, bytes)]:
    name: Any
    aliases: Any
    filenames: Any
    unicodeoutput: bool
    style: Any
    full: Any
    title: Any
    encoding: Any
    options: Any
    @overload
    def __init__(
        self: Formatter[str],
        *,
        encoding: None = ...,
        outencoding: None = ...,
        **options,
    ) -> None: ...
    @overload
    def __init__(
        self: Formatter[bytes], *, encoding: str, outencoding: None = ..., **options
    ) -> None: ...
    @overload
    def __init__(
        self: Formatter[bytes], *, encoding: None = ..., outencoding: str, **options
    ) -> None: ...
    def get_style_defs(self, arg: str = ...): ...
    def format(self, tokensource, outfile): ...
