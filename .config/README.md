# FLEXT Configuration Directory

**Modern Configuration Organization (2024 Best Practices)**

Este diretório centraliza todas as configurações especializadas seguindo boas práticas modernas para monorepos híbridos Go/Python.

## Estrutura Organizada

### 📦 `/docker/` - Configurações Docker
- `docker-compose.yml` - Configuração principal
- `docker-compose.override.yml` - Overrides para desenvolvimento
- `docker-compose.test.yml` - Configuração para testes

### 🔧 `/build/` - Configurações de Build
- `Makefile.build` - Receitas de build avançadas
- `Makefile.docker` - Comandos Docker especializados
- `Makefile.docs` - Geração de documentação
- `Makefile.workspace` - Comandos de workspace

### 🛠️ `/tools/` - Configurações de Ferramentas
- `.pre-commit.yaml` - Hooks de pre-commit
- `mkdocs.yml` - Configuração de documentação
- `.ruff-shared.toml` - Configuração compartilhada do Ruff

### 💻 `/dev-environment/` - Ambiente de Desenvolvimento
- `config.yaml` - Configuração geral
- `meltano.yml` - Configuração do Meltano
- `pyrightconfig.json` - Configuração do PyRight

### 📁 `/ci/` - CI/CD (Futuro)
- Reservado para configurações de CI/CD específicas

## Convenções

### ✅ Boas Práticas Implementadas
- **Separação por responsabilidade** - Cada diretório tem uma função específica
- **Configurações centralizadas** - Evita configurações espalhadas
- **Hierarquia clara** - Fácil localização de arquivos
- **Compatibilidade com ferramentas** - Mantém funcionalidade existente

### 📋 Como Usar

#### Para usar configurações Docker:
```bash
docker-compose -f .config/docker/docker-compose.yml up
```

#### Para usar Makefiles especializados:
```bash
make -f .config/build/Makefile.docker build
make -f .config/build/Makefile.docs serve-docs
```

#### Para ferramentas de desenvolvimento:
```bash
pre-commit run --all-files  # Busca automaticamente .config/tools/.pre-commit.yaml
mkdocs serve               # Busca automaticamente .config/tools/mkdocs.yml
```

## Migração da Configuração Legacy

### Arquivos Movidos
- ❌ `~/flext/docker-compose*.yml` → ✅ `.config/docker/`
- ❌ `~/flext/Makefile.*` → ✅ `.config/build/`
- ❌ `~/flext/.pre-commit.yaml` → ✅ `.config/tools/`
- ❌ Arquivos temporários removidos (*.log, *.coverage, *.json)

### Arquivos Mantidos no Root
- ✅ `Makefile` - Makefile principal (padrão)
- ✅ `pyproject.toml` - Configuração Python principal
- ✅ `poetry.toml` - Configuração Poetry
- ✅ `go.mod` - Dependências Go

## Compatibilidade

Todas as ferramentas continuam funcionando normalmente. O Makefile principal no root referencia as configurações especializadas quando necessário.

**Benefícios da Reorganização:**
- 🧹 Workspace mais limpa e organizada  
- 🔍 Localização intuitiva de configurações
- 🚀 Melhores práticas modernas aplicadas
- 📚 Separação clara entre dev/prod/build/tools
- 🎯 Facilita manutenção e colaboração

---
*Reorganizado seguindo padrões modernos de monorepo 2024 para híbrido Go/Python*