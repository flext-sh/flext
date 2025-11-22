# FlextModels · Metadata Corporativo

Envelope padronizado de metadados para rastrear operações e registrá-las em serviços. É o único módulo zero-dependência da stack justamente para evitar ciclos de import.

Dados levantados via AST (`flext_core/models.py`) e uso confirmado com busca estática (testes ignorados).

## Componentes

### `Metadata`

**Por que existe / qual problema resolve**

- Servir como **único** formato oficial de metadados em um ecossistema com mais de 20 projetos. A decisão de mantê-lo em um arquivo sem dependências (não importa nada de `flext_core`) evita ciclos de import e garante que qualquer módulo – até os utilitários mais básicos – possa usá-lo sem restrições.
- Estabelece um contrato mínimo para rastreabilidade (quem criou/modificou, quando, tags e atributos adicionais). Sem isso cada projeto passou a criar dicionários diferentes, dificultando auditoria e integrações cruzadas.

**Como funciona / detalhes técnicos**

- `BaseModel` com `model_config = ConfigDict(frozen=True, extra="forbid")`, garantindo imutabilidade e impedindo campos inesperados.
- Campos principais:
  - `created_by` / `modified_by`: identificadores do serviço/usuário responsável.
  - `created_at` / `modified_at`: timestamps UTC usando apenas `datetime.now(UTC)` (stdlib), tornando o módulo neutro.
  - `tags`: lista de rótulos para filtros rápidos (ex.: `[{"audit"}, {"api"}]`).
  - `attributes`: dicionário de pares chave-valor (JSON-serializáveis) usado para anexar qualquer informação específica do domínio.
- Como é imutável (frozen), qualquer “atualização” deve ser feita via `.model_copy(update={...})`, garantindo histórico controlado e evitando alterações silenciosas durante o processamento.

**Aplicações esperadas**

- **Ponto de integração** entre camadas: entidades, handlers, resultados e exportações de contexto podem carregar `Metadata` sem medo de dependências ocultas.
- **Auditoria/Logging**: decorators como `@log_operation` e registries de handlers podem receber o mesmo objeto para enriquecer logs com `tags`/`attributes` padronizados.
- **APIs externas**: quando dados trafegam entre projetos (ex.: `flext-target-oracle` -> `flext-core`), o uso do modelo evita a necessidade de converter estruturas proprietárias.

**Adoções atuais**

- `flext-core`: `examples/14_flext_handlers_complete.py`, `src/flext_core/container.py`, `decorators.py`, `dispatcher.py`, `handlers.py`, `registry.py`.
- `flext-ldif`: `src/flext_ldif/_models/domain.py`, `_utilities/metadata.py`, `api.py`.
- `flext-target-oracle`: `src/flext_target_oracle/target_commands.py`.

**Benefícios tangíveis**

- **Consistência**: todos os pipelines que aderem ao modelo conseguem consumir/exportar metadata imediatamente, sem escrever adaptadores.
- **Observabilidade/Auditoria**: facilita construir dashboards e consultas (ex.: “quais operações foram modificadas pelo serviço X?”) porque os campos são previsíveis.
- **Resiliência contra ciclos de import**: por não depender de `FlextUtilities` ou `FlextResult`, pode ser importado inclusive em utilitários de baixo nível, mantendo a hierarquia de dependências organizada.

**Oportunidades / decisões**

- **Migração de dicts legacy**: targets/taps menores ainda usam dicionários anônimos. Migrar para `Metadata` habilita validação automática e padroniza auditação.
- **Expansão por helpers externos**: se surgirem necessidades como `merge`, `diff` ou enriquecimento automático, criar funções em módulos separados para manter `metadata.py` minimalista (zero dependências) e evitar acoplamento.
- **Integração com ferramentas de conformidade**: incentivar squads de observabilidade/compliance a exigir `Metadata` em qualquer log/evento crítico, pois já está presente em boa parte da stack.
