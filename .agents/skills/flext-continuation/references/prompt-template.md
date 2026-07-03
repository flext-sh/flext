# Continuação — EPIC `<BEAD_ID>`

## Instrução de entrada

Você está retomando um EPIC no FLEXT. Siga a skill canônica `flext-continuation`; este arquivo é apenas o gatilho de contexto.

## Contexto mínimo

- **Bead ativo:** `<BEAD_ID>`
- **Objetivo do EPIC:** `<EPIC_OBJECTIVE>`
- **Skills de domínio prováveis:** `<DOMAIN_SKILLS>`

## O que fazer agora

1. Invocar **skill `flext-continuation`** com o bead `<BEAD_ID>`.
2. Carregar as skills de domínio listadas acima se o próximo passo tocar em seus respectivos domínios.
3. Ler o plano/artefato mais recente em `.beads/artifacts/<BEAD_ID>/`.
4. Executar o próximo passo não-finalizado, um por ciclo, com os gates canônicos do FLEXT.

## O que NÃO fazer

- Não recopie `AGENTS.md` ou skills neste prompt.
- Não armazene estado transitório aqui (SHAs, contagens, nomes de arquivos específicos).
- Não prescreva soluções técnicas; derive-as do diagnóstico atual.
- Não crie automação/detectores/heurísticas novos no fluxo principal — sub-bead próprio.

## Comando de referência

```bash
bd show <BEAD_ID>
```

Toda ação subsequente está na skill `flext-continuation`.
