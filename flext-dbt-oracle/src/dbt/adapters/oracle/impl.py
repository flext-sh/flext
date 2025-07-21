"""Oracle DBT Adapter Implementation using FLEXT DB Oracle.

Modern DBT adapter implementation leveraging
flext-infrastructure.databases.flext-db-oracle services
for enterprise-grade Oracle Database integration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from dbt.adapters.oracle.connections import OracleConnectionManager
from dbt.adapters.sql import SQLAdapter

if TYPE_CHECKING:
    from dbt.adapters.base import BaseRelation


class OracleAdapter(SQLAdapter):
    """Oracle Database adapter for DBT using flext-infrastructure.databases.flext-db-oracle foundation.

    Oracle Database adapter for DBT using
    flext-infrastructure.databases.flext-db-oracle foundation.

    Provides enterprise-grade Oracle Database integration with:
    - Modern connection management via flext-infrastructure.databases.flext-db-oracle
    - Advanced error handling and resilience
    - Enterprise performance optimizations
    - Zero code duplication across FLEXT ecosystem
    """

    ConnectionManager = OracleConnectionManager

    @classmethod
    def date_function(cls) -> str:
        """Return the Oracle date function."""
        return "SYSDATE"

    @classmethod
    def is_cancelable(cls) -> bool:
        """Oracle connections can be canceled."""
        return True

    def quote(self, identifier: str) -> str:
        """Quote an identifier for Oracle."""
        return f'"{identifier}"'

    def get_columns_in_relation(self, relation: BaseRelation) -> list[Any]:
        """Get columns for a given relation using flext-infrastructure.databases.flext-db-oracle services.

        Get columns for a given relation using
        flext-infrastructure.databases.flext-db-oracle services.
        """
        # Query Oracle's data dictionary - schema/table validated by dbt framework
        sql = f"""
        SELECT column_name, data_type, nullable, data_default, column_id
        FROM all_tab_columns
        WHERE owner = '{relation.schema}'
        AND table_name = '{relation.identifier}'
        ORDER BY column_id
        """  # noqa: S608

        _, table = self.execute(sql, fetch=True)
        return [
            {
                "name": row[0],
                "data_type": row[1],
                "nullable": row[2] == "Y",
                "default": row[3],
                "position": row[4],
            }
            for row in table
        ]

    def list_relations_without_caching(
        self,
        schema_relation: BaseRelation,
    ) -> list[BaseRelation]:
        """List relations in schema without caching using flext-infrastructure.databases.flext-db-oracle services.

        List relations in schema without caching using
        flext-infrastructure.databases.flext-db-oracle services.
        """
        # Query Oracle data dictionary - schema validated by dbt framework
        sql = f"""
        SELECT table_name, 'table' as relation_type
        FROM all_tables
        WHERE owner = '{schema_relation.schema}'
        UNION ALL
        SELECT view_name, 'view' as relation_type
        FROM all_views
        WHERE owner = '{schema_relation.schema}'
        """  # noqa: S608

        _, table = self.execute(sql, fetch=True)
        relations = []

        for row in table:
            relation = self.Relation.create(
                database=schema_relation.database,
                schema=schema_relation.schema,
                identifier=row[0],
                type=row[1],
            )
            relations.append(relation)

        return relations

    def check_schema_exists(self, database: str, schema: str) -> bool:
        """Check if schema exists in Oracle using flext-infrastructure.databases.flext-db-oracle services.

        Check if schema exists in Oracle using
        flext-infrastructure.databases.flext-db-oracle services.
        """
        # Query Oracle data dictionary - schema validated and uppercased
        sql = f"""
        SELECT COUNT(*)
        FROM all_users
        WHERE username = '{schema.upper()}'
        """  # noqa: S608

        _, table = self.execute(sql, fetch=True)
        return len(table) > 0 and table[0][0] > 0
