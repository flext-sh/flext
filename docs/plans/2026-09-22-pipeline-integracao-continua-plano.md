# Plano — Concluir o pipeline com integração contínua e prova real

> **Para agentes executores:** execute tarefa a tarefa; etapas usam checkbox. Achados
> completos da auditoria que fundamentam este plano:
> `docs/plans/2026-09-22-pipeline-integracao-continua-achados.md`.

**Meta:** terminar a entrega em incrementos integrados e validados — primeiro
ambiente+integração utilizáveis (raiz+31 membros+consumidores), depois os 4 incrementos
funcionais (credenciais ccs → descoberta/sondagem → ciclo vazio/publicação →
clientes/periódica), fechando com prova real (6 ciclos de 600 s em torno de reinício
controlado).

**Arquitetura:** workspace FLEXT (raiz `0.12.0-dev` + 31 submódulos) reconciliada na
workspace de recuperação `~/flext-worktrees/rope-recovery-20260921`; contrato `.venv`
corrigido no dono (`flext-infra` template+config) e regenerado; pipeline AI Hub
(`/home/marlonsc/ai-hub`, ccs, cliproxy) sob épicos `aihub-6k1` reconciliado com
`flext-itpd1.3`.

**Spec:** mensagem do operador de 2026-09-22 (5 seções) + achados da auditoria.

**Verdade em jogo:** a raiz principal avançou `1e59a9d493→daa51e8822` durante a
auditoria — pode haver outro agente commitando; toda fase re-verifica o tip antes de
agir.

## Constraints globais

- Beads nos bancos canônicos via `direnv exec <repo> bd …`; registro por lote: comando,
  workspace, SHA, exit, resultado decisivo, invalidadores; check ausente/skipped ≠
  aprovação.
- Um responsável por fonte; geração/ambiente/índice Git/publicação serializados por
  workspace; nenhuma edição durante geração/validação da mesma candidata.
- Buscar integração declarada antes de cada lote/rodada final/merge; incorporar avanços
  com `git merge --no-ff` no próximo ponto estável e repetir verificações invalidadas.
- WIP preservado por caminhos explícitos; jamais reset/stash/rebase/force-push/resolução
  integral ours-theirs.
- PRs pequenos por proprietário, título convencional, Draft/WIP sinaliza incompletude;
  promoção exige commit final não-WIP + gates completos + CI executada + revisão
  independente + merge commit.
- Comandos canônicos: `make` na raiz da workspace ativa (nunca uv/ruff/mypy/pytest
  crus); `bd` via direnv; publicar membro antes do gitlink; push fast-forward only.
- Gas City permanece desativado; nenhum clone/worktree/ambiente novo.

## Passo 0 — Registro e trackers

- [ ] 1. Gravar este plano e o MD de achados em `docs/plans/`.
- [ ] 2. Reconciliar Beads: ligar `aihub-6k1` ↔ `flext-itpd1.3` (nota de correlação
     mútua); eliminar dos textos critérios antigos (3 faixas / conclusão após 1 ciclo);
     criar bead para os "192 achados" (reproduzir na fase 1C) e para o marcador do
     cenário de substituição de ambiente.
- [ ] 3. Confirmar Gas City desativado; nenhum clone criado.

## Fase 1 — Incremento 1: ambiente e integração utilizáveis

**1A. Reconciliar a recuperação** (`rope-recovery-20260921`, merge aberto
`MERGE_HEAD=1e59a9d493`, 31 UU gitlinks +
`docs/ways-of-working/worker-lane-contract.md` + 15M/4A staged):

- [ ] 1. Re-verificar tip da raiz principal; absorver avanços com `git merge --no-ff` no
     próximo ponto estável.
- [ ] 2. Para cada um dos 17 membros com merge aberto (auth, dbt-ldap, dbt-ldif,
     dbt-oracle, dbt-oracle-wms, ldap, oracle-oic, plugin, quality, tap-ldap, tap-ldif,
     tap-oracle, target-ldap, target-oracle, target-oracle-oic, tests, web): resolver no
     dono preservando ambos os lados; conflitos em projeções resolvidos reconciliando
     fontes+gerador e produzindo a resolução por `make gen`; WIP sujo (tests 78, plugin
     17, core 16, quality 12) preservado com commits de caminhos explícitos.
- [ ] 3. Provar por membro que o HEAD contém ambos os lados do gitlink
     (`git merge-base --is-ancestor` dos dois SHAs); publicar membro antes de registrar
     gitlink na raiz; concluir o merge da raiz incluindo a resolução do documento
     restante, sem omitir recebidos.
- [ ] 4. Cobertura automatizada do contrato `.venv` (standalone físico; submódulo real
     usa `<workspace>/.venv`; env herdado não redireciona; symlink `.venv`/`.venv/bin`
     inclusive quebrado rejeitado; symlink do executável python permitido; update de
     Python só no ambiente próprio).

**1B. Contrato `.venv` no dono**
(`flext-infra/src/flext_infra/templates/project/base/Makefile.j2` +
`flext-infra/config/codegen.yaml`):

- [ ] 1. Remover o atalho standalone em `REPOSITORY_ROOT` (hoje
     `flext-core/Makefile:120-122` suprime o probe
     `git rev-parse --show-superproject-working-tree` da linha 124): a relação Git REAL
     decide; perfil standalone só quando não há superprojeto.
- [ ] 2. Extinguir o padrão borrowed: remover tolerância (`Makefile:467-493`) e
     `BORROW_RUNTIME_VENV_RECIPE` (`:500-503`); introduzir rejeição `-L` de `.venv` e
     `.venv/bin` antes de qualquer efeito (precedente mise `:253-285`); absorver bead
     `flext-bxo4y`.
- [ ] 3. Regenerar consumidores (`make gen`: 32 Makefiles + ai-hub pelos beads
     `flext-zxwqa`/`2nwjy`/`ts0t9`/`t9fay`); remover documentação que autoriza ambientes
     emprestados.
- [ ] 4. Dar rota canônica executável ao cenário de substituição de ambiente hoje
     excluído por marcador.

**1C. Reparos adotados + ciclo nativo** (re-escopo operador 2026-09-22: "não é objetivo
resolver os problemas de make check gerados por flext-infra, eles precisam ficar warning sem
bloquear o ci"):

- [ ] 1. Validar classificação config/fachadas no Core, composição MRO no infra,
     fixtures (`flext-tests`) e regras estruturais — contra donos e ADRs, não por verde.
- [ ] 2. **Fazer os findings de check gerados pelo flext-infra virarem warning sem bloquear
     CI** (dono: superfície de gates do check/CI em flext-infra + projeção ci.yml via gen) —
     em vez de resolver os ~192 achados. Registrar a contagem no bead `flext-12uxl` como
     contexto do re-escopo, não como obrigação de zerar.
- [ ] 3. Revisar o conjunto de regras ANTES de `make mod` (catálogo completo sem
     seletor), preservar checkpoint, rodar sem escritores concorrentes; efeitos
     inválidos corrigidos no dono; nunca excluir regra/teste para verde.
- [ ] 4. CI AI Hub: resolver PR #854 — regenerar as 3 projeções divergentes no branch
     (`scripts/__init__.py`, `_installed_runtime_parts/__init__.py`,
     `_session_learning/__init__.py`), finalizar commit sem WIP e título convencional,
     reexecutar CI; validar empacotamento determinístico pelo consumidor real; fechar
     runs vermelhos do dev tip (CI `35746445654`, Docs `35746445781`, PR #836
     `35746454609`).
- [ ] 5. Ciclo nativo na recuperação:
     `setup → gen → mod → gen → gen → fix → fmt → check → test → build`
     (+docs/consumidores); provar convergência (`gen`/`fix`/`fmt` repetidos = no-op exit
     0); `check` executa com findings do flext-infra em nível warning (não-bloqueante)
     conforme re-escopo.
- [ ] 6. Suíte completa dentro do orçamento tipado: investigar causa (cf.
     `aihub-kvx0x.6.2`: 1903 testes, 600 s, kill -15; `flext-yjjim`); nunca inflacionar
     limites.

**Gate F1:** raiz+31 membros+consumidores funcionando na versão integrada; merges
`--no-ff`; membros publicados antes dos gitlinks; ciclo nativo verde com prova de
convergência; CI AI Hub verde no PR promovido.

## Fase 2 — Incrementos funcionais (cada um: integração, publicação pelo dono, prova antes do seguinte)

- [ ] **2.1 Credenciais automáticas** (`aihub-6k1.29`): ai-hub executa
      `ccs tokens --api-key-only` via configuração tipada de comandos (sem shell; flag
      existe em `ccs/src/commands/tokens-command.ts:9,76,99`), captura sem registrar
      segredo, distribui pelo mecanismo existente systemd-creds
      (`_host_runtime_parts/credentials.py:37`, `LoadCredentialEncrypted`); uma
      aquisição alimenta todos os consumidores da ativação; falha/saída vazia interrompe
      antes da publicação. Segredo de gerenciamento pelo contrato CCS existente +
      config/env CLIProxy. _Observável:_ ativação/rotação sem export manual;
      ausência/inválida = erro causal.
- [ ] **2.2 Descoberta e sondagem independentes da seleção** (`aihub-6k1.28`; desacoplar
      `model_pipeline/cycle.py:70-119`, segunda leitura `:92`): inventário pelo registro
      vivo com publicação ativa ou vazia; resolução compartilhada inventário+sondagem
      validando modelo, variante, seletor e credencial; aliases normais restritos à
      publicação. _Observável:_ modelo novo aparece; recuperado pode ser sondado;
      sondagem não libera tráfego nem troca rota silenciosamente.
- [ ] **2.3 Ciclo vazio e publicação consistente:** diferenciar inventário vazio válido
      de auth/leitura/schema inválidos; 4 faixas independentes (`models.yaml:18-42`,
      ADR-0023); reler fatos após sondagens; validação CCS; recuperação de interrupções
      pela transação existente sem editar snapshots. _Observável:_ faixas vazias com
      motivo; snapshot/projeção/recibo/estado ativo concordam.
- [ ] **2.4 Clientes e operação periódica:** publicar artefatos integrados, ativar
      serviços, gerar configs dos clientes pelos consumidores canônicos de aliases
      (`model_pipeline/consumer.py`). _Observável:_ clientes usam aliases; atualização
      periódica e reinício preservam operação.

Reutilizar endpoints/formatos existentes; modelos+validadores+docs atualizados juntos;
CCS só sob incompatibilidade comprovada; sem flags de credenciais no CLIProxy.

## Fase 3 — Prova final e encerramento

- [ ] 1. Cobertura automatizada (sem contas/chamadas pagas): primeira publicação, vazia,
     modelo novo, quota recuperada; credencial ausente/inválida/rotacionada; inventário
     malformado, catálogo incompatível, rejeição sem publicação parcial;
     seletor/rota/variante inválida sem encaminhamento alternativo; interrupção
     transacional, segunda geração, reinício; falha pós-início de streaming sem troca de
     candidato; isolamento de workspace (standalone, submódulo real, env herdado
     incorreto).
- [ ] 2. Implantação: artefato/SHA/executável servindo em cada componente; validação com
     consumidores reais ANTES do `make deploy` canônico; chamadas mínimas por
     alias/protocolo (streaming, ferramentas, saída estruturada, raciocínio por faixa);
     consumo confirmado nos clientes configurados (config gerada/chamada direta não
     substitui; cliente que exija operador fica pendente explícito).
- [ ] 3. 3 ciclos completos consecutivos + reinício controlado + 3 ciclos — intervalo
     configurado 600 s (`models.yaml:5-6`) sem encurtar; registrar gerações, SHAs,
     modelos/rotas, elegibilidade, sondagens, chamadas, latências, erros — sem segredos.
- [ ] 4. Revalidar SHAs integrados, concluir PRs/Beads, retirar só recursos de entrega
     com integração comprovada.

**Condição final:** ambiente inteiro verde, 4 faixas utilizáveis, publicação
consistente, clientes comprovados, 6 ciclos observados; falta real de capacidade mantém
entrega incompleta com evidência específica — nunca sucesso parcial.
