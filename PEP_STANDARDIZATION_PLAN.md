# PEP STANDARDIZATION MASTER PLAN - FLEXT WORKSPACE

## 🎯 OBJETIVO

Padronizar completamente o workspace FLEXT e todos os subprojetos de acordo com as diretrizes PEP (Python Enhancement Proposals) para organização de projetos, filesystem, ferramentas, diretórios, nomes de arquivos, funções e chamadas.

### 🚨 FOCO ESPECIAL DESTA EXECUÇÃO

1. **Configurar exceções em pyproject.toml**: Violações de estilo não-críticas, warnings e deprecated
2. **Auditar e limpar comentários de supressão**: `# type: ignore`, `# noqa`, etc.
3. **Adicionar justificativas**: Todo ignore mantido deve ter comentário explicativo
4. **Execução manual e contextualizada**: Projeto por projeto, respeitando contexto

## 📋 CHECKLIST DE VERIFICAÇÃO PEP

### ✅ PEP 8 - Style Guide for Python Code

- [ ] Nomes de módulos: lowercase com underscores
- [ ] Nomes de classes: CapWords (CamelCase)
- [ ] Nomes de funções: lowercase com underscores
- [ ] Nomes de constantes: UPPERCASE com underscores
- [ ] Nomes de variáveis: lowercase com underscores
- [ ] Indentação: 4 espaços (sem tabs)
- [ ] Linha máxima: 79 caracteres (código), 72 (comentários)
- [ ] Imports organizados: stdlib, third-party, local

### ✅ PEP 257 - Docstring Conventions

- [ ] Docstrings em todos os módulos públicos
- [ ] Docstrings em todas as classes públicas
- [ ] Docstrings em todas as funções públicas
- [ ] Formato: """One-line summary.""" ou multi-line
- [ ] Docstrings começam com letra maiúscula
- [ ] Docstrings terminam com ponto final

### ✅ PEP 420 - Implicit Namespace Packages

- [ ] Sem **init**.py em namespace packages
- [ ] **init**.py apenas em regular packages
- [ ] Estrutura de namespaces consistente

### ✅ PEP 440 - Version Identification

- [ ] Versionamento semântico: MAJOR.MINOR.PATCH
- [ ] Pre-releases: X.Y.ZaN (alpha), X.Y.ZbN (beta), X.Y.ZrcN (release candidate)
- [ ] Dev releases: X.Y.Z.devN
- [ ] Post releases: X.Y.Z.postN

### ✅ PEP 484 - Type Hints

- [ ] Type hints em todas as funções públicas
- [ ] Type hints em parâmetros e retornos
- [ ] Uso de typing module quando necessário
- [ ] Compatibilidade com mypy

### ✅ PEP 517/518 - Build System

- [ ] pyproject.toml como arquivo de configuração principal
- [ ] [build-system] section definida
- [ ] [project] metadata completa
- [ ] Dependencies bem definidas
- [ ] Optional dependencies organizadas

## 🏗️ ESTRUTURA DE DIRETÓRIOS PEP-COMPLIANT

### Estrutura Padrão para Projetos Python

```
project_name/
├── src/
│   └── package_name/
│       ├── __init__.py
│       ├── module_name.py
│       └── subpackage/
│           ├── __init__.py
│           └── another_module.py
├── tests/
│   ├── __init__.py
│   ├── test_module_name.py
│   └── integration/
│       └── test_integration.py
├── docs/
│   ├── conf.py
│   ├── index.rst
│   └── api/
├── scripts/
│   └── utility_script.py
├── .github/
│   └── workflows/
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
├── .gitignore
├── .pre-commit-config.yaml
└── Makefile
```

### Estrutura para Projetos Go (seguindo convenções Go)

```
project_name/
├── cmd/
│   └── app_name/
│       └── main.go
├── internal/
│   ├── package_name/
│   └── another_package/
├── pkg/
│   └── public_package/
├── api/
│   └── openapi.yaml
├── scripts/
├── docs/
├── go.mod
├── go.sum
├── Makefile
├── README.md
└── .gitignore
```

## 📝 CONVENÇÕES DE NOMENCLATURA

### Python Files & Modules

- ✅ `module_name.py` (lowercase com underscores)
- ❌ `moduleName.py`, `ModuleName.py`, `module-name.py`

### Python Functions & Variables

- ✅ `def calculate_total_price():`
- ✅ `user_name = "John"`
- ❌ `def calculateTotalPrice():`, `def CalculateTotalPrice():`

### Python Classes

- ✅ `class UserAccount:`
- ✅ `class HTTPConnection:`
- ❌ `class user_account:`, `class User_Account:`

### Python Constants

- ✅ `MAX_CONNECTIONS = 100`
- ✅ `DEFAULT_TIMEOUT = 30`
- ❌ `max_connections = 100`, `MaxConnections = 100`

### Diretórios

- ✅ `src/`, `tests/`, `docs/`, `scripts/`
- ✅ `package_name/`, `sub_package/`
- ❌ `Src/`, `Tests/`, `package-name/`

## 🔧 FERRAMENTAS DE PADRONIZAÇÃO

### Linters & Formatters

1. **ruff** - Fast Python linter (substitui flake8, isort, etc.)
2. **black** - Opinionated code formatter
3. **isort** - Import sorting
4. **mypy** - Static type checker
5. **pylint** - Comprehensive linter (opcional)

### Pre-commit Hooks

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.5
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

## 📊 PLANO DE EXECUÇÃO DETALHADO

### 🔍 PROCESSO POR PROJETO

Para cada projeto, seguir rigorosamente:

#### 1. ANÁLISE INICIAL (Não modificar nada ainda!)
```bash
cd projeto
# Capturar estado atual
make lint > lint_report_inicial.txt 2>&1 || ruff check . > lint_report_inicial.txt 2>&1

# Contar violações por tipo
grep -E "^[A-Z][0-9]+" lint_report_inicial.txt | cut -d: -f1 | sort | uniq -c

# Auditar comentários de supressão
grep -r "# type: ignore" src/ --include="*.py" > type_ignores.txt
grep -r "# noqa" src/ --include="*.py" > noqa_comments.txt
grep -r "# pylint:" src/ --include="*.py" > pylint_disables.txt
```

#### 2. CATEGORIZAÇÃO DE VIOLAÇÕES

**Violações CRÍTICAS (corrigir imediatamente):**
- F821: Undefined name
- E999: Syntax error
- F401: Module imported but unused (pode indicar problema)
- E902: IO Error
- F823: Local variable referenced before assignment

**Violações NÃO-CRÍTICAS (candidatas a exceções):**
- E501: Line too long (se for URL, SQL, etc.)
- C901: Function too complex (se refatoração for arriscada)
- D100-D107: Missing docstrings (código legacy)
- N801-N807: Naming conventions (se quebrar API)
- W503/W504: Line break before/after binary operator

**Warnings e Deprecated (configurar exceções):**
- DeprecationWarning
- FutureWarning
- PendingDeprecationWarning

#### 3. CONFIGURAÇÃO DE EXCEÇÕES EM pyproject.toml

```toml
[tool.ruff]
# Configuração base
line-length = 88  # Compatível com Black
target-version = "py39"  # Ou versão mínima do projeto

# Exceções justificadas - NÃO-CRÍTICAS
ignore = [
    # Comprimento de linha
    "E501",  # Line too long - permitir em URLs, queries SQL, etc.
    
    # Docstrings (código legacy)
    "D100",  # Missing docstring in public module
    "D101",  # Missing docstring in public class
    "D102",  # Missing docstring in public method
    "D103",  # Missing docstring in public function
    "D104",  # Missing docstring in public package
    "D105",  # Missing docstring in magic method
    
    # Complexidade (refatoração arriscada)
    "C901",  # Function is too complex
    
    # Convenções de nome (quebrariam API)
    "N802",  # Function name should be lowercase
    "N803",  # Argument name should be lowercase
    "N806",  # Variable in function should be lowercase
]

# Exceções por arquivo/diretório
[tool.ruff.per-file-ignores]
"tests/*" = ["D100", "D101", "D102", "D103"]  # Tests não precisam docstrings
"legacy/*" = ["ALL"]  # Código legacy - não tocar
"migrations/*" = ["E501", "D100"]  # Migrations podem ter linhas longas

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true

# Ignorar erros em módulos específicos
[[tool.mypy.overrides]]
module = "legacy.*"
ignore_errors = true  # Código legacy não tipado

[[tool.mypy.overrides]]
module = "tests.*"
disable_error_code = ["misc", "arg-type"]  # Tests podem ser mais flexíveis
```

#### 4. LIMPEZA DE COMENTÁRIOS DE SUPRESSÃO

**Regras para manter `# type: ignore`:**
```python
# RUIM - sem justificativa
result = external_lib.method()  # type: ignore

# BOM - justificado
result = external_lib.method()  # type: ignore[no-untyped-call]  # Biblioteca sem type stubs

# BOM - específico sobre o erro
data: Any = json.loads(response)  # type: ignore[no-any-return]  # JSON pode retornar qualquer tipo
```

**Regras para `# noqa`:**
```python
# RUIM - muito genérico
from module import *  # noqa

# BOM - específico
from module import *  # noqa: F403  # Import necessário para re-exportar API

# BOM - justificado
long_sql = "SELECT * FROM users WHERE status = 'active' AND created > '2024-01-01'"  # noqa: E501  # Query SQL legível
```

#### 5. VALIDAÇÃO E QUALITY GATES

```bash
# Após mudanças, SEMPRE executar:
make check || (make lint && make typecheck && make test)

# Verificar que não criamos novos problemas
make lint > lint_report_final.txt 2>&1
diff lint_report_inicial.txt lint_report_final.txt

# Garantir que testes passam
make test

# Verificar que não há scripts proibidos
find . -name "fix_*.py" -o -name "temp_*.py" | grep -v tests/
```

### 📅 ORDEM DE EXECUÇÃO DOS PROJETOS

#### FASE 1 - Core Framework (Alta Prioridade)
1. **flext-core** - Base de tudo, deve estar perfeito
2. **flext-auth** - Segurança crítica
3. **flext-grpc** - Comunicação
4. **flext-web** - Interface usuário
5. **flext-cli** - Interface comando

#### FASE 2 - Serviços e Integrações
6. **flext-plugin** - Sistema de plugins
7. **flext-observability** - Monitoramento
8. **flext-meltano** - ETL
9. **flext-ldap** - Autenticação LDAP
10. **flext-db-oracle** - Banco de dados

#### FASE 3 - Conectores Singer/Meltano
11. **flext-tap-ldap**
12. **flext-tap-oracle-oic**
13. **flext-tap-oracle-wms**
14. **flext-target-oracle**
15. **flext-target-oracle-oic**
16. **flext-target-oracle-wms**

#### FASE 4 - Extensões e Enterprise
17. **flext-oracle-oic-ext**
18. **flext-quality**
19. **algar-oud-mig**
20. **gruponos-poc-oic-wms**

## 🚦 QUALITY GATES

### Por Projeto

- [ ] Sem erros de ruff
- [ ] Formatado com black
- [ ] Imports organizados com isort
- [ ] Type hints validados com mypy
- [ ] Testes passando
- [ ] Documentação atualizada

### Por Workspace

- [ ] Todos os projetos seguem mesma estrutura
- [ ] Convenções de nomenclatura consistentes
- [ ] Ferramentas configuradas uniformemente
- [ ] CI/CD validando padrões
- [ ] Documentação centralizada

## 📈 MÉTRICAS DE SUCESSO

1. **Conformidade PEP**: 100% dos arquivos Python
2. **Cobertura de Type Hints**: >90% das funções públicas
3. **Documentação**: 100% dos módulos públicos com docstrings
4. **Testes**: Todos os projetos com testes automatizados
5. **CI/CD**: Validação automática em todos os commits

## ⚠️ RISCOS E MITIGAÇÕES

### Riscos

1. Quebrar funcionalidade existente durante reorganização
2. Conflitos com código em desenvolvimento
3. Resistência a mudanças de convenções
4. Tempo necessário para migração completa

### Mitigações

1. Fazer backup completo antes de mudanças
2. Executar em branches separadas
3. Migração gradual por projeto
4. Testes extensivos após cada mudança
5. Documentar todas as decisões

## 🔄 PROCESSO CONTÍNUO

### Daily

- Validar novos commits com pre-commit
- Executar quality gates em CI/CD

### Weekly

- Review de conformidade PEP
- Atualizar documentação

### Monthly

- Avaliar novas PEPs relevantes
- Atualizar ferramentas
- Treinar equipe em padrões

---

**IMPORTANTE**: Este plano deve ser executado de forma metódica e cuidadosa, sempre validando que a funcionalidade não foi afetada após cada mudança. Usar controle de versão para permitir rollback se necessário.
