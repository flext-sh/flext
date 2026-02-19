# FlextModels · Base (Índice)


<!-- TOC START -->
- [Documentação por modelo](#documentao-por-modelo)
- [Como aproveitar o guia](#como-aproveitar-o-guia)
- [Resumo das mudanças e insights documentados](#resumo-das-mudanas-e-insights-documentados)
<!-- TOC END -->

Este README funciona como hub para os modelos do namespace `FlextModels.Base`. Cada link abaixo aponta para o guia completo do respectivo modelo, incluindo especificação, relacionamentos, exemplos reais e recomendações de adoção.

## Documentação por modelo

- [`Metadata`](Metadata.md) — modelo imutável usado por dispatcher, registry, LDIF e targets.
- [`Payload`](Payload.md) — payload genérico tipado com mixins de identidade e timestamp.
- [`Url`](Url.md) — value object baseado em `HttpUrl` (ainda sem adoção real).
- [`LogOperation`](LogOperation.md) — DTO para logs estruturados de operações/mixins.
- [`TimestampConfig`](TimestampConfig.md) — configuração de timestamps herdada de `Collections.Config`.
- [`SerializationRequest`](SerializationRequest.md) — envelope para parâmetros de serialização.
- [`ConditionalExecutionRequest`](ConditionalExecutionRequest.md) — executa fluxos condicionais em `FlextService`.
- [`StateInitializationRequest`](StateInitializationRequest.md) — DTO para inicializar estado/caches.

## Como aproveitar o guia

- Comece pelo modelo relevante via link acima e siga as seções padrão: especificação, relação/reuso, pontos fortes/fracos, uso real e sugestões.
- Sempre que precisar citar evidências, use os caminhos dos arquivos listados nas seções de “Uso real” para navegar diretamente no código correspondente.
- Use os insights de “Sugestões de melhoria” como backlog de ações para adoção, refino ou descontinuação em cada squad.

## Resumo das mudanças e insights documentados

- A documentação foi dividida em oito arquivos específicos para cada modelo, substituindo o antigo `DETAIL.md`.
- Registramos que apenas `Metadata` possui adoção cruzada (dispatcher, registry, LDIF, targets Oracle). Todos os outros continuam restritos a testes ou sem uso (`Url`, `TimestampConfig`, `SerializationRequest`).
- `Payload`, `LogOperation` e `ConditionalExecutionRequest` receberam diagnóstico de maturidade técnica, mas falta adoção no runtime; cada guia descreve riscos e próximos passos para incorporá-los (ex.: integrar Payload ao dispatcher, ligar LogOperation ao decorator homônimo, validar callables em ConditionalExecutionRequest).
- Modelos de suporte (`StateInitializationRequest`, `TimestampConfig`, `SerializationRequest`) agora têm recomendações explícitas para integração com `FlextService`, `u` e pipelines de serialização.

> Consulte os arquivos individuais sempre que precisar de campos, validações e exemplos concretos antes de expor novos serviços ou refatorar código legado.
