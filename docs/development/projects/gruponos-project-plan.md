# Plano de Integração Técnica – Oracle WMS Cloud e Autonomous Database

## 1. Resumo Executivo

Este documento detalha a arquitetura, implementação e operação da integração entre
**Oracle Warehouse Management Cloud (WMS Cloud)** – versão 25A/25B – e o
**Oracle Autonomous Database (Autonomous DB)**, utilizando o **Oracle Integration Cloud (OIC)**
como plataforma de orquestração. O objetivo é estabelecer fluxos de dados confiáveis
e em tempo real entre o sistema de gerenciamento de armazém e o banco de dados autônomo,
garantindo visibilidade operacional e suporte à tomada de decisão.

Os principais benefícios de negócio incluem:

- Visibilidade em tempo real de pedidos e alocações
- Centralização de dados operacionais para análise e relatórios
- Automação de fluxos que anteriormente exigiam intervenção manual
- Base para integrações adicionais com sistemas corporativos

## 2. Índice

- [Plano de Integração Técnica – Oracle WMS Cloud e Autonomous Database](#plano-de-integração-técnica--oracle-wms-cloud-e-autonomous-database)
  - [1. Resumo Executivo](#1-resumo-executivo)
  - [2. Índice](#2-índice)
  - [3. Visão Geral do Projeto](#3-visão-geral-do-projeto)
    - [3.1 Objetivos](#31-objetivos)
    - [3.2 Escopo](#32-escopo)
      - [3.2.1 No Escopo](#321-no-escopo)
      - [3.2.2 Fora do Escopo](#322-fora-do-escopo)
    - [3.3 Stakeholders](#33-stakeholders)
  - [4. Arquitetura de Integração](#4-arquitetura-de-integração)
    - [4.1 Visão Geral da Arquitetura](#41-visão-geral-da-arquitetura)
    - [4.2 Componentes](#42-componentes)
      - [4.2.1 Oracle WMS Cloud 25A/25B](#421-oracle-wms-cloud-25a25b)
      - [4.2.2 Oracle Integration Cloud (OIC) v3](#422-oracle-integration-cloud-oic-v3)
      - [4.2.3 Oracle Autonomous Database](#423-oracle-autonomous-database)
    - [4.3 Fluxos de Dados](#43-fluxos-de-dados)
      - [4.3.1 Fluxo 1: Carga Inicial](#431-fluxo-1-carga-inicial)
      - [4.3.2 Fluxo 2: Pedidos (Orders)](#432-fluxo-2-pedidos-orders)
      - [4.3.3 Fluxo 3: Alocações de Estoque (Allocations)](#433-fluxo-3-alocações-de-estoque-allocations)
    - [4.4 Segurança e Conectividade](#44-segurança-e-conectividade)

## 3. Visão Geral do Projeto

### 3.1 Objetivos

Este projeto visa estabelecer uma integração completa entre o **Oracle WMS Cloud** e o
**Oracle Autonomous Database** para os seguintes fluxos críticos:

- **Sincronia de Pedidos:** Integrar pedidos de venda entre o WMS e o Autonomous DB,
contemplando cabeçalhos e detalhes (tabelas `order_hdr` e `order_dtl`), desde cargas
iniciais até processamento contínuo.

- **Rastreamento de Alocações:** Capturar e armazenar no Autonomous DB os eventos de
alocação de estoque gerados no WMS (reservas de itens para pedidos), possibilitando
visibilidade do atendimento de pedidos.

- **Orquestração via OIC:** Utilizar o Oracle Integration Cloud para receber, transformar
e transmitir os dados entre os sistemas, aplicando validações, tratamento de erros e
garantindo segurança nas conexões.

- **Atualização em Tempo Real:** Configurar Webhooks (interfaces de saída) no WMS Cloud
para acionar fluxos do OIC em tempo real quando eventos-chave ocorrerem, reduzindo
latência e evitando integrações puramente batch.

- **Persistência e Auditoria:** Modelar tabelas de stage no Autonomous DB que armazenem
os dados integrados com campos de auditoria, servindo como histórico e ponto de
recuperação em caso de falhas.

### 3.2 Escopo

#### 3.2.1 No Escopo

- Conexões entre WMS Cloud, OIC e Autonomous Database
- Integrações bidirecionais para pedidos (orders)
- Integração unidirecional para alocações (allocations)
- Fluxos de carga inicial e em tempo real
- Monitoramento e tratamento de erros
- Documentação técnica e operacional

#### 3.2.2 Fora do Escopo

- Integrações com outros sistemas além do WMS Cloud e Autonomous DB
- Transformações complexas de dados além das especificadas
- Desenvolvimento de aplicações de consumo dos dados (BI, dashboards)
- Migração de dados históricos anteriores à data de corte definida

### 3.3 Stakeholders

| Papel | Responsabilidade |
|-------|------------------|
| Equipe de Operações de Warehouse | Validação funcional, testes de aceitação, operação diária |
| Equipe de TI/Integração | Implementação, configuração, suporte técnico |
| Gestores de Negócio | Definição de requisitos, aprovação, análise de impacto |
| Oracle Support | Suporte à plataforma, resolução de problemas técnicos |

## 4. Arquitetura de Integração

### 4.1 Visão Geral da Arquitetura

A solução segue uma arquitetura híbrida de integração, combinando **cargas batch iniciais**
via arquivos CSV e **integrações event-driven** via webhooks/REST. O Oracle Integration
Cloud (OIC) atua como mediador central entre os sistemas.

```ascii
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Oracle WMS     │     │     Oracle      │     │   Oracle        │
│    Cloud        │◄───►│  Integration    │◄───►│   Autonomous    │
│ (v25A/25B)      │     │  Cloud (OIC)    │     │   Database      │
│                 │     │                 │     │                 │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
    ┌─────────┐            ┌─────────┐             ┌─────────┐
    │ Webhook │            │ REST API│             │ Views & │
    │ Output  │            │ Orchestr│             │ Stored  │
    │Interface│            │ ation   │             │ Procs   │
    └─────────┘            └─────────┘             └─────────┘
         │                       │                       │
         │                       │                       │
         └───────────┬───────────┘                       │
                     │                                   │
                     ▼                                   ▼
              ┌─────────────┐                     ┌─────────────┐
              │ SFTP/CSV    │                     │ Reporting & │
              │ Initial Load│                     │ Downstream  │
              └─────────────┘                     └─────────────┘
```

### 4.2 Componentes

#### 4.2.1 Oracle WMS Cloud 25A/25B

- Sistema fonte e destino de dados de operações de armazém
- Fornece eventos (alocações realizadas) via webhooks
- Recebe dados de entrada (novos pedidos) via API REST
- Oferece suporte a dois formatos de dados: XML e dados delimitados (CSV)
- Protocolos de integração: REST (HTTPS) e SFTP seguro

#### 4.2.2 Oracle Integration Cloud (OIC) v3

- Plataforma iPaaS que hospeda fluxos de integração
- Conexões adaptadoras para cada endpoint:
  - REST (para webhooks e APIs do WMS)
  - FTP (para arquivos CSV de carga inicial)
  - Oracle DB (para Autonomous Database)
- Orquestra transformações de dados (XML ↔ JSON ↔ tabela)
- Implementa tratamento de exceções e lógica de negócio

#### 4.2.3 Oracle Autonomous Database

- Repositório central dos dados integrados (ATP ou ADW)
- Armazena tabelas de estágio para dados recebidos do WMS
- Fornece views e procedures para transformação e consumo
- Conexão via JDBC segura (wallet) a partir do OIC

### 4.3 Fluxos de Dados

#### 4.3.1 Fluxo 1: Carga Inicial

- WMS Cloud exporta dados em arquivos CSV para servidor SFTP
- OIC lê, transforma e grava nas tabelas de stage do Autonomous DB
- Garante que o banco inicie populado com os registros atuais

#### 4.3.2 Fluxo 2: Pedidos (Orders)

- Integração bidirecional de pedidos de venda:
  - **Inbound para WMS:** Pedidos originados em sistemas externos são enviados via OIC para WMS
  - **Outbound do WMS:** Pedidos criados no WMS são enviados ao OIC via webhook e persistidos no DB

#### 4.3.3 Fluxo 3: Alocações de Estoque (Allocations)

- WMS aciona webhook ao realizar alocação de estoque
- OIC recebe evento e insere dados na tabela ALLOC_STAGE
- Fluxo unidirecional (WMS → DB) e em tempo real

### 4.4 Segurança e Conectividade

- Comunicação via HTTPS com autenticação (Basic Auth ou OAuth2)
- Transferências SFTP em canais cifrados
- Autonomous DB acessado via conexão direta com wallet e SSL
- Configuração de ADB com endpoint público e whitelisting de IPs do OIC

> **Nota**: A arquitetura combina o melhor de dois mundos: **batch** (para sincronismo de
> grande volume inicial) e **event-driven** (para delta em tempo real), usando padrões
> nativos do WMS Cloud e garantindo persistência confiável no Autonomous DB.
