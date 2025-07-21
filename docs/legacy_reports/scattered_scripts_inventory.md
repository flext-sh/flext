# SCATTERED SCRIPTS INVENTORY - COMPLETE ANALYSIS

**Status**: URGENT - 51 scripts espalhados precisam ser organizados
**Última Análise**: 2025-07-05

---

## 🚨 SCRIPTS ESPALHADOS POR CATEGORIA

### 📂 algar-oud-mig/scripts/ (23 scripts)

**Fix Scripts (21)**:

- fix_blind_excepts.py
- fix_broken_variables.py
- fix_critical_pep.py
- fix_e501_comprehensive.py
- fix_f821_critical.py
- fix_final_phase.py
- fix_final_violations.py
- fix_import_duplicates.py
- fix_line_length_intelligent.py
- fix_long_lines.py
- fix_long_lines_smart.py
- fix_pep_strict.py
- fix_pep_systematic.py
- fix_remaining_e501.py
- fix_syntax_emergency.py
- fix_t201_prints.py
- fix_test_quality.py
- fix_tests_quality.py
- fix_todo_comments.py
- fix_typing_any.py
- fix_typing_strict.py

**Utility Scripts (2)**:

- pep_progress_report.py
- test_runner.py
- test_runner_modern.py

### 📂 Outros Projetos com Scripts

**flext-tap-oracle-wms/scripts/**:

- test_config_validation.py

**flext-core/scripts/**:

- test_pipeline.py

**flext-quality/scripts/**:

- run_tests.py

### 📂 Root scripts/ (3 test scripts)

**Scripts de Teste**:

- stress-test.sh
- test-distributed.sh
- test-end-to-end-pipeline.sh

---

## 🎯 PLANO DE CONSOLIDAÇÃO

### Fase 1: Análise de Funcionalidade

- [ ] Verificar se scripts em algar-oud-mig são específicos do projeto
- [ ] Identificar funcionalidades genéricas reutilizáveis
- [ ] Avaliar se scripts de teste são úteis ou obsoletos

### Fase 2: Consolidação

- [ ] Mover scripts específicos para diretório legacy do projeto
- [ ] Integrar funcionalidades genéricas no quality_gateway.py
- [ ] Criar scripts unificados para funcionalidades comuns

### Fase 3: Limpeza

- [ ] Remover duplicações
- [ ] Padronizar interface
- [ ] Atualizar documentação

---

## ⚠️ PRIORIDADES

**ALTA**: algar-oud-mig tem 23 scripts que podem estar duplicando funcionalidade
**MÉDIA**: Scripts de teste podem ser obsoletos
**BAIXA**: Scripts isolados em outros projetos

---

**PRÓXIMA AÇÃO**: Analisar conteúdo dos scripts para determinar quais são genéricos vs específicos
