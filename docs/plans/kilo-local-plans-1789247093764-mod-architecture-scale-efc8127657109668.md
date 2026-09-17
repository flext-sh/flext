# Plano: refatoracao arquitetural em escala pelo make mod (com simplificacao)

## Objetivo e decisoes aprovadas

Evoluir a automacao existente em flext-infra para detectar desvios arquiteturais, planejar correcoes e atualizar automaticamente todos os consumidores locais do workspace, e em seguida simplificar os componentes dessa automacao removendo cruft com funcionalidade preservada.

- Escopo: workspace completo (src, tests, examples, scripts, projecoes regeneradas), projetos descobertos pela topologia SSOT. Consumidores externos so aparecem como limite de cobertura.
- Interface unica: make mod. Regras ast-grep no catalogo atual; mudanças entre arquivos pela fase semantica existente. Nao criar motor rope_rules nem DSL paralela.
- A instrucao do operador substitui a secao de engine declarativo do ADR-014: atualizar ADR/skill na implementacao preservando o contrato arquitetural (shape law).
- Corrigir automaticamente casos com precondicoes comprovadas; todo caso restante produz diagnostico acionavel e impede declarar convergencia. Nao existe correcao semantica automatica garantida para Python arbitrario.
- Modo planejamento: nesta sessao nao houve propagacao, commits ou gates.

## Fatos verificados (auditoria de codigo, leitura direta)

Fontes: batch_apply.py, semantic_apply.py, batch_gates.py, class_nesting*.py, project_discovery.py, constants_quality_gate.py, Makefile.j2, cli_routes, consolidator.py. Referencias arquivo:linha do checkout atual.

1. Circuitoo atual: batch_apply.py:21-88 descobre regras, preflight, aplica fase semantica (semantic_apply.py:21-100) + ast-grep, detecta repeticao por fingerprint e exige validacao final. Cinco fases semanticas: future-annotations, deferred-models, nesting, aliases (somente api.py), private-imports.
2. VAZIO DE TRANSFORM: class_nesting_cst.py:39-111 so move ClassDef top-level para dentro de um owner. Nao existe: extracao de classe aninhada (hoist para fora), achatamento de wrapper com dados com rebinding X.Dbt.Y -> X.Y, nem remocao de alias em arquivo handwritten (semantic_apply.py:65-70 filtra ban-compat-alias por file.name == api.py). O piloto ADR-014 (flext-dbt-oracle-wms) exige exatamente esses tres transforms; sem eles, ou o desvio fica invisivel (sem regra) ou o circuito falha "made no progress" sem causa (com regra detection-only).
3. GERADOS EXPOSTOS: project_discovery.py:89-110 monta targets ast-grep como project/scan_dirs + project.glob("*.py") sem exclusao AUTOGEN; o apply (batch_gates.py:487-499, --rewrite-all) nao pula gerados. O planner semantico pula (class_nesting.py:155; semantic_apply.py:138), gerando assimetria e risco de oscilacao gen x mod.
4. ESCOPO LEXICAL: class_nesting_references.py:99-124 trata apenas FunctionDef/ClassDef como boundary; Lambda/compreensoes no corpo do owner mantem nome bare -> NameError. _nest_definitions nao verifica classe nao-movida definida antes do owner usando simbolo em definition-time.
5. COBERTURA ASSIMETRICA: semantic_apply.py:107-119 inventaria apenas scan_dirs (exclui .py na raiz do projeto); ast-grep inclui project.glob("*.py"). Consumidor root-level recebe fix sem rewiring. Star import perde simbolo (class_nesting_references.py:87,191,223-250).
6. DIAGNOSTICO: no-progress nao atribui fase/regra; residuo-check pos-publicacao existe so para nesting (semantic_apply.py:93-100); findings text == replacement (batch_gates.py:331-340) nunca convergem e travam ate o dry-run; dry-run nao valida fixtures (batch_apply.py:27-43 vs 51-52).
7. TOPOLOGIA TRIPLA: project_discovery.py:47-86 usa .gitmodules UU filhos com pyproject.toml; RefactorConfig().project_scan_dirs e default hardcoded de modelo (refactor_ast_grep.py:22-30). workspace.yaml e o SSOT declarado (AGENTS raiz). Eleicao necessaria.
8. PUBLICACAO FORA DO JOURNAL: semantic_apply.py:191-192 escreve via atomic_write_text_file_guarded direto; o mecanismo u.Infra.publish_file_plans (journal + backup + recovery) nao e usado na unica fase multi-repo sem transacao.
9. AUTOGEN DRIFT: semantic_apply.py:138 usa literal "# AUTO-GENERATED FILE"; class_nesting.py:155 usa c.Infra.AUTOGEN_HEADERS (variantes em _constants/codegen_lazy.py:20-26).
10. QUALITY GATE FALSO: constants_quality_gate.py:244-246,331-333 fixam zeros; passed=(value==0) em 278-286 transforma nao-medido em PASS; modified_python_files depende de git status local.
11. DEFAULT DO VERBO: Makefile.j2:698-699 encaminha mod para refactor mod --apply; linhas 351-355 rejeitam; linha 416 anuncia aplicacao por padrao. Inspecionar via make mod hoje nao e seguro.
12. Regras compostas por metadata de distribuicao instalada (codemod_rules.py:24-66): editar YAML local nao prova propagacao; evidencia exige identidade de provider/regra.
13. "local-safe" de um fix ast-grep e propriedade de autoria de regra, nao do mecanismo (validate_rule_fixtures valida snapshots, nao localidade).
14. Consolidator existe (codegen/consolidator.py, verbo CLI consolidate); auditoria que negou sua existencia foi refutada por leitura direta.

## Contratos arquiteturais (inalterados)

1. Cinco familias, base.py, dono descoberto por convencao SSOT; nao deduzir dono por prefixo textual.
2. Orfa vira entidade publica aninhada no part class certo; sem classe privada + alias.
3. Wrapper puro e achatado com rewiring e remocao no mesmo corte.
4. Enum/modelo/protocolo/classe com comportamento nao sao wrappers; metaclasses e definition-time exigem semantica.
5. Facades e lazy exports so mudam pelo gerador; porem o pipeline deve garantir isso (fato 3), nao a disciplina.
6. c -> t -> p -> m -> u; constants declarativas; config mutavel em config/settings.
7. Igualdade de valor nao prova duplicacao; consolidacao so com dono/contrato comprovados.
8. ClassVar somente constante arquitetural indevida; contratos de framework preservados.
9. Sem alteracao de valores de protocolo/serializacao como efeito colateral estrutural.
10. Sem supressoes, mocks, aliases transitorios ou exclusoes para produzir verde.

## Unidades de trabalho (re-sequenciadas pela auditoria)

Regra transversal: a simplificacao/remocao de cruft NAO e um programa adicional; faz parte da execucao de cada unidade restante. Todo dono tocado em T1-T5 sai da unidade mais simples e direto no padrao FLEXT (skill simplify: complexidade acidental removida com contratos preservados; LOC liquido negativo ou neutro; cruft comprovadamente sem consumer removido no mesmo corte, skill safe-delete; corte atomico com rewiring). O inventario global do circuito (subagente em curso: LOC, superficie publica, consumers, duplicacao, mixins de implementacao unica, constantes sem leitor) e o INPUT que alimenta essas decisoes em cada unidade, nao uma fase posterior.

Sem consumer provado NAO e cruft (dynamic dispatch/getattr/star-import/entrypoint/pytest plugin/template .j2/provider por metadata): hipotese sem prova vira bloqueio classificado na unidade, nao remocao. Candidatos suspeitos a confirmar pelo inventario: censos duplicados (codegen census vs refactor census e seus consumidores reais), cadeias de mixin com implementacao unica, fases/flags sem rota CLI, metricas/zeros mortos do quality gate, tabelas de _constants sem leitor.

### T1. Escopo unico e protecao de gerados

- Eleger workspace.yaml como autoridade de topologia; .gitmodules/descoberta direta viram verificacao de consistencia (divergencia = erro ou classificacao explicita, nunca silencio).
- Mover project_scan_dirs de default de modelo para config lida (anti-hardcode, mesmo reparo do quality gate).
- Unificar num unico dono a selecao de arquivos entre targets ast-grep e inventario semantico, incluindo .py de raiz de projeto (fato 5).
- Excluir AUTOGEN nos alvos de apply OU regenerar dentro do ciclo antes do rescan; fixture provando que nenhuma regra do catalogo casa projecoes geradas (fato 3, causa-raiz do teste gen x mod da matriz).
- Unificar deteccao autogen em c.Infra.AUTOGEN_HEADERS (fato 9).
- Simplificacao no mesmo corte: defaults de modelo viram config; deteccao autogen unica; sem autoridade de topologia duplicada remanescente.
- Aceite: scan e inventario veem o mesmo conjunto; regra nova que case gerado falha em fixture, nao em producao.

### T2. Planejamento e evidencia confiaveis

- Rotear _publish por u.Infra.publish_file_plans (journal + backup + recovery) (fato 8; decisao de projeto codegen.publish_file_plans).
- Residuo-check pos-publicacao para toda fase semantica, nao so nesting (fato 6b).
- No-progress com atribuicao de causa (fase/regra responsavel no erro) (fato 6a).
- Validar em validate_rule_fixtures o contrato fix != match (fato 6c) e declaracao "local-safe" por regra para fixes automaticos (fato 13).
- Dry-run valida fixtures e expoe preview semantico (impacto e bloqueios) sem escrita; hoje e capacidade a construir (fato 6d).
- Corrigir quality gate para escopo/resultado reais, incluindo consumidores entre repositorios (fato 10); distinguir medido/falhado/nao executado.
- Estender modelos existentes (finding/edit/report) apenas onde faltar: identidade semantica, dono origem/destino, referencias afetadas, motivo de bloqueio.
- Simplificacao no mesmo corte: fases/flags sem rota CLI, zeros fixos e metricas mortas do quality gate removidos conforme inventario; caminho de publicacao unico (journal), sem rota guardada paralela residual.
- Aceite: falha intermediaria evidenciada pelo journal; zeros so existem medidos.

### T3. Transformer lexical e os tres transforms novos

- Corrigir boundary lexical: Lambda/compreensoes/GeneratorExp como boundary em _resolves_bare_after_nesting (fato 4).
- Verificar/ajustar ordenacao de definicao pos-rewrite no modulo (classe nao-movida antes do owner usando simbolo em definition-time).
- Transform A (extracao/hoist): classe aninhada sai do wrapper para top-level e entra no part class certo (composto: extrair + aninhar).
- Transform B (achatamento): wrapper com dados e achatado; membros sobem um nivel com rebinding X.Wrapper.Y -> X.Y em todos os consumidores; colisao usa prefixo derivado so com contrato e unicidade provados, senao bloqueia.
- Transform C (alias generalizado): remocao de alias de compatibilidade em qualquer arquivo handwritten com escopo declarado (substituir o filtro file.name == api.py por selecao por contrato).
- Regras ast-grep detection-only apontando os candidatos desses transforms; regras fixaveis apenas se local-safe auditado.
- Gate alignment: namespace validator e codemod com mesma classificacao/policas e vocabulario (ADR-014 secao 5).
- Simplificacao no mesmo corte, com limite explicito: cadeias de mixin que existem para satisfazer a lei de LOC por part-file sao padrao canonico, NAO cruft — colapsar apenas quando a cadeia for acidental e o modulo resultante permanecer dentro do cap SSOT; deteccao duplicada entre validator e codemod e unificada por contrato, nao por copia.
- Aceite T3: piloto planejavel integralmente em dry-run sem escrita.

### T4. Piloto flext-dbt-oracle-wms

- Executar automaticamente: hoist de _Materialization (Transform A composto), achatamento de Dbt em base.py e enums.py (Transform B), retirada de aliases Materialization/DbtMaterialization (Transform C), rewiring de base.py:23, _models/dbt.py:28, _utilities/model_builder.py:34 e quaisquer referencias descobertas; regenerar exports pelo dono; validar facade/enum/modelo reais.
- Verificar destino canonico de PROJECT_NAME conforme ADR-005 antes de presumir pertencimento a c.
- Sem acionar operacoes Oracle externas para provar mudanca de namespace.
- Aceite: consumidor real funciona; zero referencias locais obsoletas; exports convergentes; sem residuo.

### T5. Escala e propagacao

- Medir (cProfile) antes de otimizar; reutilizar inventario/indice por execucao; eliminar leituras e scans repetidos por arquivo primeiro.
- Componente = simbolo + todos os consumidores; nao dividir arbitrariamente para caber em lote.
- Paralelizar leitura/analise/gates independentes; escritas e regeneracao serializadas por arquivo/lock; nunca dois workers no mesmo componente.
- Ordem pela DAG real (donos antes de dependentes); piloto abre a propagacao por componentes pequenos ate a topologia inteira.
- Progresso causal < 60s por fase; sem truncar traceback.
- Questao aberta cross-repo: candidato coordenado (pins + CI conjunta) antes de componentes que atravessam repos; alternativa conservadora: aplicar so componentes com sequencia de integracao comprovadamente verde, demais bloqueados sem declarar propagacao completa.

### T6. Inventario transversal consolidado (verificado)

- CRG bloqueado por permissao (fato registrado: `code-review-graph status`/`crg status` negados a subagente e a sessao principal; ADR-010 3b/flext-law tratam CRG como enriquecimento opcional). Se liberado na execucao, entra como evidencia complementar.
- Mapeamento estatico + verificacao direta desta sessao, com evidencia:
  - Verbos CLI-only com testes e SEM rota em qualquer Makefile/template: `codegen census` (cli_routes_codegen.py:115, tests/unit/codegen/census_tests.py), `codegen consolidate` (:169, consolidator_tests.py), `codegen auto-fix` (:133, autofix_workspace_tests.py), `codegen constants-quality-gate` (:160, constants_quality_gate_tests.py), `refactor census` (cli_routes_refactor.py:38, utilities_gates.py:14, test_main_cli.py:556). Classificacao: superficie CLI documentada, nao cruft; nao deletar por ausencia de rota Make. Uso operacional deles no programa: consolidate/census/quality-gate apoiam o eixo dedup pos-piloto.
  - `FlextInfraCodegenQualityGate` consumindo `FlextInfraRefactorCensus` (constants_quality_gate.py:56) com zeros fixos (fato 10): reparo em T2, nao remocao.
  - Dois censos coexistem com propositos distintos (codegen census = violacoes de namespace por projeto; refactor census = objetos Rope com kinds/duplicatas). Consolidacao ou manutencao decidida em T2 com evidencia de consumers (search-first); nao pre-decidida aqui.
  - Mixins _census_* (14 arquivos, consumer unico FlextInfraRefactorCensus) e parts _lazy_init_*: padrao canonico de part-splitting da lei de LOC; fora do escopo de remocao.
  - `consolidator.py` existe (verbo consolidate); referencia anterior do plano mantida.
- Disciplina por corte (constante em T1-T5): search-first (lazy exports, providers por metadata, entrypoints, pytest plugin, templates) -> simplify no dono tocado -> safe-delete com recovery via journal/git e corte atomico.
- Regra dura mantida: sem consumer provado NAO e cruft; hipotese sem prova vira bloqueio classificado.

## Matriz minima de verificacao (estendida)

- Fixtures ast-grep: positivos/negativos/decorators/comentarios/strings/multiplos donos/fora das familias; fix != match; nenhuma regra casa projecoes geradas.
- Lexical novo: lambda/compreensao no corpo do owner; classe nao-movida antes do owner usando simbolo em definition-time; metodos/compreensoes.
- Rewiring: A.X vs B.X; imports relativos/alias/shadowing; facade MRO multi-parts; enum aninhada (decorators/valores); alias/reexport removido com __all__ regenerado; star-import; consumidor root-level (conftest.py); anotacoes em string; templates e snippets executaveis.
- Cobertura: arquivo limpo pode ser consumidor; descoberta incompleta falha; provedores/regras identificados por versao/recurso.
- Seguranca: arquivo alterado pos-preflight; falha no meio da publicacao (journal prova efeitos e recovery); caminho fora do escopo; fonte gerada; retomada sem perda de WIP.
- Convergencia: mod x2; gen/fix/fmt x2; interacao gen x mod (oscilacao); dry-run nao muda snapshots; na aplicacao, snapshot atualizado sozinho nunca e unica evidencia.
- Comportamento: testes pelas facades sem mocks; valores da SSOT, nao congelados; testmon retido.
- Gates finais: make check/test/build pela superficie canonica (Ruff, Pyrefly, Pyright, Mypy, cobertura); grammar confirmada na SSOT.

## Protocolo operacional (proposta, NAO comportamento atual)

```text
make mod            inspecao + preview semantico (A CONSTRUIR; hoje o default aplica!)
make mod    aplica componentes seguros, registra bloqueios
make gen    regenera pelo dono
make check          estado combinado + cobertura
make test           comportamento canonic
```

Riscos conhecidos: fazer mod hoje aplica por padrao (fato 11); a interpolacao com o contrato flext-law (para mutacao) sera resolvida com o operador antes de qualquer sweep; mudanca de default exige teste de contrato e regeneracao para todos os profiles. Sem flags de exclusao ou listas manuais de projetos.

## Organizacao e fechamento

Orquestrador coordena; workers implementam unidades delimitadas; revisao independente para rewiring e remocao; documentacao na mesma mudanca. Sem gas-city. Landing quando autorizado: commit escopado -> push FF da lane -> PR -> review resolvido -> merge --no-ff -> gates no SHA integrado; sem bypass de CI; absorcao por merge, nunca rebase/force-push; gitlinks so para revisoes publicadas.

Concluido = topologia inteira coberta; zero desvios pendentes dos contratos declarados; zero referencias antigas resolviveis; ambiguidades classificadas, nao ocultas; runtime e gates verdes no integrado; geracao idempotente; cruft removido com funcionalidade preservada; docs/evidencias/tracking atualizados.

## Pendencias e limites

- Subagentes concluidos: auditoria de riscos (integrada como fatos 1-14), coleta CRG (bloqueada por permissao, registrado), mapeamento do circuito (arquitetura confirmada; lista concreta de alvos verificada diretamente nesta sessao — ver T6).
- bd bloqueado por permissao nesta sessao: tracking (flext-joe2x) revalidado quando autorizado; sem contorno.
- Reconciliacao AGENTS 200 vs codegen.yaml 1000 antes de qualquer criterio de tamanho.
- Contrato do verbo mod (default aplica) resolvido com o operador antes de qualquer sweep; mudanca exige teste de contrato e regeneracao dos profiles.
- Nao prometido: correcao de referencias dinamicas arbitrarias; decisoes de negocio automaticas; merges atomicos entre repositorios independentes sem protocolo coordenado.
