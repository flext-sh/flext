#!/usr/bin/env python3
"""Script para debugar acesso aos dados das queries Oracle."""

import sys
from pathlib import Path

# Adicionar paths
sys.path.insert(0, str(Path(__file__).parent / "dc-oracle-wms"))
sys.path.insert(0, str(Path(__file__).parent / "dc-oracle-db"))


def debug_query():
    """Debug do acesso aos dados das queries."""
    print("=== DEBUG DE QUERY ===")

    try:
        from db import DbClient
        from dotenv import load_dotenv

        # Carregar .env
        load_dotenv(Path(__file__).parent / "dc-oracle-db" / ".env")

        # Criar cliente
        db_client = DbClient(use_pool=True)
        print("✅ DbClient criado")

        # Teste simples
        test_sql = "SELECT TABLE_NAME FROM USER_TABLES WHERE ROWNUM <= 5"

        try:
            result = db_client.query(test_sql)
            print(f"Resultado tipo: {type(result)}")
            print(f"Resultado: {result}")

            if result:
                print(f"Primeiro item tipo: {type(result[0])}")
                print(f"Primeiro item: {result[0]}")

                # Tentar diferentes formas de acessar
                first_row = result[0]

                if isinstance(first_row, dict):
                    print("É um dicionário:")
                    for key, value in first_row.items():
                        print(f"  {key}: {value}")
                elif isinstance(first_row, list | tuple):
                    print("É uma lista/tupla:")
                    for i, value in enumerate(first_row):
                        print(f"  [{i}]: {value}")
                elif hasattr(first_row, '__dict__'):
                    print("Tem atributos:")
                    for attr in dir(first_row):
                        if not attr.startswith('_'):
                            try:
                                value = getattr(first_row, attr)
                                print(f"  {attr}: {value}")
                            except:
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
            wms_result = db_client.query(wms_sql)
            print(f"WMS resultado: {wms_result}")

            if wms_result:
                count_row = wms_result[0]
                print(f"Count row tipo: {type(count_row)}")
                print(f"Count row: {count_row}")

                # Tentar acessar o valor
                if isinstance(count_row, dict):
                    count = count_row.get('TOTAL', count_row.get('total', 0))
                elif isinstance(count_row, list | tuple):
                    count = count_row[0] if len(count_row) > 0 else 0
                else:
                    count = count_row

                print(f"Count: {count}")

        except Exception as e:
            print(f"❌ Erro na query WMS: {e}")

        db_client.close()
        print("\n=== DEBUG CONCLUÍDO ===")

    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_query()
