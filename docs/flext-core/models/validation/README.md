# FlextUtilities · ModelsValidation

<!-- TOC START -->

- [Componentes](#componentes)
  - [`ModelsValidation`](#modelsvalidation)
  <!-- TOC END -->

Namespace que expõe funções corporativas de validação para entidades, agregados, CQRS e pipelines. Serve como "façade" pública para rotinas implementadas em `flext_core/_utilities/validation.py`.

> **ATUALIZADO**: A validação agora é acessada via `FlextUtilities.ModelsValidation` (ou `u.ModelsValidation`), não mais via `FlextModels.Validation`.

## Componentes

### `ModelsValidation`

**Por que existe / qual problema resolve**

- Fornece ponto de entrada único para validações que são usadas em múltiplas camadas (entidades, agregados, CQRS, pipelines batch). Em vez de importar diretamente `flext_core._utilities.validation`, os projetos acessam `FlextUtilities.ModelsValidation`, garantindo estabilidade e backward compatibility.
- Ajuda a documentar quais validações oficiais existem e desestimula criação de helpers duplicados em cada serviço.

**Como funciona**

- O namespace simplesmente referencia as funções definidas em `FlextModelsValidation` (interno). São funções puras que retornam `FlextResult[bool]`, permitindo composição com o padrão railway (`flat_map`). Exemplos:
  - `validate_business_rules(entity)` – verifica invariantes declarados.
  - `validate_event_sourcing(events)` – garante consistência em replays.
- Por ser uma camada de façade, não possui campos ou estado adicional.

**Acesso direto via FlextUtilities**

As funções de validação também estão disponíveis diretamente na classe `FlextUtilities`:

```python
from flext_core.utilities import u

# Acesso via namespace
u.ModelsValidation.validate_business_rules(entity)
u.ModelsValidation.validate_event_sourcing(events)

# Acesso direto (aliases)
u.validate_business_rules(entity)
u.validate_domain_event(event)
```

**Aplicações esperadas**

- Serviços e handlers que desejam padronizar validações (ex.: antes de persistir uma entidade, antes de responder queries CQRS, ou em pipelines batch que precisam validar consistência entre registros).
- Ferramentas internas (CLI, scripts) podem chamar essas funções para rodar checklists de validação (por exemplo, `validate_batch` em conversões LDIF).

**Benefícios tangíveis**

- Centraliza contratos, facilitando evolução/observabilidade das validações. Quaisquer melhorias feitas no módulo interno passam a valer para todos os consumidores.
- Ajuda a reduzir divergências de regras entre squads – todos partem das mesmas rotinas oficiais.

**Duplicidades e relação com outros módulos**

- `flext_core/constants.py` define limites e literais usados pelos validadores (por exemplo, tamanhos máximos, enumerações). Não é uma duplicação, mas sim fonte de parâmetros.
- `flext_core/mixins.py` expõe `x.Validation` com foco em railway-oriented programming (ROP). Ele pode chamar internamente as mesmas funções ou estender comportamentos.

**Métodos disponíveis**

- `validate_business_rules` - Valida regras de negócio
- `validate_cross_fields` - Valida campos cruzados
- `validate_performance` - Valida requisitos de performance
- `validate_batch` - Valida operações em lote
- `validate_domain_invariants` - Valida invariantes de domínio
- `validate_aggregate_consistency_with_rules` - Valida consistência de agregado com regras
- `validate_event_sourcing` - Valida event sourcing
- `validate_cqrs_patterns` - Valida padrões CQRS
- `validate_domain_event` - Valida evento de domínio
- `validate_aggregate_consistency` - Valida consistência de agregado
- `validate_entity_relationships` - Valida relacionamentos de entidades
- `validate_uri` - Valida URIs
- `validate_port_number` - Valida números de porta

**Oportunidades / próximos passos**

- **Padronizar uso**: orientar squads a usar `FlextUtilities.ModelsValidation.*` ou `u.ModelsValidation.*`.
- **Instrumentação**: se adicionarmos métricas/logs nas funções internas, todos os consumidores se beneficiam sem mudar código.
- **Cobertura de testes**: reforçar que testes unitários dos módulos de domínio devem cobrir chamadas a essas funções para garantir que regras corporativas sejam respeitadas.
