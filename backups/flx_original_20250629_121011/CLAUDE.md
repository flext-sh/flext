# CLAUDE.md - FLX ORCHESTRATOR PROJECT

**Hierarquia**: PROJECT-SPECIFIC
**Projeto**: FLX Root Orchestrator - Hub de coordenação central
**Status**: IMPLEMENTAÇÃO PLANEJADA
**Última Atualização**: 2025-06-29

**Referência Global**: `/home/marlonsc/CLAUDE.md` → Princípios universais
**Referência Cross-workspace**: `/home/marlonsc/CLAUDE.local.md` → Issues temporários globais
**Referência Workspace**: `../CLAUDE.md` → Padrões PyAuto
**Referência Workspace-temp**: `../CLAUDE.local.md` → Issues temporários PyAuto
**Plano Mestre**: `../FLX_ORCHESTRATION_PLAN.md` → Plano detalhado de implementação

---

## 🎯 PROPÓSITO DO PROJETO

### **Missão**
Transformar o projeto raiz `flx/` em orquestrador central que coordena todos os módulos FLX extraídos de `flx-meltano-enterprise`.

### **Responsabilidades**
- **Coordenação**: Inicialização ordenada de todos os módulos FLX
- **Interface Unificada**: CLI e API centralizados para acesso a todos os módulos
- **Gerenciamento de Ciclo de Vida**: Start/stop coordenado de serviços
- **Configuração Central**: Gestão unificada de configurações e ambientes
- **Testes de Integração**: Validação do funcionamento conjunto dos módulos

---

## 📋 CONFIGURAÇÃO ESPECÍFICA DO PROJETO

### **Virtual Environment**
```bash
# OBRIGATÓRIO: Usar venv do workspace
source /home/marlonsc/pyauto/.venv/bin/activate
which python  # Deve retornar: /home/marlonsc/pyauto/.venv/bin/python
```

### **Coordenação de Agentes**
```bash
# Ler coordenação do workspace primeiro
cat /home/marlonsc/pyauto/.token | tail -5

# Coordenação específica do orquestrador
echo "FLX_ORCHESTRATOR_OPERATION_$(date)" >> .token
echo "PROJECT_CONTEXT=flx-orchestrator" >> .token
```

### **Environment Variables Específicas**
```bash
# Configurações do orquestrador (ver .env.example)
FLX_MODE=orchestrator
FLX_CONFIG_FILE=./config/orchestrator.yaml
FLX_MODULES_PATH=../

# Debug específico do orquestrador
FLX_ORCHESTRATOR_DEBUG=true
FLX_STARTUP_TIMEOUT=30
```

---

## 🏗️ ARQUITETURA DO ORQUESTRADOR

### **Módulos Coordenados**

| Módulo | Status | Dependências | Função |
|--------|--------|--------------|---------|
| flx-core | 95% | - | Fundação & Domain |
| flx-auth | 100% | flx-core | Autenticação |
| flx-api | 100% | flx-core, flx-auth | REST Gateway |
| flx-grpc | 100% | flx-core, flx-auth | gRPC Services |
| flx-web | 100% | flx-core, flx-auth | Django Dashboard |
| flx-cli | 95% | flx-core | CLI Interface |
| flx-plugin | 100% | flx-core | Plugin System |
| flx-observability | 100% | flx-core | Monitoring |
| flx-meltano | 100% | flx-core | ETL Integration |
| flx-database | Planejado | flx-core | DB Patterns |

### **Ordem de Inicialização**

1. **flx-core** → Carrega domain e infraestrutura base
2. **flx-observability** → Ativa métricas e tracing
3. **flx-auth** → Configura autenticação
4. **flx-plugin** → Descobre e carrega plugins
5. **flx-api + flx-grpc + flx-web** → Inicializa interfaces (paralelo)
6. **flx-cli** → CLI ativo para comandos
7. **flx-meltano** → ETL pipelines disponíveis

### **Comunicação Entre Módulos**

```python
# Event Bus centralizado (flx-core)
from flx_core.events import EventBus

# Cada módulo se registra no bus
event_bus.subscribe("auth.user_login", api_module.handle_user_login)
event_bus.subscribe("pipeline.completed", observability.record_pipeline_metrics)

# Orquestrador coordena através do bus
orchestrator.event_bus.publish("system.startup_complete", {
    "modules_loaded": loaded_modules,
    "timestamp": datetime.now()
})
```

---

## 🔧 COMANDOS ESPECÍFICOS DO PROJETO

### **Desenvolvimento Local**
```bash
# Preparação do ambiente
source /home/marlonsc/pyauto/.venv/bin/activate
cd /home/marlonsc/pyauto/flx

# Instalar dependências locais (develop mode)
poetry install

# Verificar imports
python -c "import flx; print(f'FLX v{flx.__version__} carregado')"

# Iniciar serviços de desenvolvimento
docker-compose up -d postgres redis prometheus
```

### **CLI Unificado**
```bash
# Status geral do sistema
python -m flx.cli status

# Iniciar orquestrador completo
python -m flx.cli start --debug

# Subcomandos dos módulos
python -m flx.cli core --help          # flx-cli commands
python -m flx.cli meltano --help       # flx-meltano commands
```

### **Testes de Integração**
```bash
# Testes entre módulos
pytest tests/integration/test_module_orchestration.py -v

# Teste completo de startup/shutdown
pytest tests/integration/test_full_lifecycle.py -v

# Performance de inicialização
pytest tests/integration/test_startup_performance.py -v
```

---

## 🔍 PROBLEMAS ESPECÍFICOS CONHECIDOS

### **Dependências Circulares**
**Issue**: Alguns módulos podem ter dependências circulares implícitas
**Workaround**: Usar dependency injection através do orquestrador
**Solução**: Interface abstratas em flx-core para quebrar dependências

### **Tempo de Inicialização**
**Issue**: Muitos módulos podem tornar startup lento
**Workaround**: Inicialização assíncrona e paralela quando possível
**Monitoring**: Métricas de tempo de startup por módulo

### **Conflitos de Configuração**
**Issue**: Módulos podem ter configurações conflitantes
**Workaround**: Namespace all configs by module (FLX_AUTH_*, FLX_API_*, etc.)
**Solution**: Validação central de configurações no bootstrap

---

## 📁 ESTRUTURA DE ARQUIVOS

```
flx/
├── CLAUDE.md                          # Este arquivo
├── pyproject.toml                     # Dependências de todos os módulos
├── .env.example                       # Template de configuração
├── docker-compose.yml                 # Serviços para desenvolvimento
├── README.md                          # Documentação pública
├── src/
│   └── flx/
│       ├── __init__.py                # Interface pública unificada
│       ├── orchestrator.py            # Coordenação central
│       ├── bootstrap.py               # Inicialização de módulos
│       ├── cli.py                     # CLI unificado
│       └── config/
│           ├── __init__.py
│           ├── orchestrator.py        # Config específica do orquestrador
│           └── validation.py          # Validação de configurações
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # Fixtures compartilhadas
│   ├── integration/
│   │   ├── test_module_loading.py     # Carregamento de módulos
│   │   ├── test_orchestration.py      # Coordenação
│   │   ├── test_cli_integration.py    # CLI unificado
│   │   └── test_full_lifecycle.py     # Ciclo completo
│   └── unit/
│       ├── test_orchestrator.py       # Testes unitários
│       └── test_bootstrap.py
└── docs/
    ├── README.md
    ├── architecture.md                # Arquitetura do orquestrador
    └── api/
        └── orchestrator.md            # API do orquestrador
```

---

## 🚨 PROTOCOLOS DE SEGURANÇA

### **Environment Variables**
```bash
# NUNCA modificar .env sem autorização explícita
# SEMPRE usar --debug para máxima transparência
python -m flx.cli start --debug --verbose

# Validar configuração antes de usar
python -c "
from flx.config import validate_orchestrator_config
try:
    validate_orchestrator_config()
    print('✅ Configuração válida')
except Exception as e:
    print(f'❌ Erro de configuração: {e}')
"
```

### **Backup Protocol**
```bash
# SEMPRE fazer backup antes de mudanças estruturais
cd /home/marlonsc/pyauto
tar -czf backups/flx_orchestrator_$(date +%Y%m%d_%H%M%S).tar.gz flx/

# Log todas as operações críticas
echo "ORCHESTRATOR_BACKUP_$(date)" >> .token
```

---

## 📊 MÉTRICAS DE SUCESSO

### **Indicadores Técnicos**
- ✅ Todos os módulos carregam sem erro
- ✅ Startup completo em < 30 segundos
- ✅ CLI responde a todos os comandos
- ✅ Testes de integração 100% passing
- ✅ Zero memory leaks durante operação

### **Indicadores Funcionais**
- ✅ Interface unificada funciona para todos os módulos
- ✅ Configuração centralizada gerencia todos os módulos
- ✅ Logs coordenados de todas as operações
- ✅ Shutdown graceful de todos os serviços
- ✅ Docker Compose sobe ambiente completo

---

## 🔄 WORKFLOW DE DESENVOLVIMENTO

### **Adição de Novo Módulo**
1. Adicionar dependência em `pyproject.toml`
2. Registrar no `orchestrator.py`
3. Adicionar ao CLI unificado
4. Criar testes de integração
5. Atualizar documentação

### **Debugging de Problemas**
```bash
# 1. Verificar status individual dos módulos
python -m flx.cli status

# 2. Logs detalhados de inicialização
python -m flx.cli start --debug --log-level=DEBUG

# 3. Testes específicos do módulo problemático
pytest tests/integration/test_module_loading.py::test_specific_module -v -s

# 4. Verificar dependências
poetry show --tree
```

### **Deploy e Atualizações**
```bash
# 1. Backup do estado atual
tar -czf backups/pre_update_$(date +%Y%m%d).tar.gz flx/

# 2. Atualizar dependências
poetry update

# 3. Validar mudanças
pytest tests/integration/ -v

# 4. Deploy coordenado
python -m flx.cli start --validate-only
python -m flx.cli start
```

---

## 📝 LIÇÕES APRENDIDAS DA MODULARIZAÇÃO

### **Sucessos da Modularização FLX-Meltano-Enterprise**
1. **Preservação de código**: 95% do código funcional foi mantido
2. **Boundaries naturais**: Identificação correta de limites entre módulos
3. **Import automation**: Script de atualização de imports foi crucial
4. **Arquitetura sólida**: Clean/DDD se manteve íntegra

### **Aplicação no Orquestrador**
1. **Não recriar**: Reutilizar interfaces e patterns já funcionais
2. **Coordenação leve**: Orquestrador como facilitador, não controlador
3. **Configuração central**: Mas execução distribuída
4. **Testes first**: Validação contínua de integrações

---

## 🎯 PRÓXIMOS PASSOS

### **Implementação Imediata**
1. [ ] Criar estrutura básica do projeto
2. [ ] Implementar orquestrador mínimo
3. [ ] CLI básico com status
4. [ ] Testes de carregamento de módulos

### **Médio Prazo**
1. [ ] Integração completa de todos os módulos
2. [ ] Docker Compose para desenvolvimento
3. [ ] Documentação completa da API
4. [ ] Performance tuning de startup

### **Longo Prazo**
1. [ ] Auto-discovery de novos módulos
2. [ ] Health checks automáticos
3. [ ] Deployment automatizado
4. [ ] Monitoring completo de toda a stack

---

**Authority**: Documentação específica do projeto orquestrador FLX
**Scope**: Coordenação e integração de todos os módulos FLX
**Status**: Implementação planejada com base no plano mestre
**Next**: Implementar estrutura básica seguindo FLX_ORCHESTRATION_PLAN.md