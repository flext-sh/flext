# Plano revisado — modernização runtime-first de `rope-modernize` / `flext-infra`

<!-- TOC START -->
- [Objetivo e critério de término](#objetivo-e-criterio-de-termino)
- [Reancoragem viva — 2026-09-17](#reancoragem-viva-2026-09-17)
- [Adendos de continuidade e proveniência](#adendos-de-continuidade-e-proveniencia)
- [Autocrítica do plano anterior](#autocritica-do-plano-anterior)
- [Posição atual reconciliada após o repasse do Claude](#posicao-atual-reconciliada-apos-o-repasse-do-claude)
  - [O que o Claude efetivamente avançou](#o-que-o-claude-efetivamente-avancou)
  - [O que foi superseded pelo tip atual](#o-que-foi-superseded-pelo-tip-atual)
  - [Estado vivo que substitui os snapshots anteriores](#estado-vivo-que-substitui-os-snapshots-anteriores)
  - [Decisão operacional decorrente](#decisao-operacional-decorrente)
- [Autoridades e invariantes](#autoridades-e-invariantes)
- [Estratégia de execução por fatias](#estrategia-de-execucao-por-fatias)
  - [Fase 0 — Reidratar execução e inventariar contribuição real](#fase-0-reidratar-execucao-e-inventariar-contribuicao-real)
  - [Fase 1 — Desbloquear make setup no owner genérico](#fase-1-desbloquear-make-setup-no-owner-generico)
  - [Fase 2 — Estabilizar make mod e make gen como produtos](#fase-2-estabilizar-make-mod-e-make-gen-como-produtos)
  - [Fase 3 — Modernizar arquitetura somente nos módulos alcançados pelos gates](#fase-3-modernizar-arquitetura-somente-nos-modulos-alcancados-pelos-gates)
  - [Fase 4 — Ciclo corretivo canônico](#fase-4-ciclo-corretivo-canonico)
  - [Fase 5 — Revalidar e sanear testes da frota](#fase-5-revalidar-e-sanear-testes-da-frota)
  - [Fase 6 — Check completo e correção de todos os gates](#fase-6-check-completo-e-correcao-de-todos-os-gates)
  - [Fase 7 — Integração e propagação incremental](#fase-7-integracao-e-propagacao-incremental)
- [Coordenação de agentes](#coordenacao-de-agentes)
- [Evidência obrigatória por fatia](#evidencia-obrigatoria-por-fatia)
- [Stop conditions reais](#stop-conditions-reais)
- [Primeiro incremento executável](#primeiro-incremento-executavel)
<!-- TOC END -->

## Objetivo e critério de término

Entregar a modernização como produto funcionando, não como análise: partir dos Beads autoritativos do Gas City, adotar o tip atual de cada branch de integração, corrigir as causas raiz que impedem o ciclo canônico e propagar incrementos pequenos até a integração.

## Reancoragem viva — 2026-09-17

- O Bead ativo para a reconciliação documental e de governança é
  `flext-3rld2`, reivindicado no Gas City por
  `direnv exec ~/flext-worktrees/rope-modernize bd ...`.
- O superprojeto permanece em `89fc3096335b53d81cdc52afe7cc8c785514bdb2` e
  o CRG desse SHA está atual (`head_matches_build=true`).
- O gitlink registrado de `flext-infra` é `96c52f1d6e671f5403282e7764b29d29cc061c15`;
  o checkout efetivo está em `d83ccc6160c1862e7443cf87e5fce8a6855ce559`
  com WIP concorrente. Nenhuma conclusão baseada em `469b26b4e0` valida esse
  checkout atual.
- O escopo agora inclui alinhar `~/agents` como autoridade global, melhorar seu
  pipeline de projeção e manter no projeto apenas deltas FLEXT branch-matched.
- ADRs e docs devem distinguir explicitamente implementação corrente, decisão
  aceita ainda não implementada e proposta. Projeções nunca são editadas
  diretamente.

Um incremento só termina quando, no checkout integrado e depois de qualquer regeneração:

1. o comportamento público afetado funciona em runtime;
2. `make setup`, `make gen`, `make mod`, `make fix`, `make fmt`, `make check`, `make test` e `make build` concluem com exit 0 na ordem canônica;
3. `make gen`, `make mod`, `make fix` e `make fmt` atingem fixed point: a segunda execução consecutiva é no-op;
4. não há warnings, skips indevidos, execução vazia, timeout ou falha normalizada no escopo;
5. commits dos membros foram publicados antes dos gitlinks do superprojeto;
6. a branch foi integrada por PR/merge `--no-ff`, os gates foram repetidos no SHA integrado e o runtime consumidor foi revalidado;
7. Beads contém comando, cwd, exit, saída decisiva, SHA/PR e estado final.

## Adendos de continuidade e proveniência

O contexto detalhado das sessões paradas e da cooperação com outros agentes
fica em `.kilo/plans/addenda/`:

- `addenda/claude-chronology-2026-09-16.md` — horários, comandos e avanços Claude;
- `addenda/current-state-conflicts-2026-09-16.md` — claims aceitos/rejeitados e conflitos entre trees;
- `addenda/cross-plan-coordination-2026-09-16.md` — planos concorrentes, owners e critérios de aceite.
- `addenda/beads-lanes-prs-2026-09-16.md` — tracker, SHAs e artefatos de landing a reler.

Os adendos são contexto datado; Gas City Beads e runtime permanecem autoridade.

## Autocrítica do plano anterior

O plano anterior fica substituído por este porque:

- tratou CRG como prova de runtime; CRG orienta alcance, mas Make e o consumidor real decidem;
- usou um snapshot parcial do grafo (368 nós/89 arquivos/5 testes). O grafo atual do superprojeto, já recursivo, contém 34.587 nós, 236.576 arestas e 4.701 arquivos no SHA `89fc3096335b53d81cdc52afe7cc8c785514bdb2`; o grafo isolado de `flext-infra` contém 9.242 nós, 82.383 arestas e 988 arquivos no SHA `469b26b4e0b336e78548fef1fdcfca347f9c5d53`;
- reduziu a auditoria de testes aos cinco testes do root e ignorou a frota;
- presumiu lacunas de cobertura a partir de `TESTED_BY=0`, embora dispatch por MRO, atributos e wrappers possa escapar da análise estática;
- não começou pelo Bead e tip de integração autoritativos;
- não definiu como recuperar `make setup`, o primeiro gate bloqueante;
- propôs comandos diretos de `pytest`, Ruff, Pyrefly e ast-grep, contrariando a superfície canônica Make;
- não separou absorção fix-forward do tip para a lane e propagação `--no-ff` da lane para integração;
- não definiu inventário e adjudicação de lanes/PRs/worktrees abandonados;
- não amarrou redução de LOC e reorganização de facades a comportamento público e gates por fatias.

## Posição atual reconciliada após o repasse do Claude

### O que o Claude efetivamente avançou

- Investigou a regressão introduzida por uma conversão mecânica de `try/except c.ValidationError` para `u.validate_value`: bindings usados depois do guard haviam sido removidos em `modernizer.py`, release metadata e Mise state.
- Confirmou por leitura que os nomes ausentes haviam sido restaurados naquele snapshot e corrigiu a ordenação de imports de `services/cli_routes_refactor.py`.
- Investigou `SLF001` em `_conform_gitignore.py` e `BLE001` em `runtime_census.py`.
- Atualizou/reconstruiu o CRG para incluir submódulos e produziu um plano fleet-wide mais crítico em `.kilo/plans/1789582669805-flext-infra-ruff-codemod-repair.md`.
- Não executou `make setup/gen/mod/fix/fmt/check/test`, não atualizou Beads e não aterrissou PR durante esse repasse; portanto, nenhuma alegação de runtime green daquele snapshot é aceita.

### O que foi superseded pelo tip atual

- No snapshot reconciliado de 2026-09-16, o tip de `flext-infra` era
  `469b26b4e0` e o CRG isolado não detectava diferenças contra
  `origin/0.12.0-dev`. Esse snapshot é histórico: o checkout atual está em
  `d83ccc616`, diverge do gitlink `96c52f1d6` e contém WIP.
- `modernizer.py` atualmente voltou à validação direta por adapters/modelos dentro de `try/except c.ValidationError`; os bindings `payload`, `canonical_dev`, `environments` e `runtime` existem. A conversão anterior para `u.validate_value` não é estado atual e não deve ser ressuscitada por memória.
- `_release_artifact_metadata.py` mantém `rewritten` corretamente e valida a sequência diretamente; não há F821 no source lido.
- `_mise_artifacts_state.py` retorna `result_type.ok(model_validate(...))` dentro do `try` e compensa no `except`; o RET503 relatado no snapshot antigo não existe no source atual.
- A suppression adicionada pelo Claude para `_conform_gitignore.py` não está presente no `pyproject.toml` atual. `_conform_gitignore.py` agora contém a implementação/owner completo das seções, não um wrapper de uma linha. Não remover ou mover sem CRG e runtime atuais.
- Os `except Exception as exc` de `runtime_census.py` continuam documentados como contrato de agregação de violações. Eles permanecem **pendentes de prova pelo CLI/gate público**; comentário não equivale a autorização para warning Ruff.
- O CRG atual encontra 19 testes ligados a `FlextInfraPyprojectModernizer`; a afirmação antiga de cobertura zero estava errada.

### Estado vivo que substitui os snapshots anteriores

- Superprojeto: SHA `89fc3096335b53d81cdc52afe7cc8c785514bdb2`, grafo atual e `head_matches_build=true` em 2026-09-17.
- Diferença do super contra `origin/0.12.0-dev`: 39 paths, principalmente gitlinks e governança; o CRG do super não atribui funções/flows a gitlinks, então risco 0.00 não é prova de ausência de impacto nos membros.
- `flext-infra`: o snapshot CRG em `469b26b4e0` permanece evidência histórica;
  o gitlink atual é `96c52f1d6`, o checkout está em `d83ccc616` e precisa de
  novo build de grafo depois da adjudicação do WIP.
- Dívida estrutural atual de `flext-infra`: pelo menos 60 nós com 200+ linhas. Maiores owners incluem `_models/config.py` (3.343), `codegen/conform.py` (2.990), `_utilities/_rope/source.py` (1.123), `codegen/codegen_transaction.py` (1.022) e `_utilities/pyproject_conform.py` (1.012).
- Relatórios históricos de `make check/test`, contagens de runtime census e duplicação permanecem somente evidência de investigação. Nenhum deles valida os SHAs atuais.

### Decisão operacional decorrente

O próximo incremento não é “terminar Ruff”. É reler o Bead Gas City autoritativo no rig, confirmar tips atuais e executar o ciclo desde `make setup` no tree atual. Somente a primeira falha reproduzida define o owner seguinte. Reparos do Claude já absorvidos ficam como contexto histórico, não como fila ativa.

O checkout principal contém um WIP concorrente em
`flext-infra/codegen/_conform/execute.py`: `_lazy_analysis` filtrado é criado,
mas não propagado de forma consistente ao journal/fixed-point e chega a ser
referenciado fora de escopo. Esse defeito não existe na lane em
`flext-infra@469b26b4e0` no snapshot histórico. Antes de absorver o próximo tip,
revalidar no checkout atual e preservar apenas a
intenção válida (um owner por path entre conform e lazy-init) e rejeitar a
implementação quebrada; a resolução deve usar um único
`CodegenPhaseAnalysis` filtrado em append, journal e validação.

## Autoridades e invariantes

- **Estado de execução:** somente Gas City Beads, sempre por `direnv exec <rig> bd ...`; não criar tracker paralelo.
- **Código base:** tip remoto atual da branch de integração declarada por cada repositório, normalmente `0.12.0-dev`; nunca usar SHA antigo do plano como base implícita.
- **Absorção:** integrar o tip de integração na lane por merge cooperativo, sem rebase/force-push/reset/restore/stash/revert.
- **Propagação:** lane validada entra na integração por PR e merge commit `--no-ff`; depois repetir runtime e gates no checkout integrado.
- **Concorrência:** mudanças desconhecidas ou paralelas são entrada a adotar por fix-forward. Antes de tocar arquivo mutável, reler e atribuir intent/Bead.
- **Geração:** alterar `config/*.yaml`, templates, schemas ou gerador; nunca editar projeções geradas (`__init__.py`, Makefiles, seções managed) manualmente.
- **Ferramentas:** usar CRG antes de varreduras textuais; usar `make mod` como única superfície para ast-grep/Rope/LSP; usar RTK em comandos de shell sem esconder traceback, exit ou saída causal; não usar `head`/`tail`/pipes como evidência.
- **Testes:** runtime e contrato externo definem comportamento. Testes somente confirmam interfaces públicas; remover testes sem valor real, reescrever testes úteis que dependam de mocks/fakes/privados/hardcodes e conservar testes de comportamento reais.

## Estratégia de execução por fatias

Cada fatia possui um Bead, uma lane dedicada, um conjunto pequeno de arquivos, prova de runtime e PR próprio. Não iniciar a próxima fatia enquanto a atual não estiver integrada ou registrada como bloqueada por causa externa exata.

### Fase 0 — Reidratar execução e inventariar contribuição real

1. No rig correto, executar `direnv exec <repo> bd prime`, `bd show` do épico/Bead ativo e `bd ready --json`; confirmar conexão real ao Gas City com uma leitura do Bead, não apenas metadata.
2. Registrar objetivo, exclusões, branch de integração, stop condition e gates no Bead. Reusar hierarquia existente; não criar nova engine nem novo épico duplicado.
3. Inventariar superprojeto, 31 membros, worktrees, branches, PRs e mudanças sujas. Para cada lane abandonada, comparar contribuição real contra o tip atual e os Beads; adotar somente hunks ainda necessários.
4. Atualizar CRG recursivamente no SHA atual e registrar built-at SHA. Rodar `detect_changes`, `affected_flows`, `impact_radius`, hubs, bridges, large functions, knowledge gaps e `tests_for` para os arquivos candidatos.
5. Classificar cada alteração em: adotar agora, já absorvida, obsoleta, conflito material ou fora do tema. Conflito material é o único caso que exige decisão do operador.
6. Criar/selecionar lane dedicada a partir do tip de integração atual. A lane absorve avanços posteriores por merge cooperativo; não rebasear.

**Saída:** mapa por repo com tip, Bead, lane/PR, paths alterados, contribuição real, risco CRG e primeira ação.

### Fase 1 — Desbloquear `make setup` no owner genérico

1. Executar `rtk make setup` na raiz da lane e capturar o primeiro erro completo. Nenhum diagnóstico direto por `uv`, Mise ou script ad hoc substitui o verbo.
2. Mapear o erro ao owner em `flext-infra/config/codegen.yaml`, `config/tooling.yaml`, templates sob `src/flext_infra/templates/project/base/`, schemas/modelos e código do gerador.
3. Verificar explicitamente:
   - proibição completa de `uv.lock`, `mise.lock`, `.mise.lock` e seus leitores/geradores;
   - tabelas `[tool.uv.workspace]` indevidas em membros anexados, especialmente `flext-api`;
   - seleção da versão mais recente declarada de Mise/uv sem pin ou downgrade paralelo;
   - validação de gitlinks sem checkout/reset destrutivo;
   - ambiente Gas City/direnv derivado de `.envrc`, metadata do rig e publicação runtime da cidade, sem host/port hardcoded;
   - ausência de fallback, catch ou shim para erro de provisioning.
4. Corrigir o owner uma vez; projetar por `make gen`, nunca editar os 32 consumidores manualmente.
5. Repetir `rtk make setup` até exit 0 sem warnings. Uma nova falha vira o próximo Bead/fatia somente se for independente; caso contrário permanece no mesmo Bead.

**Aceite:** workspace e membros provisionados pelo mesmo Make owner; nenhum lockfile proibido criado; `pip check`/equivalente do próprio setup verde.

### Fase 2 — Estabilizar `make mod` e `make gen` como produtos

1. Antes de cada rewire estrutural, usar CRG para callers/callees/importers/tests/flows e registrar alcance.
2. Codificar regra reutilizável no SSOT de `make mod`; não executar ast-grep bruto. A mesma invocação deve compor ast-grep, Rope e pyright-langserver e falhar em ambiguidade.
3. Corrigir locks/journal no owner. Timeout de journal é defeito rastreado; identificar o dono do lock e finalizar causalmente, nunca apagar lock preventivamente.
4. Executar `rtk make mod` e revisar cada transformação aplicada. Rejeitar corrupção de string/docstring, símbolos ambíguos e mapeamentos manuais.
5. Executar `rtk make gen` duas vezes. A segunda execução deve ser byte-identical/no-op; qualquer divergência é P0 no gerador e recebe teste de convergência.
6. Confirmar que geração não recria locks proibidos, compat aliases, `_part` ou rotas antigas.

### Fase 3 — Modernizar arquitetura somente nos módulos alcançados pelos gates

Ordem obrigatória dentro de cada módulo:

1. **Centralizar antes de dividir:** mover constantes para `c`, aliases para `t`, dependências para `p`, dados Pydantic v2 para `m`, utilidades puras/reutilizáveis para `u`, inputs externos para `settings` e regras derivadas para `config`.
2. **Eliminar duplicação:** executar gate `duplication`/jscpd pela superfície Make, eleger um owner e remover cópias no mesmo corte.
3. **Aplicar shape FLEXT:**
   - pacote privado `_<module>/`;
   - classes internas pequenas, uma família Single Class Nested por módulo;
   - `base.py` importa as classes internas e compõe a classe base completa por MRO;
   - `<module>.py`/`api.py` é facade fina que importa de `._<module>` e compõe MRO, sem comportamento adicional;
   - `cli.py` somente transporta input e propaga a primeira falha;
   - `__init__.py` somente gerado por `make gen`;
   - nenhum `_part`, facade paralela, alias de compatibilidade ou old+new.
4. **Reduzir LOC:** módulos tocados devem terminar <=200 LOC lógicos ou ser divididos na mesma fatia; a fatia deve ser net-negative em LOC customizado, salvo justificativa objetiva registrada no Bead.
5. **Preservar contrato:** comportamento público antes/depois é comparado por runtime. Não criar teste de método privado ou de layout interno para autorizar o refactor.

**Prioridade inicial orientada por risco, a confirmar no tip antes da edição:**

- owner de setup/workspace e pyproject modernizer;
- `deps/modernizer.py` e mixins associados;
- transação/codegen e journal de Mise (`codegen/_mise_artifacts_state.py` e owners);
- módulos >200 LOC identificados por `find_large_functions`, começando pelos alcançados pelo primeiro gate vermelho;
- duplicação entre utilitários Rope/análise apenas se CRG provar sobreposição e consumidores.

Não fazer uma reorganização cosmética da frota inteira antes de `make setup` verde.

### Fase 4 — Ciclo corretivo canônico

Após cada fatia funcional:

1. executar runtime público mínimo afetado;
2. `rtk make gen` duas vezes;
3. `rtk make fix` duas vezes;
4. `rtk make fmt` duas vezes;
5. `rtk make check`;
6. `rtk make test`;
7. executar o consumidor real/integrado aplicável.

Tratar warnings, cosméticos, findings antigos e falhas pré-existentes dentro do blast radius como trabalho adotado, nunca como desculpa. Não aumentar timeout, excluir paths, adicionar ignore/noqa/type-ignore ou enfraquecer regra para obter verde.

### Fase 5 — Revalidar e sanear testes da frota

1. Atualizar CRG com submódulos e obter inventário completo de testes; não inferir frota a partir dos cinco testes do root.
2. Classificar cada candidato por leitura de fonte e runtime:
   - **reter:** interface pública, filesystem/registry/DB/CLI real, configuração derivada do SSOT;
   - **reescrever:** comportamento relevante, mas usa mock/patch/monkeypatch/fake, método privado, estado global ou hardcode de valor configurável;
   - **remover:** testa implementação/layout interno, duplicata contrato já coberto, fixture artificial sem consumidor real ou arquivo histórico/archive.
3. Não classificar apenas por nome ou sintaxe: `mock` em nome/string de teste do próprio validator não é automaticamente mock de SUT; `assert` não é automaticamente inválido quando permitido como idioma pytest. O critério é realidade observável.
4. Substituir valores configuráveis por leitura do mesmo config/settings tipado consumido pela produção ou round-trip gerador/consumidor.
5. Substituir setup local por helpers públicos de `flext-tests`; sem cópias de fixtures.
6. Protocolos de teste só permanecem se houver consumidor runtime real. `tests/infra/protocols.py` deve ser provado via importadores/runtime antes de remoção; CRG sem aresta não basta por causa de lazy exports/MRO.
7. Executar `make test` no membro alterado e depois no workspace. Coleção zero, skip, warning, testmon corrompido ou timeout é vermelho.

### Fase 6 — Check completo e correção de todos os gates

1. Rodar `rtk make check` completo sem selecionar projetos ou gates.
2. Corrigir na ordem causal: falha de execução da ferramenta, namespace/layout/codemod, Pyrefly/Pyright/Mypy, Ruff/markdown/security, LOC/duplication/smells.
3. Para cada finding, mapear owner por CRG, corrigir source/config/template e regenerar; nunca corrigir projeção.
4. Pyright interrompido/timeout é falha do produto: instrumentar o gate canônico e corrigir alcance/performance sem bypass.
5. Repetir ciclo até zero findings e zero warnings.

### Fase 7 — Integração e propagação incremental

1. Antes do push, reler tip remoto e absorver avanços por merge cooperativo.
2. Reexecutar o ciclo completo após o merge; evidência anterior em paths sobrepostos fica inválida.
3. Commit por paths explícitos da fatia; nunca `git add -A`.
4. Push da lane; abrir/atualizar PR; resolver review threads e checks.
5. Merge `--no-ff` na branch de integração. Fix-forward descreve a absorção do tip na lane; `--no-ff` descreve a entrega da lane na integração.
6. No checkout do tip integrado, repetir runtime, `setup/gen/fix/fmt/check/test` e fixed points.
7. Para submódulos: publicar primeiro o commit do membro, validar tip integrado do membro, só então atualizar o gitlink do superprojeto e validar o workspace.
8. Propagar para `ai-hub` e `cosmos-main` apenas quando consumidores do contrato alterado; provar runtime real, não só testes.
9. Atualizar/fechar Beads somente depois da integração e runtime; remover lane/worktree/PR abandonado apenas após inventário mostrar contribuição totalmente absorvida ou obsoleta e registrar essa prova.

## Coordenação de agentes

- Orquestrador mantém Beads, dependências, adjudicação, integração e evidências; não implementa.
- Workers recebem exatamente um Bead/fatia/repo/worktree e o mesmo tip de integração.
- Agentes paralelos dividem por owners não sobrepostos: setup/toolchain, codegen/mod, testes, docs/governança e consumidor runtime.
- Cada worker deve notificar overlaps e adotar mudanças compatíveis. Nenhum worker fecha Bead, faz merge na integração ou descarta trabalho de outro.
- Antes de integrar, uma revisão adversarial independente compara diff, CRG impact, testes e runtime.

## Evidência obrigatória por fatia

Registrar no Bead:

- repo/worktree/branch/base tip e SHA final;
- `git status` e contribuição paralela adotada;
- CRG built-at SHA, changed nodes, flows, callers e testes relevantes;
- comandos Make exatos, cwd, exit e saída decisiva sem truncamento;
- runtime público antes/depois;
- contagem de LOC e duplicação antes/depois;
- primeira e segunda execução de gen/fix/fmt;
- commit, push, PR, merge SHA e rerun no tip integrado;
- blockers reais com owner e próximo comando, nunca promessa de verde.

## Stop conditions reais

Parar e escalar somente quando:

- Gas City Beads não responde a uma leitura real após ativação via direnv;
- duas intenções atuais e comprovadas exigem comportamento incompatível;
- a próxima ação é destrutiva/irreversível ou expandiria além do tema;
- credencial/runtime externo obrigatório está ausente;
- o comando canônico não existe — registrar defeito para criá-lo no owner, sem bypass.

Falha de gate, dirty worktree, divergência, trabalho paralelo, lock em uso, warning ou finding antigo não são stop conditions; são trabalho fix-forward dentro do Bead apropriado.

## Primeiro incremento executável

1. Continuar no Bead Gas City `flext-3rld2`, já reivindicado via `direnv exec`;
   registrar super `89fc309633`, gitlink infra `96c52f1d6` e checkout infra
   `d83ccc616` separadamente.
2. Inventariar diferenças ainda vivas, incluindo gitlinks e WIP concorrente.
   Tratar a microfatia Ruff do Claude como contexto histórico, nunca como WIP a
   reaplicar por memória.
3. Confirmar que os grafos atuais continuam em `head_matches_build=true`; reconstruir apenas após mudança de source/HEAD.
4. Executar `rtk make setup` no tree atual e trabalhar exclusivamente o primeiro erro causal reproduzido. Não assumir que o bloqueador antigo de `flext-api`, Gas City ou lock ainda existe sem nova saída.
5. Se `setup` ficar verde, executar `make gen` x2 e `make mod` x2. Qualquer mudança reinicia o fixed point de `gen`.
6. Executar runtime mínimo, `fix` x2, `fmt` x2, `check` e `test`; registrar a primeira falha atual por owner.
7. Somente após gate atual apontar o próximo módulo, abrir a primeira fatia arquitetural. Entre os candidatos grandes, priorizar o owner alcançado pela falha, nunca o maior arquivo por tamanho isolado.
8. Integrar essa fatia no tip, repetir runtime/gates no SHA integrado e atualizar Beads antes da próxima classe de violação.
