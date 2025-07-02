# FLEXT Distributed Architecture

FLEXT agora suporta uma arquitetura distribuída completa com clusterização, paralelismo e agentes remotos. Esta implementação permite escalar horizontalmente e executar workloads em múltiplos nós.

## 🏗️ Arquitetura Distribuída

### Componentes Principais

1. **Cluster Manager** - Gerencia descoberta de nós e coordenação
2. **Worker Pool** - Pool de workers com auto-scaling para paralelismo
3. **Remote Agent** - Comunicação entre nós via WebSocket
4. **Coordinator** - Distribuição e coordenação de tarefas
5. **Service Discovery** - Descoberta automática de serviços
6. **Load Balancer** - Balanceamento de carga entre instâncias
7. **Distributed Metrics** - Métricas agregadas do cluster
8. **Distributed Tracing** - Rastreamento distribuído

### Funcionalidades

- ✅ **Clusterização Automática** - Nós se descobrem automaticamente
- ✅ **Paralelismo Avançado** - Worker pools com auto-scaling
- ✅ **Agentes Remotos** - Comunicação inter-nós via WebSocket
- ✅ **Coordenação Distribuída** - Distribuição inteligente de tarefas
- ✅ **Service Discovery** - Descoberta e registro automático de serviços
- ✅ **Load Balancing** - Múltiplas estratégias de balanceamento
- ✅ **Observabilidade** - Métricas, alertas e tracing distribuído
- ✅ **Leader Election** - Eleição automática de líder
- ✅ **Health Monitoring** - Monitoramento de saúde dos nós

## 🚀 Como Usar

### Modo Standalone (Padrão)

```bash
# Modo tradicional - single node
./flext

# Com arquivo de configuração
./flext -config config/standalone.yaml
```

### Modo Distribuído

```bash
# Habilita clusterização e recursos distribuídos
./flext -distributed

# Com configuração específica
./flext -distributed -config config/distributed.yaml
```

### Docker Compose - Cluster Completo

```bash
# Inicia cluster com 3 nós + infraestrutura
docker-compose -f docker-compose.distributed.yml up

# Escala para mais nós
docker-compose -f docker-compose.distributed.yml up --scale flext-node=5
```

## 🔧 Configuração

### Variáveis de Ambiente Distribuído

```bash
# Redis para coordenação
FLEXT_REDIS_ADDRESS=localhost:6379
FLEXT_REDIS_PASSWORD=""

# Worker Pool
FLEXT_MAX_WORKERS=20
FLEXT_MIN_WORKERS=5
FLEXT_QUEUE_SIZE=2000

# Capacidades do nó
FLEXT_NODE_CAPABILITIES=pipeline,plugin,meltano,singer
```

### Configuração YAML

Veja `config/distributed.yaml` para configuração completa.

## 📊 Endpoints da API Distribuída

### Cluster Management

```
GET /api/v1/cluster/nodes      # Lista todos os nós
GET /api/v1/cluster/status     # Status do cluster
GET /api/v1/cluster/leader     # Informações do líder
```

### Service Discovery

```
GET /api/v1/services           # Lista todos os serviços
GET /api/v1/services/{name}    # Instâncias de um serviço
GET /api/v1/services/{name}/url # URL com load balancing
```

### Distributed Tasks

```
POST /api/v1/tasks             # Submete tarefa distribuída
GET  /api/v1/tasks/{id}        # Status da tarefa
GET  /api/v1/tasks             # Lista todas as tarefas
```

### Métricas e Monitoramento

```
GET /api/v1/metrics/cluster    # Métricas do cluster
GET /api/v1/metrics/node/{id}  # Métricas de um nó
GET /api/v1/metrics/alerts     # Alertas ativos
```

### Comunicação entre Agentes

```
WS /agent/ws                   # WebSocket para comunicação inter-nós
```

## 🔄 Distribuição de Tarefas

### Estratégias de Sharding

- **none** - Execução em nó único
- **round_robin** - Distribuição rotativa
- **capability** - Baseado em capacidades do nó
- **load** - Baseado na carga atual

### Exemplo de Submissão

```json
{
  "type": "pipeline",
  "payload": {
    "pipeline_id": "uuid-here"
  },
  "priority": 5,
  "sharding": "load",
  "max_nodes": 3
}
```

## 📈 Observabilidade

### Métricas Disponíveis

- Nós do cluster (total, online, offline)
- Workers ativos e jobs em execução
- Conexões entre agentes
- Throughput e latência
- Utilização de recursos

### Alertas Configurados

- Taxa de erro alta (> 10%)
- CPU alto (> 80%)
- Memória baixa (< 20%)
- Nós offline
- Falhas de comunicação

### Dashboards

- **Prometheus**: <http://localhost:9090>
- **Grafana**: <http://localhost:3000> (REDACTED_LDAP_BIND_PASSWORD/REDACTED_LDAP_BIND_PASSWORD)
- **Jaeger**: <http://localhost:16686>
- **HAProxy Stats**: <http://localhost:8404/stats>

## 🏭 Arquitetura de Produção

### Requisitos Mínimos

- **Redis**: Para coordenação do cluster
- **PostgreSQL**: Para persistência (opcional)
- **Load Balancer**: HAProxy, Nginx ou AWS ALB
- **Monitoring**: Prometheus + Grafana

### Recomendações

- Mínimo 3 nós para alta disponibilidade
- Redis em cluster ou modo replicado
- PostgreSQL com replicação
- Monitoramento de saúde dos nós
- Backup automático dos dados

### Exemplo de Deploy

```yaml
# Kubernetes deployment exemplo
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flext-distributed
spec:
  replicas: 3
  template:
    spec:
      containers:
        - name: flext
          image: flext:2.0.0-distributed
          args: ["-distributed"]
          env:
            - name: FLEXT_REDIS_ADDRESS
              value: "redis-cluster:6379"
```

## 🛠️ Desenvolvimento

### Estrutura do Código

```
internal/infrastructure/
├── cluster/          # Gerenciamento de cluster
├── worker/           # Pool de workers
├── agent/            # Comunicação remota
├── coordination/     # Coordenação de tarefas
├── discovery/        # Service discovery
├── observability/    # Métricas distribuídas
└── distributed/      # Manager principal
```

### Adicionando Novos Handlers

```go
// Registrar handler de tarefa
coordinator.RegisterTaskHandler("my-task", &MyTaskHandler{})

// Registrar handler de job
workerPool.RegisterHandler("my-job", &MyJobHandler{})
```

### Testing Distribuído

```bash
# Testa comunicação entre nós
curl http://localhost:8081/api/v1/cluster/nodes

# Submete tarefa distribuída
curl -X POST http://localhost:8081/api/v1/tasks \
  -d '{"type":"pipeline","payload":{"pipeline_id":"test"}}'

# Verifica métricas
curl http://localhost:8081/api/v1/metrics/cluster
```

## 🔒 Segurança

- Comunicação WebSocket com validação de nó
- JWT para autenticação entre serviços
- TLS para comunicação externa
- Isolamento de recursos por nó
- Rate limiting por endpoint

## 📚 Comparação: Standalone vs Distribuído

| Recurso         | Standalone   | Distribuído   |
| --------------- | ------------ | ------------- |
| Escalabilidade  | Vertical     | Horizontal    |
| Disponibilidade | Single Point | Alta          |
| Paralelismo     | Thread pool  | Cluster-wide  |
| Coordenação     | Local        | Distribuída   |
| Observabilidade | Node-level   | Cluster-level |
| Complexidade    | Baixa        | Alta          |
| Latência        | Baixa        | Média         |
| Throughput      | Limitado     | Ilimitado     |

A arquitetura distribuída do FLEXT fornece uma base sólida para aplicações enterprise que precisam de alta disponibilidade, escalabilidade horizontal e processamento distribuído de workloads.
