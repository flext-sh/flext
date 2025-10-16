import datetime as dt

from hypothesis import strategies as st
from hypothesis.strategies._internal.utils import cacheable, defines_strategy

"""
This module provides :pypi:`pytz` timezones.

If you are unable to use the stdlib :mod:`zoneinfo` module, e.g. via the
:func:`hypothesis.strategies.timezones` strategy, you can use this
strategy with :py:func:`hypothesis.strategies.datetimes` and
:py:func:`hypothesis.strategies.times` to produce timezone-aware values.

.. warning::

    Since :mod:`zoneinfo` was added in Python 3.9, this extra
    is deprecated.  We intend to remove it after libraries
    such as Pandas and Django complete their own migrations.
"""
__all__ = ["timezones"]

@cacheable
@defines_strategy()
def timezones() -> st.SearchStrategy[dt.tzinfo]: ...
