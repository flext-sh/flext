# FlextModels · Roteamento de Mensagens


<!-- TOC START -->
- [Componentes](#componentes)
  - [`MessageUnion`](#messageunion)
<!-- TOC END -->

Tipos auxiliares como o discriminated union que habilita o roteamento automático de mensagens CQRS.

> Dados extraídos via AST em `flext_core/models.py` e confirmados com busca estática (testes ignorados).

## Componentes

### `MessageUnion`

**Por que existe / qual problema resolve**

- Construir um tipo único (via `Annotated` + `Discriminator`) que represente comandos, queries e eventos (`DomainEvent`). Isso permite que dispatchers e handlers aceitem um único argumento e façam `match`/`if` com base em `message_type`, mantendo tipagem forte.
- Evita condicional manual `if isinstance(command, Command)` repetida em cada módulo, além de ser compatível com Pydantic v2 (o discriminador garante validação automática).

**Como funciona**

- Definido inline em `flext_core/models.py`:

  ```python
  _MessageUnion = Annotated[
      Cqrs.Command | Cqrs.Query | DomainEvent,
      Discriminator("message_type"),
  ]
  MessageUnion = _MessageUnion
  ```

- Cada tipo (Command/Query/DomainEvent) define `message_type` com valores literais (`"command"`, `"query"`, `"event"`). Quando um objeto é validado contra o union, o Pydantic escolhe o ramo correto automaticamente.

**Aplicações esperadas**

- APIs que recebem mensagens heterogêneas (ex.: dispatchers, filas, gRPC) podem tipar seu parâmetro como `FlextModels.MessageUnion` e lidar com três casos distintos com segurança.
- Ferramentas de roteamento e middlewares podem logar/serializar mensagens sem precisar saber o tipo estático.

**Adoções atuais**

- Ainda não há uso fora do módulo base (os projetos tratam os objetos individualmente). É uma oportunidade para uniformizar dispatchers e handlers.

**Benefícios tangíveis**

- Simplifica APIs: um único tipo cobre toda a superfície CQRS.
- Reduz erros de roteamento: se alguém enviar um objeto com `message_type` inválido, a validação falha antes da execução.
- Garante compatibilidade futura: novos tipos (ex.: sagas) podem ser incorporados adicionando-se ao union sem quebrar assinaturas.

**Decisões / próximos passos**

- Incentivar repositórios que implementam pipelines CQRS (`flext-target-oracle`, `flext-oracle-wms`, camadas de dispatcher) a tiparem seus parâmetros com `MessageUnion` para aproveitar o discriminador.
- Caso continue sem uso prático, considerar expor exemplos em `examples/` ou mover para uma RFC para evitar que fique “invisível” na API pública.
