from sqlalchemy.sql._typing import _OnlyColumnArgument
from sqlalchemy import Function
from pandas._typing import Function
from weasyprint.css import Function
from sqlalchemy.sql.expression import Function
from weasyprint.css.functions import Function
from typings.radon.visitors import Function
from typings.generated.sqlalchemy.sql.functions import Function
from cssselect.parser import Function
from pyarrow.compute import Function
from pyarrow._compute import Function
from _pytest.python import Function
from sqlalchemy.sql.functions import Function
from sqlalchemy.sql._typing import _OnClauseArgument
from sqlalchemy.sql._typing import _FromClauseArgument
from sqlalchemy import ScalarSelect
from sqlalchemy.sql.expression import ScalarSelect
from sqlalchemy.sql.selectable import ScalarSelect
from sqlalchemy import SelectBase
from sqlalchemy.sql.expression import SelectBase
from sqlalchemy.sql.selectable import SelectBase
from sqlalchemy.engine.result import _TP
from sqlalchemy.engine.row import _TP
from sqlalchemy.ext.asyncio.result import _TP
from sqlalchemy.sql._typing import _TP
from sqlalchemy.sql._typing import _SelectStatementForCompoundArgument
from sqlalchemy import CTE
from sqlalchemy.sql.expression import CTE
from sqlalchemy.sql.selectable import CTE
from sqlalchemy import HasCTE
from sqlalchemy.sql.expression import HasCTE
from sqlalchemy.sql.selectable import HasCTE
from typing import Any, _ColumnsClauseArgument

import roles as roles
from sqlalchemy.sql.elements import ColumnClause
from sqlalchemy.sql.selectable import (
    CompoundSelect,
    Exists,
    FromClause,
    Join,
    LateralFromClause,
    NamedFromClause,
    Select,
    TableClause,
    TableSample,
    Values,
)

TYPE_CHECKING: bool
def alias(selectable: FromClause, name: str | None = ..., flat: bool = ...) -> NamedFromClause: ...
def cte(selectable: HasCTE, name: str | None = ..., recursive: bool = ...) -> CTE: ...
def except_(*selects: _SelectStatementForCompoundArgument[_TP]) -> CompoundSelect[_TP]: ...
def except_all(*selects: _SelectStatementForCompoundArgument[_TP]) -> CompoundSelect[_TP]: ...
def exists(__argument: _ColumnsClauseArgument[Any] | SelectBase | ScalarSelect[Any] | None = ...) -> Exists: ...
def intersect(*selects: _SelectStatementForCompoundArgument[_TP]) -> CompoundSelect[_TP]: ...
def intersect_all(*selects: _SelectStatementForCompoundArgument[_TP]) -> CompoundSelect[_TP]: ...
def join(left: _FromClauseArgument, right: _FromClauseArgument, onclause: _OnClauseArgument | None = ..., isouter: bool = ..., full: bool = ...) -> Join: ...
def lateral(selectable: SelectBase | _FromClauseArgument, name: str | None = ...) -> LateralFromClause: ...
def outerjoin(left: _FromClauseArgument, right: _FromClauseArgument, onclause: _OnClauseArgument | None = ..., full: bool = ...) -> Join: ...
def select(*entities: _ColumnsClauseArgument[Any], **__kw: Any) -> Select[Any]: ...
def table(name: str, *columns: ColumnClause[Any], **kw: Any) -> TableClause: ...
def tablesample(selectable: _FromClauseArgument, sampling: float | Function[Any], name: str | None = ..., seed: roles.ExpressionElementRole[Any] | None = ...) -> TableSample: ...
def union(*selects: _SelectStatementForCompoundArgument[_TP]) -> CompoundSelect[_TP]: ...
def union_all(*selects: _SelectStatementForCompoundArgument[_TP]) -> CompoundSelect[_TP]: ...
def values(*columns: _OnlyColumnArgument[Any], name: str | None = ..., literal_binds: bool = ...) -> Values: ...
