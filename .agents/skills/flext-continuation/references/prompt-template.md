# Continuação — `<BEAD_ID>`

Retome o trabalho cujo estado vivo está no bead `<BEAD_ID>`.
Este prompt é apenas um gatilho; a skill `<SKILL_NAME>` é a fonte da verdade.

## Contexto mínimo

- **Bead ativo:** `<BEAD_ID>`
- **Skill canônica:** `<SKILL_NAME>`

## Regras

- SSOT é o bead: recarregue-o a cada ciclo.
- Uma ação por ciclo: próximo passo não finalizado apenas.
- Verifique antes de editar: gate mais estreito da lane ativa.
- Evidência no bead: exit code + saída decisiva; logs longos em `.beads/artifacts/<BEAD_ID>/`.
- Pare no vermelho: sem contorno, supressão, adivinhação ou stub.
- Commit atômico: pathspecs explícitos, nunca `git add .`.

## Proibições

Não recopie `AGENTS.md`, skills ou código neste prompt.
Não armazene estado transitório aqui.
Não prescreva soluções técnicas; derive-as do diagnóstico.
Não crie automação, detectores ou heurísticas novos; use sub-bead.

## Próximo passo

Invoque `<SKILL_NAME>` e execute o próximo passo do bead com os gates canônicos.
