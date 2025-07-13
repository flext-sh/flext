# FLEXT WORKSPACE - PLANO FINAL DE CORREÇÕES CRÍTICAS

**Status**: URGENTE - 18/23 projetos falhando quality checks
**Data**: 2025-07-13
**Objetivo**: Atingir 100% funcional SEM quebrar nada

---

## 🚨 SITUAÇÃO CRÍTICA ATUAL

### Falhas Identificadas:
- **18 projetos** falhando quality checks
- **flext-core**: Problema de formatação black (1 arquivo)
- **flext-api**: Linting issues (TRY300, D417, A002, FBT001, BLE001)
- **Outros projetos**: Status desconhecido mas falhando

### O que está funcionando:
- ✅ Build Go compilando (4 binários)
- ✅ Todos projetos têm `make check`
- ✅ Estrutura básica do workspace ok
- ✅ client-b-meltano-native testes passando

---

## 📋 PLANO DE AÇÃO DETALHADO

### FASE 1: CORREÇÕES IMEDIATAS (Hoje)

#### Task 1: Corrigir flext-core (MAIS CRÍTICO)
**Por quê**: É a base de todos os outros projetos

```bash
# 1. Aplicar formatação black
cd flext-core
black tests/config/test_validators_simple.py

# 2. Verificar se não quebrou nada
make test

# 3. Rodar check completo
make check
```

#### Task 2: Corrigir flext-api (CRÍTICO)
**Por quê**: Gateway principal do sistema

**Correções específicas**:
1. **TRY300**: Mover return para else block
2. **D417**: Adicionar descrição do argumento plugin_type
3. **A002**: Renomear argumento `type` para `plugin_type`
4. **FBT001**: Adicionar * antes de argumentos bool
5. **BLE001**: Especificar exceção em vez de Exception genérico

#### Task 3: Verificar projetos Singer/Meltano
**Por quê**: Muitos estão falhando e são críticos para ETL

```bash
# Para cada projeto tap/target:
cd flext-tap-ldap
make lint 2>&1 | head -20  # Ver erros específicos
make test  # Verificar se testes passam
```

### FASE 2: ESTABILIZAÇÃO (Esta semana)

#### Task 4: Criar script de diagnóstico
**NÃO automatizado**, apenas informativo:

```bash
#!/bin/bash
# diagnostic.sh - NÃO FAZ CORREÇÕES, APENAS REPORTA

echo "=== FLEXT Workspace Diagnostic ==="
for project in */; do
    if [ -f "$project/Makefile" ]; then
        echo "\n📦 $project"
        cd "$project"
        
        # Contar erros de lint
        lint_errors=$(make lint 2>&1 | grep -E "^[^ ]" | wc -l)
        echo "  Lint errors: $lint_errors"
        
        # Verificar se testes passam
        if make test > /dev/null 2>&1; then
            echo "  Tests: ✅ PASS"
        else
            echo "  Tests: ❌ FAIL"
        fi
        
        cd ..
    fi
done
```

#### Task 5: Priorizar correções por impacto
**Ordem de prioridade**:

1. **flext-core** - Base de tudo
2. **flext-auth** - Segurança crítica  
3. **flext-api** - Gateway principal
4. **flext-grpc** - Comunicação entre serviços
5. **flext-web** - Interface usuário
6. **Projetos Singer** - ETL pipeline
7. **Outros** - Menos críticos

### FASE 3: QUALIDADE INCREMENTAL

#### Task 6: Aplicar correções graduais
**Por categoria, NÃO por projeto**:

1. **Formatação** (safe, automated):
   - black em todos os projetos
   - isort para imports

2. **Documentação** (manual, careful):
   - Adicionar docstrings faltantes
   - Corrigir argumentos não documentados

3. **Type hints** (manual, test after):
   - Adicionar tipos faltantes
   - Resolver mypy errors

4. **Segurança** (manual, critical):
   - Substituir Exception genérico
   - Remover hardcoded passwords

---

## 🎯 MÉTRICAS DE SUCESSO

### Hoje:
- [ ] flext-core passando `make check`
- [ ] flext-api com <10 erros de lint
- [ ] Diagnóstico completo de todos projetos

### Esta semana:
- [ ] 10+ projetos passando quality checks
- [ ] Nenhuma funcionalidade quebrada
- [ ] Todos os testes continuam passando

### Próxima semana:
- [ ] 20+ projetos passando quality checks
- [ ] Documentação atualizada
- [ ] CI/CD pipeline funcional

---

## ⚠️ REGRAS ABSOLUTAS

1. **TESTAR APÓS CADA MUDANÇA**
2. **COMMIT FREQUENTE** de estados funcionais
3. **NUNCA** corrigir todos os erros de uma vez
4. **NUNCA** usar --fix em massa
5. **SEMPRE** verificar diff antes de commit

---

## 📝 CHECKLIST DIÁRIO

### Manhã:
- [ ] Rodar `make check-all` para baseline
- [ ] Escolher 1-2 projetos críticos
- [ ] Criar branch para correções

### Durante trabalho:
- [ ] Corrigir por categoria (não por projeto)
- [ ] Testar após cada correção
- [ ] Documentar problemas encontrados

### Final do dia:
- [ ] Rodar `make check-all` novamente
- [ ] Comparar com baseline da manhã
- [ ] Commit apenas código funcional

---

## 🚀 PRÓXIMOS PASSOS IMEDIATOS

1. **Corrigir flext-core** (1 arquivo, formatação)
2. **Diagnosticar todos os projetos** (script informativo)
3. **Criar plano específico** por projeto baseado no diagnóstico
4. **Executar correções** uma por vez, com testes

---

**LEMBRE-SE**: 
- Código funcionando com avisos > Código quebrado sem avisos
- Progresso incremental > Perfeição imediata
- Documentar tudo > Assumir conhecimento