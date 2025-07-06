"""Modern conftest.py template for FLEXT projects.

Este template fornece fixtures modernos, mocks avançados e configurações de teste
otimizadas para alta cobertura e performance.

Versão: 2025-07-05
Compatibilidade: Python 3.13+, pytest 8.0+
"""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import AsyncClient
from pydantic import BaseModel

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

# =============================================================================
# CONFIGURAÇÃO GLOBAL DE TESTES
# =============================================================================

# Configuração do event loop para testes async
pytest_asyncio.fixture(scope="session")


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop]:
    """Event loop para testes async com scope de sessão."""
    loop = asyncio.new_event_loop()
    try:
        yield loop
    finally:
        loop.close()


# =============================================================================
# FIXTURES DE AMBIENTE E CONFIGURAÇÃO
# =============================================================================


@pytest.fixture(scope="session")
def test_env() -> dict[str, str]:
    """Variáveis de ambiente para testes."""
    return {
        "ENVIRONMENT": "test",
        "DEBUG": "true",
        "LOG_LEVEL": "DEBUG",
        "DATABASE_URL": "sqlite:///:memory:",
        "REDIS_URL": "redis://localhost:6379/15",  # DB 15 para testes
        "SECRET_KEY": "test-secret-key-not-for-production",
        "JWT_SECRET": "test-jwt-secret",
        "JWT_ALGORITHM": "HS256",
    }


@pytest.fixture(autouse=True)
def setup_test_env(test_env: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
    """Configura automaticamente o ambiente para todos os testes."""
    for key, value in test_env.items():
        monkeypatch.setenv(key, value)


@pytest.fixture
def temp_dir() -> Generator[Path]:
    """Diretório temporário para testes."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def mock_config_dir(temp_dir: Path) -> Path:
    """Diretório de configuração mockado."""
    config_dir = temp_dir / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


# =============================================================================
# FIXTURES DE BANCO DE DADOS E PERSISTÊNCIA
# =============================================================================


@pytest.fixture
async def db_session() -> AsyncGenerator[Any]:
    """Sessão de banco de dados para testes async."""
    # Mock implementation - customize para seu ORM
    session = AsyncMock()
    try:
        yield session
    finally:
        await session.close()


@pytest.fixture
def mock_redis() -> Generator[MagicMock]:
    """Cliente Redis mockado."""
    with patch("redis.asyncio.Redis") as mock_redis_class:
        redis_client = AsyncMock()
        mock_redis_class.return_value = redis_client

        # Comportamentos padrão úteis
        redis_client.get.return_value = None
        redis_client.set.return_value = True
        redis_client.delete.return_value = 1
        redis_client.exists.return_value = False

        yield redis_client


# =============================================================================
# FIXTURES DE REDE E HTTP
# =============================================================================


@pytest.fixture
async def http_client() -> AsyncGenerator[AsyncClient]:
    """Cliente HTTP async para testes de API."""
    async with AsyncClient(
        timeout=30.0,
        follow_redirects=True,
    ) as client:
        yield client


@pytest.fixture
def mock_httpx() -> Generator[MagicMock]:
    """Mock do httpx para testes de integração."""
    with patch("httpx.AsyncClient") as mock_client:
        client_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = client_instance

        # Response padrão
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_response.text = "OK"

        client_instance.get.return_value = mock_response
        client_instance.post.return_value = mock_response
        client_instance.put.return_value = mock_response
        client_instance.delete.return_value = mock_response

        yield client_instance


# =============================================================================
# FIXTURES DE AUTENTICAÇÃO E SEGURANÇA
# =============================================================================


@pytest.fixture
def mock_jwt_token() -> str:
    """Token JWT mockado para testes."""
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test.token"


@pytest.fixture
def mock_user() -> dict[str, Any]:
    """Usuário mockado para testes."""
    return {
        "id": "test-user-id",
        "email": "test@example.com",
        "username": "testuser",
        "is_active": True,
        "is_admin": False,
        "roles": ["user"],
        "permissions": ["read:profile"],
    }


@pytest.fixture
def authenticated_headers(mock_jwt_token: str) -> dict[str, str]:
    """Headers HTTP com autenticação."""
    return {
        "Authorization": f"Bearer {mock_jwt_token}",
        "Content-Type": "application/json",
    }


# =============================================================================
# FIXTURES DE DOMÍNIO E BUSINESS LOGIC
# =============================================================================


class MockPipeline(BaseModel):
    """Pipeline mockado para testes."""

    id: str = "test-pipeline-id"
    name: str = "Test Pipeline"
    description: str = "Pipeline for testing"
    is_active: bool = True
    config: dict[str, Any] = {}


@pytest.fixture
def mock_pipeline() -> MockPipeline:
    """Pipeline mockado para testes de domínio."""
    return MockPipeline()


@pytest.fixture
def mock_pipeline_execution() -> dict[str, Any]:
    """Execução de pipeline mockada."""
    return {
        "id": "test-execution-id",
        "pipeline_id": "test-pipeline-id",
        "status": "running",
        "started_at": "2025-07-05T10:00:00Z",
        "progress": 0.5,
        "logs": ["Starting execution", "Processing data"],
    }


# =============================================================================
# FIXTURES DE OBSERVABILIDADE E MONITORING
# =============================================================================


@pytest.fixture
def mock_metrics() -> Generator[MagicMock]:
    """Métricas mockadas para testes."""
    with (
        patch("prometheus_client.Counter") as mock_counter,
        patch("prometheus_client.Histogram") as mock_histogram,
        patch("prometheus_client.Gauge") as mock_gauge,
    ):
        # Criar instâncias mock
        counter_instance = MagicMock()
        histogram_instance = MagicMock()
        gauge_instance = MagicMock()

        mock_counter.return_value = counter_instance
        mock_histogram.return_value = histogram_instance
        mock_gauge.return_value = gauge_instance

        yield {
            "counter": counter_instance,
            "histogram": histogram_instance,
            "gauge": gauge_instance,
        }


@pytest.fixture
def mock_tracer() -> Generator[MagicMock]:
    """Tracer mockado para OpenTelemetry."""
    with patch("opentelemetry.trace.get_tracer") as mock_get_tracer:
        tracer = MagicMock()
        mock_get_tracer.return_value = tracer

        # Span mockado
        span = MagicMock()
        tracer.start_span.return_value.__enter__.return_value = span

        yield tracer


# =============================================================================
# FIXTURES DE SINGER/MELTANO
# =============================================================================


@pytest.fixture
def mock_singer_catalog() -> dict[str, Any]:
    """Catálogo Singer mockado."""
    return {
        "streams": [
            {
                "tap_stream_id": "users",
                "schema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "email": {"type": "string"},
                    },
                },
                "metadata": [
                    {
                        "breadcrumb": [],
                        "metadata": {
                            "replication-method": "INCREMENTAL",
                            "replication-key": "updated_at",
                        },
                    }
                ],
            }
        ]
    }


@pytest.fixture
def mock_singer_state() -> dict[str, Any]:
    """Estado Singer mockado."""
    return {
        "bookmarks": {
            "users": {
                "replication_key": "updated_at",
                "replication_key_value": "2025-07-05T10:00:00Z",
            }
        }
    }


# =============================================================================
# FIXTURES DE PLUGINS E EXTENSIBILIDADE
# =============================================================================


@pytest.fixture
def mock_plugin_manager() -> Generator[MagicMock]:
    """Plugin manager mockado."""
    with patch("flext_plugin.discovery.PluginDiscovery") as mock_discovery:
        discovery = MagicMock()
        mock_discovery.return_value = discovery

        # Plugins mockados
        discovery.scan.return_value = [
            {
                "name": "test-plugin",
                "version": "1.0.0",
                "entry_point": "test_plugin:main",
                "dependencies": [],
            }
        ]

        yield discovery


# =============================================================================
# FIXTURES DE CLI E INTERFACE
# =============================================================================


@pytest.fixture
def cli_runner() -> Generator[Any]:
    """Runner para testes de CLI."""
    try:
        from click.testing import CliRunner

        yield CliRunner()
    except ImportError:
        # Fallback se Click não estiver disponível
        yield MagicMock()


@pytest.fixture
def mock_stdin(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Input do usuário mockado para CLI."""
    mock_input = MagicMock()
    monkeypatch.setattr("builtins.input", mock_input)
    return mock_input


# =============================================================================
# FIXTURES DE PERFORMANCE E BENCHMARKING
# =============================================================================


@pytest.fixture
def benchmark_config() -> dict[str, Any]:
    """Configuração para benchmarks."""
    return {
        "min_rounds": 5,
        "max_time": 1.0,
        "disable_gc": False,
        "warmup": False,
    }


# =============================================================================
# FIXTURES DE LDAP E INTEGRAÇÃO
# =============================================================================


@pytest.fixture
def mock_ldap_connection() -> Generator[MagicMock]:
    """Conexão LDAP mockada."""
    with patch("ldap3.Connection") as mock_conn:
        connection = MagicMock()
        mock_conn.return_value = connection

        # Comportamentos padrão
        connection.bind.return_value = True
        connection.search.return_value = True
        connection.entries = []

        yield connection


# =============================================================================
# UTILITÁRIOS PARA TESTES
# =============================================================================


@pytest.fixture
def assert_logs():
    """Fixture para verificar logs em testes."""

    def _assert_logs(caplog, level: str, message: str) -> bool:
        """Verifica se uma mensagem de log foi registrada."""
        records = [r for r in caplog.records if r.levelname == level]
        return any(message in record.getMessage() for record in records)

    return _assert_logs


@pytest.fixture
def time_machine():
    """Fixture para manipular tempo em testes."""

    def _freeze_time(timestamp: str) -> None:
        """Congela o tempo em um timestamp específico."""
        # Implementar com freezegun se disponível

    return _freeze_time


# =============================================================================
# MARKS E CONFIGURAÇÕES CONDICIONAIS
# =============================================================================


def pytest_configure(config: pytest.Config) -> None:
    """Configuração personalizada do pytest."""
    # Registrar markers customizados
    config.addinivalue_line(
        "markers", "requires_docker: mark test as requiring Docker to run"
    )
    config.addinivalue_line(
        "markers", "expensive: mark test as computationally expensive"
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Modifica a coleção de testes com base em configurações."""
    # Marcar automaticamente testes lentos
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(pytest.mark.timeout(300))  # 5 minutos para testes lentos

        # Marcar testes que precisam de rede
        if "network" in item.name or "http" in item.name:
            item.add_marker(pytest.mark.requires_network)


# =============================================================================
# EXEMPLO DE USO NOS TESTES
# =============================================================================

"""
Exemplos de como usar as fixtures nos testes:

```python
async def test_api_endpoint(http_client: AsyncClient, authenticated_headers: dict):
    response = await http_client.get("/api/pipelines", headers=authenticated_headers)
    assert response.status_code == 200

def test_pipeline_creation(mock_pipeline: MockPipeline, db_session):
    # Teste de criação de pipeline
    assert mock_pipeline.id == "test-pipeline-id"

@pytest.mark.slow
async def test_large_data_processing(benchmark_config: dict):
    # Teste de performance para grandes volumes de dados
    pass

@pytest.mark.requires_database
def test_user_repository(db_session):
    # Teste que precisa de banco de dados
    pass
```
"""
