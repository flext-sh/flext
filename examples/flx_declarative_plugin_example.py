#!/usr/bin/env python3
"""
FLX Declarative Plugin Example - Demonstração do sistema de plugins

Este exemplo mostra como criar plugins declarativos que podem ser expostos via:
- CLI (linha de comando)
- REST API
- Web interface

O sistema usa decorators para registro automático e dependency injection.
"""

from __future__ import annotations

import asyncio
from typing import Any

# Importar decorators para registro declarativo
from flx.adapters.inbound.fire_cli import register_command, register_command_group


@register_command_group("database")
class DatabaseCommands:
    """Plugin de comandos de banco de dados.

    Comandos disponíveis via CLI:
    - flx database backup /path/to/backup
    - flx database restore /path/to/backup
    - flx database status
    """

    def __init__(self, command_bus=None) -> None:
        """Inicializa com command bus injetado automaticamente."""
        self.command_bus = command_bus

    async def backup(self, path: str, compress: bool = True) -> dict[str, Any]:
        """Criar backup do banco de dados.

        Args:
            path: Caminho para salvar o backup
            compress: Se deve comprimir o backup

        Returns:
            Status do backup
        """
        # Simular processo de backup
        await asyncio.sleep(0.1)

        return {
            "status": "success",
            "backup_path": path,
            "compressed": compress,
            "size_mb": 150.5,
            "timestamp": "2025-06-12T12:45:00Z",
        }

    async def restore(self, backup_path: str, force: bool = False) -> dict[str, Any]:
        """Restaurar banco de dados do backup.

        Args:
            backup_path: Caminho do arquivo de backup
            force: Forçar restauração mesmo se banco existir

        Returns:
            Status da restauração
        """
        await asyncio.sleep(0.2)

        return {
            "status": "success",
            "restored_from": backup_path,
            "forced": force,
            "records_restored": 10000,
            "duration_seconds": 15.3,
        }

    def status(self) -> dict[str, Any]:
        """Verificar status do banco de dados.

        Returns:
            Status do banco
        """
        return {
            "database": "postgresql",
            "version": "15.2",
            "status": "running",
            "connections": 25,
            "size_gb": 2.4,
            "uptime_hours": 168,
        }


@register_command_group("monitoring")
class MonitoringCommands:
    """Plugin de comandos de monitoramento.

    Comandos disponíveis via CLI:
    - flx monitoring alerts
    - flx monitoring metrics --component database
    - flx monitoring health-check
    """

    def __init__(self, command_bus=None) -> None:
        self.command_bus = command_bus

    def alerts(self, severity: str = "all") -> dict[str, Any]:
        """Listar alertas do sistema.

        Args:
            severity: Filtrar por severidade (critical, warning, info, all)

        Returns:
            Lista de alertas
        """
        alerts = [
            {
                "id": "ALT-001",
                "severity": "warning",
                "component": "database",
                "message": "High connection count",
                "timestamp": "2025-06-12T12:40:00Z",
            },
            {
                "id": "ALT-002",
                "severity": "critical",
                "component": "api",
                "message": "Response time above threshold",
                "timestamp": "2025-06-12T12:42:00Z",
            },
        ]

        if severity != "all":
            alerts = [a for a in alerts if a["severity"] == severity]

        return {"alerts": alerts, "total": len(alerts), "filter": severity}

    async def metrics(
        self, component: str = "all", duration: str = "1h"
    ) -> dict[str, Any]:
        """Obter métricas do sistema.

        Args:
            component: Componente específico ou 'all'
            duration: Período das métricas (1h, 24h, 7d)

        Returns:
            Métricas do sistema
        """
        await asyncio.sleep(0.1)

        metrics = {
            "timestamp": "2025-06-12T12:45:00Z",
            "duration": duration,
            "component": component,
            "cpu_usage": 45.2,
            "memory_usage": 62.8,
            "disk_usage": 78.5,
            "network_in_mbps": 125.3,
            "network_out_mbps": 89.7,
        }

        if component == "database":
            metrics.update(
                {"connections": 25, "queries_per_second": 150, "cache_hit_ratio": 0.95}
            )
        elif component == "api":
            metrics.update(
                {
                    "requests_per_second": 450,
                    "avg_response_time_ms": 85,
                    "error_rate": 0.02,
                }
            )

        return metrics

    def health_check(self) -> dict[str, Any]:
        """Executar verificação de saúde completa.

        Returns:
            Status de saúde de todos os componentes
        """
        return {
            "overall_status": "healthy",
            "components": {
                "database": {"status": "healthy", "response_time_ms": 12},
                "api": {"status": "healthy", "response_time_ms": 8},
                "cache": {"status": "healthy", "response_time_ms": 2},
                "queue": {"status": "healthy", "response_time_ms": 5},
            },
            "checks_passed": 4,
            "checks_total": 4,
            "timestamp": "2025-06-12T12:45:00Z",
        }


@register_command("system-report")
async def generate_system_report(
    format: str = "json", output: str | None = None
) -> dict[str, Any]:
    """Comando standalone para gerar relatório do sistema.

    Args:
        format: Formato do relatório (json, yaml, csv)
        output: Arquivo de saída (opcional)

    Returns:
        Relatório gerado
    """
    await asyncio.sleep(0.3)

    report = {
        "report_id": "RPT-20250612-124500",
        "generated_at": "2025-06-12T12:45:00Z",
        "format": format,
        "sections": {
            "system_info": {
                "os": "Linux",
                "version": "6.14.8-2-cachyos",
                "architecture": "x86_64",
                "uptime_hours": 72,
            },
            "performance": {
                "cpu_usage": 45.2,
                "memory_usage": 62.8,
                "disk_usage": 78.5,
                "load_average": [1.2, 1.1, 0.9],
            },
            "services": {
                "flx_framework": "running",
                "database": "running",
                "api_server": "running",
                "monitoring": "running",
            },
        },
        "recommendations": [
            "Consider disk cleanup - usage above 75%",
            "Monitor CPU usage trends",
            "All services operating normally",
        ],
    }

    if output:
        import json
        from pathlib import Path

        output_path = Path(output)
        if format == "json":
            output_path.write_text(json.dumps(report, indent=2))

        report["output_file"] = str(output_path)

    return report


if __name__ == "__main__":
    pass
