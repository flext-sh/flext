# @flext-generated: typing-stubs

from markdown import Extension
from markdown.extensions.attr_list import AttrListTreeprocessor
from markdown.inlinepatterns import InlineProcessor

"""
Progress Bar.

pymdownx.progressbar
Simple plugin to add support for progress bars

```
/* No label */
[==30%]

/* Label */
[==30%  MyLabel]

/* works with attr_list inline style */
[==50/200  MyLabel]{: .additional-class }
```

New line is not required before the progress bar but suggested unless in a table.
Can take percentages and divisions.
Floats are okay.  Numbers must be positive.  This is an experimental extension.
Functionality is subject to change.

Minimum Recommended Styling
(but you could add gloss, candy striping, animation, or anything else):

```
.progress {
    display: block;
    width: 300px;
    margin: 10px 0;
    height: 24px;
    border: 1px solid #ccc;
    -webkit-border-radius: 3px;
    -moz-border-radius: 3px;
    border-radius: 3px;
    background-color: #F8F8F8;
    position: relative;
    box-shadow: inset -1px 1px 3px rgba(0, 0, 0, .1);
}

.progress-label {
    position: absolute;
    text-align: center;
    font-weight: bold;
    width: 100%; margin: 0;
    line-height: 24px;
    color: #333;
    -webkit-font-smoothing: antialiased !important;
    white-space: nowrap;
    overflow: hidden;
}

.progress-bar {
    height: 24px;
    float: left;
    border-right: 1px solid #ccc;
    -webkit-border-radius: 3px;
    -moz-border-radius: 3px;
    border-radius: 3px;
    background-color: #34c2e3;
    box-shadow: inset 0 1px 0px rgba(255, 255, 255, .5);
}

For Level Colors

.progress-100plus .progress-bar {
    background-color: #1ee038;
}

.progress-80plus .progress-bar {
    background-color: #86e01e;
}

.progress-60plus .progress-bar {
    background-color: #f2d31b;
}

.progress-40plus .progress-bar {
    background-color: #f2b01e;
}

.progress-20plus .progress-bar {
    background-color: #f27011;
}

.progress-0plus .progress-bar {
    background-color: #f63a0f;
}
```

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
RE_PROGRESS = ...
CLASS_LEVEL = ...

class ProgressBarTreeProcessor(AttrListTreeprocessor):
    def run(self, elem):  # -> None:

        ...

class ProgressBarPattern(InlineProcessor):
    def __init__(self, pattern, md) -> None: ...
    def create_tag(self, width, label, add_classes, alist):  # -> Element:

        ...
    def handleMatch(self, m, data):  # -> tuple[Element, int, int]:

        ...

class ProgressBarExtension(Extension):
    def __init__(self, *args, **kwargs) -> None: ...
    def extendMarkdown(self, md):  # -> None:

        ...

def makeExtension(*args, **kwargs):  # -> ProgressBarExtension:

    ...
