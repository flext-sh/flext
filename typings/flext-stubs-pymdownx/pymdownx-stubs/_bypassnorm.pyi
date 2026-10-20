# @flext-generated: typing-stubs

from markdown import Extension
from markdown.preprocessors import Preprocessor

"""
Bypass whitespace normalization.

pymdownx._bypassnorm

Strips `SOH` and `EOT` characters before whitespace normalization
allowing other extensions to then create preprocessors that stash HTML
with `SOH` and `EOT`  After whitespace normalization, all `SOH` and
`EOT` characters will be converted to the Python Markdown standard
`STX` and `ETX` convention since whitespace normalization usually
strips out the `STX` and `ETX` characters.

Copyright 2014 - 2018 Isaac Muse <isaacmuse@gmail.com>
"""
SOH = ...
EOT = ...

class PreNormalizePreprocessor(Preprocessor):
    def run(self, lines):  # -> list[str]:

        ...

class PostNormalizePreprocessor(Preprocessor):
    def run(self, lines):  # -> list[str]:

        ...

class BypassNormExtension(Extension):
    def __init__(self, *args, **kwargs) -> None: ...
    def extendMarkdown(self, md):  # -> None:

        ...

def makeExtension(*args, **kwargs):  # -> BypassNormExtension:

    ...
