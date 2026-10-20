# @flext-generated: typing-stubs

from markdown import Extension
from markdown.postprocessors import Postprocessor

"""
B64.

An extension for Python Markdown.
Given an absolute base path, this extension searches for image tags,
and if the images are local, will embed the images in base64.

MIT license.

Copyright (c) 2014 - 2017 Isaac Muse <isaacmuse@gmail.com>

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
RE_SLASH_WIN_DRIVE = ...
file_types = ...
RE_TAG_HTML = ...
RE_TAG_LINK_ATTR = ...

def repl_path(m, base_path, root_path, restrict_path=...):  # -> str:

    ...
def repl(m, base_path, root_path, restrict_path=...): ...

class B64Postprocessor(Postprocessor):
    def run(self, text):  # -> str:

        ...

class B64Extension(Extension):
    def __init__(self, *args, **kwargs) -> None: ...
    def extendMarkdown(self, md):  # -> None:

        ...

def makeExtension(*args, **kwargs):  # -> B64Extension:

    ...
