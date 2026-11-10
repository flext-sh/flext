# FLEXT Service Architecture and Facade Governance Law

## 1. Composição de Serviços e MRO em Três Níveis
1. **Nível 1 (Subserviços de Domínio Especializados):**
   - Residem em `src/<pkg>/services/_<dominio>/<funcao>.py`.
   - Cada subserviço implementa uma responsabilidade única e herda de `<Pkg>Service`.
   - Declara métodos de negócio decorados com `@h.handler(command=m.<Pkg>.<Comando>Input)`.
   - NUNCA declare constantes, tipos, protocolos ou modelos soltos dentro de subserviços.
2. **Nível 2 (Serviço Raiz do Domínio):**
   - Reside em `src/<pkg>/services/<dominio>.py`.
   - A classe `<Pkg><Dominio>` compõe todos os seus subserviços via herança múltipla cooperativa (MRO) e herda de `<Pkg>Service`.
   - Não reimplementa a lógica interna dos subserviços; atua como agregador coeso do domínio.
3. **Nível 3 (Fachada Unificada de Aplicação):**
   - Reside em `src/<pkg>/api.py`.
   - A classe `<Pkg>` herda cooperativamente via MRO de todos os serviços raiz sob `src/<pkg>/services/*.py`.
   - Expõe a instância singleton estável (ex: `dc: DcFinan = DcFinan(...)`) como ponto único de integração externa, CLI e UI.

## 2. Roteador Canônico de CLI Automatizado (Padrão FlextCli + Discovery)
1. **Zero Código de Roteamento Manual:**
   - É PROIBIDO criar sub-roteadores manuais em `_cli/` ou construir árvores de sub-comandos com `add_typer`.
   - Todo comando da CLI nasce obrigatoriamente de um método decorado com `@h.handler(command=...)` na facade composta.
2. **Descoberta Dinâmica de Rotas:**
   - O transporte CLI (`src/<pkg>/cli.py`) descobre as rotas automaticamente através de `h.Discovery.scan_class(type(facade))`.
   - Filtra exclusivamente os comandos declarados no conjunto público imutável `c.<Pkg>.COMANDOS_PUBLICOS: Final[frozenset[str]]`.
   - Valida que todo comando seja subclasse de `m.BaseModel`.
3. **Mapeamento Declarativo:**
   - Constrói instâncias imutáveis de `m.Cli.ResultCommandRoute`:
     - `name`: nome do handler convertido para kebab-case (`nome.replace("_", "-")`).
     - `help_text`: primeira linha do docstring do método.
     - `model_cls`: modelo Pydantic do comando.
     - `handler`: método da facade (`getattr(facade, nome)`).
4. **Ciclo de Execução e Encerramento:**
   - Registra as rotas em lote com `cli.register_result_routes(app, rotas)`.
   - Trata sinais de encerramento (`signal.SIGTERM`, `signal.SIGINT`) via `signal.signal(sinal, handler)`.
   - Executa via `resultado: p.Result[bool] = cli.execute_app(app, prog_name=c.<Pkg>.PROGRAMA, args=argv)`.
   - Conclui o processo estritamente pelo contrato `cli.finalize_result(resultado)`.
5. **Introspecção de Contratos:**
   - Fornece `entrada_do_verbo(verbo: str) -> t.ModelClass[t.BaseModelType]` para consulta tipada de qualquer comando.

## 3. FlextService como Classe Pydantic e Declaração de Dados (DSL)
1. `FlextService` (`s`) herda de Pydantic `BaseModel` (`EnforcedModel`, `ManagedModel`, `ArbitraryTypesModel`).
2. Todo serviço é um modelo Pydantic tipado e validado por construção.
3. Eliminar DTOs e protocols intermediários supérfluos: o próprio serviço declara seus campos com `Field(...)`, validações `@field_validator` e métodos de execução, provendo uma sintaxe DSL limpa e expressiva.

## 4. Proibição Absoluta de Declarações Locais nos Serviços (Anti-GOD Pattern)
1. É TERMINANTEMENTE PROIBIDO declarar `TypeAlias`, `TypedDict`, `dataclass`, `BaseModel`, `NewType`, enums ou constantes dentro de `src/<pkg>/services/`.
2. Toda entidade pertence estritamente aos facades canônicos sob o namespace do pacote `(c|t|p|m|u).<Pkg>.<Dominio><Tipo>`:
   - Constantes: `src/<pkg>/_constants/<dominio>.py` ➔ `c.<Pkg>.<Dominio><Nome>`
   - Tipos estritos: `src/<pkg>/_typings/<dominio>.py` ➔ `t.<Pkg>.<Dominio><Nome>`
   - Protocolos: `src/<pkg>/_protocols/<dominio>.py` ➔ `p.<Pkg>.<Dominio><Nome>`
   - Modelos Pydantic v2: `src/<pkg>/_models/<dominio>.py` ➔ `m.<Pkg>.<Dominio><Nome>`
   - Utilitários puros: `src/<pkg>/_utilities/<dominio>.py` ➔ `u.<Pkg>.<Dominio><Nome>`
3. O serviço consome exclusivamente esses facades. Qualquer declaração necessária deve ser criada no facade e apagada do serviço.
4. Use `python -m flext_infra codegen lazy-init` para regenerar automaticamente todos os `__init__.py` PEP 562.

## 5. Testes Comportamentais com flext_tests e Fixtures Canônicas
1. Testes em `tests/unit/` utilizam os facades de teste `tests.c`, `tests.t`, `tests.p`, `tests.m`, `tests.u`.
2. Asserções contratuais utilizam os matchers do FLEXT: `tests.tm.ok(res)`, `tests.tm.fail(res)`, `tests.tm.fail_code(res, ...)`, `tests.tm.that(...)`.
3. Dados reais de entrada e gabarito residem em `tests/fixtures/<dominio>/` e são injetados via `tests/conftest.py` com `tests.tf.read`.
4. POLÍTICA ZERO-MOCK: Proibido mocks de métodos privados do projeto (`unittest.mock.patch`), monkey-patching ou asserções frágeis sobre strings de log. Verifique o comportamento observável através das fronteiras públicas.

## 6. Eliminação Sumária de Módulos Legados (Zero Coexistência)
1. A lei universal de coexistência proíbe que código velho e novo convivam.
2. Assim que um novo módulo de serviço for implementado e validado pelos testes nativos e auditores de negócio, o módulo legado antigo DEVE SER APAGADO imediatamente.
3. Não manter sub-roteadores manuais em `_cli/`, arquivos de compatibilidade `_old.py`, ou cópias monolíticas em subdiretórios.
