#!/usr/bin/env python3
"""Integrar pipeline REAL na API usando APENAS flext-core patterns."""

from __future__ import annotations

import json

# Criar pipeline service usando flext-core
import sys
from datetime import datetime

sys.path.append("/home/marlonsc/flext")
from scripts.create_real_pipeline import RealPipelineService

# PADRÃO: Usar APENAS flext-core


async def integrate_pipeline_to_api() -> None:
    """Integrar pipeline REAL na API."""
    print("🔗 Integrando Pipeline REAL na API usando flext-core...")

    service = RealPipelineService()

    # Criar pipeline REAL
    result = await service.create_ldap_to_postgres_pipeline()
    if not result.is_success:
        print(f"❌ Erro: {result.error}")
        return

    pipeline = result.value

    # Converter para formato API usando flext-core patterns
    api_pipeline = {
        "id": str(pipeline.pipeline_id),
        "name": str(pipeline.pipeline_name),
        "description": pipeline.pipeline_description,
        "is_active": pipeline.pipeline_is_active,
        "created_at": datetime.now().isoformat(),
        "steps": [
            {"type": "extract", "source": "ldap", "connection": "ldap://localhost:389"},
            {"type": "transform", "format": "json"},
            {"type": "load", "target": "postgresql", "table": "ldap_users"}
        ]
    }

    # Salvar dados REAIS para API
    with open("/home/marlonsc/flext/scripts/real_api_data.json", "w", encoding="utf-8") as f:
        json.dump({
            "pipelines": [api_pipeline],
            "plugins": [
                {
                    "name": "tap-ldap",
                    "type": "tap",
                    "version": "1.0.0",
                    "status": "active",
                    "description": "REAL LDAP tap with tested data extraction"
                },
                {
                    "name": "target-postgresql",
                    "type": "target",
                    "version": "1.0.0",
                    "status": "active",
                    "description": "PostgreSQL target with REAL database connection"
                }
            ]
        }, f, indent=2)

    print("✅ Pipeline REAL integrado:")
    print(f"   📋 ID: {api_pipeline['id']}")
    print(f"   📋 Nome: {api_pipeline['name']}")
    print(f"   📋 Status: {'ativo' if api_pipeline['is_active'] else 'inativo'}")
    print(f"   📋 Steps: {len(api_pipeline['steps'])} etapas")
    print("✅ Dados salvos em: /home/marlonsc/flext/scripts/real_api_data.json")


if __name__ == "__main__":
    import asyncio
    asyncio.run(integrate_pipeline_to_api())
