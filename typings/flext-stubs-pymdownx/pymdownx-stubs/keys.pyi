# @flext-generated: typing-stubs

from markdown import Extension
from markdown.inlinepatterns import InlineProcessor

"""
Keys.

pymdownx.keys
Markdown extension for keystroke (user keyboard input) formatting.

It wraps the syntax `++key+key+key++` (for individual keystrokes with modifiers)
or `++"string"++` (for continuous keyboard input) into HTML `<kbd>` elements.

If a key is found in the extension's database, its `<kbd>` element gets a matching class.
Common synonyms are included, e.g. `++pg-up++` will match as `++page-up++`.

## Config

If `strict` is `True`, the entire series of keystrokes is wrapped into an outer`<kbd>` element, and then,
each keystroke is wrapped into a separate inner `<kbd>` element, which matches the HTML5 spec.
If `strict` is `False`, an outer `<span>` is used, which matches the practice on Github or StackOverflow.

The resulting `<kbd>` elements are separated by `separator` (`+` by default, can be `''` or something else).

If `camel_case` is `True`, `++PageUp++` will match the same as `++page-up++`.

The database can be extended or modified with the `key_map` dict.

## Examples

### Input

```
Press ++Shift+Alt+PgUp++, type in ++"Hello"++ and press ++Enter++.
```

### Config 1

```
  pymdownx.keys:
    camel_case: true
    strict: false
    separator: '+'
```

### Output 1

```
<p>Press <span class="keys"><kbd class="key-shift">Shift</kbd><span>+</span><kbd
class="key-alt">Alt</kbd><span>+</span><kbd class="key-page-up">Page Up</kbd></span>, type in <span
class="keys"><kbd>Hello</kbd></span> and press <span class="keys"><kbd class="key-enter">Enter</kbd></span>.</p>
```

### Config 2

```
  pymdownx.keys:
    camel_case: true
    strict: true
    separator: ''
```

### Output 2

```
<p>Press <kbd class="keys"><kbd class="key-shift">Shift</kbd><kbd class="key-alt">Alt</kbd><kbd
class="key-page-up">Page Up</kbd></kbd>, type in <kbd class="keys"><kbd>Hello</kbd></kbd> and press <kbd
class="keys"><kbd class="key-enter">Enter</kbd></kbd>.</p>
```

Idea by Adam Twardoch and coded by Isaac Muse.

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
RE_EARLY_KBD = ...
RE_KBD = ...
ESCAPE_RE = ...
UNESCAPED_PLUS = ...
ESCAPED_BSLASH = ...
DOUBLE_BSLASH = ...

class KeysPattern(InlineProcessor):
    def __init__(self, pattern, config, md, early=...) -> None: ...
    def merge(self, x, y): ...
    def normalize(self, key):  # -> LiteralString:

        ...
    def process_key(self, key):  # -> tuple[None, str] | tuple[str, str] | None:

        ...
    def handleMatch(
        self, m, data
    ):  # -> tuple[str | Any, int, int] | tuple[None, None, None] | tuple[Element, int, int]:

        ...

class KeysExtension(Extension):
    def __init__(self, *args, **kwargs) -> None: ...
    def extendMarkdown(self, md):  # -> None:

        ...

def makeExtension(*args, **kwargs):  # -> KeysExtension:

    ...
