# 📋 **OpenLDAP Schema Collection**

> **Coleção completa de 146+ schemas OpenLDAP oficiais e customizados para implementações LDAP enterprise**

[![Schemas](https://img.shields.io/badge/Schemas-146%2B-purple)](./)
[![OpenLDAP](https://img.shields.io/badge/Source-OpenLDAP%202.6.6-blue)](https://www.openldap.org/)
[![Standard](https://img.shields.io/badge/Type-Official%20Standards-green)](./)

---

## 🎯 **Schemas Essenciais - Quick Reference**

### **⭐ Top 10 Schemas Mais Importantes**
| **Schema** | **📋 Descrição** | **🎯 Casos de Uso** | **⭐ Prioridade** |
|------------|------------------|---------------------|-------------------|
| **core.schema** | 🏗️ Schema fundamental LDAP | Todos os diretórios | ⭐⭐⭐ CRÍTICO |
| **cosine.schema** | 🌐 COSINE/Internet schema | Organizações, pessoas | ⭐⭐⭐ ESSENCIAL |
| **inetorgperson.schema** | 👤 Classe pessoa organização | Usuários corporativos | ⭐⭐⭐ ESSENCIAL |
| **nis.schema** | 🖥️ Network Information Service | Sistemas Unix/Linux | ⭐⭐⭐ COMUM |
| **misc.schema** | 🔧 Schemas diversos úteis | Funcionalidades extras | ⭐⭐ ÚTIL |
| **rfc2307bis.schema** | 🔗 NIS mapping melhorado | Migração NIS para LDAP | ⭐⭐ ESPECÍFICO |
| **samba.schema** | 🪟 Integração Samba/Windows | Redes mistas Win/Linux | ⭐⭐ ESPECÍFICO |
| **collective.schema** | 👥 Atributos coletivos | Gestão de grupos | ⭐⭐ AVANÇADO |
| **ppolicy.schema** | 🔐 Password policies | Segurança de senhas | ⭐⭐ SEGURANÇA |
| **dyngroup.schema** | 🔄 Grupos dinâmicos | Grupos automáticos | ⭐ AVANÇADO |

---

## 📁 **Organização dos Schemas**

### **🏗️ Schemas Core (Obrigatórios)**
```
🏗️ FOUNDATION SCHEMAS
├── core.schema              ⭐ Base fundamental de qualquer diretório LDAP
├── cosine.schema            🌐 Schema COSINE para organizações
└── inetorgperson.schema     👤 Classe padrão para pessoas em organizações
```

### **🔧 Schemas de Sistema**
```
🔧 SYSTEM INTEGRATION
├── nis.schema               🖥️ Network Information Service (Unix/Linux)
├── rfc2307bis.schema        🔗 NIS mapping melhorado (migração)
├── samba.schema             🪟 Integração Samba/Windows
├── kerberos.schema          🎫 Kerberos authentication
└── sudo.schema              🛡️ Sudo access control
```

### **🏢 Schemas Enterprise**
```
🏢 ENTERPRISE FEATURES
├── collective.schema        👥 Atributos coletivos
├── dyngroup.schema          🔄 Grupos dinâmicos
├── ppolicy.schema           🔐 Password policies
├── duaconf.schema           ⚙️ Directory User Agent configuration
└── dsee.schema              📊 Directory Server Enterprise Edition
```

### **📱 Schemas de Aplicação**
```
📱 APPLICATION SPECIFIC
├── java.schema              ☕ Java objects in LDAP
├── corba.schema             🔌 CORBA objects
├── openldap.schema          🔧 OpenLDAP specific attributes
└── misc.schema              🎛️ Miscellaneous useful schemas
```

---

## 📋 **Catálogo Completo de Schemas**

### **Schema: core.schema** 🏗️
**Descrição**: Schema fundamental obrigatório para qualquer diretório LDAP
**Object Classes**: `top`, `person`, `organizationalPerson`, `organizationalUnit`, `organization`, `country`, `locality`, `device`, `groupOfNames`
**Principais Atributos**: `cn`, `sn`, `ou`, `o`, `c`, `l`, `description`, `member`
**Status**: ⭐⭐⭐ OBRIGATÓRIO

### **Schema: cosine.schema** 🌐
**Descrição**: Schema COSINE para organizações e pessoas na Internet
**Object Classes**: `pilotObject`, `pilotPerson`, `account`, `document`, `room`
**Principais Atributos**: `uid`, `userPassword`, `homeDirectory`, `loginShell`, `gecos`
**Status**: ⭐⭐⭐ ESSENCIAL

### **Schema: inetorgperson.schema** 👤
**Descrição**: Extensão padrão para pessoas em organizações (RFC 2798)
**Object Classes**: `inetOrgPerson`
**Principais Atributos**: `mail`, `telephoneNumber`, `mobile`, `jpegPhoto`, `employeeNumber`, `departmentNumber`
**Status**: ⭐⭐⭐ ESSENCIAL

### **Schema: nis.schema** 🖥️
**Descrição**: Network Information Service (NIS) para sistemas Unix/Linux
**Object Classes**: `posixAccount`, `posixGroup`, `shadowAccount`, `ipHost`, `ipNetwork`
**Principais Atributos**: `uidNumber`, `gidNumber`, `homeDirectory`, `loginShell`, `shadowLastChange`
**Status**: ⭐⭐⭐ COMUM

### **Schema: rfc2307bis.schema** 🔗
**Descrição**: Versão melhorada do NIS mapping (RFC 2307bis)
**Object Classes**: `posixAccount`, `posixGroup` (extensões), `nisMap`, `nisObject`
**Principais Atributos**: `nisMapEntry`, `nisMapName`, versões estendidas dos atributos POSIX
**Status**: ⭐⭐ ESPECÍFICO

### **Schema: samba.schema** 🪟
**Descrição**: Integração com Samba para redes Windows/Linux
**Object Classes**: `sambaSamAccount`, `sambaGroupMapping`, `sambaDomain`
**Principais Atributos**: `sambaSID`, `sambaAcctFlags`, `sambaNTPassword`, `sambaLogonScript`
**Status**: ⭐⭐ ESPECÍFICO

### **Schema: collective.schema** 👥
**Descrição**: Atributos coletivos para gestão eficiente de grupos
**Object Classes**: `collectiveAttributeSubentry`
**Principais Atributos**: Versões coletivas de atributos padrão (`c-o`, `c-ou`, `c-postalAddress`)
**Status**: ⭐⭐ AVANÇADO

### **Schema: ppolicy.schema** 🔐
**Descrição**: Password policies para segurança avançada
**Object Classes**: `pwdPolicy`, `pwdPolicySubentry`
**Principais Atributos**: `pwdAttribute`, `pwdMinAge`, `pwdMaxAge`, `pwdMinLength`, `pwdHistory`
**Status**: ⭐⭐ SEGURANÇA

### **Schema: dyngroup.schema** 🔄
**Descrição**: Grupos dinâmicos baseados em filtros LDAP
**Object Classes**: `dynamicObject`, `groupOfURLs`
**Principais Atributos**: `memberURL`, `dgIdentity`, `dgAuthz`
**Status**: ⭐ AVANÇADO

---

## 🚀 **Guias de Uso**

### **🔰 Setup Básico Mínimo**
```bash
# Schemas obrigatórios para qualquer diretório
include core.schema          # Base fundamental
include cosine.schema        # Organizações
include inetorgperson.schema # Pessoas

# Configuração mínima slapd.conf
database bdb
suffix "dc=example,dc=com"
rootdn "cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com"
```

### **🖥️ Setup para Sistemas Unix/Linux**
```bash
# Adicione aos schemas básicos
include nis.schema           # Contas POSIX
include rfc2307bis.schema    # NIS melhorado (opcional)

# Permite contas de usuário Unix
objectClass: inetOrgPerson
objectClass: posixAccount
uid: usuario
uidNumber: 1001
gidNumber: 1001
homeDirectory: /home/usuario
loginShell: /bin/bash
```

### **🪟 Setup para Redes Windows/Samba**
```bash
# Adicione para integração Samba
include samba.schema         # Integração Windows

# Permite contas Samba
objectClass: inetOrgPerson
objectClass: sambaSamAccount
sambaSID: S-1-5-21-...
sambaAcctFlags: [U]
```

### **🏢 Setup Enterprise Avançado**
```bash
# Recursos avançados
include collective.schema    # Atributos coletivos
include ppolicy.schema      # Políticas de senha
include dyngroup.schema     # Grupos dinâmicos

# Password policy example
dn: cn=default,ou=policies,dc=example,dc=com
objectClass: pwdPolicy
pwdMinLength: 8
pwdMaxAge: 7776000
pwdMinAge: 86400
```

---

## 🔍 **Validação e Teste**

### **✅ Verificação de Schema**
```bash
# Teste sintaxe do schema
slaptest -f slapd.conf -F /tmp/test-config

# Validação com schema lint
cd ../ldap-schema-lint/
python validate_schema.py core.schema

# Verificar dependências
grep "^objectclass\|^attributetype" *.schema | sort
```

### **🔧 Debug Comum**
```bash
# Erro: "objectclass: value #0 invalid per syntax"
# Solução: Verificar se todos os schemas necessários estão incluídos

# Erro: "attribute 'xxx' not allowed"
# Solução: Adicionar schema que define o atributo

# Erro: "invalid structural object class chain"
# Solução: Verificar hierarquia de object classes
```

---

## 📊 **Estatísticas da Coleção**

### **Por Categoria**
- **🏗️ Core/Essenciais**: 3 schemas (core, cosine, inetorgperson)
- **🔧 Sistema**: 4 schemas (nis, rfc2307bis, samba, kerberos)
- **🏢 Enterprise**: 5 schemas (collective, ppolicy, dyngroup, duaconf, dsee)
- **📱 Aplicação**: 3 schemas (java, corba, misc)
- **📋 Total**: 15+ schemas base + 131+ extensões

### **Por Uso**
- **✅ Obrigatórios**: core.schema
- **⭐ Essenciais**: cosine.schema, inetorgperson.schema
- **🖥️ Unix/Linux**: nis.schema, rfc2307bis.schema
- **🪟 Windows**: samba.schema
- **🔐 Segurança**: ppolicy.schema, kerberos.schema
- **👥 Grupos**: collective.schema, dyngroup.schema

---

## 🔗 **Links e Referências**

### **📚 RFCs Relacionados**
- 📄 [RFC 4519](../schema/rfc4519.txt) - Schema for User Applications
- 📄 [RFC 4517](../schema/rfc4517.txt) - Syntaxes and Matching Rules
- 📄 [RFC 2798](../schema/rfc2798.txt) - inetOrgPerson Object Class
- 📄 [RFC 2307](../informational/rfc2307.txt) - LDAP as Network Information Service

### **🌍 Recursos Externos**
- 🔧 [OpenLDAP Schema Reference](https://www.openldap.org/doc/REDACTED_LDAP_BIND_PASSWORD24/schema.html)
- 📋 [LDAP Schema Design](https://ldap.com/ldap-schemas-and-object-classes/)
- 🏛️ [IANA LDAP Registry](https://www.iana.org/assignments/ldap-parameters/)

---

<div align="center">

**📋 Schemas OpenLDAP Oficiais para Produção**

*146+ Schemas • Padrões RFC • Enterprise Ready*

[⬆️ Voltar às Implementações](../README.md) | [🏠 Documentação Principal](../../README.md)

</div>
