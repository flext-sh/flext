from . import base as base, cx_oracle as cx_oracle, dictionary as dictionary, oracledb as oracledb, types as types, vector as vector
from sqlalchemy.dialects.oracle.cx_oracle import dialect as dialect
from sqlalchemy.dialects.oracle.types import BFILE as BFILE, BINARY_DOUBLE as BINARY_DOUBLE, BINARY_FLOAT as BINARY_FLOAT, DATE as DATE, FLOAT as FLOAT, INTERVAL as INTERVAL, LONG as LONG, NCLOB as NCLOB, NUMBER as NUMBER, RAW as RAW, ROWID as ROWID, TIMESTAMP as TIMESTAMP, VARCHAR2 as VARCHAR2
from sqlalchemy.dialects.oracle.vector import SparseVector as SparseVector, VECTOR as VECTOR, VectorDistanceType as VectorDistanceType, VectorIndexConfig as VectorIndexConfig, VectorIndexType as VectorIndexType, VectorStorageFormat as VectorStorageFormat, VectorStorageType as VectorStorageType
from sqlalchemy.sql.sqltypes import BLOB as BLOB, CHAR as CHAR, CLOB as CLOB, DOUBLE_PRECISION as DOUBLE_PRECISION, NCHAR as NCHAR, NVARCHAR as NVARCHAR, NVARCHAR2 as NVARCHAR2, REAL as REAL, VARCHAR as VARCHAR
from typing import ClassVar

__all__ = ['VARCHAR', 'NVARCHAR', 'CHAR', 'NCHAR', 'DATE', 'NUMBER', 'BLOB', 'BFILE', 'CLOB', 'NCLOB', 'TIMESTAMP', 'RAW', 'FLOAT', 'DOUBLE_PRECISION', 'BINARY_DOUBLE', 'BINARY_FLOAT', 'LONG', 'dialect', 'INTERVAL', 'VARCHAR2', 'NVARCHAR2', 'ROWID', 'REAL', 'VECTOR', 'VectorDistanceType', 'VectorIndexType', 'VectorIndexConfig', 'VectorStorageFormat', 'VectorStorageType', 'SparseVector']

class oracledb_async(module):
    dialect: ClassVar[type[oracledb.OracleDialectAsync_oracledb]] = ...

# Names in __all__ with no definition:
#   BFILE
#   BINARY_DOUBLE
#   BINARY_FLOAT
#   BLOB
#   CHAR
#   CLOB
#   DATE
#   DOUBLE_PRECISION
#   FLOAT
#   INTERVAL
#   LONG
#   NCHAR
#   NCLOB
#   NUMBER
#   NVARCHAR
#   NVARCHAR2
#   RAW
#   REAL
#   ROWID
#   SparseVector
#   TIMESTAMP
#   VARCHAR
#   VARCHAR2
#   VECTOR
#   VectorDistanceType
#   VectorIndexConfig
#   VectorIndexType
#   VectorStorageFormat
#   VectorStorageType
#   dialect
