# Prompt: Migração Profunda de flext_tests - Análise e Correção Completa

<!-- TOC START -->
- [Objetivo](#objetivo)
- [Escopo](#escopo)
  - [Projetos a Analisar](#projetos-a-analisar)
  - [Diretórios a Verificar](#diretrios-a-verificar)
  - [Arquivos a Verificar](#arquivos-a-verificar)
- [Métodos Deprecados e Migrações Obrigatórias](#mtodos-deprecados-e-migraes-obrigatrias)
  - [1. tm (TestsFlextMatchers) - Métodos Deprecados](#1-tm-testsflextmatchers-mtodos-deprecados)
  - [2. tt (TestsFlextFactories) - Métodos Deprecados](#2-tt-testsflextfactories-mtodos-deprecados)
  - [3. tf (TestsFlextFiles) - Métodos Deprecados](#3-tf-testsflextfiles-mtodos-deprecados)
  - [4. tv (TestsFlextValidator) - Verificar Uso Correto](#4-tv-testsflextvalidator-verificar-uso-correto)
  - [5. tb (TestsFlextBuilders) - Verificar Uso Correto](#5-tb-testsflextbuilders-verificar-uso-correto)
- [Padrões a Identificar e Corrigir](#padres-a-identificar-e-corrigir)
  - [1. Imports Incorretos](#1-imports-incorretos)
  - [2. Uso de Métodos Privados ou Internos](#2-uso-de-mtodos-privados-ou-internos)
  - [3. Uso de Classes Aninhadas Deprecadas](#3-uso-de-classes-aninhadas-deprecadas)
  - [4. Parâmetros Legacy/Deprecados](#4-parmetros-legacydeprecados)
  - [5. Uso de Métodos Não Documentados](#5-uso-de-mtodos-no-documentados)
- [Processo de Análise e Correção](#processo-de-anlise-e-correo)
  - [Fase 1: Identificação Completa](#fase-1-identificao-completa)
  - [Fase 2: Análise Contextual](#fase-2-anlise-contextual)
  - [Fase 3: Correção Sistemática](#fase-3-correo-sistemtica)
  - [Fase 4: Validação](#fase-4-validao)
- [Checklist de Verificação](#checklist-de-verificao)
  - [Para cada projeto](#para-cada-projeto)
- [Exceções e Casos Especiais](#excees-e-casos-especiais)
  - [1. Testes de Deprecation Warnings](#1-testes-de-deprecation-warnings)
  - [2. Código de Compatibilidade](#2-cdigo-de-compatibilidade)
  - [3. Métodos Internos Legítimos](#3-mtodos-internos-legtimos)
- [Documentação de Progresso](#documentao-de-progresso)
- [Resultado Esperado](#resultado-esperado)
- [Comandos Úteis](#comandos-teis)
  - [Buscar usos deprecados em um projeto](#buscar-usos-deprecados-em-um-projeto)
  - [Executar testes de um projeto](#executar-testes-de-um-projeto)
  - [Verificar warnings](#verificar-warnings)
- [Estrutura e Organização de Testes](#estrutura-e-organizao-de-testes)
  - [Regras Fundamentais de Estrutura](#regras-fundamentais-de-estrutura)
- [Checklist de Estrutura e Organização](#checklist-de-estrutura-e-organizao)
  - [Para cada projeto](#para-cada-projeto)
- [Processo de Reorganização](#processo-de-reorganizao)
  - [Fase 1: Identificação e Análise](#fase-1-identificao-e-anlise)
  - [Fase 2: Consolidação](#fase-2-consolidao)
  - [Fase 3: Reorganização de Testes](#fase-3-reorganizao-de-testes)
  - [Fase 4: Automação](#fase-4-automao)
  - [Fase 5: Limpeza](#fase-5-limpeza)
- [Comandos Úteis de Reorganização](#comandos-teis-de-reorganizao)
  - [Buscar estrutura atual](#buscar-estrutura-atual)
  - [Reorganizar testes](#reorganizar-testes)
  - [Verificar marcações](#verificar-marcaes)
  - [Verificar nomenclatura](#verificar-nomenclatura)
- [Notas Finais](#notas-finais)
<!-- TOC END -->

## Objetivo

Realizar uma análise profunda e sistemática de **TODOS os testes de TODOS os projetos** do ecossistema FLEXT para
identificar e corrigir **TODOS os usos de funções de `flext_tests` que estão fora do padrão atual e não suportadas**.

## Escopo

### Projetos a Analisar

- ✅ Todos os projetos `flext-*` no diretório raiz
- ✅ Todos os projetos `flext-*` no diretório raiz
- ✅ Qualquer outro projeto que use `flext_tests`

### Diretórios a Verificar

- ✅ `tests/` - Todos os arquivos de teste
- ✅ `src/` - Código fonte (pode ter testes inline)
- ✅ `examples/` - Exemplos que podem usar flext_tests
- ✅ `scripts/` - Scripts de teste
- ✅ `docs/` - Documentação com exemplos de código

### Arquivos a Verificar

- ✅ Todos os arquivos `.py` nos diretórios acima
- ✅ Arquivos de configuração de teste (pytest.ini, conftest.py, etc.)

## Métodos Deprecados e Migrações Obrigatórias

### 1. tm (TestsFlextMatchers) - Métodos Deprecados

#### ❌ DEPRECADOS → ✅ MIGRAR PARA

| Método Deprecado                      | Método Público Atual                                                 | Exemplo de Migração                                                    |
| ------------------------------------- | -------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `tm.eq(actual, expected)`             | `tm.that(actual, eq=expected)`                                       | `tm.eq(x, 5)` → `tm.that(x, eq=5)`                                     |
| `tm.true(condition)`                  | `tm.that(condition, eq=True)`                                        | `tm.true(x > 0)` → `tm.that(x > 0, eq=True)`                           |
| `tm.assert_contains(container, item)` | `tm.that(container, contains=item)`                                  | `tm.assert_contains(d, "key")` → `tm.that(d, contains="key")`          |
| `tm.str_(text, ...)`                  | `tm.that(text, ...)`                                                 | `tm.str_(url, starts="http")` → `tm.that(url, starts="http")`          |
| `tm.is_(value, type)`                 | `tm.that(value, is_=type)`                                           | `tm.is_(x, str)` → `tm.that(x, is_=str)`                               |
| `tm.len(items, expected)`             | `tm.that(items, length=expected)`                                    | `tm.len(lst, 5)` → `tm.that(lst, length=5)`                            |
| `tm.hasattr(obj, *attrs)`             | `tm.that(hasattr(obj, attr), eq=True)`                               | `tm.hasattr(obj, "attr")` → `tm.that(hasattr(obj, "attr"), eq=True)`   |
| `tm.method(obj, name)`                | `tm.that(hasattr(...), eq=True)` + `tm.that(callable(...), eq=True)` | Ver exemplo abaixo                                                     |
| `tm.not_none(*values)`                | `tm.that(value, none=False)`                                         | `tm.not_none(x, y)` → `tm.that(x, none=False); tm.that(y, none=False)` |
| `tm.dict_(data, ...)`                 | `tm.that(data, keys=...)` ou `tm.that(data, length=...)`             | Ver exemplo abaixo                                                     |
| `tm.list_(items, ...)`                | `tm.that(items, has=...)` ou `tm.that(items, length=...)`            | Ver exemplo abaixo                                                     |
| `tm.assert_is_type(value, type)`      | `tm.that(value, is_=type, none=False)`                               | `tm.assert_is_type(x, str)` → `tm.that(x, is_=str, none=False)`        |

#### Exemplos Detalhados de Migração

**tm.method():**

```python
# ❌ ANTES
tm.method(api, "connect")

# ✅ DEPOIS
tm.that(hasattr(api, "connect"), eq=True)
tm.that(callable(getattr(api, "connect", None)), eq=True)
```

**tm.dict\_():**

```python
# ❌ ANTES
tm.dict_(data, has_key="name", length=5)

# ✅ DEPOIS
tm.that(data, keys=["name"], length=5)
```

**tm.list\_():**

```python
# ❌ ANTES
tm.list_(items, contains="item", length=3)

# ✅ DEPOIS
tm.that(items, has="item", length=3)
```

### 2. tt (TestsFlextFactories) - Métodos Deprecados

#### ❌ DEPRECADOS → ✅ MIGRAR PARA

| Método Deprecado                | Método Público Atual            | Exemplo de Migração                                                 |
| ------------------------------- | ------------------------------- | ------------------------------------------------------------------- |
| `tt.create_user(...)`           | `tt.model("user", ...)`         | `tt.create_user(name="John")` → `tt.model("user", name="John")`     |
| `tt.create_config(...)`         | `tt.model("settings", ...)`     | `tt.create_config(debug=True)` → `tt.model("settings", debug=True)` |
| `tt.create_service(...)`        | `tt.model("service", ...)`      | `tt.create_service(type="api")` → `tt.model("service", type="api")` |
| `tt.batch_users(count)`         | `tt.batch("user", count=count)` | `tt.batch_users(5)` → `tt.batch("user", count=5)`                   |
| `tt.create_test_operation(...)` | `tt.op(kind, ...)`              | `tt.create_test_operation("simple")` → `tt.op("simple")`            |
| `tt.create_test_service(...)`   | `tt.svc(...)`                   | `tt.create_test_service(type="test")` → `tt.svc(type="test")`       |

#### Classes Aninhadas Deprecadas (tb.\*)

| Classe/Método Deprecado             | Método Público Atual            | Exemplo de Migração                                                        |
| ----------------------------------- | ------------------------------- | -------------------------------------------------------------------------- |
| `tb.Tests.Result.ok(value)`         | `tt.res("ok", value=value)`     | `tb.Tests.Result.ok("data")` → `tt.res("ok", value="data")`                |
| `tb.Tests.Result.fail(error)`       | `tt.res("fail", error=error)`   | `tb.Tests.Result.fail("err")` → `tt.res("fail", error="err")`              |
| `tb.Tests.Model.user(...)`          | `tt.model("user", ...)`         | `tb.Tests.Model.user(name="John")` → `tt.model("user", name="John")`       |
| `tb.Tests.Model.settings(...)`      | `tt.model("settings", ...)`     | `tb.Tests.Model.settings(debug=True)` → `tt.model("settings", debug=True)` |
| `tb.Tests.Model.batch_users(count)` | `tt.batch("user", count=count)` | `tb.Tests.Model.batch_users(5)` → `tt.batch("user", count=5)`              |

### 3. tf (TestsFlextFiles) - Métodos Deprecados

#### ❌ DEPRECADOS → ✅ MIGRAR PARA

| Método Deprecado             | Método Público Atual                | Exemplo de Migração                                                                 |
| ---------------------------- | ----------------------------------- | ----------------------------------------------------------------------------------- |
| `tf.create_file_set(files)`  | `tf.files(files)` (context manager) | Ver exemplo abaixo                                                                  |
| `tf.get_file_info(path)`     | `tf.info(path)`                     | `tf.get_file_info(p)` → `tf.info(p).unwrap()`                                       |
| `tf.create_text_file(...)`   | `tf.create(content, name)`          | `tf.create_text_file("text", "file.txt")` → `tf.create("text", "file.txt")`         |
| `tf.create_binary_file(...)` | `tf.create(content, name)`          | `tf.create_binary_file(b"data", "file.bin")` → `tf.create(b"data", "file.bin")`     |
| `tf.create_empty_file(name)` | `tf.create("", name)`               | `tf.create_empty_file("empty.txt")` → `tf.create("", "empty.txt")`                  |
| `tf.create_config_file(...)` | `tf.create(content, name)`          | `tf.create_config_file("{}", "settings.json")` → `tf.create("{}", "settings.json")` |
| `tf.temporary_files(files)`  | `tf.files(files)` (context manager) | Ver exemplo abaixo                                                                  |

#### Exemplos Detalhados de Migração

**tf.create_file_set():**

```python
# ❌ ANTES
files = tf.create_file_set({"file1.txt": "content1", "file2.txt": "content2"})

# ✅ DEPOIS
with tf.files({"file1.txt": "content1", "file2.txt": "content2"}) as files:
    # usar files aqui
    pass
```

**tf.get_file_info():**

```python
# ❌ ANTES
info = tf.get_file_info(path)

# ✅ DEPOIS
info_result = tf.info(path)
tm.ok(info_result)
info = info_result.unwrap()
```

### 4. tv (TestsFlextValidator) - Verificar Uso Correto

- ✅ `tv.imports()` - Verificar se está sendo usado corretamente
- ✅ `tv.types()` - Verificar se está sendo usado corretamente
- ✅ `tv.tests()` - Verificar se está sendo usado corretamente
- ✅ `tv.validate_config()` - Verificar se está sendo usado corretamente
- ✅ `tv.bypass()` - Verificar se está sendo usado corretamente
- ✅ `tv.layer()` - Verificar se está sendo usado corretamente
- ✅ `tv.all()` - Verificar se está sendo usado corretamente

### 5. tb (TestsFlextBuilders) - Verificar Uso Correto

- ✅ `tb()` - Instância do builder (correto)
- ✅ `tb.with_users(count)` - Verificar se está sendo usado corretamente
- ✅ `tb.u.with_configs(...)` - Verificar se está sendo usado corretamente
- ✅ `tb.build()` - Verificar se está sendo usado corretamente
- ❌ `tb.Tests.*` - Classes aninhadas deprecadas (migrar para `tt.*`)

## Padrões a Identificar e Corrigir

### 1. Imports Incorretos

```python
# ❌ ERRADO
from flext_tests import TestsFlextMatchers

tm = TestsFlextMatchers()

# ✅ CORRETO
from flext_tests import tm
```

### 2. Uso de Métodos Privados ou Internos

```python
# ❌ ERRADO - Métodos que começam com _
tm._internal_method()
tt._private_factory()

# ✅ CORRETO - Usar apenas métodos públicos
tm.that(...)
tt.model(...)
```

### 3. Uso de Classes Aninhadas Deprecadas

```python
# ❌ ERRADO
tb.Tests.Result.ok(value)
tb.Tests.Model.user(...)
tt.Result.ok(value)  # Se existir
tt.Models.user(...)  # Se existir

# ✅ CORRETO
tt.res("ok", value=value)
tt.model("user", ...)
```

### 4. Parâmetros Legacy/Deprecados

Alguns métodos podem aceitar parâmetros legacy que devem ser migrados:

```python
# ❌ ERRADO - Parâmetros legacy
tm.that(data, contains="key")  # Se 'contains' for legacy para dict
tm.that(items, contains="item")  # Se 'contains' for legacy para list

# ✅ CORRETO - Parâmetros modernos
tm.that(data, keys=["key"])  # Para dict
tm.that(items, has="item")  # Para list
```

### 5. Uso de Métodos Não Documentados

Qualquer método que não esteja na documentação pública deve ser investigado e migrado.

## Processo de Análise e Correção

### Fase 1: Identificação Completa

1. **Buscar todos os usos de métodos deprecados:**

   ```bash
   # Padrões a buscar
   - tm\.eq\(
   - tm\.true\(
   - tm\.assert_contains\(
   - tm\.str_\(
   - tm\.is_\(
   - tm\.len\(
   - tm\.hasattr\(
   - tm\.method\(
   - tm\.not_none\(
   - tm\.dict_\(
   - tm\.list_\(
   - tm\.assert_is_type\(
   - tt\.create_user\(
   - tt\.create_config\(
   - tt\.create_service\(
   - tt\.batch_users\(
   - tt\.create_test_operation\(
   - tt\.create_test_service\(
   - tf\.create_file_set\(
   - tf\.get_file_info\(
   - tf\.create_text_file\(
   - tf\.create_binary_file\(
   - tf\.create_empty_file\(
   - tf\.create_config_file\(
   - tf\.temporary_files\(
   - tb\.Tests\.
   ```

2. **Buscar usos de classes aninhadas deprecadas:**

   ```bash
   - tb\.Tests\.Result\.
   - tb\.Tests\.Model\.
   - tb\.Tests\.Operations\.
   - tb\.Tests\.Batch\.
   ```

3. **Buscar imports incorretos:**

   ```bash
   - from flext_tests import TestsFlextMatchers
   - from flext_tests import TestsFlextFactories
   - from flext_tests import TestsFlextFiles
   - from flext_tests import TestsFlextBuilders
   ```

4. **Buscar usos de métodos privados:**

   ```bash
   - tm\._[a-z]
   - tt\._[a-z]
   - tf\._[a-z]
   - tv\._[a-z]
   - tb\._[a-z]
   ```

### Fase 2: Análise Contextual

Para cada uso encontrado:

1. **Ler o contexto completo:**
   - Arquivo completo ou seção relevante
   - Imports do arquivo
   - Função/método onde está sendo usado
   - Testes relacionados

2. **Identificar o padrão de uso:**
   - Qual método deprecado está sendo usado
   - Quais parâmetros estão sendo passados
   - Qual é o resultado esperado
   - Qual é o contexto de uso (assertion, factory, file operation, etc.)

3. **Determinar a migração correta:**
   - Consultar a tabela de migração acima
   - Verificar exemplos na documentação
   - Considerar casos especiais (múltiplas validações, etc.)

### Fase 3: Correção Sistemática

1. **Para cada arquivo com usos deprecados:**
   - Ler o arquivo completo
   - Identificar todos os usos
   - Criar plano de migração
   - Aplicar correções
   - Verificar imports

2. **Padrões de correção:**
   - Substituir método deprecado pelo método público atual
   - Ajustar parâmetros conforme necessário
   - Manter a mesma lógica e comportamento
   - Preservar mensagens de erro personalizadas quando existirem

3. **Casos especiais:**
   - Múltiplas validações: dividir em múltiplas chamadas `tm.that()`
   - Context managers: migrar para `tf.files()` quando apropriado
   - Resultados: usar `.unwrap()` quando necessário

### Fase 4: Validação

1. **Executar testes:**

   ```bash
   # Para cada projeto
   cd <projeto>
   source ~/flext/.venv/bin/activate
   pytest tests/ -v
   ```

2. **Verificar warnings de deprecation:**
   - Não deve haver warnings de deprecation nos testes
   - Todos os métodos deprecados devem ter sido migrados

3. **Verificar linters:**

   ```bash
   ruff check .
   MYPY_MEMORY_LIMIT_MB=6144 MYPY_TIMEOUT_SECONDS=600 make check CHECK_GATES=mypy
   ```

4. **Verificação final:**
   - Buscar novamente por padrões deprecados
   - Confirmar que não há mais usos
   - Documentar exceções (se houver)

## Checklist de Verificação

### Para cada projeto

- [ ] Todos os arquivos `.py` em `tests/` foram verificados
- [ ] Todos os arquivos `.py` em `src/` foram verificados (se aplicável)
- [ ] Todos os arquivos `.py` em `examples/` foram verificados (se aplicável)
- [ ] Todos os arquivos `.py` em `scripts/` foram verificados (se aplicável)
- [ ] Todos os usos de `tm.*` deprecados foram migrados
- [ ] Todos os usos de `tt.*` deprecados foram migrados
- [ ] Todos os usos de `tf.*` deprecados foram migrados
- [ ] Todos os usos de `tb.Tests.*` foram migrados
- [ ] Todos os imports estão corretos
- [ ] Não há usos de métodos privados (`_*`)
- [ ] Todos os testes passam
- [ ] Não há warnings de deprecation
- [ ] Linters passam sem erros

## Exceções e Casos Especiais

### 1. Testes de Deprecation Warnings

Arquivos que testam explicitamente os warnings de deprecation devem manter os métodos deprecados:

```python
# ✅ CORRETO - Teste de deprecation warning
def test_deprecation_warning():
    with warnings.catch_warnings(record=True) as w:
        tm.eq(1, 1)  # Manter método deprecado para testar warning
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
```

### 2. Código de Compatibilidade

Se houver código de compatibilidade que precisa manter métodos deprecados temporariamente, documentar claramente.

### 3. Métodos Internos Legítimos

Alguns métodos podem ser usados internamente pela própria biblioteca `flext_tests`. Verificar se o uso é legítimo.

## Documentação de Progresso

Manter um registro de:

1. **Arquivos analisados:**
   - Lista de todos os arquivos verificados
   - Status de cada arquivo (limpo, migrado, pendente)

2. **Métodos encontrados:**
   - Quantidade de cada método deprecado encontrado
   - Arquivos onde foram encontrados

3. **Migrações realizadas:**
   - Quantidade de migrações por tipo
   - Arquivos modificados

4. **Problemas encontrados:**
   - Casos especiais
   - Dúvidas sobre migração
   - Decisões tomadas

## Resultado Esperado

Ao final do processo:

- ✅ **0 usos de métodos deprecados** em código de teste
- ✅ **100% dos testes passando**
- ✅ **0 warnings de deprecation** (exceto em testes de deprecation)
- ✅ **Todos os linters passando**
- ✅ **Código usando apenas métodos públicos atuais**
- ✅ **Documentação atualizada** (se necessário)

## Comandos Úteis

### Buscar usos deprecados em um projeto

```bash
cd <projeto>
grep -r "tm\.eq(" tests/ src/ examples/ scripts/ 2>/dev/null || true
grep -r "tt\.create_user(" tests/ src/ examples/ scripts/ 2>/dev/null || true
# ... repetir para todos os padrões
```

### Executar testes de um projeto

```bash
cd <projeto>
source ~/flext/.venv/bin/activate
pytest tests/ -v --tb=short
```

### Verificar warnings

```bash
pytest tests/ -v -W error::DeprecationWarning
```

## Estrutura e Organização de Testes

### Regras Fundamentais de Estrutura

#### 1. Marcação de Testes

Todos os testes devem ser marcados explicitamente:

```python
# ✅ CORRETO - Unit test
@pytest.mark.unit
def test_user_creation():
    pass


# ✅ CORRETO - Integration test
@pytest.mark.integration
def test_database_connection():
    pass
```

**Regras:**

- ✅ Unit tests: marcados com `@pytest.mark.unit`
- ✅ Integration tests: marcados com `@pytest.mark.integration`
- ✅ E2E tests: marcados com `@pytest.mark.e2e` (se aplicável)
- ❌ Testes sem marcação explícita devem ser marcados ou removidos

#### 2. Classes Base e Namespaces

**Estrutura Centralizada em `~/flext`:**

```text
~/flext/
├── conftest.py          # ÚNICO conftest.py do ecossistema
├── constants.py         # Estende flext_tests.constants
├── models.py            # Estende flext_tests.models
├── typings.py           # Estende flext_tests.typings
├── protocols.py          # Estende flext_tests.protocols
└── utilities.py         # Estende flext_tests.utilities
```

**Regras de Namespace:**

1. **Classes base em `~/flext`** devem estender as de `flext_tests`:

   ```python
   # ~/flext/constants.py
   from flext_tests import FlextTestsConstants


   class FlextConstants(FlextTestsConstants):
       """Constants base que estende flext_tests."""

       pass
   ```

2. **Imports rápidos por projeto:**

   ```python
   # Em cada projeto, criar namespaces fáceis:
   from flext import c
   from flext import m
   from flext import p, t
   from flext import p
   from flext import u
   ```

3. **Domínios de teste por projeto:**
   - `.Tests[Projeto]` - Para projetos específicos (ex: `.TestsLdap`, `.TestsCli`)
   - `.TestsCore` - Para flext-core
   - `.TestsRoot` - Para Flext (raiz)
   - `.Tests` - Para flext-tests (sem conflito)

**Exemplo de estrutura:**

```python
# ~/flext/models.py
from flext_tests import TestsFlextModels


class FlextModels(TestsFlextModels):
    """Models base que estende flext_tests."""

    class TestsLdap:
        """Domínio de testes para flext-ldap."""

        class User:
            pass

    class TestsCli:
        """Domínio de testes para flext-cli."""

        class Command:
            pass

    class TestsCore:
        """Domínio de testes para flext-core."""

        class Service:
            pass
```

#### 3. Migração de Classes Base

**Processo obrigatório:**

1. **Identificar classes base duplicadas:**
   - Buscar `constants.py`, `models.py`, `typings.py`, `protocols.py`, `utilities.py` em cada projeto
   - Buscar múltiplos `conftest.py` em projetos

2. **Mover objetos para `~/flext`:**
   - Consolidar todas as classes base em `~/flext/`
   - Estender de `flext_tests` quando apropriado
   - Criar namespaces por projeto (`.Tests[Projeto]`)

3. **Atualizar imports:**
   - Todos os projetos devem importar de `~/flext`
   - Remover imports locais de classes base

4. **Renomear e remover:**
   - Renomear arquivos locais para `.bak` (ex: `constants.py.bak`)
   - Remover após confirmação de que tudo funciona

**Comando de busca:**

```bash
# Buscar classes base duplicadas
find . -name "constants.py" -o -name "models.py" -o -name "typings.py" \
  -o -name "protocols.py" -o -name "utilities.py" | grep -v "~/flext"
find . -name "conftest.py" | wc -l  # Deve retornar 1 (apenas em ~/flext)
```

#### 4. Estrutura de Diretórios de Testes

**Estrutura obrigatória:**

```text
<projeto>/
├── tests/
│   ├── conftest.py          # ❌ NÃO PERMITIDO (usar ~/flext/conftest.py)
│   ├── fixtures/             # ✅ Geradores de dados (Python apenas)
│   │   ├── users.py
│   │   └── configs.py
│   ├── unit/                 # ✅ Testes de unidade (100% cobertura)
│   │   ├── [namespace/]      # Opcional: namespace adicional
│   │   │   └── test_[modulo].py
│   │   └── test_[modulo].py
│   ├── integration/          # ✅ Testes de integração
│   │   └── test_[modulo].py
│   ├── e2e/                  # ✅ Testes end-to-end (se aplicável)
│   │   └── test_[modulo].py
│   └── [outros]/             # ✅ Outros tipos de testes (se necessário)
│       └── test_[modulo].py
```

**Regras:**

- ✅ `tests/fixtures/` - Apenas geradores de dados (código Python)
- ✅ `tests/unit/` - Testes de unidade com 100% de cobertura real
- ✅ `tests/integration/` - Testes de integração
- ✅ `tests/e2e/` - Testes end-to-end (se aplicável)
- ❌ `tests/conftest.py` - NÃO PERMITIDO (usar `~/flext/conftest.py`)
- ❌ Classes base locais - NÃO PERMITIDO (usar `~/flext/`)

#### 5. Nomenclatura de Arquivos e Classes

**Arquivos de teste:**

- ✅ `tests/unit/[namespace/]test_[modulo].py`
- ✅ `tests/integration/test_[modulo].py`
- ✅ `tests/e2e/test_[modulo].py`

**Classes de teste:**

- ✅ Uma única classe por arquivo: `Tests[Projeto][Modulo]`
- ✅ Prefixo obrigatório: `Tests[Projeto]`
- ✅ Nome do módulo em PascalCase após o prefixo

**Exemplos:**

```python
# tests/unit/test_user.py
class TestsLdapUser:
    """Testes de unidade para User do flext-ldap."""

    pass


# tests/unit/services/test_entry.py
class TestsLdapServicesEntry:
    """Testes de unidade para Entry service do flext-ldap."""

    pass


# tests/integration/test_sync.py
class TestsLdapSync:
    """Testes de integração para Sync do flext-ldap."""

    pass
```

#### 6. Organização de Unit Tests

**Requisitos obrigatórios:**

1. **100% de cobertura com testes reais:**
   - ✅ Sem mocks desnecessários
   - ✅ Testes reais de funcionalidade
   - ✅ Validação de comportamento real

2. **Uma única classe por arquivo:**

   ```python
   # ✅ CORRETO
   # tests/unit/test_user.py
   class TestsLdapUser:
       def test_create_user(self):
           pass

       def test_validate_user(self):
           pass
   ```

3. **Automação máxima com conftest:**
   - ✅ Todas as inicializações em `~/flext/conftest.py`
   - ✅ Conexões, containers, fixtures automáticas
   - ✅ Classes base avançadas de pytest
   - ✅ Mínimo de código, máximo de automação

4. **Estrutura de diretórios:**

   ```text
   tests/unit/
   ├── test_user.py              # TestsLdapUser
   ├── test_config.py            # TestsLdapSettings
   ├── services/
   │   └── test_entry.py         # TestsLdapServicesEntry
   └── adapters/
       └── test_ldap3.py         # TestsLdapAdaptersLdap3
   ```

#### 7. Fixtures e Geradores de Dados

**Localização:** `tests/fixtures/`

**Regras:**

- ✅ Apenas geradores de dados (código Python)
- ✅ Funções que retornam dados de teste
- ✅ Não devem conter lógica de teste
- ✅ Importáveis e reutilizáveis

**Exemplo:**

```python
# tests/fixtures/users.py
def generate_user_data(count: int = 1) -> t.SequenceOf[dict]:
    """Gera dados de usuário para testes."""
    return [
        {"name": f"User {i}", "email": f"user{i}@example.com"} for i in range(count)
    ]
```

#### 8. Conftest Centralizado

**Localização:** `~/flext/conftest.py` (ÚNICO)

**Deve conter:**

- ✅ Todas as inicializações globais
- ✅ Fixtures compartilhadas
- ✅ Settingsurações de conexões
- ✅ Containers de dependências
- ✅ Classes base avançadas de pytest
- ✅ Automação máxima para mínimo de código

**Exemplo de estrutura:**

```python
# ~/flext/conftest.py
import pytest
from flext_tests import tm, tt, tf, tv, tb


@pytest.fixture(scope="session")
def test_container():
    """Container de dependências para testes."""
    # Automação completa
    pass


@pytest.fixture
def setup_test_environment():
    """Setup automático para cada teste."""
    # Automação completa
    yield
    # Cleanup automático
    pass
```

#### 9. Priorização de Refatoração

**Sempre priorizar:**

1. ✅ **Renomear e concatenar módulos** - Juntar módulos similares
2. ✅ **Reutilizar código existente** - Evitar duplicação
3. ✅ **Automatizar com conftest** - Máxima automação
4. ❌ **Recriar do zero** - Última opção, apenas se necessário

**Processo de refatoração:**

1. Identificar módulos similares
2. Analisar código comum
3. Consolidar em um único módulo
4. Atualizar imports
5. Verificar testes

## Checklist de Estrutura e Organização

### Para cada projeto

#### Classes Base e Namespaces

- [ ] Classes base (`constants.py`, `models.py`, etc.) movidas para `~/flext/`
- [ ] Classes base estendem de `flext_tests`
- [ ] Namespaces fáceis criados (`c`, `m`, `t`, `p`, `u`)
- [ ] Domínios de teste prefixados corretamente (`.Tests[Projeto]`, `.TestsCore`, `.TestsRoot`)
- [ ] Imports atualizados para usar `~/flext/`
- [ ] Arquivos locais renomeados para `.bak` e removidos

#### Estrutura de Diretórios

- [ ] `tests/fixtures/` existe e contém apenas geradores de dados
- [ ] `tests/unit/` existe e contém testes de unidade
- [ ] `tests/integration/` existe e contém testes de integração
- [ ] `tests/e2e/` existe (se aplicável)
- [ ] Não há `tests/conftest.py` local (usar `~/flext/conftest.py`)

#### Nomenclatura

- [ ] Todos os arquivos seguem padrão `test_[modulo].py`
- [ ] Todas as classes seguem padrão `Tests[Projeto][Modulo]`
- [ ] Uma única classe por arquivo
- [ ] Namespaces em diretórios quando necessário

#### Marcação de Testes

- [ ] Todos os unit tests marcados com `@pytest.mark.unit`
- [ ] Todos os integration tests marcados com `@pytest.mark.integration`
- [ ] Todos os e2e tests marcados com `@pytest.mark.e2e` (se aplicável)
- [ ] Nenhum teste sem marcação

#### Automação

- [ ] `~/flext/conftest.py` contém todas as inicializações
- [ ] Fixtures automáticas configuradas
- [ ] Containers e conexões automatizados
- [ ] Classes base avançadas de pytest implementadas
- [ ] Mínimo de código, máximo de automação

#### Cobertura

- [ ] Unit tests alcançam 100% de cobertura
- [ ] Testes usam implementações reais (sem mocks desnecessários)
- [ ] Comportamento real validado

## Processo de Reorganização

### Fase 1: Identificação e Análise

1. **Identificar estrutura atual:**

   ```bash
   # Buscar classes base duplicadas
   find . -name "constants.py" -o -name "models.py" -o -name "typings.py" | grep -v "~/flext"

   # Buscar conftest.py duplicados
   find . -name "conftest.py" | grep -v "~/flext"

   # Analisar estrutura de testes
   find . -type d -name "tests" | xargs -I {} find {} -type f -name "*.py"
   ```

2. **Mapear dependências:**
   - Identificar quais classes base são usadas
   - Mapear imports de cada projeto
   - Identificar código comum

### Fase 2: Consolidação

1. **Criar estrutura centralizada:**
   - Criar `~/flext/constants.py`, `models.py`, etc.
   - Estender de `flext_tests`
   - Criar namespaces por projeto

2. **Mover e consolidar:**
   - Mover objetos comuns para `~/flext/`
   - Consolidar código duplicado
   - Criar domínios de teste (`.Tests[Projeto]`)

3. **Atualizar imports:**
   - Atualizar todos os projetos para usar `~/flext/`
   - Verificar que tudo funciona

### Fase 3: Reorganização de Testes

1. **Reorganizar diretórios:**
   - Criar `tests/unit/`, `tests/integration/`, etc.
   - Mover testes para diretórios corretos
   - Organizar por namespace quando necessário

2. **Renomear arquivos e classes:**
   - Renomear para `test_[modulo].py`
   - Renomear classes para `Tests[Projeto][Modulo]`
   - Consolidar múltiplas classes em uma única

3. **Adicionar marcações:**
   - Marcar todos os testes (`@pytest.mark.unit`, etc.)
   - Verificar que marcações estão corretas

### Fase 4: Automação

1. **Criar conftest centralizado:**
   - Consolidar todos os conftest.py em `~/flext/conftest.py`
   - Criar fixtures automáticas
   - Settingsurar containers e conexões

2. **Implementar classes base:**
   - Criar classes base avançadas de pytest
   - Automatizar setup/teardown
   - Minimizar código de teste

3. **Criar fixtures de dados:**
   - Mover geradores de dados para `tests/fixtures/`
   - Tornar reutilizáveis
   - Documentar uso

### Fase 5: Limpeza

1. **Renomear arquivos antigos:**

   ```bash
   # Renomear para .bak
   mv constants.py constants.py.bak
   mv conftest.py conftest.py.bak
   ```

2. **Remover após validação:**
   - Executar todos os testes
   - Verificar que tudo funciona
   - Remover arquivos `.bak`

3. **Verificação final:**
   - Estrutura correta
   - Imports corretos
   - Testes passando
   - Cobertura adequada

## Comandos Úteis de Reorganização

### Buscar estrutura atual

```bash
# Classes base duplicadas
find . -name "constants.py" -o -name "models.py" | grep -v "~/flext"

# Conftest duplicados
find . -name "conftest.py" | grep -v "~/flext"

# Estrutura de testes
tree tests/ -I "__pycache__|*.pyc"
```

### Reorganizar testes

```bash
# Mover testes para diretórios corretos
mkdir -p tests/unit tests/integration tests/fixtures
# ... mover arquivos conforme necessário
```

### Verificar marcações

```bash
# Buscar testes sem marcação
grep -r "def test_" tests/ | grep -v "@pytest.mark"
```

### Verificar nomenclatura

```bash
# Buscar classes que não seguem padrão
grep -r "class.*Test" tests/ | grep -v "Tests\[Projeto\]"
```

## Notas Finais

- **Prioridade:** Alta - Esta migração é crítica para manter o código atualizado
- **Complexidade:** Média-Alta - Requer análise cuidadosa de cada uso
- **Tempo estimado:** 4-8 horas para todos os projetos
- **Risco:** Baixo - Métodos deprecados ainda funcionam, mas devem ser migrados
- **Benefício:** Alto - Código mais limpo, sem warnings, usando API moderna

---

**Última atualização:** 2025-01-XX
**Status:** Pronto para execução
