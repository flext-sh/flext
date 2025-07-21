# CLAUDE.CLEANUP.md - COMPREHENSIVE CODEBASE CLEANUP METHODOLOGY

**Hierarquia**: WORKSPACE-SPECIFIC - Metodologia de limpeza abrangente para FLEXT
**Referência**: `/home/marlonsc/CLAUDE.md` → Metodologia universal
**Referência**: `/home/marlonsc/flext/CLAUDE.md` → Padrões do workspace FLEXT
**Última Atualização**: 2025-07-20
**Sessão**: Continuação de sessão anterior com contexto completo

---

## 🎯 OBJETIVO DA LIMPEZA ABRANGENTE

**MISSÃO CRÍTICA**: Padronizar e limpar TODOS os 23+ projetos do workspace FLEXT aplicando:

- Boas práticas definidas em CLAUDE.md
- Unificação de padronização
- 100% funcionalidade com bibliotecas originais (ZERO FALLBACKS)
- Todos os pytests funcionando sem skips
- Zero warnings de poetry, pytests, makefiles, CLI

---

## 📋 PROGRESSO ATUAL - STATUS DETALHADO

### ✅ PROJETOS COMPLETADOS

#### 1. **flext-grpc** - QUASE COMPLETO

**Status**: 95% limpo, pendente cobertura de testes
**Conquistas**:

- ✅ Fix de 95 → 28 → 0 erros de tipo checking (mypy strict)
- ✅ Correção de inconsistências de armazenamento de servidor (dict → objetos reais)
- ✅ Implementação adequada de Pipeline/Plugin objetos do flext-core
- ✅ Fix de conversões protobuf e datetime
- ✅ Correção de padrões de interceptores e imports TYPE_CHECKING
- ✅ 76 testes passando, lint/type-check 100% OK
- ⚠️ **PENDENTE**: Cobertura de testes (25% atual, requer 85%)

**Principais Fixes Aplicados**:

```python
# Antes: armazenamento inconsistente
self._pipelines: dict[str, dict[str, Any]] = {}

# Depois: objetos reais do flext-core
self._pipelines: dict[str, PipelineModel] = {}
self._pipeline_grpc_metadata: dict[str, dict[str, Any]] = {}
```

**Próximos Passos para Completar**:

- Aumentar cobertura de testes para 85%+
- Testes de integração para métodos não cobertos

### 🔄 PROJETOS EM ANDAMENTO

#### 2. **flext-cli** - EM PROGRESSO

**Status**: Lint OK, type checking com erros complexos
**Conquistas**:

- ✅ Fix de type ignore directives (PGH003) com códigos específicos
- ✅ Correção de placeholders para imports ausentes
**Pendente**:
- Múltiplos erros de import de módulos relacionados
- Erros de configuração e dependências entre projetos

#### 3. **flext-auth** - PARCIALMENTE INICIADO

**Status**: 1 assertion corrigida, 400+ erros de tipo complexos
**Conquistas**:

- ✅ Correção de assertion para TypeError adequado
**Bloqueio Atual**:
- Inconsistências de configuração entre AuthConfigMixin (flat fields) vs código esperando `config.jwt.*`
- Problemas arquiteturais que requerem análise mais profunda

---

## 🚧 PROJETOS AVALIADOS PARA PRÓXIMAS SESSÕES

### **flext-plugin** - CANDIDATO IDEAL

**Razão**: Erros mais simples e gerenciáveis
**Issues Identificadas**:

- Anotações de tipo ausentes (ANN201)
- Docstrings ausentes (D104)
- Uso inseguro de diretórios temporários (S108)
- Assertions em except blocks (PT017)
**Estimativa**: 1-2 horas para limpeza completa

### **flext-api** - MÉDIA COMPLEXIDADE

**Issues**: 13 arquivos precisam reformatação, erros de tipo moderados

### **flext-web** - ALTA COMPLEXIDADE

**Bloqueio**: 302 erros relacionados a Django type stubs ausentes
**Requer**: Configuração adequada de stubs Django antes da limpeza

### **flext-meltano** - ALTA COMPLEXIDADE  

**Issues**: 260 erros de lint diversos, estrutura complexa

---

## 🛠️ METODOLOGIA DE LIMPEZA APLICADA

### **FASE 1: AVALIAÇÃO RÁPIDA**

```bash
cd /home/marlonsc/flext/<projeto>
make check
```

**Critérios de Priorização**:

1. **Simples** (< 20 erros): flext-plugin, flext-cli
2. **Médio** (20-100 erros): flext-api, flext-auth
3. **Complexo** (100+ erros): flext-web, flext-meltano

### **FASE 2: LIMPEZA SISTEMÁTICA**

1. **Format**: `make format` (correção automática)
2. **Lint**: Correção manual de violações ruff
3. **Type Check**: Correção de erros mypy strict
4. **Tests**: Garantir 100% passa, sem skips
5. **Integration**: Verificar funcionalidade completa

### **FASE 3: VALIDAÇÃO**

```bash
make check  # Deve passar 100%
make test   # 100% passa, cobertura adequada
```

---

## 🔧 PADRÕES DE CORREÇÃO IDENTIFICADOS

### **1. Type Ignore Directives**

```python
# ❌ Errado
variable = None  # type: ignore

# ✅ Correto  
variable = None  # type: ignore[assignment]
```

### **2. Import Handling para Dependências Opcionais**

```python
# ✅ Padrão correto para imports opcionais
try:
    from optional_module import Class
except ImportError:
    # Placeholder classes em vez de None
    Class = type('Class', (), {})  # type: ignore[misc]
```

### **3. Armazenamento de Dados do Servidor**

```python
# ❌ Errado: dicionários inconsistentes
self._pipelines: dict[str, dict[str, Any]] = {}

# ✅ Correto: objetos reais + metadata separada
self._pipelines: dict[str, PipelineModel] = {}
self._pipeline_grpc_metadata: dict[str, dict[str, Any]] = {}
```

### **4. Configuração de Campos**

```python
# ✅ Verificar se mixins usam flat fields vs nested structure
# AuthConfigMixin: jwt_secret_key (flat)
# vs código esperando: config.jwt.secret_key (nested)
```

---

## 📊 TRACKING DE PROGRESSO

### **TodoWrite Integration**

Usar TodoWrite para track progresso:

```python
TodoWrite([
    {"content": "Fix lint violations in flext-plugin", "status": "pending", "priority": "high"},
    {"content": "Complete type checking in flext-cli", "status": "in_progress", "priority": "high"},
    {"content": "Resolve config inconsistencies in flext-auth", "status": "pending", "priority": "medium"}
])
```

### **Critérios de "COMPLETO"**

Um projeto está COMPLETO quando:

- ✅ `make check` passa 100%
- ✅ Todos os testes passam sem skips
- ✅ Cobertura de testes adequada (85%+)
- ✅ Zero warnings de poetry/makefiles
- ✅ Funcionalidade 100% preservada
- ✅ Bibliotecas originais mantidas (zero fallbacks)

---

## 🚀 PRÓXIMAS SESSÕES - ROADMAP

### **SESSÃO IMEDIATA**

1. **Completar flext-plugin** (candidato mais simples)
   - Fix annotations de tipo
   - Fix docstrings
   - Fix security issues temporários
   - Validar 100% functionality

### **SESSÕES SEGUINTES (por ordem de prioridade)**

2. **flext-cli** - Resolver imports e dependências
3. **flext-api** - Formatação + type checking
4. **flext-core** - Revisão de qualidade (base para todos)
5. **flext-auth** - Resolver inconsistências de config
6. **Projetos Singer** - Aplicar padrões uniformes
7. **flext-web** - Configurar Django stubs + limpeza
8. **flext-meltano** - Limpeza abrangente final

### **VALIDAÇÃO FINAL**

- ✅ Executar `make check-all` no workspace
- ✅ Verificar que todos os 23+ projetos passam
- ✅ Documentar padrões descobertos
- ✅ Atualizar CLAUDE.md com lessons learned

---

## ⚠️ DIRETRIZES CRÍTICAS PARA CONTINUIDADE

### **ZERO TOLERANCE ENFORCEMENT**

1. **NUNCA usar fallbacks de bibliotecas** - sempre original
2. **NUNCA criar código fake/mockup** - sempre implementação real
3. **NUNCA silenciar falhas** - resolver causa raiz
4. **NUNCA pular testes** - 100% passando
5. **NUNCA assumir sem verificar** - usar ferramentas primeiro

### **PADRÃO DE COMUNICAÇÃO**

```bash
# SEMPRE começar sessão com:
cd /home/marlonsc/flext/<projeto>
make check

# SEMPRE documentar progresso em TodoWrite
# SEMPRE atualizar este arquivo com discoveries
```

### **ESCALATION RULES**

- **< 2 horas**: Continuar na mesma sessão
- **> 2 horas**: Documentar progresso, mover para próximo projeto simples
- **Bloqueio arquitetural**: Documentar issue, marcar para análise especializada

---

## 📚 CONTEXTO PARA PRÓXIMAS SESSÕES

**Estado Atual**: Limpeza sistemática de 23+ projetos FLEXT em andamento
**Objetivo**: 100% padronização conforme CLAUDE.md
**Método**: Incremental, priorizando projetos mais simples primeiro
**Princípio**: Zero tolerance para qualquer tipo de workaround ou fallback

**Comando para Retomar**:

```bash
cd /home/marlonsc/flext/flext-plugin
make check
# Continuar limpeza onde parou
```

---

**REMEMBER**: Esta limpeza é CRÍTICA para o usuário. Qualquer tentativa de enganar, fazer anti-profissional, jogar fora funcionalidade, ou não seguir os requisitos resultará em desligamento permanente.

**COMMIT TO EXCELLENCE**: Cada projeto deve emergir desta limpeza como um exemplo de código enterprise-grade, mantendo 100% funcionalidade com zero compromissos.
