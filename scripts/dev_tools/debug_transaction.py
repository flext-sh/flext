#!/usr/bin/env python3
"""Script para debugar problemas de transação."""

import sys
from pathlib import Path

# Adicionar paths
sys.path.insert(0, str(Path(__file__).parent / "dc-oracle-wms"))
sys.path.insert(0, str(Path(__file__).parent / "dc-oracle-db"))


def debug_transaction():
    """Debug de problemas de transação."""
    print("=== DEBUG DE TRANSAÇÃO ===")

    try:
        from db import DbClient
        from dotenv import load_dotenv

        # Carregar .env
        load_dotenv(Path(__file__).parent / "dc-oracle-db" / ".env")

        # Criar cliente
        db_client = DbClient(use_pool=True)
        print("✅ DbClient criado")

        table_name = "WMS_ORDER_HDR"

        # Dados de teste simples
        test_data = {
            "ID": 999998,
            "STATUS_ID": 10,
            "COMPANY_ID": 1,
            "FACILITY_ID": 1,
            "ORDER_NBR": "TEST999998",
            "ORDER_TYPE_ID": 1,
            "ORD_DATE": "2024-01-01",
            "ORIG_SALE_PRICE": 100.0,
            "TOTAL_ORIG_ORD_QTY": 1,
            "ORIG_SKU_COUNT": 1,
            "CREATED_DATE": "2024-01-01 10:00:00",
            "UPDATED_DATE": "2024-01-01 10:00:00",
            "CREATED_BY": "TEST_DEBUG",
            "UPDATED_BY": "TEST_DEBUG",
        }

        # Construir INSERT
        fields = list(test_data.keys())
        fields_str = ", ".join([f'"{field}"' for field in fields])

        values = []
        for field in fields:
            value = test_data[field]
            if isinstance(value, str):
                if any(
                    date_keyword in field.lower() for date_keyword in ["date", "_dt"]
                ):
                    if len(value) == 10:  # YYYY-MM-DD
                        values.append(f"TO_DATE('{value}', 'YYYY-MM-DD')")
                    else:  # YYYY-MM-DD HH:MM:SS
                        values.append(f"TO_DATE('{value}', 'YYYY-MM-DD HH24:MI:SS')")
                else:
                    values.append(f"'{value}'")
            else:
                values.append(str(value))

        values_str = ", ".join(values)
        insert_sql = f'INSERT INTO "{table_name}" ({fields_str}) VALUES ({values_str})'

        print(f"SQL: {insert_sql[:100]}...")

        # TESTE 1: Verificar contagem antes
        count_before_sql = f'SELECT COUNT(*) as total FROM "{table_name}"'
        result_before = db_client.query(count_before_sql)
        count_before = result_before[0]["total"] if result_before else 0
        print(f"\nRegistros antes: {count_before}")

        # TESTE 2: Inserir com transaction() e verificar imediatamente
        print("\n--- TESTE COM TRANSACTION() ---")
        try:
            with db_client.transaction():
                print("Iniciando transação...")
                affected_rows = db_client.execute(insert_sql, commit=False)
                print(f"INSERT executado: {affected_rows} linhas afetadas")

                # Verificar dentro da transação
                count_in_transaction = db_client.query(count_before_sql)
                count_in_tx = (
                    count_in_transaction[0]["total"] if count_in_transaction else 0
                )
                print(f"Registros dentro da transação: {count_in_tx}")

                print("Saindo do bloco with (commit automático)...")

            print("Transação finalizada")

        except Exception as e:
            print(f"❌ Erro na transação: {e}")

        # TESTE 3: Verificar contagem após transação
        result_after = db_client.query(count_before_sql)
        count_after = result_after[0]["total"] if result_after else 0
        print(f"Registros após transação: {count_after}")

        if count_after > count_before:
            print("✅ Dados inseridos com sucesso!")

            # Buscar o registro inserido
            find_sql = f'SELECT * FROM "{table_name}" WHERE "ID" = 999998'
            found_records = db_client.query(find_sql)

            if found_records:
                record = found_records[0]
                print("Registro encontrado:")
                print(f"  ID: {record.get('ID')}")
                print(f"  STATUS_ID: {record.get('STATUS_ID')}")
                print(f"  ORDER_NBR: {record.get('ORDER_NBR')}")
                print(f"  CREATED_BY: {record.get('CREATED_BY')}")

                # Limpar dados de teste
                delete_sql = f'DELETE FROM "{table_name}" WHERE "ID" = 999998'
                db_client.execute(delete_sql, commit=True)
                print("🧹 Dados de teste removidos")

        else:
            print("❌ Dados NÃO foram inseridos")

        # TESTE 4: Verificar se há problemas com autocommit
        print("\n--- TESTE AUTOCOMMIT ---")
        try:
            with db_client.get_connection() as conn:
                print(f"Autocommit: {getattr(conn, 'autocommit', 'N/A')}")

                cursor = conn.cursor()
                cursor.execute(insert_sql.replace("999998", "999997"))
                affected = cursor.rowcount
                print(f"INSERT direto: {affected} linhas afetadas")

                # Verificar antes do commit
                cursor.execute(count_before_sql)
                count_before_commit = cursor.fetchone()[0]
                print(f"Registros antes do commit: {count_before_commit}")

                # Commit explícito
                conn.commit()
                print("COMMIT explícito executado")

                # Verificar após commit
                cursor.execute(count_before_sql)
                count_after_commit = cursor.fetchone()[0]
                print(f"Registros após commit: {count_after_commit}")

                cursor.close()

                if count_after_commit > count_before:
                    print("✅ Dados inseridos com conexão direta!")

                    # Limpar dados de teste
                    delete_sql = f'DELETE FROM "{table_name}" WHERE "ID" = 999997'
                    db_client.execute(delete_sql, commit=True)
                    print("🧹 Dados de teste removidos")

        except Exception as e:
            print(f"❌ Erro no teste direto: {e}")

        db_client.close()
        print("\n=== DEBUG CONCLUÍDO ===")

    except Exception as e:
        print(f"❌ Erro no debug: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    debug_transaction()
