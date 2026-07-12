# PyCharm Integration

PyCharm provides first-class Pydantic support through the bundled
**Pydantic plugin** (enabled by default in recent versions): autocompletion
for model fields, type-checking of model instantiation, and inspections for
`ConfigDict` options.

Setup and feature details are maintained upstream:

- [Pydantic PyCharm integration](https://docs.pydantic.dev/latest/integrations/pycharm/)

FLEXT note: the workspace gates (Ruff, Pyrefly, Pyright, Mypy) are the
authoritative type-check signal — IDE integration is a convenience layer on
top of them, never a replacement.
