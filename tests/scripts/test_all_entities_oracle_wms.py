#!/usr/bin/env python3
"""Script para testar todas as entidades Oracle WMS individualmente."""

import json
import subprocess
import time
from pathlib import Path

# Ler todas as entidades
with open("all_entities.txt", encoding="utf-8") as f:
    all_entities = [line.strip() for line in f if line.strip()]

print(f"🔍 Testando {len(all_entities)} entidades Oracle WMS...")

# Configuração base
base_config = {
    "base_url": "https://a29.wms.ocs.oraclecloud.com/raizen",
    "username": "USER_WMS_INTEGRA",
    "password": "jmCyS7BK94YvhS@",
    "page_size": 2,
    "timeout": 30,
}

# Resultados
results: dict[str, list[dict[str, object]]] = {
    "success": [],
    "schema_only": [],
    "failed": [],
    "no_data": [],
}

# Testar primeiras 30 entidades para começar
test_entities = all_entities[:30]

for i, entity in enumerate(test_entities, 1):
    print(f"\n📋 [{i:2d}/30] Testando entidade: {entity}")

    # Criar configuração para esta entidade
    config = base_config.copy()
    config["entities"] = [entity]

    config_file = f"test_entity_{entity}.json"
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f)

    try:
        # Teste 1: Discovery de schema
        print("  🔍 Descobrindo schema...")
        result = subprocess.run(
            [
                "/home/marlonsc/flext/.venv/bin/flext-tap-oracle-wms",
                "--config",
                config_file,
                "--discover",
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            print(f"  ❌ FALHA na descoberta: {result.stderr}")
            results["failed"].append(
                {"entity": entity, "stage": "discovery", "error": result.stderr},
            )
            continue

        # Verificar se schema foi gerado
        try:
            schema_data = json.loads(result.stdout)
            if not schema_data.get("streams"):
                print("  ⚠️  Schema vazio")
                results["schema_only"].append(
                    {"entity": entity, "stage": "no_streams", "error": "Schema empty"},
                )
                continue

            stream = schema_data["streams"][0]
            properties_count = len(stream["schema"]["properties"])
            print(f"  ✅ Schema: {properties_count} propriedades")

        except json.JSONDecodeError:
            print("  ❌ FALHA: JSON inválido")
            results["failed"].append(
                {"entity": entity, "stage": "schema_parse", "error": "Invalid JSON"},
            )
            continue

        # Teste 2: Extração de dados
        print("  📊 Extraindo dados...")
        result = subprocess.run(
            [
                "/home/marlonsc/flext/.venv/bin/flext-tap-oracle-wms",
                "--config",
                config_file,
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            print(f"  ⚠️  Dados falharam: {result.stderr}")
            results["schema_only"].append(
                {"entity": entity, "stage": "extraction_failed", "error": result.stderr},
            )
            continue

        # Verificar se dados foram extraídos
        output_lines = result.stdout.strip().split("\n")
        record_lines = [line for line in output_lines if '"type":"RECORD"' in line]

        if not record_lines:
            print("  ⚠️  Sem dados disponíveis")
            results["no_data"].append(
                {
                    "entity": entity,
                    "stage": "extraction_success",
                    "error": "No record data",
                },
            )
        else:
            print(f"  ✅ Extraiu {len(record_lines)} registros")

            # Analisar estrutura dos dados
            try:
                first_record = json.loads(record_lines[0])
                record_data = first_record["record"]

                # Contar tipos de campos
                flattened_fields = sum(1 for key in record_data if "__" in key)
                regular_fields = (
                    len(record_data) - flattened_fields - 2
                )  # -2 para _sdc_*

                print(
                    f"    📈 Campos: {regular_fields} originais, {flattened_fields} flattened",
                )

                results["success"].append(
                    {
                        "entity": entity,
                        "properties": properties_count,
                        "records": len(record_lines),
                        "regular_fields": regular_fields,
                        "flattened_fields": flattened_fields,
                    },
                )

            except Exception as e:
                print(f"    ⚠️  Erro analisando dados: {e}")
                results["success"].append(
                    {
                        "entity": entity,
                        "properties": properties_count,
                        "records": len(record_lines),
                        "analysis_error": str(e),
                    },
                )

    except subprocess.TimeoutExpired:
        print("  ⏰ TIMEOUT")
        results["failed"].append(
            {"entity": entity, "stage": "timeout", "error": "Process timeout"},
        )
    except Exception as e:
        print(f"  ❌ ERRO: {e}")
        results["failed"].append(
            {"entity": entity, "stage": "exception", "error": str(e)},
        )
    finally:
        # Limpeza
        Path(config_file).unlink(missing_ok=True)
        time.sleep(1)  # Evitar rate limiting

# Resultados finais
print("\n📊 RESULTADOS DO TESTE:")
print(f"✅ Sucesso completo: {len(results['success'])}")
print(f"🔍 Apenas schema: {len(results['schema_only'])}")
print(f"📊 Sem dados: {len(results['no_data'])}")
print(f"❌ Falharam: {len(results['failed'])}")

# Salvar resultados detalhados
with open("test_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("\n💾 Resultados salvos em: test_results.json")

# Mostrar sucessos
if results["success"]:
    print("\n🎉 ENTIDADES COM SUCESSO:")
    for item in results["success"][:10]:  # Mostrar primeiras 10
        entity = str(item["entity"])
        props = item["properties"]
        records = item.get("records", 0)
        flattened = item.get("flattened_fields", 0)
        print(f"  • {entity}: {props} props, {records} records, {flattened} flattened")

# Mostrar falhas
if results["failed"]:
    print("\n❌ ENTIDADES COM FALHA:")
    for item in results["failed"]:
        print(f"  • {item['entity']}: {item['stage']} - {str(item['error'])[:100]}")
