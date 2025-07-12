# CHECKLIST DE COMPLIANCE PEP REAL - FLEXT WORKSPACE

## ✅ ESTRUTURA CORRETA ATUAL (NÃO MUDAR!)

### Nomenclatura de Projetos/Diretórios

- **CORRETO**: `flext-api/`, `flext-auth/`, `flext-cli/` (diretórios com hífen)
- **CORRETO**: `src/flext_api/`, `src/flext_auth/`, `src/flext_cli/` (módulos Python com underscore)

**Esta é uma convenção aceita e amplamente usada. NÃO É uma violação PEP!**

## 🔴 PROBLEMAS REAIS DE PEP COMPLIANCE

### 1. Scripts Proibidos (VIOLAÇÃO CRÍTICA)

**Encontrados 20 scripts fix_*.py que violam as regras do workspace:**

```bash
# REMOVER URGENTEMENTE:
./flext-plugin/fix_syntax_errors.py
./scripts/fix_imports.py
./scripts/fix_missing_deps.py  
./scripts/fix_ruff_errors.py
./scripts/legacy/fix_*.py (16 arquivos)
```

### 2. Problemas de Código Python (PEP 8)

#### Verificar em cada projeto

**a) Imports (PEP 8)**

- [ ] Ordem: stdlib → third-party → local
- [ ] Um import por linha (exceto from x import a, b, c)
- [ ] Imports absolutos em src/
- [ ] Sem imports wildcard (from x import *)

**b) Espaçamento e Formatação**

- [ ] Indentação: 4 espaços (sem tabs)
- [ ] Linha máxima: 88 caracteres (Black default)
- [ ] 2 linhas em branco entre classes/funções top-level
- [ ] 1 linha em branco entre métodos

**c) Nomenclatura (PEP 8)**

```python
# CORRETO:
def calculate_total():  # funções: snake_case
class UserAccount:      # classes: CapWords
MAX_RETRIES = 3        # constantes: UPPER_SNAKE_CASE
user_name = "John"     # variáveis: snake_case

# INCORRETO:
def calculateTotal():   # camelCase
class user_account:     # snake_case para classe
maxRetries = 3         # camelCase para constante
```

### 3. Docstrings (PEP 257)

**Verificar em cada módulo:**

- [ ] Módulo tem docstring no topo
- [ ] Classes públicas têm docstring
- [ ] Funções públicas têm docstring
- [ ] Formato correto:

```python
"""Descrição de uma linha terminando com ponto."""

"""Descrição de uma linha.

Descrição mais detalhada em múltiplas linhas.
Pode ter vários parágrafos.
"""
```

### 4. Type Hints (PEP 484)

**Verificar:**

- [ ] Funções públicas têm type hints
- [ ] Parâmetros e retornos tipados
- [ ] Imports do typing quando necessário

```python
# CORRETO:
def process_data(items: list[str], max_count: int = 10) -> dict[str, int]:
    ...

# INCORRETO:
def process_data(items, max_count=10):
    ...
```

### 5. Estrutura de Projetos

**Projetos sem testes (CRÍTICO):**

- [ ] flext-grpc/ - Adicionar diretório tests/

**Estrutura não-padrão:**

- [ ] flext-quality/ - Tem tanto Django quanto package structure

## 📋 CHECKLIST DE VERIFICAÇÃO POR PROJETO

### Para cada projeto Python no workspace

1. **Verificação de Scripts Proibidos**

```bash
find projeto/ -name "fix_*.py" -o -name "temp_*.py" -o -name "migrate_*.py"
```

2. **Lint Check com Ruff**

```bash
cd projeto && make lint
```

3. **Format Check com Black**

```bash
cd projeto && make format-check
```

4. **Type Check com MyPy**

```bash
cd projeto && make type-check
```

5. **Verificar Docstrings**

```bash
# Usar pydocstyle ou verificar manualmente
grep -L '"""' src/**/*.py  # Arquivos sem docstring
```

6. **Verificar Estrutura**

```bash
# Deve existir:
ls -la tests/  # Diretório de testes
ls -la src/    # Código fonte
```

## 🚀 AÇÕES CORRETIVAS PRIORITÁRIAS

### Prioridade 1 (URGENTE)

1. **Remover todos os scripts fix_*.py**
2. **Adicionar tests/ ao flext-grpc**

### Prioridade 2 (IMPORTANTE)

1. **Executar `make format` em todos os projetos**
2. **Executar `make lint` e corrigir issues**
3. **Adicionar docstrings faltantes**

### Prioridade 3 (MELHORIA)

1. **Adicionar type hints onde faltam**
2. **Resolver estrutura do flext-quality**
3. **Documentar exceções à PEP quando justificadas**

## ⚠️ O QUE NÃO MUDAR

1. **Nomes de diretórios com hífen** - Está correto!
2. **Estrutura de pacotes existente** - Já segue PEP
3. **Arquivos de configuração** - NUNCA sem permissão
4. **Imports entre projetos** - Já funcionam corretamente

## 🎯 COMANDO DE VERIFICAÇÃO COMPLETA

```bash
# Para cada projeto:
cd projeto
make check  # Roda lint, format, type-check, tests

# Se tudo passar, o projeto está PEP-compliant!
```

## 📊 MÉTRICAS DE SUCESSO

- ✅ Zero scripts fix_*.py no workspace
- ✅ Todos os projetos passam em `make check`
- ✅ Todos os projetos têm diretório tests/
- ✅ Docstrings em todos os módulos públicos
- ✅ Zero warnings do ruff
- ✅ Código formatado com Black

---

**LEMBRE-SE**: O objetivo é melhorar a qualidade do código, não criar trabalho desnecessário. Foque nos problemas REAIS de compliance!
