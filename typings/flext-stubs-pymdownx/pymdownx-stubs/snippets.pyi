# @flext-generated: typing-stubs

import functools

from markdown import Extension
from markdown.preprocessors import Preprocessor

"""
Snippet ---8<---.

pymdownx.snippet
Inject snippets

MIT license.

Copyright (c) 2017 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
MI = ...
DEFAULT_URL_SIZE = ...
DEFAULT_URL_TIMEOUT = ...
DEFAULT_URL_REQUEST_HEADERS = ...
DEFAULT_MAX_RETRIES = ...
DEFAULT_BACKOFF_FACTOR = ...

class SnippetMissingError(Exception): ...

class SnippetPreprocessor(Preprocessor):
    RE_ALL_SNIPPETS = ...
    RE_SNIPPET = ...
    RE_SNIPPET_SECTION = ...
    RE_SNIPPET_FILE = ...
    def __init__(self, config, md) -> None: ...
    def extract_section(self, section, lines):  # -> list[str]:

        ...
    def dedent(self, lines):  # -> list[str]:

        ...
    def get_snippet_path(self, path):  # -> str | None:

        ...
    @functools.lru_cache
    def download(self, url):  # -> list[str] | list[Any]:

        ...
    def parse_snippets(self, lines, file_name=..., is_url=..., is_section=...): ...
    def run(self, lines): ...

class SnippetExtension(Extension):
    def __init__(self, *args, **kwargs) -> None: ...
    def extendMarkdown(self, md):  # -> None:

        ...
    def reset(self):  # -> None:

        ...

def makeExtension(*args, **kwargs):  # -> SnippetExtension:

    ...
