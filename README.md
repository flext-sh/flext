# FLEXT

Portifolio de 33 projetos de integracao de dados, revisados individualmente para orientar decisao tecnica e operacao.

## O que o repositorio consolida

- Bases arquiteturais para API, autenticacao, runtime, observabilidade e qualidade.
- Conectores Singer (taps e targets) para LDAP, LDIF, Oracle, OIC e WMS.
- Projetos dbt para publicacao de camada analitica por dominio.
- Solucoes operacionais dedicadas para cenarios de migracao e clientes.

## Projetos revisados caso a caso

| Projeto                   | Papel funcional no ecossistema                                                                                                                |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `algar-oud-mig`           | Ferramenta operacional para migracao LDAP/LDIF de Oracle Internet Directory (OID) para Oracle Unified Directory (OUD) com execucao por fases. |
| `flexcore`                | Runtime hibrido Go/Python para inicializacao de servicos e coordenacao operacional de componentes FLEXT.                                      |
| `flext-api`               | Camada de API HTTP para exposicao e consumo de servicos de dados no ecossistema FLEXT.                                                        |
| `flext-auth`              | Servico de autenticacao e autorizacao para controle de acesso entre APIs, CLIs e componentes FLEXT.                                           |
| `flext-cli`               | Framework de linha de comando para construir interfaces operacionais padronizadas no portfolio FLEXT.                                         |
| `flext-core`              | Base arquitetural compartilhada do ecossistema, com contratos, utilitarios e padroes transversais.                                            |
| `flext-db-oracle`         | Biblioteca de acesso Oracle para leitura, escrita e suporte de persistencia em pipelines de dados.                                            |
| `flext-dbt-ldap`          | Projeto dbt para transformar dados LDAP em modelos analiticos operacionais e de auditoria.                                                    |
| `flext-dbt-ldif`          | Projeto dbt para modelagem analitica de dados extraidos de arquivos LDIF.                                                                     |
| `flext-dbt-oracle`        | Projeto dbt para transformar dados Oracle em estruturas analiticas reutilizaveis.                                                             |
| `flext-dbt-oracle-wms`    | Projeto dbt especializado na transformacao de dados Oracle WMS para analise operacional logistica.                                            |
| `flext-grpc`              | Camada gRPC para comunicacao service-to-service de baixa latencia entre componentes FLEXT.                                                    |
| `flext-ldap`              | Biblioteca de operacoes LDAP para leitura, escrita e sincronizacao de identidades em diretorios corporativos.                                 |
| `flext-ldif`              | Biblioteca para parsing, validacao e transformacao de arquivos LDIF em fluxos de migracao de diretorio.                                       |
| `flext-meltano`           | Camada de orquestracao Singer/Meltano para coordenar extracao, carga e transformacao em pipelines FLEXT.                                      |
| `flext-observability`     | Componente de observabilidade para metricas, tracing e diagnostico operacional de servicos e pipelines.                                       |
| `flext-oracle-oic`        | Biblioteca de integracao com Oracle Integration Cloud para operacoes de conectividade e interoperabilidade.                                   |
| `flext-oracle-wms`        | Biblioteca de integracao com Oracle WMS para acesso a dados operacionais de armazem.                                                          |
| `flext-plugin`            | Sistema de plugins para extensao modular de funcionalidades sem alterar o nucleo da plataforma.                                               |
| `flext-quality`           | Camada de validacao tecnica para qualidade, conformidade e seguranca no ecossistema FLEXT.                                                    |
| `flext-tap-ldap`          | Singer Tap para extracao de dados de diretorios LDAP em pipelines de integracao.                                                              |
| `flext-tap-ldif`          | Singer Tap para extracao de dados a partir de arquivos LDIF.                                                                                  |
| `flext-tap-oracle`        | Singer Tap para extracao de dados de bancos Oracle para pipelines ELT.                                                                        |
| `flext-tap-oracle-oic`    | Singer Tap para extracao de entidades e dados de Oracle Integration Cloud.                                                                    |
| `flext-tap-oracle-wms`    | Singer Tap para extracao de dados operacionais de Oracle Warehouse Management System.                                                         |
| `flext-target-ldap`       | Singer Target para aplicacao de dados em destinos LDAP.                                                                                       |
| `flext-target-ldif`       | Singer Target para materializar saida de pipeline em formato LDIF.                                                                            |
| `flext-target-oracle`     | Singer Target para carga de dados em banco Oracle como destino final de pipeline.                                                             |
| `flext-target-oracle-oic` | Singer Target para enviar dados a recursos Oracle Integration Cloud.                                                                          |
| `flext-target-oracle-wms` | Singer Target para aplicar dados em Oracle WMS como destino operacional.                                                                      |
| `flext-web`               | Camada web para operacao e visualizacao das capacidades do ecossistema FLEXT.                                                                 |
| `gruponos-meltano-native` | Pipeline ETL Meltano dedicado ao contexto Grupo Nos, com foco operacional em cargas Oracle WMS.                                               |

## Estado atual do portfolio

- Qualidade global: **Alpha**
- Uso recomendado: **Nao produtivo**
- Aplicacao permitida: desenvolvimento, POC e homologacao controlada.

## Diretriz de governanca desta revisao

Cada README foi tratado individualmente com foco no que o projeto faz, no contexto operacional de uso e no risco atual de adocao.

## Repositorio oficial

Codigo-fonte e governanca: [github.com/flext-sh/flext](https://github.com/flext-sh/flext).
