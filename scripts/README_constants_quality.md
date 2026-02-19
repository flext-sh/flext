# FLEXT Constants Quality Assurance


<!-- TOC START -->
- [Visão Geral](#viso-geral)
- [Funcionalidades](#funcionalidades)
  - [✅ Validação de Conformidade de Constantes](#-validao-de-conformidade-de-constantes)
  - [✅ Detecção de Declarações Duplicadas](#-deteco-de-declaraes-duplicadas)
  - [✅ Validação de Padrões FLEXT](#-validao-de-padres-flext)
  - [✅ Detecção de Uso Incorreto](#-deteco-de-uso-incorreto)
  - [✅ Infraestrutura de Qualidade](#-infraestrutura-de-qualidade)
- [Uso](#uso)
  - [Uso Básico (Recomendado)](#uso-bsico-recomendado)
  - [Correção Automática](#correo-automtica)
  - [Operações Avançadas](#operaes-avanadas)
- [Exemplos Práticos](#exemplos-prticos)
  - [1. Workflow Completo para FLEXT-Core](#1-workflow-completo-para-flext-core)
  - [2. Análise Rápida de Todos os Projetos](#2-anlise-rpida-de-todos-os-projetos)
  - [3. Correção Automática com Backup](#3-correo-automtica-com-backup)
  - [4. Recuperação de Emergência](#4-recuperao-de-emergncia)
- [Tipos de Violações Detectadas](#tipos-de-violaes-detectadas)
  - [CONSTANTS - Violações de Conformidade](#constants-violaes-de-conformidade)
  - [DUPLICATE - Declarações Duplicadas](#duplicate-declaraes-duplicadas)
  - [PATTERN - Violações de Padrões FLEXT](#pattern-violaes-de-padres-flext)
  - [USAGE - Uso Incorreto](#usage-uso-incorreto)
- [Relatórios Gerados](#relatrios-gerados)
- [Infraestrutura Técnica](#infraestrutura-tcnica)
  - [Dependências](#dependncias)
  - [Estrutura de Arquivos](#estrutura-de-arquivos)
  - [Segurança e Robustez](#segurana-e-robustez)
- [Integração CI/CD](#integrao-cicd)
  - [GitHub Actions](#github-actions)
  - [GitLab CI](#gitlab-ci)
  - [Jenkins Pipeline](#jenkins-pipeline)
- [Resolução de Problemas](#resoluo-de-problemas)
  - [Problema: Script não encontra projetos](#problema-script-no-encontra-projetos)
  - [Problema: Backup falha](#problema-backup-falha)
  - [Problema: Ruff não disponível](#problema-ruff-no-disponvel)
  - [Problema: Rollback necessário](#problema-rollback-necessrio)
- [Desenvolvimento e Contribuição](#desenvolvimento-e-contribuio)
  - [Adicionando Novos Padrões](#adicionando-novos-padres)
  - [Melhorando Correções Automáticas](#melhorando-correes-automticas)
- [Histórico de Versões](#histrico-de-verses)
<!-- TOC END -->

## Visão Geral

O script `flext-constants.sh` é uma ferramenta unificada e avançada para garantia de qualidade de constantes no ecossistema FLEXT. Ele consolida todas as funcionalidades em um único script poderoso com infraestrutura de qualidade enterprise.

## Funcionalidades

### ✅ Validação de Conformidade de Constantes

- Detecção de valores hardcoded onde constantes deveriam ser usadas
- Validação de imports adequados (FlextConstants, [Project]Constants)
- Verificação de uso correto em diferentes contextos (src/, tests/, examples/)

### ✅ Detecção de Declarações Duplicadas

- Identificação de constantes declaradas múltiplas vezes
- Detecção de conflitos de nomes
- Análise de redundância e duplicação

### ✅ Validação de Padrões FLEXT

- Verificação de imports arquiteturais proibidos
- Detecção de uso direto de bibliotecas de infraestrutura
- Validação de separação de domínios

### ✅ Detecção de Uso Incorreto

- Identificação de padrões de uso problemáticos
- Detecção de aliases deprecated
- Validação de convenções de nomenclatura

### ✅ Infraestrutura de Qualidade

- **Check (padrão)**: Análise segura sem modificações
- **Fix**: Aplicação automática de correções com backup
- **Backup**: Criação de backup antes de mudanças
- **Restore**: Restauração em caso de problemas
- **Report**: Geração de relatórios abrangentes

## Uso

### Uso Básico (Recomendado)

```bash
# Verificar todos os projetos (seguro, sem mudanças)
./flext-constants.sh

# Verificar projeto específico
./flext-constants.sh flext-core
```

### Correção Automática

```bash
# Aplicar correções automáticas com backup
./flext-constants.sh flext-core --fix
```

### Operações Avançadas

```bash
# Criar backup manual
./flext-constants.sh flext-core --backup

# Restaurar backup
./flext-constants.sh flext-core --restore

# Gerar relatórios
./flext-constants.sh --report
```

## Exemplos Práticos

### 1. Workflow Completo para FLEXT-Core

```bash
./validate_constants_advanced.sh workflow flext-core
```

Este comando executará:

1. ✅ Verificação de pré-requisitos
2. ✅ Análise dry-run para identificar problemas
3. ✅ Criação de backup se necessário
4. ✅ Aplicação de correções automáticas
5. ✅ Validação final com Ruff
6. ✅ Geração de relatório abrangente

### 2. Análise Rápida de Todos os Projetos

```bash
./validate_constants_advanced.sh dry-run
```

### 3. Correção Automática com Backup

```bash
# Criar backup
./validate_constants_advanced.sh backup flext-api

# Aplicar correções
./validate_constants_advanced.sh exec flext-api

# Validar resultado
./validate_constants_advanced.sh validate flext-api
```

### 4. Recuperação de Emergência

```bash
# Se algo der errado, restaurar backup
./validate_constants_advanced.sh rollback flext-api
```

## Tipos de Violações Detectadas

### CONSTANTS - Violações de Conformidade

```
❌ Valores hardcoded encontrados
❌ Imports ausentes para constantes
❌ Uso incorreto de constantes em produção
```

### DUPLICATE - Declarações Duplicadas

```
❌ Constantes declaradas múltiplas vezes
❌ Conflitos de nomes
❌ Redundância desnecessária
```

### PATTERN - Violações de Padrões FLEXT

```
❌ Import direto de bibliotecas CLI (click, rich)
❌ Uso direto de bibliotecas HTTP (requests, httpx)
❌ Violação de camadas arquiteturais
```

### USAGE - Uso Incorreto

```
❌ Valores hardcoded onde constantes existem
❌ Uso de aliases deprecated ('c' em vez de FlextConstants)
❌ Padrões de uso inconsistentes
```

## Relatórios Gerados

Os scripts geram relatórios abrangentes em `reports/`:

- **Log detalhado**: `constants_validation_YYYYMMDD_HHMMSS.log`
- **Relatório de qualidade**: `constants_quality_report_YYYYMMDD_HHMMSS.md`
- **Sumário de workflow**: `workflow_summary_YYYYMMDD_HHMMSS.md`

## Infraestrutura Técnica

### Dependências

- **Ruff**: Para validação de qualidade de código (opcional)
- **Python 3**: Para execução de scripts auxiliares
- **Bash**: Shell compatível com POSIX

### Estrutura de Arquivos

```
scripts/
├── validate_constants_advanced.sh    # Script principal unificado
├── validate_constants_comprehensive.sh # Wrapper legacy
└── README_constants_quality.md       # Esta documentação

reports/                              # Relatórios gerados
├── constants_validation_*.log
├── constants_quality_report_*.md
└── workflow_summary_*.md

.constants_backup/                    # Backups automáticos
├── project_timestamp/
└── .last_backup_project
```

### Segurança e Robustez

- **Backup automático**: Antes de qualquer modificação
- **Rollback automático**: Em caso de falha
- **Dry-run seguro**: Análise sem risco
- **Validação rigorosa**: Múltiplas camadas de checagem
- **Logs abrangentes**: Rastreamento completo de ações

## Integração CI/CD

### GitHub Actions

```yaml
- name: Constants Quality Assurance
  run: |
    ./scripts/validate_constants_advanced.sh workflow ${{ matrix.project }}
```

### GitLab CI

```yaml
constants_quality:
  script:
    - ./scripts/validate_constants_advanced.sh workflow $PROJECT
```

### Jenkins Pipeline

```groovy
sh './scripts/validate_constants_advanced.sh workflow ${PROJECT}'
```

## Resolução de Problemas

### Problema: Script não encontra projetos

```
Solução: Verificar se está executando do diretório correto (raiz do workspace)
```

### Problema: Backup falha

```
Solução: Verificar permissões de escrita em .constants_backup/
```

### Problema: Ruff não disponível

```
Solução: Instalar ruff ou executar sem validação (--skip-ruff)
```

### Problema: Rollback necessário

```
Solução: ./validate_constants_advanced.sh rollback [project]
```

## Desenvolvimento e Contribuição

### Adicionando Novos Padrões

1. Adicionar padrões em `HARDCODED_PATTERNS` ou `FLEXT_PATTERNS`
2. Implementar função de validação em `validate_*_patterns()`
3. Adicionar mapeamentos em `CONSTANT_MAPPINGS`
4. Testar com dry-run

### Melhorando Correções Automáticas

1. Identificar padrões corrigíveis automaticamente
2. Implementar lógica em `apply_automatic_fixes()`
3. Adicionar validação pós-correção
4. Testar thoroughly com backup/rollback

## Histórico de Versões

- **v4.0.0**: Script unificado com workflow completo
- **v3.0.0**: Detecção avançada de duplicatas e padrões FLEXT
- **v2.0.0**: Infraestrutura de backup e rollback
- **v1.0.0**: Validação básica de constantes

---

_Documentação gerada automaticamente - FLEXT Quality Assurance v4.0.0_
