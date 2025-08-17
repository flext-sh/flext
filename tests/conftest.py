"""Configuração pytest global para o workspace FLEXT.

Este módulo resolve o problema de pytest_plugins em conftest.py não-top-level
e fornece configuração global para todos os projetos do workspace.
"""

import warnings
from pathlib import Path

import pytest

# Silenciar warnings conhecidos de dependências externas
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    module=r"pyasn1(\.|$)",
)

warnings.filterwarnings(
    "ignore",
    message="PydanticDeprecatedSince20",
    category=DeprecationWarning,
)


# Configuração global de marcadores pytest
def pytest_configure(config: pytest.Config) -> None:
    """Configura pytest com marcadores customizados globais."""
    # Marcadores padrão para todos os projetos
    markers = [
      "e2e: marca testes como testes de integração end-to-end",
      "integration: marca testes como testes de integração",
      "unit: marca testes como testes unitários",
      "slow: marca testes como execução lenta",
      "docker: marca testes que requerem Docker",
      "oracle: marca testes específicos do Oracle",
      "performance: marca testes de performance",
      "stress: marca testes de stress",
      "resilience: marca testes de resiliência",
      "integrity: marca testes de integridade",
      "edge_cases: marca testes de casos extremos",
    ]

    for marker in markers:
      config.addinivalue_line("markers", marker)

    # Filtros de warning globais
    config.addinivalue_line(
      "filterwarnings",
      "ignore::DeprecationWarning:pyasn1(\\.|$)",
    )
    config.addinivalue_line(
      "filterwarnings",
      "ignore:PydanticDeprecatedSince20:DeprecationWarning",
    )


# Fixtures globais compartilhadas
@pytest.fixture(scope="session")
def workspace_root() -> Path:
    """Obtém o diretório raiz do workspace FLEXT."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_data_dir(workspace_root: Path) -> Path:
    """Obtém o diretório de dados de teste do workspace."""
    return workspace_root / "data"
