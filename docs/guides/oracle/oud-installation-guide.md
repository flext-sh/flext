# OUD Automation - Instalação e Uso

## Instalação Padrão Python (PEP8)

### Pré-requisitos

- Python 3.9 ou superior
- pip (gerenciador de pacotes Python)
- venv (módulo de ambientes virtuais)

### Instalação via pip

#### 1. Criar ambiente virtual

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

#### 2. Instalar o pacote

##### Opção A: Instalação em modo desenvolvimento (recomendado para desenvolvimento)

```bash
# Clone o repositório
git clone https://github.com/youruser/oud-automation.git
cd oud-automation

# Instalar em modo desenvolvimento
pip install -e .

# Ou com dependências de desenvolvimento
pip install -e ".[dev]"
```

##### Opção B: Instalação direta

```bash
# Instalar diretamente do diretório
pip install .

# Ou com dependências de desenvolvimento
pip install ".[dev]"
```

##### Opção C: Instalação do arquivo wheel

```bash
# Construir o pacote
python -m build

# Instalar do arquivo wheel
pip install dist/oud_automation-1.0.0-py3-none-any.whl
```

### Configuração

1. Copie o arquivo de configuração exemplo:

```bash
cp .env.example .env
```

2. Edite o arquivo `.env` com suas configurações:

```bash
# Editar com seu editor preferido
vim .env
# ou
nano .env
```

### Uso

Após a instalação, o comando `oud-cli` estará disponível:

```bash
# Verificar instalação
oud-cli --help

# Verificar versão
oud-cli version

# Comandos básicos
oud-cli ldif-process input.ldif
oud-cli schema-migrate --from-oid
oud-cli ldap-search --filter "(uid=john*)"
oud-cli test-connection
oud-cli health
```

### Executar sem instalar

Se preferir executar sem instalar:

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar diretamente
python -m oud_automation.cli.simple_cli --help
```

### Desenvolvimento

#### Configurar ambiente de desenvolvimento

```bash
# Instalar em modo desenvolvimento com todas as ferramentas
pip install -e ".[dev]"

# Instalar pre-commit hooks (opcional)
pre-commit install
```

#### Executar testes

```bash
# Executar todos os testes
pytest

# Com cobertura
pytest --cov=oud_automation

# Testes específicos
pytest tests/test_cli.py
```

#### Verificar qualidade do código

```bash
# Formatação com Black (PEP8)
black src tests

# Verificar com flake8
flake8 src tests

# Verificar com ruff
ruff check src tests

# Verificar tipos com mypy
mypy src
```

#### Construir pacote

```bash
# Instalar ferramentas de build
pip install build

# Construir pacote
python -m build

# Arquivos gerados:
# dist/oud_automation-1.0.0.tar.gz
# dist/oud_automation-1.0.0-py3-none-any.whl
```

### Estrutura do Projeto

```
oud-automation/
├── src/
│   └── oud_automation/
│       ├── __init__.py
│       ├── cli/
│       │   ├── __init__.py
│       │   └── simple_cli.py      # CLI principal
│       ├── config.py              # Configuração
│       ├── ldap_connection.py     # Conexão LDAP
│       ├── ldif_processor.py      # Processador LDIF
│       └── schema_manager.py      # Gerenciador de schema
├── tests/
│   ├── __init__.py
│   └── test_cli.py
├── .env.example                   # Exemplo de configuração
├── .flake8                        # Configuração flake8
├── pyproject.toml                 # Configuração do projeto
├── setup.py                       # Script de instalação
├── MANIFEST.in                    # Arquivos incluídos
└── README.md                      # Documentação
```

### Desinstalação

Para remover o pacote:

```bash
pip uninstall oud-automation
```

### Troubleshooting

#### Comando não encontrado

Se o comando `oud-cli` não for encontrado após a instalação:

1. Verifique se o ambiente virtual está ativado
2. Verifique se o pip instalou os scripts:

   ```bash
   pip show -f oud-automation | grep oud-cli
   ```

3. Execute diretamente:

   ```bash
   python -m oud_automation.cli.simple_cli
   ```

#### Problemas de importação

Se houver erros de importação:

1. Verifique se está no diretório correto
2. Verifique se o pacote foi instalado:

   ```bash
   pip list | grep oud-automation
   ```

3. Reinstale em modo desenvolvimento:

   ```bash
   pip install -e .
   ```

### Integração com Poetry (Alternativa)

Se preferir usar Poetry:

```bash
# Instalar poetry
pip install poetry

# Instalar dependências
poetry install

# Executar com poetry
poetry run oud-cli --help
```
