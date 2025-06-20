#!/usr/bin/env python3
"""Script para verificar quais colunas existem na tabela Oracle."""

import sys
from pathlib import Path

# Adicionar paths
sys.path.insert(0, str(Path(__file__).parent / "dc-oracle-wms"))
sys.path.insert(0, str(Path(__file__).parent / "dc-oracle-db"))


def check_oracle_columns() -> None:
    """Verifica quais colunas existem na tabela Oracle."""
    print("=== VERIFICAÇÃO DE COLUNAS ORACLE ===")

    try:
        from db import DbClient
        from db.schema import SchemaExtractor
        from dotenv import load_dotenv

        # Carregar .env
        load_dotenv(Path(__file__).parent / "dc-oracle-db" / ".env")

        # Criar cliente
        db_client = DbClient(use_pool=True)
        print("✅ DbClient criado")

        table_name = "WMS_ORDER_HDR"

        # Método 1: Usar SchemaExtractor
        print("\n--- MÉTODO 1: SchemaExtractor ---")
        try:
            with db_client.get_connection() as conn:
                extractor = SchemaExtractor(conn)
                table_schema = extractor.extract_table_schema(table_name)
                oracle_schema = table_schema.to_dict()

                columns = oracle_schema.get("columns", [])
                print(f"Colunas encontradas: {len(columns)}")

                print(f"\nTodas as colunas da tabela {table_name}:")
                for i, column in enumerate(columns, 1):
                    name = column["name"]
                    data_type = column.get("data_type", "UNKNOWN")
                    nullable = "NULL" if column.get(
                        "nullable", True) else "NOT NULL"
                    length = column.get("length", "")
                    length_str = f"({length})" if length else ""

                    print(
                        f"  {
                            i:2d}. {
                            name:<25} {data_type}{
                            length_str:<15} {nullable}",
                    )

        except Exception as e:
            print(f"❌ Erro com SchemaExtractor: {e}")

        # Método 2: Query direta no dicionário de dados Oracle
        print("\n--- MÉTODO 2: Query direta no dicionário de dados ---")
        try:
            columns_sql = """
            SELECT
                COLUMN_NAME,
                DATA_TYPE,
                DATA_LENGTH,
                DATA_PRECISION,
                DATA_SCALE,
                NULLABLE,
                COLUMN_ID
            FROM USER_TAB_COLUMNS
            WHERE TABLE_NAME = :table_name
            ORDER BY COLUMN_ID
            """

            result = db_client.query(columns_sql, {"table_name": table_name})

            if result:
                print(f"Colunas encontradas: {len(result)}")
                print("\nDetalhes das colunas:")
                for i, row in enumerate(result, 1):
                    name = row["COLUMN_NAME"]
                    data_type = row["DATA_TYPE"]
                    length = row.get("DATA_LENGTH", "")
                    precision = row.get("DATA_PRECISION", "")
                    scale = row.get("DATA_SCALE", "")
                    nullable = row["NULLABLE"]

                    # Formatar tipo
                    if data_type == "NUMBER" and precision:
                        if scale and scale > 0:
                            type_str = f"NUMBER({precision},{scale})"
                            type_str = f"NUMBER({precision})"
                    elif data_type in {"VARCHAR2", "CHAR"} and length:
                        type_str = f"{data_type}({length})"
                        type_str = data_type

                    nullable_str = "NULL" if nullable == "Y" else "NOT NULL"

                    print(
                        f"  {
                            i:2d}. {
                            name:<25} {
                            type_str:<20} {nullable_str}")
                print(f"❌ Nenhuma coluna encontrada para tabela {table_name}")

        except Exception as e:
            print(f"❌ Erro na query direta: {e}")

        # Método 3: Verificar se tabela existe
        print("\n--- MÉTODO 3: Verificar se tabela existe ---")
        try:
            table_exists_sql = """
            SELECT COUNT(*) as table_count
            FROM USER_TABLES
            WHERE TABLE_NAME = :table_name
            """

            result = db_client.query(
                table_exists_sql, {
                    "table_name": table_name})
            table_count = result[0]["table_count"] if result else 0

            if table_count > 0:
                print(f"✅ Tabela {table_name} existe")
                print(f"❌ Tabela {table_name} NÃO existe")

                # Listar tabelas disponíveis
                tables_sql = "SELECT TABLE_NAME FROM USER_TABLES ORDER BY TABLE_NAME"
                tables_result = db_client.query(tables_sql)

                if tables_result:
                    print("\nTabelas disponíveis no schema:")
                    for i, row in enumerate(tables_result, 1):
                        table = row["TABLE_NAME"]
                        print(f"  {i:2d}. {table}")

                        # Verificar se é relacionada a WMS
                        if "WMS" in table or "ORDER" in table:
                            print("      ⭐ Possível tabela WMS")

        except Exception as e:
            print(f"❌ Erro ao verificar tabela: {e}")

        db_client.close()
        print("\n=== VERIFICAÇÃO CONCLUÍDA ===")

    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    check_oracle_columns()
