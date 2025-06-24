#!/usr/bin/env python3
"""Script para listar todas as tabelas disponíveis."""

import sys
from pathlib import Path

# Adicionar paths
sys.path.insert(0, str(Path(__file__).parent / "dc-oracle-wms"))
sys.path.insert(0, str(Path(__file__).parent / "dc-oracle-db"))


def list_tables() -> None:
    """Lista todas as tabelas disponíveis."""
    print("=== LISTAGEM DE TABELAS ===")

    try:
        from db import DbClient
        from dotenv import load_dotenv

        # Carregar .env
        load_dotenv(Path(__file__).parent / "dc-oracle-db" / ".env")

        # Criar cliente
        db_client = DbClient(use_pool=True)
        print("✅ DbClient criado")

        # Listar todas as tabelas
        tables_sql = "SELECT TABLE_NAME FROM USER_TABLES ORDER BY TABLE_NAME"

        try:
            result = db_client.query(tables_sql)
            print(f"Tabelas encontradas: {len(result)}")

            wms_tables: list = []
            other_tables: list = []

            for row in result:
                # Acessar dados da linha corretamente
                if isinstance(row, dict):
                    table_name = row.get("TABLE_NAME", "")
                elif isinstance(row, list | tuple):
                    table_name = row[0] if len(row) > 0 else ""
                    table_name = str(row)

                if "WMS" in table_name:
                    wms_tables.append(table_name)
                    other_tables.append(table_name)

            print(f"\n--- TABELAS WMS ({len(wms_tables)}) ---")
            for i, table in enumerate(wms_tables, 1):
                print(f"  {i:2d}. {table}")

            print(f"\n--- OUTRAS TABELAS ({len(other_tables)}) ---")
            for i, table in enumerate(other_tables, 1):
                print(f"  {i:2d}. {table}")

            # Verificar especificamente as tabelas que queremos
            target_tables = ["WMS_ALLOCATION", "WMS_ORDER_DTL", "WMS_ORDER_HDR"]

            print("\n--- VERIFICAÇÃO DAS TABELAS ALVO ---")
            for table in target_tables:
                if table in wms_tables:
                    print(f"  ✅ {table} - EXISTE")
                    print(f"  ❌ {table} - NÃO EXISTE")

        except Exception as e:
            print(f"❌ Erro ao listar tabelas: {e}")
            import traceback

            traceback.print_exc()

        db_client.close()
        print("\n=== LISTAGEM CONCLUÍDA ===")

    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    list_tables()
