# OUD Automation - PEP8 Compliant Python Project

Este projeto segue rigorosamente o padrão PEP8 para código Python, sem uso de scripts shell ou artimanhas.

## Características

- ✅ **100% Python puro** - Sem scripts shell
- ✅ **PEP8 compliant** - Linhas de até 79 caracteres
- ✅ **Instalação padrão Python** - pip install
- ✅ **Entry points Python** - Console scripts
- ✅ **Configuração via .env** - Carregamento automático

## Instalação

### Via pip (Recomendado)

```bash
# Criar e ativar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate  # Windows

# Instalar o pacote
pip install .

# Ou em modo desenvolvimento
pip install -e .

# Com ferramentas de desenvolvimento
pip install -e ".[dev]"
```

### Via Poetry

```bash
# Instalar poetry
pip install poetry

# Instalar dependências
poetry install

# Executar via poetry
poetry run oud-cli --help
```

## Uso

### Como comando instalado

Após a instalação, o comando `oud-cli` estará disponível:

```bash
# Ajuda
oud-cli --help

# Versão
oud-cli version

# Processar LDIF
oud-cli ldif-process arquivo.ldif

# Buscar no LDAP
oud-cli ldap-search --filter "(uid=user*)"

# Testar conexão
oud-cli test-connection
```

### Como módulo Python

```bash
# Executar como módulo
python -m oud_automation --help

# Ou diretamente
python -m oud_automation.cli.cli_pep8 --help
```

### Importar em código Python

```python
from oud_automation.cli.cli_pep8 import OudCliApplication
from oud_automation.config import OudConfig

# Criar aplicação
app = OudCliApplication()

# Executar comando
import asyncio
asyncio.run(app.test_connection())
```

## Configuração

### Arquivo .env

Crie um arquivo `.env` na raiz do projeto:

```env
# Configuração LDAP
LDAP_HOST=ldap.example.com
LDAP_PORT=389
LDAP_BIND_DN=cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com
LDAP_BIND_PASSWORD=secretpassword
LDAP_BASE_DN=dc=example,dc=com
LDAP_USE_SSL=false
LDAP_TIMEOUT=30.0

# Configuração OUD
OUD_INSTANCE_DIR=/opt/oracle/oud/instances/oud1
OUD_ADMIN_PORT=4444
OUD_BACKEND_ID=userRoot

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/oud_automation.log
```

## Desenvolvimento

### Configurar ambiente

```bash
# Clonar repositório
git clone https://github.com/youruser/oud-automation.git
cd oud-automation

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar em modo desenvolvimento
pip install -e ".[dev]"
```

### Executar testes

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=oud_automation

# Teste específico
pytest tests/test_cli.py -v
```

### Verificar código PEP8

```bash
# Formatar com Black (79 chars)
black --line-length 79 src tests

# Verificar com flake8
flake8 src tests

# Verificar com ruff
ruff check src tests

# Verificar tipos
mypy src
```

### Construir pacote

```bash
# Instalar build tools
pip install build

# Construir
python -m build

# Resultado:
# dist/oud_automation-1.0.0-py3-none-any.whl
# dist/oud_automation-1.0.0.tar.gz
```

## Estrutura do Projeto

```
oud-automation/
├── src/
│   └── oud_automation/
│       ├── __init__.py
│       ├── __main__.py              # Entry point do módulo
│       ├── __version__.py           # Versão do pacote
│       ├── cli/
│       │   ├── __init__.py
│       │   └── cli_pep8.py         # CLI PEP8 compliant
│       ├── config.py                # Configuração
│       ├── ldap_connection.py       # Conexão LDAP
│       ├── ldif_processor_simple.py # Processador LDIF
│       └── schema_manager.py        # Gerenciador de schema
├── tests/
│   ├── __init__.py
│   └── test_*.py
├── .env.example
├── .flake8                          # Configuração flake8
├── pyproject.toml                   # Configuração Poetry/PEP517
├── setup.py                         # Setup tradicional
├── MANIFEST.in                      # Arquivos incluídos
├── requirements.txt                 # Dependências
└── requirements-dev.txt             # Dependências dev
```

## Padrões de Código

### PEP8 Enforced

- Máximo 79 caracteres por linha
- 4 espaços para indentação
- 2 linhas em branco entre classes
- 1 linha em branco entre métodos
- Imports organizados (stdlib, third-party, local)

### Exemplo de código PEP8

```python
"""Módulo exemplo seguindo PEP8."""

import os
import sys
from pathlib import Path

import click
from dotenv import load_dotenv


class ExampleClass:
    """Classe exemplo com docstring."""
    
    def __init__(self, name: str) -> None:
        """Inicializa a classe.
        
        Args:
            name: Nome do exemplo
        """
        self.name = name
    
    def process(self, data: str) -> str:
        """Processa dados.
        
        Args:
            data: Dados para processar
            
        Returns:
            Dados processados
        """
        # Linha longa dividida corretamente
        result = (
            f"Processando {data} "
            f"com nome {self.name}"
        )
        return result
```

## Publicação

### PyPI

```bash
# Construir
python -m build

# Upload para TestPyPI
twine upload --repository testpypi dist/*

# Upload para PyPI
twine upload dist/*
```

### Instalação do PyPI

```bash
# Do PyPI
pip install oud-automation

# Do TestPyPI
pip install -i https://test.pypi.org/simple/ oud-automation
```

## Licença

MIT License - veja LICENSE para detalhes.
