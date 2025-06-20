#!/usr/bin/env python3
"""Script corrigido para criar colunas de auditoria nas tabelas WMS."""

import sys
from pathlib import Path

# Adicionar paths
sys.path.insert(0, str(Path(__file__).parent / "dc-oracle-wms"))
sys.path.insert(0, str(Path(__file__).parent / "dc-oracle-db"))


def create_audit_columns_fixed() -> None:
    """Cria colunas de auditoria nas tabelas WMS (versão corrigida)."""
    print("=== CRIAÇÃO DE COLUNAS DE AUDITORIA (CORRIGIDA) ===")

    try:
        from db import DbClient
        from dotenv import load_dotenv

        # Carregar .env
        load_dotenv(Path(__file__).parent / "dc-oracle-db" / ".env")

        # Criar cliente
        db_client = DbClient(use_pool=True)
        print("✅ DbClient criado")

        # Tabelas WMS para modificar
        tables = ["WMS_ALLOCATION", "WMS_ORDER_DTL", "WMS_ORDER_HDR"]

        # Comandos ALTER TABLE para cada coluna de auditoria
        audit_columns_sql = [
            'ALTER TABLE "{table}" ADD "CREATED_DATE" TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP',
            'ALTER TABLE "{table}" ADD "UPDATED_DATE" TIMESTAMP(6)',
            'ALTER TABLE "{table}" ADD "CREATED_BY" VARCHAR2(100) DEFAULT \'WMS_INTEGRATION\'',
            'ALTER TABLE "{table}" ADD "UPDATED_BY" VARCHAR2(100)',
        ]

        for table_name in tables:
            print(f"\n--- PROCESSANDO TABELA: {table_name} ---")

            # Verificar se tabela existe (formato corrigido)
            table_exists_sql = f"SELECT COUNT(*) as count FROM USER_TABLES WHERE TABLE_NAME = '{table_name}'"

            try:
                result = db_client.query(table_exists_sql)
                # CORREÇÃO: Acessar dados como dicionário
                table_count = result[0]["count"] if result and len(
                    result) > 0 else 0

                if table_count == 0:
                    print(f"❌ Tabela {table_name} NÃO existe - pulando")
                    continue

                print(f"✅ Tabela {table_name} existe")

            except Exception as e:
                print(f"❌ Erro ao verificar tabela {table_name}: {e}")
                continue

            # Criar cada coluna de auditoria
            for sql_template in audit_columns_sql:
                alter_sql = sql_template.format(table=table_name)

                # Extrair nome da coluna para log
                if 'ADD "CREATED_DATE"' in alter_sql:
                    col_name = "CREATED_DATE"
                elif 'ADD "UPDATED_DATE"' in alter_sql:
                    col_name = "UPDATED_DATE"
                elif 'ADD "CREATED_BY"' in alter_sql:
                    col_name = "CREATED_BY"
                elif 'ADD "UPDATED_BY"' in alter_sql:
                    col_name = "UPDATED_BY"
                    col_name = "UNKNOWN"

                try:
                    print(f"  Criando coluna: {col_name}")
                    print(f"  SQL: {alter_sql}")

                    db_client.execute(alter_sql, commit=True)
                    print(f"  ✅ Coluna {col_name} criada com sucesso")

                except Exception as e:
                    error_msg = str(e)

                    # Verificar se erro é "column already exists"
                    if (
                        "ORA-01430" in error_msg
                        or "already exists" in error_msg.lower()
                    ):
                        print(f"  ⚠️ Coluna {col_name} já existe - OK")
                        print(f"  ❌ Erro ao criar coluna {col_name}: {e}")

        # Verificação final (formato corrigido)
        print("\n--- VERIFICAÇÃO FINAL ---")
        for table_name in tables:
            try:
                # Verificar se tabela existe
                table_exists_result = db_client.query(
                    f"SELECT COUNT(*) as count FROM USER_TABLES WHERE TABLE_NAME = '{table_name}'", )
                if not table_exists_result or table_exists_result[0]["count"] == 0:
                    continue

                # Verificar colunas de auditoria
                audit_check_sql = f"""
                SELECT COUNT(*) as audit_count
                FROM USER_TAB_COLUMNS
                WHERE TABLE_NAME = '{table_name}'
                AND COLUMN_NAME IN ('CREATED_DATE', 'UPDATED_DATE', 'CREATED_BY', 'UPDATED_BY')
                """

                audit_result = db_client.query(audit_check_sql)
                # CORREÇÃO: Acessar dados como dicionário
                audit_count = (
                    audit_result[0]["audit_count"]
                    if audit_result and len(audit_result) > 0
                    else 0
                )

                print(f"{table_name}: {audit_count}/4 colunas de auditoria")

                if audit_count == 4:
                    print("  ✅ Todas as colunas de auditoria presentes")
                    print(f"  ❌ Faltam {4 - audit_count} colunas de auditoria")

                # Listar colunas existentes
                columns_list_sql = f"""
                SELECT COLUMN_NAME as column_name
                FROM USER_TAB_COLUMNS
                WHERE TABLE_NAME = '{table_name}'
                AND COLUMN_NAME IN ('CREATED_DATE', 'UPDATED_DATE', 'CREATED_BY', 'UPDATED_BY')
                ORDER BY COLUMN_NAME
                """

                existing_audit = db_client.query(columns_list_sql)
                if existing_audit:
                    # CORREÇÃO: Acessar dados como dicionário
                    existing_names = [row["column_name"]
                                      for row in existing_audit]
                    print(f"  Colunas existentes: {existing_names}")

            except Exception as e:
                print(f"❌ Erro na verificação final de {table_name}: {e}")

        db_client.close()
        print("\n=== CRIAÇÃO CONCLUÍDA ===")

    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    create_audit_columns_fixed()
