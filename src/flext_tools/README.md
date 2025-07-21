# 🛠️ FLEXT Tools - Biblioteca Modular

Biblioteca Python para gerenciamento modular de dependências e análise de projetos no workspace FLEXT.

## 🎯 Objetivo

Reduzir a complexidade dos scripts monolíticos dividindo funcionalidades em módulos testáveis e reutilizáveis.

## 📦 Módulos

### 🔍 Discovery

Descoberta automática de dependências em projetos Python.

```python
from flext_tools import DependencyDiscovery

discovery = DependencyDiscovery()
missing_deps = discovery.discover_project_dependencies(project_path)
```

**Funcionalidades:**

- Análise de imports Python via AST
- Descoberta em arquivos de configuração (.pre-commit-config.YAML, tox.ini, etc)
- Mapeamento inteligente de nomes de pacotes (cv2 → opencv-Python)
- Detecção automática de módulos da stdlib
- Filtros para arquivos internos do projeto

### 📊 Analysis

Análise de versões e conflitos entre projetos.

```python
from flext_tools import VersionAnalyzer, ConflictAnalyzer

# Análise de versões
analyzer = VersionAnalyzer()
compatibility = analyzer.check_version_compatibility([">=1.0", "<2.0"], "django")

# Análise de conflitos
conflict_analyzer = ConflictAnalyzer()
conflicts = conflict_analyzer.analyze_workspace_conflicts(workspace_path)
```

**Funcionalidades:**

- Parsing de constraints de versão (^, ~, >=, etc)
- Detecção de conflitos entre projetos
- Identificação de bloqueadores de atualização
- Sugestões de resolução automática
- Relatórios formatados em Markdown

### 🎭 Poetry

Operações com Poetry de forma programática.

```python
from flext_tools import PoetryOperations, PoetryValidator

# Operações
ops = PoetryOperations(dry_run=True)
added = ops.add_dependencies(project_path, missing_deps)

# Validação
validator = PoetryValidator()
validation = validator.validate_project(project_path)
```

**Funcionalidades:**

- Adição automática de dependências
- Atualização de versões no pyproject.toml
- Validação de configurações Poetry
- Modo dry-run para simulação
- Verificação de poetry.lock

### 💾 Cache

Sistema de cache inteligente para performance.

```python
from flext_tools import cached, CacheManager

@cached(namespace="discovery", ttl=3600)
def expensive_operation():
    return compute_something()

# Ou uso direto
cache = CacheManager()
result = cache.get_cached_or_compute("key", lambda: compute())
```

**Funcionalidades:**

- Decoradores para cache automático
- Cache em disco com TTL
- Locks para concorrência
- Estatísticas de hit/miss
- Limpeza automática de expirados

### 🎨 Utils

Utilitários comuns para todos os módulos.

```python
from flext_tools import print_colored, Colors, get_stdlib_modules

print_colored("Sucesso!", Colors.GREEN)
stdlib = get_stdlib_modules()
```

**Funcionalidades:**

- Cores para terminal
- Lista de módulos da stdlib
- Filtros de caminhos
- Utilitários de path

## 🚀 Scripts Refatorados

### Principais Scripts

1. **sync_dependencies.py** - Sincronização completa de dependências
2. **discover_missing_deps.py** - Descoberta de dependências faltantes
3. **analyze_who_blocks_updates.py** - Análise de conflitos e bloqueadores
4. **validate_poetry_projects.py** - Validação de projetos Poetry
5. **quality_gateway.py** - Gateway de qualidade completo
6. **workspace_status.py** - Status geral do workspace

### Comparação: Antes vs Depois

**Antes (monolítico):**

```python
# sync_dependencies.py - 3400+ linhas
# Lógica misturada, difícil de testar
# Performance ruim (7+ segundos)
# Código duplicado entre scripts
```

**Depois (modular):**

```python
# sync_dependencies.py - 200 linhas
from flext_tools import DependencyDiscovery, ConflictAnalyzer

discovery = DependencyDiscovery()
analyzer = ConflictAnalyzer()
# Lógica clara, testável, rápida
```

## 📈 Benefícios

### ✅ Performance

- **Cache inteligente**: Evita recomputação desnecessária
- **Análise incremental**: Processa apenas o que mudou
- **Paralelização**: Cache permite execução concorrente

### ✅ Manutenibilidade

- **Módulos pequenos**: Cada módulo tem responsabilidade única
- **Testabilidade**: Unidades testáveis independentemente
- **Reutilização**: Funcionalidades compartilhadas entre scripts

### ✅ Confiabilidade

- **Validação**: Cada operação é validada antes de executar
- **Dry-run**: Simulação antes de modificações reais
- **Error handling**: Tratamento robusto de erros

### ✅ Usabilidade

- **Interface consistente**: Padrões unificados entre módulos
- **Documentação**: Cada função tem docstring detalhada
- **Feedback visual**: Cores e ícones para melhor UX

## 🔧 Uso Rápido

### Descobrir dependências faltantes

```bash
python discover_missing_deps.py --dry-run
```

### Análise completa de conflitos

```bash
python analyze_who_blocks_updates.py --report
```

### Sincronização completa

```bash
python sync_dependencies.py --dry-run
```

### Quality gateway

```bash
python quality_gateway.py --strict
```

### Status do workspace

```bash
python workspace_status.py
```

## 🧪 Exemplo de Uso

```python
#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from flext_tools import (
    DependencyDiscovery,
    ConflictAnalyzer,
    PoetryOperations,
    cached
)

# Descoberta com cache
@cached(ttl=600)
def discover_deps(project_path):
    discovery = DependencyDiscovery()
    return discovery.discover_project_dependencies(project_path)

# Análise de conflitos
analyzer = ConflictAnalyzer()
conflicts = analyzer.analyze_workspace_conflicts(Path.cwd())

# Operações Poetry
ops = PoetryOperations(dry_run=True)
# ... suas operações
```

## 📝 Arquitetura

```
flext_tools/
├── __init__.py          # API principal
├── discovery/           # Descoberta de dependências
│   ├── base.py         # Classe principal
│   ├── python.py       # Análise de imports Python
│   └── config.py       # Análise de configs
├── analysis/            # Análise de versões
│   ├── version.py      # Análise de versões
│   └── conflicts.py    # Análise de conflitos
├── poetry/              # Operações Poetry
│   ├── operations.py   # Operações CRUD
│   └── validator.py    # Validação
├── cache/               # Sistema de cache
│   ├── manager.py      # Gerenciador de cache
│   └── decorators.py   # Decoradores
└── utils/               # Utilitários
    ├── colors.py       # Cores de terminal
    ├── stdlib.py       # Módulos stdlib
    └── paths.py        # Utilitários de path
```

## 🎯 Próximos Passos

1. **Testes unitários** para cada módulo
2. **CI/CD integration** para validação automática
3. **Plugin system** para extensibilidade
4. **Web dashboard** para visualização
5. **Metrics collection** para monitoramento

---

**Versão**: 0.1.0  
**Mantido por**: FLEXT Team  
**Licença**: Uso interno
