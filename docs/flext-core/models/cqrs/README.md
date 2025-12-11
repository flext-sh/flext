# FlextModels · CQRS e Mensageria

Namespace oficial para comandos, queries, handlers e utilidades de roteamento de mensagens. Dados extraídos via AST em `flext_core/models.py` e confirmados com busca estática (testes ignorados) para mapear uso real.

Cada item a seguir mostra motivação, funcionamento interno, aplicações recomendadas, adoções atuais, benefícios e decisões sugeridas.

## Componentes

### `Cqrs`

**Por que existe / qual problema resolve**

- Agrupa todos os building blocks CQRS (Command, Query, Handler, Bus, Pagination) e funções auxiliares (\_get defaults). Sem essa namespace cada projeto criaria versões incompatíveis, tornando o roteamento de mensagens inconsistente.

**Como funciona**

- Estrutura baseada em Pydantic com classes filhas de `FlextModelsEntity` e helpers. Exposição oficial ocorre via `FlextModels.Cqrs` para garantir compatibilidade com o restante do ecossistema.

**Adoções atuais**

- Namespace importado em `flext-core/examples/14_flext_handlers_complete.py`, `flext-core/src/flext_core/handlers.py`, `flext-oracle-wms/src/flext_oracle_wms/api.py`, `flext-target-oracle/src/flext_target_oracle/target_commands.py`.

**Benefícios / decisões**

- Mantém contrato único para todos os projetos que expõem comandos/queries. O arquivo `flext_core/constants.py` fornece enums/literais complementares, não é duplicação. Recomenda-se que novos projetos (targets/taps) importem diretamente daqui.

#### `Cqrs.Command`

**Motivação**

- Define DTO imutável para comandos, embutindo `message_type="command"`, mixins de identificação (`id`, timestamps) e `command_type` auto derivado do nome da classe.

**Funcionamento**

- Herda `ArbitraryTypesModel`, `IdentifiableMixin`, `TimestampableMixin`. Validator `validate_command` ajusta `command_type`. Campos extras como `issuer_id` permitem rastrear quem enviou o comando.

**Aplicações**

- Produtores de comandos (targets, orquestradores) devem herdar desta classe para garantir compatibilidade com `MessageUnion` e com `FlextHandlerRegistry`.

**Uso atual**

- Ainda não há usos fora de testes; projetos costumam declarar comandos como `BaseModel`. Há oportunidade clara de migração.

**Decisão**

- Incentivar adoção nos módulos que já criam comandos (ex.: `flext-target-oracle`). Caso continue sem uso, documentar como padrão recomendado para futuras implementações.

#### `Cqrs.Pagination`

**Motivação**

- Provê objeto de paginação com `page`, `size`, `offset`, `limit`. Evita repetição de lógica em queries e ensures consistent pages.

**Funcionamento**

- `BaseModel` com defaults de `FlextConstants.Pagination`, validação de limites e propriedades derivadas.

**Aplicações**

- Queries REST/gRPC, adaptadores DB que precisam de `offset`/`limit` calculados automaticamente.

**Uso atual**

- Ainda não referenciado fora do namespace.

**Decisão**

- Documentar que queries devem aceitar este objeto (ou dict compatível) para habilitar features automáticas (ex.: caching). Caso contrário, considerar arquivar se não houver roadmap.

#### `Cqrs.Query`

**Motivação**

- Define envelope padronizado para operações de leitura com filtros, paginação e `query_type`. Inclui `message_type="query"` para uso no discriminated union.

**Funcionamento**

- `BaseModel` com campos `filters`, `pagination` (aceita dict ou `Pagination`), `query_id`, `query_type`. Validators convertem dicts e garantem compatibilidade.

**Aplicações**

- Buscas em APIs, queries em handlers gRPC, operações “read side” em CQRS.

**Uso atual**

- Ainda não há referências externas.

**Decisão**

- Recomendar para times que criam queries (ex.: `flext-oracle-wms`). Sem adoção no próximo ciclo, classificar como experimental.

#### `Cqrs.Bus`

**Motivação**

- Configura o barramento (dispatcher) com rotas, middlewares, timeouts. Sem isso, cada bus teria parâmetros diferentes.

**Funcionamento**

- `BaseModel` com campos para `name`, `description`, `middleware`, `retry_policy`, etc. (ver `_models/cqrs.py`).

**Aplicações**

- Orquestradores que expõem múltiplos handlers/commands (ex.: flext-core bus, oracle API gateway).

**Uso atual**

- Não há registros fora dos testes.

**Decisão**

- Quando formalizarmos o command bus, usar esse DTO como contrato; até lá, avaliar se deve ficar marcado como beta.

#### `Cqrs.Handler`

**Motivação**

- Declara metadados do handler (nome, modos aceitos, categorias, métricas). Sem isso, registries precisam receber dicionários heterogêneos.

**Funcionamento**

- `BaseModel` com campos para `name`, `handler_type`, `supported_modes`, `metadata`, etc., e validações para garantir nomes válidos.

**Aplicações**

- `flext_core/handlers.py` usa este DTO para registrar handlers, e outros projetos podem exportar handlers em configurações YAML/JSON.

**Uso atual**

- Referenciado em `flext-core/examples/14_flext_handlers_complete.py`, `flext-core/src/flext_core/handlers.py`, `flext-oracle-wms/src/flext_oracle_wms/api.py`, `flext-target-oracle/src/flext_target_oracle/target_commands.py`.

**Benefícios / decisões**

- Força padronização no registro e habilita tooling (listagem, introspecção). Manter como estrutura oficial; expandir uso para outros targets.

#### `_get_command_timeout_default` / `_get_max_command_retries_default`

**Motivação**

- Funções internas usadas em testes para garantir que os defaults de timeout/retentativa puxam valores de `FlextSettings` antes de cair nos `FlextConstants`.

**Funcionamento**

- Obtêm `FlextSettings.get_global_instance().dispatcher_timeout_seconds` / `max_retry_attempts` e, se zero ou negativo, retornam o default definido em `FlextConstants.Cqrs`.

**Aplicações**

- Garantem backwards compatibility entre config dinâmico e constantes, principalmente em ambientes onde `FlextSettings` pode ser reconfigurado em runtime.

**Uso atual**

- Somente testes.

**Decisão**

- Mantê-las como helpers internos; se novas APIs precisarem acessar os mesmos defaults, publicá-las oficialmente.

### `_MessageUnion`

**Por que existe / qual problema resolve**

- Fornece union discriminada (Pydantic v2) para Comandos, Queries e Eventos (`DomainEvent`). Substitui tipos genéricos e permite match pattern com `message_type`.

**Como funciona**

- `Annotated[Cqrs.Command | Cqrs.Query | DomainEvent, Discriminator("message_type")]`. O Pydantic valida e encaminha automaticamente o payload correto com base no campo `message_type`.

**Aplicações**

- Message buses, dispatchers e middlewares podem aceitar `FlextModels.MessageUnion` para tratar todos os tipos (command/query/event) com `match` ou ifs simples.

**Uso atual**

- Ainda não há uso fora do módulo principal; os projetos costumam tratar objetos manualmente.

**Benefícios / decisões**

- Permite tipagem única para APIs e simplifica `match`/`isinstance` no dispatcher. Recomenda-se adotá-lo nos handlers do `flext-core` e nas targets que recebem mensagens heterogêneas. Sem adoção, considerar movê-lo para um módulo “experimental” para não inflar a superfície pública.
