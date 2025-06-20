#!/usr/bin/env python3
"""Script para verificar e criar colunas de auditoria nas tabelas WMS."""

import sys
from pathlib import Path

# Adicionar paths
sys.path.insert(0, str(Path(__file__).parent / "dc-oracle-wms"))
sys.path.insert(0, str(Path(__file__).parent / "dc-oracle-db"))


def check_and_create_audit_columns() -> None:
    """Verifica e cria colunas de auditoria nas tabelas WMS."""
    print("=== VERIFICAÇÃO E CRIAÇÃO DE COLUNAS DE AUDITORIA ===")

    try:
        from db import DbClient
        from dotenv import load_dotenv

        # Carregar .env
        load_dotenv(Path(__file__).parent / "dc-oracle-db" / ".env")

        # Criar cliente
        db_client = DbClient(use_pool=True)
        print("✅ DbClient criado")

        # Tabelas WMS para verificar
        tables = ["WMS_ALLOCATION", "WMS_ORDER_DTL", "WMS_ORDER_HDR"]

        # Colunas de auditoria padrão que devem existir
        audit_columns = {
            "CREATED_DATE": "TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP",
            "UPDATED_DATE": "TIMESTAMP(6)",
            "CREATED_BY": "VARCHAR2(100) DEFAULT 'WMS_INTEGRATION'",
            "UPDATED_BY": "VARCHAR2(100)",
        }

        for table_name in tables:
            print(f"\n--- VERIFICANDO TABELA: {table_name} ---")

            # Verificar se tabela existe
            table_exists_sql = """
            SELECT COUNT(*) as table_count
            FROM USER_TABLES
            WHERE TABLE_NAME = :table_name
            """

            try:
                result = db_client.query(
                    table_exists_sql, {
                        "table_name": table_name})
                table_count = result[0]["table_count"] if result else 0

                if table_count == 0:
                    print(f"❌ Tabela {table_name} NÃO existe - pulando")
                    continue

                print(f"✅ Tabela {table_name} existe")

            except Exception as e:
                print(f"❌ Erro ao verificar tabela {table_name}: {e}")
                continue

            # Verificar colunas existentes
            columns_sql = """
            SELECT COLUMN_NAME, DATA_TYPE, DATA_LENGTH, NULLABLE
            FROM USER_TAB_COLUMNS
            WHERE TABLE_NAME = :table_name
            ORDER BY COLUMN_NAME
            """

            try:
                existing_columns = db_client.query(
                    columns_sql, {"table_name": table_name}
                )
                existing_column_names = {
                    row["COLUMN_NAME"] for row in existing_columns}

                print(f"Colunas existentes: {len(existing_column_names)}")

                # Verificar quais colunas de auditoria existem
                existing_audit: list = []
                missing_audit: list = []

                for audit_col in audit_columns:
                    if audit_col in existing_column_names:
                        existing_audit.append(audit_col)
                        missing_audit.append(audit_col)

                if existing_audit:
                    print(
                        f"✅ Colunas de auditoria existentes: {existing_audit}")

                if missing_audit:
                    print(f"❌ Colunas de auditoria faltando: {missing_audit}")

                    # Criar colunas faltando
                    for col_name in missing_audit:
                        col_definition = audit_columns[col_name]
                        alter_sql = f'ALTER TABLE "{table_name}" ADD "{col_name}" {col_definition}'

                        try:
                            print(f"Criando coluna: {col_name}")
                            print(f"SQL: {alter_sql}")

                            db_client.execute(alter_sql, commit=True)
                            print(f"✅ Coluna {col_name} criada com sucesso")

                        except Exception as e:
                            print(f"❌ Erro ao criar coluna {col_name}: {e}")

                            # Se erro for "column already exists", ignorar
                            if (
                                "ORA-01430" in str(e)
                                or "already exists" in str(e).lower()
                            ):
                                print(
                                    f"⚠️ Coluna {col_name} já existe - ignorando erro")
                                print(f"❌ Erro real ao criar {col_name}: {e}")
                    print("✅ Todas as colunas de auditoria já existem")

            except Exception as e:
                print(f"❌ Erro ao verificar colunas de {table_name}: {e}")

        # Verificar resultado final
        print("\n--- VERIFICAÇÃO FINAL ---")
        for table_name in tables:
            try:
                # Verificar se tabela existe
                table_exists_result = db_client.query(
                    table_exists_sql, {"table_name": table_name}
                )
                if table_exists_result[0]["table_count"] == 0:
                    continue

                # Contar colunas de auditoria
                audit_count_sql = """
                SELECT COUNT(*) as audit_count
                FROM USER_TAB_COLUMNS
                WHERE TABLE_NAME = :table_name
                AND COLUMN_NAME IN ('CREATED_DATE', 'UPDATED_DATE', 'CREATED_BY', 'UPDATED_BY')
                """

                audit_result = db_client.query(
                    audit_count_sql, {"table_name": table_name}
                )
                audit_count = audit_result[0]["audit_count"] if audit_result else 0

                print(f"{table_name}: {audit_count}/4 colunas de auditoria")

                if audit_count == 4:
                    print("  ✅ Todas as colunas de auditoria presentes")
                    print(f"  ❌ Faltam {4 - audit_count} colunas de auditoria")

            except Exception as e:
                print(f"❌ Erro na verificação final de {table_name}: {e}")

        db_client.close()
        print("\n=== VERIFICAÇÃO E CRIAÇÃO CONCLUÍDA ===")

    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    check_and_create_audit_columns()
