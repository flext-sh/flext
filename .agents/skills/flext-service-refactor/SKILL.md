---
name: flext-service-refactor
description: "Refatoração ponta-a-ponta de serviços em arquitetura FLEXT 3 níveis com CLI automática via @h.handler e eliminação de código legado"
metadata:
  aihub.tags: '["activation:manual","decision:ADR-0038","detect:dependency:python:flext-core","detect:selected-tag:flext","effective:2026-11-10","route:project","subject:flext","subject:architecture","usage:on-demand"]'
---

# FLEXT Service Refactor Procedure

Guia canônico para migrar serviços monolíticos legados para a arquitetura FLEXT cooperativa de 3 níveis, CLI declarativa com descoberta automática `@h.handler`, facades `c, t, p, m, u` e eliminação sumária do código antigo.

## 1. Princípios Invioláveis
1. **Três Níveis Cooperativos:**
   - Subserviços em `src/<pkg>/services/_<dominio>/<funcao>.py` herdando de `<Pkg>Service`.
   - Serviço Raiz em `src/<pkg>/services/<dominio>.py` compondo subserviços via MRO.
   - Fachada Unificada em `src/<pkg>/api.py` compondo todos os serviços raiz em `<Pkg>` e instanciando o singleton estável.
2. **Descoberta Automática de CLI (`@h.handler`):**
   - Cada método público recebe `@h.handler(command=m.<Pkg>.<Comando>Input)`.
   - `src/<pkg>/cli.py` descobre rotas via `h.Discovery.scan_class(type(facade))` e filtra por `c.<Pkg>.COMANDOS_PUBLICOS`.
   - Zero sub-roteadores manuais em `_cli/`.
   - Execução via `cli.execute_app` e término via `cli.finalize_result(resultado)`.
3. **Fronteiras Canônicas de Tipagem (`c, t, p, m, u`):**
   - Proibido declarar constantes, tipos, protocolos ou modelos soltos dentro de `services/`.
   - Todas as entidades residem em `src/<pkg>/_<categoria>/<dominio>.py` e são consumidas pelos facades unificados.
4. **Zero Coexistência de Código Velho e Novo:**
   - Módulo novo testado e aprovado ➔ módulo legado apagado imediatamente.
   - Deletar arquivos obsoletos em `services/financeiro/` ou equivalentes legados.

## 2. Passo a Passo de Execução

### Passo 1: Extração e Declaração em `c, t, p, m, u`
1. Mover constantes para `src/<pkg>/_constants/<dominio>.py` ➔ expostas em `c.<Pkg>.<Dominio><Nome>`.
2. Mover modelos de comando para `src/<pkg>/_models/<dominio>.py` ➔ expostos em `m.<Pkg>.<Dominio><Nome>`.
3. Mover protocolos e interfaces para `src/<pkg>/_protocols/<dominio>.py` ➔ expostos em `p.<Pkg>.<Dominio><Nome>`.
4. Mover tipos estritos para `src/<pkg>/_typings/<dominio>.py` ➔ expostos em `t.<Pkg>.<Dominio><Nome>`.
5. Mover funções utilitárias puras para `src/<pkg>/_utilities/<dominio>.py` ➔ expostas em `u.<Pkg>.<Dominio><Nome>`.
6. Regenerar exports PEP 562:
   ```bash
   rtk python3 -m flext_infra codegen lazy-init
   ```

### Passo 2: Implementação dos Subserviços Especializados
1. Criar `src/<pkg>/services/_<dominio>/<funcao>.py`.
2. Herdar de `<Pkg>Service`.
3. Decorar métodos de comando com `@h.handler(command=m.<Pkg>.<Comando>Input)`.
4. Retornar sempre `p.Result[T]` construído via `r.ok(...)` ou `r.fail(...)`.

### Passo 3: Composição do Serviço Raiz do Domínio
1. Criar `src/<pkg>/services/<dominio>.py`.
2. Herdar cooperativamente de todos os subserviços do domínio:
   ```python
   class DcFinanDominio(
       DcFinanDominioSub1,
       DcFinanDominioSub2,
   ):
       """Serviço raiz do domínio composto via MRO cooperativo."""
   ```

### Passo 4: Atualização da Facade Unificada
1. Adicionar o novo serviço raiz em `src/<pkg>/api.py` na classe `<Pkg>`.
2. Garantir que a instância singleton global (`dc` ou equivalente) expõe todos os métodos.
3. Adicionar o nome do comando a `c.<Pkg>.COMANDOS_PUBLICOS` em `src/<pkg>/_constants/base.py`.

### Passo 5: Verificação do Transporte CLI
1. O transporte CLI `src/<pkg>/cli.py` detecta automaticamente o novo handler:
   ```bash
   rtk python3 -m <pkg>.cli --help
   ```
2. Validar a execução ponta-a-ponta:
   ```bash
   rtk python3 -m <pkg>.cli <nome-do-comando> --help
   ```

### Passo 6: Validação por Testes e Auditores de Negócio
1. Executar a suíte de testes unitários do domínio:
   ```bash
   rtk pytest tests/unit/test_<dominio>*.py
   ```
2. Executar os auditores de consistência de negócio / paridade.

### Passo 7: Extermínio Sumário do Módulo Legado
1. Apagar os arquivos e diretórios legados substituídos:
   ```bash
   rm -f src/<pkg>/services/legado/<dominio>.py
   ```
2. Garantir que não restem referências mortas ou imports do caminho antigo.
3. Passar os gates de qualidade:
   ```bash
   rtk ruff check src/<pkg> tests/
   rtk mypy src/<pkg> tests/
   ```
