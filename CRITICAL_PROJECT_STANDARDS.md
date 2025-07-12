# CRITICAL PROJECT STANDARDS - FLEXT WORKSPACE

**ATENÇÃO EXTREMA**: Este documento contém os padrões REAIS de CADA projeto.
**NUNCA** modifique arquivos sem consultar este documento!

## 🔴 REGRA SUPREMA: NUNCA MODIFICAR SEM PERMISSÃO EXPLÍCITA

### Arquivos INTOCÁVEIS em TODOS os projetos

- `pyproject.toml` - Define dependências e estrutura
- `.gitignore` - Regras de versionamento
- `Makefile` - Automação padronizada
- `.env` - Configurações e secrets
- `docker-compose*.yml` - Infraestrutura
- `go.mod/go.sum` - Dependências Go
- `package.json` - Dependências JS

---

## PROJETO 1: flext-core

### 📋 CONFIGURAÇÃO VERIFICADA

- **pyproject.toml**: ✅ EXISTS - Poetry, Python 3.13
- **Makefile**: ✅ EXISTS - Comandos: check, test, lint, format, type-check
- **.gitignore**: ✅ EXISTS - 235 linhas, exclui fix_*.py
- **requirements.txt**: ❌ ARCHIVED - Usa Poetry
- **.env/.env.example**: ✅ BOTH EXIST
- **CLAUDE.md**: ⚠️ ARCHIVED - Criar novo no root

### 🛠️ PADRÕES ESTABELECIDOS

```bash
# COMANDOS CORRETOS:
make check      # Roda TUDO: format, lint, type, test
make test       # Roda pytest
make lint       # Roda ruff
make format     # Roda ruff format + isort

# DEBUG:
PYTHONPATH=. python -m module --debug
LOG_LEVEL=DEBUG python script.py
```

### ❌ PROIBIDO

- Criar fix_*.py (já no .gitignore)
- Modificar pyproject.toml (Poetry gerenciado)
- Alterar estrutura src/flext/core/

---

## PROJETO 2: flext-api

### 📋 CONFIGURAÇÃO VERIFICADA

- **pyproject.toml**: ✅ EXISTS - Poetry, Python
- **Makefile**: ✅ EXISTS - Comandos: api-serve, api-serve-prod, docker-build
- **.gitignore**: ✅ EXISTS
- **Linguagem**: Python (FastAPI/REST)

### 🛠️ PADRÕES ESTABELECIDOS

```bash
# COMANDOS CORRETOS:
make api-serve      # Dev server com reload
make api-serve-prod # Prod com 4 workers
make test          # Roda pytest
make lint-fix      # Ruff fix

# NUNCA USAR:
python main.py     # USE make api-serve
```

---

## PROJETO 3: flext-auth

### 📋 CONFIGURAÇÃO VERIFICADA

- **pyproject.toml**: ✅ EXISTS - Poetry, Python
- **Makefile**: ✅ EXISTS - Comandos: cli-test, security
- **.gitignore**: ✅ EXISTS
- **Linguagem**: Python (Autenticação)

### 🛠️ PADRÕES ESTABELECIDOS

```bash
# COMANDOS CORRETOS:
make cli-test    # Testa sistema de auth
make security    # Bandit security check
make test        # Roda pytest
```

---

## PROJETO 4: flext-cli

### 📋 CONFIGURAÇÃO VERIFICADA

- **pyproject.toml**: ✅ EXISTS - Poetry, Python
- **Makefile**: ✅ EXISTS - Comandos: cli-help, cli-demo, plugin-scaffold
- **.gitignore**: ✅ EXISTS
- **Linguagem**: Python (CLI)

### 🛠️ PADRÕES ESTABELECIDOS

```bash
# COMANDOS CORRETOS:
make cli-help       # Mostra ajuda
make cli-demo       # Roda demos
make plugin-scaffold # Cria plugin template
```

---

## PROJETO 5: flext-web

### 📋 CONFIGURAÇÃO VERIFICADA

- **pyproject.toml**: ✅ EXISTS - Poetry, Python/Django
- **Makefile**: ✅ EXISTS - Comandos: dev
- **.gitignore**: ✅ EXISTS
- **⚠️ PROBLEMA**: Makefile linha 121 tem erro de template

### 🛠️ PADRÕES ESTABELECIDOS

```bash
# COMANDOS CORRETOS:
make dev    # Django runserver debug
make check  # Todos os checks
```

---

## PROJETO 6: flext-grpc

### 📋 CONFIGURAÇÃO VERIFICADA

- **pyproject.toml**: ✅ EXISTS - Poetry, Python/gRPC
- **Makefile**: ✅ EXISTS
- **.gitignore**: ✅ EXISTS
- **⚠️ PROBLEMA**: Makefile linha 121 tem erro de template

### 🛠️ PADRÕES ESTABELECIDOS

```bash
# COMANDOS CORRETOS:
make dev    # gRPC server debug
make check  # Todos os checks
```

---

## 🚨 PROBLEMAS ENCONTRADOS

1. **flext-plugin**: TEM arquivo `fix_syntax_errors.py` - DEVE SER REMOVIDO
2. **flext-web** e **flext-grpc**: Erro no Makefile linha 121
3. **Scripts em /scripts/**: 74 arquivos incluindo vários fix_*.py

## ANÁLISE EM PROGRESSO DOS DEMAIS PROJETOS
