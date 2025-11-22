# ConditionalExecutionRequest (`FlextModels.Base.ConditionalExecutionRequest`)

## Visão geral
DTO para encapsular fluxos condicionais executados dentro de `FlextService`. Foi concebido para eliminar ramos `if/else` espalhados pelos serviços e garantir que condições, ações e contexto trafeguem juntos. A classe vive em `flext_core/_models/base.py:181-196` e é exposta como `FlextModels.ConditionalExecutionRequest`.

## Contrato detalhado
- Herança: `FlextModelsEntity.ArbitraryTypesModel` (validação estrita `extra="forbid"`, suporte a tipos arbitrários).
- Aliases: `ConditionCallable = Callable[[object], bool]` e `ActionCallable = Callable[..., object]` definidos no mesmo módulo.
- `validate_condition`: placeholder para validações pós-instanciação (atualmente retorna o valor sem checagens, mas serve como ponto de extensão).

| Campo        | Tipo                             | Observações |
| ------------ | -------------------------------- | ----------- |
| `condition`  | `ConditionCallable`              | Obrigatório; recebe normalmente `self` (instância de serviço/handler). |
| `true_action`| `ActionCallable \| None`         | Executada quando a condição retorna `True`. |
| `false_action`| `ActionCallable \| None`        | Executada quando a condição retorna `False`. |
| `context`    | `dict[str, object]`              | Metadados auxiliares (pode carregar parâmetros, métricas, etc.). |

## Fluxo dentro do `FlextService`
Em `flext_core/src/flext_core/service.py:1412-1455`, o método `execute_conditionally` consome o DTO:
1. Avalia `request.condition(self)` convertendo o resultado para `bool`.
2. Se a condição falha e `false_action` existe, delega para `_execute_action` (que já integra com `FlextResult`).
3. Se falha sem `false_action`, retorna `self.fail("Condition not met")` (propagando `FlextResult` de erro).
4. Se a condição passa e `true_action` existe, chama `_execute_action` novamente.
5. Caso não haja ações explícitas, segue com a operação padrão do serviço.

Esse fluxo garante compatibilidade com `FlextResult`, `FlextLogger` e `FlextUtilities` dentro da classe base `FlextService`.

## Integrações e usos
- **Flext core**: além do método citado, o DTO aparece em `flext_core/src/flext_core/models.py:357` como parte do namespace `FlextModels` e participa do `model_rebuild` para garantir compatibilidade com Pydantic v2.
- **Testes**: `flext-core/tests/unit/test_service.py` e `flext-core/tests/unit/test_service_coverage_100.py` simulam cenários de condição verdadeira/falsa, ausência de ações, propagação de exceções, etc.
- **Projetos externos**: ainda não há adoção em taps/targets; fluxos condicionais em `flext-target-oracle` ou `flext-ldif` continuam sendo escritos manualmente.

## Pontos fortes x riscos
- **Fortes**: padroniza execução condicional, integra com `_execute_action` (que já trata `FlextResult` e validações), oferece `context` para transportar dados entre condição e ações.
- **Riscos**: `validate_condition` ainda é um stub; não há tipagem para o retorno das ações, então `FlextResult` pode ser quebrado por objetos inesperados; nenhuma telemetria/logging embutida — difícil rastrear porque uma condição falhou em produção.

## Backlog recomendado
1. **Validação real**: implementar `validate_condition` garantindo que o callable aceite `self` ou nenhum argumento (`inspect.signature`).
2. **Integração com `LogOperation`**: registrar automaticamente decisões condicionalmente (qual condição foi avaliada, resultado, ação executada) para facilitar auditoria.
3. **Builders declarativos**: expor helpers (`ConditionalExecutionRequest.when(predicate).then(func).otherwise(func)`) para tornar o uso mais legível em projetos Singer/LDIF.
4. **Tipagem de resultado**: permitir declarar `expected_result_type: type[TDomainResult]` para que `_execute_action` valide automaticamente o retorno.
5. **Adoção cross-projeto**: documentar casos em `flext-target-oracle` (ex.: reprocessar lote só se `should_retry` for verdadeiro) e `flext-ldif` (executar fallback quando `entry` não existe) usando o DTO em vez de lógica manual.
