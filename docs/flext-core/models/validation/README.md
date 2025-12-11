# FlextModels · Validação Oficial

Namespace que expõe funções corporativas de validação para entidades, agregados, CQRS e pipelines. Serve como “façade” pública para rotinas implementadas em `flext_core/_models/validation.py`, `x.Validation` e constantes.

> Fonte: AST de `flext_core/models.py` + busca estática (testes ignorados).

## Componentes

### `Validation`

**Por que existe / qual problema resolve**

- Fornece ponto de entrada único para validações que são usadas em múltiplas camadas (entidades, agregados, CQRS, pipelines batch). Em vez de importar diretamente `flext_core._models.validation`, os projetos acessam `FlextModels.Validation`, garantindo estabilidade e backward compatibility.
- Ajuda a documentar quais validações oficiais existem e desestimula criação de helpers duplicados em cada serviço.

**Como funciona**

- O namespace simplesmente referencia as funções definidas em `FlextModelsValidation` (interno). São funções puras que retornam `FlextResult[bool]`, permitindo composição com o padrão railway (`flat_map`). Exemplos:
  - `validate_business_rules(entity)` – verifica invariantes declarados.
  - `validate_event_sourcing(events)` – garante consistência em replays.
- Por ser uma camada de façade, não possui campos ou estado adicional.

**Aplicações esperadas**

- Serviços e handlers que desejam padronizar validações (ex.: antes de persistir uma entidade, antes de responder queries CQRS, ou em pipelines batch que precisam validar consistência entre registros).
- Ferramentas internas (CLI, scripts) podem chamar essas funções para rodar checklists de validação (por exemplo, `validate_batch` em conversões LDIF).

**Adoções atuais**

- Até o momento não encontramos chamadas diretas fora do módulo base; muitos projetos ainda usam `x.Validation`. Há oportunidade para migrar o uso público para este namespace.

**Benefícios tangíveis**

- Centraliza contratos, facilitando evolução/observabilidade das validações. Quaisquer melhorias feitas no módulo interno passam a valer para todos os consumidores.
- Ajuda a reduzir divergências de regras entre squads – todos partem das mesmas rotinas oficiais.

**Duplicidades e relação com outros módulos**

- `flext_core/constants.py` define limites e literais usados pelos validadores (por exemplo, tamanhos máximos, enumerações). Não é uma duplicação, mas sim fonte de parâmetros.
- `flext_core/mixins.py` expõe `x.Validation` com foco em railway-oriented programming (ROP). Ele pode chamar internamente as mesmas funções ou estender comportamentos.

**Oportunidades / próximos passos**

- **Padronizar uso**: orientar squads a trocar chamadas diretas a helpers caseiros por `FlextModels.Validation.*`.
- **Instrumentação**: se adicionarmos métricas/logs nas funções internas, todos os consumidores se beneficiam sem mudar código.
- **Cobertura de testes**: reforçar que testes unitários dos módulos de domínio devem cobrir chamadas a essas funções para garantir que regras corporativas sejam respeitadas.
