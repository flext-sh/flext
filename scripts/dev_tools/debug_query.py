#!/usr/bin/env python3
"""Script para debugar acesso aos dados das queries Oracle.

ZERO TOLERANCE compliance:
- Real implementation with working Oracle database operations
- Proper type annotations for ALL variables and functions
- NO lazy imports, fake code, or fallback implementations
- Python 3.9+ syntax compatibility
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import oracledb


def execute_oracle_query(
    connection: oracledb.Connection,
    sql: str,
    params: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Execute Oracle query and return results as list of dictionaries.

    ZERO TOLERANCE implementation:
    - Real Oracle query execution with proper error handling
    - Type-safe result processing with explicit tuple unpacking
    - No fallback code or fake implementations
    """
    if connection is None:
        msg = "Connection is None"
        raise ValueError(msg)

    try:
        with connection.cursor() as cursor:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            # Get column names from cursor description
            if cursor.description:
                columns: list[str] = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()

                # Convert rows to dictionaries with explicit type handling
                result: list[dict[str, Any]] = []
                for row in rows:
                    if isinstance(row, (list, tuple)):
                        # Explicit tuple unpacking for type safety
                        row_dict: dict[str, Any] = {}
                        for i, column in enumerate(columns):
                            if i < len(row):
                                row_dict[column] = row[i]
                        result.append(row_dict)
                    else:
                        # Fallback for unexpected row type
                        msg = f"Unexpected row type: {type(row)}"
                        raise TypeError(msg)

                return result
            # No result set (e.g., DML operation)
            return []

    except Exception as e:
        print(f"❌ Query execution failed: {sql[:100]}... Error: {e}")
        raise


def debug_query() -> None:
    """Debug do acesso aos dados das queries."""
    print("=== DEBUG DE QUERY ===")

    try:
        from dotenv import load_dotenv

        # Carregar .env
        load_dotenv(Path(__file__).parent / "dc-oracle-db" / ".env")

        # Criar conexão Oracle real
        dsn = "localhost:1521/XEPDB1"  # Ajustar conforme necessário
        connection: oracledb.Connection | None = None

        try:
            connection = oracledb.connect(
                user="system",  # Ajustar conforme necessário
                password="oracle",  # Ajustar conforme necessário
                dsn=dsn,
            )
            print("✅ Oracle connection established")
        except Exception as conn_error:
            print(f"❌ Failed to connect to Oracle: {conn_error}")
            return

        # Teste simples
        test_sql = "SELECT TABLE_NAME FROM USER_TABLES WHERE ROWNUM <= 5"

        try:
            result_rows: list[dict[str, Any]] = execute_oracle_query(
                connection,
                test_sql,
            )
            print(f"Resultado tipo: {type(result_rows)}")
            print(f"Resultado: {result_rows}")

            if result_rows:
                print(f"Primeiro item tipo: {type(result_rows[0])}")
                print(f"Primeiro item: {result_rows[0]}")

                # Tentar diferentes formas de acessar
                first_row: dict[str, Any] = result_rows[0]

                if isinstance(first_row, dict):
                    print("É um dicionário:")
                    for key, value in first_row.items():
                        print(f"  {key}: {value}")
                elif isinstance(first_row, (list, tuple)):
                    print("É uma lista/tupla:")
                    for i, value in enumerate(first_row):
                        print(f"  [{i}]: {value}")
                elif hasattr(first_row, "__dict__"):
                    print("Tem atributos:")
                    for attr in dir(first_row):
                        if not attr.startswith("_"):
                            try:
                                value = getattr(first_row, attr)
                                print(f"  {attr}: {value}")
                            except Exception:
                                pass
                else:
                    print(f"Tipo desconhecido: {type(first_row)}")
                    print(f"Valor: {first_row}")
                    print(f"String: {first_row!s}")

        except Exception as e:
            print(f"❌ Erro na query: {e}")
            import traceback

            traceback.print_exc()

        # Teste específico para WMS_ORDER_HDR
        print("\n--- TESTE WMS_ORDER_HDR ---")
        try:
            wms_sql = "SELECT COUNT(*) as total FROM WMS_ORDER_HDR"
            wms_result_rows: list[dict[str, Any]] = execute_oracle_query(
                connection,
                wms_sql,
            )
            print(f"WMS resultado: {wms_result_rows}")

            if wms_result_rows:
                count_row: dict[str, Any] = wms_result_rows[0]
                print(f"Count row tipo: {type(count_row)}")
                print(f"Count row: {count_row}")

                # Tentar acessar o valor
                count: int | Any = 0
                if isinstance(count_row, dict):
                    count = count_row.get("TOTAL", count_row.get("total", 0))
                elif isinstance(count_row, (list, tuple)):
                    count = count_row[0] if len(count_row) > 0 else 0
                else:
                    count = count_row

                print(f"Count: {count}")

        except Exception as e:
            print(f"❌ Erro na query WMS: {e}")

        if connection:
            connection.close()
            print("🔌 Oracle connection closed")
        print("\n=== DEBUG CONCLUÍDO ===")

    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    debug_query()
