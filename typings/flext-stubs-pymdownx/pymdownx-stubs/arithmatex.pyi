# @flext-generated: typing-stubs

from markdown import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.inlinepatterns import InlineProcessor

r"""
Arithmatex.

pymdownx.arithmatex
Extension that preserves the following for MathJax use:

```
$Equation$, \(Equation\)

$$
  Display Equations
$$

\[
  Display Equations
\]

\begin{align}
  Display Equations
\end{align}
```

and `$Inline MathJax Equations$`

Inline and display equations are converted to scripts tags. You can optionally generate previews.

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
RE_SMART_DOLLAR_INLINE = ...
RE_DOLLAR_INLINE = ...
RE_BRACKET_INLINE = ...
RE_DOLLAR_BLOCK = ...
RE_TEX_BLOCK = ...
RE_BRACKET_BLOCK = ...

def arithmatex_inline_format(**kwargs):  # -> partial[Element] | None:

    ...
def arithmatex_fenced_format(**kwargs):  # -> partial[str] | partial[Any] | None:

    ...

class InlineArithmatexPattern(InlineProcessor):
    ESCAPED_BSLASH = ...
    def __init__(self, pattern, config) -> None: ...
    def handleMatch(
        self, m, data
    ):  # -> tuple[str | Any, int, int] | tuple[Element, int, int]:

        ...

class BlockArithmatexProcessor(BlockProcessor):
    def __init__(self, pattern, config, md) -> None: ...
    def test(self, parent, block):  # -> bool:

        ...
    def mathjax_output(self, parent, math):  # -> None:

        ...
    def generic_output(self, parent, math):  # -> None:

        ...
    def run(self, parent, blocks):  # -> Literal[True]:

        ...

class ArithmatexExtension(Extension):
    def __init__(self, *args, **kwargs) -> None: ...
    def extendMarkdown(self, md):  # -> None:

        ...

def makeExtension(*args, **kwargs):  # -> ArithmatexExtension:

    ...
