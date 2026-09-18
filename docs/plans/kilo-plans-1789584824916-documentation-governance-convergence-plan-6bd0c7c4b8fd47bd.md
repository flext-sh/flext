# Plano v2: convergência documental, governança e projeções

## Resultado obrigatório

Convergir `~/agents`, AI Hub e a frota FLEXT para um único estado documental e de
governança verificável, sem confundir source, projeção, histórico, plano, memória ou
evidência runtime.

O trabalho só termina quando:

- cada regra, skill, command, ADR, configuração e documento corrente possui um owner
  gravável único;
- AI Hub projeta o bundle integrado de `~/agents` sem cópias manuais ou destinos
  quebrados;
- `make gen` e a coleta de planos atingem fixed point sem writers concorrentes;
- artifacts `incoming/<digest>/` permanecem byte-immutáveis e fora dos fixers;
- `make docs` passa nos 33 scopes, sem warnings, findings ou exemplos inválidos;
- cada membro alterado é integrado antes do gitlink correspondente;
- Gas City contém estado, bloqueios, comandos, SHAs, PRs e runtime; memórias Kilo apenas
  espelham decisões estáveis e corrigidas.

Este plano substitui como roteiro documental o plano
`1789584987558-documentation-governance-convergence-plan.md`. Os planos `1789582669805`
e `1789564109553` permanecem autoridade para a modernização fleet-wide que não pertence
à campanha documental.

## Estado verificado após a primeira execução

### Autoridade global

- `~/agents` foi integrado e publicado em `origin/dev` no SHA `d079b548`.
- Bead `ag-q76u` foi fechado com evidência de:
  - `GovernanceBundle`: 132 skills, 19 commands, 66 agents, 90 rules e 244 resources
    exatos;
  - `make runtime`, `make docs`, `make audit`, `make check`, `make test-full`;
  - 57 testes full executados, zero warnings/skips;
  - `make gen` duas vezes, com 10 hooks, 1 plugin e 2 pointers em fixed point.
- O limite FLEXT de 200 LOC agora pertence somente a
  `rules/architecture/internal-clean-architecture.md`; a cópia de 1000 LOC no sweep foi
  removida.
- `living-documentation`, fan-out, Beads continuity e landing foram reduzidos a deltas
  sobre owners canônicos.

### AI Hub

- Bead ativo: `aihub-agfq7`.
- Owner de projeção atual: `config/agents.yaml` + serviços de governance projection;
  `config/projections.json` e `agentsctl sync` são referências históricas, não a
  superfície runtime atual.
- `make setup` e `make gen ×2` passaram sobre o bundle integrado.
- `make docs` ainda não possui snapshot estável: writers concorrentes alteraram o
  projector durante planning/audit. Nenhum deploy/runtime pode ocorrer antes de
  docs/check/test verdes no mesmo SHA.

### FLEXT

- Bead ativo: `flext-5fxu6.4.28`, filho de `flext-5fxu6.4`.
- `make setup` passou com 286 packages.
- `make gen` chegou ao fixed point depois da remoção do contrato morto de dependency
  cooldown e de preflights contra writers concorrentes.
- `config/plan-collection.yaml` associa `.kilo/plans` a `docs/plans`.
- O boundary YAML de `PlanCollectionConfig` foi corrigido para parse tipado via
  `u.validate_value(..., strict=False)`.
- O docs fixer alterou indevidamente revisions autenticadas; `incoming` passou a
  integrar `DOC_EXCLUDED_DIRS`, com teste público de discovery.
- O artifact já corrompido foi restaurado pelos bytes versionados; manifesto e revisions
  não foram apagados.
- `make docs` gera relatórios úteis, mas está vermelho em 33 scopes. O root report atual
  registra 321 arquivos, 121 issues e 100% de docstrings públicas.
- Os findings dominantes são projeções compartilhadas, links cross-project, codeblocks
  pseudo-Python, símbolos aposentados, machine paths e páginas que duplicam API gerada.
- As sessões temáticas de `python_codeblock` e arquitetura falharam no mesmo provider
  Nvidia antes de executar. Não retomar esses contextos: o coordenador assume a classe
  ou cria, no máximo, uma sessão nova por arquivo/report slice, sem herdar o contexto
  falho.
- A sessão temática de links/catalog terminou sem result/evidência. Ela não produziu
  contribuição nem reserva de path; a Onda B permanece sob o coordenador e começa no
  report canônico mais recente.
- A segunda tentativa temática de arquitetura também falhou no provider antes de
  qualquer tool call. O retry budget dessa classe está esgotado: placeholder,
  machine-path e stale-symbol nos sete paths já inventariados serão corrigidos
  diretamente pelo coordenador, sem novo fan-out.
- A primeira fatia de guide snippets falhou no AtlasCloud antes de executar. Durante a
  Onda C ela admite uma única substituição por arquivo (`using-flext-core`,
  `using-flext-tests`, deletion audit), sempre em sessão nova; qualquer nova falha
  devolve o arquivo ao coordenador.
- A pesquisa read-only de seis reports concluiu que seis signatures compartilhadas
  explicam grande parte do vermelho em root, CLI, gRPC, Meltano, Observability e Tap
  Oracle WMS. Tratar cada signature no owner e regenerar; não abrir uma correção por
  ocorrência projetada.

### Memórias e tracker

- Gas City está ativo e é o tracker autoritativo; a memória que o declarava desativado
  foi corrigida.
- `make mod` existe; verbo `ast` e `config/rules/ast/` continuam target aceito, não
  runtime atual. A memória prematura foi corrigida.
- Beads e `bd remember` são a memória durável primária. Kilo não substitui dependências,
  status ou receipts.

## Autoridades e cadeia de projeção

| Camada                | Owner gravável                                                      | Projeções/consumidores                                               | Verbo de prova                                                                     |
| --------------------- | ------------------------------------------------------------------- | -------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Governança global     | `~/agents/{rules,skills,commands,agents,config}`                    | `GovernanceBundle`, hooks e pointers do bundle                       | `make runtime`, `make check`, `make test-full`, `make gen ×2`                      |
| Adaptação/provider    | `~/ai-hub/config/agents.yaml` + projector/services                  | capsules `AGENTS.md`, hooks, `.agents`, `.github`, homes de provider | `make setup`, `make gen ×2`, `make docs`, `make check`, `make test`, `make deploy` |
| FLEXT tooling         | `flext-infra/config/{codegen,tooling}.yaml`, templates e generators | `pyproject.toml`, Make/CI, lazy exports, project metadata            | root `make gen ×2`, `make check`, `make test`                                      |
| Guides compartilhados | root `docs/guides` e docs generator                                 | guides nos membros                                                   | root `make docs`                                                                   |
| Plan collection       | `config/plan-collection.yaml` + collector                           | `docs/plans`, manifest, receipts, incoming revisions                 | root `make docs` duas vezes                                                        |
| Execução              | Gas City Beads                                                      | status, blockers, receipts e closure                                 | `direnv exec <repo> bd show ... --json`                                            |
| Memória               | `bd remember`; Kilo secundário                                      | decisões/constraints estáveis                                        | busca/readback das chaves                                                          |

Nenhum output da coluna “Projeções/consumidores” é editado manualmente para obter green.
Se um arquivo não possui owner demonstrável, ele é classificado e fica fora da mutação
até o owner ser eleito.

## Protocolo de barreira de writers

### Antes de qualquer generator, fixer ou formatter

1. Encerrar fan-out da fatia pelo mecanismo normal e coletar todos os resultados.
2. Reabrir cada arquivo tocado e adjudicar contribuições; relatório de subagente nunca
   vale como evidência sozinho.
3. Registrar no Bead a matriz:
   `repo → paths → writer/fatia → owner → próximo gate → estado`.
4. Confirmar zero assignments sobrepostos e zero processos owners do lock canônico. Um
   arquivo lock sem processo owner não é removido.
5. Executar preflight live de branch, HEAD, upstream, status e diff por repo.
6. Somente o coordenador inicia `gen`, `docs`, `fix`, `fmt` ou deploy.

### Se o snapshot mudar durante planning

1. Preservar a contribuição e reler o arquivo/diff.
2. Registrar o path e a causa no Bead.
3. Fazer um único retry após novo preflight.
4. Segunda ocorrência na mesma classe: parar o verbo, restaurar a barreira de writers e
   não repetir até identificar o writer.

### Locks

- Timeout vira evidência no Bead.
- Usar `lsof`/owner publicado para identificar o processo.
- Encerrar somente o processo que mantém o lock quando a lei do journal exigir.
- Nunca `rm` do lock, nunca apagar journal, nunca iniciar store alternativo.

## Política de subagentes

Cada assignment declara exatamente um modo:

- `research-only`: produz owner map ou classificação, zero writes;
- `edit-only`: paths disjuntos e findings já materializados em report;
- `owner-and-test`: altera um único owner e seu teste estreito.

Regras operacionais:

1. Não autorizar commit, gitlink, geração ou Beads ao worker temático.
2. Não atribuir “todos os docs” ou uma árvore ampla. Dividir por issue type e diretório
   owner.
3. Primeira falha de provider/context: criar uma nova fatia menor uma vez.
4. Segunda falha equivalente: coordenador assume; sem loop de retries.
5. Toda resposta é verificada no source e no diff. Correções que introduzam `PROJECT=`,
   `WHAT=`, `APPLY`, ferramenta direta ou paths inexistentes são rejeitadas, mesmo
   quando bem-intencionadas.
6. O coordenador integra apenas depois de todos os workers daquela barreira terminarem.
7. Uma falha ocorrida antes de qualquer tool call não produz contribuição nem reserva de
   path; registrar o task id como evidência e devolver a fatia ao coordenador.

## Fases de execução

### Fase 0 — Congelar e reancorar os três repositórios

1. Atualizar `flext-5fxu6.4.28`, `aihub-agfq7` e o sucessor/closure de `ag-q76u` com
   HEAD/upstream/dirty paths/primeiro red.
2. Parar geração enquanto houver subagente ou processo escrevendo nos mesmos paths.
3. Reconciliar commits concorrentes já publicados por contribuição real; nunca
   resetar/rebasear ou restaurar árvore inteira.
4. Rebuild CRG somente depois da barreira; registrar built-at SHA.

**GO:** owners e writers de todo path dirty conhecidos; locks sem owner ativo.

### Fase 1 — Fechar runtime global e projeção AI Hub

1. Revalidar `~/agents` apenas se HEAD divergir de `d079b548`.
2. No AI Hub, absorver o bundle integrado pelo pin declarado e repetir `make setup` e
   `make gen ×2`.
3. Corrigir no owner AI Hub toda documentação que ainda apresenta
   `config/projections.json` ou `agentsctl sync` como runtime atual; planos históricos
   recebem rótulo, não rewrite semântico.
4. Provar que `config/agents.yaml` materializa apenas o bundle global aplicável e o
   delta local `internal_flext` (`flext-context-routing`/`flext-law`).
5. Validar targets e modos de symlinks/arquivos dos providers; nenhum link quebrado ou
   destino cacheado.
6. Executar `make docs`, `make check`, `make test` no mesmo SHA.
7. Somente verde: `make deploy`, confirmar processo/runtime e identidade do SHA.
8. Executar nova geração/sync e exigir zero writes.

**STOP:** qualquer writer concorrente, docs red, target quebrado ou runtime que não
identifique o bundle integrado.

### Fase 2 — Endurecer os owners do pipeline documental FLEXT

1. Manter `incoming` fora de todo fix/audit mutável e cobrir o comportamento em teste
   público.
2. Garantir que canonical curado pode receber guidance histórico, enquanto
   `incoming/<digest>` e `provenance.json` são imutáveis.
3. Fazer o collector publicar uma nova revision quando source muda, sem alterar
   revisions antigas e sem apagar receipts.
4. Corrigir comentários de provenance gerados para nomear
   `<workspace-root>/docs/guides/...`, não o próprio output.
5. Melhorar o reporter antes de nova campanha se um gate informar apenas contagem: todo
   finding precisa de file/type/severity/message em
   `.reports/docs/{audit-report.md,audit-summary.json}`.
6. Provar plan collection + fixer + audit duas vezes, byte-identical.

**GO:** teste estreito verde e artifacts históricos idênticos ao Git/manifest.

### Fase 3 — Corrigir por classe, não por arquivo

Usar o report mais recente como fila efêmera. O Bead guarda somente a classe e o owner;
o report guarda ocorrências.

#### Onda A — Owners compartilhados e generated ownership

- corrigir template/guide root que se projeta em vários membros;
- remover páginas manuais que duplicam API gerada ou convertê-las em overview sem
  inventário de símbolos;
- regenerar todos os consumidores uma vez.

Baseline de signatures já materializadas:

| Signature                                    | Owner candidato a provar                                         | Consumidores observados                            | Corte esperado                                                   |
| -------------------------------------------- | ---------------------------------------------------------------- | -------------------------------------------------- | ---------------------------------------------------------------- |
| `undefined-name u` em exemplos               | `docs/guides/using-flext-core.md`                                | root, CLI, Meltano, Observability, Tap Oracle WMS  | importar a facade pública correta uma vez; regenerar guides      |
| `undefined-name p` e comparação float direta | `docs/guides/using-flext-{core,tests}.md`                        | mesmos cinco scopes                                | imports por bloco + assertion pública sem igualdade float frágil |
| links `../../flext-*/README.md`              | generator de `docs/projects` derivado de `config/workspace.yaml` | todos os scopes amostrados                         | emitir URL HTTPS branch-matched no generator                     |
| manual API duplicates generated ownership    | template/owner de `docs/api-reference.md` e `docs/api/*.md`      | root, gRPC, Meltano, Observability, Tap Oracle WMS | overview delega ao generated API; zero inventário duplicado      |
| output de Semgrep/Sonar marcado como Python  | templates compartilhados de security triage                      | CLI, Meltano, Tap Oracle WMS                       | fences `text` para output; Python apenas para código executável  |
| `/home/...` em guidance/report               | owner de ADR/ecosystem/security report                           | root e CLI                                         | path sem host (`${HOME}`, repo URL ou descrição histórica)       |

“Owner candidato” não autoriza edição imediata: localizar template/generator e confirmar
que a mesma fonte produz as ocorrências antes de escrever.

#### Onda B — Links e catálogo de projetos

- links internos permanecem relativos dentro do mesmo repo;
- referências a outro repo usam URL HTTPS obtida de `config/workspace.yaml`;
- plan collector reescreve/responde por links de addenda; nunca editar `incoming`;
- corrigir links quebrados no source, não em projeções repetidas.

#### Onda C — Exemplos executáveis

- código Python precisa importar e executar pela facade pública;
- pseudocódigo usa fence `text`, nunca fence Python inválido;
- exemplos de config-owned facts derivam do owner, não congelam valores;
- somente verbos Make selector-free aparecem como comandos FLEXT atuais.
- cada fence é validado isoladamente pelo audit report, mas corrigido no menor source
  compartilhado; não adicionar imports num bloco diferente daquele que os executa.

#### Onda D — Arquitetura e linguagem corrente

- remover machine-local paths;
- substituir placeholders por owner/roadmap real;
- símbolos aposentados saem do guidance corrente;
- relatórios CRG e handoffs antigos são rotulados como evidência histórica, não
  reescritos como runtime atual.

#### Onda E — Resíduo por domínio

Executar somente depois de A–D regeneradas:

1. foundation/control plane;
2. platform;
3. LDAP/Oracle/domain;
4. taps/targets/dbt.

Cada domínio recebe paths disjuntos, report atualizado e um único owner/test.

**Gate por onda:** barreira de writers → `make docs` → report novo → zero findings da
classe corrente. Não iniciar a onda seguinte com o owner anterior vermelho.

### Fase 4 — ADRs, skills, commands e memórias

1. ADRs declaram explicitamente `CURRENT IMPLEMENTATION`, `ACCEPTED TARGET` ou
   `PROPOSED`; status e tracking precisam existir no Gas City.
2. `ADR-014/017` não podem afirmar `ast` disponível antes do runtime.
3. Skills globais permanecem em `~/agents`; o projeto contém somente deltas declarados
   em `.agents/provider.toml`.
4. Commands descrevem uma facade pública existente; sem aliases históricos.
5. Rules mantêm uma única norma por assunto. Companion rules só acrescentam delta e
   apontam ao owner.
6. Atualizar `bd remember` primeiro; corrigir Kilo para o mesmo conteúdo e eliminar
   contradições antigas.

**GO:** bundle global e projeção local carregam sem phantom refs, duplicação ou paths
inexistentes.

### Fase 5 — Fixed points e gates FLEXT

Com todos os writers encerrados, no root:

```bash
make setup
make gen
make gen
make docs
make docs
make check
make test
make build
```

`mod/fix/fmt` entram apenas se os findings exigirem mudança estrutural/formatada; se
executados, rodam pelo root, são repetidos para fixed point e invalidam os gates
posteriores.

Condições:

- segunda geração e segunda docs não escrevem;
- docs reporta zero em todos os 33 scopes;
- warnings, skips não autorizados, zero collection, timeout ou output oculto são
  vermelhos;
- qualquer edição posterior repete os gates sobrepostos.

### Fase 6 — Landing por repositório

Ordem obrigatória:

1. `~/agents` source bundle;
2. AI Hub pin/projector/runtime;
3. `flext-infra` owner de generator/docs;
4. cada membro com mudança hand-written ou projection commitável;
5. superprojeto e gitlinks.

Para cada repo:

1. diff/ancestry/gates do repo;
2. commit explícito somente dos paths aceitos;
3. push da lane e PR;
4. review/checks;
5. merge `--no-ff` na integração;
6. rerun afetado no merge SHA;
7. runtime quando o repo o possui;
8. somente então atualizar consumidor/gitlink.

Nenhum commit guarda-chuva avança 31 gitlinks sem os 31 SHAs publicados e integrados.

### Fase 7 — Closeout

1. Atualizar cada Bead com receipts no schema abaixo.
2. `bd lint --json` retorna zero.
3. Fechar somente itens cujo acceptance foi provado; os demais mantêm primeiro red e
   próxima ação exata.
4. `bd remember` registra owners e decisões finais.
5. Kilo recebe apenas correções equivalentes, sem estado transitório de execução.
6. Trees terminam limpos, não ahead e alinhados ao upstream.

## Retry budget e tratamento de falhas

| Falha                                   | Resposta obrigatória                                                                 |
| --------------------------------------- | ------------------------------------------------------------------------------------ |
| Provider/subagente falha uma vez        | Nova sessão menor, sem herdar contexto inflado                                       |
| Segunda falha equivalente               | Coordenador assume; zero retry adicional                                             |
| Snapshot muda durante planning          | Preservar, reler, registrar, um retry após barreira                                  |
| Segunda mudança concorrente             | Parar e identificar writer; não insistir no gate                                     |
| Lock timeout                            | Registrar, identificar owner, terminar somente owner autorizado; nunca remover lock  |
| Gate só imprime contagem                | Ler report canônico; se inexistente/incompleto, corrigir reporter antes dos findings |
| Artifact `incoming` diverge             | Recuperar bytes autenticados por Git/manifest; corrigir fixer; nunca apagar history  |
| Projeção diverge em vários membros      | Corrigir um owner e regenerar; não editar consumidores                               |
| Subagente introduz selector/tool direto | Rejeitar hunk e corrigir pelo comando canônico                                       |
| Runtime contradiz teste/doc             | Runtime e contrato externo vencem; corrigir owner/test/doc                           |

## Schema mínimo de evidência por Bead

Cada grain registra:

- repo, branch, HEAD e upstream;
- Bead/owner e paths;
- classe do finding;
- source owner e projeções afetadas;
- comando exato, cwd, exit e output decisivo;
- contagens antes/depois do report;
- prova de fixed point quando aplicável;
- commit, push, PR, merge SHA e checks;
- runtime/artifact/config identity;
- primeiro red remanescente e próxima ação.

Sem esses campos não há claim de green, integração ou conclusão.

## Critérios finais de aceite

- `~/agents` source e AI Hub projector/runtime integrados e identificáveis por SHA;
- zero duplicate rule owner, phantom skill/command e provider target quebrado;
- Gas City ativo como único tracker, Beads sem lint e memórias sem contradição;
- collector/fixer preserva `incoming` byte-immutável e plan collection é fixed point;
- `make docs` passa em todos os scopes com reports detalhados e zero issues;
- guidance corrente usa somente interfaces/símbolos/comandos existentes;
- históricos estão rotulados e não dirigem execução atual;
- ADRs distinguem implementação, target e proposta;
- generated outputs apontam ao owner e nunca foram corrigidos à mão;
- `setup/gen/docs/check/test/build` verdes nos SHAs integrados;
- membros publicados antes dos gitlinks; superprojeto limpo e alinhado.

## Fora de escopo

- modernização arquitetural não documental sem finding do gate desta campanha;
- third-party forks;
- reescrita estética de históricos;
- restauração de comandos/paths aposentados;
- bypass, suppression, compatibility shim, baseline de warnings ou store Beads
  alternativo.
