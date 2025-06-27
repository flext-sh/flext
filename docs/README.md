# 📚 **LDAP Documentation Hub**

> **Centro de conhecimento completo sobre LDAP/LDIF/Schema com 86+ RFCs organizados e 57+ implementações de referência**

[![RFCs](https://img.shields.io/badge/RFCs-86%2B-blue)](.)
[![Implementations](https://img.shields.io/badge/Implementations-57%2B-green)](reference/)
[![Languages](https://img.shields.io/badge/Languages-12%2B-orange)](reference/)
[![Schemas](https://img.shields.io/badge/Schemas-146%2B-purple)](reference/schemas-collection/)

---

## 🎯 **Navegação Rápida**

### **🚀 Para Começar Agora**

| **Objetivo**               | **Recurso**                                        | **Tempo** |
| -------------------------- | -------------------------------------------------- | --------- |
| **📖 Aprender LDAP**       | [Core Specs (RFC 4510-4519)](#core-specs)          | 2-3 horas |
| **🔧 Implementar Cliente** | [Python: ldap3](reference/#python-implementations) | 30 min    |
| **🖥️ Interface Gráfica**   | [Apache Directory Studio](reference/#gui-tools)    | 15 min    |
| **🌐 Interface Web**       | [phpLDAPadmin](reference/#web-interfaces)          | 10 min    |
| **📋 Validar Schemas**     | [Schema Validators](reference/#validation-tools)   | 5 min     |

### **🗺️ Mapa do Conhecimento**

```
📁 docs/
├── 🎯 PARA INICIANTES
│   ├── 📖 core-specs/          # RFCs 4510-4519 (LDAP v3 base)
│   ├── 💡 informational/       # Guias e melhores práticas
│   └── 🔧 reference/python/    # Cliente Python simples
│
├── 👨‍💻 PARA DESENVOLVEDORES
│   ├── 🔌 controls-extensions/ # RFCs de controles/extensões
│   ├── 📋 schema/              # RFCs de schemas/definições
│   └── 🗂️ reference/          # 57+ implementações reais
│
└── 🏢 PARA ADMINISTRADORES
    ├── 🖥️ reference/gui-tools/  # Interfaces gráficas
    ├── 🌐 reference/web-tools/  # Interfaces web
    └── 🔧 reference/cli-tools/  # Ferramentas linha de comando
```

---

## 📖 **Coleção de RFCs Organizados**

Esta é uma **coleção completa e categorizada de RFCs LDAP**, desde as especificações core até extensões experimentais.

### 🏗️ **Core Specifications** <a id="core-specs"></a>

**📁 [`core-specs/`](core-specs/)** - A base fundamental do LDAP v3

| RFC  | Nome                                                              | Descrição                                      | Prioridade |
| ---- | ----------------------------------------------------------------- | ---------------------------------------------- | ---------- |
| 4510 | Technical Specification Road Map                                  | 🗺️ Visão geral e roteiro da especificação LDAP | ⭐⭐⭐     |
| 4511 | The Protocol                                                      | 🔌 Protocolo LDAP core                         | ⭐⭐⭐     |
| 4512 | Directory Information Models                                      | 📊 Modelos de informação do diretório          | ⭐⭐⭐     |
| 4513 | Authentication Methods and Security Mechanisms                    | 🔐 Autenticação e segurança                    | ⭐⭐⭐     |
| 4514 | The Distinguished Name (DN) and Relative Distinguished Name (RDN) | 🏷️ Nomes distinguidos                          | ⭐⭐⭐     |
| 4515 | String Representation of Search Filters                           | 🔍 Filtros de busca                            | ⭐⭐⭐     |
| 4516 | Internationalized String Preparation                              | 🌍 Strings internacionais                      | ⭐⭐       |
| 4517 | Syntaxes and Matching Rules                                       | 📝 Sintaxes e regras                           | ⭐⭐⭐     |
| 4518 | String Representation of Distinguished Names                      | 📋 Representação de DNs                        | ⭐⭐⭐     |
| 4519 | Schema for User Applications                                      | 👤 Schema para aplicações                      | ⭐⭐⭐     |

### 🔌 **Controls & Extensions**

**📁 [`controls-extensions/`](controls-extensions/)** - Controles LDAP e extensões do protocolo

<details>
<summary><b>📋 18 RFCs de Controles e Extensões</b></summary>

| RFC  | Nome                                                   | Tipo      | Casos de Uso              |
| ---- | ------------------------------------------------------ | --------- | ------------------------- |
| 2589 | LDAPv3: Extensions for Dynamic Directory Services      | Extension | Diretórios dinâmicos      |
| 2696 | LDAP Control Extension for Simple Paged Results        | Control   | Paginação de resultados   |
| 2891 | LDAP Control Extension for Server Side Sorting         | Control   | Ordenação server-side     |
| 3062 | LDAP Password Modify Extended Operation                | Extension | Modificação de senhas     |
| 3296 | Named Subordinate References in LDAP                   | Extension | Referências subordinadas  |
| 3671 | Collective Attributes in LDAP                          | Extension | Atributos coletivos       |
| 3672 | Subentries in LDAP                                     | Extension | Sub-entradas              |
| 3829 | LDAPv3: Schema Definitions for LDAP Control Extensions | Schema    | Definições de controles   |
| 3876 | Returning Matched Values with LDAP Search              | Control   | Valores correspondentes   |
| 3909 | Cancel Operation for LDAP                              | Extension | Cancelamento de operações |
| 4370 | LDAP Proxied Authorization Control                     | Control   | Autorização por proxy     |
| 4527 | LDAP Read Entry Controls                               | Control   | Controles de leitura      |
| 4528 | LDAP Assertion Control                                 | Control   | Controles de asserção     |
| 4531 | LDAP Turn Operation                                    | Extension | Operação Turn             |
| 4532 | LDAP "Who am I?" Operation                             | Extension | Identificação do usuário  |
| 4533 | The LDAP Content Synchronization Operation             | Extension | Sincronização de conteúdo |
| 5805 | LDAP Transactions                                      | Extension | Transações LDAP           |
| 6171 | The LDAP Don't Use Copy Control                        | Control   | Controle "não usar cópia" |

</details>

### 📋 **Schema Definitions**

**📁 [`schema/`](schema/)** - RFCs sobre schemas, atributos e classes de objetos

<details>
<summary><b>📊 11 RFCs de Schema</b></summary>

| RFC  | Nome                                                         | Foco               | Importância |
| ---- | ------------------------------------------------------------ | ------------------ | ----------- |
| 2247 | Using Domains in LDAP/X.500 Distinguished Names              | Domain Components  | ⭐⭐⭐      |
| 2798 | Definition of the inetOrgPerson LDAP Object Class            | inetOrgPerson      | ⭐⭐⭐      |
| 2926 | Conversion of LDAP Schemas to and from SLP Service Templates | Schema Conversion  | ⭐⭐        |
| 3045 | Storing Vendor Information in the LDAP root DSE              | Vendor Info        | ⭐⭐        |
| 3112 | LDAP Authentication Password Schema                          | Password Schema    | ⭐⭐⭐      |
| 3687 | LDAP Component Matching Rules                                | Component Matching | ⭐⭐        |
| 3698 | LDAP: Additional Matching Rules                              | Additional Rules   | ⭐⭐        |
| 4523 | Anonymous LDAP                                               | Anonymous Access   | ⭐⭐        |
| 4524 | COSINE LDAP/X.500 Schema                                     | COSINE Schema      | ⭐⭐⭐      |
| 4530 | LDAP entryUUID Operational Attribute                         | Entry UUID         | ⭐⭐        |
| 5020 | LDAP entryDN Operational Attribute                           | Entry DN           | ⭐⭐        |

</details>

### 💡 **Informational & Best Practices**

**📁 [`informational/`](informational/)** - Guias, melhores práticas e documentação educacional

<details>
<summary><b>📖 20 RFCs Informativos</b></summary>

| RFC  | Nome                                                                                                             | Categoria          | Audiência       |
| ---- | ---------------------------------------------------------------------------------------------------------------- | ------------------ | --------------- |
| 1823 | The LDAP Application Program Interface                                                                           | API Guide          | Desenvolvedores |
| 2079 | Definition of an X.500 Attribute Type and an Object Class to Hold Uniform Resource Identifiers                   | URI Attributes     | Administradores |
| 2307 | An Approach for Using LDAP as a Network Information Service                                                      | NIS Integration    | Administradores |
| 2377 | Naming Plan for Internet Directory-Enabled Applications                                                          | Naming Plans       | Arquitetos      |
| 2649 | An LDAP Control and Schema for Holding Operation Signatures                                                      | Digital Signatures | Segurança       |
| 2713 | Schema for Representing Java(tm) Objects in an LDAP Directory                                                    | Java Objects       | Desenvolvedores |
| 2714 | Schema for Representing CORBA Object References in an LDAP Directory                                             | CORBA Integration  | Enterprise      |
| 2739 | Calendar Attributes for vCard and LDAP                                                                           | Calendar Schema    | Aplicações      |
| 2820 | Access Control Requirements for LDAP                                                                             | Access Control     | Segurança       |
| 2849 | The LDAP Data Interchange Format (LDIF) - Technical Specification                                                | LDIF Spec          | ⭐⭐⭐ Todos    |
| 3384 | Lightweight Directory Access Protocol (version 3) Replication Requirements                                       | Replication        | Administradores |
| 3494 | Lightweight Directory Access Protocol version 2 (LDAPv2) to Historic status                                      | LDAPv2 Historic    | Histórico       |
| 3703 | Policy Core LDAP Schema                                                                                          | Policy Schema      | Enterprise      |
| 4403 | Lightweight Directory Access Protocol (LDAP) Schema for Universal Description, Discovery, and Integration (UDDI) | UDDI Schema        | Web Services    |
| 4520 | Internet Assigned Numbers Authority (IANA) Considerations for LDAP                                               | IANA Registry      | Padronização    |
| 4521 | Considerations for LDAP Extensions                                                                               | Extension Design   | Desenvolvedores |
| 4525 | LDAP: Procedures for Requesting IANA Assignments                                                                 | IANA Procedures    | Padronização    |
| 4529 | Requesting Attributes by Object Class in LDAP                                                                    | Attribute Requests | Desenvolvedores |
| 4876 | A Configuration Profile Schema for Lightweight Directory Access Protocol (LDAP)-Based Agents                     | Config Profiles    | Administradores |
| 5803 | LDAP Schema for Storing Salted Challenge Response Authentication Mechanism (SCRAM) Secrets                       | SCRAM Auth         | Segurança       |

</details>

### 🧪 **Experimental**

**📁 [`experimental/`](experimental/)** - RFCs experimentais e propostas

| RFC  | Nome                                                | Status       | Descrição                        |
| ---- | --------------------------------------------------- | ------------ | -------------------------------- |
| 3088 | OpenLDAP Root Service                               | Experimental | Serviço raiz OpenLDAP            |
| 3663 | Domain Administrative Data in LDAP                  | Experimental | Dados administrativos de domínio |
| 4373 | LBURP: Lightweight Bulk Update/Replication Protocol | Experimental | Protocolo de atualização em lote |

---

## 🗂️ **Implementações de Referência**

### **📁 [`reference/`](reference/)** - 57+ Implementações Reais

A pasta `reference/` contém uma **coleção curada das melhores implementações LDAP** em diversas linguagens e ferramentas.

#### **🐍 Python Implementations**

```bash
reference/
├── ldap3-python-client/          # ⭐ Recomendado: Biblioteca moderna RFC-compliant
├── python-ldap-source/           # Wrapper para OpenLDAP C libraries
└── python3-ldap-fork/           # Fork Python 3 específico
```

#### **☕ Java Implementations**

```bash
reference/
├── apache-ldap-api/              # ⭐ Apache Directory LDAP API
└── unboundid-ldap-sdk/          # UnboundID LDAP SDK (comercial/open)
```

#### **🦀 Rust & Modern Languages**

```bash
reference/
├── lldap-light-implementation/   # ⭐ LLDAP: Implementação leve em Rust
├── go-ldap-source/              # Cliente Go
├── nodejs-ldapjs/               # Node.js LDAPjs
└── ruby-ldap-source/            # Ruby Net::LDAP
```

#### **🖥️ GUI Tools**

```bash
reference/
├── apache-directory-studio-source/  # ⭐ Eclipse-based LDAP browser
├── jxplorer-source/                 # Java LDAP explorer
└── alasca-ldap-schema-editor/       # Editor de schemas
```

#### **🌐 Web Interfaces**

```bash
reference/
├── phpldapadmin-web-interface/      # ⭐ Interface web PHP clássica
├── ldap-ui-minimalist-web/          # UI web minimalista
└── ltb-*/                           # LDAP Tool Box (self-service, etc.)
```

#### **🔧 CLI & Validation Tools**

```bash
reference/
├── openldap-source/                 # ⭐ OpenLDAP completo (ldapsearch, etc.)
├── ldap-schema-lint/                # Validador de schemas
├── openldap-config-parser/          # Parser de configuração
└── ldaptools-minimalist/            # Ferramentas minimalistas
```

#### **📋 Schemas & Standards**

```bash
reference/
├── schemas-collection/              # ⭐ 146+ schemas OpenLDAP padrão
├── ldap-hub-schemas/                # Schemas formatados ldap-hub
├── fusiondirectory-schemas/         # Schemas FusionDirectory
└── oidplus-oid-registry/            # Sistema de registro OID
```

---

## 🎯 **Guias de Uso Por Cenário**

### **🔰 Cenário 1: "Sou novo em LDAP"**

```bash
# 1. Comece com a teoria
cd docs/core-specs/
cat rfc4510.txt  # Road map geral

# 2. Entenda o protocolo
cat rfc4511.txt  # Protocolo base

# 3. Veja um cliente simples
cd ../reference/ldap3-python-client/
# Explore examples/ e documentação
```

### **👨‍💻 Cenário 2: "Preciso implementar um cliente"**

```bash
# Python (recomendado)
cd reference/ldap3-python-client/
# Veja examples/ para começar rapidamente

# Java Enterprise
cd reference/apache-ldap-api/
# Documentação completa disponível

# Rust (performance)
cd reference/lldap-light-implementation/
# Implementação moderna e eficiente
```

### **🏢 Cenário 3: "Preciso administrar um servidor LDAP"**

```bash
# Interface gráfica completa
cd reference/apache-directory-studio-source/
# Eclipse-based, muito completo

# Interface web simples
cd reference/phpldapadmin-web-interface/
# Deploy rápido via Docker

# Linha de comando
cd reference/openldap-source/
# ldapsearch, ldapmodify, etc.
```

### **🔍 Cenário 4: "Preciso validar schemas"**

```bash
# Validator Python
cd reference/ldap-schema-lint/

# Schemas padrão de referência
cd reference/schemas-collection/
ls *.schema  # 146+ schemas oficiais

# RFCs sobre schemas
cd ../schema/
# Consulte RFCs 4517, 4519, etc.
```

### **🗂️ Cenário 5: "Preciso processar LDIF"**

```bash
# Parser Python moderno
cd reference/ldif-python-parser/

# Conversor C high-performance
cd reference/ldif-csv-c/

# RFC oficial LDIF
cd ../informational/
cat rfc2849.txt  # Especificação LDIF oficial
```

---

## 📊 **Estatísticas da Coleção**

### **🎯 Por Números**

- **📖 RFCs**: 86 documentos organizados em 5 categorias
- **🔧 Implementações**: 57 projetos de código fonte
- **🐍 Python**: 2.263 arquivos de implementações
- **📋 Schemas**: 146 schemas OpenLDAP padrão
- **🌐 Linguagens**: 12+ linguagens representadas
- **📦 Projetos**: De startups a enterprise (Apache, Microsoft, etc.)

### **🏆 Quality Score**

- ✅ **Projetos Ativos**: Mantidos e atualizados
- ✅ **RFC Compliance**: Seguem padrões oficiais
- ✅ **Documentação**: Bem documentados
- ✅ **Comunidade**: Amplamente utilizados
- ✅ **Licenças**: Open source verificadas

---

## 🚀 **Próximos Passos**

### **📚 Para Estudar**

1. **Básico**: [`core-specs/rfc4510.txt`](core-specs/rfc4510.txt) - Road map LDAP
2. **Protocolo**: [`core-specs/rfc4511.txt`](core-specs/rfc4511.txt) - Protocolo core
3. **Schemas**: [`schema/rfc4519.txt`](schema/rfc4519.txt) - Schema básico
4. **LDIF**: [`informational/rfc2849.txt`](informational/rfc2849.txt) - Formato LDIF

### **🔧 Para Implementar**

1. **Python**: [`reference/ldap3-python-client/`](reference/ldap3-python-client/)
2. **Java**: [`reference/apache-ldap-api/`](reference/apache-ldap-api/)
3. **Rust**: [`reference/lldap-light-implementation/`](reference/lldap-light-implementation/)
4. **Web**: [`reference/phpldapadmin-web-interface/`](reference/phpldapadmin-web-interface/)

### **🏢 Para Administrar**

1. **GUI**: [`reference/apache-directory-studio-source/`](reference/apache-directory-studio-source/)
2. **CLI**: [`reference/openldap-source/`](reference/openldap-source/)
3. **Web**: [`reference/phpldapadmin-web-interface/`](reference/phpldapadmin-web-interface/)
4. **Schemas**: [`reference/schemas-collection/`](reference/schemas-collection/)

---

## 🔗 **Links Rápidos**

- 📄 [**README Principal**](../README.md) - Visão geral do projeto
- 🔧 [**Implementações**](reference/README.md) - Guia das implementações
- 📊 [**Resumo Executivo**](reference/FINAL-SUMMARY.md) - Estatísticas completas
- 🌍 [**RFC Editor**](https://www.rfc-editor.org/) - Fonte oficial dos RFCs

---

<div align="center">

**🏛️ Centro de Conhecimento LDAP Definitivo**

_Documentação completa • Implementações reais • Padrões oficiais_

[⬆️ Voltar ao topo](#-ldap-documentation-hub) | [📁 Estrutura Completa](../README.md#-estrutura-detalhada)

</div>
