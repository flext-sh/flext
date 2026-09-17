# Runbook de estabilização — checkpoint 0.12.0

<!-- TOC START -->
- [(a) Ciclo canônico](#a-ciclo-canonico)
- [(b) Contrato beads central](#b-contrato-beads-central)
- [(c) Integração](#c-integracao)
- [(d) Extermínios vigentes](#d-exterminios-vigentes)
<!-- TOC END -->

> **Status (2026-09-17):** a estabilidade global deste checkpoint ainda não foi
> comprovada. O ciclo abaixo é o contrato de validação, não um recibo verde.
> `flext-itpd1.3` coordena a recuperação sob `flext-itpd1`; os workstreams irmãos
> `flext-itpd1.2` (documentação) e `flext-itpd1.4` (maquinaria Make) mantêm seus
> escopos. Beads detém o estado vivo; este documento mantém o contrato versionado.
> Planos locais são contexto de sessão: sua utilização aprovada não autoriza
> cópia ou publicação, nem seleção automática pelo nome mais recente.

## (a) Ciclo canônico

```bash
make setup
make gen
make mod
make gen
make gen
make fix
make fmt
make check
make test
make build
```

Uma falha → corrigir o dono do verbo; sem inflar timeout; sem remover testmon.
Executar os verbos sem seletores na raiz ativa do workspace. Completar com o
runtime público aplicável e a validação nativa de documentação e links.
Comprovar que repetições de `make gen`, `make fix` e `make fmt` não alteram o
candidato e terminam com exit zero; alterações posteriores invalidam os recibos
afetados. Warnings e findings residuais impedem o fechamento. Não iniciar outro
ciclo até comprovar a frota inteira verde nos SHAs integrados e publicados.

## (b) Contrato beads central

- `bd` roda via `direnv exec <repo> gc bd ...`
- A ativação vem do `.envrc`/`.envrc.local` gerado (AGENTS_GAS_CITY_ROOT + porta da publicação da cidade + banco da metadata do rig)
- Reparo de identidade: `gc rig set-endpoint flext --inherit`
- Nunca inicializar banco embedded/porta manual (fonte: `flext-infra/docs/guides/execution-context.md`)

## (c) Integração

1. Workers entregam reparos delimitados e evidências; não fazem merge nem fecham
   Beads. O coordenador mantém dependências, decisões de integração e a janela
   serializada de geração, ambiente e gates.
2. Preservar o WIP e revisar commits escopados (paths explícitos, nunca
   `git add -A`); integrar por `merge --no-ff` na branch de integração verificada,
   esperada `0.12.0-dev`, com revisão e CI aplicáveis.
3. Publicar membros antes de atualizar os gitlinks da raiz. Push fast-forward;
   divergência exige absorção por merge e revalidação, nunca rebase ou force-push.
4. Revalidar gates, convergência de geração e runtime no SHA integrado publicado;
   um checkpoint ou teste local não comprova a estabilidade da frota.
5. O coordenador registra no Bead comando, cwd, exit, saída decisiva, SHAs e
   recibos de revisão/CI/runtime; fecha apenas obrigações comprovadamente entregues.

## (d) Extermínios vigentes

`APPLY`, `uv.lock`, `mise.lock`, banco local de beads — leitura/geração também, não só gitignore.
