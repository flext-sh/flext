# FlextModels · Coleções e Estruturas Configuráveis


<!-- TOC START -->
- [Componentes](#componentes)
  - [`Categories`](#categories)
  - [`Statistics`](#statistics)
  - [`Config`](#config)
  - [`Results`](#results)
  - [`Rules`](#rules)
  - [`Options`](#options)
<!-- TOC END -->

Este conjunto agrupa modelos genéricos usados para estruturar coleções categorizadas, consolidação de métricas, configuração dinamicamente mesclável, resultados agregáveis e regras/opções declarativas. Todos os dados foram levantados via AST em `flext_core/models.py` e confirmados com uma varredura estática (ignorando testes) para mapear uso real no monorepo.

Para cada componente listamos por que ele existe, como funciona internamente, onde deveria ser aplicado no negócio, o que já o consome hoje, benefícios tangíveis e recomendações de adoção ou descarte.

## Componentes

### `Categories`

**Por que existe / qual problema resolve**

- Normaliza coleções multi-categoria (ex.: usuários, grupos, objetos de schema) evitando arrays paralelos ou dicionários sem validação. Fornece estrutura única para pipelines de classificação.

**Como funciona**

- `Categories[T]` herda `ArbitraryTypesModel` e mantém um `dict[str, list[T]]`. Expõe utilitários (`add_entries`, `set_entries`, `summary`, `total_entries`, `category_names`, operações tipo dict) e validação estrita (`ConfigDict(strict=True, validate_assignment=True)`).
- Computed fields `total_entries` e `summary` garantem métricas instantâneas sem escrever loops em cada serviço.

**Aplicações esperadas no negócio**

- Pipelines LDIF/LDAP que agrupam entradas por tipo (usado em relatórios e dashboards).
- Ferramentas de observabilidade que precisam classificar eventos/respostas por categoria antes de gerar métricas.
- DSLs de ETL (flext-meltano-native) para organizar entidades por “tabelas” ou “streams”.

**Adoções atuais**

- Sem referências fora do módulo base.

**Benefícios concretos**

- Elimina repetição de código para agrupar itens e evita inconsistências entre projetos ao manipular coleções categorizadas.
- A validação estrita impede que categorias recebam tipos inesperados, reduzindo falhas de runtime.

**Oportunidades / decisões**

- Integrar no `flext-ldif/src/flext_ldif/_models/results.py`, que hoje monta dicionários manualmente para categorias de entradas.
- Caso a plataforma adote outra abstração (ex.: pandas DataFrame), mover `Categories` para um pacote experimental para não comprometer a API oficial.

### `Statistics`

**Por que existe / qual problema resolve**

- Provê base imutável para estatísticas de processamento com agregação declarativa, evitando que cada módulo crie métodos próprios para somar contadores ou concatenar listas.
- Ajuda squads diferentes (ldap, ldif, observability) a compartilhar o mesmo formato de métricas.

**Como funciona**

- Value object (`FlextModelsEntity.Value`) e, portanto, hashável/imutável. Possui `aggregate`, que aceita `list[Self]` e combina campos automaticamente: soma números, concatena listas, mantém o último valor para tipos não agregáveis (usando `FlextRuntime` para detectar list-like).

**Aplicações esperadas no negócio**

- Consolidação de métricas em sincronizações LDIF/LDAP, relatórios de ingestão, monitoramento de pipelines ETL.
- Dashboards corporativos que recebem múltiplas execuções e precisam de um método padrão para agregá-las.

**Adoções atuais**

- `flext-ldap/src/flext_ldap/models.py` e `flext-ldif/src/flext_ldif/models.py` utilizam este modelo.

**Benefícios concretos**

- Reduz risco de somatórios inconsistentes e facilita auditorias (cada campo segue a mesma regra de agregação em todo o ecossistema).

**Oportunidades / decisões**

- `flext-ldif/src/flext_ldif/_models/results.py` implementa um `Statistics` específico para LDIF com dezenas de campos. Avaliar se parte dessa lógica pode herdar do modelo genérico ou se devemos documentar oficialmente as diferenças para evitar duplicação.

### `Config`

**Por que existe / qual problema resolve**

- Ponto central para configurações mutáveis com utilidades corporativas: `merge`, `diff`, `from_dict`, `with_updates`, `__eq__` por valor. Evita que cada time crie dicionários com merges inconsistentes.

**Como funciona**

- `ArbitraryTypesModel` não congelado (explicitamente não-hashable). Métodos expostos:
  - `merge`: cria novo config com prioridade para o outro objeto.
  - `with_updates`/`from_dict`/`to_dict`: padronizam conversões.
  - `diff`: retorna um mapa com campos divergentes, útil para auditoria e debugging.

**Aplicações esperadas no negócio**

- Definição de configs para conectores (LDAP, Oracle, Observability) e para serviços que precisam mesclar defaults com overrides por cliente.
- APIs REST/gRPC que aceitam payloads de configuração e precisam compará-los com valores persistidos.

**Adoções atuais**

- `flext-ldap/src/flext_ldap/models.py` utiliza o modelo.

**Benefícios concretos**

- Fornece operações de merge/diff já testadas e reduz o risco de bug ao comparar configs complexos.

**Oportunidades / decisões**

- O pacote `flext-grpc/src/flext_grpc/models.py` mantém um `Config` próprio para servidores/clients gRPC. Migrar para `FlextModels.Collections.Config` evitaria duplicidade de métodos e garantiria consistência.

### `Results`

**Por que existe / qual problema resolve**

- Define base imutável para resultados (quantidades processadas, erros, detalhes). Sem isso, cada time implementa agregações de forma diferente, dificultando relatórios consolidados.

**Como funciona**

- Value object com método `aggregate` que delega ao helper `_aggregate_values`: soma números, concatena listas, mescla dicionários (com override para valores mais novos) e mantém o último valor para outros tipos. Usa `FlextRuntime` para detectar tipos list/dict-like.

**Aplicações esperadas no negócio**

- Somar resultados de execuções parciais (shards, batches, workers) antes de gerar o relatório final ou devolver a resposta para o cliente.

**Adoções atuais**

- `flext-ldap/src/flext_ldap/models.py` utiliza o modelo.

**Benefícios concretos**

- Reduz a chance de unidades retornarem resultados inconsistentes e habilita agregação padronizada no nível do orquestrador.

**Oportunidades / decisões**

- Incentivar uso em outros projetos (targets, taps) para padronizar respostas de operações longas. Sem plano de expansão, considerar documentar que o modelo será mantido apenas como referência.

### `Rules`

**Por que existe / qual problema resolve**

- Fornece base Pydantic (`extra="forbid"`) para regras declarativas de configuração, garantindo que apenas campos conhecidos sejam aceitos e que qualquer regra malformada seja rejeitada cedo.

**Como funciona**

- `ArbitraryTypesModel` com `validate_assignment=True` e `extra="forbid"`. Ideal para representar matrizes de regras, validadores de negócio ou políticas dinâmicas.

**Aplicações esperadas no negócio**

- Modelagem de regras LDIF (ex.: matriz de conversão, filtros). Também útil para regras de transformação em pipelines de ETL ou políticas de validação em `flext-core`.

**Adoções atuais**

- `flext-ldif/src/flext_ldif/_models/config.py` utiliza o modelo.

**Benefícios concretos**

- Evita que clientes internos adicionem campos inesperados nas regras, facilitando auditoria e validação.

**Oportunidades / decisões**

- Expandir uso para outros módulos que definem regras (ex.: `flext-quality`). Caso continue restrito a LDIF, avaliar documentar como “base legacy” para evitar manutenção desnecessária.

### `Options`

**Por que existe / qual problema resolve**

- Value object para opções configuráveis com merge/filtragem embutidos. Sem ele, cada time mantém combinações de defaults/overrides manualmente.

**Como funciona**

- Herda `FlextModelsEntity.Value`. Disponibiliza `merge` (overrides têm precedência e usa `exclude_unset`), `with_only` (retorna dict com subset de campos) e serialização automática.

**Aplicações esperadas no negócio**

- Configurações opcionais em conectores LDAP/TAP/TARGET, definindo overrides por execução ou cliente.

**Adoções atuais**

- `flext-ldap/src/flext_ldap/models.py` utiliza o modelo.

**Benefícios concretos**

- Permite construir DSLs declarativas de opções, facilita testes (value objects) e evita “dicionários mágicos”.

**Oportunidades / decisões**

- Incentivar reuso em pacotes como `flext-target-oracle` e `flext-tap-ldif`, que atualmente definem opções em dicionários. Ausente plano de migração, registrar a intenção para evitar backlog eterno.
