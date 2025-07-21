#!/usr/bin/env python3
"""Script para análise profunda dos tipos de dados complexos Oracle WMS."""

from __future__ import annotations

import sys
from collections import defaultdict
from typing import Any

sys.path.insert(0, "/home/marlonsc/flext/flext-oracle-wms/src")
sys.path.insert(0, "/home/marlonsc/flext/flext-tap-oracle-wms/src")

from flext_observability.logging import get_logger
from pydantic import HttpUrl

from flext_oracle_wms.client import OracleWMSClient
from flext_oracle_wms.config_module import OracleWMSConfig

logger = get_logger(__name__)


def analyze_data_types(data: Any, path: str = "") -> dict[str, set[str]]:
    """Analisa recursivamente os tipos de dados em uma estrutura."""
    type_analysis = defaultdict(set)

    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            type_analysis[current_path].add(type(value).__name__)

            # Análise recursiva
            if isinstance(value, (dict, list)):
                nested_analysis = analyze_data_types(value, current_path)
                for nested_path, nested_types in nested_analysis.items():
                    type_analysis[nested_path].update(nested_types)

    elif isinstance(data, list):
        for i, item in enumerate(data):
            current_path = f"{path}[{i}]" if path else f"[{i}]"
            type_analysis[current_path].add(type(item).__name__)

            # Análise recursiva
            if isinstance(item, (dict, list)):
                nested_analysis = analyze_data_types(item, current_path)
                for nested_path, nested_types in nested_analysis.items():
                    type_analysis[nested_path].update(nested_types)

    return type_analysis


def analyze_complex_structures(record: dict[str, Any]) -> dict[str, Any]:
    """Analisa estruturas complexas em um registro."""
    analysis: dict[str, Any] = {
        "complex_fields": {},
        "array_fields": {},
        "object_fields": {},
        "nested_depth": 0,
        "field_types": {},
    }

    def analyze_field(key: str, value: Any, depth: int = 0) -> None:
        current_depth: int = analysis["nested_depth"]
        analysis["nested_depth"] = max(current_depth, depth)
        analysis["field_types"][key] = type(value).__name__

        if isinstance(value, dict):
            analysis["object_fields"][key] = {
                "keys": list(value.keys()),
                "depth": depth,
                "sub_types": {k: type(v).__name__ for k, v in value.items()},
            }

            # Recursão para objetos aninhados
            for sub_key, sub_value in value.items():
                analyze_field(f"{key}.{sub_key}", sub_value, depth + 1)

        elif isinstance(value, list):
            analysis["array_fields"][key] = {
                "length": len(value),
                "depth": depth,
                "item_types": [type(item).__name__ for item in value],
            }

            # Análise dos itens do array
            for i, item in enumerate(value):
                analyze_field(f"{key}[{i}]", item, depth + 1)

        elif isinstance(value, (dict, list)) or hasattr(value, "__dict__"):
            analysis["complex_fields"][key] = {
                "type": type(value).__name__,
                "depth": depth,
                "content": str(value)[:200],  # Primeiros 200 chars
            }

    for key, value in record.items():
        analyze_field(key, value)

    return analysis


def main() -> None:
    """Executa análise completa dos dados Oracle WMS."""
    # Configuração
    config = OracleWMSConfig(
        base_url=HttpUrl("https://a29.wms.ocs.oraclecloud.com/raizen"),
        username="USER_WMS_INTEGRA",
        password="jmCyS7BK94YvhS@",
        batch_size=50,  # Menos registros para análise mais focada
        timeout_seconds=30.0,
    )

    client = OracleWMSClient(config)

    entities_to_analyze: list[str] = ["allocation", "order_hdr", "order_dtl"]

    for entity in entities_to_analyze:
        try:
            # Validar e buscar dados da entidade
            validated_entity = client.validate_entity_name(entity)
            response = client.get_entity_data(validated_entity)
            records = response.records

            if not records:
                continue

            # Análise do primeiro registro (mais detalhada)
            first_record = records[0]

            complex_analysis = analyze_complex_structures(first_record)

            # Mostrar campos objeto detalhadamente
            if complex_analysis["object_fields"]:
                for field_name in complex_analysis["object_fields"]:
                    logger.info(f"Object field: {field_name}")

            # Mostrar campos array detalhadamente
            if complex_analysis["array_fields"]:
                for field_name in complex_analysis["array_fields"]:
                    logger.info(f"Array field: {field_name}")

            # Mostrar alguns exemplos de campos complexos
            sample_fields = list(first_record.keys())[:10]  # Primeiros 10 campos
            for field in sample_fields:
                value = first_record[field]
                if isinstance(value, (dict, list)):
                    if isinstance(value, dict):
                        pass

            # Análise de todos os registros para padrões
            all_types = analyze_data_types(records)

            complex_patterns = {
                k: v
                for k, v in all_types.items()
                if len(v) > 1 or any(t in {"dict", "list"} for t in v)
            }

            if complex_patterns:
                for _field_path, _types in complex_patterns.items():
                    pass

        except Exception:
            import traceback

            traceback.print_exc()

        finally:
            # Clean up client connection
            if hasattr(client, "_client"):
                client_instance = getattr(client, "_client", None)
                if client_instance is not None and hasattr(client_instance, "close"):
                    client_instance.close()


if __name__ == "__main__":
    main()
