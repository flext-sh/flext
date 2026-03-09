# ARCHIVED — Subsumed by modernization-reorg-execution.md

# Plan: Namespace Governance & MRO Deduplication — ALL 31 Projects

**Status**: ACTIVE
**Scope**: 31 projects × 5 facade types (c, t, p, m, u) × src + tests = 310 audit/fix units
**Goal**: Organizar, desduplicar e monopolizar o máximo de uso e composição com as classes mais altas para redução de código e de declaração de responsabilidades, mantendo a nomenclatura e padronização
**Exit criteria**: `make check && make test` = 0 warnings, 0 errors, 0 failures em TODOS os 31 projetos + `make validate VALIDATE_SCOPE=workspace` = 0

---

## REGRAS DO USUÁRIO — VERBATIM, AS IS (NENHUMA PODE SER IGNORADA OU REINTERPRETADA)

> R1: "esse plano, tem que fazer isso, dando voltas nos 33 projetos, nos 5 tipos de classes, organizando, desduplicando e monopolizando o maximo de uso e composicaao com as classes mais altas para reducao de codigo e de declaracao de suas responsabildiades, mantendo a nomenclatura e padronizacaso"
>
> R2: "isso é importante que seja feito tambem nos testes"
>
> R3: "ao fazer um padrao de classe, todos os modulos do projeto tem que ser auditados por violacoes as regras"
>
> R4: "fazer das bibliotecas namespaced de forma real"
>
> R5: "ter o codigo lintado e corrigido pelos 4 lints"
>
> R6: "depois a mesma coisa para os tests que deveram ter sempre um namespace .Tests. depois do de projeto para seus usos internos para os 5 tipos"
>
> R7: "coloque plano para ter 5 ondas, com todos os 33 projetos comecando por flext-core"
>
> R8: "indo ate ate o workspace, algar e gruponos (sao externos e workspace nao importa eles de forma direta, por isso faca por ultimo)"
>
> R9: "ao final de cada etapa biblioca/projeot, todos os 4 lints e pytests tem que ter absolutamente 0% de falha em warnings, erros, mesmo que sejam pre-existentes"
>
> R10: "todo o codigo tem que ser rewired e em hipótese alguma, algo pode ser deixado para depois ou pulado por ser complexo demais"
>
> R11: "isso é fundamental para quebrar o ciclo de nunca conseguirmos arrumar o projeto"
>
> R12: "ser controlados por beads e agentes de verificacao para nao deixar passar etapas pela metade e com qualidade duvidosa"
>
> R13: "t.StreamProcessing is very wrong, correct is t.Meltano.StreamProcessing, only flext-core put on root-level facade !!!!!"
>
> R14: "ONLY flext-core put on root-level facade !!!!!"
>
> R15: "temos que usar SEMPRE MRO com namespace"
>
> R16: "as classes altas nos projetos Dbt, Tap, Target tem que ter pouquíssimas ou nenhuma adição ao que vem de Meltano"
>
> R17: "nao quero em absoluto factories"
>
> R18: "nao mistura dados de dominio especifico com flext-core"
>
> R19: "isso vale para c, t, p, m e u" (constants, typings, protocols, models, utilities)
>
> R20: "onde estao as definicoes de fase, o que fazer, o que vai entregar, como vai ter certeza que vai entregar"
>
> R21: "em hipótese alguma, algo pode ser deixado para depois ou pulado por ser complexo demais"
>
> R22: "mesmo que sejam pre-existentes" (falhas pre-existentes de lint/test TÊM que ser corrigidas também)

---

## LEI DO NAMESPACE (ABSOLUTA — VIOLAÇÃO = REJEIÇÃO IMEDIATA)

```
SÓ flext-core pode ter atributos/classes no nível raiz de uma facade.
TODOS os outros projetos DEVEM colocar TODO conteúdo de domínio DENTRO da sua inner class de namespace.
NUNCA criar aliases, re-exports ou classes no nível raiz fora do namespace.
```

**Exemplo do que está ERRADO e COMO corrigir:**

```python
# ❌ ERRADO — StreamProcessing no nível raiz de um consumidor
class FlextTapLdifTypes(FlextMeltanoTypes, FlextLdifTypes):
    class StreamProcessing:  # ← VIOLAÇÃO: no raiz do facade
        class StreamConfiguration: ...

# ✅ CORRETO — tudo sob namespace do projeto
class FlextTapLdifTypes(FlextMeltanoTypes, FlextLdifTypes):
    class TapLdif:  # ← namespace do projeto
        # Conteúdo MÍNIMO — só o que NÃO vem via MRO
        pass
    # StreamProcessing NÃO aparece aqui — vem via MRO de FlextMeltanoTypes.Meltano
```

**Acesso correto:**
- `t.Meltano.StreamProcessing` ✅ (via MRO de FlextMeltanoTypes)
- `t.StreamProcessing` ❌ (violação — só flext-core pode ter raiz)
- `t.TapLdif.StreamProcessing` ❌ (duplicação desnecessária)

---

## REGISTRY DE NAMESPACES (FIXO — NÃO INVENTAR NOVOS)

| Camada    | Projeto            | Namespace      | Padrão de Acesso        | Herda De                       |
|-----------|--------------------| ---------------|-------------------------|--------------------------------|
| Core      | flext-core         | (raiz)         | `c.CommonStatus`        | —                              |
| Base      | flext-cli          | `Cli`          | `c.Cli.*`               | FlextConstants                 |
| Base      | flext-ldif         | `Ldif`         | `c.Ldif.*`              | FlextConstants                 |
| Base      | flext-db-oracle    | `DbOracle`     | `c.DbOracle.*`          | FlextConstants                 |
| Base      | flext-plugin       | `Plugin`       | `c.Plugin.*`            | FlextConstants                 |
| Base      | flext-auth         | `Auth`         | `c.Auth.*`              | FlextConstants                 |
| Base      | flext-api          | `Api`          | `c.Api.*`               | FlextConstants                 |
| Base      | flext-grpc         | `Grpc`         | `c.Grpc.*`              | FlextConstants                 |
| Base      | flext-observability| `Observability` | `c.Observability.*`    | FlextConstants                 |
| Base      | flext-quality      | `Quality`      | `c.Quality.*`           | FlextConstants                 |
| Base      | flext-web          | `Web`          | `c.Web.*`               | FlextConstants                 |
| Base      | flext-oracle-oic   | `OracleOic`    | `c.OracleOic.*`         | FlextConstants                 |
| Base      | flext-oracle-wms   | `OracleWms`    | `c.OracleWms.*`         | FlextConstants                 |
| Hub       | flext-meltano      | `Meltano`      | `c.Meltano.*`           | FlextCliConstants              |
| Hub       | flext-ldap         | `Ldap`         | `c.Ldap.*`              | FlextLdifConstants             |
| Consumer  | flext-tap-oracle   | `TapOracle`    | `c.TapOracle.*`         | FlextMeltano + FlextDbOracle   |
| Consumer  | flext-tap-oracle-oic | `TapOracleOic` | `c.TapOracleOic.*`   | FlextMeltano + FlextOracleOic  |
| Consumer  | flext-tap-oracle-wms | `TapOracleWms` | `c.TapOracleWms.*`   | FlextMeltano + FlextOracleWms  |
| Consumer  | flext-tap-ldap     | `TapLdap`      | `c.TapLdap.*`           | FlextMeltano + FlextLdap       |
| Consumer  | flext-tap-ldif     | `TapLdif`      | `c.TapLdif.*`           | FlextMeltano + FlextLdif       |
| Consumer  | flext-target-oracle| `TargetOracle`  | `c.TargetOracle.*`     | FlextMeltano + FlextDbOracle   |
| Consumer  | flext-target-oracle-oic | `TargetOracleOic` | `c.TargetOracleOic.*` | FlextMeltano + FlextOracleOic |
| Consumer  | flext-target-oracle-wms | `TargetOracleWms` | `c.TargetOracleWms.*` | FlextMeltano + FlextOracleWms |
| Consumer  | flext-target-ldap  | `TargetLdap`   | `c.TargetLdap.*`        | FlextMeltano + FlextLdap       |
| Consumer  | flext-target-ldif  | `TargetLdif`   | `c.TargetLdif.*`        | FlextMeltano + FlextLdif       |
| Consumer  | flext-dbt-oracle   | `DbtOracle`    | `c.DbtOracle.*`         | FlextMeltano + FlextDbOracle   |
| Consumer  | flext-dbt-oracle-wms | `DbtOracleWms` | `c.DbtOracleWms.*`   | FlextMeltano + FlextOracleWms  |
| Consumer  | flext-dbt-ldap     | `DbtLdap`      | `c.DbtLdap.*`           | FlextMeltano + FlextLdap       |
| Consumer  | flext-dbt-ldif     | `DbtLdif`      | `c.DbtLdif.*`           | FlextMeltano + FlextLdif       |
| External  | algar-oud-mig      | (próprio)      | (padrão próprio)        | workspace, NÃO importado       |
| External  | gruponos-meltano   | (próprio)      | (padrão próprio)        | workspace, NÃO importado       |

---

## COMPOSIÇÃO MRO — COMO FUNCIONA (PARA CADA TIPO c, t, p, m, u)

```python
# Consumer facade — conteúdo MÍNIMO próprio, herda TUDO via MRO
class FlextTapOracleTypes(FlextMeltanoTypes, FlextDbOracleTypes):
    # Ganha DE GRAÇA via MRO:
    #   t.Meltano.*        (StreamProcessing, ErrorHandling, Singer, etc.)
    #   t.Cli.*            (via FlextCliTypes dentro de FlextMeltanoTypes)
    #   t.DbOracle.*       (Query, Transaction, Schema, etc.)
    #   t.ScalarValue etc  (de FlextTypes raiz)
    #
    # Consumer adiciona SÓ conteúdo único do projeto sob PRÓPRIO namespace:
    class TapOracle:
        # SÓ tipos que NÃO existem em NENHUM outro lugar vão aqui
        ...
    # Se nada for único, o corpo é só: pass
```

---

## NAMESPACE DE TESTES (R2, R6)

```python
# tests/models.py — SEMPRE usa namespace Tests
class TestsFlextTapOracleModels:
    Tests = FlextTestsModels.Tests  # Composição, NÃO herança
    class TapOracle:  # Namespace do projeto nos testes
        class Tests:  # Namespace interno para usos de teste
            ...
```

Regra: "os tests devem ter sempre um namespace .Tests. depois do de projeto para seus usos internos para os 5 tipos"

---

## OS 4 QUALITY GATES (TODOS devem passar por projeto, 0% tolerância — R5, R9, R22)

| Gate     | Comando                                  | Meta            |
|----------|------------------------------------------|-----------------|
| Lint     | `make check CHECK_GATES=lint`            | 0 violações     |
| Format   | `make check CHECK_GATES=format`          | 0 violações     |
| TypeCheck| `make check CHECK_GATES=pyrefly`         | 0 erros         |
| Security | `make check CHECK_GATES=security`        | 0 findings      |
| Tests    | `make test`                              | 0 falhas        |

**Falhas pre-existentes TÊM que ser corrigidas (R22). Nada é deixado para depois (R10, R21).**

---

## GUARDRAILS (ABSOLUTOS — agente DEVE recusar se qualquer um for violado)

- G1: NUNCA mexer em alias assignments locais — `c = FlextXxxConstants` é estrutural
- G2: NUNCA mesclar Settings FIELD DEFINITIONS entre projetos
- G3: NUNCA deletar adapter code sem prova via `diff`
- G4: NUNCA afirmar que código é morto sem prova via `lsp_find_references`
- G5: NUNCA mexer em `__version__.py`
- G6: NUNCA colocar conteúdo de domínio no nível raiz de facade (SÓ flext-core pode — R14)
- G7: NUNCA misturar dados de domínio específico com flext-core (R18)
- G8: NUNCA usar factory pattern — SÓ facade classes + MRO (R17)
- G9: NUNCA deixar algo para depois ou pular por complexidade (R10, R21)
- G10: NUNCA aceitar quality gate com > 0 falhas, incluindo pre-existentes (R9, R22)
- G11: NUNCA terminar um projeto pela metade (R12)
- G12: NUNCA criar namespaces novos — usar APENAS os do Registry acima

---

## PROTOCOLO DE VERIFICAÇÃO POR PROJETO (R12)

```bash
# Agente executa esta SEQUÊNCIA EXATA. TODOS devem retornar 0.
cd flext-{project}
make check CHECK_GATES=lint     # 0 violações
make check CHECK_GATES=format   # 0 violações
make check CHECK_GATES=pyrefly  # 0 erros
make check CHECK_GATES=security # 0 findings
make test                       # 0 falhas
```

Evidência capturada em: `.sisyphus/evidence/wave-{N}/flext-{project}-check.txt`

Após TODOS os gates passarem, o agente de verificação confirma:
1. Zero classes no nível raiz de facades (exceto flext-core)
2. Zero duplicatas de classes que deveriam vir via MRO
3. Zero referências usando caminho sem namespace (e.g., `t.StreamProcessing` em vez de `t.Meltano.StreamProcessing`)
4. Test facades seguem padrão `.Tests.`

---

## ESTRUTURA DE WAVES (5 Ondas — R7, R8)

### Resumo de Ondas

```
Wave 1 (Sequencial — fundação):
└── flext-core — limpar dead code, validar facades raiz, validar test pattern

Wave 2 (Paralelo — 12 bases):
├── flext-cli          (2 violações — constants.py)
├── flext-ldif         (16 violações — constants.py)
├── flext-db-oracle    (9 violações — typings.py + utilities.py)
├── flext-web          (11 violações — typings.py + protocols.py)
├── flext-plugin       (0 violações — só quality gates + tests)
├── flext-auth         (0 violações — só quality gates + tests)
├── flext-api          (0 violações — só quality gates + tests)
├── flext-grpc         (0 violações — só quality gates + tests)
├── flext-observability(0 violações — só quality gates + tests)
├── flext-quality      (0 violações — só quality gates + tests)
├── flext-oracle-oic   (0 violações — só quality gates + tests)
└── flext-oracle-wms   (0 violações — só quality gates + tests)

Wave 3 (Sequencial — 2 hubs, ANTES dos consumers):
├── flext-meltano — centralizar Singer types duplicados + quality gates
└── flext-ldap — namespace tests + quality gates

Wave 4 (Paralelo — 14 consumers, DEPOIS dos hubs):
├── flext-tap-oracle         (1 violação)
├── flext-tap-oracle-oic     (audit pendente)
├── flext-tap-oracle-wms     (audit pendente)
├── flext-tap-ldap           (audit pendente)
├── flext-tap-ldif           (25 violações)
├── flext-target-oracle      (18 violações)
├── flext-target-oracle-oic  (audit pendente)
├── flext-target-oracle-wms  (11 violações)
├── flext-target-ldap        (audit pendente)
├── flext-target-ldif        (audit pendente)
├── flext-dbt-oracle         (audit pendente)
├── flext-dbt-oracle-wms     (16 violações)
├── flext-dbt-ldap           (42 violações)
└── flext-dbt-ldif           (audit pendente)

Wave 5 (Sequencial — externos + workspace):
├── algar-oud-mig
├── gruponos-meltano-native
└── make validate VALIDATE_SCOPE=workspace
```

---

## TODOs

### WAVE 1: Fundação — flext-core (1 projeto, sequencial)

- [ ] W1-1. **flext-core: Limpar dead code + validar facades raiz + validar test pattern**

  **Violações encontradas no audit:**
  - `flext-core/src/flext_core/typings.py`: `DictValueT` TypeVar — 0 referências em todo o workspace (confirmado via lsp_find_references). DEAD CODE.
  - Facades raiz (constants.py 1497 linhas, typings.py 562 linhas, protocols.py 1813 linhas, utilities.py 481 linhas): conteúdo no raiz é CORRETO para core — validar que nenhum conteúdo de domínio específico de outro projeto vazou aqui (R18).
  - Test pattern reference: `tests/__init__.py`, `tests/models.py` (TestsFlextModels com composição Tests).
  - Test shared infra: `src/flext_tests/__init__.py` (FlextTestsModels) — validar padrão `.Tests.`.

  **O que fazer:**
  1. Remover `DictValueT` de `typings.py` (dead code confirmado — 0 refs)
  2. Auditar TODOS os 5 facades (c, t, p, m, u) verificando que NENHUM conteúdo de domínio específico de outro projeto está aqui (R18)
  3. Auditar `src/flext_tests/` verificando padrão `.Tests.` para composição (R6)
  4. Auditar TODOS os módulos .py em `src/flext_core/` e `src/flext_tests/` por violações de acesso sem namespace
  5. Rodar `make check` (4 gates) — corrigir TODAS as falhas incluindo pre-existentes (R9, R22)
  6. Rodar `make test` — corrigir TODAS as falhas incluindo pre-existentes (R9, R22)

  **O que entrega:**
  - Zero dead code em facades
  - Zero conteúdo de domínio específico em flext-core
  - Test pattern `.Tests.` validado como referência para todos os outros projetos
  - `make check && make test` = 0 issues

  **Como verificar:**
  ```bash
  cd flext-core
  grep -rn 'DictValueT' src/         # Expected: 0 matches
  make check CHECK_GATES=lint         # Expected: 0 violations
  make check CHECK_GATES=format       # Expected: 0 violations
  make check CHECK_GATES=pyrefly      # Expected: 0 errors
  make check CHECK_GATES=security     # Expected: 0 findings
  make test                           # Expected: 0 failures
  ```

  **Agent**: `category=deep`, `load_skills=["rules-flext-core", "flext-strict-typing"]`
  **Commit**: `refactor(flext-core): remove dead code, validate facade and test patterns`
  **Evidence**: `.sisyphus/evidence/wave-1/flext-core-check.txt`

---

### WAVE 2: Base Libraries (12 projetos, paralelo — R7)

#### Projetos COM violações de namespace (4 projetos — corrigir violações + quality gates):

- [ ] W2-1. **flext-cli: Mover 2 classes raiz para namespace Cli + quality gates**

  **Violações encontradas no audit:**
  - `flext-cli/src/flext_cli/constants.py`: 2 classes no nível raiz que DEVEM estar sob `class Cli:`:
    - `Configuration` → mover para `Cli.Configuration`
    - `Authentication` → mover para `Cli.Authentication`
  - typings.py, protocols.py, models.py, utilities.py: ✅ compliant (0 violações)

  **O que fazer:**
  1. Em `constants.py`: mover `Configuration` e `Authentication` para dentro de `class Cli:`
  2. Auditar TODOS os módulos .py em `src/flext_cli/` por referências diretas (`c.Configuration` → `c.Cli.Configuration`)
  3. Auditar TODOS os test facades em `tests/` por padrão `.Tests.` (R6)
  4. Corrigir TODAS as referências nos módulos do projeto
  5. Rodar 4 quality gates + pytest — corrigir TUDO incluindo pre-existentes (R9, R22)

  **O que entrega:**
  - Violações namespace: 2 → 0
  - TODOS os módulos usando `c.Cli.Configuration` em vez de `c.Configuration`
  - Test facades com padrão `.Tests.`
  - `make check && make test` = 0 issues

  **Como verificar:**
  ```bash
  cd flext-cli
  # Verificar zero classes raiz (só Cli deve existir como inner class direta)
  grep -n '^    class ' src/flext_cli/constants.py  # Expected: só 'class Cli:'
  # Verificar zero referências diretas sem namespace
  grep -rn 'c\.Configuration[^_]' src/flext_cli/ --include='*.py' | grep -v 'Cli\.Configuration' | grep -v '#'  # Expected: 0
  grep -rn 'c\.Authentication[^_]' src/flext_cli/ --include='*.py' | grep -v 'Cli\.Authentication' | grep -v '#'  # Expected: 0
  make check && make test  # Expected: 0 issues
  ```

  **Agent**: `category=quick`, `load_skills=["flext-architecture-layers"]`
  **Commit**: `refactor(flext-cli): move Configuration, Authentication under Cli namespace`
  **Evidence**: `.sisyphus/evidence/wave-2/flext-cli-check.txt`

- [ ] W2-2. **flext-ldif: Mover 16 StrEnums raiz para namespace Ldif + quality gates**

  **Violações encontradas no audit:**
  - `flext-ldif/src/flext_ldif/constants.py`: 16 StrEnum classes no nível raiz que DEVEM estar sob `class Ldif:`:
    - `DnPrefixField` → `Ldif.DnPrefixField`
    - `SchemaKwField` → `Ldif.SchemaKwField`
    - `AclBindIpField` → `Ldif.AclBindIpField`
    - `PersonField` → `Ldif.PersonField`
    - `OrganizationalUnitField` → `Ldif.OrganizationalUnitField`
    - `UserField` → `Ldif.UserField`
    - `GroupField` → `Ldif.GroupField`
    - `AudioField` → `Ldif.AudioField`
    - `StrictField` → `Ldif.StrictField`
    - `LenientField` → `Ldif.LenientField`
    - `SubtreeField` → `Ldif.SubtreeField`
    - `OnelevelField` → `Ldif.OnelevelField`
    - `BaseField` → `Ldif.BaseField`
    - `AllField` → `Ldif.AllField`
    - `AciField` → `Ldif.AciField`
    - `AclWildcardField` → `Ldif.AclWildcardField`
  - typings.py: ✅ compliant (tem `class Ldif:` correto)

  **O que fazer:**
  1. Em `constants.py`: mover TODAS as 16 StrEnums para dentro de `class Ldif:`
  2. Auditar TODOS os módulos .py em `src/flext_ldif/` por referências diretas (`c.DnPrefixField` → `c.Ldif.DnPrefixField`)
  3. Auditar TODOS os módulos em projetos que HERDAM de flext-ldif (flext-ldap, flext-tap-ldif, flext-target-ldif, flext-dbt-ldif) — eles vão precisar atualizar referências na Wave 3/4
  4. Auditar test facades por padrão `.Tests.` (R6)
  5. Rodar 4 quality gates + pytest — corrigir TUDO incluindo pre-existentes (R9, R22)

  **O que entrega:**
  - Violações namespace: 16 → 0
  - TODOS os módulos usando `c.Ldif.DnPrefixField` em vez de `c.DnPrefixField`
  - `make check && make test` = 0 issues

  **Como verificar:**
  ```bash
  cd flext-ldif
  grep -n '^    class ' src/flext_ldif/constants.py  # Expected: só 'class Ldif:'
  # Verificar que as 16 enums estão DENTRO de Ldif (indent 8+)
  grep -n '^        class .*Field' src/flext_ldif/constants.py  # Expected: 16 matches
  make check && make test  # Expected: 0 issues
  ```

  **Agent**: `category=deep`, `load_skills=["flext-architecture-layers"]`
  **Commit**: `refactor(flext-ldif): move 16 StrEnums under Ldif namespace`
  **Evidence**: `.sisyphus/evidence/wave-2/flext-ldif-check.txt`

- [ ] W2-3. **flext-db-oracle: Mover 9 classes raiz para namespace DbOracle + quality gates**

  **Violações encontradas no audit:**
  - `flext-db-oracle/src/flext_db_oracle/typings.py`: 8 classes no nível raiz que DEVEM estar sob `class DbOracle:`:
    - `Query` → `DbOracle.Query`
    - `Transaction` → `DbOracle.Transaction`
    - `Schema` → `DbOracle.Schema`
    - `Session` → `DbOracle.Session`
    - `Performance` → `DbOracle.Performance`
    - `Security` → `DbOracle.Security`
    - `DataTypes` → `DbOracle.DataTypes`
    - `Project` → `DbOracle.Project`
  - `flext-db-oracle/src/flext_db_oracle/utilities.py`: 1 classe no nível raiz:
    - `OracleValidation` → `DbOracle.OracleValidation`
  - constants.py, protocols.py, models.py: ✅ compliant

  **O que fazer:**
  1. Em `typings.py`: mover 8 classes para dentro de `class DbOracle:`
  2. Em `utilities.py`: mover `OracleValidation` para dentro de `class DbOracle:`
  3. Auditar TODOS os módulos .py em `src/flext_db_oracle/` por referências diretas (`t.Query` → `t.DbOracle.Query`)
  4. Auditar TODOS os projetos que HERDAM de flext-db-oracle (flext-tap-oracle, flext-target-oracle, flext-dbt-oracle, etc.) — referências mudam de `t.Query.*` para `t.DbOracle.Query.*`
  5. Auditar test facades por padrão `.Tests.` (R6)
  6. Rodar 4 quality gates + pytest — corrigir TUDO incluindo pre-existentes (R9, R22)

  **IMPACTO CROSS-PROJECT:** Esta mudança afeta consumers que acessam `t.Query`, `t.Transaction`, etc. diretamente. Eles terão que mudar para `t.DbOracle.Query`, `t.DbOracle.Transaction` na Wave 4. Documentar todas as referências encontradas.

  **O que entrega:**
  - Violações namespace: 9 → 0
  - TODOS os módulos usando `t.DbOracle.Query` em vez de `t.Query`
  - Lista de referências cross-project que precisam atualizar na Wave 4
  - `make check && make test` = 0 issues

  **Como verificar:**
  ```bash
  cd flext-db-oracle
  grep -n '^    class ' src/flext_db_oracle/typings.py  # Expected: só 'class DbOracle:'
  grep -n '^    class ' src/flext_db_oracle/utilities.py  # Expected: só 'class DbOracle:'
  make check && make test  # Expected: 0 issues
  ```

  **Agent**: `category=deep`, `load_skills=["flext-architecture-layers"]`
  **Commit**: `refactor(flext-db-oracle): move 9 classes under DbOracle namespace`
  **Evidence**: `.sisyphus/evidence/wave-2/flext-db-oracle-check.txt`

- [ ] W2-4. **flext-web: Mover 11 classes raiz para namespace Web + quality gates**

  **Violações encontradas no audit:**
  - `flext-web/src/flext_web/typings.py`: 5 classes no nível raiz:
    - `HttpMessage` (line 84) → `Web.HttpMessage`
    - `HttpRequest` (line 87) → `Web.HttpRequest`
    - `HttpResponse` (line 90) → `Web.HttpResponse`
    - `ApplicationEntity` (line 101) → `Web.ApplicationEntity`
    - `AppData` (line 108) → `Web.AppData`
  - `flext-web/src/flext_web/protocols.py`: classes adicionais no nível raiz (verificar — audit reportou WebCore, Types, Data, WebConfigDict, AppConfigDict, TypesConfig, Project; Momus indicou que podem estar em typings.py em vez de protocols.py — o agente executor DEVE fazer `grep -n '^    class ' src/flext_web/protocols.py` para confirmar localização exata antes de mover)
  - constants.py, models.py, utilities.py: ✅ compliant

  **O que fazer:**
  1. Em `typings.py`: mover 5 classes para dentro de `class Web:`
  2. Em `protocols.py`: mover 6 classes para dentro de `class Web:`
  3. Auditar TODOS os módulos .py em `src/flext_web/` por referências diretas
  4. Auditar test facades por padrão `.Tests.` (R6)
  5. Rodar 4 quality gates + pytest — corrigir TUDO incluindo pre-existentes (R9, R22)

  **O que entrega:**
  - Violações namespace: 11 → 0
  - `make check && make test` = 0 issues

  **Como verificar:**
  ```bash
  cd flext-web
  grep -n '^    class ' src/flext_web/typings.py   # Expected: só 'class Web:'
  grep -n '^    class ' src/flext_web/protocols.py  # Expected: só 'class Web:'
  make check && make test  # Expected: 0 issues
  ```

  **Agent**: `category=deep`, `load_skills=["flext-architecture-layers"]`
  **Commit**: `refactor(flext-web): move 11 classes under Web namespace`
  **Evidence**: `.sisyphus/evidence/wave-2/flext-web-check.txt`

#### Projetos SEM violações de namespace (8 projetos — só quality gates + test namespace audit):

- [ ] W2-5. **flext-plugin: Auditar test namespace + quality gates**

  **Status src/ facades:** ✅ 0 violações namespace (audit confirmado)

  **O que fazer:**
  1. Auditar TODOS os 5 src facades (c, t, p, m, u) — confirmar 0 violações
  2. Auditar TODOS os módulos .py em `src/flext_plugin/` por referências sem namespace
  3. Auditar TODOS os test facades em `tests/` por padrão `.Tests.` (R6) — corrigir se necessário
  4. Rodar 4 quality gates + pytest — corrigir TUDO incluindo pre-existentes (R9, R22)

  **O que entrega:**
  - Confirmação de compliance namespace em src/
  - Test facades com padrão `.Tests.`
  - `make check && make test` = 0 issues

  **Como verificar:**
  ```bash
  cd flext-plugin
  grep -n '^    class ' src/flext_plugin/*.py  # Expected: só 'class Plugin:' por facade
  make check && make test  # Expected: 0 issues
  ```

  **Agent**: `category=quick`, `load_skills=["flext-architecture-layers"]`
  **Commit**: `refactor(flext-plugin): namespace audit + quality gates`

- [ ] W2-6. **flext-auth: Auditar test namespace + quality gates**
  (Mesmo template que W2-5. Status src/: ✅ 0 violações. Namespace: Auth)
  **Agent**: `category=quick`, **Commit**: `refactor(flext-auth): namespace audit + quality gates`

- [ ] W2-7. **flext-api: Auditar test namespace + quality gates**
  (Mesmo template que W2-5. Status src/: ✅ 0 violações. Namespace: Api)
  **Agent**: `category=quick`, **Commit**: `refactor(flext-api): namespace audit + quality gates`

- [ ] W2-8. **flext-grpc: Auditar test namespace + quality gates**
  (Mesmo template que W2-5. Status src/: ✅ 0 violações. Namespace: Grpc)
  **Agent**: `category=quick`, **Commit**: `refactor(flext-grpc): namespace audit + quality gates`

- [ ] W2-9. **flext-observability: Auditar test namespace + quality gates**
  (Mesmo template que W2-5. Status src/: ✅ 0 violações. Namespace: Observability)
  **Agent**: `category=quick`, **Commit**: `refactor(flext-observability): namespace audit + quality gates`

- [ ] W2-10. **flext-quality: Auditar test namespace + quality gates**
  (Mesmo template que W2-5. Status src/: ✅ 0 violações. Namespace: Quality)
  **Agent**: `category=quick`, **Commit**: `refactor(flext-quality): namespace audit + quality gates`

- [ ] W2-11. **flext-oracle-oic: Auditar test namespace + quality gates**
  (Mesmo template que W2-5. Status src/: ✅ 0 violações. Namespace: OracleOic)
  **Agent**: `category=quick`, **Commit**: `refactor(flext-oracle-oic): namespace audit + quality gates`

- [ ] W2-12. **flext-oracle-wms: Auditar test namespace + quality gates**
  (Mesmo template que W2-5. Status src/: ✅ 0 violações. Namespace: OracleWms)
  **Agent**: `category=quick`, **Commit**: `refactor(flext-oracle-wms): namespace audit + quality gates`

---

### WAVE 3: Hubs/Middleware (2 projetos, sequencial — consumers dependem destes — R7)

- [ ] W3-1. **flext-meltano: Centralizar Singer types duplicados + namespace governance + quality gates**

  **Status src/ facades:** ✅ 0 violações de namespace (audit confirmou — `class Meltano:` correto em todos os 5 facades)

  **MAS: Deve RECEBER classes duplicadas dos consumers para centralizar via MRO (R1, R13, R15)**

  **Classes a centralizar em `class Meltano:` nos respectivos facades:**

  | Classe Duplicada      | Facade Destino | Projetos que TÊM cópia idêntica (deletar na Wave 4)         |
  |-----------------------|----------------|--------------------------------------------------------------|
  | `StreamProcessing`    | typings.py     | tap-ldif, tap-oracle-oic, target-oracle, target-oracle-wms   |
  | `ErrorHandling`       | typings.py     | tap-ldif, tap-oracle-oic, target-oracle, target-oracle-wms   |
  | `DataExtraction`      | typings.py     | tap-ldif, tap-oracle-oic                                     |
  | `DataTransformation`  | typings.py     | target-oracle, target-oracle-wms                             |
  | `SingerMessage`       | typings.py     | target-oracle                                                |
  | `ConfigValidation`    | utilities.py   | tap-ldif, tap-oracle-oic, tap-oracle-wms, target-ldap, target-ldif |
  | `StateManagement`     | utilities.py   | tap-ldif, tap-oracle-oic, tap-oracle-wms, target-ldap, target-ldif |
  | `StreamUtilities`     | utilities.py   | tap-oracle-wms, target-ldap, target-ldif                     |

  **Confirmação de segurança:**
  - StreamProcessing: IDÊNTICO em 4 projetos (confirmado via comparação de conteúdo), 0 referências fora de typings.py
  - ErrorHandling: IDÊNTICO em 4 projetos (confirmado via comparação de conteúdo), 0 referências fora de typings.py
  - DataExtraction, DataTransformation, SingerMessage: validar com `lsp_find_references` antes de mover (G4)
  - ConfigValidation, StateManagement, StreamUtilities: validar com `lsp_find_references` antes de mover (G4)

  **O que fazer:**
  1. Para cada classe na tabela acima:
     a. Copiar UMA instância da classe duplicada do consumer para `flext-meltano/src/flext_meltano/{facade}.py`
     b. Colocar DENTRO de `class Meltano:` (NUNCA no raiz — R14)
     c. Verificar que a classe funciona no contexto de flext-meltano
  2. Auditar TODOS os módulos .py em `src/flext_meltano/` por referências sem namespace
  3. Auditar test facades por padrão `.Tests.` (R6)
  4. Rodar 4 quality gates + pytest — corrigir TUDO incluindo pre-existentes (R9, R22)
  5. NÃO deletar as cópias nos consumers ainda — isso é feito na Wave 4

  **O que entrega:**
  - 8 classes centralizadas sob `Meltano` namespace
  - Consumers poderão acessar via MRO: `t.Meltano.StreamProcessing`, `t.Meltano.ErrorHandling`, etc.
  - `make check && make test` = 0 issues em flext-meltano

  **Como verificar:**
  ```bash
  cd flext-meltano
  # Verificar que classes estão DENTRO de Meltano namespace
  python -c "from flext_meltano.typings import FlextMeltanoTypes; assert hasattr(FlextMeltanoTypes.Meltano, 'StreamProcessing')"
  python -c "from flext_meltano.typings import FlextMeltanoTypes; assert hasattr(FlextMeltanoTypes.Meltano, 'ErrorHandling')"
  python -c "from flext_meltano.utilities import FlextMeltanoUtilities; assert hasattr(FlextMeltanoUtilities.Meltano, 'ConfigValidation')"
  # Verificar que NÃO estão no raiz
  grep -n '^    class StreamProcessing' src/flext_meltano/typings.py  # Expected: 0 (deve estar indent 8+)
  grep -n '^        class StreamProcessing' src/flext_meltano/typings.py  # Expected: 1 (dentro de Meltano)
  make check && make test  # Expected: 0 issues
  ```

  **Agent**: `category=deep`, `load_skills=["flext-architecture-layers"]`
  **Commit**: `refactor(flext-meltano): centralize 8 Singer types under Meltano namespace`
  **Evidence**: `.sisyphus/evidence/wave-3/flext-meltano-check.txt`

- [ ] W3-2. **flext-ldap: Corrigir test namespace violations + quality gates**

  **Status src/ facades:** ✅ 0 violações de namespace
  **Status test facades:** ⚠️ Violações em tests/constants.py — Fixtures, Mocks, Servers, RFC, General estão no raiz do test facade em vez de sob namespace

  **O que fazer:**
  1. Confirmar 0 violações em src/ facades (audit confirmou)
  2. Em `tests/constants.py`: mover Fixtures, Mocks, Servers, RFC, General para dentro de namespace `Ldap.Tests` ou `Tests.Ldap`
  3. Auditar TODOS os test facades por padrão `.Tests.` (R6)
  4. Auditar TODOS os módulos .py em `src/flext_ldap/` por referências sem namespace
  5. Rodar 4 quality gates + pytest — corrigir TUDO incluindo pre-existentes (R9, R22)

  **O que entrega:**
  - Test facades com padrão `.Tests.` correto
  - `make check && make test` = 0 issues

  **Como verificar:**
  ```bash
  cd flext-ldap
  grep -n '^    class ' tests/constants.py  # Expected: só namespace classes
  make check && make test  # Expected: 0 issues
  ```

  **Agent**: `category=quick`, `load_skills=["flext-architecture-layers"]`
  **Commit**: `refactor(flext-ldap): fix test namespace + quality gates`
  **Evidence**: `.sisyphus/evidence/wave-3/flext-ldap-check.txt`

---

### WAVE 4: Consumer Leaf Projects (14 projetos, máximo paralelo — R7)

> **REGRA CRÍTICA para Wave 4 (R1, R13, R15, R16):**
> Após Wave 3, flext-meltano tem StreamProcessing, ErrorHandling, etc. sob `Meltano` namespace.
> Consumers HERDAM esses tipos via MRO. Portanto:
> 1. DELETAR as cópias locais dessas classes dos consumers
> 2. MOVER todas as classes raiz para sob o namespace do consumer
> 3. Consumer deve ter conteúdo MÍNIMO próprio — "pouquíssimas ou nenhuma adição" (R16)
> 4. Auditar TODOS os módulos por referências sem namespace
> 5. Quality gates 0% em TUDO

#### Consumers COM audit completo (6 projetos):

- [ ] W4-1. **flext-tap-oracle: Mover 1 classe raiz + quality gates**

  **Violações encontradas no audit:**
  - `typings.py`: 1 violação — `Project` no raiz → mover para `TapOracle.Project`
  - constants.py, protocols.py, models.py, utilities.py: ✅ compliant

  **O que fazer:**
  1. Em `typings.py`: mover `Project` para dentro de `class TapOracle:`
  2. Verificar se alguma classe herdada via MRO de FlextMeltanoTypes ou FlextDbOracleTypes está re-declarada — DELETAR se sim
  3. Auditar TODOS os módulos .py por referências sem namespace (`t.Project` → `t.TapOracle.Project`)
  4. Auditar TODOS os módulos por referências a classes que agora vêm via MRO do hub (ex: `t.Query` deve ser `t.DbOracle.Query`)
  5. Auditar test facades por padrão `.Tests.` (R6)
  6. Rodar 4 quality gates + pytest — corrigir TUDO (R9, R22)

  **O que entrega:** Violações: 1 → 0. Conteúdo mínimo sob TapOracle. `make check && make test` = 0
  **Agent**: `category=quick`, `load_skills=["flext-architecture-layers"]`
  **Commit**: `refactor(flext-tap-oracle): namespace governance + MRO dedup`

- [ ] W4-2. **flext-tap-ldif: Mover 25 classes raiz + deletar duplicatas MRO + quality gates**

  **Violações encontradas no audit (CRÍTICO — 25 classes!):**
  - `constants.py`: 5 violações — Format, TapLdifPerformance, TapLdifValidation, EntrySchema, SampleEntry
  - `typings.py`: 6 violações — LdifProcessing, DataExtraction, StreamProcessing, FileHandling, ErrorHandling, Project
  - `models.py`: 10 violações — LdifEntry, LdifChangeRecord, LdifFile, LdifStream, LdifBatch, LdifProcessingState, LdifTapConfig, LdifRecord, LdifValidationResult, LdifPerformanceMetrics
  - `utilities.py`: 4 violações — LdifFileProcessing, LdifDataProcessing, ConfigValidation, StateManagement

  **Classes a DELETAR (vêm via MRO de FlextMeltanoTypes após Wave 3):**
  - `StreamProcessing` — agora em `t.Meltano.StreamProcessing`
  - `ErrorHandling` — agora em `t.Meltano.ErrorHandling`
  - `DataExtraction` — agora em `t.Meltano.DataExtraction`
  - `ConfigValidation` — agora em `u.Meltano.ConfigValidation`
  - `StateManagement` — agora em `u.Meltano.StateManagement`

  **Classes a MOVER para `class TapLdif:` (conteúdo único do projeto):**
  - Format, TapLdifPerformance, TapLdifValidation, EntrySchema, SampleEntry (constants)
  - LdifProcessing, FileHandling, Project (typings — após deletar duplicatas)
  - LdifEntry, LdifChangeRecord, LdifFile, LdifStream, LdifBatch, LdifProcessingState, LdifTapConfig, LdifRecord, LdifValidationResult, LdifPerformanceMetrics (models)
  - LdifFileProcessing, LdifDataProcessing (utilities — após deletar duplicatas)

  **O que fazer:**
  1. DELETAR StreamProcessing, ErrorHandling, DataExtraction de `typings.py` (confirmado 0 refs, vêm via MRO)
  2. DELETAR ConfigValidation, StateManagement de `utilities.py` (vêm via MRO)
  3. MOVER todas as 20 classes restantes para dentro de `class TapLdif:`
  4. Atualizar TODOS os módulos .py: referências mudam (ex: `t.StreamProcessing` → `t.Meltano.StreamProcessing`)
  5. Auditar test facades por padrão `.Tests.` (R6)
  6. Rodar 4 quality gates + pytest — corrigir TUDO (R9, R22)

  **O que entrega:** Violações: 25 → 0. 5 duplicatas deletadas. Conteúdo mínimo sob TapLdif. `make check && make test` = 0
  **Agent**: `category=deep`, `load_skills=["flext-architecture-layers"]`
  **Commit**: `refactor(flext-tap-ldif): namespace governance + MRO dedup (25 violations fixed)`

- [ ] W4-3. **flext-target-oracle: Mover 18 classes raiz + deletar duplicatas MRO + quality gates**

  **Violações encontradas no audit (CRÍTICO — 18 classes!):**
  - `constants.py`: 7 violações — LoadMethod, StorageMode, TargetOracleProcessing, Loading, TargetOracleValidation, FeatureFlags, Observability
  - `typings.py`: 10 violações — OracleDatabase, OracleTable, OracleSql, OraclePerformance, DataTransformation, StreamProcessing, SingerMessage, ErrorHandling, Core, Project
  - `utilities.py`: 1 violação — OracleDataProcessing

  **Classes a DELETAR (vêm via MRO após Wave 3):**
  - `StreamProcessing` — agora em `t.Meltano.StreamProcessing`
  - `ErrorHandling` — agora em `t.Meltano.ErrorHandling`
  - `DataTransformation` — agora em `t.Meltano.DataTransformation`
  - `SingerMessage` — agora em `t.Meltano.SingerMessage`

  **Classes a MOVER para `class TargetOracle:` (conteúdo único):**
  - LoadMethod, StorageMode, TargetOracleProcessing, Loading, TargetOracleValidation, FeatureFlags, Observability (constants)
  - OracleDatabase, OracleTable, OracleSql, OraclePerformance, Core, Project (typings)
  - OracleDataProcessing (utilities)

  **O que entrega:** Violações: 18 → 0. 4 duplicatas deletadas. `make check && make test` = 0
  **Agent**: `category=deep`, `load_skills=["flext-architecture-layers"]`
  **Commit**: `refactor(flext-target-oracle): namespace governance + MRO dedup (18 violations fixed)`

- [ ] W4-4. **flext-target-oracle-wms: Mover 11 classes raiz + deletar duplicatas MRO + quality gates**

  **Violações encontradas no audit:**
  - `constants.py`: 1 violação — ErrorType
  - `typings.py`: 9 violações — WmsWarehouse, WmsInventory, WmsOrderManagement, WmsLaborManagement, WmsTransportation, DataTransformation, StreamProcessing, ErrorHandling, Project
  - `utilities.py`: 1 violação — Validation

  **Classes a DELETAR (vêm via MRO após Wave 3):**
  - `StreamProcessing`, `ErrorHandling`, `DataTransformation`

  **Classes a MOVER para `class TargetOracleWms:`:**
  - ErrorType (constants)
  - WmsWarehouse, WmsInventory, WmsOrderManagement, WmsLaborManagement, WmsTransportation, Project (typings)
  - Validation (utilities)

  **O que entrega:** Violações: 11 → 0. 3 duplicatas deletadas. `make check && make test` = 0
  **Agent**: `category=deep`, `load_skills=["flext-architecture-layers"]`
  **Commit**: `refactor(flext-target-oracle-wms): namespace governance + MRO dedup (11 violations fixed)`

- [ ] W4-5. **flext-dbt-oracle-wms: Mover 16 classes raiz + quality gates**

  **Violações encontradas no audit (CRÍTICO — 16 classes!):**
  - `typings.py`: 14 violações — Base, Timeouts, DbtProject, OracleWmsConnection, WmsData, DbtTransformation, DimensionalModeling, WmsBusinessLogic, DbtModel, DbtSource, OracleWmsAdapter, PerformanceOptimization, Project, DomainObjects
  - `models.py`: 1 violação — ModelGenerator
  - `utilities.py`: 1 violação — WmsDimensionalModeling

  **O que fazer:** MOVER todas as 16 classes para `class DbtOracleWms:`. Verificar se alguma vem via MRO — DELETAR se sim.
  **O que entrega:** Violações: 16 → 0. `make check && make test` = 0
  **Agent**: `category=deep`, `load_skills=["flext-architecture-layers"]`
  **Commit**: `refactor(flext-dbt-oracle-wms): namespace governance + MRO dedup (16 violations fixed)`

- [ ] W4-6. **flext-dbt-ldap: Mover 42 classes raiz + quality gates (PIOR PROJETO)**

  **Violações encontradas no audit (GRAVÍSSIMO — 42 classes!):**
  - `constants.py`: 10 violações — Dbt, LdapSchemaMapping, LdapEntityTypes, LdapAttributes, DbtModels, DbtProcessing, TransformationOptimization, DbtLogging, LdapOperations, DbtCommands
  - `typings.py`: 2 violações — DbtTransformation, Project
  - `models.py`: 26 violações — ValidationMetrics, DbtRunStatus, DbtLdapPipelineResult, SyncResult, PerformanceAnalysis, ServiceStatus, AnalyticsReport, DbtProjectConfig, DbtProfileConfig, DbtSourceTable, DbtSourceSchema, DbtModelDefinition, DbtTestConfig, DbtSourceFreshness, DbtSourceDefinition, DbtConfig, ProjectStructureValidation, OptimizationHints, TransformationConfig, TransformationRule, DataValidationConfig, LdapSchema, LdapQuery, UserDimension, GroupDimension, MembershipFact
  - `utilities.py`: 4 violações — LdapDataTransformation, MacroManagement, SchemaGeneration, TransformationOptimization

  **O que fazer:** MOVER todas as 42 classes para `class DbtLdap:`. Verificar duplicatas MRO — DELETAR se existirem.
  **O que entrega:** Violações: 42 → 0. `make check && make test` = 0
  **Agent**: `category=deep`, `load_skills=["flext-architecture-layers"]`
  **Commit**: `refactor(flext-dbt-ldap): namespace governance + MRO dedup (42 violations fixed)`

#### Consumers SEM audit completo (8 projetos — audit como PRIMEIRO passo):

> Para estes projetos, o audit de violações não foi feito ainda.
> O agente DEVE executar o audit como PRIMEIRO passo, seguindo o mesmo padrão dos projetos acima.
> O padrão observado nos consumers auditados sugere violações similares (média 15-20 por projeto).

- [ ] W4-7. **flext-tap-oracle-oic: Audit + namespace governance + MRO dedup + quality gates**

  **Namespace:** TapOracleOic. **Herda de:** FlextMeltanoTypes + FlextOracleOicTypes
  **Duplicatas esperadas (deletar — vêm via MRO):** StreamProcessing, ErrorHandling, DataExtraction, ConfigValidation, StateManagement

  **O que fazer:**
  1. AUDIT: `grep -n '^    class ' src/flext_tap_oracle_oic/{constants,typings,protocols,models,utilities}.py` — listar TODAS as classes raiz
  2. Para cada classe raiz que NÃO é `TapOracleOic`: classificar como VIOLAÇÃO
  3. Para cada violação: decidir se é duplicata MRO (DELETAR) ou conteúdo único (MOVER para `class TapOracleOic:`)
  4. Executar todas as correções
  5. Auditar módulos + test facades (R3, R6)
  6. Quality gates 0% (R9, R22)

  **Agent**: `category=deep`, `load_skills=["flext-architecture-layers"]`
  **Commit**: `refactor(flext-tap-oracle-oic): namespace governance + MRO dedup`

- [ ] W4-8. **flext-tap-oracle-wms: Audit + namespace governance + MRO dedup + quality gates**
  **Namespace:** TapOracleWms. **Herda de:** FlextMeltanoTypes + FlextOracleWmsTypes
  **Duplicatas esperadas:** ConfigValidation, StateManagement, StreamUtilities
  (Mesmo template que W4-7)
  **Agent**: `category=deep`, **Commit**: `refactor(flext-tap-oracle-wms): namespace governance + MRO dedup`

- [ ] W4-9. **flext-tap-ldap: Audit + namespace governance + MRO dedup + quality gates**
  **Namespace:** TapLdap. **Herda de:** FlextMeltanoTypes + FlextLdapTypes
  (Mesmo template que W4-7)
  **Agent**: `category=deep`, **Commit**: `refactor(flext-tap-ldap): namespace governance + MRO dedup`

- [ ] W4-10. **flext-target-oracle-oic: Audit + namespace governance + MRO dedup + quality gates**
  **Namespace:** TargetOracleOic. **Herda de:** FlextMeltanoTypes + FlextOracleOicTypes
  (Mesmo template que W4-7)
  **Agent**: `category=deep`, **Commit**: `refactor(flext-target-oracle-oic): namespace governance + MRO dedup`

- [ ] W4-11. **flext-target-ldap: Audit + namespace governance + MRO dedup + quality gates**
  **Namespace:** TargetLdap. **Herda de:** FlextMeltanoTypes + FlextLdapTypes
  **Duplicatas esperadas:** ConfigValidation, StateManagement, StreamUtilities
  (Mesmo template que W4-7)
  **Agent**: `category=deep`, **Commit**: `refactor(flext-target-ldap): namespace governance + MRO dedup`

- [ ] W4-12. **flext-target-ldif: Audit + namespace governance + MRO dedup + quality gates**
  **Namespace:** TargetLdif. **Herda de:** FlextMeltanoTypes + FlextLdifTypes
  **Duplicatas esperadas:** ConfigValidation, StateManagement, StreamUtilities
  (Mesmo template que W4-7)
  **Agent**: `category=deep`, **Commit**: `refactor(flext-target-ldif): namespace governance + MRO dedup`

- [ ] W4-13. **flext-dbt-oracle: Audit + namespace governance + MRO dedup + quality gates**
  **Namespace:** DbtOracle. **Herda de:** FlextMeltanoTypes + FlextDbOracleTypes
  (Mesmo template que W4-7)
  **Agent**: `category=deep`, **Commit**: `refactor(flext-dbt-oracle): namespace governance + MRO dedup`

- [ ] W4-14. **flext-dbt-ldif: Audit + namespace governance + MRO dedup + quality gates**
  **Namespace:** DbtLdif. **Herda de:** FlextMeltanoTypes + FlextLdifTypes
  (Mesmo template que W4-7)
  **Agent**: `category=deep`, **Commit**: `refactor(flext-dbt-ldif): namespace governance + MRO dedup`

---

### WAVE 5: External + Workspace Validation (2 projetos + 1 validação — R8)

- [ ] W5-1. **algar-oud-mig: Audit + namespace governance + quality gates**

  **Contexto:** Projeto externo — NÃO é importado por nenhum hub. Padrão próprio.
  **O que fazer:**
  1. AUDIT: verificar quais facades existem e sua estrutura
  2. Aplicar namespace governance se facades existirem
  3. Quality gates 0% (R9, R22)
  **Agent**: `category=deep`, **Commit**: `refactor(algar-oud-mig): namespace governance`

- [ ] W5-2. **gruponos-meltano-native: Audit + namespace governance + quality gates**

  **Contexto:** Projeto externo — NÃO é importado por nenhum hub. Padrão próprio.
  **O que fazer:**
  1. AUDIT: verificar quais facades existem e sua estrutura
  2. Aplicar namespace governance se facades existirem
  3. Quality gates 0% (R9, R22)
  **Agent**: `category=deep`, **Commit**: `refactor(gruponos-meltano-native): namespace governance`

- [ ] W5-3. **Workspace validation final**

  **O que fazer:**
  ```bash
  make validate VALIDATE_SCOPE=workspace  # DEVE retornar 0 issues
  ```
  **O que entrega:** Validação workspace-wide de que TUDO está consistente
  **Agent**: `category=quick`
  **Evidence**: `.sisyphus/evidence/wave-5/workspace-validate.txt`

## WAVE FINAL — Verificação Cruzada (4 agentes em paralelo, TODOS devem APROVAR)

- [ ] F1. **Auditoria de Compliance ao Plano** — `oracle`
  Ler o plano inteiro. Para cada regra R1-R22: verificar implementação (ler arquivo, rodar comando). Para cada guardrail G1-G12: buscar padrões proibidos no codebase — rejeitar com file:line se encontrado. Verificar que arquivos de evidência existem em `.sisyphus/evidence/`. Comparar deliverables contra o plano.
  Output: `Regras [N/22] | Guardrails [N/12] | Tasks [N/N] | VEREDITO: APPROVE/REJECT`

- [ ] F2. **Revisão de Qualidade de Código** — `unspecified-high`
  Rodar `make check` + `make test` em TODOS os 31 projetos. Revisar todos os arquivos alterados buscando: `as any`/`@ts-ignore`, empty catches, console.log em prod, código comentado, imports não usados. Verificar AI slop: comentários excessivos, over-abstraction, nomes genéricos.
  Output: `Build [PASS/FAIL] | Lint [PASS/FAIL] | Tests [N pass/N fail] | VEREDITO`

- [ ] F3. **QA Real** — `unspecified-high`
  Começar de estado limpo. Para cada projeto: importar facade, verificar que namespace resolve corretamente, verificar que MRO traz classes dos hubs, verificar que zero classes estão no raiz (exceto core). Testar integração cross-project.
  Output: `Projetos [N/31 pass] | Namespace [N/N] | MRO [N/N] | VEREDITO`

- [ ] F4. **Checagem de Fidelidade ao Escopo** — `deep`
  Para cada task: ler "O que fazer", ler diff real (git log/diff). Verificar 1:1 — tudo no spec foi feito (nada faltando), nada além do spec foi feito (sem scope creep). Verificar compliance com "Must NOT do". Detectar contaminação cross-task.
  Output: `Tasks [N/N compliant] | Contaminação [CLEAN/N issues] | VEREDITO`

---

## ESTRATÉGIA DE COMMIT

- Um commit por projeto após completar TODAS as etapas
- Formato: `refactor(flext-{project}): namespace governance + MRO dedup`
- Pre-commit: `make check && make test` com 0 falhas
- Bead update após cada commit

---

## CRITÉRIOS DE SUCESSO (R9, R10, R11, R20)

### O que o plano entrega (R20):
- [ ] TODOS os 31 projetos passam `make check && make test` com 0 issues
- [ ] TODOS os src facades usam proper namespace inner classes (R4, R14)
- [ ] TODOS os test facades usam padrão `.Tests.` (R2, R6)
- [ ] TODOS os consumers têm conteúdo MÍNIMO próprio — herdado via MRO (R1, R15, R16)
- [ ] TODAS as referências usam acesso com namespace completo — `t.Meltano.StreamProcessing`, NÃO `t.StreamProcessing` (R13)
- [ ] Zero atributos/classes no nível raiz em facades não-core (R14)
- [ ] Zero duplicatas de classes entre projetos — centralizadas via MRO (R1)
- [ ] Zero factories — só facade classes + MRO (R17)
- [ ] `make validate VALIDATE_SCOPE=workspace` passa

### Como ter certeza que vai entregar (R20):
- Beads controlam progresso por projeto (R12)
- Agentes de verificação rodam quality gates após cada projeto (R12)
- Evidência capturada em `.sisyphus/evidence/wave-{N}/` para cada projeto
- Wave Final com 4 agentes de revisão independentes
- NADA é deixado para depois (R10, R21)
- NADA é pulado por complexidade (R10, R21)
