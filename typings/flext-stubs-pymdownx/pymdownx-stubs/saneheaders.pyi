# @flext-generated: typing-stubs

from markdown import Extension
from markdown.blockprocessors import HashHeaderProcessor

"""
Sane headers.

Allow for a header implementation that requires `#` headers to have a space
after the `#` portion. This allows for things like Magiclink issues to work
at the beginning of lines, and potentially other things like tag extensions
etc.
"""
RE_HEADER = ...

class SaneHeadersProcessor(HashHeaderProcessor):
    RE = ...

class SaneHeadersExtension(Extension):
    def extendMarkdown(self, md):  # -> None:

        ...

def makeExtension(*args, **kwargs):  # -> SaneHeadersExtension:

    ...
