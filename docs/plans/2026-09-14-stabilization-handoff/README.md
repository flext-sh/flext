# FLEXT 0.12.0 — handoff de estabilização em andamento

Documento de transferência autorizado, preparado em 2026-09-14 após o encerramento da rodada de testes às 23:25:33 UTC. Não é tracker substituto: a execução permanece em `flext-itpd1.1`, no épico `flext-itpd1`. Estabilização não concluída.

## 1. Estado vigente e próxima ação

**Beads central, verificado em 2026-09-15:** executar sempre por
`direnv exec . gc bd <comando> --rig flext`. A consulta
`show flext-itpd1.1 --json` retornou exit 0 no checkout principal e na lane,
com resposta do store do rig `flext`. Essa prova é histórica: o override local
do principal foi posteriormente retirado, e a referência correspondente da lane
também foi removida. Não repetir endpoints em configurações da lane.
Não executar `bd init`: ausência de configuração local não autoriza criar banco.
O diretório `.beads` de identidade não equivale a um banco local; preservar essa
identidade e o banco central. Nenhuma remoção de banco foi necessária nesta correção.

**Última revalidação:** consultas via direnv/Gas City nos dois checkouts retornaram
exit 1 com `Dolt server unreachable at 127.0.0.1:14499`, `connection refused` e
`gc.endpoint_origin=inherited_city`. A resolução é central, mas o serviço estava
indisponível nessa prova. `gc status` retornou exit 0 com estado parcial: controlador
ativo, cidade não suspensa, rig flext suspenso e erro de acesso ao Dolt. Não confundir
exit 0 do status parcial com saúde do banco. A última tentativa de atualizar o épico
não ocorreu; repetir quando o owner estiver disponível, sem banco substituto.

O `make check` 16946 alcançou 23/32 e continua ativo. Falhas ordinárias de tipagem
do contrato Result permanecem; a rodada não comprova o candidato corrigido.
Os patches externos S2 e instalação sem lock aguardam composição e revisão final.
No segundo, o scaffold parcial revelou dependência indevida de manifestos ainda
ausentes: o provisionamento deve consumir os manifestos reais após inicializar
submódulos. Não congelar grupos em testes nem inventar manifestos para passar gates.

**Atualização do operador, 2026-09-15 00:35–00:36 UTC:** absorver os tips atuais do GitHub nos 32 projetos
 e publicar o resultado nas branches de integração; retirar `uv.lock`, `mise.lock` e o modo `APPLY`
 de produtores, consumidores, templates, testes e orientações vigentes. Não basta retirar rastreamento Git:
 setup ainda cria lock e consumidores ainda o exigem. Locks de journal/coordenação permanecem fora dessa retirada.
 A recomendação anterior de manter fixtures do modo aposentado está superada. A execução segue na bead,
 sem promover WIP como validação ou integração.

O pedido vigente é estabilizar operacionalmente e integrar os **32 projetos** (raiz e 31 membros) por PR com **merge commit** em `0.12.0-dev`, propagar o código integrado ao checkout principal, provar runtime e fechar as beads com evidência. Publicação de WIP preserva trabalho; não comprova pouso, aprovação de gates ou runtime.

O operador reiterou às **23:07 UTC** o uso de `gh pr merge --merge --admin`. Registrar essa autorização administrativa como tal, sem apresentá-la como aprovação independente satisfeita. Ela não converte checks vermelhos em verdes nem dispensa as demais provas exigidas para integração e fechamento.

**Exclusão específica:** os custom checks do flext-infra pertencem ao outro responsável e podem permanecer vermelhos. Não alterar, desligar ou enfraquecer esses checks para produzir aprovação artificial. Essa exclusão não abrange Ruff, Pyrefly, Pyright, Mypy, testes, geração, provisionamento, processos ou runtime. Um teste do infra não é automaticamente um custom check excluído: suas falhas precisam de diagnóstico causal.

As duas execuções consecutivas de **`make gen` 17490 e 69562 encerraram com exit 0**.
A segunda informou zero efeitos lazy-init em 220,21 s e completou as verificações de receipts e conformidade dos 32.
O **`make check` 16946 está em andamento**: raiz concluída com falha por markdown (duas linhas longas já corrigidas,
ainda sem nova prova) e 200 findings codemod custom; lint, segurança, Pyright, Pyrefly e Mypy passaram na raiz.
Isso não valida os outros 31. Não iniciar outro Make em paralelo na lane; aguardar a rodada, corrigir os owners
ordinários e revalidar o candidato. A rodada de testes anterior não valida os patches posteriores.
A correção documental posterior em Target Oracle deve ser considerada na próxima prova de geração.

Não recomeçar pela absorção de `206c02ee1d`: essa base já foi incorporada na lane. Antes de publicar ou pousar, buscar as bases atuais dos 32 e absorver somente divergências realmente novas por `merge --no-ff`, preservando ambos os históricos.

### Atualização das tips de integração

A busca das 32 bases em 2026-09-15 identificou o novo tip CLI `b6db6cec9`
(correção de notificação de término de processo), absorvido e publicado por merge
`3058c420`. Nova busca identificou o tip infra `b82eefa3e` (merge externo do PR #732),
absorvido por `ec9813edd` com ancestralidade base → HEAD exit 0.
Os conflitos ficaram em dois testes: contrato CI combina comandos renderizados com
etapas derivadas do catálogo; conform adota os helpers e módulos de teste reorganizados
na integração, que já preservam a remoção dos campos aposentados.
Isso atualiza a base da lane; não comprova pouso dos PRs #240/#731.

A exigência reiterada às 01:00 UTC é trabalhar sobre a tip de integração atual em todos
os projetos: buscar novamente antes de aplicar os patches preparados e incorporar
avanços por merge no-ff. Às 01:09 UTC, o operador reiterou runtime como autoridade:
provar o comportamento pelo consumidor canônico antes de alinhar testes e declarar
sucesso. Os patches externos de S2 e instalação sem lock ainda não foram aplicados;
precisam adaptação ao merge infra mais recente e revisão antes da geração/setup.

### Workspace e coordenação

- Lane existente: `~/flext/.claude/worktrees/bugfix+stabilize-0.12.0`.
- Raiz e infra: `bugfix/stabilize-0.12.0`.
- Demais membros: `bugfix/absorb-checkout-20260914`.
- Checkout principal: `~/flext`; cooperar com seu estado atual antes da propagação.
- Cursor: `flext-itpd1.1`; integração relacionada: `flext-yirgp`.
- Não criar clones/worktrees, não apagar journal lock e não iniciar outro Make durante a geração.
- Preservar todo WIP e resolver fix-forward. Sem reset, restore, checkout destrutivo, stash, clean, rebase, force-push ou no-verify.

### Evidências encerradas

| Operação | Evidência e limite |
| --- | --- |
| Absorção da base na raiz | `origin/0.12.0-dev` recém-buscado em `206c02ee1d`, incorporado por `04c4d724e84203588dccd2ede473d384c49780bc`; prova base → HEAD retornou 0 naquele candidato. Isso comprova absorção, não pouso. |
| Absorção no infra | `1a7c784a6ae6be9d6d9125942220d83b8e85e485` incorporado na lane, ancestralidade para HEAD exit 0; não comprova merge de #731 em dev. |
| `make setup` 61068 | Exit 0; 285 pacotes resolvidos, ldap3 instalado em 2.10.2rc4. |
| `make gen` 22544 | Exit 0, 32/32; três efeitos lazy-init nos pacotes LDIF `_oid`, `_oud`, `_rfc`. Não houve segunda execução comprovada sobre aquele mesmo candidato. |
| `make test` 25454 | Concluído às 23:25:33 UTC, **exit 2**, `total=32 completed=32 passed=25 failed=7`. |
| `make fmt` 3139 | Exit 0, 32/32; formatação do candidato, sem comprovação funcional. |
| `make gen` 17490 | Exit 0; 32 repositórios renderizados, lazy-init com zero efeitos em 333,32 s e verificações de ponto fixo/receipts concluídas. |
| `make gen` 69562 | Exit 0; lazy-init com zero efeitos em 220,21 s, receipts e conformidade dos 32 concluídos. |

Os sete membros com falha na rodada 25454 foram **API, core, infra, quality, tap-oracle-wms, target-oracle e target-oracle-wms**. O despachante completou os 32 projetos; isso não significa que todas as suites internas terminaram. Infra retornou **erro 241** antes de completar sua suite. Seus dois testes de release marcados FAILED não deixaram traceback final nem JUnit da execução interrompida; causa ainda desconhecida.

Resultados de referência dessa rodada: raiz 5 passed; API 2 failed/72 passed; auth 162 passed; CLI 1263 passed; core 6 failed/2655 passed; DB Oracle 541 passed/6 skipped; DBT LDAP 44 passed; DBT LDIF 84 passed; DBT Oracle 69 skipped, nenhum teste executado; DBT Oracle WMS 26 passed; gRPC 350 passed. **PASS com skips não comprova runtime omitido**, especialmente quando falha de provisionamento foi convertida em skip.

Os relatórios nativos em `.reports/workspace/test/` e `.reports/workspace/check/` são mutáveis e devem ser associados à invocação e ao candidato correspondente. Não atribuir seus resultados automaticamente ao HEAD atual.

### Patches aplicados depois dos respectivos testes, ainda não validados

- API: dois testes substituíram `is_str` inexistente pelo contrato `is_=str`.
- Core: executor dos exemplos passou a `u.Cli.run_raw`, preservando assertions e timeout. O owner coleta processos e drena pipes; a troca ainda não comprova eliminação dos timeouts ou do processo Git deixado por outra rota.
- Core: protocolo `Result[T]` deixou de declarar covariância falsa; `ResultView` permanece covariante. Teste público de `flow_through` verifica atribuições a `p.Result[int]` e comportamento, sem exigir tipo concreto exato.
- Flext-tests: removido somente o ramo RootModel inalcançável em `to_normalized_value`; docstring esclarece que `to_payload` já desembrulha RootModel. Alias original preservado; não foi criada nova API para justificar código morto.
- Quality `9d2c0b27`: corrigida a entrada do validador.
- DBT Oracle `7c259091`: retirada fixture autouse Docker sem consumidor nos testes de modelos; nenhum teste removido. Isso não substitui cobertura Oracle que efetivamente executa SQL.
- Infra `de3c7811a`: teste de checkout lê comandos reais de `jobs.ci.steps[].run` no YAML, usa configuração CI e verifica chmod antes de setup/gen/check; não congela rótulos descritivos.
- Tap Oracle WMS `30f9154a`: marcador alinhado à categoria canônica integration.
- Target Oracle WMS `97586e3d`: produtores de mensagens Singer usam os modelos públicos; a chamada inválida de helper foi corrigida e os contratos de scripts foram separados dos módulos de suporte, sem remover testes.
- DB Oracle `0bd29b64`: três testes locais deixaram de exigir conexão artificial; os três casos SQL/DDL/timing foram preservados.
- Oracle WMS `7e73e1fe`: entrada de modelo passou por `model_validate`, preservando o caso inválido.
- Target LDAP `f0cb6ac`: falha de startup agora falha no teste; configuração vem do manager, não de um campo inexistente no ContainerInfo.
- Publicados como WIP, ainda sem validação: pré-validação de credencial SMTP e ajustes de tipos em Quality, refinamento de fixture de modelo em Web, factories da união Singer e herança das exceções em Target Oracle. Não atribuir resultados anteriores a essas mudanças.
- Configuração canônica do infra registra o marcador Oracle consumido pelos testes; a geração projetou essa alteração nos 32 pyprojects. Não foi desligado strict-markers.

RootModel e BaseModel são classes irmãs, mas esse fato isolado não justificava ampliar `NormalizationInput`. A leitura dos consumidores mostrou que todos desembrulham RootModel antes de normalizar. A proposta de alias genérico e testes de TypeAdapter foi retirada por fix-forward; o reparo final elimina o ramo morto e preserva a entrada existente.

### Publicação não é integração

O checkpoint da raiz **`a0d0bd81e8`** publicou o handoff e os gitlinks dos quatro membros daquele lote. Entre os checkpoints publicados estão API `f34cfb5c`, core `ae3e0b07f`, infra `e6c58b412` e LDIF `c42accd5`. Infra publicou depois `de3c7811a` por push FF, de `e6c58b412`, com `git diff --check`, commit escopado e push retornando 0.

Esses hashes são **checkpoints WIP publicados**, não uma lista de SHAs integrados em dev. Os patches de fundação foram publicados no checkpoint abaixo e ainda aguardam validação do candidato correspondente. Não fechar a bead nem alegar pouso por causa desses pushes.

PRs de referência: [raiz #240](https://github.com/flext-sh/flext/pull/240), [infra #731](https://github.com/flext-sh/flext-infra/pull/731), [core #474](https://github.com/flext-sh/flext-core/pull/474), [tests #110](https://github.com/flext-sh/flext-tests/pull/110), [API #99](https://github.com/flext-sh/flext-api/pull/99). Conferir estado/checks/head atuais antes do pouso; o documento não transforma estado histórico de Draft/OPEN/CLEAN em consulta atual.

### Checkpoint dos membros em 2026-09-15 UTC

Os 31 membros publicaram os deltas revisados por commits WIP e push FF. O snapshot
[candidate-publication-20260915.json](candidate-publication-20260915.json) registra HEAD,
branch, upstream e referência de publicação. As 31 referências `origin/<branch da lane>`
coincidem com os HEADs capturados; os upstreams configurados apontam à integração e não
comprovam publicação da lane. O snapshot inclui core dirty pelo teste de regressão iniciado
após o checkpoint; não afirmar limpeza do candidato atual.

Core `e09753be2`, tests `53c3f8f`, infra `895db98f7`, Quality `ce8b5c571`, Web `e7223adf0`
e Target Oracle `a26ae5e12` preservam os reparos descritos acima. A documentação de herança
Target Oracle foi alinhada ao owner. Os demais membros publicaram o marker Oracle gerado e
formatação pertinente. Esses são SHAs de branches de trabalho, não SHAs de merge.

O check atual da API terminou com exit 2 e 14 erros Mypy de conformidade entre
`FlextResult[T]` e `p.Result[T]`, concentrados em JsonValue; causa sob investigação no core.
Auth terminou com falhas custom (silent-failure, runtime-census, namespace), Mypy passou.
O restante da frota continua em execução; nenhuma contagem final ou integração foi obtida.

### Endereços dos 32 PRs de estabilização

Esta tabela é navegação, não atestado de merge ou consulta atual de checks.

| Repositório | PR |
| --- | --- |
| flext | [#240](https://github.com/flext-sh/flext/pull/240) |
| flext-api | [#99](https://github.com/flext-sh/flext-api/pull/99) |
| flext-auth | [#100](https://github.com/flext-sh/flext-auth/pull/100) |
| flext-cli | [#168](https://github.com/flext-sh/flext-cli/pull/168) |
| flext-core | [#474](https://github.com/flext-sh/flext-core/pull/474) |
| flext-db-oracle | [#101](https://github.com/flext-sh/flext-db-oracle/pull/101) |
| flext-dbt-ldap | [#101](https://github.com/flext-sh/flext-dbt-ldap/pull/101) |
| flext-dbt-ldif | [#110](https://github.com/flext-sh/flext-dbt-ldif/pull/110) |
| flext-dbt-oracle | [#101](https://github.com/flext-sh/flext-dbt-oracle/pull/101) |
| flext-dbt-oracle-wms | [#101](https://github.com/flext-sh/flext-dbt-oracle-wms/pull/101) |
| flext-grpc | [#96](https://github.com/flext-sh/flext-grpc/pull/96) |
| flext-infra | [#731](https://github.com/flext-sh/flext-infra/pull/731) |
| flext-ldap | [#114](https://github.com/flext-sh/flext-ldap/pull/114) |
| flext-ldif | [#110](https://github.com/flext-sh/flext-ldif/pull/110) |
| flext-meltano | [#113](https://github.com/flext-sh/flext-meltano/pull/113) |
| flext-observability | [#109](https://github.com/flext-sh/flext-observability/pull/109) |
| flext-oracle-oic | [#100](https://github.com/flext-sh/flext-oracle-oic/pull/100) |
| flext-oracle-wms | [#97](https://github.com/flext-sh/flext-oracle-wms/pull/97) |
| flext-plugin | [#99](https://github.com/flext-sh/flext-plugin/pull/99) |
| flext-quality | [#170](https://github.com/flext-sh/flext-quality/pull/170) |
| flext-tap-ldap | [#99](https://github.com/flext-sh/flext-tap-ldap/pull/99) |
| flext-tap-ldif | [#102](https://github.com/flext-sh/flext-tap-ldif/pull/102) |
| flext-tap-oracle | [#94](https://github.com/flext-sh/flext-tap-oracle/pull/94) |
| flext-tap-oracle-oic | [#97](https://github.com/flext-sh/flext-tap-oracle-oic/pull/97) |
| flext-tap-oracle-wms | [#100](https://github.com/flext-sh/flext-tap-oracle-wms/pull/100) |
| flext-target-ldap | [#100](https://github.com/flext-sh/flext-target-ldap/pull/100) |
| flext-target-ldif | [#103](https://github.com/flext-sh/flext-target-ldif/pull/103) |
| flext-target-oracle | [#105](https://github.com/flext-sh/flext-target-oracle/pull/105) |
| flext-target-oracle-oic | [#100](https://github.com/flext-sh/flext-target-oracle-oic/pull/100) |
| flext-target-oracle-wms | [#101](https://github.com/flext-sh/flext-target-oracle-wms/pull/101) |
| flext-tests | [#110](https://github.com/flext-sh/flext-tests/pull/110) |
| flext-web | [#92](https://github.com/flext-sh/flext-web/pull/92) |

As revisões independentes dos deltas de core/tests/Target Oracle, Quality/Web/Target LDAP e infra/Target WMS terminaram sem achados de código bloqueantes, condicionadas aos gates atuais. A revisão identificou documentação de herança em Target Oracle a alinhar. Nenhuma revisão afirmou sucesso funcional ou aprovação de CI.

## 2. Falhas operacionais e reparos causais

### Core

As três falhas de exemplos foram timeouts de 10 segundos em `process.communicate()`, não divergências comprovadas de goldens. O caso de decorator ValueError falhou com avisos de recursos não coletados, coerentes com subprocessos deixados pelos exemplos interrompidos; os outros parâmetros passaram. Não alterar o decorator sem prova de defeito nele.

O teste agregado de arquitetura excedeu o limite durante `git status` via GitPython; o teste seguinte recebeu aviso de subprocesso ainda vivo. Isso não demonstra findings custom ou campos inválidos de violações. A correção do executor dos exemplos não valida automaticamente a rota Git. Não elevar limites, excluir testes ou mudar goldens para esconder o problema. Otimização exige perfil causal.

### Oracle e provisionamento

Startup Compose retornou 125 e fixtures converteram falhas em skips. Inspeção histórica encontrou Compose instalado pelo mise sem diretório padrão de plugins Docker; isso permanece hipótese até prova do comando canônico com stderr. Corrigir o owner do provisionamento e propagar a primeira falha, sem instalar plugin manual fora da geração nem converter falhas em sucesso.

Os três testes DB Oracle que realmente executam SQL/DDL/timing continuam exigindo provisionamento real. A retirada de fixture sem consumidor em DBT Oracle não autoriza remover infraestrutura de testes que a utilizam. Suites inteiramente puladas não cumprem o aceite operacional.

### Infra

Distinguir defeitos do produto de findings custom excluídos. O teste de checkout tinha expectativa obsoleta `gen check (blocking)`; o gerador já emitia ponto fixo por make gen e verificação de limpeza. O reparo passou a observar comandos, preservando o contrato atual.

As duas falhas de `release/protocol_tests.py` permanecem sem causa determinada pela execução interrompida. Não inferir timeout, problema de Git ou defeito do protocolo sem traceback. Recuperar evidência na próxima rodada canônica.

### Ferramentas padrão

Ruff, Pyrefly, Pyright, Mypy e testes precisam de rodada no candidato estabilizado. O Mypy histórico foi interrompido com teto de 6144 MiB; isso não identifica sozinho a causa nem autoriza execução ilimitada. Não reutilizar contagens históricas como confirmação de erros ainda presentes ou corrigidos.

## 3. Ordem de execução até o fechamento

1. Recolher a rodada `make check` 16946 até os 32, classificar as falhas ordinárias e corrigir seus owners. As gerações 17490/69562 já terminaram com exit 0; não repetir por memória. Alterações posteriores precisam da validação correspondente.
2. Executar os verbos canônicos necessários na raiz da lane: setup quando o ambiente/dependências mudarem, gen, fix, fmt, check e test. Coordenar mutações para que a prova final corresponda ao candidato publicado. Sem `PROJECT=`, `WHAT=`, novos seletores ou gates avulsos.
3. Corrigir falhas padrão e ambiente pelos owners, preservando a exclusão dos custom checks. Registrar o que executou, o que falhou e o que não teve runtime. Cada correção invalida somente as provas que dependem do trecho alterado; a rodada final deve cobrir os 32 declarados.
4. Adjudicar contribuições úteis ainda pendentes, especialmente [raiz #242](https://github.com/flext-sh/flext/pull/242); infra #732 já chegou pela nova base e suas incompatibilidades com o pedido atual devem ser corrigidas fix-forward, contra o HEAD atual. Incorporar por fix-forward/no-ff somente semântica útil, sem restaurar políticas retiradas ou assumir implementação de custom checks excluídos. Mudanças incorporadas retornam ao ciclo de geração/validação.
5. Publicar por push FF os candidatos dos membros, resolver checks/conversas e registrar a autorização administrativa de 23:07. Integrar os PRs por merge commit em `0.12.0-dev`; não promover um head WIP como se validado. Usar a autorização administrativa sem declarar uma aprovação independente inexistente; manter a revisão independente e as demais condições vigentes.
6. Registrar SHA de merge por membro, buscar a base novamente e provar candidato → base. Atualizar gitlinks da raiz para os SHAs pousados; validar e integrar a raiz por PR com merge commit. Completar esse procedimento nos 32 projetos, não somente raiz e infra.
7. Propagar ao principal por fast-forward onde aplicável. Reconciliar cooperativamente qualquer WIP/divergência por fix-forward; nunca mover submódulos cegamente sobre trabalho local. Rodar setup/gen e validação do código realmente instalado. Provar runtime dos contratos exercidos, sem confundir importação, unidade ou skips com serviços reais.
8. Atualizar e fechar beads somente com estado registrado, histórico integrado, comando/cwd/exit/saída decisiva e código atual concordantes. Registrar SHAs de merge e runtime. Retirar PRs/branches/worktrees somente com autorização aplicável e ancestralidade contra base recém-buscada. Não promover para main.
9. Manter S0–S8 reconciliado na bead. Cada fatia restante precisa de ciclo completo; nenhuma fatia é concluída por este handoff.

## 4. Plano, Beads e fontes

Fontes canônicas de planejamento a reler integralmente ao retomar:

- `~/.claude/plans/happy-puzzling-flask.md` — plano completo, reconciliado com o operador mais recente.
- `~/.claude/plans/happy-puzzling-flask-handoff.md` — handoff anterior, evidência histórica.
- `~/.claude/plans/ai-hub-envrc-agent-hooks.md` — coordenação externa e fronteiras ai-hub.
- `docs/plans/2026-09-14-stabilization-handoff/README.md` — handoff vigente, publicado como checkpoint; não comprova integração.

Tracker central, sempre carregado por direnv:

```bash
direnv exec . gc bd show flext-itpd1 flext-itpd1.1 --rig flext --json
direnv exec . gc bd list --parent flext-itpd1 --limit 100 --rig flext --json
```

A resolução atual pelo Gas City identifica o servidor herdado da cidade. Não repetir
exports manuais nem inicializar armazenamento embedded. A consulta pelo Gas City e
a atualização de `flext-itpd1.1` tiveram exit 0 anteriormente; as consultas mais
recentes falharam por conexão recusada no servidor central, conforme seção 1.
O acesso direto anterior com exports é evidência histórica, superada pela exigência
explícita de carregamento automático via direnv e Gas City.

Filhas de referência para consultar, sem fechar por lembrança: `flext-ocxtt` (gates), `flext-2j4lr`
(desempenho/replanejamento), `flext-za816`/`flext-2h0un` (ponto fixo), `flext-bdmdg` (render spec), `flext-rlb47`
(raízes Python), `flext-xldlq` (journal), `flext-7ua33`/`flext-gajwa` (scratch), `flext-x1x1q` (deptry), `flext-c4k44`
(testes), `flext-rwls4` (fronteira pública). As beads `flext-c1vvr`, `flext-k7vvp`, `flext-6x6jr`, `flext-xobfw` incluem
enforcers/codemods/gates: reconciliar responsabilidade excluída antes de agir. A contagem histórica de 19 filhas não é
censo atual.

`land_members.sh` e `roll_members.sh`, no diretório externo dos planos, são apoio histórico; ler suas pré-condições antes de usar. Não assumir branches, limpeza ou base exata a partir desses scripts.

### Auditoria histórica imutável

A auditoria anterior permanece no [commit `81873eeff9`](https://github.com/flext-sh/flext/blob/81873eeff9/docs/plans/2026-09-14-stabilization-handoff/README.md). Seus estados, ordens de pausa, ausência de autorização administrativa, resultados parciais e comandos futuros descrevem aquele instante; **não são instruções vigentes**.

Anexos históricos mantidos no pacote, sem reescrevê-los como tracker:

- `plan-source.md` — snapshot do plano anotado.
- `previous-handoff-source.md` — snapshot do handoff anterior.
- `ai-hub-package-source.md` — snapshot de coordenação externa.
- `state-before-checkpoint.json` — estado datado dos 32 e principal.
- `prs-at-audit.json` — PRs e heads observados na auditoria.
- `beads-at-audit.json` — beads consultadas naquela captura.
- `member-publication.json` — comandos e resultados dos pushes daquele lote.

Todos ficam em `docs/plans/2026-09-14-stabilization-handoff/`. A revisão deste documento confirmou a existência dos sete anexos; não refez consultas remotas ou provas de runtime.

## 5. Crítica da execução e correções de método

1. **Preservação excedeu entrega.** A absorção ampla foi autorizada, mas WIP e Draft PRs acumularam sem pouso. Publicação não substitui incremento entregue; limitar cada rodada a um candidato que possa ser validado e integrado.
2. **O cursor perdeu prioridade.** #240 e propagação eram a primeira obrigação. As ampliações legítimas não revogaram esse objetivo; a bead deve manter uma próxima ação concreta, sem reiniciar inventários já encerrados.
3. **A direção de ancestralidade importa.** Base ancestral da lane demonstra absorção; candidato ancestral da base recém-buscada demonstra pouso. Não usar a primeira prova para afirmar a segunda.
4. **As provas envelheceram.** Commits, merges e geração posteriores alteraram candidatos. Cada relatório precisa de escopo temporal; fix/fmt ou PASS parcial não comprovam check/test atual.
5. **A janela de geração precisa ser exclusiva.** Mutações durante gen impedem prova confiável de ponto fixo. Cooperar com todos os atores e preservar seu trabalho; concorrência não transfere culpa nem justifica abandono.
6. **Desempenho foi investigado parcialmente.** CPU ativa e progresso não eliminam gargalo. Não declarar travamento resolvido sem perfil, observabilidade e prova no caminho que demorava.
7. **Comparações históricas induziram erros.** ConfigDict pertence a m; RootModel ser irmão de BaseModel não criava consumidor para nova API. Ler produtor, consumidor e HEAD atual antes de modificar contrato ou classificar contribuição.
8. **Delegação não encerra o ciclo.** Lotes terminaram preservação/revisão, mas gates, pouso e runtime ficaram pendentes. O coordenador deve manter esses passos ativos até o aceite dos 32.
9. **A comunicação terminou cedo demais.** Relatar agentes lançados ou patches prontos não cumpre a execução completa. Handoffs autorizados transferem contexto; não encerram estabilização.
10. **Tracker e documentação precisam acompanhar realidade.** Evitar múltiplos blocos vigentes conflitantes. Bead guarda cursor; handoff explica evidência e retoma a próxima ação real.
11. **Autorização administrativa deve ser descrita precisamente.** A ausência histórica de autorização foi superada às 23:07. Registrar o uso autorizado sem chamar check vermelho de verde ou aprovação independente de satisfeita.
12. **Exclusão de custom checks é delimitada.** Não assumir todo infra como excluído; também não exigir reparo dos custom checks antes de pouso contra o aceite atual. Classificar falhas pelo owner e contrato.

## 6. Reconciliação de S0–S8

| Fatia | Estado e limite de conclusão |
| --- | --- |
| S0/S1/A4/A5 | Entregas históricas #727 e membros registradas. Revalidar preservação após absorções; não repetir merges já incorporados como trabalho novo. |
| S2 | Cutover completo ainda não comprovado. O inventário histórico encontrou gascity_enabled, WorkspaceBeadsServerSpec, beads_enabled, ledger_id e BeadsWorkspaceEnvironmentSpec. Conferir owner atual antes de remover; template parcial `95baa0c0d` não é entrega completa. |
| S2b | Inventariar runtime externo retirado e preservar CI/actions próprios autorizados. Não exigir zero global de `.github`, GithubWorkflow ou GITHUB_* quando a CI continua parte do produto. |
| S3 | Quatro regiões AGENTS ainda sem implementação/validação completa comprovada nesta sessão. Preservar conteúdo externo conforme fronteira autorizada. |
| S4 | Custom gates têm outro responsável e estão excluídos desta implementação. Registrar resultados reais e coordenação, sem duplicar trabalho nem chamá-los de verdes. |
| S5 | Bootstrap perdeu argumento vazio da retirada de APPLY. Restante precisa respeitar execução estrita: não adotar plano antigo que converte erro em warning ou pula repositório. |
| S6 | Geração/locks/checkpoints avançaram; candidato final ainda precisa gates, integração e runtime nos 32. |
| S7 | Gitlinks de merge, documentação, scripts/pacote e coordenação externa devem corresponder ao código integrado. Não publicar repin como se etapa operacional ausente estivesse concluída. |
| S8 | Fechamento depende de gates atuais, merge dos 32, propagação, runtime, adjudicação de PRs e quatro fontes nas beads. Retirada exige prova recente e preservação. |

Cada fatia implementada muda seu próprio candidato e deve ser validada e pousada por PR com merge commit. S8 consolida essas provas; não estreia os testes. Enviar o SHA da S2 completa à sessão ai-hub somente após pouso e dentro da autorização de comunicação existente.

Outras reconciliações: retirar integralmente o modo APPLY e migrar suas fixtures conforme a atualização de 00:35–00:36 UTC; não restaurar validação de gitlink no runtime apenas porque o pouso exige prova Git; preservar regiões externas byte a byte quando essa é a fronteira autorizada; não assumir que revisão histórica de branch autoriza sua aposentadoria.

## 7. Contribuições históricas e adjudicação pendente

Infra #723/#724/#730 foram incorporados na lane; não confundir isso com pouso de #731 em dev. #729 foi mergeado externamente pelo operador como `a312043b5`, head `155c52a34`, às 19:18 UTC, com checks então falhando; não é fechamento verde desta sessão.

A adjudicação histórica identificou conteúdo já presente ou obsoleto em release/checkpoint dos quatro DBTs, budgets retirados e resets de endpoints. ConfigDict WMS já estava no owner correto. DBT Oracle #97 propunha caminhos inexistentes; não copiar código quebrado por mera afinidade de família. LDIF #102 e Target Oracle #102 exigem respeitar owners atuais; decisões históricas não dispensam comparação com os heads atuais.

Raiz #242 ainda precisa adjudicação das contribuições úteis. Infra #732 foi integrado externamente por `b82eefa3e` e absorvido na lane por `ec9813edd`; sua descrição abaixo é o diagnóstico anterior, não uma instrução de deixá-lo pendente. O primeiro trouxe automação com pré-condições incompletas; o segundo mistura melhorias de documentação/relatórios com mudanças que podem conflitar com execução incondicional e verificação atômica já adotadas. Conferir hunks atuais e cooperar
antes de absorver. PRs de dependências/actions devem mudar o SSOT e regenerar, nunca somente projeções.

Ao encerrar, registrar o que foi incorporado, já estava presente ou foi superado, com prova. Nenhuma dessas classificações autoriza apagar branches sem fetch recente e ancestralidade. O estado atual continua ativo e incompleto até que integração e runtime dos 32 sejam comprovados.
