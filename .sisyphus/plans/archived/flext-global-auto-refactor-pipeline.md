# ARCHIVED — Subsumed by modernization-reorg-execution.md

# Flext Global Auto-Refactor Pipeline

## TL;DR

> **Quick Summary**: Automatizar refactor de melhoria em todos os projetos FLEXT, reaproveitando `flext_infra/refactor/*`, consolidando modelos/aliases/imports e validando namespace+MRO com gates completos.
>
> **Deliverables**:
> - Pipeline automatizado de discovery -> classify -> transform -> repoint -> validate
> - Reapontamento de imports/usos para locais canonicos
> - Validacao completa (ruff, mypy, pyright, pyrefly, testes) em todos os projetos
> - Evidencias e checkpoints para rollback/resume
>
> **Estimated Effort**: XL
> **Parallel Execution**: YES - 5 waves + final
> **Critical Path**: T1 -> T5 -> T9 -> T13 -> T16 -> FINAL

---

## Context

### Original Request
Automatizar refactor de melhoria em todo o workspace FLEXT (33+ projetos), interligando melhor o pipeline, corrigindo problemas, unificando/reusando modelos e reapontando usos/imports com validacao de namespace e MRO.

### Interview Summary
- Escopo global unico (sem dividir em multiplos planos)
- Reuso maximo de infraestrutura existente (sem reescrever do zero)
- Refactor automatico orientado por uso real
- Qualidade alvo: sem erros apos execucao

### Metis Review (incorporado)
- Gaps cobertos: definicao objetiva de "zero erro", preflight global, checkpoints por onda, fila de manual-review, edge cases (star import/dynamic import/cycle/metaclass).
- Guardrails adicionados: sem novas dependencias, sem mudanca de API publica, sem tocar codigo gerado/vendor, fail-fast por onda.

---

## Work Objectives

### Core Objective
Executar uma automacao de refactor de melhoria, em escala monorepo, que consolida arquitetura de modelos/handlers/imports e melhora o pipeline existente sem quebrar contratos publicos.

### Concrete Deliverables
- Orquestrador global no `flext_infra/refactor` para 33+ projetos
- Mapa de simbolos/aliases/usos por projeto
- Plano de repoint de imports e namespaces canonicos
- Validacao automatica de MRO/layer/quality gates
- Pacote de evidencias em `.sisyphus/evidence/` e `.reports/refactor/`

### Definition of Done
- [ ] Todos os projetos alvo passam em ruff+mypy+pyright+pyrefly+testes (ou baseline documentado e nao-regredido)
- [ ] Nenhum import quebrado apos reapontamento
- [ ] MRO/layer checks sem violacoes criticas
- [ ] Checkpoints e relatorios completos para auditoria

### Must Have
- Automacao ponta-a-ponta sem etapa manual obrigatoria
- Reuso de `scanner.py`, `engine.py`, `safety.py`, `mro_resolver.py`, `dependency_analyzer.py`, `rules/*`
- Repoint de imports/usos validado por AST e gates

### Must NOT Have (Guardrails)
- Nao adicionar framework/dependencia nova sem necessidade estrita
- Nao alterar assinatura de API publica
- Nao tocar `vendor/`, codigo gerado, fixtures de teste
- Nao misturar refactor com feature nova fora de escopo

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES
- **Automated tests**: YES (tests-after por onda + regressao global)
- **Framework**: stack existente por projeto

### Zero-Error Policy (objetiva)
- `ruff check` sem erros
- `mypy` sem erros
- `pyright` sem erros
- `pyrefly` sem erros
- testes do projeto sem regressao

### QA Policy
Cada task inclui cenarios executaveis por agente com evidencia em `.sisyphus/evidence/task-{N}-*.{log|json|png|txt}`.

---

## Execution Strategy

### Parallel Execution Waves

Wave 1 (baseline + classificacao): T1-T6
Wave 2 (modelos/aliases): T7-T11
Wave 3 (imports/usos): T12-T15
Wave 4 (MRO/layer hardening): T16-T19
Wave 5 (gates globais + evidencias): T20-T22
Wave FINAL (auditoria independente): F1-F4

### Dependency Matrix (resumo)
- T1: -- -> T2,T3,T4,T5,T6
- T5: T1 -> T7,T8,T9,T10,T11
- T9: T5 -> T12,T13,T14,T15
- T13: T9 -> T16,T17,T18,T19
- T16: T13 -> T20,T21,T22
- T20-T22: T16-19 -> F1-F4

### Agent Dispatch Summary
- Wave 1: quick/unspecified-high/deep (6 tarefas)
- Wave 2: deep/unspecified-high (5 tarefas)
- Wave 3: quick/deep/unspecified-high (4 tarefas)
- Wave 4: deep/unspecified-high (4 tarefas)
- Wave 5: unspecified-high/deep/writing (3 tarefas)
- FINAL: oracle + 3 validadores paralelos

---

## TODOs

- [ ] 1. Baseline global e inventario de projetos

  **What to do**: executar discovery de todos os projetos, registrar baseline de erros/avisos/testes e matriz de dependencias inicial.
  **Must NOT do**: iniciar transformacao sem baseline salvo.
  **Recommended Agent Profile**: Category `deep`; Skills `flext-patterns`, `scripts-validation`.
  **Parallelization**: NO; **Blocked By**: None; **Blocks**: T2-T6.
  **References**: `flext-core/src/flext_infra/refactor/engine.py`, `flext-core/src/flext_infra/refactor/dependency_analyzer.py`.
  **Acceptance Criteria**: baseline consolidado em `.reports/refactor/baseline.json`.
  **QA Scenarios**: happy/erro com evidencia em `task-4-*`.
  Scenario: Baseline happy
    Tool: Bash
    Steps: 1) run orchestrator baseline mode 2) assert file exists 3) assert projects >= 33
    Expected Result: baseline.json valido
    Evidence: .sisyphus/evidence/task-1-baseline.json

  Scenario: Baseline erro
    Tool: Bash
    Steps: 1) run with invalid root 2) assert non-zero exit 3) assert mensagem de erro clara
    Expected Result: falha graciosa
    Evidence: .sisyphus/evidence/task-1-invalid-root.log
  ```

- [ ] 2. Preflight de ambiente e segurança

  **What to do**: validar ferramentas, estado git, parse AST, arquivos protegidos/excluidos e limites de recurso.
  **Must NOT do**: modificar codigo quando preflight falhar.
  **Recommended Agent Profile**: Category `quick`; Skills `workspace-maintenance`, `scripts-security`.
  **Parallelization**: YES (Wave 1); **Blocked By**: T1; **Blocks**: T7-T22.
  **References**: `flext-core/src/flext_infra/refactor/safety.py`.
  **Acceptance Criteria**: relatorio `.reports/refactor/preflight.json` sem blockers criticos.
  **QA Scenarios**:
  ```
  Scenario: Preflight happy
    Tool: Bash
    Steps: run preflight; assert blockers==0
    Evidence: .sisyphus/evidence/task-2-preflight.json

  Scenario: Preflight erro
    Tool: Bash
    Steps: hide required tool; rerun; assert blocker emitted
    Evidence: .sisyphus/evidence/task-2-missing-tool.log
  ```

- [ ] 3. Scanner AST de simbolos/aliases/usos

  **What to do**: mapear classes de modelos/handlers, aliases (`m`, `h`, etc), propriedades e handlers nao-validacao, com contagem de referencias.
  **Must NOT do**: inferir uso sem evidencia de referencia.
  **Recommended Agent Profile**: Category `deep`; Skills `flext-agent-strict-rules`, `rules-src`.
  **Parallelization**: YES (Wave 1); **Blocked By**: T1; **Blocks**: T7-T15.
  **References**: `flext-core/src/flext_infra/refactor/scanner.py`, `flext-core/src/flext_core/models.py`, `flext-core/src/flext_core/handlers.py`.
  **Acceptance Criteria**: `symbol-map.json` com defs+refs+confidence.
  **QA Scenarios**:
  ```
  Scenario: Scanner happy
    Tool: Bash
    Steps: run scanner; assert keys models/handlers/properties exist
    Evidence: .sisyphus/evidence/task-3-symbol-map.json

  Scenario: Scanner erro
    Tool: Bash
    Steps: inject syntax-error fixture; rerun; assert file quarantined, run continues
    Evidence: .sisyphus/evidence/task-3-quarantine.log
  ```

- [ ] 4. Classificacao de codigo solto e candidatos de unificacao

  **What to do**: classificar unused/provavel-unused/referenciado dinamicamente; gerar backlog de consolidacao por risco.
  **Must NOT do**: deletar codigo automaticamente nesta fase.
  **Recommended Agent Profile**: Category `unspecified-high`; Skills `flext-refactoring-workflow`, `scripts-architecture`.
  **Parallelization**: YES (Wave 1); **Blocked By**: T1,T3; **Blocks**: T7-T11.
  **References**: `flext-core/src/flext_infra/refactor/analysis.py`.
  **Acceptance Criteria**: `loose-code-report.json` com confidence e action plan.
  **QA Scenarios**:
  ```

- [ ] 5. Definicao de namespace canonico por layer

  **What to do**: definir alvo canonico por projeto/layer (core/domain/application/infra) com regras de namespace.
  **Must NOT do**: criar namespace novo sem justificativa de uso.
  **Recommended Agent Profile**: Category `deep`; Skills `flext-architecture-layers`, `rules-flext-core`.
  **Parallelization**: YES (Wave 1); **Blocked By**: T1,T3; **Blocks**: T7-T19.
  **References**: `flext-core/src/flext_infra/refactor/project_classifier.py`, `flext-core/src/flext_infra/models.py`.
  **Acceptance Criteria**: `namespace-targets.json` com mapeamento completo.
  **QA Scenarios**: happy/erro com evidencia em `task-5-*`.

- [ ] 6. Orquestracao de ondas e checkpoints

  **What to do**: configurar execucao por ondas com checkpoint por wave/projeto e resume idempotente.
  **Must NOT do**: seguir para wave seguinte com falha critica nao resolvida.
  **Recommended Agent Profile**: Category `unspecified-high`; Skills `scripts-infra`, `workspace-maintenance`.
  **Parallelization**: YES (Wave 1); **Blocked By**: T1,T2; **Blocks**: T7-T22.
  **References**: `flext-core/src/flext_infra/refactor/safety.py`, `flext-core/src/flext_infra/refactor/engine.py`.
  **Acceptance Criteria**: resume de checkpoint reproduzivel.
  **QA Scenarios**: happy/erro com evidencia em `task-6-*`.

- [ ] 7. Consolidacao de aliases de modelos

  **What to do**: reapontar aliases duplicados/legacy para nomes canonicos em `m.*` mantendo compatibilidade de API.
  **Must NOT do**: quebrar import publico existente.
  **Recommended Agent Profile**: Category `deep`; Skills `flext-agent-strict-rules`, `flext-type-system`.
  **Parallelization**: YES (Wave 2); **Blocked By**: T4,T5,T6; **Blocks**: T12-T15.
  **References**: `flext-core/src/flext_core/models.py`.
  **Acceptance Criteria**: aliases legados reduzidos e referencias atualizadas.
  **QA Scenarios**: happy/erro com evidencia em `task-7-*`.

- [ ] 8. Consolidacao de contratos de handlers

  **What to do**: unificar contratos de handler/registration/decorator para ponto canonico e remover duplicacoes de representacao.
  **Must NOT do**: mudar semantica de pipeline de `FlextHandlers`.
  **Recommended Agent Profile**: Category `deep`; Skills `backend-api-patterns`, `flext-patterns`.
  **Parallelization**: YES (Wave 2); **Blocked By**: T4,T5; **Blocks**: T12-T19.
  **References**: `flext-core/src/flext_core/handlers.py`, `flext-core/src/flext_core/_models/handler.py`.
  **Acceptance Criteria**: contratos unificados com testes verdes.
  **QA Scenarios**: happy/erro com evidencia em `task-8-*`.

- [ ] 9. Repoint de usos para local canonico (AST)

  **What to do**: aplicar transformacoes AST (nao regex) para reapontar `imports` e acessos simbolicos para namespaces canonicos.
  **Must NOT do**: rewrite textual cego.
  **Recommended Agent Profile**: Category `unspecified-high`; Skills `flext-strict-refactoring`, `rules-scripts`.
  **Parallelization**: YES (Wave 2); **Blocked By**: T5,T7,T8; **Blocks**: T12-T16.
  **References**: `flext-core/src/flext_infra/refactor/rules/import_modernizer.py`, `flext-core/src/flext_infra/refactor/transformers/class_reconstructor.py`.
  **Acceptance Criteria**: `import-repoint-report.json` sem unresolved targets.
  **QA Scenarios**: happy/erro com evidencia em `task-9-*`.

- [ ] 10. Ajuste automatico de imports quebrados

  **What to do**: detectar e corrigir imports invalidos pos-repoint, incluindo alias collisions.
  **Must NOT do**: criar ciclos novos.
  **Recommended Agent Profile**: Category `quick`; Skills `flext-import-rules`, `rules-src`.
  **Parallelization**: YES (Wave 2); **Blocked By**: T9; **Blocks**: T13-T16.
  **References**: `flext-core/src/flext_infra/refactor/dependency_analyzer.py`.
  **Acceptance Criteria**: import-check 100% pass.
  **QA Scenarios**: happy/erro com evidencia em `task-10-*`.

- [ ] 11. Fila automatica de manual-review (baixo risco de quebra)

  **What to do**: separar casos ambigüos (dynamic import, metaclass edge, star import) em fila estruturada sem bloquear restante.
  **Must NOT do**: travar pipeline inteiro por outlier.
  **Recommended Agent Profile**: Category `writing`; Skills `scripts-maintenance`, `flext-plan-hygiene`.
  **Parallelization**: YES (Wave 2); **Blocked By**: T4,T9; **Blocks**: T20-T22.
  **References**: `flext-core/src/flext_infra/refactor/rules/*`.
  **Acceptance Criteria**: `manual-review-queue.json` com severidade e proposta.
  **QA Scenarios**: happy/erro com evidencia em `task-11-*`.

- [ ] 12. Validacao estrutural de referencias de modelos

  **What to do**: validar se todo uso de model aponta para classe canonica apos refactor e sem alias morto.
  **Must NOT do**: confiar apenas em import check sem usage check.
  **Recommended Agent Profile**: Category `deep`; Skills `flext-type-system`, `testing-patterns`.
  **Parallelization**: YES (Wave 3); **Blocked By**: T7,T9,T10; **Blocks**: T16-T22.
  **References**: `flext-core/src/flext_core/models.py`, `flext-core/src/flext_infra/models.py`.
  **Acceptance Criteria**: `model-usage-validation.json` sem dangling refs.
  **QA Scenarios**: happy/erro com evidencia em `task-12-*`.

- [ ] 13. Validacao de namespace por layer (core/domain/app/infra)

  **What to do**: verificar classes/simbolos no layer correto e reportar desvios com sugestao automatica.
  **Must NOT do**: mover simbolos sem prova de uso/contrato.
  **Recommended Agent Profile**: Category `deep`; Skills `flext-architecture-layers`, `scripts-architecture`.
  **Parallelization**: YES (Wave 3); **Blocked By**: T5,T9,T10; **Blocks**: T16-T20.
  **References**: `flext-core/src/flext_infra/refactor/project_classifier.py`.
  **Acceptance Criteria**: `layer-validation.json` sem violacoes criticas.
  **QA Scenarios**: happy/erro com evidencia em `task-13-*`.

- [ ] 14. Validacao MRO pre/post-transform

  **What to do**: calcular MRO antes/depois e bloquear regressao de ordem funcional de resolucao.
  **Must NOT do**: aceitar conflito de heranca em silencio.
  **Recommended Agent Profile**: Category `deep`; Skills `python-313-typing`, `flext-type-system`.
  **Parallelization**: YES (Wave 3); **Blocked By**: T8,T9,T13; **Blocks**: T16-T22.
  **References**: `flext-core/src/flext_infra/refactor/mro_resolver.py`.
  **Acceptance Criteria**: `mro-diff-report.json` sem conflitos novos.
  **QA Scenarios**: happy/erro com evidencia em `task-14-*`.

- [ ] 15. Ajuste de handlers e propriedades nao-validacao

  **What to do**: mapear/reapontar usos de propriedades e handlers operacionais (nao apenas `validate`) para pontos canonicos.
  **Must NOT do**: remover propriedade usada implicitamente sem referencia cruzada.
  **Recommended Agent Profile**: Category `unspecified-high`; Skills `backend-data-patterns`, `python-type-narrowing`.
  **Parallelization**: YES (Wave 3); **Blocked By**: T3,T8,T9; **Blocks**: T16,T20.
  **References**: `flext-core/src/flext_core/handlers.py`.
  **Acceptance Criteria**: `handler-property-usage.json` com 100% coverage de referencias.
  **QA Scenarios**: happy/erro com evidencia em `task-15-*`.

- [ ] 16. Execucao de transformacao global por ondas

  **What to do**: aplicar todas as regras aprovadas por ondas, com fail-fast e rollback por checkpoint.
  **Must NOT do**: seguir apos erro critico sem rollback/recovery.
  **Recommended Agent Profile**: Category `unspecified-high`; Skills `scripts-infra`, `workspace-maintenance`.
  **Parallelization**: YES (Wave 4); **Blocked By**: T12,T13,T14,T15; **Blocks**: T20-T22.
  **References**: `flext-core/src/flext_infra/refactor/engine.py`, `flext-core/src/flext_infra/refactor/safety.py`.
  **Acceptance Criteria**: `wave-execution-report.json` completo.
  **QA Scenarios**: happy/erro com evidencia em `task-16-*`.

- [ ] 17. Gate ruff+mypy por projeto transformado

  **What to do**: rodar quality gates de lint/tipagem por projeto apos transformacao da onda.
  **Must NOT do**: aceitar warning/error novo.
  **Recommended Agent Profile**: Category `quick`; Skills `flext-quality-gates`, `scripts-validation`.
  **Parallelization**: YES (Wave 4); **Blocked By**: T16; **Blocks**: T20-T22.
  **References**: `base.mk`, scripts de validacao do workspace.
  **Acceptance Criteria**: relatorio por projeto com status PASS/FAIL.
  **QA Scenarios**: happy/erro com evidencia em `task-17-*`.

- [ ] 18. Gate pyright+pyrefly por projeto transformado

  **What to do**: validar estaticamente tipagem avancada e compatibilidade pos-repoint.
  **Must NOT do**: mascarar erro com ignore.
  **Recommended Agent Profile**: Category `unspecified-high`; Skills `flext-pyrefly-typecheck-fix`, `flext-strict-typing`.
  **Parallelization**: YES (Wave 4); **Blocked By**: T16; **Blocks**: T20-T22.
  **References**: configuracoes de pyright/pyrefly dos projetos.
  **Acceptance Criteria**: zero erros novos.
  **QA Scenarios**: happy/erro com evidencia em `task-18-*`.

- [ ] 19. Regressao de testes por projeto e cross-project smoke

  **What to do**: rodar suites locais + smoke de integracao entre projetos dependentes.
  **Must NOT do**: concluir com regressao nao documentada.
  **Recommended Agent Profile**: Category `deep`; Skills `testing-patterns`, `scripts-testing`.
  **Parallelization**: YES (Wave 4); **Blocked By**: T16; **Blocks**: T20-T22.
  **References**: comandos de teste de cada projeto.
  **Acceptance Criteria**: sem regressao funcional.
  **QA Scenarios**: happy/erro com evidencia em `task-19-*`.

- [ ] 20. Auditoria de import graph e ciclos

  **What to do**: recalcular grafo de imports, detectar ciclos novos e falhas de resolucao.
  **Must NOT do**: manter ciclo novo sem mitigacao.
  **Recommended Agent Profile**: Category `deep`; Skills `scripts-architecture`, `flext-patterns`.
  **Parallelization**: YES (Wave 5); **Blocked By**: T13,T16,T17,T18; **Blocks**: FINAL.
  **References**: `flext-core/src/flext_infra/refactor/dependency_analyzer.py`.
  **Acceptance Criteria**: `import-graph-after.json` sem ciclos novos.
  **QA Scenarios**: happy/erro com evidencia em `task-20-*`.

- [ ] 21. Consolidacao de evidencias e artefatos

  **What to do**: agregar relatorios por projeto/onda em pacote unico auditavel.
  **Must NOT do**: perder rastreabilidade entre transformacao e validacao.
  **Recommended Agent Profile**: Category `writing`; Skills `readme-standardization`, `skill-format-universal`.
  **Parallelization**: YES (Wave 5); **Blocked By**: T16-T19; **Blocks**: FINAL.
  **References**: `.sisyphus/evidence/`, `.reports/refactor/`.
  **Acceptance Criteria**: indice de evidencias completo.
  **QA Scenarios**: happy/erro com evidencia em `task-21-*`.

- [ ] 22. Dry-run final + run final idempotente

  **What to do**: executar dry-run global e run final garantindo idempotencia (rodar duas vezes, mesmo resultado).
  **Must NOT do**: concluir sem prova de idempotencia.
  **Recommended Agent Profile**: Category `unspecified-high`; Skills `scripts-validation`, `workspace-maintenance`.
  **Parallelization**: YES (Wave 5); **Blocked By**: T16-T21; **Blocks**: FINAL.
  **References**: orquestrador global configurado nas tasks anteriores.
  **Acceptance Criteria**: segunda execucao nao gera diff inesperado.
  **QA Scenarios**: happy/erro com evidencia em `task-22-*`.

---

## Final Verification Wave

- [ ] F1. **Plan Compliance Audit** (`oracle`)
- [ ] F2. **Code Quality Review** (`unspecified-high`)
- [ ] F3. **Real QA Replay** (`unspecified-high`)
- [ ] F4. **Scope Fidelity Check** (`deep`)

---

## Commit Strategy

- Commits por onda, agrupados por dominio (`refactor(models)`, `refactor(imports)`, `refactor(mro)`, `chore(validation)`).

---

## Success Criteria

### Verification Commands
```bash
make validate VALIDATE_SCOPE=workspace
```

### Final Checklist
- [ ] Todos os "Must Have" entregues
- [ ] Todos os "Must NOT Have" respeitados
- [ ] Gates verdes em todos os projetos afetados
- [ ] Evidencias e relatorios publicados
