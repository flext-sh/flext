from typing import ClassVar

from sqlalchemy.dialects.postgresql.array import (
    ARRAY as ARRAY,
    All as All,
    Any as Any,
    array as array,
)
from sqlalchemy.dialects.postgresql.dml import Insert as Insert, insert as insert
from sqlalchemy.dialects.postgresql.ext import (
    ExcludeConstraint as ExcludeConstraint,
    aggregate_order_by as aggregate_order_by,
    array_agg as array_agg,
)
from sqlalchemy.dialects.postgresql.hstore import HSTORE as HSTORE, hstore as hstore
from sqlalchemy.dialects.postgresql.json import (
    JSON as JSON,
    JSONB as JSONB,
    JSONPATH as JSONPATH,
)
from sqlalchemy.dialects.postgresql.named_types import (
    DOMAIN as DOMAIN,
    ENUM as ENUM,
    CreateDomainType as CreateDomainType,
    CreateEnumType as CreateEnumType,
    DropDomainType as DropDomainType,
    DropEnumType as DropEnumType,
    NamedType as NamedType,
)
from sqlalchemy.dialects.postgresql.psycopg2 import dialect as dialect
from sqlalchemy.dialects.postgresql.ranges import (
    DATEMULTIRANGE as DATEMULTIRANGE,
    DATERANGE as DATERANGE,
    INT4MULTIRANGE as INT4MULTIRANGE,
    INT4RANGE as INT4RANGE,
    INT8MULTIRANGE as INT8MULTIRANGE,
    INT8RANGE as INT8RANGE,
    NUMMULTIRANGE as NUMMULTIRANGE,
    NUMRANGE as NUMRANGE,
    TSMULTIRANGE as TSMULTIRANGE,
    TSRANGE as TSRANGE,
    TSTZMULTIRANGE as TSTZMULTIRANGE,
    TSTZRANGE as TSTZRANGE,
    Range as Range,
)
from sqlalchemy.dialects.postgresql.types import (
    BIT as BIT,
    BYTEA as BYTEA,
    CIDR as CIDR,
    CITEXT as CITEXT,
    INET as INET,
    INTERVAL as INTERVAL,
    MACADDR as MACADDR,
    MACADDR8 as MACADDR8,
    MONEY as MONEY,
    OID as OID,
    REGCLASS as REGCLASS,
    REGCONFIG as REGCONFIG,
    TIME as TIME,
    TIMESTAMP as TIMESTAMP,
    TSQUERY as TSQUERY,
    TSVECTOR as TSVECTOR,
)
from sqlalchemy.sql.sqltypes import (
    BIGINT as BIGINT,
    BOOLEAN as BOOLEAN,
    CHAR as CHAR,
    DATE as DATE,
    DOUBLE_PRECISION as DOUBLE_PRECISION,
    FLOAT as FLOAT,
    INTEGER as INTEGER,
    NUMERIC as NUMERIC,
    REAL as REAL,
    SMALLINT as SMALLINT,
    TEXT as TEXT,
    UUID as UUID,
    VARCHAR as VARCHAR,
)

from . import (
    _psycopg_common as _psycopg_common,
    asyncpg as asyncpg,
    base as base,
    dml as dml,
    ext as ext,
    json as json,
    named_types as named_types,
    operators as operators,
    pg8000 as pg8000,
    pg_catalog as pg_catalog,
    psycopg as psycopg,
    psycopg2 as psycopg2,
    psycopg2cffi as psycopg2cffi,
    ranges as ranges,
    types as types,
)

__all__ = ['ARRAY', 'BIGINT', 'BIT', 'BOOLEAN', 'BYTEA', 'CHAR', 'CIDR', 'CITEXT', 'DATE', 'DATEMULTIRANGE', 'DATERANGE', 'DOMAIN', 'DOUBLE_PRECISION', 'ENUM', 'FLOAT', 'HSTORE', 'INET', 'INT4MULTIRANGE', 'INT4RANGE', 'INT8MULTIRANGE', 'INT8RANGE', 'INTEGER', 'INTERVAL', 'JSON', 'JSONB', 'JSONPATH', 'MACADDR', 'MACADDR8', 'MONEY', 'NUMERIC', 'NUMMULTIRANGE', 'NUMRANGE', 'OID', 'REAL', 'REGCLASS', 'REGCONFIG', 'SMALLINT', 'TEXT', 'TIME', 'TIMESTAMP', 'TSMULTIRANGE', 'TSQUERY', 'TSRANGE', 'TSTZMULTIRANGE', 'TSTZRANGE', 'TSVECTOR', 'UUID', 'VARCHAR', 'All', 'Any', 'CreateDomainType', 'CreateEnumType', 'DropDomainType', 'DropEnumType', 'ExcludeConstraint', 'Insert', 'NamedType', 'Range', 'aggregate_order_by', 'array', 'array_agg', 'dialect', 'hstore', 'insert']

class psycopg_async(module):
    dialect: ClassVar[type[psycopg.PGDialectAsync_psycopg]] = ...

# Names in __all__ with no definition:
#   ARRAY
#   All
#   Any
#   BIGINT
#   BIT
#   BOOLEAN
#   BYTEA
#   CHAR
#   CIDR
#   CITEXT
#   CreateDomainType
#   CreateEnumType
#   DATE
#   DATEMULTIRANGE
#   DATERANGE
#   DOMAIN
#   DOUBLE_PRECISION
#   DropDomainType
#   DropEnumType
#   ENUM
#   ExcludeConstraint
#   FLOAT
#   HSTORE
#   INET
#   INT4MULTIRANGE
#   INT4RANGE
#   INT8MULTIRANGE
#   INT8RANGE
#   INTEGER
#   INTERVAL
#   Insert
#   JSON
#   JSONB
#   JSONPATH
#   MACADDR
#   MACADDR8
#   MONEY
#   NUMERIC
#   NUMMULTIRANGE
#   NUMRANGE
#   NamedType
#   OID
#   REAL
#   REGCLASS
#   REGCONFIG
#   Range
#   SMALLINT
#   TEXT
#   TIME
#   TIMESTAMP
#   TSMULTIRANGE
#   TSQUERY
#   TSRANGE
#   TSTZMULTIRANGE
#   TSTZRANGE
#   TSVECTOR
#   TSVECTOR
#   UUID
#   VARCHAR
#   aggregate_order_by
#   array
#   array_agg
#   dialect
#   hstore
#   insert
