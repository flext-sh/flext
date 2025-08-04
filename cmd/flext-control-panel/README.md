# FLEXT Control Panel

**FLEXT Control Panel** é o serviço central de gerenciamento e monitoramento do ecossistema FLEXT. Ele coordena e monitora instâncias distribuídas do **FlexCore Runtime** através de APIs gRPC e fornece interfaces REST e CLI para gerenciamento.

## Arquitetura

```
FLEXT Control Panel (Porta 8081)
    ├── Management: Gerencia instâncias FlexCore  
    ├── Monitoring: Monitora saúde e métricas
    ├── Configuration: Gerencia configurações
    └── Coordination: Coordena múltiplas instâncias
                ↓ (gRPC)
FlexCore Runtime (Porta 8080)
    └── Executa workflows via Windmill
```

## Responsabilidades

### 🎯 Control Panel (Este Serviço)

- **NÃO executa** runtimes diretamente
- **Gerencia** instâncias FlexCore (start/stop/configure)
- **Monitora** saúde, performance, logs
- **Coordena** orchestração multi-FlexCore
- **Fornece** APIs REST, Dashboard, CLI

### 🚀 FlexCore Runtime (Projeto Separado)

- **Executa** todos os runtimes via workflows Windmill
- **Runtimes disponíveis**:
  - ✅ Meltano (via flext-core/flext-meltano) - **IMPLEMENTADO**
  - 📝 Ray (via flext-core/flext-ray) - **STUB/DOC**
  - 📝 Kubernetes - **STUB/DOC**
  - 🔮 Outros runtimes - **EXPANSÃO FUTURA**

## Executando

```bash
# Iniciar Control Panel (porta 8081)
./flext-control-panel --port 8081 --env development

# FlexCore deve estar rodando em separado (porta 8080)
# Ver: flexcore/README.md para instruções
```

## Endpoints API

```bash
# Health checks
GET /health                     # Status do Control Panel
GET /api/v1/flexcore/health    # Status das instâncias FlexCore

# Gerenciamento
GET /api/v1/plugins            # Plugins disponíveis
GET /api/v1/meltano/projects   # Projetos Meltano
GET /api/v1/singer/taps        # Singer taps
GET /api/v1/dbt/models         # Modelos DBT
```

## Arquitetura Interna

```
pkg/controlpanel/
├── management/        # Gerencia instâncias FlexCore + DI container
├── monitoring/        # APIs de monitoramento + servidor HTTP
├── configuration/     # Gerenciamento de configurações  
└── coordination/      # Coordenação multi-instância
```

## Diferenças da Arquitetura Anterior

**ANTES (Incorreto)**:

- FLEXT executava runtimes diretamente
- Mistura de responsabilidades
- Runtime e controle no mesmo processo

**AGORA (Correto)**:

- **FLEXT Control Panel**: Puro controle e coordenação
- **FlexCore Runtime**: Pura execução via Windmill
- **Separação clara** de responsabilidades
- **Comunicação gRPC** entre Control Panel ↔ FlexCore

## Próximos Passos

1. ✅ **Control Panel funcional** - Compilando e estruturado
2. 🔄 **Integração gRPC** - Comunicação com FlexCore
3. 📊 **Dashboard Web** - Interface de monitoramento
4. 🔧 **CLI avançado** - Comandos de gerenciamento
5. 📈 **Métricas avançadas** - Observabilidade completa
